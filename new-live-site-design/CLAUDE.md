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
- **Pending:** `countUp()` in `dc-fx.js` is stubbed (stats show static numbers
  until implemented); design polish passes (capability tables, project case-study
  detail pages, FAQ + schema, self-hosted header font, image optimisation of the
  blog PNGs); `?id=` on the Services links doesn't yet filter/scroll the hub.
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
| `/projects`, `/project/<slug>` | projects.html | no per-project detail pages |
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

## File map (mirror root)
Flat by design — do not move pages into subfolders (breaks relative links + the
overlay rewrite + Pages URLs). Loose files at root:
`dc-overlay.css/.js` `dc-pages.css` `dc-products.js` `dc-fx.js` = the live system;
97 `*.html` pages (6 core · 8 functional · 76 service · careers/terms/privacy/404);
`sitemap.xml` `robots.txt` `llms.txt`; `CLAUDE.md` `READ-ME-FIRST.txt`.
Folders: `assets1/` `fonts/` `imgserver/` (assets), `_build/` (the 4 generators
+ `mirror_strings.json`; run all four from there to rebuild).
