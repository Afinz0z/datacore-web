# Content guide — adding services, products and projects

Three kinds of content change, three processes. Nothing here needs HTML —
every page regenerates from data, in both languages, with one command.

## Products (day-to-day) — fully tooled

```bash
cd src
python manage.py add                       # asks questions, rebuilds
python manage.py img <SKU> photo.jpg       # attach/replace the photo
python manage.py remove <SKU>              # delete (offers to remove photo)
python manage.py list / check              # inventory / validation
```

Full walkthrough: `docs/PRODUCTS.md`. Product photos live in
`src/assets/products/` named after the SKU (`/` becomes `_`); auto-sourced
photos are logged with their origin in `src/data/product-image-sources.json`
— confirm rights before launch, and replace any photo by dropping a new
file with the same name.

## Projects — edit one list

1. Open `src/content.py`, find `'proj'` in **both** `C['en']` and `C['ar']`.
2. Copy an existing entry and edit its seven fields:
   `(SECTOR, CITY, title, body, [kit chips], client, scope)`.
   Keep sector spelling consistent — sectors become the filter chips.
3. Add the project photo to `src/assets/photos/`, register it in
   `content.PHOTOS` (file, width, height, EN alt, AR alt), and append its
   key to `content.PROJECT_PHOTOS` **in the same position** as the new
   project (the two lists pair by index).
4. `python build.py && python check.py`. A missing Arabic entry fails the
   build on purpose.

Only name a client with their written consent (see docs/BUILD-NOTES.md).

## Services — three data touches

A new sub-service (say the client adds "CCTV analytics"):

1. **Name it** in `src/content.py`: append to the right discipline's list in
   `C['en']['disc']` and `C['ar']['disc']` (same position), and add a blurb
   under `svc_blurbs` in both languages — the build refuses to run if one
   side is missing.
2. **Give it a slug** in `content.SERVICE_SLUGS`
   (`'CCTV analytics': 'cctv-analytics-solutions'`).
3. **Give it page copy**: add the slug's entry to
   `src/data/services-copy.json` (`{"title","desc","h1","intro","sections":
   [{"h","ps":[…],"lis":[…]}]}` under `services.<slug>.en`) and its Arabic
   twin in `services-copy-ar.json`. Copy the shape of any existing service.
4. Optional: hero art — drop `src/assets/services/<slug>.svg|png`
   (hub icon + page illustration), or map a real photo via
   `content.SERVICE_PHOTOS`.
5. `python build.py && python check.py` — the hub card, both detail pages,
   sitemap and llms.txt all appear automatically.

Removing a service is the reverse: delete it from the four places above
(the build's assertions will point at anything you forget).

## The interaction layer (for reference)

Scroll reveals, stat count-ups and the brand marquee are automatic — new
sections, stats and cards inherit them. Brand logos: `src/assets/brands/`
plus an entry in `content.BRAND_LOGOS` (only brands on the authorised
PARTNERS list). The chat bubble's quick actions live in `content.py`
(`chat_*` strings); live chat uses the client's existing tawk.to account
and loads only when a visitor starts it.
