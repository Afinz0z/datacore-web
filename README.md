# Datacore Solutions website

Bilingual (English / Arabic) marketing and catalogue site for **Datacore
Solutions**, a Riyadh-based ELV / AV / ICT systems integrator. The site is
statically generated with Python (standard library only), its content is edited
through a Git-based CMS, and it deploys to GitHub Pages automatically on push.

## Architecture

The site lives in `new-live-site-design/` — a flat set of static HTML pages plus
assets. There is no runtime backend and no JavaScript build step.

- **Core pages** (`index`, `about-us`, `services`, each in English and Arabic)
  are the client's existing live-site markup, kept intact. A small overlay
  (`dc-overlay.css` / `dc-overlay.js`) adds the shared header, dark mode, the
  Arabic layer, and the contact widgets on top of them.
- **Everything else** — products, projects, insights, contact, the 38
  service-detail pages, and the terms / privacy / 404 pages, all in both
  languages — is generated from Python templates in `new-live-site-design/_build/`.
- **Content is data.** Insights, project case studies, showcase projects, and
  products are each stored as one JSON file per entry under
  `_build/content/{insights,projects,showcase,products}/`.

## Editing content

Non-developers edit content through **Pages CMS** (pagescms.org). The `.pages.yml`
file at the repo root defines four collections — Insights, Projects (case
studies), Showcase projects, and Products. Saving in the CMS commits the change
and triggers a rebuild and deploy. Developers can edit the same JSON files
directly, or change the templates in `_build/`.

## Building locally

No dependencies beyond Python 3.9+ (standard library only):

```bash
cd new-live-site-design/_build
python build_pages.py && python build_products.py && python build_services.py && python build_extra.py
```

Serve the result:

```bash
python -m http.server -d new-live-site-design 8000
```

## Deploying

Push to the default branch. GitHub Actions (`.github/workflows/pages.yml`) runs
the four generators and publishes `new-live-site-design/` to GitHub Pages. There
is no manual deploy step.

## Conventions

- **Bilingual parity.** Every page exists in English and Arabic
  (`<page>-ar.html`). Add or change copy in both.
- **Arabic is a first draft** pending native technical review. Flag any new
  Arabic as unreviewed; don't treat it as final.
- **Accessibility — brand teal.** Never put text on the bright teal `#00ACA1`; it
  fails WCAG AA (2.83:1). Use `#00776F` (5.43:1) for anything carrying text. The
  bright teal is for the logo, marker dots, and fills only.
- **RTL.** Use logical CSS properties (`margin-inline`, `inset-inline`), never
  physical ones (`margin-left`, `left`). Wrap Latin runs inside Arabic — brand
  names, model codes, phone numbers — in `dir="ltr"`.
- **Don't invent client facts.** Certifications, CR / VAT numbers, client
  relationships, and head-counts must be real. If a value isn't confirmed, leave
  a `TODO` rather than a plausible guess.

## Operational notes

- **Shared front-end assets** (`dc-overlay.*`, `dc-pages.css`, `dc-products.js`,
  `dc-fx.js`) are cache-busted by a `VER` string in `build_pages.py`. Bump it when
  you change one of them, or browsers keep serving a stale copy.
- **Dark mode** is a CSS `filter: invert()` applied per top-level block — not to
  the whole page, because a filter on an element taller than the GPU layer limit
  is silently dropped. Media is counter-inverted so photos stay true colour.
- **Image loading.** Don't `loading="lazy"` a grid of small primary thumbnails —
  in some render contexts the load never fires and tiles stay blank; load them
  eagerly with `fetchpriority` tiering instead. Never lazy-load the LCP hero.
- **Keep the core pages faithful.** Enhance the three live-capture pages through
  the overlay, not by rewriting their bodies.
- After changing a generator or content, rebuild and review the generated HTML
  diff — the build is deterministic apart from the date-stamped `sitemap.xml` and
  `security.txt`.

## Repo layout

```
new-live-site-design/          the site — static pages and assets
  _build/                      Python generators + content data
    content/                   per-entry JSON: insights, projects, showcase, products
    build_pages.py             products / projects / insights / contact (+ shell, footer)
    build_products.py          products catalogue
    build_services.py          38 service-detail pages
    build_extra.py             terms / privacy / 404, sitemap, robots, llms.txt
  assets1/  fonts/  imgserver/  images, fonts, media
.pages.yml                     Pages CMS configuration
.github/workflows/pages.yml    CI: build + deploy to GitHub Pages
```
