#!/usr/bin/env python3
"""Telegram bot that turns photos into a single PDF.

Send photos one by one or as an album (package) — the original order is
preserved — then press the "Convert to PDF" button.

Usage:
    python3 bot.py          # reads TELEGRAM_BOT_TOKEN from .env
"""

import asyncio
import io
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Wait this long after the last photo of an album before replying, so a
# package of photos gets one confirmation message instead of one per photo.
ALBUM_SETTLE_SECONDS = 1.2

# Image extensions we accept when a photo is sent as a file/document.
SUPPORTED = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".webp"}

CONVERT_CALLBACK = "convert"
CLEAR_CALLBACK = "clear"

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("photo2pdf")


@dataclass
class Session:
    """Photos collected from one chat, in the order they arrived."""

    # (message_id, image bytes) — message_id keeps album order stable.
    photos: list[tuple[int, bytes]] = field(default_factory=list)

    def add(self, message_id: int, data: bytes) -> None:
        self.photos.append((message_id, data))
        self.photos.sort(key=lambda item: item[0])

    def images(self) -> list[bytes]:
        return [data for _, data in self.photos]

    def clear(self) -> None:
        self.photos.clear()


def get_session(context: ContextTypes.DEFAULT_TYPE) -> Session:
    session = context.chat_data.get("session")
    if session is None:
        session = Session()
        context.chat_data["session"] = session
    return session


def convert_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📄 Convert to PDF", callback_data=CONVERT_CALLBACK)],
            [InlineKeyboardButton("🗑 Clear", callback_data=CLEAR_CALLBACK)],
        ]
    )


def build_pdf(images: list[bytes]) -> bytes:
    """Combine raw image bytes into a single PDF, preserving order."""
    frames = []
    for data in images:
        img = Image.open(io.BytesIO(data))
        # PDF has no alpha/palette; convert everything to RGB.
        if img.mode != "RGB":
            img = img.convert("RGB")
        frames.append(img)

    buffer = io.BytesIO()
    first, rest = frames[0], frames[1:]
    first.save(buffer, "PDF", save_all=True, append_images=rest)
    return buffer.getvalue()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hi! Send me photos — one by one or as an album — and I'll combine "
        "them into a single PDF.\n\n"
        "The order you send them in is the order they'll appear.\n"
        "When you're done, press *Convert to PDF*.",
        parse_mode="Markdown",
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session = get_session(context)
    count = len(session.photos)
    if not count:
        await update.message.reply_text("No photos collected yet — send me some!")
        return
    await update.message.reply_text(
        f"{count} photo{'s' if count != 1 else ''} collected.",
        reply_markup=convert_keyboard(),
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    get_session(context).clear()
    await update.message.reply_text("Cleared. Send me new photos whenever you like.")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Store an incoming photo and schedule the confirmation reply."""
    message = update.message

    if message.photo:
        # photo is a list of sizes, largest last.
        tg_file = await message.photo[-1].get_file()
    else:
        document = message.document
        suffix = Path(document.file_name or "").suffix.lower()
        if not (document.mime_type or "").startswith("image/") and suffix not in SUPPORTED:
            await message.reply_text("That file doesn't look like an image — skipping it.")
            return
        tg_file = await document.get_file()

    data = bytes(await tg_file.download_as_bytearray())
    get_session(context).add(message.message_id, data)

    # One reply per photo, or one per album: replace any pending reply job so
    # only the last photo of a package triggers the confirmation.
    chat_id = message.chat_id
    for job in context.job_queue.get_jobs_by_name(f"reply:{chat_id}"):
        job.schedule_removal()

    context.job_queue.run_once(
        send_confirmation,
        ALBUM_SETTLE_SECONDS,
        chat_id=chat_id,
        name=f"reply:{chat_id}",
        data=context.chat_data,
    )


async def send_confirmation(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_data = context.job.data
    session = chat_data.get("session")
    if session is None or not session.photos:
        return

    count = len(session.photos)
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=(
            f"Got {count} photo{'s' if count != 1 else ''}.\n"
            "Send more photos, or press *Convert to PDF*."
        ),
        parse_mode="Markdown",
        reply_markup=convert_keyboard(),
    )


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    session = get_session(context)

    if query.data == CLEAR_CALLBACK:
        session.clear()
        await query.answer("Cleared")
        await query.edit_message_text("Cleared. Send me new photos whenever you like.")
        return

    if not session.photos:
        await query.answer("No photos to convert — send me some first.", show_alert=True)
        return

    await query.answer()
    count = len(session.photos)
    await query.edit_message_text(f"Converting {count} photo{'s' if count != 1 else ''}…")
    await context.bot.send_chat_action(query.message.chat_id, ChatAction.UPLOAD_DOCUMENT)

    # Encoding is CPU-bound; keep the event loop responsive.
    pdf = await asyncio.to_thread(build_pdf, session.images())

    await context.bot.send_document(
        chat_id=query.message.chat_id,
        document=io.BytesIO(pdf),
        filename="photos.pdf",
        caption=f"Here's your PDF — {count} page{'s' if count != 1 else ''}.",
    )
    session.clear()


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.exception("Handler error", exc_info=context.error)


def main() -> int:
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        print(
            "TELEGRAM_BOT_TOKEN is not set.\n"
            "Copy .env.example to .env and put your token from @BotFather in it."
        )
        return 1

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_photo))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_error_handler(on_error)

    log.info("Bot started — press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
