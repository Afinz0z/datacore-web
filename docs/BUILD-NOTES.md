# Datacore site rebuild — build notes

14 static pages: 7 in English, 7 in Arabic. Everything is generated from `src/`,
so the two languages cannot drift apart.

| | English | Arabic |
|---|---|---|
| Home | `index.html` | `index-ar.html` |
| About us | `about.html` | `about-ar.html` |
| Services | `services.html` | `services-ar.html` |
| Products | `products.html` | `products-ar.html` |
| Projects | `projects.html` | `projects-ar.html` |
| Insights | `insights.html` | `insights-ar.html` |
| Contact | `contact.html` | `contact-ar.html` |

Open any file directly in a browser. Keep them all in one folder or the
navigation between them breaks.

## Regenerating

```
cd src && python3 build.py
```

- `content.py` — every string, both languages, in one structure. Edit copy here.
- `css.py` — the single stylesheet.
- `build.py` — page templates and the generator.

## How Arabic works

There is no second stylesheet and no RTL override file. The whole stylesheet is
written in CSS logical properties — `margin-inline-start`, `inset-inline-end`,
`text-align: start` — so setting `dir="rtl"` on `<html>` mirrors the entire
layout. Verified: no `margin-left`, `padding-right`, `float` or
`text-align: left` anywhere.

What is deliberately **not** mirrored:
- the logo (a mark must never flip)
- part numbers, phone numbers, emails, model names, `EN 54-16`, `Cat6A`
  — each wrapped in `dir="ltr"` so digits and Latin strings read correctly
  inside Arabic sentences
- the stat figures, which are tabular and LTR

Arabic also gets its own typography: **IBM Plex Sans Arabic** instead of Archivo,
line-height 1.9 instead of 1.55, and letter-spacing reset to zero — Arabic
headings set at Latin leading look cramped, and tracked-out Arabic is unreadable.

`hreflang` pairs are on every page. When this moves onto your CMS the
`?lang=ar` pattern you already use is fine; keep the hreflang tags.

## Before this goes live — needs your input

1. **CR and VAT numbers** in the footer are dummy digits. These are a legal
   requirement for a Saudi commercial site. Replace `CR 0000000000` and
   `VAT 300000000000003`.
2. **Arabic review.** I have written the Arabic to a professional standard but
   it needs one pass from a native speaker who knows low-current terminology —
   particularly `التيار الخفيف`, `النداء والإخلاء الصوتي` and the service names.
   Do not skip this; sector vocabulary is where translated technical sites fail.
3. **Manufacturer list.** The Services and About pages say "authorised to
   install". That is a stronger claim than a logo wall. Confirm each of the 14
   names, and remove any where the authorisation is not current.
4. **Standards references** (EN 54-16, EN 54-24, ISO/IEC 11801, TIA-568)
   describe the disciplines, not certifications Datacore holds. Check the
   wording suits your compliance position.
5. **Project consent.** AOU, PSAU and TAQEEM are named. Confirm each client
   permits it before publishing.
6. **Photography.** No stock images anywhere by design. Real installation
   photographs of the four named projects would strengthen the Projects page
   more than anything else on this list.

## Fixed from the old site

- Stat counters render real numbers instead of `0`
- 15+ years corrected to 19 (that figure stopped updating around 2022)
- Blog "Lorem Ipsum" placeholder replaced
- Two-slide hero carousel replaced with one fixed hero
- Placeholder partner logos (`01.png`–`05.png`, shown twice) replaced with one
  named list
- Dead LinkedIn `#`, `yourhandle` and `yourchannel` links removed; LinkedIn and
  Instagram wired to the real accounts
- `Full_Time` enum no longer surfaces in the UI
- Services taxonomy corrected: access control, CCTV, parking and GRMS moved out
  of *Datacenter Solutions* into *Surveillance and security*, which was empty;
  the three datacentre services moved out of *Network Infrastructure*
- All phone numbers are `tel:` links; WhatsApp added
- Brand teal split: `#00ACA1` for marks and fills, `#00776F` (5.43:1) for
  anything carrying text
- Breadcrumbs on every page below the top level
- Skip link, visible focus rings, labelled form fields throughout

## Map

The contact page uses a **facade**: a styled placeholder that loads the Google
embed only when the visitor clicks it. Nothing reaches Google before that, so
the map costs nothing on first paint and sets no cookies before consent. The
`hl` parameter follows the page language, so the Arabic page loads an Arabic map.

Riyadh uses the coordinates from your old embed (`24.6675676, 46.7045394`).
Dubai and Kozhikode resolve by address query — **check both pins**. I could not
open the `share.google` short link you sent (no web access from here); if it
points somewhere other than the Dabbab Complex address, send me the coordinates.

Each office card also has a Directions link that opens Google Maps with the
destination pre-filled.

## Social accounts

Defined once in `content.py` as `SOCIALS`, rendered in two places:
- footer icons, every page
- labelled buttons on the contact page under "Follow us"

LinkedIn, Instagram and Facebook are all wired. The dead `#`, `yourhandle` and
`yourchannel` links from the old footer are gone.

## Still to build

Service detail template (38 pages), project detail template, blog post
template, careers, 404, sitemap.xml, and the RFQ back end. The catalogue front
end is complete and posts a documented JSON payload to `POST /api/rfq`.
