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
the four generators and publishes the website to GitHub Pages. The generators
(`_build/`) and the plain-language guide (`readme.txt`) stay in the repository
but are not published. There is no manual deploy step.

## Contributing

The working rules — bilingual parity, RTL, brand colours, cache-busting,
self-hosted libraries, consent, sitemap dates, search basics, plain copy — are
in `CONTRIBUTING.md`. Read it before changing anything.

## Repo layout

```
new-live-site-design/          the site — static pages and assets
  _build/                      Python generators + content data
    content/                   per-entry JSON: insights, projects, showcase, products
    build_pages.py             products / projects / insights / contact (+ shell, footer)
    build_products.py          products catalogue
    build_services.py          38 service-detail pages
    build_extra.py             terms / privacy / 404, sitemap, robots, llms.txt
  assets1/  fonts/  imgserver/  images, fonts, media (third-party libraries in assets1/vendor/)
  readme.txt                   plain-language guide for non-technical readers
.pages.yml                     Pages CMS configuration
.github/workflows/pages.yml    CI: build + deploy to GitHub Pages
CONTRIBUTING.md                working rules for anyone changing the site
```
