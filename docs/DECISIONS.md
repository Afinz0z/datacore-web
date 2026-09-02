# Decisions

Settled choices and why. If you want to reverse one, that's fine — but read the
reason first so it's a decision rather than an accident.

## Static generation from Python, not a CMS or JS framework

Seven pages in two languages. A framework would add a toolchain, a build step
and a dependency tree for no gain. Python because the client's team already
works in Excel-adjacent tooling and the generator is readable without a
JavaScript background. When this moves into their CMS, `content.py` maps
cleanly onto CMS fields.

## One template, two languages

Rather than 14 hand-written pages. Bilingual sites drift — the second language
falls a version behind within months and nobody notices. A missing Arabic
string raises `KeyError` at build time instead of silently shipping English.

## Logical CSS properties instead of an RTL stylesheet

`dir="rtl"` mirrors the entire layout with no override file. The common
alternative — a second stylesheet, or a `[dir=rtl]` block at the bottom —
doubles the surface area and desynchronises the moment someone adds a component.

## Brand teal split into two values

`#00ACA1` from the logo fails WCAG AA on white at 2.83:1 — below even the 3:1
threshold for interface components. Rather than change the brand, the same hue
is darkened to `#00776F` (5.43:1) for anything carrying text, and the original
is kept for the mark and decorative fills. The client keeps their colour; the
site passes.

## Sans throughout, serif dropped

The old homepage set headlines in a serif while service pages used a geometric
sans, so a visitor arriving from search saw a different company. The logo
wordmark is geometric, so the sans is the coherent survivor. Archivo has enough
personality at display sizes to avoid reading as a default.

## Typographic hero, no photograph

Three reasons: the stock datacentre corridor on the old hero said nothing; the
hero image was the LCP bottleneck; and stock imagery actively weakens a claim
about work you have actually done. When real installation photography arrives,
revisit — but with their photos, not stock.

## Catalogue is RFQ, not e-commerce

Confirmed with the client. Full checkout would mean a payment gateway, ZATCA
e-invoicing, VAT handling and a stock ledger — all wrong for an integrator
whose buyers want a quotation. The catalogue has full shopping-site UX; the
basket submits an enquiry.

## No prices in the catalogue

Standard B2B practice in the Kingdom, and it stops competitors scraping margins.
Stock status and lead time in days are shown instead, which is what actually
drives the decision.

## Spec facets are data-driven

Filters are generated from `SPEC_FACETS` against whatever keys exist in the
product data, with counts computed per dimension excluding that dimension
(proper faceted search). A new spec key on a category creates a new filter with
no code change. At 1,000+ SKUs this is the difference between a usable
catalogue and a dead one.

## Map loads directly (supersedes: click-to-load facade)

**Changed 2 September 2026 by owner decision** ("load the map directly, no
need to ask again"). The contact map is now a real iframe with
`loading="lazy"`, so it still never competes with first paint — the browser
only fetches it as the visitor approaches it. The original facade rationale
(≈700KB of third-party JS + pre-consent cookies) is recorded below for
context; the PDPL/consent aspect should be revisited with the cookie-consent
banner at launch, since Google now sets cookies when the map loads.

*Original rationale:* a Google Maps embed is roughly 700KB of third-party
JavaScript and sets cookies on load. On the old contact page it loaded
immediately, directly under the phone number someone came for.

## Social accounts are links, not embedded feeds

Meta's embed SDK is heavy and sets tracking cookies; Instagram's supported embed
route needs an app and an expiring token; LinkedIn has no official feed widget
at all. Feeds also fail badly when posting goes quiet. If feed content is wanted
later, fetch server-side on a schedule and render as native HTML — no
third-party JS, styleable, cacheable.

## Services taxonomy corrected, not mirrored

Production files access control, CCTV, parking and GRMS under "Datacenter
Solutions" while "Surveillance and Security" sits empty, and the three
datacentre services sit under "Network Infrastructure". This repo puts them
where they belong. Do not sync this back to match production.
