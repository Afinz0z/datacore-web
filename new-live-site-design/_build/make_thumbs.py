# -*- coding: utf-8 -*-
"""Make the 300 px copies of product photos and maker logos that card grids use on standard screens:
assets1/images/products/sm/<name>.webp and assets1/images/brands/sm/<name>.webp.

    python make_thumbs.py

Run it after adding photos or logos. Needs Pillow 12.3.0 or newer (pip install "pillow>=12.3.0"), so it
is not one of the four build scripts CI runs; build_products.py adds a srcset only where the small copy
exists. A file that can't be read as WebP is listed and skipped."""
import os, re, sys, warnings

MIN_PILLOW = (12, 3, 0)
try:
    import PIL
    from PIL import Image
except ImportError:
    sys.exit('make_thumbs.py needs Pillow 12.3.0 or newer: pip install "pillow>=12.3.0"')
_v = re.match(r'(\d+)\.(\d+)\.(\d+)', PIL.__version__)
if not _v or tuple(map(int, _v.groups())) < MIN_PILLOW:
    sys.exit(f'make_thumbs.py needs Pillow 12.3.0 or newer, this is {PIL.__version__}: '
             'pip install --upgrade "pillow>=12.3.0"')

# Photos and logos are 600 x 600 and the largest committed one is 2000 x 2000; refuse anything far bigger
Image.MAX_IMAGE_PIXELS = 3000 * 3000
warnings.simplefilter('error', Image.DecompressionBombWarning)

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets1', 'images')
SIZE = 300

made, bad = 0, []
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
        try:
            with Image.open(src, formats=['WEBP']) as im:
                im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
                im.thumbnail((SIZE, SIZE), Image.LANCZOS)
                im.save(out, 'WEBP', quality=80, method=6)
        except Exception as e:
            bad.append(f'{sub}/{f}: {e}')
            if os.path.exists(out):            # no half-written or outdated small copy
                os.remove(out)
            continue
        made += 1
    for f in os.listdir(out_dir):              # a photo that was removed takes its small copy with it
        if not os.path.exists(os.path.join(src_dir, f)):
            os.remove(os.path.join(out_dir, f))
print('small copies made:', made)
if bad:
    print(f'skipped {len(bad)} file(s):')
    for b in bad:
        print('  ' + b)
    sys.exit(1)
