# -*- coding: utf-8 -*-
"""Generate the mirror's 38 service-detail pages (EN+AR = 76 files) in the live
look, from the copy fetched verbatim into services-copy.json. Flat filenames
service-<slug>.html at the mirror root; the overlay rewrites the live
services.html 'service-details/<slug>' links to these at runtime, so the live
pages stay byte-for-byte untouched. Adds the methodology band (design #4)."""
import os, sys, json, html
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_pages import shell, cta_band, footer, esc, loc, STR, ROOT, I_ARROW, SITE, INSIGHTS

# slug -> (EN title, AR title) so service pages can link the matching guides
_ITITLE = {e["slug"]: (e["title"], a.get("title", e["title"]))
           for e, a in zip(INSIGHTS["en"]["posts"], INSIGHTS["ar"]["posts"])}
# discipline index (see DISC below) -> related insight slugs. Internal links from the
# money pages (services) to the guides deepen topical authority and keep readers on site.
DISC_INSIGHTS = {
  0: ["structured-cabling-standards-explained", "single-mode-vs-multimode-fibre", "wifi-site-survey-guide"],
  1: ["data-centre-design-essentials", "active-vs-passive-network-infrastructure"],
  2: ["designing-cctv-for-coverage", "access-control-credentials-compared", "control-room-soc-noc-design"],
  3: ["hybrid-meeting-room-av", "control-room-soc-noc-design"],
  4: ["hybrid-meeting-room-av", "smart-building-elv-convergence"],
  5: ["led-video-wall-pixel-pitch", "digital-signage-that-works"],
  6: ["what-is-a-public-address-system", "voice-evacuation-en54-sbc801"],
  7: ["iptv-for-enterprise-hospitality"],
  8: ["why-annual-maintenance-contracts-matter", "choosing-an-elv-contractor-saudi-arabia"],
}
def related_reading(di, ar):
    slugs = DISC_INSIGHTS.get(di, [])
    if not slugs:
        return ""
    head = "قراءة ذات صلة" if ar else "Related reading"
    links = "".join(
        f'<a class="dcp-dir" href="{loc("insight-"+sl, ar)}">{esc(_ITITLE.get(sl,(sl,sl))[1 if ar else 0])} {I_ARROW}</a>'
        for sl in slugs)
    return (f'<section class="dcp-sec alt"><div class="dcp-wrap" style="max-width:820px">'
            f'<div class="dcp-head"><h2>{esc(head)}</h2></div>'
            f'<div style="display:flex;flex-direction:column;gap:13px">{links}</div></div></section>')

DATA = r"C:\Users\afnan\Documents\Datacore\Datacore Website\datacore-web\src\data"
SVC = json.load(open(os.path.join(DATA, "services-copy.json"), encoding="utf-8"))["services"]
# The live AR service pages are empty shells; the Arabic copy was authored
# separately into services-copy-ar.json. Use that for AR, live copy for EN.
SVC_AR = json.load(open(os.path.join(DATA, "services-copy-ar.json"), encoding="utf-8"))["services"]

# The copy was captured from the live site ALREADY HTML-escaped (e.g. "&amp;"),
# and every field flows through esc() once before output — so a raw load double-
# escapes ("&amp;" -> "&amp;amp;", visible literally in titles/SERPs). Unescape the
# copy once here so a single esc() at render time produces correct entities.
def _unesc(o):
    if isinstance(o, str):  return html.unescape(o)
    if isinstance(o, list): return [_unesc(x) for x in o]
    if isinstance(o, dict): return {k: _unesc(v) for k, v in o.items()}
    return o
SVC = _unesc(SVC); SVC_AR = _unesc(SVC_AR)
SLUGS = list(SVC.keys())

def copy_of(slug, ar):
    return (SVC_AR.get(slug) or {}) if ar else SVC[slug]["en"]

# 9 disciplines in header order; counts slice the ordered slug list (sum = 38)
DISC = [
  ("network-infrastructure-services", "Network Infrastructure Services", "البنية التحتية للشبكات",
   "Cat6A · OM4 · TIA-568 · ISO/IEC 11801", "Cat6A · OM4 · TIA-568 · ISO/IEC 11801", 6),
  ("datacenter-solutions", "Datacenter Solutions", "حلول مراكز البيانات",
   "Containment · power · cooling · DCIM", "الاحتواء · الطاقة · التبريد · DCIM", 3),
  ("surveillance-and-security-solutions", "Surveillance & Security Solutions", "حلول المراقبة والأمن",
   "ONVIF · integrated with HR and visitor systems", "ONVIF · تكامل مع أنظمة الموارد البشرية والزوّار", 4),
  ("meeting-room-solutions", "Meeting Room Solutions", "حلول قاعات الاجتماعات",
   "Teams Rooms · Zoom Rooms · BYOD", "Teams Rooms · Zoom Rooms · BYOD", 5),
  ("audio-visual-solutions", "Audio-Visual Solutions", "الحلول السمعية والبصرية",
   "AV-over-IP · Dante · programmed control", "AV-over-IP · Dante · تحكم مبرمج", 8),
  ("digital-signage-amp-video-walls", "Digital Signage & Video Walls", "اللافتات الرقمية وشاشات العرض",
   "Fine-pitch LED · content management", "LED دقيقة الخطوة · إدارة المحتوى", 4),
  ("public-address-and-fire-alarm-system", "Public Address & Fire Alarm", "النداء الآلي وإنذار الحريق",
   "EN 54-16 · EN 54-24 · Saudi Building Code", "EN 54-16 · EN 54-24 · كود البناء السعودي", 4),
  ("iptv-solutions", "IPTV Solutions", "حلول IPTV",
   "Hospitality · healthcare · campus distribution", "الضيافة · الرعاية الصحية · التوزيع الجامعي", 2),
  ("professional-services", "Professional Services", "الخدمات الاحترافية",
   "SLA-backed · on-site resident engineers", "مدعوم باتفاقية مستوى خدمة · مهندسون مقيمون", 2),
]
# slug -> discipline index
SLUG_DISC = {}
i = 0
for di, d in enumerate(DISC):
    for _ in range(d[5]):
        SLUG_DISC[SLUGS[i]] = di; i += 1
assert i == len(SLUGS) == 38, (i, len(SLUGS))

METHOD = {
 "en": ("How we deliver", [
   ("Survey", "We start on site — a measured survey of the building, not a pick from a catalogue."),
   ("Design", "A design justified against your operational requirement and the relevant standard."),
   ("Install & commission", "Our own engineers install, then commission with documented test results."),
   ("Maintain", "Response-time-backed cover and scheduled preventive visits after handover."),
 ]),
 "ar": ("كيف ننفّذ", [
   ("المسح", "نبدأ من الموقع — مسح ميداني مقاس للمبنى، لا اختيار من كتالوج."),
   ("التصميم", "تصميم مبرَّر بمتطلبك التشغيلي وبالمعيار ذي الصلة."),
   ("التركيب والتشغيل", "كوادرنا تتولى التركيب ثم التشغيل بنتائج اختبار موثّقة."),
   ("الصيانة", "تغطية مدعومة بزمن استجابة وزيارات وقائية مجدولة بعد التسليم."),
 ]),
}
UI = {
 "en": {"home": "Home", "services": "Services", "in_disc": "In this discipline",
        "get": "Talk to an engineer", "get_p": "Tell us the building and the stage you are at.",
        "ask": "Request a consultation", "sections_more": "What this covers"},
 "ar": {"home": "الرئيسية", "services": "خدماتنا", "in_disc": "ضمن هذا التخصص",
        "get": "تحدّث إلى مهندس", "get_p": "أخبرنا بالمبنى والمرحلة التي أنت فيها.",
        "ask": "اطلب استشارة", "sections_more": "ما يشمله هذا"},
}

def svc_file(slug, ar): return "service-" + slug + ("-ar" if ar else "") + ".html"

# Real OWIS Riyadh project photos shown on matching service pages: (img, en cap, ar cap)
SVC_PHOTO = {
 "auditorium": ("dc-proj-owis-auditorium.jpg", "Auditorium video wall — OWIS Riyadh", "جدار فيديو المسرح — مدرسة ون وورلد الرياض"),
 "indoor-led-video-wall": ("dc-proj-owis-auditorium.jpg", "2.5 mm indoor LED video wall — OWIS Riyadh", "جدار فيديو LED داخلي 2.5 مم — مدرسة ون وورلد الرياض"),
 "access-control-solutions": ("dc-proj-owis-access.jpg", "Suprema face & fingerprint access — OWIS Riyadh", "تحكّم في الدخول بالوجه والبصمة — مدرسة ون وورلد الرياض"),
 "structured-cabling-solutions": ("dc-proj-owis-rack.jpg", "Communications rack — OWIS Riyadh", "خزانة الاتصالات — مدرسة ون وورلد الرياض"),
 "it-network-solutions": ("dc-proj-owis-rack.jpg", "Network core — OWIS Riyadh", "نواة الشبكة — مدرسة ون وورلد الرياض"),
 "smart-class-rooms": ("dc-proj-owis-classroom.jpg", "Interactive-panel classroom — OWIS Riyadh", "فصل بشاشة تفاعلية — مدرسة ون وورلد الرياض"),
 "smart-meeting-room-amp-boardroom-solution": ("dc-proj-owis-panel.jpg", "Interactive display — OWIS Riyadh", "شاشة تفاعلية — مدرسة ون وورلد الرياض"),
 "professional-audio": ("dc-proj-owis-mixer.jpg", "Soundcraft mixer, auditorium — OWIS Riyadh", "مازج صوت المسرح — مدرسة ون وورلد الرياض"),
}

def sections_html(sec):
    out = ""
    for s in sec:
        ps = "".join("<p>" + esc(p) + "</p>" for p in s.get("ps", []))
        h = esc(s.get("h", "")).strip()
        out += "<section>" + (("<h2>" + h + "</h2>") if h else "") + ps + "</section>"
    return out

def build(slug, ar):
    lang = "ar" if ar else "en"
    c = copy_of(slug, ar); di = SLUG_DISC[slug]; d = DISC[di]
    U = UI[lang]; s = STR[lang]
    disc_name = d[2] if ar else d[1]; std = d[4] if ar else d[3]
    h1 = c.get("h1") or c.get("title") or slug
    intro = c.get("intro", "")
    # standards chips (codes stay LTR)
    chips = "".join('<span dir="ltr">' + esc(x.strip()) + "</span>" for x in std.split("·"))
    # breadcrumb + hero
    crumb = (f'<div class="dcp-crumb"><a href="{loc("index",ar)}">{esc(U["home"])}</a> &rsaquo; '
             f'<a href="{loc("services",ar)}">{esc(U["services"])}</a> &rsaquo; '
             f'<a href="{loc("services",ar)}?id={d[0]}">{esc(disc_name)}</a></div>')
    hero = (f'<section class="dcp-hero"><div class="dcp-wrap">{crumb}'
            f'<h1>{esc(h1)}</h1><p class="dcp-lede">{esc(intro)}</p>'
            f'<div class="dcp-chips">{chips}</div></div></section>')
    # methodology band (#4)
    mh, steps = METHOD[lang]
    msteps = "".join(f'<div class="dcp-method-step"><h3>{esc(t)}</h3><p>{esc(p)}</p></div>'
                     for t, p in steps)
    method = (f'<section class="dcp-sec dcp-method"><div class="dcp-wrap">'
              f'<div class="dcp-head"><h2>{esc(mh)}</h2></div>'
              f'<div class="dcp-method-grid">{msteps}</div></div></section>')
    # sibling services in the same discipline
    sibs = [sl for sl, dj in SLUG_DISC.items() if dj == di]
    sib_li = ""
    for sl in sibs:
        sc = copy_of(sl, ar)
        name = sc.get("h1") or sc.get("title") or sl
        cur = ' aria-current="page"' if sl == slug else ''
        sib_li += f'<li><a href="{svc_file(sl,ar)}"{cur}>{esc(name)}</a></li>'
    aside = (f'<aside class="dcp-aside"><div class="box"><h3>{esc(U["in_disc"])}</h3>'
             f'<ul class="siblings">{sib_li}</ul></div>'
             f'<div class="box cta"><h3>{esc(U["get"])}</h3><p>{esc(U["get_p"])}</p>'
             f'<a class="dcp-btn" href="{loc("contact",ar)}">{esc(U["ask"])} {I_ARROW}</a></div></aside>')
    body_sec = (f'<section class="dcp-sec"><div class="dcp-wrap"><div class="dcp-svc-grid">'
                f'<div class="dcp-svc-body">{sections_html(c.get("sections", []))}</div>'
                f'{aside}</div></div></section>')
    ph = SVC_PHOTO.get(slug); photo = ''
    if ph:
        cap = ph[2] if ar else ph[1]
        photo = (f'<section class="dcp-sec"><div class="dcp-wrap"><figure class="dcp-svc-shot">'
                 f'<img src="assets1/images/{ph[0]}" alt="{esc(cap)}" loading="lazy" width="1100" height="700">'
                 f'<figcaption>{esc(cap)}</figcaption></figure></div></section>')
    body = hero + photo + method + body_sec + related_reading(di, ar) + cta_band(ar) + footer(ar)
    # schema: Service + BreadcrumbList
    schema = {"@context": "https://schema.org", "@type": "Service", "name": h1,
              "serviceType": disc_name, "provider": {"@id": SITE + "/#org"},
              "areaServed": ["SA", "AE", "IN"], "description": c.get("desc", intro)[:300]}
    head = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False) + '</script>'
    title = c.get("title") or (h1 + (" | داتاكور للحلول" if ar else " | Datacore Solutions"))
    _loc = ("السعودية", "الرياض") if ar else ("Saudi Arabia", "Riyadh")
    if not any(w in title for w in _loc):   # GEO: every service title should carry a country signal
        _ins = " في السعودية" if ar else " in Saudi Arabia"
        title = title.replace(" | ", _ins + " | ", 1) if " | " in title else title + _ins
    return shell(ar, "services", title, c.get("desc", intro)[:180], body, extra_head=head, canon="service-" + slug)

n = 0
for slug in SLUGS:
    for ar in (False, True):
        open(os.path.join(ROOT, svc_file(slug, ar)), "w", encoding="utf-8").write(build(slug, ar))
        n += 1
print("wrote", n, "service pages")
