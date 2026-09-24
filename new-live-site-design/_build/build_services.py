# -*- coding: utf-8 -*-
"""Generate the mirror's 38 service-detail pages (EN+AR = 76 files) in the live
look, from the copy fetched verbatim into services-copy.json. Flat filenames
service-<slug>.html at the mirror root; the overlay rewrites the live
services.html 'service-details/<slug>' links to these at runtime, so the live
pages stay byte-for-byte untouched. Adds the methodology band (design #4)."""
import os, sys, json, html
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_pages import shell, cta_band, footer, esc, loc, STR, ROOT, I_ARROW, SITE, INSIGHTS, FAQ_CSS, wrap_ltr

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
    E = wrap_ltr if ar else esc
    head = "قراءة ذات صلة" if ar else "Related reading"
    links = "".join(
        f'<a class="dcp-dir" href="{loc("insight-"+sl, ar)}">{E(_ITITLE.get(sl,(sl,sl))[1 if ar else 0])} {I_ARROW}</a>'
        for sl in slugs)
    return (f'<section class="dcp-sec alt"><div class="dcp-wrap" style="max-width:820px">'
            f'<div class="dcp-head"><h2>{esc(head)}</h2></div>'
            f'<div style="display:flex;flex-direction:column;gap:13px">{links}</div></div></section>')

# Discipline-level FAQs — accurate: they restate the standards / scope / coverage
# already stated on the pages, no invented facts. Rendered visibly AND as FAQPage
# schema so AI assistants and search can lift the answers. Arabic is first-draft.
DISC_FAQ = [
 [("What cabling standards do you install to?", "We install structured cabling to TIA-568 and ISO/IEC 11801, using Cat6A copper and OM4 fibre, and hand over documented certification test results."),
  ("Do you cover both copper and fibre?", "Yes — structured cabling, fibre-optic backbones, enterprise Wi-Fi, IT networks, UPS and IP telephony, across Saudi Arabia, the UAE and India."),
  ("Do you certify the installation?", "Every link is tested and certified against the relevant standard, with the results provided at handover.")],
 [("Do you design and build data centres from scratch?", "Yes — design, implementation, migration and assessment, covering containment, power, precision cooling and DCIM."),
  ("What Tier level do you build to?", "We prepare Tier III-class data centres, including civil and electrical works, UPS, FM200 suppression, raised floor and cabinets."),
  ("Can you assess an existing data centre?", "Yes — data-centre assessment and recommendations are available as a standalone service.")],
 [("Are your CCTV and access-control systems SIRA-compliant?", "Yes — we design and install to SIRA and Civil Defense requirements in Saudi Arabia."),
  ("Can security systems integrate with our other building systems?", "Yes — our ONVIF-based CCTV and access control integrate with HR, visitor and related systems."),
  ("What access-control credentials do you support?", "Card, PIN, biometric (face and fingerprint) and mobile credentials.")],
 [("Do you support Microsoft Teams Rooms and Zoom Rooms?", "Yes — meeting and board rooms built for Teams Rooms and Zoom Rooms, with BYOD connectivity."),
  ("Can you add room and desk booking?", "Yes — room and desk booking systems, plus control-room (SOC/NOC) design."),
  ("Do you handle acoustics?", "Acoustic treatment is part of our meeting-room and boardroom fit-outs.")],
 [("What AV control platforms do you program?", "We design AV-over-IP systems with Dante audio and programmed control for auditoriums, classrooms and boardrooms."),
  ("Do you cover auditoriums and smart classrooms?", "Yes — auditoriums, smart classrooms, professional audio and simultaneous-interpretation systems, among others."),
  ("Is the control programming done in-house?", "Yes — design, installation, commissioning and control programming are delivered by our own engineers.")],
 [("What LED video walls do you supply?", "Indoor and outdoor fine-pitch LED video walls with content management, plus interactive video walls."),
  ("How do I choose the right pixel pitch?", "Pixel pitch follows the viewing distance and the room; we size it per site (see our LED pixel-pitch guide)."),
  ("Do you provide the content-management system?", "Yes — digital signage with a CMS for scheduling and remote management.")],
 [("Are your voice-evacuation systems EN 54-certified?", "Yes — PAVA voice evacuation to EN 54-16 and EN 54-24, aligned with the Saudi Building Code (SBC 801)."),
  ("Are the systems Civil-Defense approved?", "We design fire-alarm and voice-evacuation systems to Civil Defense requirements in Saudi Arabia."),
  ("Do you cover industrial PAGA?", "Yes — public address and general alarm (PAGA) for industrial sites, plus background-music systems.")],
 [("Where are your IPTV systems used?", "Hospitality, healthcare and campus environments, plus MATV and satellite distribution."),
  ("What is the difference between IPTV and MATV?", "IPTV distributes TV over the IP network and MATV over coax; we supply both and advise on the right fit."),
  ("Can IPTV integrate with digital signage?", "Yes — IPTV and digital signage can share the same screens and management.")],
 [("Do you offer maintenance contracts?", "Yes — SLA-backed annual maintenance contracts (AMCs) with response-time cover and scheduled preventive visits."),
  ("Can you place engineers on our site?", "Yes — resident engineers and IT staffing, managed by Datacore."),
  ("What does an AMC cover?", "Preventive maintenance, priority response, spares management and documentation — scoped to your systems.")],
]
DISC_FAQ_AR = [
 [("ما المعايير التي تُنفّذون بها التمديدات الهيكلية؟", "نُنفّذ التمديدات الهيكلية وفق TIA-568 وISO/IEC 11801، باستخدام نحاس Cat6A وألياف OM4، ونُسلّم نتائج اختبار واعتماد موثّقة."),
  ("هل تغطّون النحاس والألياف معاً؟", "نعم — تمديدات هيكلية وشبكات ألياف رئيسية وواي فاي للمؤسسات وشبكات تقنية المعلومات وأنظمة UPS والهاتف عبر IP، في السعودية والإمارات والهند."),
  ("هل تعتمدون التركيب باختبار؟", "يُختبر كل مسار ويُعتمد وفق المعيار ذي الصلة، مع تسليم النتائج عند التسليم.")],
 [("هل تصمّمون وتبنون مراكز البيانات من الصفر؟", "نعم — تصميم وتنفيذ ونقل وتقييم، شاملاً الاحتواء والطاقة والتبريد الدقيق وأنظمة DCIM."),
  ("ما مستوى الفئة (Tier) الذي تبنون له؟", "نجهّز مراكز بيانات من فئة Tier III، شاملة الأعمال المدنية والكهربائية وأنظمة UPS وإطفاء FM200 والأرضية المرتفعة والخزانات."),
  ("هل يمكنكم تقييم مركز بيانات قائم؟", "نعم — تقييم مراكز البيانات وتقديم التوصيات متاح كخدمة مستقلة.")],
 [("هل أنظمة الكاميرات والتحكم في الدخول لديكم معتمدة من SIRA؟", "نعم — نصمّم ونركّب وفق متطلبات SIRA والدفاع المدني في السعودية."),
  ("هل يمكن دمج الأنظمة الأمنية مع أنظمة المبنى الأخرى؟", "نعم — كاميراتنا القائمة على ONVIF والتحكم في الدخول تتكامل مع أنظمة الموارد البشرية والزوّار والأنظمة ذات الصلة."),
  ("ما وسائل التعريف المدعومة للتحكم في الدخول؟", "البطاقات وأرقام PIN والقياسات الحيوية (الوجه والبصمة) والهاتف المحمول.")],
 [("هل تدعمون Microsoft Teams Rooms وZoom Rooms؟", "نعم — قاعات اجتماعات ومجالس مبنية لـ Teams Rooms وZoom Rooms مع اتصال BYOD."),
  ("هل يمكن إضافة حجز القاعات والمكاتب؟", "نعم — أنظمة حجز القاعات والمكاتب، إضافة إلى تصميم غرف التحكم (SOC/NOC)."),
  ("هل تتعاملون مع المعالجة الصوتية؟", "المعالجة الصوتية جزء من تجهيز قاعات الاجتماعات والمجالس.")],
 [("ما منصّات التحكم السمعي البصري التي تبرمجونها؟", "نصمّم أنظمة AV-over-IP بصوت Dante وتحكّم مبرمج للمسارح والفصول وقاعات المجالس."),
  ("هل تغطّون المسارح والفصول الذكية؟", "نعم — مسارح وفصول ذكية وصوت احترافي وأنظمة ترجمة فورية، من بين غيرها."),
  ("هل تُنفَّذ برمجة التحكم داخلياً؟", "نعم — التصميم والتركيب والتشغيل وبرمجة التحكم يُنفّذها مهندسونا.")],
 [("ما شاشات LED الجدارية التي تورّدونها؟", "شاشات LED جدارية داخلية وخارجية دقيقة الخطوة مع إدارة محتوى، إضافة إلى الجدران التفاعلية."),
  ("كيف أختار خطوة البكسل المناسبة؟", "تتبع خطوة البكسل مسافة المشاهدة والقاعة؛ نحدّدها لكل موقع (انظر دليل خطوة البكسل)."),
  ("هل تقدّمون نظام إدارة المحتوى؟", "نعم — لافتات رقمية مع نظام إدارة محتوى للجدولة والتحكم عن بُعد.")],
 [("هل أنظمة الإخلاء الصوتي لديكم معتمدة وفق EN 54؟", "نعم — إخلاء صوتي PAVA وفق EN 54-16 وEN 54-24، متوافق مع كود البناء السعودي (SBC 801)."),
  ("هل الأنظمة معتمدة من الدفاع المدني؟", "نصمّم أنظمة إنذار الحريق والإخلاء الصوتي وفق متطلبات الدفاع المدني في السعودية."),
  ("هل تغطّون النداء والإنذار الصناعي PAGA؟", "نعم — النداء العام والإنذار (PAGA) للمواقع الصناعية، إضافة إلى أنظمة الموسيقى الخلفية.")],
 [("أين تُستخدم أنظمة IPTV لديكم؟", "في الضيافة والرعاية الصحية والحُرم الجامعية، إضافة إلى توزيع MATV والبث الفضائي."),
  ("ما الفرق بين IPTV وMATV؟", "يوزّع IPTV القنوات عبر شبكة IP بينما يوزّعها MATV عبر الكابل المحوري؛ نورّد الاثنين وننصح بالأنسب."),
  ("هل يتكامل IPTV مع اللافتات الرقمية؟", "نعم — يمكن لـ IPTV واللافتات الرقمية مشاركة الشاشات نفسها وإدارتها.")],
 [("هل تقدّمون عقود صيانة؟", "نعم — عقود صيانة سنوية مدعومة باتفاقية مستوى خدمة، بزمن استجابة وزيارات وقائية مجدولة."),
  ("هل يمكنكم توفير مهندسين في موقعنا؟", "نعم — مهندسون مقيمون وتوفير كوادر تقنية، بإدارة داتاكور."),
  ("ماذا يشمل عقد الصيانة السنوي؟", "الصيانة الوقائية والاستجابة ذات الأولوية وإدارة قطع الغيار والتوثيق — محدّدة حسب أنظمتك.")],
]
def faq_section(di, ar):
    qa = (DISC_FAQ_AR if ar else DISC_FAQ)[di]
    if not qa:
        return ""
    E = wrap_ltr if ar else esc
    head = "أسئلة شائعة" if ar else "Frequently asked"
    items = "".join(
        f'<details class="dcp-faq"><summary>{E(q)}</summary>'
        f'<div class="dcp-faq-a"><p>{E(a)}</p></div></details>' for q, a in qa)
    return (f'<section class="dcp-sec"><div class="dcp-wrap" style="max-width:820px">'
            f'<div class="dcp-head"><h2>{esc(head)}</h2></div>{items}</div></section>')
def faq_schema(di, ar):
    qa = (DISC_FAQ_AR if ar else DISC_FAQ)[di]
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]} if qa else None

DATA = os.path.dirname(os.path.abspath(__file__))  # data files bundled in _build/
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

def sections_html(sec, ar=False):
    E = wrap_ltr if ar else esc
    out = ""
    for s in sec:
        ps = "".join("<p>" + E(p) + "</p>" for p in s.get("ps", []))
        h = E(s.get("h", "")).strip()
        out += "<section>" + (("<h2>" + h + "</h2>") if h else "") + ps + "</section>"
    return out

def build(slug, ar):
    lang = "ar" if ar else "en"
    c = copy_of(slug, ar); di = SLUG_DISC[slug]; d = DISC[di]
    U = UI[lang]; s = STR[lang]
    E = wrap_ltr if ar else esc   # wrap Latin/code runs in Arabic body copy
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
            f'<h1>{E(h1)}</h1><p class="dcp-lede">{E(intro)}</p>'
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
        sib_li += f'<li><a href="{svc_file(sl,ar)}"{cur}>{E(name)}</a></li>'
    aside = (f'<aside class="dcp-aside"><div class="box"><h3>{esc(U["in_disc"])}</h3>'
             f'<ul class="siblings">{sib_li}</ul></div>'
             f'<div class="box cta"><h3>{esc(U["get"])}</h3><p>{esc(U["get_p"])}</p>'
             f'<a class="dcp-btn" href="{loc("contact",ar)}">{esc(U["ask"])} {I_ARROW}</a></div></aside>')
    body_sec = (f'<section class="dcp-sec"><div class="dcp-wrap"><div class="dcp-svc-grid">'
                f'<div class="dcp-svc-body">{sections_html(c.get("sections", []), ar)}</div>'
                f'{aside}</div></div></section>')
    ph = SVC_PHOTO.get(slug); photo = ''
    if ph:
        cap = ph[2] if ar else ph[1]
        photo = (f'<section class="dcp-sec"><div class="dcp-wrap"><figure class="dcp-svc-shot">'
                 f'<img src="assets1/images/{ph[0]}" alt="{esc(cap)}" fetchpriority="high" decoding="async" width="1100" height="700">'
                 f'<figcaption>{esc(cap)}</figcaption></figure></div></section>')
    body = hero + photo + method + body_sec + related_reading(di, ar) + faq_section(di, ar) + cta_band(ar) + footer(ar)
    # schema: Service + BreadcrumbList
    schema = {"@context": "https://schema.org", "@type": "Service", "name": h1,
              "serviceType": disc_name, "provider": {"@id": SITE + "/#org"},
              "areaServed": ["SA", "AE", "IN"], "description": c.get("desc", intro)[:300]}
    _schemas = [schema]
    _fq = faq_schema(di, ar)
    if _fq:
        _schemas.append(_fq)
    head = "".join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>'
                   for x in _schemas) + FAQ_CSS
    title = c.get("title") or (h1 + (" | داتاكور للحلول" if ar else " | Datacore Solutions"))
    _loc = ("السعودية", "الرياض") if ar else ("Saudi Arabia", "Riyadh")
    if not any(w.lower() in title.lower() for w in _loc):   # GEO: every service title carries a country signal (case-insensitive so a lowercase location isn't doubled)
        _ins = " في السعودية" if ar else " in Saudi Arabia"
        title = title.replace(" | ", _ins + " | ", 1) if " | " in title else title + _ins
    return shell(ar, "services", title, c.get("desc", intro)[:180], body, extra_head=head, canon="service-" + slug)

n = 0
for slug in SLUGS:
    for ar in (False, True):
        open(os.path.join(ROOT, svc_file(slug, ar)), "w", encoding="utf-8").write(build(slug, ar))
        n += 1
print("wrote", n, "service pages")
