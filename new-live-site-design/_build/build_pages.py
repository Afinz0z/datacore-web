# -*- coding: utf-8 -*-
"""Generate the mirror's functional pages (contact / projects / insights, EN+AR)
in the live Texta look. Each page loads the developed-site header + dark mode via
dc-overlay.css/js and the live-look content styles via dc-pages.css. Live body
HTML is not touched — these are brand-new pages the header's nav links point to."""
import os, json, html, sys, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = r"C:\Users\afnan\Documents\Datacore\Datacore Website\datacore-enhanced"
STR = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mirror_strings.json"), encoding="utf-8"))

def esc(s): return html.escape(str(s), quote=True)

# wrap Latin/acronym runs in dir="ltr" for correct rendering inside RTL Arabic.
# run on ALREADY-escaped text; only wraps runs that contain a letter.
def wrap_ltr(t):
    def r(m):
        s = m.group(0)
        return '<span dir="ltr">' + s + '</span>' if re.search(r'[A-Za-z]', s) else s
    return re.sub(r'[A-Za-z0-9][A-Za-z0-9/.+\-]*(?:\s[A-Za-z0-9/.+\-]+)*', r, t)

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
PROJ_IMG = ['dc-proj-owis.jpg','dc-proj-aou-council.jpg','dc-proj-psau.jpg','dc-proj-taqeem.jpg','dc-proj-auditorium.jpg',
            'dc-proj-stc.jpg','dc-proj-kafd.jpg','dc-proj-neom.jpg','dc-proj-mawhiba.jpg',
            'dc-proj-sama.jpg','dc-proj-altayyar.jpg','dc-proj-mansard.jpg']
# disciplines each project actually touches (read off its real kit/scope) — powers the
# projects filter; slugs match DISCIPLINES / the services-nav dropdown so the two never drift.
PROJ_DISC = [
  ['network-infrastructure-services','surveillance-and-security-solutions','audio-visual-solutions','digital-signage-amp-video-walls'],  # OWIS
  ['audio-visual-solutions','meeting-room-solutions'],                                                                                   # AOU council
  ['audio-visual-solutions','digital-signage-amp-video-walls','meeting-room-solutions'],                                                 # PSAU
  ['audio-visual-solutions','meeting-room-solutions'],                                                                                   # TAQEEM
  ['audio-visual-solutions','digital-signage-amp-video-walls'],                                                                          # auditorium
  ['audio-visual-solutions','meeting-room-solutions'],                          # STC command centres
  ['audio-visual-solutions','meeting-room-solutions'],                          # KAFD
  ['audio-visual-solutions','meeting-room-solutions'],                          # NEOM exec room
  ['audio-visual-solutions','meeting-room-solutions'],                          # Mawhiba auditorium + boardrooms
  ['datacenter-solutions','network-infrastructure-services'],                   # SAMA data centre
  ['datacenter-solutions'],                                                     # Al Tayyar Tier III
  ['datacenter-solutions'],                                                     # Mansard Tier III
]
# "From our sites" gallery — real installation/site photos, (file, en alt, ar alt)
GAL_IMG = [
  ('dc-proj-controlroom.jpg', 'A control room we integrated', 'غرفة تحكم من تنفيذنا'),
  ('dc-proj-videowall.jpg', 'A video wall we installed', 'شاشة عرض جدارية من تنفيذنا'),
  ('dc-proj-survey.jpg', 'An on-site survey', 'مسح ميداني في الموقع'),
  ('dc-proj-airport.jpg', 'Terminal fit-out on an airport project', 'تجهيزات في مشروع مطار'),
  ('dc-proj-firealarm.jpg', 'Installing and testing a fire-alarm detector on site', 'تركيب واختبار كاشف إنذار حريق في الموقع'),
  ('dc-proj-avmount.jpg', 'Mounting a video-wall array on site', 'تركيب حامل شاشة عرض جدارية في الموقع'),
  ('dc-proj-owis-auditorium.jpg', 'OWIS Riyadh auditorium — 2.5 mm LED video wall', 'مسرح مدرسة ون وورلد الرياض — جدار فيديو LED بمقاس 2.5 مم'),
  ('dc-proj-owis-rack.jpg', 'The communications rack at OWIS Riyadh', 'خزانة الاتصالات في مدرسة ون وورلد الرياض'),
  ('dc-proj-owis-building.jpg', 'OWIS Riyadh campus building', 'مبنى حرم مدرسة ون وورلد الرياض'),
]
# case-study detail pages — slugs index-aligned with proj[] / PROJ_IMG
CASE_SLUG = ['owis', 'aou-council', 'psau', 'taqeem', 'auditorium',
             '', '', '', '', '', '', '']   # 7 showcase cards from the portfolio decks: image+detail, no dedicated case page
CASES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cases.json"), encoding="utf-8"))
FAQ = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "faq.json"), encoding="utf-8"))
GLOSSARY = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "glossary.json"), encoding="utf-8"))
INSIGHTS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "insights.json"), encoding="utf-8"))
LANDING = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "landing.json"), encoding="utf-8"))
CASE_UI = {
 'en': {'read': 'Read the case study', 'projects': 'Projects', 'at_glance': 'At a glance',
        'client': 'Client', 'sector': 'Sector', 'location': 'Location', 'completed': 'Completed',
        'scope': 'Scope', 'kit': 'Systems delivered', 'gallery': 'On site',
        'get': 'Start a project', 'get_p': 'Tell us the building and the stage you are at.'},
 'ar': {'read': 'اقرأ دراسة الحالة', 'projects': 'مشاريعنا', 'at_glance': 'لمحة سريعة',
        'client': 'العميل', 'sector': 'القطاع', 'location': 'الموقع', 'completed': 'اكتمل',
        'scope': 'النطاق', 'kit': 'الأنظمة المُنفّذة', 'gallery': 'من الموقع',
        'get': 'ابدأ مشروعًا', 'get_p': 'أخبرنا بالمبنى والمرحلة التي أنت فيها.'},
}
POST_SLUG = [p['slug'] for p in INSIGHTS['en']['posts']]   # insights.json is the single source of truth
POST_IMG  = [p['img']  for p in INSIGHTS['en']['posts']]   # card / hero image per post
POST_ISO  = [p['iso']  for p in INSIGHTS['en']['posts']]   # datePublished for BlogPosting schema
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
VER = "43"

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
         "foundingDate": "2007", "taxID": "7002812043", "vatID": "311206394100003",
         "logo": SITE + "/assets1/images/dc-logo-full.png", "image": OG_IMG,
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
<link rel="preload" as="font" type="font/woff2" href="fonts/TextaBold.woff2" crossorigin>
<link rel="stylesheet" href="dc-overlay.css?v={VER}">
<link rel="stylesheet" href="dc-pages.css?v={VER}">
{seo_meta(ar, c, title, desc)}
{site_jsonld(ar)}
{breadcrumb_jsonld(ar, c, title)}
{extra_head}</head>
<body class="dcp">
{body}
<script src="dc-overlay.js?v={VER}"></script>
<script src="dc-forms.js?v={VER}"></script>
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
                   for d in DISCIPLINES[:4])
    land = ''.join(f'<li><a href="{loc(p["slug"],ar)}">{esc(p["nav"])}</a></li>'
                   for p in LANDING['ar' if ar else 'en']['pages'])
    comp = ''.join(f'<li><a href="{loc(k,ar)}">{esc(lab)}</a></li>' for k,lab in s['f_links'])
    o0 = s['offices'][0]
    touch = (f'<li><a href="{loc("contact",ar)}">{esc(o0[2])}, {esc(o0[3])}</a></li>'
             f'<li><a href="tel:{o0[5]}">{esc(o0[4])}</a></li>'
             f'<li><a href="{loc("careers",ar)}">{esc(s["f_careers"])}</a></li>')
    return f"""<footer class="dcp-foot"><div class="dcp-wrap">
<div class="dcp-foot-top">
  <div><a class="logo" href="{loc('index',ar)}"><img src="assets1/images/dc-logo.svg" alt="Datacore Solutions" style="height:40px"></a>
    <p class="dcp-foot-blurb">{esc(s['brand_line'])}</p>
    <div class="dcp-foot-social">
      <a href="https://www.linkedin.com/company/datacore-solutions" target="_blank" rel="noopener" aria-label="LinkedIn"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M4.98 3.5a2.5 2.5 0 11-.02 5 2.5 2.5 0 01.02-5zM3 9h4v12H3zM10 9h3.84v1.64h.05c.53-.95 1.84-1.95 3.79-1.95 4.05 0 4.8 2.4 4.8 5.52V21h-4v-4.9c0-1.17-.02-2.68-1.63-2.68-1.64 0-1.89 1.28-1.89 2.6V21h-4z"/></svg></a>
      <a href="https://www.instagram.com/datacore_sa" target="_blank" rel="noopener" aria-label="Instagram"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1.2" fill="currentColor" stroke="none"/></svg></a>
      <a href="https://www.facebook.com/www.datacore.com.sa" target="_blank" rel="noopener" aria-label="Facebook"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M22 12a10 10 0 10-11.56 9.88v-6.99H7.9V12h2.54V9.8c0-2.5 1.49-3.89 3.77-3.89 1.09 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56V12h2.78l-.44 2.89h-2.34v6.99A10 10 0 0022 12z"/></svg></a>
    </div></div>
  <div><h4>{esc(s['f_company'])}</h4><ul>{comp}<li><a href="{loc('products',ar)}">{esc(s['f_catalogue'])}</a></li></ul></div>
  <div><h4>{esc(s['f_services'])}</h4><ul>{land}{disc}<li><a href="{loc('services',ar)}">{esc(s['f_all_disc'])}</a></li></ul></div>
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
    stats = ([(16, 'سنة من التكامل'), (3, 'دول'), (9, 'تخصصات'), (38, 'خدمة')] if ar else
             [(16, 'Years integrating'), (3, 'Countries'), (9, 'Disciplines'), (38, 'Services')])
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
# page-scoped so no shared-asset VER bump is needed; adapts to dark mode via the dcp tokens.
PROJ_FILTER_CSS = """<style>
.dcp-phero{border-bottom:0}
.dcp-phero .dcp-phero-grid{display:grid;grid-template-columns:1.15fr .85fr;gap:40px;align-items:end}
.dcp-pfilter-sec{position:relative;z-index:20;padding-block:0 40px}
.dcp-phero-l h1{margin:.28em 0 0}
.dcp-phero-r p{margin:0;color:var(--dcp-ink2);font-size:1.03rem;line-height:1.75;max-width:52ch}
.dcp-pfilter{display:flex;gap:14px;flex-wrap:wrap;margin-top:-30px;padding:14px;background:var(--dcp-soft);border:1px solid var(--dcp-line);border-radius:16px}
.dcp-pf-search{flex:1 1 300px;display:flex;align-items:center;gap:10px;padding:12px 18px;background:var(--dcp-bg);border:1px solid var(--dcp-line);border-radius:11px;transition:border-color .15s}
.dcp-pf-search svg{flex:0 0 auto;color:var(--dcp-ink3)}
.dcp-pf-search input{flex:1;min-width:0;border:0;outline:0;background:transparent;color:var(--dcp-ink);font:inherit;font-size:1rem}
.dcp-pf-search input::placeholder{color:var(--dcp-ink3)}
.dcp-pf-search:focus-within{border-color:var(--dcp-teal-d)}
.dcp-pf-drop{position:relative;flex:0 0 auto;min-width:236px}
.dcp-pf-btn{width:100%;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 16px;background:var(--dcp-bg);border:1px solid var(--dcp-line);border-radius:11px;color:var(--dcp-ink);font:inherit;font-size:1rem;cursor:pointer;text-align:start;transition:border-color .15s,box-shadow .15s}
.dcp-pf-btn:hover{border-color:var(--dcp-ink3)}
.dcp-pf-drop[data-open] .dcp-pf-btn,.dcp-pf-btn:focus-visible{border-color:var(--dcp-teal-d);outline:none;box-shadow:0 0 0 3px rgba(0,119,111,.13)}
.dcp-pf-caret{flex:0 0 auto;color:var(--dcp-ink3);transition:transform .2s}
.dcp-pf-drop[data-open] .dcp-pf-caret{transform:rotate(180deg)}
.dcp-pf-menu{position:absolute;z-index:40;top:calc(100% + 8px);inset-inline-start:0;min-width:100%;margin:0;padding:6px;list-style:none;background:var(--dcp-bg);border:1px solid var(--dcp-line);border-radius:13px;box-shadow:0 20px 46px -20px rgba(0,0,0,.4);max-height:340px;overflow:auto}
.dcp-pf-menu li{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:11px 14px;border-radius:8px;color:var(--dcp-ink2);font-size:.97rem;cursor:pointer;white-space:nowrap;outline:none}
.dcp-pf-menu li:hover,.dcp-pf-menu li:focus-visible{background:var(--dcp-soft);color:var(--dcp-ink)}
.dcp-pf-menu li.is-sel{color:var(--dcp-teal-d);font-weight:600;background:var(--dcp-soft)}
.dcp-pf-menu li .tick{opacity:0;color:var(--dcp-teal-d);font-weight:700}
.dcp-pf-menu li.is-sel .tick{opacity:1}
.dcp-proj.is-hidden{display:none}
.dcp-noresult{grid-column:1/-1;width:100%;text-align:center;color:var(--dcp-ink3);padding:44px 0;font-size:1.05rem}
@media(max-width:820px){.dcp-phero .dcp-phero-grid{grid-template-columns:1fr;gap:20px;align-items:start}.dcp-phero-r p{max-width:none}.dcp-pf-search{flex-basis:100%}.dcp-pf-drop{flex:1 1 100%}}
</style>"""
PROJ_FILTER_JS = """<script>
(function(){
  var q=document.getElementById('dcp-psearch'),drop=document.getElementById('dcp-pservice'),
      grid=document.getElementById('dcp-projgrid'),none=document.getElementById('dcp-noresult');
  if(!grid)return;
  var cards=[].slice.call(grid.querySelectorAll('.dcp-proj'));
  var btn=drop&&drop.querySelector('.dcp-pf-btn'),menu=drop&&drop.querySelector('.dcp-pf-menu'),
      cur=drop&&drop.querySelector('.dcp-pf-cur'),opts=menu?[].slice.call(menu.children):[];
  function apply(){
    var term=((q&&q.value)||'').trim().toLowerCase(),svc=(drop&&drop.getAttribute('data-value'))||'',shown=0;
    cards.forEach(function(c){
      var disc=(c.getAttribute('data-disc')||'').split(' ');
      var show=(!svc||disc.indexOf(svc)>-1)&&(!term||(c.textContent||'').toLowerCase().indexOf(term)>-1);
      c.classList.toggle('is-hidden',!show);if(show)shown++;
    });
    if(none)none.hidden=shown!==0;
  }
  function setOpen(o){ if(!menu)return; menu.hidden=!o; o?drop.setAttribute('data-open',''):drop.removeAttribute('data-open'); btn.setAttribute('aria-expanded',o?'true':'false'); }
  function choose(li){
    drop.setAttribute('data-value',li.getAttribute('data-value'));
    cur.textContent=li.getAttribute('data-label')||li.textContent.trim();
    opts.forEach(function(x){var s=x===li;x.classList.toggle('is-sel',s);x.setAttribute('aria-selected',s?'true':'false');});
    setOpen(false); btn.focus(); apply();
  }
  if(btn&&menu){
    opts.forEach(function(x){x.tabIndex=-1;});
    btn.addEventListener('click',function(e){e.stopPropagation();var willOpen=menu.hidden;setOpen(willOpen);if(willOpen)(menu.querySelector('.is-sel')||opts[0]||btn).focus();});
    menu.addEventListener('click',function(e){var li=e.target.closest('[role=option]');if(li)choose(li);});
    document.addEventListener('click',function(e){if(!drop.contains(e.target))setOpen(false);});
    drop.addEventListener('keydown',function(e){
      var i=opts.indexOf(document.activeElement);
      if(e.key==='Escape'){setOpen(false);btn.focus();}
      else if(e.key==='ArrowDown'){e.preventDefault();if(menu.hidden){setOpen(true);(menu.querySelector('.is-sel')||opts[0]).focus();}else if(i<opts.length-1)opts[i+1].focus();}
      else if(e.key==='ArrowUp'){e.preventDefault();if(!menu.hidden&&i>0)opts[i-1].focus();}
      else if((e.key==='Enter'||e.key===' ')&&i>-1){e.preventDefault();choose(opts[i]);}
    });
  }
  if(q)q.addEventListener('input',apply);
})();
</script>"""

# Real, named delivered work from the company presentation + AV/network reference decks.
# (client, sector_en, sector_ar, scope_en, scope_ar)
SELECTED = [
 ("Qiddiya Entertainment City","Giga-project","مشروع عملاق",
  "ICT, structured cabling, access control, CCTV, video walls and AV for the Speed Park Formula 1 circuit, and a park-wide public-address and fire-alarm system for Six Flags.",
  "أنظمة تقنية المعلومات والتمديدات الهيكلية والتحكم في الدخول وكاميرات المراقبة وشاشات الفيديو الجدارية والصوتيات لحلبة الفورمولا 1 في سبيد بارك، ونظام نداء عام وإنذار حريق على مستوى المدينة الترفيهية لـ Six Flags."),
 ("NEOM","Giga-project","مشروع عملاق",
  "CEO meeting room with Cisco Telepresence; passive systems and video walls at NEOM Bay Airport; camp offices (NC1/NC2); complete passive scope at NEOM Hospital; CCTV and access control at NEOM International Airport.",
  "قاعة اجتماعات الرئيس التنفيذي بنظام Cisco Telepresence؛ أنظمة سلبية وشاشات فيديو جدارية في مطار نيوم باي؛ مكاتب المخيمات (NC1/NC2)؛ الحلول السلبية الكاملة لمستشفى نيوم؛ كاميرات المراقبة والتحكم في الدخول في مطار نيوم الدولي."),
 ("KAFD HQ","Corporate","مقر مؤسسي",
  "IT infrastructure and audio-visual for the King Abdullah Financial District HQ — meeting rooms, board rooms and a command centre.",
  "البنية التحتية لتقنية المعلومات والحلول السمعية والبصرية لمقر مركز الملك عبدالله المالي — قاعات اجتماعات ومجالس إدارة وغرفة عمليات."),
 ("SAMA — KAFD","Data centre","مركز بيانات",
  "Complete data-centre passive scope: 118 Panduit network cabinets, six containment systems, and SYSTIMAX imVision intelligent patch panels.",
  "النطاق السلبي الكامل لمركز البيانات: 118 خزانة شبكات Panduit، وستة أنظمة احتواء، ولوحات توصيل ذكية SYSTIMAX imVision."),
 ("Bank Al Bilad","Data centre","مركز بيانات",
  "Complete active and passive ELV systems for the bank's data centre, plus public address and CCTV.",
  "أنظمة التيار الخفيف الفعّالة والسلبية الكاملة لمركز بيانات البنك، بالإضافة إلى النداء العام وكاميرات المراقبة."),
 ("SABB","Data centre","مركز بيانات",
  "SYSTIMAX imVision intelligent patch-panel installation and configuration for the HQ data centre.",
  "تركيب وتهيئة لوحات التوصيل الذكية SYSTIMAX imVision لمركز بيانات المقر الرئيسي."),
 ("Prince Sattam bin Abdulaziz University","University","جامعة",
  "Campus-wide audio-visual — smart classrooms, board rooms and auditoriums — at Al-Kharj.",
  "حلول سمعية وبصرية على مستوى الحرم الجامعي — فصول ذكية وقاعات مجالس إدارة ومسارح — في الخرج."),
 ("Arab Open University","University","جامعة",
  "Audio-visual for classrooms, board rooms, the council room and auditorium at the Riyadh campus.",
  "حلول سمعية وبصرية للفصول وقاعات مجالس الإدارة وقاعة المجلس والمسرح في حرم الرياض."),
 ("TAQEEM HQ","Government","جهة حكومية",
  "IT infrastructure and audio-visual for the Riyadh HQ — multipurpose room, board rooms and training rooms.",
  "البنية التحتية لتقنية المعلومات والحلول السمعية والبصرية للمقر في الرياض — قاعة متعددة الأغراض وقاعات مجالس إدارة وقاعات تدريب."),
 ("King Abdulaziz International Airport","Airport","مطار",
  "Fire-alarm and public-address systems for the new south terminal, Jeddah.",
  "أنظمة إنذار الحريق والنداء العام للصالة الجنوبية الجديدة، جدة."),
 ("Maaden PCS Testing Center","Command centre","غرفة عمليات",
  "A large-format video wall for real-time process visualisation, integrated control and monitoring, and ergonomic 24/7 operator consoles — installed, tested and commissioned end-to-end.",
  "شاشة فيديو جدارية كبيرة لعرض العمليات في الوقت الفعلي، وأنظمة تحكم ومراقبة متكاملة، ووحدات تشغيل مريحة على مدار الساعة — بالتركيب والاختبار والتشغيل الكامل."),
 ("S15 MOI Border Guards Housing","Residential","إسكان",
  "Complete ICT solutions for 300 villas, 1,000 apartments and a data centre, Jazan.",
  "حلول تقنية معلومات كاملة لـ 300 فيلا و1000 شقة ومركز بيانات، جازان."),
]
CLIENT_ROSTER = ["NEOM","Qiddiya","KAFD","SAMA","SABB","Bank Al Bilad","Riyad Bank","STC","Mobily",
  "Zain","Prince Sattam University","Arab Open University","MCIT","Mawhiba","Ma'aden","Marafiq",
  "National Housing Company","Dimension Data","Deloitte","Almarai","Landmark"]
SELECTED_CSS = """<style>
.dcp-spgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px;margin-top:30px}
.dcp-sp{border:1px solid var(--dcp-line);border-radius:14px;padding:22px 22px 24px;background:var(--dcp-bg);transition:border-color .2s,transform .2s}
.dcp-sp:hover{border-color:var(--dcp-teal-d);transform:translateY(-3px)}
.dcp-sp-sec{display:inline-block;font-size:.7rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--dcp-teal-d);background:var(--dcp-soft);padding:5px 11px;border-radius:999px}
.dcp-sp h3{margin:14px 0 8px;font-size:1.07rem;line-height:1.25}
.dcp-sp p{margin:0;color:var(--dcp-ink2);font-size:.91rem;line-height:1.6}
.dcp-roster{margin-top:44px;text-align:center}
.dcp-roster h3{font-size:.78rem;letter-spacing:.1em;text-transform:uppercase;color:var(--dcp-ink3);margin:0 0 18px}
.dcp-roster-names{display:flex;flex-wrap:wrap;justify-content:center;gap:10px 12px;max-width:920px;margin:0 auto}
.dcp-roster-names span{font-size:.9rem;font-weight:600;color:var(--dcp-ink2);background:var(--dcp-bg);border:1px solid var(--dcp-line);border-radius:999px;padding:8px 16px}
</style>"""

def selected_section(ar):
    ltr = (lambda x: '<span dir="ltr">' + esc(x) + '</span>') if ar else (lambda x: esc(x))
    head = 'مشاريع مختارة في أنحاء المملكة' if ar else 'Selected projects across the Kingdom'
    sub = ('من المشاريع العملاقة والبنوك الوطنية والجامعات إلى مراكز البيانات الحيوية — عيّنة من أعمالنا المُنجزة.'
           if ar else 'From giga-projects and national banks to universities and mission-critical data centres — a sample of delivered work.')
    cards = ''.join(
        f'<article class="dcp-sp"><span class="dcp-sp-sec">{esc(se_a if ar else se_e)}</span>'
        f'<h3>{ltr(cl)}</h3><p>{esc(sc_a if ar else sc_e)}</p></article>'
        for cl, se_e, se_a, sc_e, sc_a in SELECTED)
    roster = ''.join(f'<span>{ltr(c)}</span>' for c in CLIENT_ROSTER)
    rhead = 'يثقون بنا' if ar else 'Trusted by'
    return (SELECTED_CSS
        + f'<section class="dcp-sec alt"><div class="dcp-wrap"><div class="dcp-head dcp-center">'
          f'<h2>{esc(head)}</h2><p>{esc(sub)}</p></div>'
          f'<div class="dcp-spgrid">{cards}</div>'
          f'<div class="dcp-roster"><h3>{esc(rhead)}</h3><div class="dcp-roster-names">{roster}</div></div>'
          f'</div></section>')

# Broader project reference list from the decks (client, year) by discipline. Client names
# are proper nouns (same in EN/AR, wrapped dir=ltr on the Arabic page); years are neutral.
REFERENCES = [
 ("Public address & voice alarm", "النداء العام والإنذار الصوتي", [
   ("General Directorate of Passports","2018"), ("General Directorate of Defence","2018"),
   ("General Directorate of Narcotics Control","2018"), ("General Directorate of Prisons","2019"),
   ("General Directorate of Technical Affairs","2019"), ("General Directorate of Border Guard","2019"),
   ("Sports Training Centres — Abha, Jazan, Makkah, Najran","2019"), ("Jawwy (STC)","2020"),
   ("Mövenpick Hotel, Dammam","2021"), ("Mansard Hotels (Radisson)","2022"),
   ("Danabay Resorts","2022"), ("Bank Al Bilad","2023"),
   ("KAP 4 — Ateis PA/VA",""), ("UCIC Factory — Ateis PA/VA",""), ("SDCC / SEC — Dammam, Qassim, Jubail",""),
 ]),
 ("Access control", "التحكم في الدخول", [
   ("STC Jawwy","2016"), ("Mansard Hotel & Residences","2018"), ("Al Tayyar Travels Group","2018"),
   ("Prince Naif Arab Academy","2018"), ("Madaen Star Group","2019"), ("AXA Insurance","2019"),
   ("Landmark Group","2019"), ("UCIC","2019"), ("Yousuf Naghi Motors","2020"),
   ("Mövenpick Hotel, Dammam","2021"), ("Danabay Resorts","2022"), ("SRA — Bay Airport","2023"),
   ("Red Sea Coastal Village","2023"), ("Red Sea Airport","2023"), ("NEOM Hospital","2024"),
   ("NEOM International Airport Services","2024"), ("Deloitte, Dammam","2024"), ("Deloitte, Riyadh","2024"),
 ]),
 ("CCTV & surveillance", "المراقبة بالكاميرات والأمن", [
   ("STC Jawwy","2016"), ("Riyadh Pharma","2017"), ("Arab Open University","2019"),
   ("King Khalid International Airport, Riyadh","2019"), ("Almarai","2018"), ("LAWASEQ","2018"),
   ("Mansard Hotels (Radisson)","2018"), ("The Red Sea","2023"), ("Red Sea Airport","2023"),
   ("Coastal Village","2023"), ("Saudi Royal Aviation — Jeddah, NEOM, Riyadh","2023"),
   ("NEOM Bay Airport","2023"), ("NEOM Hospital","2024"), ("NEOM International Airport","2024"),
   ("Bank Al Bilad","2024"), ("Deloitte — Dammam & Riyadh","2024"),
 ]),
 ("Networks, cabling & data centres", "الشبكات والتمديدات ومراكز البيانات", [
   ("SAMA — data centre (118 cabinets, SYSTIMAX imVision)",""), ("SABB — data-centre passive","2024"),
   ("Bank Al Bilad — passive","2024"), ("Zain Telecom — DC revamp (Cisco), Riyadh & Jeddah",""),
   ("Mobily — security DC upgrade",""), ("Landmark Arabia — complete data centre",""),
   ("Al Tayyar Travels — Tier-3 data centre",""), ("Mansard Hotel & Residence — Tier-3 data centre",""),
   ("Prince Naif Arab Academy — passive","2019"), ("KAP-2A — passive cabling","2018"),
   ("King Saud University — fibre optic","2018"), ("Tatweer — active & passive","2019"),
   ("NEOM — NIC camp Wi-Fi","2021"), ("NEOM — racking NC1/NC2 & P2P","2022"),
   ("NEOM — North Palaces fibre/UTP","2023"), ("Coastal Village — passive, security, UPS","2023"),
   ("NEOM Hospital — passive","2023"), ("National Housing Company — switches","2024"),
   ("STC Jawwy — passive","2016"), ("Dimension Data — passive","2017"),
 ]),
 ("Audio-visual & command centres", "الحلول السمعية والبصرية وغرف العمليات", [
   ("KAFD HQ — meeting & command rooms",""), ("Riyad Bank — control room & video wall",""),
   ("STC — command centres",""), ("Dimension Data — OCC & meeting rooms",""),
   ("Prince Sattam University (PSAU), Al-Kharj",""), ("Arab Open University — classrooms & council room",""),
   ("Mawhiba — auditorium & board rooms",""), ("NEOM — CEO meeting room",""),
   ("Marafiq — board & meeting rooms",""), ("MCIT — auditorium & board rooms",""),
   ("NUPCO — council room",""), ("Taqeem — meeting & board rooms",""),
   ("Landmark — meeting rooms",""), ("Wipro — office AV",""), ("Google Cloud — meeting room",""),
   ("Ma'aden PCS — video wall & command centre",""), ("NHC Sales Center — LED & interactive displays",""),
 ]),
]
# 5-phase delivery model from the company deck.
APPROACH = [
 ("Plan","التخطيط","Needs analysis, site surveys and a costed solution roadmap.","تحليل الاحتياجات والمسح الميداني وخارطة حل مُسعّرة."),
 ("Design","التصميم","Vendor-agnostic engineering to standard, validated at every stage.","هندسة محايدة تجاه المورّدين وفق المعايير، مُتحقَّق منها في كل مرحلة."),
 ("Build","التنفيذ","Certified installation teams delivering on time, on spec.","فرق تركيب معتمدة تُسلّم في الوقت وبالمواصفات."),
 ("Commission","التشغيل","Testing, configuration and warranty-backed sign-off.","اختبار وتهيئة وتسليم مدعوم بالضمان."),
 ("Support","الدعم","Ongoing maintenance, monitoring and lifecycle management.","صيانة ومراقبة وإدارة دورة حياة مستمرة."),
]
REF_CSS = """<style>
.dcp-approach{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-top:30px}
.dcp-apx{border:1px solid var(--dcp-line);border-radius:13px;padding:20px;background:var(--dcp-bg)}
.dcp-apx .n{font-family:inherit;font-weight:800;font-size:1.05rem;color:var(--dcp-teal-d)}
.dcp-apx h3{margin:8px 0 7px;font-size:1rem}
.dcp-apx p{margin:0;color:var(--dcp-ink2);font-size:.88rem;line-height:1.55}
.dcp-refgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:24px 30px;margin-top:30px}
.dcp-refcat h3{font-size:.8rem;letter-spacing:.06em;text-transform:uppercase;color:var(--dcp-teal-d);margin:0 0 10px;padding-bottom:9px;border-bottom:1px solid var(--dcp-line)}
.dcp-refcat ul{list-style:none;margin:0;padding:0}
.dcp-refcat li{display:flex;justify-content:space-between;gap:14px;padding:7px 0;border-bottom:1px dashed var(--dcp-line);font-size:.88rem}
.dcp-refcat li:last-child{border-bottom:0}
.dcp-refcat .rc{color:var(--dcp-ink)}
.dcp-refcat .ry{color:var(--dcp-ink3);flex:none;font-variant-numeric:tabular-nums}
</style>"""

def approach_section(ar):
    head = 'كيف نُسلّم' if ar else 'How we deliver'
    sub = ('فريق واحد مسؤول عبر دورة الحياة الكاملة — من التخطيط إلى الدعم.'
           if ar else 'One accountable team across the full lifecycle — from planning to support.')
    cells = ''.join(
        f'<div class="dcp-apx"><div class="n">0{i+1}</div><h3>{esc(pa if ar else pe)}</h3>'
        f'<p>{esc(da if ar else de)}</p></div>'
        for i,(pe,pa,de,da) in enumerate(APPROACH))
    return (f'<section class="dcp-sec"><div class="dcp-wrap"><div class="dcp-head dcp-center">'
            f'<h2>{esc(head)}</h2><p>{esc(sub)}</p></div><div class="dcp-approach">{cells}</div></div></section>')

def references_section(ar):
    ltr = (lambda x: '<span dir="ltr">' + esc(x) + '</span>') if ar else (lambda x: esc(x))
    head = 'مرجع المشاريع' if ar else 'Project reference list'
    sub = ('عيّنة أوسع من الأعمال المُنجَزة عبر التخصصات والسنوات — تُظهر عمق سجلّنا.'
           if ar else 'A broader sample of delivered work across disciplines and years — the depth behind the highlights.')
    blocks = ''
    for ce, ca, items in REFERENCES:
        rows = ''.join(f'<li><span class="rc">{ltr(cl)}</span>'
                       + (f'<span class="ry">{esc(yr)}</span>' if yr else '') + '</li>' for cl, yr in items)
        blocks += f'<div class="dcp-refcat"><h3>{esc(ca if ar else ce)}</h3><ul>{rows}</ul></div>'
    return (REF_CSS + f'<section class="dcp-sec"><div class="dcp-wrap"><div class="dcp-head dcp-center">'
            f'<h2>{esc(head)}</h2><p>{esc(sub)}</p></div><div class="dcp-refgrid">{blocks}</div></div></section>')

def build_projects(ar):
    s = STR['ar' if ar else 'en']
    U = CASE_UI['ar' if ar else 'en']
    cards = ''
    for i, p in enumerate(s['proj']):
        sector, city, name, body, kit, client, scope = p
        kits = ''.join(f'<span>{esc(k)}</span>' for k in kit)
        # only the five projects with a dedicated case-study page get a "read more" link;
        # the portfolio-deck showcase cards (CASE_SLUG[i] == '') show image + detail only.
        read_link = (f'<a class="dcp-dir" href="{loc("project-"+CASE_SLUG[i], ar)}">{esc(U["read"])} {I_ARROW}</a>'
                     if CASE_SLUG[i] else '')
        cards += f"""<article class="dcp-proj" data-disc="{' '.join(PROJ_DISC[i])}">
  <div class="ph"><img src="assets1/images/{PROJ_IMG[i]}" alt="{esc(name)}" loading="lazy" width="1200" height="750"></div>
  <div class="band"><span class="c">{esc(sector)}</span><span>{esc(city)}</span></div>
  <div class="in"><h3>{esc(name)}</h3><p class="body">{esc(body)}</p>
    <div class="dcp-kit">{kits}</div>
    <dl><dt>{esc(s['p_client'])}</dt><dd>{esc(client)}</dd>
        <dt>{esc(s['p_scope'])}</dt><dd>{esc(scope)}</dd></dl>
    {read_link}
  </div></article>"""
    feat = ''.join(f'<div class="dcp-featcell"><span class="dcp-featic">{FEAT_ICONS[i]}</span>'
                   f'<h3>{esc(t)}</h3><p>{esc(d)}</p></div>'
                   for i,(t,d) in enumerate(s['pj_feat']))
    gal = ''.join(f'<figure><img src="assets1/images/{g[0]}" alt="{esc(g[2] if ar else g[1])}" '
                  f'loading="lazy" width="900" height="600">'
                  f'<figcaption>{esc(g[2] if ar else g[1])}</figcaption></figure>' for g in GAL_IMG)
    # ── two-column hero + working filter bar (matches the live projects hero layout,
    #    but with our own engineer-voice copy instead of the generic blurb) ──
    ghost = 'PROJECT' if not ar else 'مشاريع'
    crumb = (f'<div class="dcp-crumb"><a href="{loc("index",ar)}">{esc(s["home"])}</a> '
             f'&rsaquo; {esc(s["pj_title"])}</div>')
    sub = ('استكشف أمثلة واقعية من حلولنا وهي قيد التشغيل، من خلال دراسات الحالة.'
           if ar else 'Explore real-world examples of our solutions in action, through our case studies.')
    rpar = ('كل مشروع هنا نظام صمّمناه وورّدناه وركّبناه وسلّمناه بأنفسنا — عملاء محدّدون، والمعدات '
            'الفعلية التي رُكّبت، والمعايير التي بُني عليها: من التمديدات الهيكلية وشبكات الواي فاي إلى '
            'جدران فيديو LED والإخلاء الصوتي والتحكم في الدخول، عبر مدارس وحُرم جامعية وقاعات مجالس في '
            'المملكة.' if ar else
            'Every project here is a system we designed, supplied, installed and handed over ourselves '
            '— named clients, the exact equipment deployed, and the standards it was built to. From '
            'structured cabling and Wi-Fi networks to LED video walls, voice evacuation and access '
            'control, across schools, campuses and boardrooms in Saudi Arabia.')
    present = [d for d in DISCIPLINES if any(d[0] in dd for dd in PROJ_DISC)]
    alllbl = 'كل الخدمات' if ar else 'All Services'
    optl = (f'<li role="option" data-value="" data-label="{esc(alllbl)}" class="is-sel" aria-selected="true"><span>{esc(alllbl)}</span><span class="tick" aria-hidden="true">✓</span></li>'
            + ''.join(f'<li role="option" data-value="{d[0]}" data-label="{esc(d[2] if ar else d[1])}" aria-selected="false"><span>{esc(d[2] if ar else d[1])}</span><span class="tick" aria-hidden="true">✓</span></li>' for d in present))
    ph = 'ابحث في المشاريع…' if ar else 'Search projects…'
    noresult = 'لا توجد مشاريع مطابقة.' if ar else 'No projects match your search.'
    search_svg = ('<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" '
                  'stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/>'
                  '<path d="M21 21l-4.3-4.3"/></svg>')
    phero = (f'<section class="dcp-hero dcp-phero"><div class="dcp-ghost" aria-hidden="true">{esc(ghost)}</div>'
             f'<div class="dcp-wrap"><div class="dcp-phero-grid">'
             f'<div class="dcp-phero-l">{crumb}<h1>{esc(s["pj_title"])}</h1>'
             f'<p class="dcp-lede">{esc(sub)}</p></div>'
             f'<div class="dcp-phero-r"><p>{esc(rpar)}</p></div></div></div></section>'
             f'<section class="dcp-pfilter-sec"><div class="dcp-wrap">'
             f'<div class="dcp-pfilter"><div class="dcp-pf-search">{search_svg}'
             f'<input type="search" id="dcp-psearch" placeholder="{esc(ph)}" aria-label="{esc(ph)}"></div>'
             f'<div class="dcp-pf-drop" id="dcp-pservice" data-value="">'
             f'<button type="button" class="dcp-pf-btn" aria-haspopup="listbox" aria-expanded="false" aria-label="{esc(alllbl)}">'
             f'<span class="dcp-pf-cur">{esc(alllbl)}</span>'
             f'<svg class="dcp-pf-caret" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>'
             f'</button>'
             f'<ul class="dcp-pf-menu" role="listbox" hidden>{optl}</ul>'
             f'</div>'
             f'</div></div></section>')
    body = (
      PROJ_FILTER_CSS + phero
      + stats_marquee(ar)
      + approach_section(ar)
      + f'<section class="dcp-sec"><div class="dcp-wrap"><div class="dcp-projs" id="dcp-projgrid">{cards}'
        f'<p class="dcp-noresult" id="dcp-noresult" hidden>{esc(noresult)}</p></div></div></section>'
      + selected_section(ar)
      + references_section(ar)
      + f'<section class="dcp-sec alt"><div class="dcp-wrap"><div class="dcp-head dcp-center">'
        f'<h2>{esc(s["pj_gal_h"])}</h2><p>{esc(s["pj_gal_p"])}</p></div>'
        f'<div class="dcp-gal">{gal}</div></div></section>'
      + f'<section class="dcp-sec"><div class="dcp-wrap"><div class="dcp-head dcp-center">'
        f'<h2>{esc(s["pj_feat_h"])}</h2></div><div class="dcp-featgrid">{feat}</div></div></section>'
      + cta_band(ar) + footer(ar) + PROJ_FILTER_JS)
    title = ('مشاريعنا | داتاكور للحلول' if ar else 'Projects | Datacore Solutions')
    return shell(ar, 'projects', title, s['pj_lede'], body)

# ── CASE-STUDY DETAIL PAGES ───────────────────────────────────────────────
def build_case(slug, ar):
    lang = 'ar' if ar else 'en'
    C = CASES[slug]; c = C[lang]; U = CASE_UI[lang]; s = STR[lang]
    E = (lambda x: wrap_ltr(esc(x))) if ar else (lambda x: esc(x))
    crumb = (f'<div class="dcp-crumb"><a href="{loc("index",ar)}">{esc(s["home"])}</a> &rsaquo; '
             f'<a href="{loc("projects",ar)}">{esc(U["projects"])}</a> &rsaquo; {E(c["name"])}</div>')
    hero = (f'<section class="dcp-hero"><div class="dcp-wrap">{crumb}'
            f'<h1>{E(c["name"])}</h1><p class="dcp-lede">{E(c["lede"])}</p></div></section>')
    photo = (f'<section class="dcp-sec"><div class="dcp-wrap"><figure class="dcp-svc-shot">'
             f'<img src="assets1/images/{C["img"]}" alt="{esc(c["name"])}" loading="lazy" width="1200" height="750">'
             f'</figure></div></section>')
    # "At a glance" facts — styled inline so no new CSS / VER bump is needed
    facts = [(U['client'], c.get('client')), (U['sector'], c.get('sector')), (U['location'], c.get('city'))]
    if c.get('completed'): facts.append((U['completed'], c['completed']))
    facts.append((U['scope'], c.get('scope')))
    frows = ''.join(
        '<div style="display:flex;justify-content:space-between;gap:14px;padding:8px 0;'
        'border-block-start:1px solid rgba(128,128,128,.18)">'
        f'<dt style="color:var(--dcp-ink3);font-size:.82rem">{esc(k)}</dt>'
        f'<dd style="margin:0;text-align:end;font-weight:600">{E(v)}</dd></div>'
        for k, v in facts if v)
    kit = ''.join(f'<span>{E(k)}</span>' for k in c.get('kit', []))
    kit_block = f'<h3 style="margin-top:18px">{esc(U["kit"])}</h3><div class="dcp-kit">{kit}</div>' if kit else ''
    glance = (f'<div class="box"><h3>{esc(U["at_glance"])}</h3>'
              f'<dl style="margin:.4rem 0 0">{frows}</dl>{kit_block}</div>'
              f'<div class="box cta"><h3>{esc(U["get"])}</h3><p>{esc(U["get_p"])}</p>'
              f'<a class="dcp-btn" href="{loc("contact",ar)}">{esc(s["consult"])} {I_ARROW}</a></div>')
    secs = ''
    for sec in c.get('sections', []):
        ps = ''.join(f'<p>{E(p)}</p>' for p in sec.get('ps', []))
        secs += f'<section><h2>{E(sec["h"])}</h2>{ps}</section>'
    body_sec = (f'<section class="dcp-sec"><div class="dcp-wrap"><div class="dcp-svc-grid">'
                f'<div class="dcp-svc-body">{secs}</div>'
                f'<aside class="dcp-aside">{glance}</aside></div></div></section>')
    gal = ''
    if c.get('gallery'):
        figs = ''.join(f'<figure><img src="assets1/images/{g["img"]}" alt="{esc(g["cap"])}" '
                       f'loading="lazy" width="1100" height="700"><figcaption>{E(g["cap"])}</figcaption></figure>'
                       for g in c['gallery'])
        gal = (f'<section class="dcp-sec alt"><div class="dcp-wrap"><div class="dcp-head dcp-center">'
               f'<h2>{esc(U["gallery"])}</h2></div><div class="dcp-gal">{figs}</div></div></section>')
    body = hero + photo + body_sec + gal + cta_band(ar) + footer(ar)
    schema = {"@context": "https://schema.org", "@type": "CreativeWork", "name": c["name"],
              "about": c.get("client"), "creator": {"@id": SITE + "/#org"},
              "publisher": {"@id": SITE + "/#org"},
              "image": SITE + "/assets1/images/" + C["img"], "inLanguage": lang}
    if c.get("date_iso"): schema["datePublished"] = c["date_iso"]
    head = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False) + '</script>'
    title = c["name"] + (" | داتاكور للحلول" if ar else " | Datacore Solutions")
    return shell(ar, "projects", title, c["lede"][:180], body, extra_head=head, canon="project-" + slug)

# ── FAQ ───────────────────────────────────────────────────────────────────
FAQ_CSS = ('<style>'
  '.dcp-faq{border-block-end:1px solid var(--dcp-line,#e6ebea)}'
  '.dcp-faq summary{cursor:pointer;padding:20px 2px;font-weight:700;font-size:1.06rem;'
  'list-style:none;display:flex;justify-content:space-between;gap:18px;align-items:center}'
  '.dcp-faq summary::-webkit-details-marker{display:none}'
  '.dcp-faq summary::after{content:"+";color:var(--dcp-teal-d,#00776f);font-weight:400;'
  'font-size:1.6rem;line-height:1;flex:none;transition:transform .2s}'
  '.dcp-faq[open] summary::after{content:"\\2013"}'
  '.dcp-faq-a{padding:0 2px 22px;color:var(--dcp-ink2,#555);max-width:70ch;line-height:1.75}'
  '.dcp-faq-a p{margin:0}'
  '</style>')

def build_faq(ar):
    lang = 'ar' if ar else 'en'; F = FAQ[lang]
    E = (lambda x: wrap_ltr(esc(x))) if ar else (lambda x: esc(x))
    ghost = 'أسئلة' if ar else 'FAQ'
    items = ''.join(
        f'<details class="dcp-faq"><summary>{E(q)}</summary>'
        f'<div class="dcp-faq-a"><p>{E(a)}</p></div></details>'
        for q, a in F['items'])
    body = (hero(ar, ghost, F['h1'], F['h1'], F['lede'])
            + f'<section class="dcp-sec"><div class="dcp-wrap" style="max-width:840px">{items}</div></section>'
            + cta_band(ar) + footer(ar))
    schema = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q,
                              "acceptedAnswer": {"@type": "Answer", "text": a}}
                             for q, a in F['items']]}
    head = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False) + '</script>' + FAQ_CSS
    return shell(ar, 'faq', F['title'], F['lede'], body, extra_head=head, canon='faq')

# ── GLOSSARY ────────────────────────────────────────────────────────────────
GLOSSARY_CSS = ('<style>'
  '.dcp-gloss{margin:0}'
  '.dcp-gloss>div{padding:18px 2px;border-block-end:1px solid var(--dcp-line,#e6ebea);'
  'display:grid;grid-template-columns:minmax(190px,1fr) 2fr;gap:8px 30px;align-items:start}'
  '.dcp-gloss dt{margin:0;font-weight:700;font-size:1.02rem;color:var(--dcp-teal-d,#00776f)}'
  '.dcp-gloss dd{margin:0;color:var(--dcp-ink2,#555);line-height:1.72;max-width:70ch}'
  '@media(max-width:640px){.dcp-gloss>div{grid-template-columns:1fr;gap:5px}}'
  '</style>')

def build_glossary(ar):
    lang = 'ar' if ar else 'en'; G = GLOSSARY[lang]
    E = (lambda x: wrap_ltr(esc(x))) if ar else (lambda x: esc(x))
    ghost = 'مسرد' if ar else 'Glossary'
    rows = ''.join(
        f'<div id="gloss-{i}"><dt>{E(t)}</dt><dd>{E(d)}</dd></div>'
        for i, (t, d) in enumerate(G['terms']))
    body = (hero(ar, ghost, G['h1'], G['h1'], G['lede'])
            + f'<section class="dcp-sec"><div class="dcp-wrap" style="max-width:900px">'
              f'<dl class="dcp-gloss">{rows}</dl></div></section>'
            + cta_band(ar) + footer(ar))
    setid = SITE + '/' + loc('glossary', ar) + '#set'
    schema = {"@context": "https://schema.org", "@type": "DefinedTermSet", "@id": setid,
              "name": G['title'], "inLanguage": lang,
              "hasDefinedTerm": [{"@type": "DefinedTerm", "name": t, "description": d,
                                  "inDefinedTermSet": {"@id": setid}} for t, d in G['terms']]}
    head = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False) + '</script>' + GLOSSARY_CSS
    return shell(ar, 'glossary', G['title'], G['lede'], body, extra_head=head, canon='glossary')

# ── INSIGHTS ────────────────────────────────────────────────────────────
def build_insights(ar):
    lang = 'ar' if ar else 'en'
    s = STR[lang]
    E = (lambda x: wrap_ltr(esc(x))) if ar else (lambda x: esc(x))
    read = 'اقرأ المقال' if ar else 'Read the article'
    cards = ''
    for i, p in enumerate(INSIGHTS[lang]['posts']):
        cards += f"""<article class="dcp-post">
  <div class="ph"><a href="{loc('insight-'+p['slug'],ar)}"><img src="assets1/images/{POST_IMG[i]}?v={VER}" alt="{esc(p['title'])}" loading="lazy" width="561" height="306"></a></div>
  <div class="in"><span class="by">{E(p['date'])} &middot; {E(p['team'])}</span>
    <h3><a href="{loc('insight-'+p['slug'],ar)}">{E(p['title'])}</a></h3><p>{E(p['dek'])}</p>
    <a class="dcp-dir" href="{loc('insight-'+p['slug'],ar)}">{esc(read)} {I_ARROW}</a></div></article>"""
    body = (hero(ar, 'NOTES' if not ar else 'ملاحظات', s['i_title'], s['i_title'], s['i_lede'])
      + f'<section class="dcp-sec"><div class="dcp-wrap"><div class="dcp-posts">{cards}</div></div></section>'
      + cta_band(ar) + footer(ar))
    title = ('ملاحظات تقنية | داتاكور للحلول' if ar else 'Technical notes | Datacore Solutions')
    return shell(ar, 'insights', title, s['i_lede'], body)

# ── INSIGHT ARTICLE (per-post detail page) ──────────────────────────────────
POST_CSS = ('<style>'
  '.dcp-art-fig{max-width:760px;margin:0 auto 30px;border:1px solid var(--dcp-line,#e6ebea);'
  'border-radius:8px;overflow:hidden}'
  '.dcp-art-fig img{width:100%;height:auto;display:block}'
  '.dcp-article{max-width:720px;margin:0 auto}'
  '.dcp-article p{color:var(--dcp-ink2,#444);line-height:1.8;font-size:1.05rem;margin:0 0 20px}'
  '.dcp-article h2{font-size:1.4rem;line-height:1.3;margin:36px 0 12px;color:var(--dcp-ink,#1a202c)}'
  '.dcp-hero .byline{color:var(--dcp-ink3,#8a949a);font-size:.9rem;margin:0 0 4px;font-weight:600;'
  'letter-spacing:.02em}'
  '.dcp-related{max-width:720px;margin:34px auto 0;padding:22px 24px;border:1px solid var(--dcp-line,#e6ebea);'
  'border-radius:8px;background:var(--dcp-soft,#f5f9f8)}'
  '.dcp-related h2{font-size:1.02rem;margin:0 0 12px;color:var(--dcp-ink,#1a202c)}'
  '.dcp-related a{display:inline-flex;align-items:center;gap:5px;margin:0 16px 8px 0;'
  'color:var(--dcp-teal-d,#00776f);font-weight:600;text-decoration:none}'
  '.dcp-related a:hover{text-decoration:underline}'
  '</style>')

def build_post(i, ar):
    lang = 'ar' if ar else 'en'
    P = INSIGHTS[lang]['posts'][i]; s = STR[lang]
    E = (lambda x: wrap_ltr(esc(x))) if ar else (lambda x: esc(x))
    ins_lbl = 'ملاحظات تقنية' if ar else 'Insights'
    ghost = 'ملاحظات' if ar else 'NOTES'
    crumb = (f'<div class="dcp-crumb"><a href="{loc("index",ar)}">{esc(s["home"])}</a> '
             f'&rsaquo; <a href="{loc("insights",ar)}">{esc(ins_lbl)}</a> '
             f'&rsaquo; {E(P["title"])}</div>')
    hero_html = (f'<section class="dcp-hero"><div class="dcp-ghost" aria-hidden="true">{esc(ghost)}</div>'
                 f'<div class="dcp-wrap">{crumb}'
                 f'<p class="byline">{E(P["date"])} &middot; {E(P["team"])}</p>'
                 f'<h1>{E(P["title"])}</h1><p class="dcp-lede">{E(P["dek"])}</p></div></section>')
    fig = (f'<figure class="dcp-art-fig"><img src="assets1/images/{POST_IMG[i]}?v={VER}" '
           f'alt="{esc(P["title"])}" width="561" height="306"></figure>')
    blocks = ''.join(f'<{typ}>{E(txt)}</{typ}>' for typ, txt in P['blocks'])
    faq = P.get('faq', [])
    faq_html = ''
    if faq:
        items = ''.join(f'<details class="dcp-faq"><summary>{E(q)}</summary>'
                        f'<div class="dcp-faq-a"><p>{E(a)}</p></div></details>' for q, a in faq)
        faq_h = 'أسئلة شائعة' if ar else 'Frequently asked'
        faq_html = (f'<div class="dcp-faqwrap" style="max-width:720px;margin:36px auto 0">'
                    f'<h2 style="font-size:1.4rem;margin:0 0 6px">{esc(faq_h)}</h2>{items}</div>')
    rel = ''.join(f'<a href="{loc("service-"+slug,ar)}">{E(anchor)} {I_ARROW}</a>'
                  for slug, anchor in P['related'])
    rel_h = 'خدمات ذات صلة' if ar else 'Related services'
    body = (hero_html
            + f'<section class="dcp-sec"><div class="dcp-wrap">{fig}'
              f'<div class="dcp-article">{blocks}</div>{faq_html}'
              f'<div class="dcp-related"><h2>{esc(rel_h)}</h2>{rel}</div></div></section>'
            + cta_band(ar) + footer(ar))
    url = SITE + '/' + loc('insight-' + P['slug'], ar)
    schema = [{"@context": "https://schema.org", "@type": "BlogPosting",
               "headline": P['title'], "description": P['meta'],
               "datePublished": POST_ISO[i], "dateModified": POST_ISO[i], "inLanguage": lang,
               "image": SITE + '/assets1/images/' + POST_IMG[i],
               "author": {"@type": "Organization", "name": "Datacore Solutions", "@id": SITE + '/#org'},
               "publisher": {"@id": SITE + '/#org'},
               "mainEntityOfPage": {"@type": "WebPage", "@id": url}}]
    if faq:
        schema.append({"@context": "https://schema.org", "@type": "FAQPage",
                       "mainEntity": [{"@type": "Question", "name": q,
                                       "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
    head = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False) + '</script>' + FAQ_CSS + POST_CSS
    title = P['title'] + (' | داتاكور للحلول' if ar else ' | Datacore Solutions')
    return shell(ar, 'insights', title, P['meta'], body, extra_head=head, canon='insight-' + P['slug'])

# ── SEO LANDING PAGES (query-targeted solution pages) ───────────────────────
LANDING_KEYS = [p['slug'] for p in LANDING['en']['pages']]
LANDING_CSS = ('<style>'
  '.dcp-facts{display:flex;flex-wrap:wrap;gap:16px 44px;margin:22px 0 4px;padding:18px 0;'
  'border-block:1px solid var(--dcp-line,#e6ebea)}'
  '.dcp-facts>div{display:flex;flex-direction:column}'
  '.dcp-facts b{font-size:1.55rem;line-height:1;color:var(--dcp-teal-d,#00776f);font-weight:700}'
  '.dcp-facts span{font-size:.82rem;color:var(--dcp-ink3,#8a949a);margin-top:4px}'
  '.dcp-land h2{font-size:1.42rem;margin:34px 0 12px;color:var(--dcp-ink,#1a202c)}'
  '.dcp-land p{color:var(--dcp-ink2,#444);line-height:1.8;font-size:1.04rem;margin:0 0 18px;max-width:70ch}'
  '.dcp-land .dcp-faqwrap{margin-top:30px}'
  '.dcp-land .dcp-faqwrap>h2{margin-bottom:6px}'
  '</style>')
FACTS = {'en': [('19+', 'years, since 2007'), ('180+', 'specialists'), ('38', 'services'), ('1,500+', 'clients')],
         'ar': [('19+', 'سنة، منذ 2007'), ('180+', 'مختص'), ('38', 'خدمة'), ('1,500+', 'عميل')]}

def build_landing(idx, ar):
    lang = 'ar' if ar else 'en'
    Pg = LANDING[lang]['pages'][idx]; s = STR[lang]
    E = (lambda x: wrap_ltr(esc(x))) if ar else (lambda x: esc(x))
    svc_lbl = 'خدماتنا' if ar else 'Services'
    ghost = 'حلول' if ar else 'SOLUTIONS'
    crumb = (f'<div class="dcp-crumb"><a href="{loc("index",ar)}">{esc(s["home"])}</a> '
             f'&rsaquo; <a href="{loc("services",ar)}">{esc(svc_lbl)}</a> '
             f'&rsaquo; {E(Pg["nav"])}</div>')
    hero_html = (f'<section class="dcp-hero"><div class="dcp-ghost" aria-hidden="true">{esc(ghost)}</div>'
                 f'<div class="dcp-wrap">{crumb}<h1>{E(Pg["h1"])}</h1>'
                 f'<p class="dcp-lede">{E(Pg["dek"])}</p></div></section>')
    facts = '<div class="dcp-facts">' + ''.join(
        f'<div><b dir="ltr">{esc(n)}</b><span>{E(l)}</span></div>' for n, l in FACTS[lang]) + '</div>'
    blocks = ''.join(f'<{t}>{E(x)}</{t}>' for t, x in Pg['blocks'])
    faq_items = ''.join(
        f'<details class="dcp-faq"><summary>{E(q)}</summary>'
        f'<div class="dcp-faq-a"><p>{E(a)}</p></div></details>' for q, a in Pg['faq'])
    faq_h = 'أسئلة شائعة' if ar else 'Frequently asked'
    rel = ''.join(f'<a href="{loc("service-"+sl,ar)}">{E(an)} {I_ARROW}</a>' for sl, an in Pg['related'])
    rel_h = 'خدمات ذات صلة' if ar else 'Related services'
    body = (hero_html
            + f'<section class="dcp-sec"><div class="dcp-wrap" style="max-width:820px"><div class="dcp-land">'
              f'{facts}{blocks}'
              f'<div class="dcp-faqwrap"><h2>{esc(faq_h)}</h2>{faq_items}</div>'
              f'<div class="dcp-related"><h2>{esc(rel_h)}</h2>{rel}</div>'
              f'</div></div></section>'
            + cta_band(ar) + footer(ar))
    url = SITE + '/' + loc('' + Pg['slug'], ar)
    schema = [
        {"@context": "https://schema.org", "@type": "Service", "name": Pg['h1'],
         "serviceType": Pg['nav'], "description": Pg['meta'], "inLanguage": lang,
         "areaServed": {"@type": "Country", "name": "Saudi Arabia"},
         "provider": {"@id": SITE + '/#org'}, "url": url},
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q,
                         "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in Pg['faq']]}]
    head = ('<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False) + '</script>'
            + FAQ_CSS + POST_CSS + LANDING_CSS)
    return shell(ar, 'services', Pg['title'], Pg['meta'], body, extra_head=head, canon=Pg['slug'])

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
    var g=function(id){{var el=form.querySelector(id);return el?el.value:'';}};
    var fd={{name:g('#q-name'),company:g('#q-co'),email:g('#q-mail'),phone:g('#q-tel'),
             type:g('#q-type'),project:g('#q-proj'),message:g('#q-msg'),reference:ref}};
    var btn=form.querySelector('button[type=submit]');if(btn){{btn.disabled=true;}}
    window.dcpDeliver(fd,'{("استفسار من الموقع" if ar else "Website enquiry")} — '+(fd.name||'')).then(function(mode){{
      var ok=document.createElement('div');
      ok.className='dcp-form';ok.setAttribute('role','status');
      var msg=(mode==='sent')
        ?'{("رقمك المرجعي" if ar else "Your reference number is")} <strong>'+ref+'</strong>. {("سنرد خلال يوم عمل واحد." if ar else "We will reply within one working day.")}'
        :'{("فتحنا رسالتك في تطبيق البريد لديك — أرسلها وسنرد خلال يوم عمل واحد." if ar else "Your message is ready in your email app — send it and we will reply within one working day.")} {("المرجع" if ar else "Ref")} <strong>'+ref+'</strong>.';
      ok.innerHTML='<h2>{("تم استلام استفسارك" if ar else "Enquiry received")}</h2>'
        +'<p style="color:var(--dcp-ink2)">'+msg+'</p>';
      form.replaceWith(ok);
    }});
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
        w(loc('faq', ar), build_faq(ar))
        w(loc('glossary', ar), build_glossary(ar))
        for i in range(len(POST_SLUG)):
            w(loc('insight-' + POST_SLUG[i], ar), build_post(i, ar))
        for i in range(len(LANDING_KEYS)):
            w(loc(LANDING_KEYS[i], ar), build_landing(i, ar))
        for slug in CASE_SLUG:
            if not slug: continue   # showcase-only cards have no dedicated case page
            w(loc('project-' + slug, ar), build_case(slug, ar))
    print("done")
