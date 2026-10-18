# -*- coding: utf-8 -*-
"""Make the 300 px copies of product photos and maker logos that card grids use on standard screens:
assets1/images/products/sm/<name>.webp and assets1/images/brands/sm/<name>.webp.

    python make_thumbs.py

Run it after adding photos or logos. Needs Pillow (pip install pillow), so it is not one of the four
build scripts CI runs; build_products.py adds a srcset only where the small copy exists."""
import os
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets1', 'images')
SIZE = 300

made = 0
for sub in ('products', 'brands'):
    src_dir = os.path.join(ROOT, sub)
    out_dir = os.path.join(src_dir, 'sm')
    os.makedirs(out_dir, exist_ok=True)
    for f in sorted(os.listdir(src_dir)):
        if not f.lower().endswith('.webp'):
            continue
        src, out = os.path.join(src_dir, f), os.path.join(out_dir, f)
        if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(src):
            continue
        im = Image.open(src)
        im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
        im.thumbnail((SIZE, SIZE), Image.LANCZOS)
        im.save(out, 'WEBP', quality=80, method=6)
        made += 1
    for f in os.listdir(out_dir):              # a photo that was removed takes its small copy with it
        if not os.path.exists(os.path.join(src_dir, f)):
            os.remove(os.path.join(out_dir, f))
print('small copies made:', made)
