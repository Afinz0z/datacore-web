# datacore-web

Rebuild of datacore.com.sa — 10 templates (7 pages + terms/privacy stubs and
a 404), English and Arabic, statically generated.

## Run

```bash
cd src
python build.py          # writes 20 pages + robots.txt + sitemap.xml to dist/
python check.py          # verify — run after every change
python -m http.server -d ../dist 8000
```

Python 3.9+ (`python3` on macOS/Linux). No dependencies.

## Layout

```
CLAUDE.md              context for Claude Code — read first
src/build.py           page templates + generator
src/content.py         all copy, both languages
src/css.py             the stylesheet
src/manage.py          catalogue manager — add/remove products, photos
src/check.py           post-build verification
src/data/              catalogue products, icon glyphs
src/assets/Logo.svg    brand mark
src/assets/products/   product photos, named after the SKU
dist/                  generated output (gitignored)
docs/                  design system, decisions, backlog, products how-to
data/                  improvement register, product import template (xlsx)
```

## Editing

| To change | Edit |
|---|---|
| Any wording | `src/content.py` — both `C['en']` and `C['ar']` |
| Colours, spacing, layout | `src/css.py` |
| Page structure | `src/build.py` |
| Catalogue items / photos | `python manage.py` — see `docs/PRODUCTS.md` |

Then rebuild. Never edit `dist/`.

## Before launch

The blockers are listed in `docs/BUILD-NOTES.md`. Two are hard: the CR and VAT
numbers in the footer are placeholders and legally required, and the Arabic
needs a native technical review pass. The terms/privacy pages are honest
placeholders awaiting the real legal text.
