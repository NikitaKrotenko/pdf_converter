#!/usr/bin/env python3
"""Convert all photos in the ./input sub-folder into a single PDF,
processing them in alphabetical (case-insensitive) order.
The result is saved into the ./output sub-folder.

Usage:
    python3 convert.py                 # -> output/output.pdf
    python3 convert.py my_album.pdf    # custom output filename
"""

import sys
from pathlib import Path

from PIL import Image

# Image extensions Pillow can open and we want to include.
SUPPORTED = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".webp", ".heic"}


def main() -> int:
    src_dir = Path(__file__).parent / "input"
    out_dir = Path(__file__).parent / "output"
    out_name = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output.pdf")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / out_name.name

    if not src_dir.is_dir():
        print(f"Error: folder not found: {src_dir}", file=sys.stderr)
        return 1

    # Collect and sort alphabetically, case-insensitively.
    photos = sorted(
        (p for p in src_dir.iterdir()
         if p.is_file() and p.suffix.lower() in SUPPORTED),
        key=lambda p: p.name.lower(),
    )

    if not photos:
        print(f"No images found in {src_dir}", file=sys.stderr)
        return 1

    print(f"Converting {len(photos)} image(s) in order:")
    images = []
    for p in photos:
        print(f"  - {p.name}")
        img = Image.open(p)
        # PDF has no alpha/palette; convert to RGB.
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        elif img.mode != "RGB":
            img = img.convert("RGB")
        images.append(img)

    first, rest = images[0], images[1:]
    first.save(out_path, "PDF", save_all=True, append_images=rest)
    print(f"\nSaved {out_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
