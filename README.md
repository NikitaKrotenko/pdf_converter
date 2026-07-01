# PDF Converter

Converts all photos in the `input/` folder into a single PDF, combining them
in alphabetical (case-insensitive) order.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Place your photos in the `input/` folder, then run:

```bash
python3 convert.py                 # -> output/output.pdf
python3 convert.py my_album.pdf    # custom output filename
```

## Supported formats

`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tif`, `.tiff`, `.webp`, `.heic`
