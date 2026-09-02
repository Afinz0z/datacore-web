# Managing the product catalogue

Everything happens with one tool, from the `src/` folder:

```bash
cd src
python manage.py            # shows help
```

You never edit HTML. The catalogue lives in one data file
(`src/data/products.json`) and photos in one folder
(`src/assets/products/`); every command below updates the data **and
rebuilds the site** so `dist/` is immediately up to date.

## See what's in the catalogue

```bash
python manage.py list
```

Shows SKU, brand, category, availability and whether a photo exists.

## Add a product

```bash
python manage.py add
```

It asks, in order: SKU, name, brand, category, icon, availability, specs.

- Press ENTER to accept the suggestion shown in `[brackets]`.
- **Category** — reuse an existing one when it fits (they become the filter
  sidebar). A new name creates a new filter automatically.
- **Icon** — the sketch shown until a photo exists. The suggestion is
  whatever the rest of the category uses; ENTER is almost always right.
- **Availability** — `stock`, or `lead` plus a number of days.
- **Specs** — one per line, `Key: Value` (e.g. `Ports: 24`), empty line to
  finish. Spec keys drive the filters: reuse the same spelling as similar
  products (`PoE`, `Resolution`, `Rack`…) and the product appears under the
  existing filters with no extra work.

## Add or replace a photo

```bash
python manage.py img C9200L-24P-4G-E "C:\photos\c9200l.jpg"
```

Accepts jpg / png / webp / svg. The file is copied and renamed after the
SKU; the card, list row and detail drawer switch from the icon to the photo
on the next build (which runs automatically). Replacing is the same
command with a new file. Square-ish photos on white backgrounds look best.

## Remove a product

```bash
python manage.py remove C9200L-24P-4G-E
```

Asks for confirmation, and offers to delete the product's photo with it.

## Check the data

```bash
python manage.py check
```

Flags duplicate SKUs, missing fields, unknown icons, missing lead times and
orphaned photos. `build.py` also refuses to build broken data, so a bad
hand-edit of `products.json` cannot silently ship.

## Where the current photos came from

The catalogue's initial photos were auto-sourced from manufacturer/product
pages on the web; every one is logged in
`src/data/product-image-sources.json` (SKU → image URL → source page).
Using manufacturers' product imagery is normal practice for an authorised
reseller, but **confirm rights before launch** and replace any image the
client prefers by running `python manage.py img <SKU> <file>` — same
command, new photo wins.

## Notes

- Add `--no-build` to any command to skip the automatic rebuild.
- Bulk import (1,000+ SKUs from Excel) is a back-end feature — the template
  is `data/datacore-product-import-template.xlsx` and the plan is in
  `docs/BACKLOG.md`. This tool is for day-to-day changes until then.
- Hand-editing `src/data/products.json` is fine too: it's an ordinary JSON
  list, `manage.py check` validates it, `python build.py` publishes it.
