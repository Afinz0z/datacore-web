# Datacore site — enhancement log (sandbox)

Working copy of `datacore-live-mirror` (baseline = VER 26). **Local only — not pushed.**
Focus: refinement (performance, accessibility, SEO, polish, consistency), not a redesign
(prior redesign attempts were rejected — keep the approved look/brand).

Served locally at http://localhost:8138 for verification.

## Workstreams
1. **Performance** — image optimization (WebP/sizing), render-blocking, fonts, CLS.
2. **Accessibility** — alt text, contrast, focus states, ARIA, skip link, reduced-motion, headings.
3. **SEO / structured data** — FAQ schema, breadcrumbs, meta completeness, sitemap.
4. **Polish / consistency** — typography, spacing, hover/focus, small visual refinements.
5. **Content** — fill gaps, tighten copy.

## Changelog
_(newest first)_

- **Forms now deliver + bigger logo (VER 29→30)** — the RFQ basket and contact form were
  front-end-only demos (showed a ref number, sent nothing — silently dropping every lead). New
  **`dc-forms.js`** `dcpDeliver()`: if a Web3Forms `DCP_FORM_KEY` is set, submissions POST straight
  to the inbox; otherwise (or on failure) the visitor's email app opens pre-filled to
  `sales@datacore.com.sa` with their details + the RFQ items — **no more silent drops**. Wired into
  the contact handler (build_contact) and RFQ handler (dc-products.js), loaded via `shell()` on the
  form pages. **Action for client: paste a free Web3Forms key into `dc-forms.js` for seamless inbox
  capture** (until then it's mailto). Verified both forms gather all fields + the basket and deliver.
  Also **enlarged the header logo** 46→56px (38→46 condensed) so the "Technology Integrators" tagline
  is more legible. VER 29→30, regenerated + re-stamped the 6 live pages. 128 pages, 0 broken refs.

- **SEO: 5 query-targeted landing pages (EN+AR)** — from the competitive audit: dedicated
  provider/solution pages built for the exact search queries the field ranks for —
  `av-solutions-provider-saudi-arabia`, `elv-low-current-systems-saudi-arabia`,
  `network-solutions-provider-riyadh`, `structured-cabling-company-riyadh`,
  `av-network-integrator-saudi-arabia`. Each: keyword in slug + `<title>` + H1, a trust-facts
  strip (19 yrs / 9 disciplines / 38 services / 1,000+ clients), ~500–700 words of **unique**
  copy (no doorway duplication) with Saudi-compliance framing (SBC 801, Civil Defense, Vision
  2030) alongside TIA-568 / EN 54 / ISO, an on-page FAQ, related-service links, and **Service +
  FAQPage + BreadcrumbList** JSON-LD. `build_landing()` + `_build/landing.json`. Linked site-wide
  from the footer Services column + `sitemap.xml`. Grounded in real client facts; Arabic first-draft.
  128 pages, 0 broken refs, no `VER` bump.

- **Polish: print stylesheet + llms.txt articles (VER 28→29)** — added an `@media print` block to
  `dc-overlay.css`: hides the interactive chrome (header, chat, sticky CTA, back-to-top, progress bar,
  ghost watermark, CTA band, footer), forces dark-mode off (`filter:none`), black-on-white, and
  `break-inside:avoid` on cards/figures/articles — so a service, case-study or article page prints as
  clean content. Added the 3 Insights articles to `llms.txt` (answer-engine discovery). Bumped VER
  28→29, regenerated + re-stamped the 6 live core pages. 118 pages, 0 broken refs, mirror clean.

- **Content/SEO: Insights articles (per-post detail pages)** — the 3 blog teasers were one-liners
  routing to the contact page; now each has a full **article page** (`insight-<slug>.html`, EN+AR):
  *What is a public address system?*, *The impact of 5G on passive networks*, *Active versus passive
  network infrastructure*. Substantive ELV explainers grounded in the standards the site cites
  (EN 54, TIA-568, ISO/IEC 11801) — no invented claims. Each has a 3-level breadcrumb, byline,
  featured image, H2 structure, a **Related services** box (internal links to the matching service
  pages), **BlogPosting JSON-LD** (headline/datePublished/author/publisher `@id`/image), and is added
  to `sitemap.xml`. Insights hub cards now link to the articles. Content authored as text blocks so
  Arabic Latin runs auto-wrap `dir="ltr"` (verified: `EN 54-16`, `PA/VA`, `STI`). Arabic is first-draft.
  118 pages, 0 broken refs. No `VER` bump (scoped in-head CSS).

- **Nav discoverability: "Resources" dropdown (VER 27→28)** — FAQ + Glossary were footer-only;
  now surfaced in the header via a new **Resources** dropdown (between Insights and Contact),
  reusing the Services `.dcx-drop`/`.dcx-sub` pattern so it works on desktop (hover panel) and
  mobile (accordion) with no new JS. One top-level item added (minimal width impact) rather than
  two, with a narrower `.dcx-sub-simple` panel (186px vs the 282px mega-menu). Added `resources`/
  `faq`/`glossary` labels to the overlay `T` table (EN + AR: "مصادر" / "الأسئلة الشائعة" /
  "مسرد المصطلحات"), active-state highlighting via `stem`. Changed `dc-overlay.js` + `dc-overlay.css`
  → bumped **VER 27→28**, regenerated all pages + re-stamped the 6 live core pages (`?v=27`→`?v=28`).
  Verified: nav order correct, links resolve (`faq(-ar).html`/`glossary(-ar).html`), active state on
  the current page, renders in LTR + RTL, live pages load the new overlay, 0 broken refs across 112 pages.

- **Perf: product catalogue images → WebP** — 5 of the 6 remaining product PNGs converted
  to WebP (alpha preserved): `U6-ENTERPRISE` 326→17KB, `USW-PRO-48-POE` 106→14, `SIGNO-20K`
  104→9, `DM-NVX-360` 61→8, `760152661` 18→2 (**−565KB**). `MXA920-S.png` kept — WebP was
  *larger* for it (15→25KB). Product-image folder 1.9MB → 1.3MB. The photo map is derived
  from filenames (`_PFILES` in `build_products.py`), so deleting each PNG + rebuilding
  auto-repointed the SKUs to `.webp`; verified all 5 decode + 0 broken across the 35-card
  catalogue. (No cross-repo change — images + map are local.)

- **Fix: Services `?id=` deep-link (header dropdown → discipline on the hub)** — the header
  Services menu links to `services.html?id=<discipline>`, and the page already had a handler
  that scrolls to `[slug="<id>"]`. Bug: **2 of 9 sections carried a descriptive sentence as
  their `slug`** (Network Infrastructure, Meeting Room) instead of the discipline slug, so
  those two deep-links silently failed (`allFound` was false for them). Corrected both slugs
  in `services.html` + `services-ar.html` → all 9 now resolve. Also improved the scroll
  offset: the discipline tab-bar is a *second* sticky layer, so the handler now subtracts
  `headerHeight + tabbarHeight + 20` (was header only), landing the section 20px below the
  sticky chrome instead of tucked under it. Verified: all 9 slugs resolve, handler logs no
  "not found"/error, computed target clears the 140px sticky chrome. (Body-script fix, no
  overlay/asset change → no `VER` bump. Pane can't scroll full-height live pages — verified
  by logic + served DOM, as with the V22 sticky fix.)

- **SEO/content: Glossary page** — new `glossary.html` / `glossary-ar.html` (EN + AR):
  18 plain-language definitions of the ELV / AV / ICT terms the site uses (ELV, structured
  cabling, PA/VA, IPTV, AV over IP, UC, AMC, …), grounded in the site's own disciplines and
  the standards it already cites (TIA-568, ISO/IEC 11801, EN 54) — no invented claims.
  **`DefinedTermSet` + 18 `DefinedTerm` JSON-LD** for answer engines. Two-column definition
  list (`<dl>`), teal-d headwords (WCAG), ghost watermark, breadcrumb — reuses the generated-
  page shell, so no new page chrome and **no `VER` bump**. Modeled on the FAQ generator
  (`build_glossary` in `build_pages.py`, content in `_build/glossary.json`). Wired into the
  footer (`f_links`), `sitemap.xml` (EN+AR) and `llms.txt`. Arabic is first-draft (Latin
  acronyms auto-wrapped `dir="ltr"`). Regenerated all pages so every footer carries the link.

- **Services hero alignment + image parity (`services.css?v=2→3`)** — two reported issues:
  (1) *Sub-header alignment*: the right intro paragraph had an arbitrary `padding-left:8%`
  that pushed its text off any grid line, and its lead words were bright `#00aca1`
  (fails WCAG AA on white). Removed the indent so the block right-aligns cleanly to the
  container edge (same right margin as the H1), and recoloured the lead to `#00776F`
  (`--dcp-teal-d`, passes AA). Verified EN + AR (RTL mirrors correctly). Confirmed the
  live site has identical geometry — this is an inherited flaw, fixed here.
  (2) *Image effects*: the 9 service **category photos** (`.system`/`.DataCentre`/`.digital`)
  now get the same treatment as the index photos (`.project-card .image-project`,
  `.img-fluidz`) — hairline `#E2E8E6` border + 6px radius at rest, lift + soft shadow on
  hover, reduced-motion gated. Scoped to `.tab-content` so the small card SVG icons and
  READ-MORE arrows are untouched. (`!important` on the hover shadow to beat Bootstrap
  `.shadow-sm`.) No `VER` bump (page-local stylesheet, own `?v=` param).

- **QA sweep** — **0 broken local links/assets** across all 110 pages; **0 missing alt**;
  Product schema already present on products.html; reduced-motion well-gated; fonts use
  `font-display:swap` + TTF preload. Console errors exist **only on the 3 live-capture pages**
  (inherited: `grecaptcha` suppressed, jQuery `$` timing, null-element access) — benign
  (pages render/work); generated pages are clean.
- **A11y: skip link + focus ring (VER 27)** — overlay now injects a "Skip to content"
  link (first tab stop, bilingual, targets `#dc-content` with `tabindex=-1`) and a
  site-wide `:focus-visible` outline (was sparse; live-page CSS had none). In
  `dc-overlay.js`/`.css` → VER 26→27, regenerated + re-stamped live pages. (Pane can't
  paint `:focus` — window is blurred under automation — but DOM/CSS verified correct.)
- **Perf: decorative + blog images → WebP** — bg-circle, about-left-bg, right-bg-img
  (with alpha) + the 2 blog PNGs (via `POST_IMG`) → WebP (−0.5 MB). Skipped back.png/03.png
  (referenced from minified vendor CSS). **Image workstream total: ~6 MB saved (15→9 MB).**
- **SEO/UX: FAQ page** — new `faq.html` / `faq-ar.html` with a native `<details>`
  accordion (accessible, no JS), **FAQPage JSON-LD** (9 Q&A, answers grounded in existing
  site facts — no invented claims), scoped CSS in-head (no VER bump). Added to footer
  (`f_links`) + `sitemap.xml`. Arabic is first-draft. _Note: `_build/*` ROOT was hardcoded
  to the original mirror — fixed to write into this sandbox; restored the original mirror._
- **Security: rel=noopener** — added `rel="noopener noreferrer"` to 36 `target="_blank"`
  external links on the 6 live pages.
- **Perf: service photos → WebP** — the 8 service-category photos were 1000px RGB photos
  stored as PNG (6.0 MB total). Converted to WebP q82 → **0.41 MB (−5.5 MB, ~93%)**.
  Updated refs in services.html/-ar.html, removed old PNGs, verified all load, 0 broken.
- **Setup** — sandbox created from mirror VER 26, fresh local git (no remote), server on :8138.
