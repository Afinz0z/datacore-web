#!/usr/bin/env python3
"""
Catalogue manager — the simplest way to add, remove and illustrate products.

    python manage.py list                    show every product
    python manage.py add                     add a product (asks questions)
    python manage.py remove <SKU>            delete a product
    python manage.py img <SKU> <image file>  attach a photo (jpg/png/webp/svg)
    python manage.py check                   validate the catalogue data

After add / remove / img the site is rebuilt automatically, so the change is
live in dist/ as soon as the command finishes. Pass --no-build to skip that.

Photos land in src/assets/products/ named after the SKU; build.py copies them
into dist/assets/products/ and the catalogue shows a photo instead of the
category icon wherever one exists. Removing a product offers to remove its
photo too. No dependencies beyond the Python standard library.
"""
import json, os, re, shutil, subprocess, sys

# Windows consoles and pipes often default to cp1252, which cannot print
# the check marks (or Arabic) — force UTF-8 rather than crash.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA     = os.path.join(HERE, "data", "products.json")
GLYPHS   = os.path.join(HERE, "data", "glyphs.json")
IMG_DIR  = os.path.join(HERE, "assets", "products")
IMG_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".svg")


def sku_file(sku):
    """SKU -> safe file stem. Keep in sync with build.py."""
    return re.sub(r'[^A-Za-z0-9._-]', '_', sku)


def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def save(products):
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=1)
        f.write("\n")


def glyph_names():
    with open(GLYPHS, encoding="utf-8") as f:
        return list(json.load(f).keys())


def find(products, sku):
    for p in products:
        if p["sku"].lower() == sku.lower():
            return p
    return None


def image_of(sku):
    stem = sku_file(sku)
    if os.path.isdir(IMG_DIR):
        for fn in os.listdir(IMG_DIR):
            base, ext = os.path.splitext(fn)
            if base == stem and ext.lower() in IMG_EXTS:
                return os.path.join(IMG_DIR, fn)
    return None


def rebuild():
    print("\nRebuilding the site…")
    r = subprocess.run([sys.executable, os.path.join(HERE, "build.py")])
    if r.returncode:
        sys.exit("build.py failed — the data change is saved, fix and re-run build.py")
    subprocess.run([sys.executable, os.path.join(HERE, "check.py")])


def ask(prompt, default=None, required=False, options=None):
    hint = f" [{default}]" if default else ""
    while True:
        v = input(f"  {prompt}{hint}: ").strip()
        if not v and default is not None:
            v = default
        if options and v and v not in options:
            print(f"    one of: {', '.join(options)}")
            continue
        if v or not required:
            return v
        print("    required")


def cmd_list(products):
    print(f"{'SKU':24} {'Brand':12} {'Category':20} {'Avail':8} Photo")
    print("-" * 74)
    for p in sorted(products, key=lambda x: (x["c"], x["b"], x["sku"])):
        avail = "stock" if p["avail"] == "stock" else f"{p.get('lead','?')}d"
        photo = "yes" if image_of(p["sku"]) else "-"
        print(f"{p['sku']:24} {p['b']:12} {p['c']:20} {avail:8} {photo}")
    print(f"\n{len(products)} products")


def cmd_add(products):
    print("New product — ENTER accepts the [default]; specs end with an empty line.")
    sku = ask("SKU / part number", required=True)
    if find(products, sku):
        sys.exit(f"{sku} already exists — remove it first or pick another SKU")
    name  = ask("Name (what the buyer reads)", required=True)
    brand = ask("Brand", required=True)
    cats  = sorted({p["c"] for p in products})
    print(f"    existing categories: {', '.join(cats)}")
    cat   = ask("Category (existing or new)", required=True)
    # suggest the glyph most used in this category, so the icon just works
    in_cat = [p["g"] for p in products if p["c"] == cat]
    gdef   = max(set(in_cat), key=in_cat.count) if in_cat else "switch"
    glyphs = glyph_names()
    print(f"    icons: {', '.join(glyphs)}")
    glyph = ask("Icon", default=gdef, options=glyphs)
    avail = ask("Availability — stock or lead", default="stock", options=["stock", "lead"])
    p = {"sku": sku, "n": name, "b": brand, "c": cat, "g": glyph, "avail": avail}
    if avail == "lead":
        while True:
            try:
                p["lead"] = int(ask("Lead time in days", required=True)); break
            except ValueError:
                print("    a number, e.g. 21")
    print("  Specs — one per line as  Key: Value  (e.g. Ports: 24). Empty line to finish.")
    specs = {}
    while True:
        line = input("    ").strip()
        if not line:
            break
        if ":" not in line:
            print("    format is  Key: Value")
            continue
        k, _, v = line.partition(":")
        specs[k.strip()] = v.strip()
    p["specs"] = specs
    products.append(p)
    save(products)
    print(f"\nAdded {sku}. Photo? run:  python manage.py img \"{sku}\" path\\to\\photo.jpg")
    return True


def cmd_remove(products, sku):
    p = find(products, sku)
    if not p:
        sys.exit(f"no product with SKU {sku}")
    print(f"  {p['sku']} — {p['n']} ({p['b']}, {p['c']})")
    if ask("Delete this product? y/n", default="n") != "y":
        sys.exit("nothing removed")
    products.remove(p)
    save(products)
    img = image_of(p["sku"])
    if img and ask(f"Also delete its photo {os.path.basename(img)}? y/n", default="y") == "y":
        os.remove(img)
    print(f"Removed {p['sku']}.")
    return True


def cmd_img(products, sku, path):
    p = find(products, sku)
    if not p:
        sys.exit(f"no product with SKU {sku} — add it first")
    if not os.path.isfile(path):
        sys.exit(f"file not found: {path}")
    ext = os.path.splitext(path)[1].lower()
    if ext not in IMG_EXTS:
        sys.exit(f"use one of {', '.join(IMG_EXTS)}")
    os.makedirs(IMG_DIR, exist_ok=True)
    old = image_of(p["sku"])
    if old:
        os.remove(old)  # one photo per SKU, any extension
    dest = os.path.join(IMG_DIR, sku_file(p["sku"]) + ext)
    shutil.copy2(path, dest)
    print(f"Photo saved as assets/products/{os.path.basename(dest)}")
    return True


def cmd_check(products):
    bad = []
    seen = set()
    glyphs = set(glyph_names())
    for p in products:
        sku = p.get("sku", "")
        if not sku:                          bad.append("product without a SKU")
        if sku.lower() in seen:              bad.append(f"duplicate SKU {sku}")
        seen.add(sku.lower())
        for k in ("n", "b", "c", "g", "avail", "specs"):
            if not p.get(k) and p.get(k) != {}:
                bad.append(f"{sku}: missing '{k}'")
        if p.get("g") and p["g"] not in glyphs:
            bad.append(f"{sku}: icon '{p['g']}' not in glyphs.json")
        if p.get("avail") not in ("stock", "lead"):
            bad.append(f"{sku}: avail must be 'stock' or 'lead'")
        if p.get("avail") == "lead" and not isinstance(p.get("lead"), int):
            bad.append(f"{sku}: lead-time days missing")
    stems = {sku_file(p["sku"]) for p in products}
    if os.path.isdir(IMG_DIR):
        for fn in os.listdir(IMG_DIR):
            base, ext = os.path.splitext(fn)
            if ext.lower() in IMG_EXTS and base not in stems:
                bad.append(f"orphan photo assets/products/{fn} (no matching SKU)")
    if bad:
        print("\n".join("  ✗ " + b for b in bad)); sys.exit(1)
    print(f"  ✓ {len(products)} products, data is clean")


def main():
    args = [a for a in sys.argv[1:] if a != "--no-build"]
    build = "--no-build" not in sys.argv[1:]
    if not args:
        print(__doc__.strip()); return
    cmd, rest = args[0], args[1:]
    products = load()
    changed = False
    if   cmd == "list":   cmd_list(products)
    elif cmd == "check":  cmd_check(products)
    elif cmd == "add":    changed = cmd_add(products)
    elif cmd == "remove":
        if len(rest) != 1: sys.exit("usage: python manage.py remove <SKU>")
        changed = cmd_remove(products, rest[0])
    elif cmd == "img":
        if len(rest) != 2: sys.exit("usage: python manage.py img <SKU> <image file>")
        changed = cmd_img(products, rest[0], rest[1])
    else:
        sys.exit(f"unknown command {cmd} — run without arguments for help")
    if changed and build:
        rebuild()


if __name__ == "__main__":
    main()
