# CLAUDE.md

Context for Claude Code. Read this before touching anything.

## What this is

A rebuild of **datacore.com.sa** for Datacore Solutions — a low-current / ELV
systems integrator headquartered in Riyadh, with entities in Dubai and
Kozhikode. Founded Jeddah 2007. Their buyers are procurement engineers, MEP
consultants, main contractors and university/government procurement teams.

Seven pages, English and Arabic, generated from Python. The old site still runs
in production; nothing here is live yet.

## Commands

```bash
cd src
python3 build.py                   # writes 14 files to dist/
python3 check.py                   # verify — run this after every change
python3 -m http.server -d ../dist  # serve locally at :8000
```

`check.py` enforces the hard rules below mechanically: structure, internal
links, lang/dir pairs, inline JS syntax, no physical CSS direction properties,
and no text on `--brand`. It exits non-zero on failure. If you change CSS or
templates, run it before saying you are done.

No npm, no build toolchain, no dependencies beyond the Python standard library.
Keep it that way unless there's a real reason not to.

## Architecture

```
src/build.py        page templates + generator          ← logic
src/content.py      every string, both languages        ← copy
src/css.py          the single stylesheet               ← styles
src/data/*.json     catalogue products and icon glyphs  ← data
src/assets/Logo.svg brand mark, inlined at build time
dist/               GENERATED — never edit, never commit
```

**Never edit anything in `dist/`.** It is overwritten on every build. If you
find yourself editing a `.html` file, you are in the wrong place.

Both languages come out of the same templates. This is deliberate: hand-
maintained bilingual sites drift, and within a year the Arabic is a version
behind. If you add a string, add it to both `C['en']` and `C['ar']` in
`content.py` — the builder will `KeyError` if you forget, which is the
intended behaviour.

## Hard rules

These came out of an accessibility and content audit. Don't reverse them
without saying why.

**1. Never put text on `--brand`.** The logo teal `#00ACA1` measures 2.83:1 on
white, which fails WCAG AA (4.5:1 for text) and even the 3:1 bar for interface
components. Use `--accent` `#00776F` (5.43:1) for anything carrying or
displaying text. `--brand` is for the logo, marker dots and decorative fills
only. This is the single most common way to break the design.

**2. No physical CSS direction properties.** No `margin-left`, `padding-right`,
`float`, `text-align: left|right`, `left:`, `right:`. Use logical properties —
`margin-inline-start`, `inset-inline-end`, `text-align: start`. RTL works
because of this and there is no separate Arabic stylesheet. Verify after any
CSS change:

```bash
grep -nE '(margin|padding|border)-(left|right)|float:|text-align:\s*(left|right)' src/css.py
```

Should return nothing.

**3. Wrap Latin runs inside Arabic in `dir="ltr"`.** Part numbers, phone
numbers, emails, `Cat6A`, `EN 54-16`, `OM4`, model names, and the stat figures.
Without it, digits and punctuation reorder and read wrong. The logo is never
mirrored either.

**4. Do not invent facts about the client.** No certifications, no CR or VAT
numbers, no partner tiers, no project values, no client names, no employee
counts beyond what is in `content.py`. The footer CR/VAT are deliberately
obvious dummies awaiting the real numbers — leave them obvious rather than
plausible. If content is needed and you don't have it, add a TODO, don't fill
the gap.

**5. No stock photography.** There are currently no photographs on the site at
all, by choice. The old site used generic server-room stock that weakened every
claim on the page. Real installation photos are coming from the client. Until
then the design carries itself typographically — do not paper over the gap with
Unsplash.

**6. No third-party scripts on the critical path.** The map is a click-to-load
facade for this reason, and the old site's auto-opening chat widget was removed.
Anything from Meta, Google or an analytics vendor loads after interaction or
after consent, never at first paint.

## Design tokens

Defined in `:root` at the top of `src/css.py`. Use the variables, never raw hex.

| | |
|---|---|
| `--ink` `#1A1B1F` | text, footer, dark bands (from the logo) |
| `--accent` `#00776F` | links, buttons, anything with text — 5.43:1 |
| `--brand` `#00ACA1` | logo teal, dots, fills. **Never text** — 2.83:1 |
| `--paper` `#F4F7F6` / `--mint` `#EAF6F4` | alternating section backgrounds |
| `--line` `#E2E8E6` / `--line-2` `#CBD5D2` | borders |

Type: **Archivo** for Latin, **IBM Plex Sans Arabic** for Arabic, **IBM Plex
Mono** for data only — part numbers, scope counts, standards strings. Mono is
functional here (it stops 0/O confusion in SKUs), not decorative. Arabic
switches family, sets line-height 1.9 instead of 1.55, and zeroes
letter-spacing; tracked-out Arabic is close to unreadable.

Spacing is an 8px-based scale, `--s1` through `--s6`. Radius is 2–3px
throughout; nothing is pill-shaped except filter chips.

## Client facts

Use these rather than recalling them. They are also in `content.py`.

- Riyadh HQ: Datacore Solutions, Office 503, Dabbab Complex, Dabbab St, Riyadh
  12626 · +966 11 512 8888 · `24.6675676, 46.7045394`
- Dubai: DCS Advanced Technologies L.L.C, OF09-390, Um Hurair Second · +971 52
  753 6070
- India: Artifitia Solutions LLP, Sahya Building, Govt Cyberpark, Kozhikode,
  Kerala 673016 · +91 495 350 1154
- sales@ / info@ / careers@datacore.com.sa
- LinkedIn `/company/datacore-solutions` · Instagram `@datacore_sa` ·
  Facebook `/www.datacore.com.sa/`
- 9 disciplines, 38 services, 1,000+ clients, 100+ staff, founded 2007
- Named projects: Arab Open University (council room, auditorium), Prince Sattam
  bin Abdulaziz University (smart classrooms), TAQEEM (HQ AV)

**19 years, not 15.** The live site says "15+", which stopped updating around
2022. Derive from 2007 if you touch it.

## Current state

Done: all 7 pages in both languages, the products catalogue front end with
faceted search and an RFQ basket, the click-to-load map, socials, breadcrumbs,
skip links, focus rings, `tel:` links, WhatsApp.

Not done: service detail template (38 pages), project detail template, blog post
template, careers, 404, `sitemap.xml`, structured data, and the entire RFQ back
end. See `docs/BACKLOG.md`.

The catalogue front end posts a documented JSON payload to `POST /api/rfq`.
Nothing receives it yet. Product data is 37 sample SKUs in
`src/data/products.json`; production is 1,000+ via the Excel importer in
`data/datacore-product-import-template.xlsx`, which defines the schema.

## Gotchas

- `build.py` uses f-strings containing JavaScript, so literal braces in JS must
  be doubled `{{ }}`. If the catalogue breaks after an edit, check this first.
- `content.py` is UTF-8 with substantial Arabic. Don't let an editor rewrite the
  encoding or reorder the RTL text.
- The Arabic in `content.py` is **a first draft awaiting native technical
  review.** Don't treat it as final and don't propagate its phrasing into new
  pages without flagging that it's unreviewed.
- The taxonomy on the live site is wrong — access control, CCTV, parking and
  GRMS are filed under "Datacenter Solutions" while "Surveillance and Security"
  is empty. This repo fixes that. Don't "correct" it back to match production.
- `docs/RESEARCH-PROMPT.md` is for a separate browsing-enabled session, not for
  you to execute.
