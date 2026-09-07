# -*- coding: utf-8 -*-
"""Generate the mirror's 38 service-detail pages (EN+AR = 76 files) in the live
look, from the copy fetched verbatim into services-copy.json. Flat filenames
service-<slug>.html at the mirror root; the overlay rewrites the live
services.html 'service-details/<slug>' links to these at runtime, so the live
pages stay byte-for-byte untouched. Adds the methodology band (design #4)."""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_pages import shell, cta_band, footer, esc, loc, STR, ROOT, I_ARROW

DATA = r"C:\Users\afnan\Documents\Datacore\Datacore Website\datacore-web\src\data"
SVC = json.load(open(os.path.join(DATA, "services-copy.json"), encoding="utf-8"))["services"]
# The live AR service pages are empty shells; the Arabic copy was authored
# separately into services-copy-ar.json. Use that for AR, live copy for EN.
SVC_AR = json.load(open(os.path.join(DATA, "services-copy-ar.json"), encoding="utf-8"))["services"]
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
    body = hero + method + body_sec + cta_band(ar) + footer(ar)
    # schema: Service + BreadcrumbList
    schema = {"@context": "https://schema.org", "@type": "Service", "name": h1,
              "serviceType": disc_name, "provider": {"@type": "Organization", "name": "Datacore Solutions"},
              "areaServed": ["SA", "AE", "IN"], "description": c.get("desc", intro)[:300]}
    head = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False) + '</script>'
    title = c.get("title") or (h1 + (" | داتاكور" if ar else " | Datacore"))
    return shell(ar, "services", title, c.get("desc", intro)[:180], body, extra_head=head)

n = 0
for slug in SLUGS:
    for ar in (False, True):
        open(os.path.join(ROOT, svc_file(slug, ar)), "w", encoding="utf-8").write(build(slug, ar))
        n += 1
print("wrote", n, "service pages")
