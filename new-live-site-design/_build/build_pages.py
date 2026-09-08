# -*- coding: utf-8 -*-
"""Generate the mirror's functional pages (contact / projects / insights, EN+AR)
in the live Texta look. Each page loads the developed-site header + dark mode via
dc-overlay.css/js and the live-look content styles via dc-pages.css. Live body
HTML is not touched — these are brand-new pages the header's nav links point to."""
import os, json, html, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = r"C:\Users\afnan\Documents\Datacore\Datacore Website\datacore-live-mirror"
STR = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mirror_strings.json"), encoding="utf-8"))

def esc(s): return html.escape(str(s), quote=True)

# ── inline icons (stroke=currentColor) ──────────────────────────────────
def ic(p): return ('<svg viewBox="0 0 24 24" width="22" height="22" fill="none" '
    'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
    'stroke-linejoin="round" aria-hidden="true">' + p + '</svg>')
I_ARROW   = ic('<path d="M5 12h14M13 6l6 6-6 6"/>')
I_PIN     = ic('<path d="M12 21s7-5.5 7-11a7 7 0 10-14 0c0 5.5 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>')
I_PHONE   = ic('<path d="M22 16.9v3a2 2 0 01-2.2 2 19.8 19.8 0 01-8.6-3.1 19.5 19.5 0 01-6-6A19.8 19.8 0 012.1 4.2 2 2 0 014 2h3a2 2 0 012 1.7c.1.9.3 1.8.6 2.6a2 2 0 01-.4 2.1L8 9.6a16 16 0 006 6l1.2-1.2a2 2 0 012.1-.4c.8.3 1.7.5 2.6.6a2 2 0 011.7 2z"/>')
I_MAIL    = ic('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>')
I_DIR     = ic('<path d="M12 2l9 9-9 9-9-9 9-9z"/><path d="M9 12h4v3l4-4-4-4v3H9z"/>')
I_DOWN    = ic('<path d="M12 3v13M7 11l5 5 5-5M5 21h14"/>')
FEAT_ICONS = [
  ic('<path d="M12 2a7 7 0 00-4 12.7c.6.5 1 1.2 1 2h6c0-.8.4-1.5 1-2A7 7 0 0012 2zM9 21h6M10 18h4"/>'),
  ic('<path d="M3 7l9-4 9 4-9 4-9-4z"/><path d="M3 12l9 4 9-4M3 17l9 4 9-4"/>'),
  ic('<circle cx="9" cy="8" r="3"/><path d="M15 8a3 3 0 010 6M3 20a6 6 0 0112 0M15 14a6 6 0 016 6"/>'),
  ic('<rect x="9" y="3" width="6" height="5" rx="1"/><rect x="3" y="16" width="6" height="5" rx="1"/><rect x="15" y="16" width="6" height="5" rx="1"/><path d="M12 8v4M12 12H6v4M12 12h6v4"/>'),
  ic('<path d="M12 14l4-4M4 20a8 8 0 1116 0"/><circle cx="12" cy="14" r="1"/>'),
]

DISCIPLINES = [  # (services.html?id=, EN, AR) — matches the header dropdown
  ('network-infrastructure-services','Network Infrastructure','البنية التحتية للشبكات'),
  ('datacenter-solutions','Datacenter Solutions','حلول مراكز البيانات'),
  ('surveillance-and-security-solutions','Surveillance & Security','المراقبة والأمن'),
  ('meeting-room-solutions','Meeting Room Solutions','قاعات الاجتماعات'),
  ('audio-visual-solutions','Audio-Visual Solutions','الحلول السمعية والبصرية'),
  ('digital-signage-amp-video-walls','Signage & Video Walls','اللافتات وشاشات العرض'),
  ('public-address-and-fire-alarm-system','Public Address & Fire Alarm','النداء وإنذار الحريق'),
  ('iptv-solutions','IPTV Solutions','حلول IPTV'),
  ('professional-services','Professional Services','الخدمات الاحترافية'),
]
PROJ_IMG = ['dc-proj-aou-council.jpg','dc-proj-psau.jpg','dc-proj-taqeem.jpg','dc-proj-auditorium.jpg']
# "From our sites" gallery — real installation/site photos, (file, en alt, ar alt)
GAL_IMG = [
  ('dc-proj-controlroom.jpg', 'A control room we integrated', 'غرفة تحكم من تنفيذنا'),
  ('dc-proj-videowall.jpg', 'A video wall we installed', 'شاشة عرض جدارية من تنفيذنا'),
  ('dc-proj-survey.jpg', 'An on-site survey', 'مسح ميداني في الموقع'),
  ('dc-proj-airport.jpg', 'Terminal fit-out on an airport project', 'تجهيزات في مشروع مطار'),
  ('dc-proj-firealarm.jpg', 'Installing and testing a fire-alarm detector on site', 'تركيب واختبار كاشف إنذار حريق في الموقع'),
  ('dc-proj-avmount.jpg', 'Mounting a video-wall array on site', 'تركيب حامل شاشة عرض جدارية في الموقع'),
]
POST_IMG = ['dc-blog-pa.jpg','dc-blog-5g.png','dc-blog-passive.png']
# Google Maps "search + embed" (no API key, loads only when the user clicks)
MAP_Q = ['Dabbab+Complex+Dabbab+Street+Riyadh+12626',
         'Um+Hurair+Second+Dubai+UAE',
         'Government+Cyberpark+Kozhikode+Kerala+673016']

# the mirror's about page is about-us.html (live filename), not about.html
PAGE_ALIAS = {'about': 'about-us'}
def loc(base, ar): return PAGE_ALIAS.get(base, base) + ('-ar' if ar else '') + '.html'

# Asset cache-busting version. Bump whenever dc-overlay.* / dc-pages.css /
# dc-products.js change, so browsers refetch instead of serving a stale copy.
# Keep in sync with the value stamped into the 6 live core pages.
VER = "18"

# ── SEO / GEO / AEO: canonical, hreflang, Open Graph, JSON-LD entity graph ──
SITE = "https://www.datacore.com.sa"   # canonical production domain (matches build_extra BASE)
OG_IMG = SITE + "/assets1/images/dc-og.jpg"

def _abs(base, ar):
    return SITE + "/" + loc(base, ar)

def seo_meta(ar, active, title, desc):
    """Per-page canonical + hreflang alternates + Open Graph + Twitter cards."""
    if active:
        en_url, ar_url = _abs(active, False), _abs(active, True)
        page_url = ar_url if ar else en_url
        alts = (f'<link rel="canonical" href="{page_url}">'
                f'<link rel="alternate" hreflang="en" href="{en_url}">'
                f'<link rel="alternate" hreflang="ar" href="{ar_url}">'
                f'<link rel="alternate" hreflang="x-default" href="{en_url}">')
    else:
        page_url, alts = SITE + "/", ''
    lc = 'ar_SA' if ar else 'en_US'
    return (alts +
        '<meta property="og:type" content="website">'
        '<meta property="og:site_name" content="Datacore Solutions">'
        f'<meta property="og:locale" content="{lc}">'
        f'<meta property="og:title" content="{esc(title)}">'
        f'<meta property="og:description" content="{esc(desc)}">'
        f'<meta property="og:url" content="{page_url}">'
        f'<meta property="og:image" content="{OG_IMG}">'
        '<meta name="twitter:card" content="summary_large_image">'
        f'<meta name="twitter:title" content="{esc(title)}">'
        f'<meta name="twitter:description" content="{esc(desc)}">'
        f'<meta name="twitter:image" content="{OG_IMG}">')

# Organization + three regional offices + WebSite — the entity graph that answer
# engines (Google, ChatGPT, Perplexity) read. Facts only; no invented data.
def site_jsonld(ar):
    g = {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": SITE + "/#org", "name": "Datacore Solutions",
         "alternateName": "Datacore Technology Integrators", "url": "https://www.datacore.com.sa/",
         "foundingDate": "2007", "logo": SITE + "/assets1/images/dc-logo-full.png", "image": OG_IMG,
         "email": "info@datacore.com.sa", "telephone": "+966115128888",
         "description": "Low-current (ELV) systems integrator delivering IT network infrastructure, "
                        "audio-visual, data centre, surveillance, IPTV, and public-address & fire-alarm "
                        "solutions across Saudi Arabia, the UAE and India since 2007.",
         "areaServed": [{"@type": "Country", "name": "Saudi Arabia"},
                        {"@type": "Country", "name": "United Arab Emirates"},
                        {"@type": "Country", "name": "India"}],
         "sameAs": ["https://www.linkedin.com/company/datacore-solutions",
                    "https://www.instagram.com/datacore_sa",
                    "https://www.facebook.com/www.datacore.com.sa"]},
        {"@type": "LocalBusiness", "@id": SITE + "/#riyadh", "name": "Datacore Solutions — Riyadh",
         "parentOrganization": {"@id": SITE + "/#org"}, "telephone": "+966115128888", "email": "sales@datacore.com.sa",
         "address": {"@type": "PostalAddress", "streetAddress": "Office 503, Dabbab Complex, Dabbab St.",
                     "addressLocality": "Riyadh", "postalCode": "12626", "addressCountry": "SA"},
         "geo": {"@type": "GeoCoordinates", "latitude": 24.6675676, "longitude": 46.7045394}},
        {"@type": "LocalBusiness", "@id": SITE + "/#dubai", "name": "Datacore Solutions — Dubai",
         "parentOrganization": {"@id": SITE + "/#org"}, "telephone": "+971527536070",
         "address": {"@type": "PostalAddress", "addressLocality": "Dubai", "addressCountry": "AE"}},
        {"@type": "LocalBusiness", "@id": SITE + "/#kozhikode", "name": "Datacore Solutions — Kozhikode",
         "parentOrganization": {"@id": SITE + "/#org"}, "telephone": "+914953501154",
         "address": {"@type": "PostalAddress", "streetAddress": "Government Cyberpark", "addressLocality": "Kozhikode",
                     "addressRegion": "Kerala", "postalCode": "673016", "addressCountry": "IN"}},
        {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "Datacore Solutions",
         "publisher": {"@id": SITE + "/#org"}, "inLanguage": ["en", "ar"]}
    ]}
    return '<script type="application/ld+json">' + json.dumps(g, ensure_ascii=False) + '</script>'

def breadcrumb_jsonld(ar, active, title):
    if not active or active == 'index':
        return ''
    home = STR['ar' if ar else 'en'].get('home', 'Home')
    g = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": home, "item": _abs('index', ar)},
        {"@type": "ListItem", "position": 2, "name": title, "item": _abs(active, ar)}]}
    return '<script type="application/ld+json">' + json.dumps(g, ensure_ascii=False) + '</script>'

# ── page shell ──────────────────────────────────────────────────────────
def shell(ar, active, title, desc, body, extra_head='', extra_js='', canon=None):
    lang = 'ar' if ar else 'en'
    dr = 'rtl' if ar else 'ltr'
    c = canon or active   # canonical/hreflang base; service pages override via canon
    return f"""<!DOCTYPE html>
<html lang="{lang}" dir="{dr}">
<head>
<script>try{{if(localStorage.getItem("dc-theme")==="dark")document.documentElement.classList.add("dc-dark");}}catch(e){{}}</script>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="apple-touch-icon" sizes="180x180" href="assets1/images/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="assets1/images/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="assets1/images/favicon-16x16.png">
<link rel="preload" as="font" type="font/ttf" href="fonts/TextaBold.ttf" crossorigin>
<link rel="stylesheet" href="dc-overlay.css?v={VER}">
<link rel="stylesheet" href="dc-pages.css?v={VER}">
{seo_meta(ar, c, title, desc)}
{site_jsonld(ar)}
{breadcrumb_jsonld(ar, c, title)}
{extra_head}</head>
<body class="dcp">
{body}
<script src="dc-overlay.js?v={VER}"></script>
{extra_js}<script src="dc-fx.js?v={VER}"></script>
</body>
</html>"""

def hero(ar, ghost, crumb_active, title, lede, btns=''):
    home = STR[('ar' if ar else 'en')]['home']
    crumb = (f'<div class="dcp-crumb"><a href="{loc("index",ar)}">{esc(home)}</a> '
             f'&rsaquo; {esc(crumb_active)}</div>')
    return (f'<section class="dcp-hero"><div class="dcp-ghost" aria-hidden="true">{esc(ghost)}</div>'
            f'<div class="dcp-wrap">{crumb}<h1>{esc(title)}</h1>'
            f'<p class="dcp-lede">{esc(lede)}</p>{btns}</div></section>')

def cta_band(ar):
    s = STR['ar' if ar else 'en']
    return (f'<section class="dcp-cta"><div class="dcp-wrap"><div><h2>{esc(s["cta_h"])}</h2>'
            f'<p>{esc(s["cta_p"])}</p></div><div class="btns">'
            f'<a class="dcp-btn" href="{loc("contact",ar)}">{esc(s["consult"])} {I_ARROW}</a>'
            f'<a class="dcp-btn-o" href="{loc("services",ar)}">{esc(s["f_all_disc"])}</a>'
            f'</div></div></section>')

def footer(ar):
    s = STR['ar' if ar else 'en']
    disc = ''.join(f'<li><a href="{loc("services",ar)}?id={d[0]}">{esc(d[1] if not ar else d[2])}</a></li>'
                   for d in DISCIPLINES[:6])
    comp = ''.join(f'<li><a href="{loc(k,ar)}">{esc(lab)}</a></li>' for k,lab in s['f_links'])
    o0 = s['offices'][0]
    touch = (f'<li><a href="{loc("contact",ar)}">{esc(o0[2])}, {esc(o0[3])}</a></li>'
             f'<li><a href="tel:{o0[5]}">{esc(o0[4])}</a></li>'
             f'<li><a href="{loc("careers",ar)}">{esc(s["f_careers"])}</a></li>')
    return f"""<footer class="dcp-foot"><div class="dcp-wrap">
<div class="dcp-foot-top">
  <div><a class="logo" href="{loc('index',ar)}"><img src="assets1/images/dc-logo.svg" alt="Datacore Solutions" style="height:40px"></a>
    <p class="dcp-foot-blurb">{esc(s['brand_line'])}</p></div>
  <div><h4>{esc(s['f_company'])}</h4><ul>{comp}<li><a href="{loc('products',ar)}">{esc(s['f_catalogue'])}</a></li></ul></div>
  <div><h4>{esc(s['f_services'])}</h4><ul>{disc}<li><a href="{loc('services',ar)}">{esc(s['f_all_disc'])}</a></li></ul></div>
  <div><h4>{esc(s['f_touch'])}</h4><ul>{touch}</ul></div>
</div>
<div class="dcp-foot-btm"><span class="legal">{esc(s['f_rights'])}</span>
  <span class="legal">{esc(s['f_legal'])}</span>
  <a href="{loc('terms',ar)}">{esc(s['f_terms'])}</a>
  <a href="{loc('privacy',ar)}">{esc(s['f_privacy'])}</a></div>
</div></footer>"""

# real manufacturer partners (from the product catalogue) — text marquee
BRANDS = ['Cisco', 'Aruba', 'Axis', 'Bosch', 'Crestron', 'Extron', 'Biamp', 'Q-SYS',
          'Shure', 'Honeywell', 'Hikvision', 'Samsung', 'LG', 'CommScope', 'Suprema', 'APC']

def stats_marquee(ar):
    # only facts already stated on the site (2026 − 2007 = 19 years)
    stats = ([(19, 'سنة من التكامل'), (3, 'دول'), (9, 'تخصصات'), (38, 'خدمة')] if ar else
             [(19, 'Years integrating'), (3, 'Countries'), (9, 'Disciplines'), (38, 'Services')])
    cells = ''.join(
        f'<div class="dcp-stat"><div class="num" data-count="{n}">{n}</div>'
        f'<div class="lab">{esc(lab)}</div></div>' for n, lab in stats)
    h = 'شركاء موثوقون' if ar else 'Trusted alliances'
    # doubled list so the -50% keyframe loops seamlessly
    row = ''.join(f'<span dir="ltr">{esc(b)}</span>' for b in BRANDS * 2)
    return (f'<section class="dcp-sec alt"><div class="dcp-wrap"><div class="dcp-stats">{cells}</div></div></section>'
            f'<section class="dcp-sec" style="padding-block:44px"><div class="dcp-wrap dcp-center">'
            f'<div class="dcp-head" style="margin-bottom:22px"><h2 style="font-size:1.15rem;'
            f'letter-spacing:.08em;color:var(--dcp-ink3);text-transform:uppercase">{esc(h)}</h2></div></div>'
            f'<div class="dcp-marquee"><div class="track">{row}</div></div></section>')

# ── PROJECTS ────────────────────────────────────────────────────────────
def build_projects(ar):
    s = STR['ar' if ar else 'en']
    cards = ''
    for i, p in enumerate(s['proj']):
        sector, city, name, body, kit, client, scope = p
        kits = ''.join(f'<span>{esc(k)}</span>' for k in kit)
        cards += f"""<article class="dcp-proj">
  <div class="ph"><img src="assets1/images/{PROJ_IMG[i]}" alt="{esc(name)}" loading="lazy" width="1200" height="750"></div>
  <div class="band"><span class="c">{esc(sector)}</span><span>{esc(city)}</span></div>
  <div class="in"><h3>{esc(name)}</h3><p class="body">{esc(body)}</p>
    <div class="dcp-kit">{kits}</div>
    <dl><dt>{esc(s['p_client'])}</dt><dd>{esc(client)}</dd>
        <dt>{esc(s['p_scope'])}</dt><dd>{esc(scope)}</dd></dl>
  </div></article>"""
    feat = ''.join(f'<div class="dcp-featcell"><span class="dcp-featic">{FEAT_ICONS[i]}</span>'
                   f'<h3>{esc(t)}</h3><p>{esc(d)}</p></div>'
                   for i,(t,d) in enumerate(s['pj_feat']))
    gal = ''.join(f'<figure><img src="assets1/images/{g[0]}" alt="{esc(g[2] if ar else g[1])}" '
                  f'loading="lazy" width="900" height="600">'
                  f'<figcaption>{esc(g[2] if ar else g[1])}</figcaption></figure>' for g in GAL_IMG)
    body = (
      hero(ar, 'WORK' if not ar else 'مشاريع', s['pj_title'], s['pj_title'], s['pj_lede'],
           f'<div style="margin-top:26px;display:flex;gap:12px;flex-wrap:wrap">'
           f'<a class="dcp-btn" href="{loc("contact",ar)}">{esc(s["consult"])} {I_ARROW}</a></div>')
      + stats_marquee(ar)
      + f'<section class="dcp-sec"><div class="dcp-wrap"><div class="dcp-projs">{cards}</div></div></section>'
      + f'<section class="dcp-sec alt"><div class="dcp-wrap"><div class="dcp-head dcp-center">'
        f'<h2>{esc(s["pj_feat_h"])}</h2></div><div class="dcp-featgrid">{feat}</div></div></section>'
      + f'<section class="dcp-sec"><div class="dcp-wrap"><div class="dcp-head dcp-center">'
        f'<h2>{esc(s["pj_gal_h"])}</h2><p>{esc(s["pj_gal_p"])}</p></div>'
        f'<div class="dcp-gal">{gal}</div></div></section>'
      + cta_band(ar) + footer(ar))
    title = ('مشاريعنا | داتاكور للحلول' if ar else 'Projects | Datacore Solutions')
    return shell(ar, 'projects', title, s['pj_lede'], body)

# ── INSIGHTS ────────────────────────────────────────────────────────────
def build_insights(ar):
    s = STR['ar' if ar else 'en']
    cards = ''
    for i, p in enumerate(s['posts']):
        date, team, ttl, body = p
        cards += f"""<article class="dcp-post">
  <div class="ph"><img src="assets1/images/{POST_IMG[i]}" alt="{esc(ttl)}" loading="lazy" width="561" height="306"></div>
  <div class="in"><span class="by">{esc(date)} &middot; {esc(team)}</span>
    <h3>{esc(ttl)}</h3><p>{esc(body)}</p>
    <a class="dcp-dir" href="{loc('contact',ar)}">{esc(s['svc_ask'])} {I_ARROW}</a></div></article>"""
    body = (hero(ar, 'NOTES' if not ar else 'ملاحظات', s['i_title'], s['i_title'], s['i_lede'])
      + f'<section class="dcp-sec"><div class="dcp-wrap"><div class="dcp-posts">{cards}</div></div></section>'
      + cta_band(ar) + footer(ar))
    title = ('ملاحظات تقنية | داتاكور للحلول' if ar else 'Technical notes | Datacore Solutions')
    return shell(ar, 'insights', title, s['i_lede'], body)

# ── CONTACT ─────────────────────────────────────────────────────────────
def build_contact(ar):
    s = STR['ar' if ar else 'en']; f = s['c_f']
    offices = ''
    for i, o in enumerate(s['offices']):
        head, org, addr1, addr2, phone, phone_raw = o
        on = ' on' if i == 0 else ''
        offices += f"""<div class="dcp-office{on}" data-i="{i}" role="button" tabindex="0" aria-pressed="{'true' if i==0 else 'false'}">
  <h3>{esc(head)}</h3>
  <p>{esc(org)}<br>{esc(addr1)}<br>{esc(addr2)}</p>
  <div class="rows"><span>{I_PHONE} <a href="tel:{esc(phone_raw)}" dir="ltr">{esc(phone)}</a></span></div>
  <a class="dcp-dir" href="https://www.google.com/maps/search/?api=1&amp;query={MAP_Q[i]}" target="_blank" rel="noopener">{I_DIR} {esc(s['directions'])}</a>
</div>"""
    tabs = ''.join(f'<button type="button" class="{"on" if i==0 else ""}" data-i="{i}" '
                   f'aria-pressed="{"true" if i==0 else "false"}">{esc(t)}</button>'
                   for i,t in enumerate(s['map_tabs']))
    types = ''.join(f'<option>{esc(t)}</option>' for t in s['c_types'])
    # Riyadh gets verified coordinates for a precise pin; the others use an
    # address query. Map auto-loads to office 0 and switches on tab/card click.
    map_val = ['24.6675676,46.7045394', MAP_Q[1], MAP_Q[2]]
    map_src = ['https://www.google.com/maps?q=' + v + '&output=embed' for v in map_val]
    map_dir = ['https://www.google.com/maps/search/?api=1&query=' + q for q in MAP_Q]
    map_cap = [f'{o[2]}, {o[3]}' for o in s['offices']]
    geo = (f'<section class="dcp-sec"><div class="dcp-wrap">'
           f'<div class="dcp-head"><h2>{esc(s["c_offices_h"])}</h2></div>'
           f'<div class="dcp-geo"><div class="dcp-offices-list" id="dcp-offices">{offices}</div>'
           f'<div class="dcp-map-col"><div class="dcp-tabs" id="dcp-mtabs">{tabs}</div>'
           f'<div class="dcp-map" id="dcp-map"><iframe title="{esc(s["map_h"])}" loading="lazy" '
           f'src="{map_src[0]}" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>'
           f'<p class="dcp-mapcap"><span id="dcp-mapcap">{esc(map_cap[0])}</span> &middot; '
           f'<a id="dcp-mapdir" href="{map_dir[0]}" target="_blank" rel="noopener">{esc(s["directions"])}</a></p>'
           f'</div></div></div></section>')
    form = f"""<form class="dcp-form" id="dcp-enq" novalidate>
  <div class="dcp-head"><h2>{esc(s['c_form_h'])}</h2></div>
  <div class="dcp-two">
    <div class="dcp-field"><label for="q-name">{esc(f['name'])}</label><input id="q-name" name="name" required></div>
    <div class="dcp-field"><label for="q-co">{esc(f['company'])}</label><input id="q-co" name="company"></div>
  </div>
  <div class="dcp-two">
    <div class="dcp-field"><label for="q-mail">{esc(f['email'])}</label><input id="q-mail" name="email" type="email" dir="ltr" required></div>
    <div class="dcp-field"><label for="q-tel">{esc(f['phone'])}</label><input id="q-tel" name="phone" type="tel" dir="ltr"></div>
  </div>
  <div class="dcp-field"><label for="q-type">{esc(f['type'])}</label><select id="q-type" name="type">{types}</select></div>
  <div class="dcp-field"><label for="q-proj">{esc(f['project'])}</label><input id="q-proj" name="project" placeholder="{esc(f['project_hint'])}"></div>
  <div class="dcp-field"><label for="q-msg">{esc(f['msg'])}</label><textarea id="q-msg" name="message" rows="5" required></textarea></div>
  <button class="dcp-btn" type="submit">{esc(f['send'])} {I_ARROW}</button>
  <p class="dcp-note">{esc(f['note'])}</p>
</form>"""
    other = (f'<div><div class="dcp-head"><h2>{esc(s["c_other_h"])}</h2></div>'
             f'<div class="dcp-office"><div class="rows">'
             f'<a href="mailto:sales@datacore.com.sa" dir="ltr">sales@datacore.com.sa</a>'
             f'<a href="mailto:info@datacore.com.sa" dir="ltr">info@datacore.com.sa</a>'
             f'<a href="mailto:careers@datacore.com.sa" dir="ltr">careers@datacore.com.sa</a>'
             f'<a href="https://wa.me/966115128888" target="_blank" rel="noopener">{esc(s["f_whatsapp"])}</a>'
             f'</div></div>'
             f'<div class="dcp-head" style="margin-top:32px"><h2>{esc(s["follow_h"])}</h2></div>'
             f'<p style="color:var(--dcp-ink2);margin-bottom:14px">{esc(s["follow_p"])}</p>'
             f'<div class="dcp-socials">'
             f'<a href="https://www.linkedin.com/company/datacore-solutions" target="_blank" rel="noopener">LinkedIn</a>'
             f'<a href="https://www.instagram.com/datacore_sa" target="_blank" rel="noopener">Instagram</a>'
             f'</div></div>')
    formsec = (f'<section class="dcp-sec alt"><div class="dcp-wrap"><div class="dcp-cgrid">'
               f'<div>{form}</div>{other}</div></div></section>')
    body = (hero(ar, 'TALK' if not ar else 'تواصل', s['c_title'], s['c_title'], s['c_lede'])
            + geo + formsec + footer(ar))
    js = f"""<script>
(function(){{
  var SRC={json.dumps(map_src)}, CAP={json.dumps(map_cap, ensure_ascii=False)}, DIR={json.dumps(map_dir)};
  var offs=document.querySelectorAll('#dcp-offices .dcp-office');
  var tabs=document.querySelectorAll('#dcp-mtabs button');
  var map=document.getElementById('dcp-map');
  function pick(i){{
    offs.forEach(function(o,j){{var on=j===i;o.classList.toggle('on',on);o.setAttribute('aria-pressed',String(on));}});
    tabs.forEach(function(t,j){{var on=j===i;t.classList.toggle('on',on);t.setAttribute('aria-pressed',String(on));}});
    document.getElementById('dcp-mapcap').textContent=CAP[i];
    document.getElementById('dcp-mapdir').href=DIR[i];
    var fr=map.querySelector('iframe');
    if(fr&&fr.src!==SRC[i])fr.src=SRC[i];
  }}
  tabs.forEach(function(t){{t.addEventListener('click',function(){{pick(+t.dataset.i);}});}});
  offs.forEach(function(o){{
    o.addEventListener('click',function(ev){{if(ev.target.closest('a'))return;pick(+o.dataset.i);}});
    o.addEventListener('keydown',function(ev){{if(ev.key==='Enter'||ev.key===' '){{ev.preventDefault();pick(+o.dataset.i);}}}});
  }});
  var form=document.getElementById('dcp-enq');
  form.addEventListener('submit',function(e){{
    e.preventDefault();
    if(!form.checkValidity()){{form.reportValidity();return;}}
    var ref='DC-'+Date.now().toString(36).toUpperCase().slice(-6);
    var ok=document.createElement('div');
    ok.className='dcp-form';ok.setAttribute('role','status');
    ok.innerHTML='<h2>{("تم استلام استفسارك" if ar else "Enquiry received")}</h2>'
      +'<p style="color:var(--dcp-ink2)">{("رقمك المرجعي" if ar else "Your reference number is")} '
      +'<strong>'+ref+'</strong>. {("سنرد خلال يوم عمل واحد." if ar else "We will reply within one working day.")}</p>';
    form.replaceWith(ok);
  }});
}})();
</script>"""
    schema = ('<script type="application/ld+json">' + json.dumps({
        "@context":"https://schema.org","@type":"LocalBusiness",
        "name":"Datacore Solutions",
        "description":s['brand_line'],
        "url":"https://www.datacore.com.sa/",
        "telephone":s['offices'][0][5],
        "address":{"@type":"PostalAddress","streetAddress":s['offices'][0][2],
                   "addressLocality":"Riyadh","postalCode":"12626","addressCountry":"SA"},
        "areaServed":["SA","AE","IN"]
      }, ensure_ascii=False) + '</script>')
    title = ('تواصل معنا | داتاكور للحلول' if ar else 'Contact | Datacore Solutions')
    return shell(ar, 'contact', title, s['c_lede'], body, extra_head=schema, extra_js=js)

# ── write all ───────────────────────────────────────────────────────────
def w(name, s):
    open(os.path.join(ROOT, name), "w", encoding="utf-8").write(s)
    print("wrote", name, len(s), "chars")

if __name__ == "__main__":
    for ar in (False, True):
        w(loc('projects', ar), build_projects(ar))
        w(loc('insights', ar), build_insights(ar))
        w(loc('contact', ar), build_contact(ar))
    print("done")
