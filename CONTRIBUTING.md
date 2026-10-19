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
  `Custom-1`, `Rack` or `Structure`, custom items with no brand or model, and discontinued models.
- Discontinued models stay off the site even when they belong to a bundle; their supporting products stay
  listed. `_build/product_discontinued.json` names each one with the maker's page that says so and the
  date it was checked. Add a model only on the maker's own word, never because it is hard to find.
- Only public fields are imported. Prices, fees, distributors, lead times, Zoho IDs and the names of
  the staff who created records never reach the site.
- Specs come from the maker's own page wherever one exists for the exact model: saved in the product file with
  `src` (the page) and `checked` (the date), kept across re-imports, and labelled on the site as checked against
  the maker. Where no maker page gives them (the site blocks reading, opts out of crawlers, or has no page per
  model), the export's Specifications column is shown instead (`spec_src: inventory`), labelled as Datacore's
  inventory record and not yet checked against the maker. Checked specs replace it as soon as they exist.
- Where the maker's site can't be read, specs may come from a distributor's listing that shows the exact part number
  as the manufacturer part number. The product file then carries `src_kind: distributor` and `src_name` (for example
  CDW), and the site says the specs come from that distributor's listing, not the maker's page. A listing that
  contradicts the inventory record is held back for a person to read. A distributor never decides that a model is
  discontinued, and the maker's own page replaces a listing as soon as it can be read.
- Product pages may show up to three of the maker's official videos (`videos` in the product file: YouTube id, title,
  channel). A video counts only when it is embedded in the maker's product page saved in `src`, its channel is the
  maker's own, the same video is not on five or more of the brand's products (a brand reel), and YouTube's oEmbed
  still answers for it. Each shows as a still from our photo with a play button; nothing loads from YouTube until a
  visitor presses play, and then it plays from youtube-nocookie.com. The privacy pages say so.
- Checking specs: use only the maker's own page for that exact model code (a variant suffix is allowed
  when the address starts with the code), in English. Keep at most 12 rows, key specs first and
  dimensions, weight and environment last. Leave out rows that can't be read cleanly (nested tables,
  footnote marks, filler such as "see the table below", a value the maker's page itself garbles);
  a missing row is better than a wrong one. Read every value flagged as different by eye before
  reporting it to the client: the same fact written another way (1.8 m and 6 ft (1.83 m)) is not wrong.
- Products the export lists only by a code ("DIN-AO8") or a bare kind ("Speaker") get a readable name from
  the first phrase of their own description, with the code kept in brackets; the original is saved as `model`.
  A description that runs its title into a sentence ("Amplifier, 75 W The AMP-X75 provides...") is cut
  before the sentence. A trailing brand in brackets ("Switch License (Huawei)") is dropped, since the
  card shows the brand.
- Search must find every product by its part number, its model code with or without punctuation, words
  from its name, its brand and its category, in both languages. The type and brand filters show the
  eight largest; a window lists all of them by first letter.
- Categories map to filter groups, Arabic names and card icons in `_build/product_categories.json`.
  A category missing from it shows under Other until it is added.
- Bundles: `acc` lists a product's supporting products (mounts, licences, support contracts) and `for`
  the main products it supports. The cards link both ways.
- Every link is checked against evidence before it is trusted: the supporting product naming the main one,
  the screen size inside a mount's range (the maker's figure when its page gives one, otherwise the range in
  the name), or the same maker. Links that fail (a screen outside the mount's range, or no fit at all when
  read by a person) go in `_build/product_links_fix.json` with the reason, and the importer leaves them out.
  The same file is the list to fix in Quattro.
- Record errors in the export are corrected in `import_products.py` with the evidence in a comment:
  `BRAND_BY_SKU` for a wrong maker, `CATEGORY_BY_SKU` for a wrong category.
- Photos are `assets1/images/products/<sku>.webp`, 600 × 600, with the SKU's punctuation turned into
  `_` (`safe_name()` in `product_data.py`). Products with a photo are listed first. Licences, support
  contracts, warranties and software show the maker's logo instead (`assets1/images/brands/<brand>.webp`,
  same size, named with `safe_name()` of the lower-case brand).
- Pages hold 60 cards (rows of 2 to 6 always fill). Photos past the first 12 cards load at low priority.
- A card shows up to four short spec lines, with a size or weight in the last place when the product has
  one (`card_specs()`). With fewer than three lines it also shows up to four lines of the product's own
  description (`card_note()`), unless the description only repeats the name. Nothing else fills a card:
  no placeholder text and no specs from the export's free-text column.
- On desktop the request button sits at the top of the filter sidebar, which stays in view, so it never
  covers a card. On phones it floats in the corner as an icon with the count.
- The default order mixes the catalogue: products with a photo first, then each half dealt out one at a
  time across filter groups, then brands inside a group, then categories (`_variety()` in
  `build_products.py`). A page never opens on one category, and one maker with many photos can't fill it.
- Product pages: every product with its own photo or checked specs gets `product-<brand>-<sku>.html` and
  `-ar.html` at the site root (page links are relative to the root, so pages can't live in a folder).
  `build_products.py` writes them and deletes the pages of products that no longer qualify, and
  `build_extra.py` lists whatever is there in the sitemap. They carry Product schema without prices.
- Category pages: `products-<group>.html` for each filter group except Other, the catalogue opened on that
  group. Their introduction is written from the catalogue (count, makers, commonest types), so it stays true
  after every import. Write no claims into it by hand.
- Small photos: after adding photos or logos, run `python make_thumbs.py` in `_build/` (it needs Pillow, so CI
  doesn't run it). It writes 300 px copies to `sm/` folders, and grids offer them to standard screens. A
  product without a small copy still shows its full photo.
- The catalogue keeps its view in the address: `q`, `grp`, `cat`, `brand`, `rel`, `sort` and `p` (an open
  quick view), so any view can be shared and Back works. `rfq` (a request list someone shared) and `req=1`
  (open the request) are read once and removed. Links from elsewhere on the site can use these, as the
  project pages do for the brands a case study names.
- Searches that find nothing are sent to analytics as `dcp_search_none`, and only once Google Tag Manager has
  loaded, which happens after the visitor accepts cookies.
- The page itself carries the first page of cards. Card data is `assets1/data/products-data.js`; descriptions,
  full spec lists, model codes and makers' pages are in `assets1/data/products-text.js`, which loads once the
  page has drawn. Both are
  stamped with a hash of their contents, so a new import is never served from a stale cache.

## Checks and visitor reports

- Every build runs `_build/check_site.py` before it deploys: each local link, image, script, stylesheet and
  sitemap address must exist and each page needs a title. A broken build stops there and is not published.
- The daily "Site check" workflow (`.github/workflows/site-check.yml`) requests every page of the published
  site with `_build/check_live.py`. If anything does not answer it opens a GitHub issue labelled `site-check`
  (GitHub emails the owner) and closes it once everything answers again. Run it by hand from the Actions tab.
- Visitors report mistakes from the chat bubble ("Report a mistake on this page") or from the link on the 404
  page. Reports go through `dcpDeliver()` with the page address, the page the visitor came from and the
  screen size; the privacy page says so. The 404 page also records `page_not_found` for analytics, which only
  reaches Google Tag Manager after the visitor accepts cookies.

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
