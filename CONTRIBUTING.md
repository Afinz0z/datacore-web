# Contributing

How to change the Datacore website without breaking it. Read `README.md` first
for the architecture, the build and the deploy.

## Workflow

1. Edit content — the JSON files under `new-live-site-design/_build/content/`,
   or the same entries through Pages CMS — or the templates in `_build/`.
2. Rebuild:

   ```bash
   cd new-live-site-design/_build
   python build_pages.py && python build_products.py && python build_services.py && python build_extra.py
   ```

3. Review the generated HTML diff. It should contain only what you meant to
   change; the build is otherwise deterministic.
4. Check every page you touched in English and Arabic, with the browser console
   open: `python -m http.server -d new-live-site-design 8000`.
5. Commit the content change together with the regenerated pages, then push to
   `master`. GitHub Actions rebuilds and deploys; there is no manual step.

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
- **Keep the core pages faithful.** `index`, `about-us` and `services` (and their
  Arabic versions) are the client's live-site markup. Enhance them through the
  overlay (`dc-overlay.css` / `dc-overlay.js`) rather than rewriting their bodies.

## Search basics (every page, both languages)

- One `<h1>`. Another line that should look like a page title is an `<h2 class="h1 dc-h1">`
  (the stylesheets style `.dc-h1` exactly like `h1`).
- A meta description of 100 to 160 characters, unique to the page. The generators use the
  entry's lede; when the lede is too long or too short, add a `desc` field to the entry.
- A canonical tag pointing at the page itself, breadcrumbs (on the page and as
  `BreadcrumbList`), and a link to the page from at least one other page.
- `alt` text that says what a content image shows; `alt=""` on decorative images.
- `noindex` only on the 404 pages. Internal links point at the final page (no redirects,
  no links to the old live domain), and none may return 404.
- Articles carry the team author block and `author` in the schema; when the client names
  an author, use the person. The author block ends with a link that lets readers add
  datacore.com.sa as a Google preferred source (`PREFSRC` in `build_pages.py`): a plain
  link, so nothing loads from Google until it is clicked.
- Images are WebP with `width` and `height`. Project photos also ship a 720 px copy
  (`<name>-720.webp`); `photo_attrs()` in `build_pages.py` adds the `srcset`.

## Writing and styling

- Plain, specific copy. No em dashes: use commas or brackets around an aside, a colon
  before an explanation, a full stop; the Arabic comma (،) in Arabic. No "it's not X,
  it's Y" formulas, emojis or tick marks in text and buttons, and no testimonials unless
  they are real and attributed.
- Build from the existing classes in `dc-pages.css`. Don't add decorative gradients,
  glows, frosted-glass blur, extra shadows or hover animations.
- Put `<style>` blocks and stylesheet links in `<head>`, never in the body: a stylesheet in
  the body repaints everything above it and shifts the layout.
- Third-party content never holds up the page: Google Tag Manager loads only after cookie
  consent (`dc-consent.js`), and the contact-page map is added once the page has loaded and
  the map is near the screen.
  The privacy pages describe both, so change them together.

## Products

- The catalogue comes from the inventory export (`Products-All-Categories-<date>.xlsx`). To refresh it:

  ```bash
  cd new-live-site-design/_build
  python import_products.py path/to/Products-All-Categories-<date>.xlsx --skipped ../../../skipped.csv
  python build_products.py
  ```

  Keep the skipped list outside the repository. It names every row left out and why.
- Rows left out: inactive items, anything marked TBA (to be assigned), placeholder rows such as
  `Custom-1`, `Rack` or `Structure`, and custom items with no brand or model.
- Only public fields are imported. Prices, fees, distributors, lead times, Zoho IDs and the names of
  the staff who created records never reach the site.
- The export's free-text Specifications column is not published. Until a product's specs are checked
  against the manufacturer's page, its card shows only the type, series and sale unit. Checked specs
  are saved in the product file with `src` (the page) and `checked` (the date), and a re-import keeps them.
- Products the export lists only by a code ("DIN-AO8") or a bare kind ("Speaker") get a readable name from
  the first phrase of their own description, with the code kept in brackets; the original is saved as `model`.
- Categories map to filter groups, Arabic names and card icons in `_build/product_categories.json`.
  A category missing from it shows under Other until it is added.
- Bundles: `acc` lists a product's supporting products (mounts, licences, support contracts) and `for`
  the main products it supports. The cards link both ways.
- Photos are `assets1/images/products/<sku>.webp`, 600 × 600, with the SKU's punctuation turned into
  `_` (`safe_name()` in `product_data.py`). Products with a photo are listed first. Licences, support
  contracts, warranties and software show the maker's logo instead (`assets1/images/brands/<brand>.webp`,
  same size, named with `safe_name()` of the lower-case brand).
- The page itself carries the first 24 cards. The full catalogue is `assets1/data/products-data.js`,
  stamped with a hash of its contents, so a new import is never served from a stale cache.

## Operational notes

- **Cache-busting.** Shared assets (`dc-overlay.*`, `dc-pages.css`,
  `dc-products.js`, `dc-fx.js`, `dc-consent.js`) are loaded with a `?v=` stamp
  taken from `VER` in `build_pages.py`. When you change one of them, bump `VER`
  and rebuild. The six core pages are not generated, so update their `?v=`
  stamps by hand (search for the old number).
- **Libraries are self-hosted.** jQuery, Bootstrap, Slick, AOS, jarallax and
  Bootstrap Icons live under `assets1/vendor/`, and the Poppins font under
  `fonts/poppins/`. Keep them local: CDN copies add connections, and a Google
  Fonts link contacts Google before the visitor has answered the cookie banner.
  Bootstrap Icons is trimmed to the four icons in use (`chevron-down`,
  `circle-fill`, `list`, `x`); to use another one, replace the folder with the
  full 1.10.5 release or re-subset the font.
- **Consent.** Google Tag Manager loads only after the visitor accepts cookies
  (`dc-consent.js`). Don't add tags or scripts that bypass it.
- **Dark mode** is a CSS `filter: invert()` applied per top-level block — not to
  the whole page, because a filter on an element taller than the GPU layer limit
  is silently dropped. Media is counter-inverted so photos stay true colour.
- **Image loading.** Don't `loading="lazy"` a grid of small primary thumbnails —
  in some render contexts the load never fires and tiles stay blank; load them
  eagerly with `fetchpriority` tiering instead. Never lazy-load the LCP hero.
- **Scroll reveals** (`dc-fx.js`) only animate blocks that start below the fold
  and fit on one screen, so page content is never hidden while it loads.
- **Sitemap dates.** Each page's `<lastmod>` is the last day its visible text
  changed, read from the git history by `build_extra.py`. Committing regenerated
  pages together with the content change keeps the dates right.
- **Keep the repository clean.** No local tool settings, archives or scratch
  files; `readme.txt` (the plain-language guide) and `_build/` are kept in the
  repository but are not published.
