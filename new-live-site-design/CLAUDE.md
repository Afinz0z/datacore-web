# CLAUDE.md — "New Live Site Design" (datacore-live-mirror)

Context for anyone (human or Claude) picking up this folder. This is the
**New Live Site Design**: the client's live site datacore.com.sa, mirrored
offline and then progressively enhanced into a complete, bilingual, themeable
site. It is a **separate deliverable** from `../datacore-web/` (the from-scratch
rebuild). Do not confuse the two.

## What it is
- The bodies of `index.html`, `about-us.html`, `services.html` (+ `-ar`) are the
  **live site's exact HTML/CSS/JS**, captured 3 Sep 2026. Keep them byte-faithful
  — the client wanted the live look kept exactly. Enhancements ride on top via an
  overlay, never by editing these bodies.
- Everything else (products / projects / insights / contact, 38 service-detail
  pages, terms / privacy / 404, EN+AR) is **generated** in the live "Texta" look
  with the rebuilt site's header.

## Architecture — the overlay pattern
- `dc-overlay.css` / `dc-overlay.js` graft the developed-site **header** (logo,
  nav with a 9-discipline Services dropdown, theme toggle, language switch,
  consultation button) onto every page, add **dark mode** and the **Arabic**
  layer, the **quick-contact chat bubble** (WhatsApp/Call/Email/Enquiry) and the
  **sticky mobile CTA**. `mount()` wraps the page body in `#dc-content` and adds
  the header + fixed overlays as direct `<body>` children.
- **Dark mode** = `filter:invert(1) hue-rotate(180deg)` on `#dc-content`, with
  media counter-inverted. Elements that must stay upright (header, chat bubble,
  sticky bar, RFQ drawer) live **outside** `#dc-content` and are themed by hand,
  because a filtered ancestor also breaks `position:fixed`.
- The overlay **rewrites** the live `service-details/<slug>` links to the local
  `service-<slug>.html` files at runtime (one-shot pass + a delayed pass for
  late-injected links + a document-level click delegator). The live HTML on disk
  is never modified.
- `dc-pages.css` = live-look styles for the generated pages. `dc-products.js` =
  the catalogue filter + RFQ basket. `dc-fx.js` = scroll-reveals + count-up.

## Rebuilding — the generators
Persisted in `_build/` (were in a temp scratchpad; copied here so they survive):
- `build_pages.py`   → products / projects / insights / contact (+ `-ar`); holds
  the shared `shell()`, `hero()`, `cta_band()`, `footer()`, the `VER` asset
  version, `mirror_strings.json` (extracted copy), and `stats_marquee()`.
- `build_products.py` → products.html (+ar); reads `../datacore-web/src/data/products.json`.
- `build_services.py` → 38 service pages ×2; EN copy from `services-copy.json`,
  AR from `services-copy-ar.json` (the live AR pages are empty shells).
- `build_extra.py`    → terms / privacy / 404 (+ar), `sitemap.xml`, `robots.txt`, `llms.txt`.

To rebuild everything (run from `_build/`):
```
python build_pages.py && python build_products.py && python build_services.py && python build_extra.py
```
Then, if any of `dc-overlay.*` / `dc-pages.css` / `dc-products.js` / `dc-fx.js`
changed, **bump the cache-buster**: raise `VER` in `build_pages.py`, re-run the
generators, and re-stamp the 6 live core pages (regex-replace `dc-overlay.(css|js)?v=`).
Browsers cache these assets hard; without a version bump they serve a stale copy.

## Conventions & hard rules (inherited from ../datacore-web/CLAUDE.md)
- **Keep the 3 live pages exact.** Enhance via the overlay only.
- **WCAG:** never put text on the bright brand teal (`#00ACA1`/`#00b3a6`, fails
  AA). Text/buttons use `--dcp-teal-d` = `#00776F`; bright teal is decoration only.
- **RTL:** logical CSS properties only (`inset-inline-*`, `margin-inline-*`); wrap
  Latin runs inside Arabic in `dir="ltr"` (brands, codes, phone numbers).
- **Arabic is a first draft** (service copy authored in-repo) — needs native review.
- **Never invent client facts.** CR/VAT in the footer are placeholders. Real
  endpoints in use: WhatsApp `wa.me/966115128888` (client to confirm it's a WA
  Business line), email `sales@datacore.com.sa` / `info@datacore.com.sa`, and the
  three office tel numbers (Riyadh/Dubai/Kozhikode).

## Verification note
The Python `http.server` on Windows resets a few image connections under the live
pages' ~40-image load, so an image can look blank on first paint in-browser. The
files are valid and complete (serve fine one-at-a-time and on GitHub Pages). It's
a test-server quirk, not a defect — don't "fix" it by re-exporting images.

## Status (this chat)
- **Done:** header+dropdown, About extras (CEO photo, team gallery, features),
  dark mode, Arabic, all functional pages (products faceted search + RFQ, projects,
  insights, contact map switcher + form + schema), 38 service pages ×2 with
  methodology band + Service schema, terms/privacy/404, SEO scaffolding, chat
  bubble, sticky mobile CTA, stats band + brand marquee + scroll reveals.
- **Pending:** project case-study detail pages, FAQ + schema, self-hosted header
  font, image optimisation of the blog PNGs; `?id=` on the Services links doesn't
  yet filter/scroll the hub. (`countUp()` is now implemented — see session log.)
- **Backups:** `../backups/live-mirror-V{1,2,3}-*.zip` (one per pass, user's
  standing preference).

## Skills experiment (reverted)
Two design skills were trialled and the user rejected both, so the pre-skills
version is what ships. Reverted: deleted `dc-redesign.css` (frontend-design
pilot), `dc-home.css` + `index-v2.html` (taste-skill Home candidate), and the
`class="dcp-r"` / redesign `<link>` hooks on index/products. If retrying: keep
any redesign as a scoped `html.<class>` override layer loaded on 1-2 pages only,
and never add the `.dcp` base class to a bespoke page (it re-imports the
uppercase-heading rule).

## Page coverage vs the live site (checked 7 Sep 2026)
Every internal page the live site links to is brought in locally. The overlay
rewrites live absolute `datacore.com.sa/<path>` links to the local file at
runtime (so no page bounces the user back to the live header):

| live path | local | note |
|---|---|---|
| `/` | index.html | |
| `/about-us` | about-us.html | |
| `/services` | services.html | |
| `/service-details/<slug>` | service-`<slug>`.html | 38 ×2 = 76 |
| `/projects`, `/project/<slug>` | projects.html | + 5 `project-<slug>.html` case-study pages (V21) |
| `/blogs`, `/blog/<slug>` | insights.html | no per-post detail pages |
| `/contact-us` | contact.html | |
| `/career` | careers.html | added 7 Sep 2026 |
| `/terms-service` | terms.html | |
| `/privacy-policy` | privacy.html | |

Re-run the check any time: it lives in the session, but the logic is just
"extract every `datacore.com.sa/<seg>` from the 6 core pages, map via the
overlay's `LINKMAP`, confirm each `<local>.html` exists." Gaps to note: individual
project and blog *detail* pages are intentionally not mirrored (routed to the
hub pages); the live tawk.to chat and reCAPTCHA are **suppressed** in the mirror
(domain-locked; they error off-domain and duplicate our own chat bubble) — they
work on the real datacore.com.sa.

## Fixes after the skills revert (7 Sep 2026)
- About "people behind the projects" subtitle inherited the live `.sub` hero
  style (≈70px); `.dcx-team .sub` now sets an explicit size (`!important`).
- Projects "From our sites" gallery raised from 3 to 6 photos (`GAL_IMG`).
- Careers page built (EN+AR) + footer link points to it; overlay routes the live
  `/career` link to it.
- Chatbot: the live tawk.to widget + reCAPTCHA are hidden (`killWidgets()` in the
  overlay hides body-level iframes outside our chat / `#dc-content`; CSS hides the
  reCAPTCHA). Our own quick-contact bubble is the single chat.

## Session log — chat bubble, animations, Arabic fix, photos, SEO (7 Sep 2026)
Asset version is now **VER = "15"**. Deployed across several passes.
- **Quick-contact bubble** moved bottom-left → **bottom-right**; now a 60px white
  circle showing the Datacore logo mark (`assets1/images/dc-logo-chat.png`, from
  `Images/LOGO DATACORE.png`). Products RFQ FAB stacks *above* it (96px desktop /
  150px mobile) so they don't collide.
- **Load optimisation** of the 6 live core pages: `about.css`/`services.css` made
  non-render-blocking (`media=print` onload + `<noscript>`), duplicate Poppins
  `<link>` removed, below-the-fold images `loading="lazy" decoding="async"` (first
  5 kept eager to protect the LCP hero).
- **Animations** (`dc-fx.js` + `dc-pages.css` + overlay), all
  `prefers-reduced-motion` gated: stats **count-up** (ease-out cubic — `countUp()`
  now implemented), product/project **card hover** lift + image zoom, gallery
  figure lift, **header condense-on-scroll** (`dcx-scrolled` toggled by a scroll
  listener in `dc-overlay.js`), **RFQ badge pulse** on count change, fail-safe
  hero entrance (`animation-fill-mode:both`, no standalone `opacity:0`, keyframes
  at top level — nested-in-@media keyframes don't resolve in some engines).
- **Arabic "???" fix.** The 3 live-capture pages (index/about-us/services `-ar`)
  inherited the live site's UTF-8 encoding fault: whole Arabic strings rendered as
  "?" (plus some demo-template leftovers — LaslesVPN, Lorem Ipsum, fake
  testimonials). Re-authored the visible corrupted text (~50 runs) from the English
  siblings + the datacore-web rebuild's Arabic, applied by structural (tag+class+
  index) pairing. **First draft — needs native review.** 0 visible "???" remain;
  about-us-ar's corruption was entirely in the overlay-hidden header.
- **Team photos.** `dc-team-kozhikode.jpg` ("Indian Team") rebuilt from the 48MP
  `Images/Indian Team.DNG` (PIL reads it as MPO; trimmed 10% top/bottom, 1200px).
  `dc-team-riyadh.jpg` ("Datacore Connect 2026, Riyadh") from
  `Images/Annual Meet Riyadh.jpg` (the turf-field group), cropped to the slot's
  3/2. *(First attempt used the indoor `#2.jpg` — user flagged it wrong.)*
- **SEO / GEO / AEO / LLMO.** Central `seo_meta()` + `site_jsonld()` +
  `breadcrumb_jsonld()` in `build_pages.shell()` → every generated page gets
  canonical, hreflang en/ar/x-default, OG/Twitter (real 1200×630 `dc-og.jpg`), and
  a JSON-LD graph: **Organization + three LocalBusiness offices (geo/phone/addr) +
  WebSite + BreadcrumbList**; service pages self-canonicalise and link their
  `Service` node to `#org` via `@id`. Live pages: fixed broken meta (description
  URL leak, `&amp;amp;`, `@YOUR_TWITTER_HANDLE`, relative OG), Arabic titles +
  `og:locale ar_SA`, injected the same graph. `SITE` in build_pages =
  `build_extra` `BASE` = `https://www.datacore.com.sa` (all URLs consistent). New
  `seo_live.py` (scratchpad) does the live-page pass; re-run it if the live heads
  are regenerated.

## Session log — Arabic live-page parity repair (8 Sep 2026)
The 3 live-capture Arabic pages had inherited corruption from a broken state of
the live Arabic CMS (it was passing NULL service names into `htmlspecialchars()`,
emitting empty tags + leaked PHP warnings). English captures were healthy, so the
fix = port the English structure into Arabic. **HTML-body edits only — no overlay/
asset change, so no VER bump.** Deployed (mirror `e97ddcb` → datacore-web
`519ef35`, Pages success). Backup **V20** = `live-mirror-V20-arabic-pages-parity.zip`.
- **index-ar** "How we help you succeed": 4th card was empty (`src=""`, empty
  h3/p — the empty src is what rendered the broken-image glyph); other 3 pulled
  from the `phpstack-…cloudwaysapps.com` staging box. Rebuilt all 4 to mirror
  English's local images (`secure/frame/server/audio_*.png`) + added the Audio-
  Visual card in Arabic.
- **about-us-ar** Core Values: 6 value cards had local images but blank h2/p;
  plus 3 extra junk cards (external imgs) absent from English. Filled the 6
  (الابتكار/التركيز على العميل/النزاهة/الأمان/الموثوقية/التطوّر) + dropped the 3 junk cards → matches EN's 6.
- **services-ar**: removed 5 leaked `Deprecated: htmlspecialchars()` lines; then
  **full rebuild** of the tab region to match English — EN & AR share the 9
  category `#SER…` ids, so it was a clean whole-region swap (`_build`-style script
  in scratchpad `svc_ar.py`): 9 categories + 38 cards, Arabic titles+descriptions,
  all-local icons, positional replacement (robust to the mojibake in EN source),
  Latin acronyms auto-wrapped `dir="ltr"`. Fixed a capture drift where AR had
  categories mislabeled against their ids (e.g. `#SER0cb934c0` is Audio-Visual in
  EN but was tagged "Meeting Rooms" in AR). **All rebuilt Arabic is first-draft —
  needs native review** (user chose to deploy now and refine later).

## Session log — project case-study pages (8 Sep 2026, V21)
Added **per-project case-study detail pages** — the first per-project pages in the
mirror. Deployed (mirror `1a2d3bc` → datacore-web `8a742e5`, Pages success). Backup
**V21** = `live-mirror-V21-project-case-studies.zip`. No `VER` bump (reused existing
CSS classes; the "at a glance" facts panel is inline-styled).
- **Source docs** (repo root): `OWIS_Riyadh_Case_Study.pdf` (text), `Taqeem Case
  Study.pdf` (text + photos), `AOU-Auditorium Case Study.docx`, `PSAU Case Study.docx`,
  and `Arab Open Unversity Case Study.pdf` (image-only, rendered via `fitz`). **Gotcha:**
  that last PDF is the AET-vendor copy of the **auditorium**, not the council room — the
  user's guess was wrong, the document won. So the auditorium got the extra source and
  the **council page was built from its existing `proj[1]` summary** (no dedicated doc;
  nothing invented).
- **New generator** `build_case(slug, ar)` in `build_pages.py`, modelled on
  `build_services.build()`: hero + `dcp-svc-shot` photo + inline-styled "At a glance"
  facts + narrative sections + `dcp-gal` gallery + `cta_band` + `footer`, wrapped by
  `shell(ar,'projects',…,canon='project-'+slug)` with per-case **CreativeWork** JSON-LD
  (datePublished only where the doc states it — Taqeem 2024-04, auditorium 2023). Content
  lives in **`_build/cases.json`** (5 cases × EN/AR). `CASE_SLUG` is index-aligned with
  `proj`/`PROJ_IMG`. `wrap_ltr()` helper wraps Latin runs `dir="ltr"` in the AR pages.
  `__main__` writes `project-<slug>.html` / `-ar.html` (10 files). **Arabic is first-draft.**
- **Real photos** extracted from the docs (PIL crop→1200×750 card / 1100×700 gallery):
  replaced the generic `dc-proj-{taqeem,psau,auditorium}.jpg` and added 8
  `dc-proj-*-N.jpg` gallery shots. Council keeps its old image (no source photo).
- **Links:** hub cards (`build_projects`) get a "Read the case study" `.dcp-dir` link;
  the **homepage** project cards (EN `index.html` + AR `index-ar.html`) were repointed
  from `datacore.com.sa/projects/<slug>` to the local `project-<slug>.html` (overlay
  leaves local hrefs alone — verified post-overlay). Fixed the AR homepage's blank
  "success stories" heading/lede + the `<?= SITE_URL ?>` leftover in both homepages.
- **Known pre-existing (not touched):** `index(-ar).html` still have ~11 empty headings
  (brand band / hidden hero) + one `cloudwaysapps` `pcm__…png` image — live-capture cruft,
  unrelated to this task.

## Session log — services fixes + Arabic Our Story (8 Sep 2026, V22)
Three reported bugs, mirror `eb7f194` → datacore-web `dbc5095` (Pages success), backup **V22**.
- **Services tab-bar overlap:** `.scroll-container` in `assets1/css/services.css` was
  `position:sticky; top:13%` — a viewport-% offset that lands *below* the fixed overlay
  header (77px, doesn't condense here), leaving a gap where the service cards showed
  through. Changed to `top:77px` (flush). Note: these live pages scroll on `body`
  (`overflow:auto`), and the preview pane renders them at full height (no scroll viewport),
  so sticky can't be shown in-pane — verified via the served CSS + header height instead.
  Added `?v=2` to the `services.css` link on both services pages (it's outside the `VER`
  system) so the fix isn't cached.
- **Arabic hero watermark:** the `.service-bg` was `SERVICES.svg` (English wordmark as
  paths) at `right:0`. Added **`assets1/images/SERVICES-ar.svg`** (an SVG `<text>` "خدماتنا",
  5% opacity, RTL) and `[dir="rtl"] .service-bg{right:auto;left:0}` in services.css to
  mirror it to the left. Verified rendered. **(V23)** Same fix for the About Us hero
  watermark: `assets1/about/ABOUT.svg` → `ABOUT-ar.svg` (من نحن) + `[dir="rtl"] .about-bg`
  → left, `about.css?v=2`. **(V24)** Fixed uneven shading in both AR watermark SVGs:
  `<text fill-opacity="0.05">` double-painted overlapping Arabic glyph seams → wrapped
  full-black text in `<g opacity="0.05">` (flatten then composite once); `?v=2` on the img refs.
- **Arabic About Us "Our Story":** `about-us-ar.html` had the `قصتنا` heading but an empty
  `.about-story-text` body — filled from the English (Arabic first-draft). (Like the EN
  page, the block nests `<h4>`/`<p>` inside a `<p>`, so the browser auto-closes the outer
  `p` and the text renders as siblings — `.about-story-text.textContent` reads empty by
  design; check `.xc-p-left`.)

## File map (mirror root)
Flat by design — do not move pages into subfolders (breaks relative links + the
overlay rewrite + Pages URLs). Loose files at root:
`dc-overlay.css/.js` `dc-pages.css` `dc-products.js` `dc-fx.js` = the live system;
97 `*.html` pages (6 core · 8 functional · 76 service · careers/terms/privacy/404);
`sitemap.xml` `robots.txt` `llms.txt`; `CLAUDE.md` `READ-ME-FIRST.txt`.
Folders: `assets1/` `fonts/` `imgserver/` (assets), `_build/` (the 4 generators
+ `mirror_strings.json`; run all four from there to rebuild).
