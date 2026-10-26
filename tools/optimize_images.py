#!/usr/bin/env python3
"""Create WebP copies of every JPEG under Project Images/2026 and Project Images/jobs,
plus small `-sm.webp` thumbnails (600px) for the job galleries.

The site references the .webp files; the original JPEGs stay in the repo as
masters. Re-run after adding photos:  python3 tools/optimize_images.py
Requires Pillow (pip install pillow).
"""
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
DIRS = [ROOT / 'Project Images' / '2026', ROOT / 'Project Images' / 'jobs']
MAX_SIDE = 1600
QUALITY = 78
THUMB_SIDE = 600


def main():
    before = after = count = 0
    for d in DIRS:
        for src in sorted(d.rglob('*.jpg')):
            dst = src.with_suffix('.webp')
            thumb = src.with_name(src.stem + '-sm.webp')
            wants_thumb = 'jobs' in src.parts
            if dst.exists() and (thumb.exists() or not wants_thumb):
                continue
            im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
            im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
            im.save(dst, 'WEBP', quality=QUALITY, method=6)
            if wants_thumb:
                im.thumbnail((THUMB_SIDE, THUMB_SIDE), Image.LANCZOS)
                im.save(thumb, 'WEBP', quality=QUALITY, method=6)
            before += src.stat().st_size
            after += dst.stat().st_size
            count += 1
    if count:
        print(f'{count} images: {before/1e6:.1f} MB JPEG -> {after/1e6:.1f} MB WebP '
              f'({100 - 100*after/before:.0f}% smaller)')
    else:
        print('All WebP files up to date.')


if __name__ == '__main__':
    main()
