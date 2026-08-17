# Photo to PDF

[![Download latest release](https://img.shields.io/github/v/release/NikitaKrotenko/pdf_converter?label=Download&style=for-the-badge)](https://github.com/NikitaKrotenko/pdf_converter/releases/latest)

A tiny app that combines your photos into a single PDF. Available as a
desktop app for macOS and Windows, or as a command-line script.

## Download (no Python required)

Go to the [Releases](../../releases) page and download the build for your OS:

- **macOS** — `Photo-to-PDF-macOS.zip`, unzip it and double-click `Photo to PDF.app`.
  Since it's unsigned, macOS will need an extra step the first time — see
  below.
- **Windows** — `Photo to PDF.exe`, just double-click it.
  Windows SmartScreen may warn about an unknown publisher the first
  time — click **More info** → **Run anyway**.

New builds are published automatically whenever a version tag (e.g. `v1.0.0`)
is pushed, via [.github/workflows/build.yml](.github/workflows/build.yml).

### Opening the macOS app for the first time

The app isn't code-signed, so Gatekeeper blocks it by default. To open it:

1. Right-click (or Control-click) `Photo to PDF.app` → **Open**, then confirm
   in the dialog that appears.
2. If you still see *"Apple could not verify... is free of malware"*, do one
   of the following:
   - **System Settings**: open **Privacy & Security**, scroll down to the
     blocked-app notice, and click **Open Anyway** (then confirm once more).
   - **Terminal**: remove the quarantine flag and open it directly:
     ```bash
     xattr -cr "/path/to/Photo to PDF.app"
     ```

This is only needed once — after approving it, double-clicking works
normally.

## Using the app

Only two buttons:

1. **Select Files** — pick any photos (`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`,
   `.tif`, `.tiff`, `.webp`, `.heic`).
2. **Convert** — choose where to save, and it combines the selected photos
   into one PDF in the order you picked them.

## Running from source

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python3 src/app.py
```

## Telegram bot

`src/bot.py` runs a Telegram bot that collects photos and sends back a PDF.

Send photos one by one or as an album — the order they arrive in is the order
they appear in the PDF. After each photo (or each album) the bot replies with
"Send more photos, or press *Convert to PDF*" and a **Convert to PDF** button.
Pressing it returns the finished PDF and clears the collection.

Commands: `/start`, `/status` (how many photos are queued), `/clear`.

### Setup

1. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token.
2. Put the token in `.env` at the repo root (copy `.env.example` if it's
   missing). `.env` is gitignored, so the token never gets committed:

   ```
   TELEGRAM_BOT_TOKEN=123456789:AAExampleTokenGoesHere
   ```

3. Install the dependencies and run it:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   python3 src/bot.py
   ```

The bot uses long polling, so it needs no public URL — it just has to keep
running. Stop it with Ctrl+C.

## Command-line version

`src/convert.py` converts every photo in the `input/` folder into a PDF in
alphabetical order, saved to `output/`:

```bash
python3 src/convert.py                 # -> output/output.pdf
python3 src/convert.py my_album.pdf    # custom output filename
```

## Building the desktop apps yourself

**macOS** (via [py2app](https://py2app.readthedocs.io/)):

```bash
pip install py2app
python3 packaging/macos/setup.py py2app
open "dist/Photo to PDF.app"
```

**Windows** (via [PyInstaller](https://pyinstaller.org/), run on Windows):

```bash
pip install pyinstaller
pyinstaller packaging/windows/PhotoToPDF.spec
dist\Photo to PDF.exe
```
