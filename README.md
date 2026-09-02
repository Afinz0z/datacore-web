# datacore-web

Rebuild of datacore.com.sa — 7 pages, English and Arabic, statically generated.

## Run

```bash
cd src
python3 build.py
python3 check.py
python3 -m http.server -d ../dist 8000
```

Python 3.9+. No dependencies.

## Layout

```
CLAUDE.md              context for Claude Code — read first
src/build.py           page templates + generator
src/content.py         all copy, both languages
src/css.py             the stylesheet
src/data/              catalogue products, icon glyphs
src/assets/Logo.svg    brand mark
dist/                  generated output (gitignored)
docs/                  design system, decisions, backlog, research prompt
data/                  improvement register, product import template (xlsx)
```

## Editing

| To change | Edit |
|---|---|
| Any wording | `src/content.py` — both `C['en']` and `C['ar']` |
| Colours, spacing, layout | `src/css.py` |
| Page structure | `src/build.py` |
| Catalogue items | `src/data/products.json` |

Then rebuild. Never edit `dist/`.

## Before launch

Six blockers are listed in `docs/BUILD-NOTES.md`. Two are hard: the CR and VAT
numbers in the footer are placeholders and legally required, and the Arabic
needs a native technical review pass.
