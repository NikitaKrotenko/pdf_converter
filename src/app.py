#!/usr/bin/env python3
"""Minimal Mac app: pick photos, convert them to a single PDF.

Two buttons only: "Select Files" and "Convert".
"""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from PIL import Image

SUPPORTED = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".webp", ".heic"}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Photo to PDF")
        self.geometry("420x220")
        self.resizable(False, False)

        self.selected_files: list[Path] = []

        self.status = tk.Label(self, text="No files selected", wraplength=380, justify="center")
        self.status.pack(pady=(24, 12))

        button_frame = tk.Frame(self)
        button_frame.pack(pady=12)

        self.select_button = tk.Button(
            button_frame, text="Select Files", width=16, command=self.select_files
        )
        self.select_button.pack(side="left", padx=8)

        self.convert_button = tk.Button(
            button_frame, text="Convert", width=16, command=self.convert, state="disabled"
        )
        self.convert_button.pack(side="left", padx=8)

    def select_files(self):
        paths = filedialog.askopenfilenames(
            title="Select photos",
            filetypes=[
                ("Images", " ".join(f"*{ext}" for ext in SUPPORTED)),
                ("All files", "*.*"),
            ],
        )
        if not paths:
            return
        self.selected_files = [Path(p) for p in paths]
        self.status.config(text=f"{len(self.selected_files)} file(s) selected")
        self.convert_button.config(state="normal")

    def convert(self):
        if not self.selected_files:
            return

        out_path = filedialog.asksaveasfilename(
            title="Save PDF as",
            defaultextension=".pdf",
            initialfile="output.pdf",
            filetypes=[("PDF", "*.pdf")],
        )
        if not out_path:
            return

        try:
            images = []
            for p in self.selected_files:
                img = Image.open(p)
                if img.mode != "RGB":
                    img = img.convert("RGB")
                images.append(img)

            first, rest = images[0], images[1:]
            first.save(out_path, "PDF", save_all=True, append_images=rest)
        except Exception as exc:
            messagebox.showerror("Conversion failed", str(exc))
            return

        messagebox.showinfo("Done", f"Saved to {out_path}")


def main() -> int:
    App().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
