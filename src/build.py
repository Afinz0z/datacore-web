# -*- coding: utf-8 -*-
import re, os, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from css import CSS
from content import (C, PARTNERS, SOCIALS, OFFICE_GEO, WHATSAPP,
                     PHOTOS, SERVICE_PHOTOS, SERVICE_SLUGS)
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.normpath(os.path.join(HERE, "..", "dist"))
os.makedirs(OUT, exist_ok=True)
PAGES = ["index","about","services","products","projects","insights","contact"]

# Canonical origin for hreflang/canonical/OG/sitemap. Meta only — every href
# the visitor clicks stays relative, so the build still works from file://.
BASE = "https://www.datacore.com.sa/"

# ── build-time content sanity ─────────────────────────────────────────────
# Same structure in both languages, and a blurb for every service — a missing
# key should stop the build, not ship a silently empty card.
assert [len(d[2]) for d in C['en']['disc']] == [len(d[2]) for d in C['ar']['disc']], \
    "EN/AR discipline lists have drifted apart"
for _l in ("en","ar"):
    _missing = [s for d in C[_l]['disc'] for s in d[2] if s not in C[_l]['svc_blurbs']]
    assert not _missing, f"svc_blurbs[{_l}] missing: {_missing}"

# ── logo ──────────────────────────────────────────────────────────────────
_svg = open(os.path.join(HERE,"assets","Logo.svg"), encoding="utf-8").read().strip()
_svg = re.sub(r'^<svg ', '<svg role="img" aria-label="Datacore Solutions" ', _svg)
LOGO       = _svg                                  # dark ink, for white header
LOGO_LIGHT = _svg.replace("#1A1B1F", "#FFFFFF")    # white ink, for dark footer

# Favicon: the swirl mark alone — the first two paths of the logo file.
_mark = "".join(re.findall(r'<path .*?/>', _svg)[:2])
FAVICON = quote(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 1 48 61">{_mark}</svg>')

# ── catalogue data ───────────────────────────────────────────────────────
# Swap products.json for a live /api/products fetch when the back end exists.
# Nothing else in this file needs to change.
import json as _json
import shutil as _shutil
_D = os.path.join(HERE, "data")
_load = lambda n: _json.load(open(os.path.join(_D, n), encoding="utf-8"))

def sku_file(sku):
    """SKU -> safe file stem (SKUs can contain '/', e.g. DS-...-ISU/SL)."""
    return re.sub(r'[^A-Za-z0-9._-]', '_', sku)

# Product photos: drop assets/products/<sku_file(SKU)>.(jpg|jpeg|png|webp|svg)
# next to the sources and rebuild — the card, list row and detail drawer pick
# it up; products without a photo keep their category glyph. Managed by
# manage.py ("python manage.py img <SKU> <file>"), or copy files in by hand.
IMG_DIR = os.path.join(HERE, "assets", "products")
_products = _load("products.json")
_img = {}
if os.path.isdir(IMG_DIR):
    for _fn in sorted(os.listdir(IMG_DIR)):
        _base, _ext = os.path.splitext(_fn)
        if _ext.lower() in (".jpg", ".jpeg", ".png", ".webp", ".svg"):
            _img[_base] = _fn
for _p in _products:
    _fn = _img.get(sku_file(_p["sku"]))
    if _fn:
        _p["img"] = "assets/products/" + _fn
if _img:
    os.makedirs(os.path.join(OUT, "assets", "products"), exist_ok=True)
    for _fn in _img.values():
        _shutil.copy2(os.path.join(IMG_DIR, _fn),
                      os.path.join(OUT, "assets", "products", _fn))

P_DATA  = "const P = "     + _json.dumps(_products, ensure_ascii=False) + ";"
P_GLYPH = "const GLYPH = " + _json.dumps(_load("glyphs.json"),   ensure_ascii=False) + ";"

# ── site assets: brand images + photography ──────────────────────────────
_ASSETS = os.path.join(OUT, "assets")
os.makedirs(_ASSETS, exist_ok=True)
for _fn in ("og-image.png", "apple-touch-icon.png", "favicon-32.png"):
    _src = os.path.join(HERE, "assets", _fn)
    if os.path.exists(_src):
        _shutil.copy2(_src, os.path.join(_ASSETS, _fn))
_PHOTO_DIR = os.path.join(HERE, "assets", "photos")
if os.path.isdir(_PHOTO_DIR):
    os.makedirs(os.path.join(_ASSETS, "photos"), exist_ok=True)
    for _fn in os.listdir(_PHOTO_DIR):
        _shutil.copy2(os.path.join(_PHOTO_DIR, _fn),
                      os.path.join(_ASSETS, "photos", _fn))

def photo(key, l, crop=False, lazy=True):
    """Captioned <figure> for a client photo; alt/caption follow the language."""
    f, w, h, en_alt, ar_alt = PHOTOS[key]
    alt = ar_alt if l == "ar" else en_alt
    cls = "ph crop" if crop else "ph"
    loading = ' loading="lazy"' if lazy else ""
    return (f'<figure class="{cls}"><img src="assets/photos/{f}" width="{w}" height="{h}"'
            f'{loading} alt="{e(alt)}"><figcaption>{e(alt)}</figcaption></figure>')

# ── service detail copy (fetched from the live site; AR authored in-repo) ─
SVC_EN = _load("services-copy.json")["services"]
SVC_AR = _load("services-copy-ar.json")["services"]
assert set(SVC_EN) == set(SVC_AR) == set(SERVICE_SLUGS.values()), \
    "service copy files and SERVICE_SLUGS have drifted apart"

# hub-name lookup per slug and language (EN key position -> AR counterpart)
_slug_names = {}
for _di, _d in enumerate(C['en']['disc']):
    for _si, _s in enumerate(_d[2]):
        _slug = SERVICE_SLUGS[_s]
        _slug_names[_slug] = {
            "en": _s, "ar": C['ar']['disc'][_di][2][_si], "disc": _di}

# the live site's H1s are inconsistent in a few places — display fixes only,
# fetched data stays verbatim
H1_FIX = {
 'wifi-solutions': 'Wi-Fi Solutions',
 'fire-alarm-systems': 'Fire Alarm Systems',
 'interactive-video-walls-tiles': 'Interactive Video Walls & Tiles',
 'pava-public-address-amp-voice-evacuation-system':
     'PAVA — Public Address & Voice Evacuation',
 'paga-public-address-and-general-alarm-system':
     'PAGA — Public Address & General Alarm',
 'full-time-staffing-solution': 'Full-Time Staffing Solution',
 'grms-solutions-': 'GRMS Solutions',
}
P_ICO   = ('const ico=(g,s)=>`<svg width="${s}" height="${s}" viewBox="0 0 24 24" '
           'fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
           'stroke-linejoin="round">${GLYPH[g]||GLYPH.switch}</svg>`;\n')

SOC_SVG = {
 "linkedin":'<svg width="19" height="19" viewBox="0 0 24 24" fill="currentColor"><path d="M4.98 '
            '3.5a2.5 2.5 0 11-.02 5 2.5 2.5 0 01.02-5zM3 9h4v12H3zM10 9h3.8v1.7h.05c.53-.95 '
            '1.83-1.95 3.77-1.95 4.03 0 4.78 2.5 4.78 5.75V21h-4v-5.6c0-1.34-.03-3.06-1.9-3.06'
            '-1.9 0-2.2 1.45-2.2 2.96V21h-4z"/></svg>',
 "instagram":'<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
             'stroke-width="1.9"><rect x="3" y="3" width="18" height="18" rx="5"/>'
             '<circle cx="12" cy="12" r="4"/>'
             '<circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>',
 "facebook":'<svg width="19" height="19" viewBox="0 0 24 24" fill="currentColor"><path d="M14 '
            '9h3V6h-3c-2.2 0-4 1.8-4 4v2H8v3h2v7h3v-7h3l1-3h-4v-2c0-.55.45-1 1-1z"/></svg>',
}
def soc_icons():
    # label is just the network name — language-neutral, correct on AR pages too
    return "".join(
        f'<a href="{u}" aria-label="{n}" rel="noopener me" target="_blank">'
        f'{SOC_SVG[k]}</a>' for k, u, n in SOCIALS)

def soc_buttons():
    return '<div class="socrow">' + "".join(
        f'<a href="{u}" rel="noopener me" target="_blank">{SOC_SVG[k]}<span>{n}</span></a>'
        for k, u, n in SOCIALS) + '</div>'

def maps_embed(idx, l):
    geo, q = OFFICE_GEO[idx]
    return ("https://www.google.com/maps?q=" + (geo or quote(q)) +
            f"&hl={l}&z=16&output=embed")

def maps_link(idx):
    geo, q = OFFICE_GEO[idx]
    return "https://www.google.com/maps/dir/?api=1&destination=" + quote(geo or q)

def url(page, l):
    return f"{page}.html" if l == "en" else f"{page}-ar.html"

def e(s):
    return html.escape(str(s), quote=False)

# ══════════════════════════════════════════════════════════════════════════
#  SHELL
# ══════════════════════════════════════════════════════════════════════════
def head(l, page, title, desc, extra_css="", noindex=False):
    t = C[l]
    og_locale = "ar_SA" if l == "ar" else "en_US"
    og_alt    = "en_US" if l == "ar" else "ar_SA"
    robots = '\n<meta name="robots" content="noindex">' if noindex else ''
    return f"""<!DOCTYPE html>
<html lang="{t['lang']}" dir="{t['dir']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">{robots}
<meta name="theme-color" content="#00776F">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,{FAVICON}">
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="canonical" href="{BASE}{url(page,l)}">
<link rel="alternate" hreflang="{t['other_lang']}" href="{BASE}{url(page,t['other'])}">
<link rel="alternate" hreflang="{t['lang']}" href="{BASE}{url(page,l)}">
<link rel="alternate" hreflang="x-default" href="{BASE}{url(page,'en')}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Datacore Solutions">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{BASE}{url(page,l)}">
<meta property="og:locale" content="{og_locale}">
<meta property="og:locale:alternate" content="{og_alt}">
<meta property="og:image" content="{BASE}assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Datacore Technology Integrators">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{t['font']}&display=swap" rel="stylesheet">
<style>{CSS}{extra_css}</style>
</head>
<body>
<a class="skip" href="#main">{t['skip']}</a>
"""

def nav_link(k, v, page, l):
    # No backslash inside the f-string expression — that needs Python 3.12,
    # and this repo promises 3.9+.
    cur = ' aria-current="page"' if k == page else ''
    return f'<a href="{url(k,l)}"{cur}>{v}</a>'

def header(l, page):
    t = C[l]
    nav = "".join(nav_link(k, v, page, l) for k, v in t['nav'])
    return f"""<header class="hdr">
  <div class="wrap">
    <a class="logo" href="{url('index',l)}" aria-label="Datacore Solutions">{LOGO}</a>
    <nav class="mainnav" id="mainnav" aria-label="Main">{nav}<a class="menu-cta"
      href="{url('contact',l)}">{t['consult']}</a></nav>
    <div class="hdr-cta">
      <a class="lang" href="{url(page,t['other'])}" lang="{t['other_lang']}"
         hreflang="{t['other_lang']}">{t['other_label']}</a>
      <a class="btn btn-p" href="{url('contact',l)}">{t['consult']}</a>
      <button class="burger" aria-label="{t['menu']}" aria-expanded="false"
              aria-controls="mainnav">
        <svg class="bars" width="24" height="24" viewBox="0 0 24 24" fill="none"
             stroke="currentColor" stroke-width="2"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
        <svg class="x" width="24" height="24" viewBox="0 0 24 24" fill="none"
             stroke="currentColor" stroke-width="2"><path d="M5 5l14 14M19 5L5 19"/></svg>
      </button>
    </div>
  </div>
</header>
<main id="main">"""

def phead(l, page, title, lede):
    t = C[l]
    crumb = f'<a href="{url("index",l)}">{t["home"]}</a><span>/</span><span>{title}</span>'
    return f"""<section class="phead"><div class="wrap">
  <nav class="crumbs" aria-label="Breadcrumb">{crumb}</nav>
  <h1>{title}</h1><p>{lede}</p>
</div></section>"""

def cta(l):
    # TODO: restore the company-profile button when the client supplies the
    # PDF (docs/BACKLOG.md — "Current company profile PDF"). The old link
    # pointed at /assets1/... on the legacy site and 404s from this build.
    t = C[l]
    return f"""<section class="cta"><div class="wrap">
  <div><h2>{t['cta_h']}</h2><p>{t['cta_p']}</p></div>
  <div class="btns">
    <a class="btn btn-p" href="{url('contact',l)}">{t['consult']}</a>
    <a class="btn btn-s" href="{url('products',l)}">{t['f_catalogue']}</a>
  </div>
</div></section>"""

def footer(l):
    t = C[l]
    company = "".join(f'<li><a href="{url(k,l)}">{v}</a></li>' for k, v in t['f_links'])
    # careers live on the contact page (careers@ + the enquiry type dropdown)
    # until a real careers template is built — see docs/BACKLOG.md
    company += f'<li><a href="{url("contact",l)}">{t["f_careers"]}</a></li>'
    svc = "".join(f'<li><a href="{url("services",l)}#{d[0]}">{d[1]}</a></li>'
                  for d in t['disc'][:4])
    svc += f'<li><a href="{url("services",l)}">{t["f_all_disc"]}</a></li>'
    offices = "".join(
        f'<div class="office"><strong>{o[0]}</strong>'
        f'<p>{o[1]}<br>{o[2]}<br>{o[3]}</p>'
        f'<a href="tel:{o[5]}" dir="ltr">{o[4]}</a></div>' for o in t['offices'])
    return f"""</main>
<footer class="ftr"><div class="wrap">
  <div class="ftr-top">
    <div>
      <div class="logo">{LOGO_LIGHT}</div>
      <p class="ftr-blurb">{t['brand_line']}</p>
    </div>
    <div><h4>{t['f_company']}</h4><ul>{company}</ul></div>
    <div><h4>{t['f_services']}</h4><ul>{svc}</ul></div>
    <div><h4>{t['f_touch']}</h4><ul>
      <li><a href="{url('products',l)}">{t['f_catalogue']}</a></li>
      <li><a href="{url('contact',l)}">{t['get_quote']}</a></li>
      <li><a href="mailto:sales@datacore.com.sa" dir="ltr">sales@datacore.com.sa</a></li>
      <li><a href="mailto:careers@datacore.com.sa" dir="ltr">careers@datacore.com.sa</a></li>
      <li><a href="https://wa.me/{WHATSAPP}" rel="noopener" target="_blank">{t['f_whatsapp']}</a></li>
    </ul></div>
  </div>
  <div class="offices">{offices}</div>
  <div class="ftr-btm">
    <span>{t['f_rights']}</span>
    <a href="{url('terms',l)}">{t['f_terms']}</a>
    <a href="{url('privacy',l)}">{t['f_privacy']}</a>
    <span class="legal">{t['f_legal']}</span>
    <div class="soc">{soc_icons()}
    </div>
  </div>
</div></footer>
<script>
const b=document.querySelector('.burger'),n=document.querySelector('.mainnav');
if(b){{
  const close=()=>{{b.setAttribute('aria-expanded','false');n.classList.remove('open');}};
  b.addEventListener('click',()=>{{
    const o=b.getAttribute('aria-expanded')==='true';
    b.setAttribute('aria-expanded',String(!o));
    n.classList.toggle('open',!o);
  }});
  n.addEventListener('click',ev=>{{if(ev.target.closest('a'))close();}});
  document.addEventListener('keydown',ev=>{{if(ev.key==='Escape')close();}});
  matchMedia('(min-width:861px)').addEventListener('change',m=>{{if(m.matches)close();}});
}}
</script>
</body></html>"""

# ── shared blocks ─────────────────────────────────────────────────────────
def disc_cards(l):
    t = C[l]
    out = []
    for slug, name, subs, std, _ in t['disc']:
        lis = "".join(f"<li>{s}</li>" for s in subs)
        out.append(f'<article id="{slug}"><h3><a href="{url("services",l)}#{slug}">{name}</a>'
                   f'</h3><ul>{lis}</ul><p class="mono std" dir="ltr">{std}</p></article>')
    return '<div class="disc">' + "".join(out) + '</div>'

def proj_cards(l):
    t = C[l]
    out = []
    for sector, city, title, body, kit, client, scope in t['proj']:
        k = "".join(f'<a href="{url("products",l)}">{x}</a>' for x in kit)
        out.append(f"""<article class="proj" data-sector="{e(sector)}">
  <div class="band"><span>{sector}</span><span>{city}</span></div>
  <div class="in"><h3>{title}</h3><p>{body}</p>
    <div class="kit">{k}</div>
    <dl><dt>{t['p_client']}</dt><dd>{client}</dd>
        <dt>{t['p_scope']}</dt><dd>{scope}</dd></dl>
  </div></article>""")
    return '<div class="projs">' + "".join(out) + '</div>'

def partners_grid():
    return '<div class="partners">' + "".join(f"<span>{p}</span>" for p in PARTNERS) + '</div>'

def timeline(l):
    return '<div class="tl">' + "".join(
        f'<article><time datetime="{y}">{y}</time><h3>{h}</h3><p>{p}</p></article>'
        for y, h, p in C[l]['tl']) + '</div>'

def posts(l, on_insights=False):
    # Post detail pages don't exist yet (docs/BACKLOG.md — blog template).
    # On the home page the titles lead to the insights listing; on the
    # insights page itself they are plain headings rather than links to
    # nowhere. Link them to insights/<slug>.html when the template lands.
    t = C[l]
    out = []
    for i, (date, by, title, body) in enumerate(t['posts']):
        big = on_insights and i == 0
        cls = "post post-lg" if big else "post"
        h = title if on_insights else f'<a href="{url("insights",l)}">{title}</a>'
        inner = (f'<div><span class="by">{date} · {by}</span><h3>{h}</h3></div>'
                 f'<p>{body}</p>') if big else \
                (f'<span class="by">{date} · {by}</span><h3>{h}</h3>'
                 f'<p>{body}</p>')
        out.append(f'<article class="{cls}">{inner}</article>')
    return '<div class="posts">' + "".join(out) + '</div>'

# ══════════════════════════════════════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════════════════════════════════════
def page_index(l):
    t = C[l]
    stack = "".join(
        f'<a href="{url("services",l)}#{d[0]}" style="animation-delay:{.05*(i+1):.2f}s">'
        f'<span class="n">{i+1:02d}</span><span>{d[1]}</span>'
        f'<span class="c">{len(d[2])}</span></a>'
        for i, d in enumerate(t['disc']))
    stats = "".join(f'<div class="stat"><i></i><b dir="ltr">{n}</b><span>{s}</span></div>'
                    for n, s in t['stats'])
    return f"""<section class="hero"><div class="wrap">
  <div>
    <span class="eyebrow">{t['h_eyebrow']}</span>
    <h1>{t['h_title']}</h1>
    <p class="lede">{t['h_lede']}</p>
    <div class="hero-cta">
      <a class="btn btn-p" href="{url('contact',l)}">{t['consult']}</a>
      <a class="btn btn-s" href="{url('projects',l)}">{t['see_projects']}</a>
    </div>
  </div>
  <div class="stack">
    <header><strong>{t['h_stack']}</strong><span class="mono">{t['h_scope']}</span></header>
    {stack}
  </div>
</div></section>

<section class="stats" aria-label="{t['h_stack']}"><div class="wrap">{stats}</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head split"><h2>{t['h_disc_title']}</h2><p>{t['h_disc_lede']}</p></div>
  {disc_cards(l)}
</div></section>

<section class="sec sec-alt"><div class="wrap">
  <div class="sec-head split"><h2>{t['h_proj_title']}</h2><p>{t['h_proj_lede']}</p></div>
  {proj_cards(l)}
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><h2>{t['h_tl_title']}</h2><p>{t['h_tl_lede']}</p></div>
  {timeline(l)}
</div></section>

<section class="sec sec-alt"><div class="wrap">
  <div class="sec-head"><h2>{t['h_part_title']}</h2><p>{t['h_part_lede']}</p></div>
  {partners_grid()}
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head split"><h2>{t['h_ins_title']}</h2><p>{t['h_ins_lede']}</p></div>
  {posts(l)}
</div></section>
{cta(l)}"""

def page_about(l):
    t = C[l]
    story = "".join(f"<p style='margin-bottom:var(--s2)'>{p}</p>" for p in t['a_story'])
    vals = "".join(f'<div class="val"><span class="n">{i+1:02d}</span><h3>{h}</h3><p>{p}</p></div>'
                   for i, (h, p) in enumerate(t['a_vals']))
    stats = "".join(f'<div class="stat"><i></i><b dir="ltr">{n}</b><span>{s}</span></div>'
                    for n, s in t['stats'])
    return f"""{phead(l,'about',t['a_title'],t['a_lede'])}
<section class="stats"><div class="wrap">{stats}</div></section>
<section class="sec"><div class="wrap">
  <div class="duo" style="margin-bottom:var(--s5)">
    <div>
      <div class="sec-head" style="margin-bottom:var(--s3)"><h2>{t['a_story_h']}</h2></div>
      <div style="color:var(--ink-2);font-size:1.0625rem">{story}</div>
    </div>
    {photo('ceo', l, crop=True)}
  </div>
  {timeline(l)}
</div></section>
<section class="sec sec-alt"><div class="wrap">
  <div class="sec-head"><h2>{t['a_vals_h']}</h2></div>
  <div class="vals">{vals}</div>
</div></section>
<section class="sec"><div class="wrap">
  <div class="sec-head split"><h2>{t['a_team_h']}</h2><p>{t['a_team_p']}</p></div>
  <div class="gal">{photo('team-riyadh', l, crop=True)}{photo('team-kozhikode', l, crop=True)}{photo('qsys-training', l, crop=True)}</div>
</div></section>
<section class="sec sec-alt"><div class="wrap">
  <div class="sec-head split"><h2>{t['a_where_h']}</h2><p>{t['a_where']}</p></div>
  {partners_grid()}
</div></section>
{cta(l)}"""

def page_services(l):
    # Every card links to its detail page (service-<slug>.html), whose slug
    # matches the live site via content.SERVICE_SLUGS.
    t = C[l]
    en_subs = C['en']['disc']
    arr = "←" if l == "ar" else "→"
    chips = f'<a class="on" href="#svc-top" data-all="1">{t["s_all"]}</a>' + "".join(
        f'<a href="#{d[0]}">{d[1]}</a>' for d in t['disc'])
    cats = []
    for i, (slug, name, subs, std, blurb) in enumerate(t['disc']):
        cards = ""
        for j, s in enumerate(subs):
            surl = url("service-" + SERVICE_SLUGS[en_subs[i][2][j]], l)
            cards += (f'<article class="svc"><h3><a href="{surl}">{s}</a></h3>'
                      f'<p>{t["svc_blurbs"][s]}</p>'
                      f'<a class="more" href="{surl}">{t["read"]} {arr}</a></article>')
        cats.append(f"""<section class="cat" id="{slug}">
  <div class="cat-head">
    <div><span class="num">{i+1:02d} — {len(subs)}</span><h2>{name}</h2></div>
    <div><p>{blurb}</p><p class="mono" style="margin-top:14px" dir="ltr">{std}</p></div>
  </div>
  <div class="svcs">{cards}</div>
</section>""")
    return f"""{phead(l,'services',t['s_title'],t['s_lede'])}
<div class="wrap" id="svc-top"><div class="filters" id="svcFilters">{chips}</div>{"".join(cats)}</div>
{cta(l)}
<script>
const fl=document.getElementById('svcFilters');
fl&&fl.addEventListener('click',ev=>{{const a=ev.target.closest('a');if(!a)return;
  fl.querySelectorAll('a').forEach(x=>x.classList.remove('on'));a.classList.add('on');}});
</script>"""

def page_projects(l):
    t = C[l]
    feats = "".join(f'<div class="val"><span class="n">{i+1:02d}</span><h3>{h}</h3><p>{p}</p></div>'
                    for i, (h, p) in enumerate(t['pj_feat']))
    sectors = sorted({p[0] for p in t['proj']})
    chips = f'<button class="on" aria-pressed="true">{t["s_all"]}</button>' + "".join(
        f'<button data-sector="{e(s)}" aria-pressed="false">{s}</button>' for s in sectors)
    gal = "".join(photo(k, l, crop=True) for k in
                  ('control-room','videowall-install','videowall-mounts',
                   'fire-alarm-wiring','detector-testing','site-survey'))
    return f"""{phead(l,'projects',t['pj_title'],t['pj_lede'])}
<section class="sec"><div class="wrap">
  <div class="filters" id="pjFilters" style="margin-bottom:var(--s4)">{chips}</div>
  {proj_cards(l)}
</div></section>
<section class="sec sec-alt"><div class="wrap">
  <div class="sec-head split"><h2>{t['pj_gal_h']}</h2><p>{t['pj_gal_p']}</p></div>
  <div class="gal">{gal}</div>
</div></section>
<section class="sec"><div class="wrap">
  <div class="sec-head"><h2>{t['pj_feat_h']}</h2></div>
  <div class="vals">{feats}</div>
</div></section>
{cta(l)}
<script>
const pf=document.getElementById('pjFilters');
pf&&pf.addEventListener('click',ev=>{{
  const btn=ev.target.closest('button');if(!btn)return;
  pf.querySelectorAll('button').forEach(x=>{{x.classList.remove('on');
    x.setAttribute('aria-pressed','false');}});
  btn.classList.add('on');btn.setAttribute('aria-pressed','true');
  const s=btn.dataset.sector;
  document.querySelectorAll('.proj').forEach(p=>{{
    p.hidden=!!s&&p.dataset.sector!==s;}});
}});
</script>"""

def page_insights(l):
    t = C[l]
    return f"""{phead(l,'insights',t['i_title'],t['i_lede'])}
<section class="sec"><div class="wrap">{posts(l, on_insights=True)}</div></section>
{cta(l)}"""

def page_contact(l):
    import json
    t = C[l]
    f = t['c_f']
    arr = "←" if l == "ar" else "→"
    title_js = json.dumps(t['map_h'], ensure_ascii=False)
    opts = "".join(f"<option>{o}</option>" for o in t['c_types'])
    # office cards double as the map switcher (data-off)
    offices = "".join(f"""<div class="office-card{' on' if i == 0 else ''}" data-off="{i}"
      role="button" tabindex="0" aria-pressed="{'true' if i == 0 else 'false'}">
      <h3>{o[0]}</h3>
      <p>{o[1]}<br>{o[2]}<br>{o[3]}</p>
      <div class="rows"><a href="tel:{o[5]}" dir="ltr">{o[4]}</a></div>
      <a class="dirlink" href="{maps_link(i)}" rel="noopener" target="_blank">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          stroke-width="1.8"><path d="M12 21s7-6.3 7-11a7 7 0 10-14 0c0 4.7 7 11 7 11z"/>
          <circle cx="12" cy="10" r="2.6"/></svg>{t['directions']} {arr}</a>
      </div>""" for i, o in enumerate(t['offices']))
    tabs = "".join(
        ('<button class="on" aria-pressed="true"' if i == 0
         else '<button aria-pressed="false"')
        + f' data-off="{i}">{n}</button>'
        for i, n in enumerate(t['map_tabs']))
    map_off = json.dumps([
        {"src": maps_embed(i, l),
         "cap": f"{o[2]}, {o[3]}",
         "dir": maps_link(i)}
        for i, o in enumerate(t['offices'])], ensure_ascii=False)
    mail_meta = json.dumps({
        "to": "sales@datacore.com.sa",
        "subject": t['mail_subject'],
        "regarding": t['svc_enquiry_prefix'],
        "labels": [f['name'], f['company'], f['email'], f['phone'],
                   f['type'], f['project'], f['msg']]}, ensure_ascii=False)
    # LocalBusiness per office; Riyadh carries verified coordinates
    lat, lng = OFFICE_GEO[0][0].split(",")
    biz_ld = json.dumps([
        {"@context": "https://schema.org", "@type": "LocalBusiness",
         "name": "Datacore Solutions", "url": BASE,
         "telephone": "+966115128888",
         "geo": {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng},
         "address": {"@type": "PostalAddress",
             "streetAddress": "Office 503, Dabbab Complex, Dabbab St",
             "addressLocality": "Riyadh", "postalCode": "12626",
             "addressCountry": "SA"}},
        {"@context": "https://schema.org", "@type": "LocalBusiness",
         "name": "DCS Advanced Technologies L.L.C", "url": BASE,
         "telephone": "+971527536070",
         "address": {"@type": "PostalAddress",
             "streetAddress": "OF09-390, Um Hurair Second",
             "addressLocality": "Dubai", "addressCountry": "AE"}},
        {"@context": "https://schema.org", "@type": "LocalBusiness",
         "name": "Artifitia Solutions LLP", "url": BASE,
         "telephone": "+914953501154",
         "address": {"@type": "PostalAddress",
             "streetAddress": "No. 26, Sahya Building, Govt Cyberpark",
             "addressLocality": "Kozhikode", "postalCode": "673016",
             "addressCountry": "IN"}},
    ], ensure_ascii=False)
    return f"""{phead(l,'contact',t['c_title'],t['c_lede'])}
<section class="sec"><div class="wrap">
  <div class="sec-head" style="margin-bottom:var(--s3)"><h2>{t['c_offices_h']}</h2></div>
  <div class="geo-grid">
    <div class="offices-list" id="officeList">{offices}</div>
    <div class="map-col">
      <div class="map-tabs" id="mapTabs">{tabs}</div>
      <div class="map" id="map"><iframe src="{maps_embed(0,l)}" loading="lazy"
        title={title_js} referrerpolicy="no-referrer-when-downgrade"
        allowfullscreen></iframe></div>
      <p class="map-cap"><span id="mapCap">{t['offices'][0][2]}, {t['offices'][0][3]}</span> ·
        <a id="mapDir" href="{maps_link(0)}" rel="noopener" target="_blank">{t['directions']}</a></p>
    </div>
  </div>
</div></section>

<section class="sec sec-alt"><div class="wrap"><div class="contact-grid">
  <div>
    <form class="form" id="enquiry">
      <div class="sec-head" style="margin-bottom:var(--s3)"><h2>{t['c_form_h']}</h2></div>
      <div class="two">
        <div class="field"><label for="cn">{f['name']}</label>
          <input id="cn" name="name" autocomplete="name" required></div>
        <div class="field"><label for="cc">{f['company']}</label>
          <input id="cc" name="company" autocomplete="organization"></div>
      </div>
      <div class="two">
        <div class="field"><label for="ce">{f['email']}</label>
          <input id="ce" name="email" type="email" dir="ltr" autocomplete="email" required></div>
        <div class="field"><label for="cp">{f['phone']}</label>
          <input id="cp" name="phone" type="tel" dir="ltr" autocomplete="tel" placeholder="+966"></div>
      </div>
      <div class="field"><label for="ct">{f['type']}</label>
        <select id="ct" name="type">{opts}</select></div>
      <div class="field"><label for="cj">{f['project']}
        <span class="hint">— {f['project_hint']}</span></label><input id="cj" name="project"></div>
      <div class="field"><label for="cm">{f['msg']}</label>
        <textarea id="cm" name="message" rows="5"></textarea></div>
      <button class="btn btn-p" type="submit">{f['send']}</button>
      <p class="formnote">{f['note']}</p>
    </form>
  </div>
  <div>
    <div class="sec-head" style="margin-bottom:var(--s2)"><h2>{t['c_other_h']}</h2></div>
    <div class="office-card"><div class="rows">
      <a href="mailto:sales@datacore.com.sa" dir="ltr">sales@datacore.com.sa</a>
      <a href="mailto:info@datacore.com.sa" dir="ltr">info@datacore.com.sa</a>
      <a href="mailto:careers@datacore.com.sa" dir="ltr">careers@datacore.com.sa</a>
      <a href="https://wa.me/{WHATSAPP}" rel="noopener" target="_blank">{t['f_whatsapp']}</a>
    </div></div>
    <div class="sec-head" style="margin:var(--s4) 0 var(--s2)"><h2>{t['follow_h']}</h2></div>
    <p style="color:var(--ink-2)">{t['follow_p']}</p>
    {soc_buttons()}
  </div>
</div></div></section>
<script>
/* The map now loads directly (owner decision, Sep 2026) but stays lazy, so
   it never competes with first paint. Office cards and tabs both switch it. */
const MOFF={map_off};
const mw=document.getElementById('map'),tabs=document.getElementById('mapTabs'),
      list=document.getElementById('officeList');
function pick(i){{
  tabs.querySelectorAll('button').forEach(x=>{{
    const on=+x.dataset.off===i;
    x.classList.toggle('on',on);x.setAttribute('aria-pressed',String(on));}});
  list.querySelectorAll('.office-card').forEach(c=>{{
    const on=+c.dataset.off===i;
    c.classList.toggle('on',on);c.setAttribute('aria-pressed',String(on));}});
  document.getElementById('mapCap').textContent=MOFF[i].cap;
  document.getElementById('mapDir').href=MOFF[i].dir;
  const fr=mw.querySelector('iframe');
  if(fr&&fr.src!==MOFF[i].src)fr.src=MOFF[i].src;
}}
tabs.addEventListener('click',ev=>{{
  const b=ev.target.closest('button');if(b)pick(+b.dataset.off);}});
list.addEventListener('click',ev=>{{
  if(ev.target.closest('a'))return;          // tel/directions keep working
  const c=ev.target.closest('.office-card');if(c)pick(+c.dataset.off);}});
list.addEventListener('keydown',ev=>{{
  if(ev.key!=='Enter'&&ev.key!==' ')return;
  const c=ev.target.closest('.office-card');
  if(c){{ev.preventDefault();pick(+c.dataset.off);}}}});
/* No back end yet: submitting opens a pre-filled email to sales@ so the
   form genuinely works today. Swap for a POST when the RFQ service lands. */
const eq=document.getElementById('enquiry');
const M={mail_meta};
eq.addEventListener('submit',ev=>{{
  ev.preventDefault();
  const vals=[eq.name.value,eq.company.value,eq.email.value,eq.phone.value,
              eq.type.value,eq.project.value,eq.message.value];
  const body=M.labels.map((lab,i)=>lab+": "+(vals[i]||"—")).join("\\r\\n");
  location.href="mailto:"+M.to+"?subject="+encodeURIComponent(M.subject+" — "+eq.type.value)
    +"&body="+encodeURIComponent(body);
}});
/* arriving from a service page pre-fills the enquiry */
const svc=new URLSearchParams(location.search).get('service');
if(svc){{
  eq.message.value=M.regarding+": "+svc;
  eq.scrollIntoView({{block:'start'}});
  eq.name.focus();
}}
</script>
<script type="application/ld+json">{biz_ld}</script>"""

# ── service detail pages ──────────────────────────────────────────────────
def service_page(slug, l):
    """One of the 38 service detail pages. EN body copy is the client's own
    live-site text (src/data/services-copy.json); AR is its in-repo Arabic
    edition (services-copy-ar.json) awaiting the same native review as the
    rest of the Arabic."""
    import json
    t = C[l]
    info = _slug_names[slug]
    name = info[l]
    disc = t['disc'][info['disc']]
    d = SVC_EN[slug]['en'] if l == 'en' else SVC_AR[slug]
    h1 = H1_FIX.get(slug, d['h1']) if l == 'en' else d['h1']

    # the live site left ~10 pages with the generic site title/description —
    # derive proper unique meta for those
    title = d['title'].strip()
    if title in ("Datacore Solutions", ""):
        title = f"{h1} in Saudi Arabia | Datacore"
    desc = d['desc'].strip()
    if desc.startswith("DataCore provides integrated technology") or not desc:
        desc = d['intro'] if len(d['intro']) <= 158 else d['intro'][:155] + "…"

    body = []
    for s in d['sections']:
        lis = s.get('lis', [])
        ps = [p for p in s.get('ps', []) if p not in lis]  # live pages repeat lists as <p>s
        sec = f"<h2>{e(s['h'])}</h2>"
        sec += "".join(f"<p>{e(p)}</p>" for p in ps)
        if lis:
            sec += "<ul>" + "".join(f"<li>{e(li)}</li>" for li in lis) + "</ul>"
        body.append(sec)
    ph = photo(SERVICE_PHOTOS[slug], l) if slug in SERVICE_PHOTOS else ""

    rel = []
    for s_en in C['en']['disc'][info['disc']][2]:
        rslug = SERVICE_SLUGS[s_en]
        if rslug == slug:
            continue
        rel.append(f'<li><a href="{url("service-" + rslug, l)}">'
                   f'{_slug_names[rslug][l]}</a></li>')
    rel_html = ("<ul>" + "".join(rel) + "</ul>") if rel else ""
    ask = f'{url("contact", l)}?service={quote(name)}'

    ld = json.dumps({
        "@context": "https://schema.org", "@type": "Service",
        "name": h1, "serviceType": info['en'],
        "provider": {"@type": "Organization", "name": "Datacore Solutions",
                     "url": BASE},
        "areaServed": {"@type": "Country", "name": "Saudi Arabia"},
        "description": desc, "url": f"{BASE}{url('service-' + slug, l)}",
    }, ensure_ascii=False)
    crumbs_ld = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": t['home'],
             "item": f"{BASE}{url('index', l)}"},
            {"@type": "ListItem", "position": 2, "name": t['nav'][1][1],
             "item": f"{BASE}{url('services', l)}"},
            {"@type": "ListItem", "position": 3, "name": h1},
        ]}, ensure_ascii=False)

    return f"""<section class="phead"><div class="wrap">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{url('index',l)}">{t['home']}</a>
    <span>/</span><a href="{url('services',l)}">{t['nav'][1][1]}</a>
    <span>/</span><span>{e(h1)}</span></nav>
  <h1>{e(h1)}</h1><p>{e(d['intro'])}</p>
</div></section>
<div class="wrap"><div class="svc-grid">
  <div class="svc-body">
    {ph}
    {"".join(body)}
  </div>
  <aside class="svc-aside">
    <div class="box">
      <h3>{t['svc_in_disc']}</h3>
      <p style="font-weight:600"><a href="{url('services',l)}#{disc[0]}"
        style="text-decoration:none">{disc[1]}</a></p>
      <p class="mono" style="margin-top:10px" dir="ltr">{disc[3]}</p>
    </div>
    <div class="box">
      <h3>{t['svc_related']}</h3>
      {rel_html}
    </div>
    <a class="btn btn-p" href="{ask}">{t['svc_ask']}</a>
    <a class="btn btn-s" href="{url('products',l)}">{t['f_catalogue']}</a>
  </aside>
</div></div>
{cta(l)}
<script type="application/ld+json">{ld}</script>
<script type="application/ld+json">{crumbs_ld}</script>"""

# ── products page (catalogue) ─────────────────────────────────────────────
PROD_CSS = """
.cat-shell{display:grid;grid-template-columns:250px minmax(0,1fr);gap:var(--s4);
  align-items:start;padding-block:var(--s4) var(--s6)}
.facets{position:sticky;top:96px}
.fgroup{border-bottom:1px solid var(--line);padding:14px 0}
.fgroup:first-child{padding-top:0}
.fgroup>h3{margin:0 0 9px;font-size:.8125rem;font-weight:600;color:var(--ink-2);
  display:flex;justify-content:space-between;align-items:center}
.fgroup label{display:flex;align-items:center;gap:9px;padding:3px 0;font-size:.875rem;cursor:pointer}
.fgroup input{accent-color:var(--accent);width:15px;height:15px;flex:none}
.fgroup label span:last-child{margin-inline-start:auto;color:var(--ink-3);font-size:.75rem}
.fgroup label.off{opacity:.38}
.clear-all,.more{font-size:.8125rem;color:var(--accent);text-decoration:underline;padding:0}
.bar{display:flex;align-items:center;gap:12px;margin-bottom:14px;flex-wrap:wrap}
.count{font-size:.875rem;color:var(--ink-2)}
.count b{color:var(--ink)}
.bar-r{margin-inline-start:auto;display:flex;gap:8px;align-items:center}
select.sort{border:1px solid var(--line-2);background:var(--surface);border-radius:2px;
  padding:7px 10px;font-size:.875rem}
.vtog{display:flex;border:1px solid var(--line-2);border-radius:2px;overflow:hidden;
  background:var(--surface)}
.vtog button{padding:7px 10px;display:flex;color:var(--ink-2)}
.vtog button[aria-pressed=true]{background:var(--ink);color:#fff}
.chips{display:flex;gap:7px;flex-wrap:wrap;width:100%}
.chip{background:var(--surface);border:1px solid var(--line-2);border-radius:20px;
  padding:3px 8px 3px 11px;font-size:.8125rem;display:flex;align-items:center;gap:6px}
.pgrid{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(255px,1fr))}
.plist{display:flex;flex-direction:column;gap:9px}
.pcard{background:var(--surface);border:1px solid var(--line);border-radius:2px;
  display:flex;flex-direction:column;overflow:hidden}
.pcard:hover{border-color:var(--line-2)}
.pcard .thumb{background:var(--paper);height:132px;display:flex;align-items:center;
  justify-content:center;border-bottom:1px solid var(--line);cursor:pointer;color:#8A9299;
  width:100%;padding:0;overflow:hidden}
.thumb img{width:100%;height:100%;object-fit:contain;mix-blend-mode:multiply}
.linklike{font:inherit;font-weight:inherit;text-align:start;padding:0;color:inherit;
  cursor:pointer}
.linklike:hover{color:var(--accent)}
.pcard .body{padding:12px;display:flex;flex-direction:column;gap:7px;flex:1}
.pmeta{font-size:.75rem;color:var(--ink-2);display:flex;gap:6px}
.pmeta b{color:var(--ink);font-weight:600}
.pcard h4{margin:0;font-size:.9375rem;font-weight:500;line-height:1.35;cursor:pointer}
.pcard h4:hover{color:var(--accent)}
.sku{font-family:'IBM Plex Mono',monospace;font-size:.8125rem;direction:ltr;text-align:start}
.specs{display:flex;flex-wrap:wrap;gap:5px}
.spec{background:var(--paper);border:1px solid var(--line);border-radius:2px;
  padding:2px 6px;font-size:.75rem;color:var(--ink-2)}
.stock{font-size:.8125rem;display:flex;align-items:center;gap:6px;margin-top:auto}
.stock i{width:7px;height:7px;border-radius:50%;background:var(--brand);flex:none}
.stock.lead i{background:var(--amber)}.stock.lead{color:var(--amber)}
.add{display:flex;gap:7px;padding:0 12px 12px}
.add input{width:56px;border:1px solid var(--line-2);border-radius:2px;padding:7px 8px;
  text-align:center;direction:ltr}
.add button{flex:1;background:var(--ink);color:#fff;border-radius:2px;padding:7px 10px;
  font-size:.875rem;font-weight:500}
.add button:hover{background:var(--accent-d)}
.add button.in{background:var(--accent)}
.prow{background:var(--surface);border:1px solid var(--line);border-radius:2px;display:grid;
  grid-template-columns:56px minmax(0,2.2fr) minmax(0,1.6fr) 140px 150px;gap:14px;
  align-items:center;padding:10px 12px}
.prow .thumb{height:44px;background:var(--paper);border:1px solid var(--line);border-radius:2px;
  display:flex;align-items:center;justify-content:center;color:#8A9299;cursor:pointer;
  padding:0;overflow:hidden}
.prow h4{margin:0;font-size:.9375rem;font-weight:500;cursor:pointer}
.prow .add{padding:0}
.empty{background:var(--surface);border:1px dashed var(--line-2);border-radius:2px;
  padding:44px 24px;text-align:center}
.loadmore{margin:18px auto 0;display:block;border:1px solid var(--line-2);
  background:var(--surface);border-radius:2px;padding:10px 26px;font-weight:500}
.scrim{position:fixed;inset:0;background:rgba(26,27,31,.42);z-index:60;opacity:0;
  pointer-events:none;transition:opacity .2s}
.scrim.on{opacity:1;pointer-events:auto}
.drawer{position:fixed;top:0;bottom:0;inset-inline-end:0;width:min(470px,100%);
  background:var(--surface);z-index:61;display:flex;flex-direction:column;
  transform:translateX(102%);visibility:hidden;
  transition:transform .24s cubic-bezier(.3,.7,.3,1),visibility 0s .24s}
html[dir=rtl] .drawer{transform:translateX(-102%)}
.drawer.on{transform:none;visibility:visible;
  transition:transform .24s cubic-bezier(.3,.7,.3,1)}
.drawer>header{padding:16px 20px;border-bottom:1px solid var(--line);display:flex;
  align-items:center;gap:12px}
.drawer>header h2{margin:0;font-size:1.0625rem;font-weight:600}
.drawer>header button{margin-inline-start:auto;font-size:1.5rem;line-height:1;color:var(--ink-2)}
.dbody{overflow-y:auto;flex:1;padding:20px}
.dfoot{border-top:1px solid var(--line);padding:16px 20px;background:var(--paper)}
.pd-hero{background:var(--paper);border:1px solid var(--line);height:190px;display:flex;
  align-items:center;justify-content:center;color:#8A9299;margin-bottom:16px}
.stable{width:100%;border-collapse:collapse;margin-top:16px;font-size:.875rem}
.stable th{text-align:start;font-weight:500;color:var(--ink-2);padding:8px 0;
  border-bottom:1px solid var(--line);width:44%;vertical-align:top}
.stable td{padding:8px 0;border-bottom:1px solid var(--line)}
.line{display:grid;grid-template-columns:1fr auto;gap:4px 12px;padding:14px 0;
  border-bottom:1px solid var(--line)}
.line h5{margin:0;font-size:.9375rem;font-weight:500}
.line .lmeta{color:var(--ink-2);font-size:.8125rem}
.line .lctl{grid-column:2;grid-row:1/3;display:flex;flex-direction:column;align-items:end;gap:7px}
.line .lctl input{width:62px;border:1px solid var(--line-2);border-radius:2px;padding:6px;
  text-align:center;direction:ltr}
.line .lctl button{font-size:.8125rem;color:var(--ink-2);text-decoration:underline}
.line textarea{grid-column:1/-1;width:100%;border:1px solid var(--line-2);border-radius:2px;
  padding:7px 9px;font-size:.8125rem;min-height:34px;margin-top:6px}
.payload{background:var(--ink);color:#9FE6D6;border-radius:2px;padding:14px;
  font-family:'IBM Plex Mono',monospace;font-size:.75rem;line-height:1.6;overflow-x:auto;
  white-space:pre;margin-top:14px;direction:ltr;text-align:start}
.toast{position:fixed;inset-inline-end:20px;bottom:20px;background:var(--ink);color:#fff;
  padding:12px 18px;border-radius:2px;z-index:70;font-size:.875rem;transform:translateY(140%);
  transition:transform .22s;display:flex;gap:10px;align-items:center}
.toast.on{transform:none}
.toast i{width:7px;height:7px;border-radius:50%;background:var(--brand)}
.psearch{position:relative;max-width:620px;margin-top:var(--s3)}
.psearch input{width:100%;padding:12px 40px;border:1px solid var(--line-2);border-radius:2px;
  background:var(--surface)}
.psearch svg{position:absolute;inset-inline-start:13px;top:13px;color:var(--ink-3)}
.mobfilter{display:none}
@media(max-width:1080px){.prow{grid-template-columns:56px minmax(0,1fr) 150px}
  .prow .rspecs,.prow .rstock{display:none}}
@media(max-width:900px){
  .cat-shell{grid-template-columns:1fr}
  .facets{position:static;display:none;background:var(--surface);border:1px solid var(--line);
    padding:14px}
  .facets.on{display:block}
  .mobfilter{display:inline-flex;gap:8px;align-items:center;border:1px solid var(--line-2);
    background:var(--surface);border-radius:2px;padding:7px 13px;font-size:.875rem}
}
"""

PROD_STR = {
 'en':{'refine':'Refine','clear':'Clear all','f_cat':'Category','f_brand':'Brand',
   'f_avail':'Availability','in_stock':'In stock','on_order':'On order','lead_time':'Lead time',
   'days':'days','product':'product','products':'products','add':'Add to request',
   'added':'Added','loadmore':'Load more','details':'Product details',
   'rfq_title':'Your request',
   'rfq_empty_h':'Nothing added yet',
   'rfq_empty_p':'Browse the catalogue and add the parts you need. You can adjust quantities '
                 'before sending.',
   'remove':'Remove','ph_note':'Note for this line — variant, colour, mounting…',
   'f_name':'Your name','f_company':'Company','f_email':'Email','f_phone':'Phone',
   'f_project':'Project','ph_project':'e.g. Riyadh HQ — Level 3 fit-out','f_msg':'Anything else',
   'send':'Send request','unit':'unit','units':'units',
   'send_note':"You'll get an acknowledgement immediately and a priced quotation within one "
               "working day.",
   'empty_h':'No products match those filters',
   'empty_p':'Try removing a filter or searching a part number.',
   'toast_added':'added to your request','filters':'Filters','rfq':'Request for quote',
   'ph_search':'Search by part number, brand or description','received':'Request received',
   'received_p':'Sales will come back to you with a priced quotation within one working day.',
   'posts_to':'This is what posts to POST /api/rfq in the real build:',
   's_rel':'Sort: relevance','s_az':'Name A–Z','s_brand':'Brand','s_avail':'In stock first',
   'sort_label':'Sort','grid_label':'Grid view','list_label':'List view','close':'Close',
   'qty':'Quantity','crumb':'Breadcrumb',
   'need_contact':'Add your name and an email or phone number so we can reply.',
   'noscript':'The catalogue needs JavaScript. Email sales@datacore.com.sa and we will send '
              'the product list and a quotation instead.',
   'facet_titles':{'PoE':'PoE','Resolution':'Resolution','Type':'Type',
     'Category':'Cable category','Rack':'Rack size','Standard':'Standard',
     'IP rating':'IP rating'}},
 'ar':{'refine':'تصفية','clear':'مسح الكل','f_cat':'الفئة','f_brand':'العلامة التجارية',
   'f_avail':'التوفر','in_stock':'متوفر','on_order':'تحت الطلب','lead_time':'مدة التوريد',
   'days':'يوم','product':'منتج','products':'منتج','add':'أضف إلى الطلب','added':'تمت الإضافة',
   'loadmore':'عرض المزيد','details':'تفاصيل المنتج',
   'rfq_title':'طلبك','rfq_empty_h':'لم تتم إضافة أي شيء بعد',
   'rfq_empty_p':'تصفح الكتالوج وأضف القطع التي تحتاجها. يمكنك تعديل الكميات قبل الإرسال.',
   'remove':'إزالة','ph_note':'ملاحظة لهذا البند — الطراز، اللون، طريقة التركيب…',
   'f_name':'الاسم','f_company':'الشركة','f_email':'البريد الإلكتروني','f_phone':'رقم الجوال',
   'f_project':'المشروع','ph_project':'مثال: المقر الرئيسي بالرياض — الدور الثالث',
   'f_msg':'ملاحظات إضافية','send':'إرسال الطلب','unit':'وحدة','units':'وحدة',
   'send_note':'ستصلك رسالة تأكيد فوراً وعرض سعر خلال يوم عمل واحد.',
   'empty_h':'لا توجد منتجات مطابقة','empty_p':'جرب إزالة أحد عوامل التصفية أو البحث برقم القطعة.',
   'toast_added':'أُضيف إلى طلبك','filters':'عوامل التصفية','rfq':'طلب عرض سعر',
   'ph_search':'ابحث برقم القطعة أو العلامة التجارية أو الوصف','received':'تم استلام طلبك',
   'received_p':'سيتواصل معك فريق المبيعات بعرض سعر خلال يوم عمل واحد.',
   'posts_to':'هذا ما يُرسل إلى POST /api/rfq في النسخة النهائية:',
   's_rel':'الترتيب: الأنسب','s_az':'الاسم أ–ي','s_brand':'العلامة التجارية',
   's_avail':'المتوفر أولاً',
   'sort_label':'الترتيب','grid_label':'عرض شبكي','list_label':'عرض قائمة','close':'إغلاق',
   'qty':'الكمية','crumb':'مسار التنقل',
   'need_contact':'أضف اسمك وبريدك الإلكتروني أو رقم جوالك حتى نتمكن من الرد.',
   'noscript':'يتطلب الكتالوج تفعيل JavaScript. راسل sales@datacore.com.sa وسنرسل لك قائمة '
              'المنتجات وعرض السعر.',
   'facet_titles':{'PoE':'PoE','Resolution':'الدقة','Type':'النوع',
     'Category':'فئة الكابل','Rack':'مقاس الراك','Standard':'المعيار',
     'IP rating':'تصنيف الحماية'}},
}

def page_products(l):
    t = C[l]
    s = PROD_STR[l]
    import json
    return f"""<section class="phead"><div class="wrap">
  <nav class="crumbs" aria-label="{s['crumb']}"><a href="{url('index',l)}">{t['home']}</a><span>/</span>
    <span>{t['pr_title']}</span></nav>
  <h1>{t['pr_title']}</h1><p>{t['pr_lede']}</p>
  <div class="psearch">
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      stroke-width="2.2"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>
    <input id="q" type="search" placeholder="{s['ph_search']}" autocomplete="off"
      aria-label="{s['ph_search']}">
  </div>
  <noscript><p class="formnote" style="text-align:start;margin-top:16px">{s['noscript']}</p></noscript>
</div></section>

<div class="wrap"><div class="cat-shell">
  <aside class="facets" id="facets"></aside>
  <div>
    <div class="bar">
      <button class="mobfilter" id="mobFilter" aria-expanded="false"
        aria-controls="facets">{s['filters']}</button>
      <span class="count" id="count" aria-live="polite"></span>
      <div class="bar-r">
        <button class="btn btn-p" id="openRfq">{s['rfq']} <b id="rfqCount">0</b></button>
        <select class="sort" id="sort" aria-label="{s['sort_label']}">
          <option value="rel">{s['s_rel']}</option><option value="az">{s['s_az']}</option>
          <option value="brand">{s['s_brand']}</option><option value="avail">{s['s_avail']}</option>
        </select>
        <div class="vtog">
          <button id="vGrid" aria-pressed="true" aria-label="{s['grid_label']}">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
            <rect x="3" y="3" width="8" height="8" rx="1"/><rect x="13" y="3" width="8" height="8" rx="1"/>
            <rect x="3" y="13" width="8" height="8" rx="1"/><rect x="13" y="13" width="8" height="8" rx="1"/></svg></button>
          <button id="vList" aria-pressed="false" aria-label="{s['list_label']}">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            stroke-width="2.2"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button>
        </div>
      </div>
      <div class="chips" id="chips"></div>
    </div>
    <div id="results"></div>
    <button class="loadmore" id="loadmore" hidden>{s['loadmore']}</button>
  </div>
</div></div>

<div class="scrim" id="scrim"></div>
<aside class="drawer" id="pdDrawer" role="dialog" aria-modal="true" aria-hidden="true"
  aria-label="{s['details']}">
  <header><h2>{s['details']}</h2><button class="x" aria-label="{s['close']}">&times;</button></header>
  <div class="dbody" id="pdBody"></div><div class="dfoot" id="pdFoot"></div>
</aside>
<aside class="drawer" id="rfqDrawer" role="dialog" aria-modal="true" aria-hidden="true"
  aria-label="{s['rfq_title']}">
  <header><h2>{s['rfq_title']}</h2><button class="x" aria-label="{s['close']}">&times;</button></header>
  <div class="dbody" id="rfqBody"></div><div class="dfoot" id="rfqFoot"></div>
</aside>
<div class="toast" id="toast" role="status"><i></i><span id="toastMsg"></span></div>

<script>
{P_DATA}
{P_GLYPH}
{P_ICO}
const SPEC_FACETS=["PoE","Resolution","Type","Category","Rack","Standard","IP rating"];
const S={{q:"",cat:[],brand:[],avail:[],spec:{{}},sort:"rel",view:"grid",shown:12,rfq:[]}};
const L={json.dumps(s, ensure_ascii=False)};
const T=k=>L[k]||k, FT=k=>(L.facet_titles||{{}})[k]||k, PAGE=12, $=q=>document.querySelector(q);
const esc=x=>String(x).replace(/[&<>"]/g,c=>({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}}[c]));
/* The basket survives navigation and reload. localStorage can throw
   (private windows, file://) — degrade to an in-memory basket. */
const saveRfq=()=>{{try{{localStorage.setItem("dc-rfq",JSON.stringify(S.rfq));}}catch(e){{}}}};
try{{const st=JSON.parse(localStorage.getItem("dc-rfq")||"[]");
  if(Array.isArray(st))S.rfq=st.filter(x=>x&&P.some(p=>p.sku===x.sku));}}catch(e){{}}

function match(p,skip){{
  if(S.q){{const t=(p.sku+" "+p.n+" "+p.b+" "+p.c+" "
      +Object.values(p.specs).join(" ")).toLowerCase();
    if(!S.q.toLowerCase().split(/\\s+/).every(w=>t.includes(w)))return false;}}
  if(skip!=="cat"&&S.cat.length&&!S.cat.includes(p.c))return false;
  if(skip!=="brand"&&S.brand.length&&!S.brand.includes(p.b))return false;
  if(skip!=="avail"&&S.avail.length&&!S.avail.includes(p.avail))return false;
  for(const k in S.spec){{if(skip==="spec:"+k)continue;
    if(S.spec[k].length&&!S.spec[k].includes(p.specs[k]))return false;}}
  return true;
}}
const results=()=>{{let r=P.filter(p=>match(p,null));
  if(S.sort==="az")r.sort((a,b)=>a.n.localeCompare(b.n));
  if(S.sort==="brand")r.sort((a,b)=>a.b.localeCompare(b.b)||a.n.localeCompare(b.n));
  if(S.sort==="avail")r.sort((a,b)=>(a.avail==="stock"?0:1)-(b.avail==="stock"?0:1));
  return r;}};
function tally(dim,get){{const m={{}};P.filter(p=>match(p,dim)).forEach(p=>{{
  const v=get(p); if(v!=null)m[v]=(m[v]||0)+1;}}); return m;}}
function fgroup(title,dim,counts,selected,limit){{
  const all=[...new Set([...Object.keys(counts),...selected])].sort();
  const open=all.length<=(limit||7)||S["_m_"+dim], list=open?all:all.slice(0,limit||7);
  let h=`<div class="fgroup"><h3>${{esc(title)}}</h3>`;
  list.forEach(v=>{{const c=counts[v]||0,on=selected.includes(v);
    h+=`<label class="${{c===0&&!on?"off":""}}"><input type="checkbox" data-dim="${{esc(dim)}}"
      value="${{esc(v)}}" ${{on?"checked":""}}><span>${{esc(v)}}</span><span>${{c}}</span></label>`;}});
  if(all.length>list.length)h+=`<button class="more" data-more="${{esc(dim)}}"
    aria-expanded="false">+${{all.length-list.length}}</button>`;
  return h+`</div>`;}}
function renderFacets(){{
  const n=S.cat.length+S.brand.length+S.avail.length+Object.values(S.spec).flat().length;
  let h=`<div class="fgroup"><h3><span>${{T("refine")}}</span>${{n?`<button class="clear-all"
    id="clearAll">${{T("clear")}}</button>`:""}}</h3></div>`;
  h+=fgroup(T("f_cat"),"cat",tally("cat",p=>p.c),S.cat,9);
  h+=fgroup(T("f_brand"),"brand",tally("brand",p=>p.b),S.brand,7);
  h+=fgroup(T("f_avail"),"avail",tally("avail",p=>p.avail==="stock"?T("in_stock"):T("on_order")),
      S.avail.map(v=>v==="stock"?T("in_stock"):T("on_order")),4);
  SPEC_FACETS.forEach(k=>{{const c=tally("spec:"+k,p=>p.specs[k]);
    if(Object.keys(c).length>1)h+=fgroup(FT(k),"spec:"+k,c,S.spec[k]||[],6);}});
  $("#facets").innerHTML=h;}}
const stockHtml=p=>p.avail==="stock"?`<div class="stock"><i></i>${{T("in_stock")}}</div>`
  :`<div class="stock lead"><i></i>${{T("lead_time")}} ${{p.lead}} ${{T("days")}}</div>`;
function addHtml(p){{const c=S.rfq.find(l=>l.sku===p.sku);
  return `<div class="add"><input type="number" min="1" value="${{c?c.qty:1}}"
    aria-label="${{T("qty")}}" data-qty="${{esc(p.sku)}}"><button data-add="${{esc(p.sku)}}"
    class="${{c?"in":""}}">${{c?T("added"):T("add")}}</button></div>`;}}
const chipsOf=p=>Object.entries(p.specs).slice(0,3).map(([k,v])=>
  `<span class="spec">${{esc(v)}}</span>`).join("");
/* photo when the product has one (assets/products/<sku>.jpg via build),
   category glyph otherwise */
const thumb=(p,s)=>p.img?`<img src="${{esc(p.img)}}" alt="" loading="lazy">`:ico(p.g,s);
function renderResults(){{
  const r=results(),sl=r.slice(0,S.shown);
  $("#count").innerHTML=`<b>${{r.length}}</b> ${{r.length===1?T("product"):T("products")}}`;
  const ch=[];S.cat.forEach(v=>ch.push(["cat",v]));S.brand.forEach(v=>ch.push(["brand",v]));
  S.avail.forEach(v=>ch.push(["avail",v==="stock"?T("in_stock"):T("on_order")]));
  Object.entries(S.spec).forEach(([k,vs])=>vs.forEach(v=>ch.push(["spec:"+k,v])));
  $("#chips").innerHTML=ch.map(([d,v])=>`<span class="chip">${{esc(v)}}<button
    data-chip="${{esc(d)}}" data-val="${{esc(v)}}" aria-label="Remove">&times;</button></span>`).join("");
  if(!r.length){{$("#results").innerHTML=`<div class="empty"><h3>${{T("empty_h")}}</h3>
    <p style="color:var(--ink-2);margin:6px 0 16px">${{T("empty_p")}}</p>
    <button class="loadmore" id="clearAll2">${{T("clear")}}</button></div>`;
    $("#loadmore").hidden=true;return;}}
  if(S.view==="grid"){{$("#results").className="pgrid";
    $("#results").innerHTML=sl.map(p=>`<article class="pcard">
      <button class="thumb" data-open="${{esc(p.sku)}}"
        aria-label="${{T("details")}}: ${{esc(p.n)}}">${{thumb(p,46)}}</button>
      <div class="body"><div class="pmeta"><b>${{esc(p.b)}}</b><span>·</span><span>${{esc(p.c)}}</span></div>
      <h4><button class="linklike" data-open="${{esc(p.sku)}}">${{esc(p.n)}}</button></h4>
      <div class="sku">${{esc(p.sku)}}</div>
      <div class="specs">${{chipsOf(p)}}</div>${{stockHtml(p)}}</div>${{addHtml(p)}}</article>`).join("");
  }}else{{$("#results").className="plist";
    $("#results").innerHTML=sl.map(p=>`<article class="prow">
      <button class="thumb" data-open="${{esc(p.sku)}}"
        aria-label="${{T("details")}}: ${{esc(p.n)}}">${{thumb(p,24)}}</button>
      <div><h4><button class="linklike" data-open="${{esc(p.sku)}}">${{esc(p.n)}}</button></h4>
      <div class="pmeta"><b>${{esc(p.b)}}</b>
        <span>·</span><span class="sku">${{esc(p.sku)}}</span></div></div>
      <div class="specs rspecs">${{chipsOf(p)}}</div><div class="rstock">${{stockHtml(p)}}</div>
      ${{addHtml(p)}}</article>`).join("");}}
  $("#loadmore").hidden=r.length<=S.shown;}}
const renderCount=()=>$("#rfqCount").textContent=S.rfq.reduce((a,l)=>a+l.qty,0);
const render=()=>{{renderFacets();renderResults();renderCount();}};
let pdSku=null;
function openProduct(sku){{const p=P.find(x=>x.sku===sku);if(!p)return;
  pdSku=sku;
  $("#pdBody").innerHTML=`<div class="pd-hero">${{thumb(p,74)}}</div>
    <div class="pmeta"><b>${{esc(p.b)}}</b><span>·</span><span>${{esc(p.c)}}</span></div>
    <h3 style="margin:6px 0 4px;font-size:1.1875rem">${{esc(p.n)}}</h3>
    <div class="sku">${{esc(p.sku)}}</div>${{stockHtml(p)}}
    <table class="stable">${{Object.entries(p.specs).map(([k,v])=>
      `<tr><th>${{esc(k)}}</th><td>${{esc(v)}}</td></tr>`).join("")}}</table>`;
  $("#pdFoot").innerHTML=addHtml(p);show("#pdDrawer");}}
function addToRfq(sku,qty){{const l=S.rfq.find(x=>x.sku===sku);
  if(l)l.qty=qty;else S.rfq.push({{sku,qty,note:""}});
  saveRfq();
  toast(`${{sku}} — ${{T("toast_added")}}`);render();
  // the details drawer keeps its own Add button in sync
  if(pdSku===sku&&$("#pdDrawer").classList.contains("on"))
    $("#pdFoot").innerHTML=addHtml(P.find(x=>x.sku===sku));
  if($("#rfqDrawer").classList.contains("on"))renderRfq();}}
function renderRfq(){{
  if(!S.rfq.length){{$("#rfqBody").innerHTML=`<div class="empty"><h3>${{T("rfq_empty_h")}}</h3>
    <p style="color:var(--ink-2);margin-top:6px">${{T("rfq_empty_p")}}</p></div>`;
    $("#rfqFoot").innerHTML=`<button class="btn btn-p" style="width:100%;justify-content:center"
      disabled>${{T("send")}}</button>`;return;}}
  $("#rfqBody").innerHTML=S.rfq.map(l=>{{const p=P.find(x=>x.sku===l.sku);
    return `<div class="line"><h5>${{esc(p.n)}}</h5>
      <div class="lmeta"><span class="sku">${{esc(p.sku)}}</span> · ${{esc(p.b)}}</div>
      <div class="lctl"><input type="number" min="1" value="${{l.qty}}" data-rqty="${{esc(l.sku)}}"
        aria-label="${{T("qty")}}"><button data-del="${{esc(l.sku)}}">${{T("remove")}}</button></div>
      <textarea data-note="${{esc(l.sku)}}" aria-label="${{T("ph_note")}}"
        placeholder="${{T("ph_note")}}">${{esc(l.note)}}</textarea>
    </div>`;}}).join("")+`<div style="margin-top:22px">
    <div class="two"><div class="field"><label for="rName">${{T("f_name")}}</label>
      <input id="rName" autocomplete="name"></div>
    <div class="field"><label for="rCo">${{T("f_company")}}</label>
      <input id="rCo" autocomplete="organization"></div></div>
    <div class="two"><div class="field"><label for="rEmail">${{T("f_email")}}</label>
      <input id="rEmail" type="email" dir="ltr" autocomplete="email"></div>
    <div class="field"><label for="rPhone">${{T("f_phone")}}</label>
      <input id="rPhone" type="tel" dir="ltr" autocomplete="tel" placeholder="+966"></div></div>
    <div class="field"><label for="rProj">${{T("f_project")}}</label><input id="rProj"
      placeholder="${{T("ph_project")}}"></div>
    <div class="field"><label for="rMsg">${{T("f_msg")}}</label>
      <textarea id="rMsg" rows="3"></textarea></div></div>`;
  const u=S.rfq.reduce((a,l)=>a+l.qty,0);
  $("#rfqFoot").innerHTML=`<button class="btn btn-p" id="send"
    style="width:100%;justify-content:center">${{T("send")}} — ${{u}}
    ${{u===1?T("unit"):T("units")}}</button><p class="formnote">${{T("send_note")}}</p>`;}}
let lastFocus=null;
const show=s=>{{lastFocus=document.activeElement;
  $("#scrim").classList.add("on");$(s).classList.add("on");
  $(s).setAttribute("aria-hidden","false");document.body.style.overflow="hidden";
  const x=$(s).querySelector(".x");x&&x.focus();}};
const hideAll=()=>{{$("#scrim").classList.remove("on");
  document.querySelectorAll(".drawer").forEach(d=>{{d.classList.remove("on");
    d.setAttribute("aria-hidden","true");}});document.body.style.overflow="";
  lastFocus&&lastFocus.focus&&lastFocus.focus();lastFocus=null;}};
let tt;const toast=m=>{{$("#toastMsg").textContent=m;$("#toast").classList.add("on");
  clearTimeout(tt);tt=setTimeout(()=>$("#toast").classList.remove("on"),2400);}};

$("#q").addEventListener("input",e=>{{S.q=e.target.value;S.shown=PAGE;render();}});
$("#sort").addEventListener("change",e=>{{S.sort=e.target.value;renderResults();}});
$("#vGrid").addEventListener("click",()=>{{S.view="grid";$("#vGrid").ariaPressed="true";
  $("#vList").ariaPressed="false";renderResults();}});
$("#vList").addEventListener("click",()=>{{S.view="list";$("#vList").ariaPressed="true";
  $("#vGrid").ariaPressed="false";renderResults();}});
$("#loadmore").addEventListener("click",()=>{{S.shown+=PAGE;renderResults();}});
$("#mobFilter").addEventListener("click",()=>{{
  const on=$("#facets").classList.toggle("on");
  $("#mobFilter").setAttribute("aria-expanded",String(on));}});
$("#facets").addEventListener("change",ev=>{{const d=ev.target.dataset.dim;if(!d)return;
  let v=ev.target.value,arr;
  if(d==="cat")arr=S.cat;else if(d==="brand")arr=S.brand;
  else if(d==="avail"){{arr=S.avail;v=(v===T("in_stock"))?"stock":"lead";}}
  else{{const k=d.slice(5);S.spec[k]=S.spec[k]||[];arr=S.spec[k];}}
  const i=arr.indexOf(v);ev.target.checked?(i<0&&arr.push(v)):(i>-1&&arr.splice(i,1));
  S.shown=PAGE;render();}});
$("#facets").addEventListener("click",ev=>{{
  if(ev.target.dataset.more){{S["_m_"+ev.target.dataset.more]=true;renderFacets();}}
  if(ev.target.id==="clearAll"){{S.cat=[];S.brand=[];S.avail=[];S.spec={{}};S.shown=PAGE;render();}}}});
$("#chips").addEventListener("click",ev=>{{const d=ev.target.dataset.chip;if(!d)return;
  const v=ev.target.dataset.val;
  if(d==="cat")S.cat=S.cat.filter(x=>x!==v);
  else if(d==="brand")S.brand=S.brand.filter(x=>x!==v);
  else if(d==="avail"){{const k=(v===T("in_stock"))?"stock":"lead";S.avail=S.avail.filter(x=>x!==k);}}
  else{{const k=d.slice(5);S.spec[k]=(S.spec[k]||[]).filter(x=>x!==v);}}
  render();}});
document.addEventListener("click",ev=>{{
  const o=ev.target.closest("[data-open]");if(o){{openProduct(o.dataset.open);return;}}
  const a=ev.target.closest("[data-add]");
  if(a){{const sku=a.dataset.add,qi=(a.closest(".add")||document)
    .querySelector(`[data-qty="${{CSS.escape(sku)}}"]`);
    addToRfq(sku,Math.max(1,parseInt(qi&&qi.value)||1));return;}}
  if(ev.target.id==="clearAll2"){{S.cat=[];S.brand=[];S.avail=[];S.spec={{}};S.q="";
    $("#q").value="";render();}}
  if(ev.target.closest("#openRfq")){{renderRfq();show("#rfqDrawer");}}
  if(ev.target.closest(".drawer > header .x")||ev.target.id==="scrim")hideAll();}});
$("#rfqBody").addEventListener("input",ev=>{{
  if(ev.target.dataset.rqty){{const l=S.rfq.find(x=>x.sku===ev.target.dataset.rqty);
    l.qty=Math.max(1,parseInt(ev.target.value)||1);renderCount();saveRfq();
    const u=S.rfq.reduce((a,x)=>a+x.qty,0);
    $("#rfqFoot").querySelector("button").textContent=
      `${{T("send")}} — ${{u}} ${{u===1?T("unit"):T("units")}}`;}}
  if(ev.target.dataset.note){{
    S.rfq.find(x=>x.sku===ev.target.dataset.note).note=ev.target.value;saveRfq();}}}});
$("#rfqBody").addEventListener("click",ev=>{{if(ev.target.dataset.del){{
  S.rfq=S.rfq.filter(l=>l.sku!==ev.target.dataset.del);saveRfq();renderRfq();render();}}}});
$("#rfqFoot").addEventListener("click",ev=>{{if(ev.target.id!=="send")return;
  // no back end yet, but don't accept a request nobody can answer
  if(!$("#rName").value.trim()||
     !($("#rEmail").value.trim()||$("#rPhone").value.trim())){{
    toast(T("need_contact"));
    ($("#rName").value.trim()?$("#rEmail"):$("#rName")).focus();return;}}
  const payload={{contact:{{name:$("#rName").value||"—",company:$("#rCo").value||"—",
    email:$("#rEmail").value||"—",phone:$("#rPhone").value||"—"}},
    project:$("#rProj").value||"—",message:$("#rMsg").value||"",
    lines:S.rfq.map(l=>({{sku:l.sku,qty:l.qty,note:l.note}})),
    locale:document.documentElement.lang,source:"web-catalogue"}};
  $("#rfqBody").innerHTML=`<div class="empty" style="border-style:solid">
    <h3>${{T("received")}}</h3><p style="color:var(--ink-2);margin-top:6px">${{T("received_p")}}</p></div>
    <p class="formnote" style="text-align:start;margin-top:18px">${{T("posts_to")}}</p>
    <div class="payload">${{esc(JSON.stringify(payload,null,2))}}</div>`;
  $("#rfqFoot").innerHTML="";S.rfq=[];saveRfq();renderCount();render();}});
document.addEventListener("keydown",ev=>{{if(ev.key==="Escape")hideAll();}});
render();
</script>"""

def org_ld():
    # Organization schema — facts mirror content.py, nothing invented.
    import json
    d = {
      "@context": "https://schema.org", "@type": "Organization",
      "name": "Datacore Solutions", "url": BASE, "foundingDate": "2007",
      "email": "info@datacore.com.sa", "telephone": "+966115128888",
      "sameAs": [u for _k, u, _n in SOCIALS],
      "address": [
        {"@type": "PostalAddress", "streetAddress": "Office 503, Dabbab Complex, Dabbab St",
         "addressLocality": "Riyadh", "postalCode": "12626", "addressCountry": "SA"},
        {"@type": "PostalAddress", "streetAddress": "OF09-390, Um Hurair Second",
         "addressLocality": "Dubai", "addressCountry": "AE"},
        {"@type": "PostalAddress", "streetAddress": "No. 26, Sahya Building, Govt Cyberpark",
         "addressLocality": "Kozhikode", "postalCode": "673016", "addressCountry": "IN"}],
    }
    return ('<script type="application/ld+json">'
            + json.dumps(d, ensure_ascii=False) + '</script>')

# ══════════════════════════════════════════════════════════════════════════
META = {
 'index':   ("Low-current systems integration in Saudi Arabia | Datacore Solutions",
             "Datacore designs, supplies, installs and maintains network, datacentre, security, "
             "audio-visual and life-safety systems across Saudi Arabia and the UAE. Since 2007.",
             "تكامل أنظمة التيار الخفيف في السعودية | داتاكور للحلول",
             "تصميم وتوريد وتركيب وصيانة أنظمة الشبكات ومراكز البيانات والأمن والأنظمة السمعية "
             "والبصرية والسلامة في السعودية والإمارات. منذ 2007."),
 'about':   ("About Datacore | Low-current integrator in Riyadh since 2007",
             "Founded in Jeddah in 2007, Datacore now delivers nine low-current disciplines "
             "in-house from Riyadh, Dubai and Kozhikode.",
             "من نحن | داتاكور، تكامل أنظمة التيار الخفيف منذ 2007",
             "تأسست في جدة عام 2007، وتنفذ داتاكور اليوم تسعة تخصصات في التيار الخفيف بكوادرها "
             "من الرياض ودبي وكوزيكود."),
 'services':("Services | 38 low-current services across nine disciplines | Datacore",
             "Network infrastructure, datacentre, surveillance, meeting rooms, audio-visual, "
             "signage, public address, IPTV and maintenance — all delivered in-house.",
             "خدماتنا | 38 خدمة في التيار الخفيف عبر تسعة تخصصات | داتاكور",
             "البنية التحتية للشبكات ومراكز البيانات والمراقبة وقاعات الاجتماعات والأنظمة "
             "السمعية والبصرية واللافتات والنداء الآلي و IPTV والصيانة."),
 'products':("Product catalogue | Request a quote | Datacore Solutions",
             "Browse network, security and audio-visual hardware and build a request for "
             "quotation. Priced quotations with lead times within one working day.",
             "كتالوج المنتجات | اطلب عرض سعر | داتاكور للحلول",
             "تصفح أجهزة الشبكات والأمن والأنظمة السمعية والبصرية وأنشئ طلب عرض سعر. عروض "
             "مسعّرة مع مدد التوريد خلال يوم عمل واحد."),
 'projects':("Projects | AOU, PSAU and TAQEEM case studies | Datacore",
             "Named clients, stated scope and the equipment deployed on recent low-current "
             "and audio-visual projects across Saudi Arabia.",
             "مشاريعنا | دراسات حالة | داتاكور",
             "عملاء بالاسم ونطاق عمل محدد والأجهزة المركّبة في مشاريع حديثة للتيار الخفيف "
             "والأنظمة السمعية والبصرية في المملكة."),
 'insights':("Technical notes | Datacore Solutions",
             "Notes from our engineers on public address standards, passive networks and the "
             "decisions that come up on real projects.",
             "ملاحظات تقنية | داتاكور للحلول",
             "ملاحظات من مهندسينا حول مواصفات أنظمة النداء والشبكات السلبية والقرارات التي "
             "تتكرر في المشاريع الفعلية."),
 'contact':("Contact | Riyadh, Dubai and Kozhikode | Datacore Solutions",
            "Send a BOQ, a schedule of materials or drawings and we return a priced scope and "
            "programme. Offices in Riyadh, Dubai and Kozhikode.",
            "تواصل معنا | الرياض ودبي وكوزيكود | داتاكور للحلول",
            "أرسل جدول الكميات أو المواد أو المخططات وسنعود بنطاق مسعّر وبرنامج زمني. مكاتبنا "
            "في الرياض ودبي وكوزيكود."),
}
BODY = {'index':page_index,'about':page_about,'services':page_services,
        'products':page_products,'projects':page_projects,'insights':page_insights,
        'contact':page_contact}

written = []
def write_page(name, doc):
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(doc)
    written.append((name, round(len(doc)/1024, 1)))

for l in ("en","ar"):
    for p in PAGES:
        m = META[p]
        title, desc = (m[0], m[1]) if l == "en" else (m[2], m[3])
        extra = PROD_CSS if p == "products" else ""
        body = BODY[p](l)
        if p in ("index", "contact"):
            body += org_ld()
        doc = head(l,p,title,desc,extra) + header(l,p) + body + footer(l)
        write_page(url(p,l), doc)

# ── 38 service detail pages per language ─────────────────────────────────
for l in ("en","ar"):
    for slug in SERVICE_SLUGS.values():
        d = SVC_EN[slug]['en'] if l == 'en' else SVC_AR[slug]
        h1 = H1_FIX.get(slug, d['h1']) if l == 'en' else d['h1']
        title = d['title'].strip()
        if title in ("Datacore Solutions", ""):
            title = f"{h1} in Saudi Arabia | Datacore"
        desc = d['desc'].strip()
        if desc.startswith("DataCore provides integrated technology") or not desc:
            desc = d['intro'] if len(d['intro']) <= 158 else d['intro'][:155] + "…"
        doc = (head(l, 'service-' + slug, title, desc)
               + header(l, 'services') + service_page(slug, l) + footer(l))
        write_page(url('service-' + slug, l), doc)

# ── utility pages ─────────────────────────────────────────────────────────
# Legal stubs: the old site's /terms-service and /privacy-policy don't exist
# in this build, and a dead footer link is worse than an honest placeholder.
# Both are noindex until the client supplies the real text (launch blocker —
# PDPL requires a privacy policy on a Saudi commercial site).
for l in ("en","ar"):
    t = C[l]
    brand = 'داتاكور للحلول' if l == 'ar' else 'Datacore Solutions'
    for p, heading in (("terms", t['f_terms']), ("privacy", t['f_privacy'])):
        doc = (head(l, p, f"{heading} | {brand}", t['legal_stub'], noindex=True)
               + header(l, p) + phead(l, p, heading, t['legal_stub'])
               + f'<section class="sec"><div class="wrap">'
                 f'<a class="btn btn-s" href="{url("index",l)}">{t["nf_home"]}</a>'
                 f'</div></section>' + footer(l))
        write_page(url(p, l), doc)
    doc = (head(l, '404', f"{t['nf_title']} | {brand}", t['nf_p'], noindex=True)
           + header(l, '404') + phead(l, '404', t['nf_title'], t['nf_p'])
           + f'<section class="sec"><div class="wrap">'
             f'<a class="btn btn-p" href="{url("index",l)}">{t["nf_home"]}</a>'
             f'</div></section>' + footer(l))
    write_page(url('404', l), doc)

# ── robots.txt + sitemap.xml ──────────────────────────────────────────────
import datetime
today = datetime.date.today().isoformat()
open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(
    f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
urls = [url(p, l) for l in ("en","ar") for p in PAGES]
urls += [url('service-' + s, l) for l in ("en","ar") for s in SERVICE_SLUGS.values()]
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    sm.append(f"  <url><loc>{BASE}{u}</loc><lastmod>{today}</lastmod></url>")
sm.append("</urlset>\n")
open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm))

# ── llms.txt: a concise, factual guide for AI answer engines (GEO) ───────
_svc_lines = "\n".join(
    f"- [{_slug_names[s]['en']}]({BASE}{url('service-' + s, 'en')})"
    for s in SERVICE_SLUGS.values())
open(os.path.join(OUT, "llms.txt"), "w", encoding="utf-8").write(f"""# Datacore Solutions

> Low-current / ELV systems integrator headquartered in Riyadh, Saudi Arabia,
> with entities in Dubai (DCS Advanced Technologies L.L.C) and Kozhikode,
> India (Artifitia Solutions LLP). Founded in Jeddah in 2007. Nine
> disciplines, 38 services, delivered in-house: design, supply, installation,
> commissioning and maintenance. English pages: *.html — Arabic: *-ar.html.

Contact: sales@datacore.com.sa · +966 11 512 8888 · {BASE}contact.html

## Main pages
- [Services]({BASE}services.html): nine disciplines, 38 services
- [Products]({BASE}products.html): catalogue with request-for-quotation
- [Projects]({BASE}projects.html): named case studies
- [About]({BASE}about.html): history since 2007, offices, values
- [Contact]({BASE}contact.html): offices, map, enquiry form

## Services
{_svc_lines}
""")

for n,k in written:
    print(f"{n:26s} {k:>7} KB")
print(f"\n{len(written)} pages + robots.txt + sitemap.xml written to {OUT}")
if _img:
    print(f"{len(_img)} product image(s) copied to assets/products/")
