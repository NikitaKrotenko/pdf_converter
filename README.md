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
