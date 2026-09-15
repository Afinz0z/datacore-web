# -*- coding: utf-8 -*-
"""Generate the mirror's supporting pages — Terms, Privacy, 404 (EN+AR) — plus
SEO/GEO scaffolding (robots.txt, sitemap.xml, llms.txt). Legal copy is generic
boilerplate for a B2B systems-integrator brochure site; the CR/VAT numbers are
placeholders and it is not legal advice."""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_pages import shell, hero, cta_band, footer, esc, loc, STR, ROOT

BASE = "https://www.datacore.com.sa"  # canonical destination domain

LEGAL = {
 "terms": {
  "en": ("Terms of Service", "The terms on which this website is offered.", [
    ("Using this site", ["This website presents Datacore Solutions' services, products and projects. "
      "The content is for general information and does not by itself form a contract or a binding quotation."]),
    ("Quotations & scope", ["Any pricing, availability or lead time we return in response to an enquiry is "
      "an estimate valid for the period stated in that quotation. A binding scope is set only in a signed "
      "agreement between you and Datacore Solutions."]),
    ("Intellectual property", ["The text, images, logos and layout of this site belong to Datacore Solutions "
      "or its licensors. Manufacturer names and marks belong to their respective owners and are used to "
      "describe the equipment we supply."]),
    ("Liability", ["We take reasonable care over the information here but do not warrant that it is complete "
      "or current. To the extent permitted by law, Datacore Solutions is not liable for decisions taken "
      "solely on the basis of this website."]),
    ("Contact", ["Questions about these terms can be sent through the contact page."]),
  ]),
  "ar": ("شروط الخدمة", "الشروط التي يُقدَّم على أساسها هذا الموقع.", [
    ("استخدام الموقع", ["يعرض هذا الموقع خدمات داتاكور للحلول ومنتجاتها ومشاريعها. المحتوى لغرض المعلومات "
      "العامة ولا يشكّل بذاته عقداً أو عرض سعر ملزماً."]),
    ("عروض الأسعار والنطاق", ["أي سعر أو توفّر أو مدة توريد نوردها رداً على استفسار هو تقدير صالح للمدة "
      "المذكورة في ذلك العرض. ولا يُحدَّد النطاق الملزم إلا في اتفاقية موقّعة بينك وبين داتاكور للحلول."]),
    ("الملكية الفكرية", ["النصوص والصور والشعارات وتصميم هذا الموقع ملك لداتاكور للحلول أو المرخِّصين لها. "
      "أسماء وعلامات الشركات المصنّعة ملك لأصحابها وتُستخدم لوصف الأجهزة التي نوردها."]),
    ("المسؤولية", ["نبذل عناية معقولة في المعلومات الواردة هنا لكننا لا نضمن اكتمالها أو حداثتها. وبالقدر "
      "الذي يسمح به النظام، لا تتحمل داتاكور للحلول مسؤولية القرارات المتخذة بناءً على هذا الموقع وحده."]),
    ("التواصل", ["يمكن إرسال الأسئلة حول هذه الشروط عبر صفحة التواصل."]),
  ]),
 },
 "privacy": {
  "en": ("Privacy Policy", "What we collect through this site and how we use it.", [
    ("What we collect", ["When you send an enquiry or a quotation request, we receive the details you type — "
      "typically your name, company, email, phone and your message. We do not ask for payment or ID details "
      "on this site."]),
    ("How we use it", ["We use those details only to answer your enquiry and to prepare a quotation or a site "
      "survey. We do not sell your data."]),
    ("Analytics & third parties", ["The live pages use Google Tag Manager and a tawk.to chat widget, which set "
      "their own cookies when they load. The office map loads from Google only when you choose to load it."]),
    ("Retention", ["We keep enquiry correspondence for as long as needed to serve the request and to meet our "
      "record-keeping obligations."]),
    ("Your choices", ["You can ask us what we hold about you, or ask us to delete it, through the contact page."]),
  ]),
  "ar": ("سياسة الخصوصية", "ما نجمعه عبر هذا الموقع وكيف نستخدمه.", [
    ("ما نجمعه", ["عند إرسالك استفساراً أو طلب عرض سعر، نستلم البيانات التي تكتبها — عادةً الاسم والشركة والبريد "
      "الإلكتروني ورقم الجوال ورسالتك. ولا نطلب بيانات دفع أو هوية على هذا الموقع."]),
    ("كيف نستخدمها", ["نستخدم هذه البيانات فقط للرد على استفسارك ولإعداد عرض سعر أو زيارة ومسح للموقع. ولا نبيع "
      "بياناتك."]),
    ("التحليلات والأطراف الثالثة", ["تستخدم الصفحات الحية Google Tag Manager وأداة محادثة tawk.to، وتضع كلٌّ منها "
      "ملفات تعريف ارتباط خاصة بها عند تحميلها. وتُحمَّل خريطة المكاتب من جوجل عند اختيارك تحميلها فقط."]),
    ("الاحتفاظ", ["نحتفظ بمراسلات الاستفسار للمدة اللازمة لخدمة الطلب والوفاء بالتزاماتنا في حفظ السجلات."]),
    ("خياراتك", ["يمكنك أن تسألنا عمّا نحتفظ به عنك، أو أن تطلب حذفه، عبر صفحة التواصل."]),
  ]),
 },
}

def build_legal(kind, ar):
    lang = "ar" if ar else "en"
    title, lede, sections = LEGAL[kind][lang]
    ghost = ("TERMS" if kind == "terms" else "PRIVACY") if not ar else ("شروط" if kind == "terms" else "خصوصية")
    body = hero(ar, ghost, title, title, lede)
    def _slug(h):
        out = ''.join(c if c.isalnum() else '-' for c in h.lower())
        while '--' in out:
            out = out.replace('--', '-')
        return out.strip('-') or 'sec'
    toc_label = 'الوصول السريع' if ar else 'Quick access'
    toc = ''.join(f'<li><a href="#{_slug(h)}">{esc(h)}</a></li>' for h, _ in sections)
    inner = ""
    for h, ps in sections:
        inner += (f'<section id="{_slug(h)}"><h2>{esc(h)}</h2>'
                  + "".join("<p>" + esc(p) + "</p>" for p in ps) + "</section>")
    body += (f'<section class="dcp-sec"><div class="dcp-wrap"><div class="dcp-legal">'
             f'<nav class="dcp-toc" aria-label="{esc(toc_label)}"><h2>{esc(toc_label)}</h2><ul>{toc}</ul></nav>'
             f'<div class="dcp-legal-body">{inner}</div>'
             f'</div></div></section>' + cta_band(ar) + footer(ar))
    tt = title + (" | داتاكور للحلول" if ar else " | Datacore Solutions")
    return shell(ar, kind, tt, lede, body)

def build_404(ar):
    lang = "ar" if ar else "en"; s = STR[lang]
    if ar:
        h, p, b1, b2 = ("الصفحة غير موجودة", "يبدو أن هذا الرابط لم يعد موجوداً أو أن العنوان غير صحيح.",
                        "العودة للرئيسية", "تصفّح الخدمات")
    else:
        h, p, b1, b2 = ("Page not found", "That link may have moved, or the address is not quite right.",
                        "Back to home", "Browse services")
    more_h = "صفحات مفيدة" if ar else "Or try a popular page"
    _links = ([("services", "الخدمات"), ("products", "المنتجات"), ("projects", "المشاريع"),
               ("insights", "الأفكار"), ("faq", "الأسئلة الشائعة"), ("contact", "تواصل معنا")] if ar else
              [("services", "Services"), ("products", "Products"), ("projects", "Projects"),
               ("insights", "Insights"), ("faq", "FAQ"), ("contact", "Contact us")])
    link_html = ''.join(f'<a href="{loc(k, ar)}">{esc(lbl)}</a>' for k, lbl in _links)
    body = (f'<section class="dcp-hero" style="min-height:56vh;display:flex;align-items:center">'
            f'<div class="dcp-ghost" aria-hidden="true">404</div>'
            f'<div class="dcp-wrap"><h1>{esc(h)}</h1><p class="dcp-lede">{esc(p)}</p>'
            f'<div style="margin-top:26px;display:flex;gap:12px;flex-wrap:wrap">'
            f'<a class="dcp-btn" href="{loc("index",ar)}">{esc(b1)}</a>'
            f'<a class="dcp-btn-o" href="{loc("services",ar)}">{esc(b2)}</a></div>'
            f'<div style="margin-top:34px"><p style="font-size:.8rem;letter-spacing:.06em;text-transform:uppercase;'
            f'color:var(--dcp-ink3);margin:0 0 12px">{esc(more_h)}</p>'
            f'<div style="display:flex;gap:10px 22px;flex-wrap:wrap;font-weight:600" class="dcp-404links">{link_html}</div>'
            f'</div></div></section>'
            + footer(ar))
    tt = h + (" | داتاكور" if ar else " | Datacore Solutions")
    return shell(ar, "", tt, p, body)

CAREERS = {
 "en": ("Careers", "Build low-current systems that run real buildings.",
   "We hire engineers and technicians across Saudi Arabia, the UAE and India: people who install to "
   "standard, trained by the manufacturers whose systems they deploy.",
   [("Who we look for", ["Network, audio-visual, security, public-address and datacentre specialists, in "
       "both field and design roles.",
       "Manufacturer certifications matter to us because they matter on site, and we back them with our own training."]),
    ("How we work", ["Everything is delivered in-house: survey, design, installation, commissioning and "
       "maintenance. An engineer sees a project through, not just a ticket.",
       "For clients that need it, we place resident engineers on site, managed by us."]),
    ("How to apply", ["Send a CV and a short note on the disciplines you work in to careers@datacore.com.sa, "
       "or reach us through the contact page. We acknowledge every application."])],
   "careers@datacore.com.sa"),
 "ar": ("الوظائف", "ابنِ أنظمة التيار الخفيف التي تُشغّل المباني.",
   "نوظّف مهندسين وفنيين في السعودية والإمارات والهند: أشخاص يركّبون وفق المعايير، ومدرَّبون لدى الشركات "
   "المصنّعة للأنظمة التي ينفّذونها.",
   [("من نبحث عنه", ["اختصاصيو الشبكات والأنظمة السمعية والبصرية والأمن والنداء الآلي ومراكز البيانات، في "
       "أدوار ميدانية وتصميمية.",
       "الشهادات المعتمدة من المصنّعين تهمّنا لأنها تهمّ في الموقع، وندعمها بتدريبنا الخاص."]),
    ("كيف نعمل", ["كل شيء يُنفَّذ داخلياً: المسح والتصميم والتركيب والتشغيل والصيانة. المهندس يرافق المشروع حتى نهايته.",
       "وعند الحاجة، نضع مهندسين مقيمين في الموقع بإدارتنا."]),
    ("كيف تتقدّم", ["أرسل سيرتك الذاتية ونبذة عن التخصصات التي تعمل بها إلى careers@datacore.com.sa، أو تواصل عبر "
       "صفحة التواصل. نؤكّد استلام كل طلب."])],
   "careers@datacore.com.sa"),
}

def build_careers(ar):
    lang = "ar" if ar else "en"
    title, h1, intro, sections, email = CAREERS[lang]
    ghost = "JOIN" if not ar else "الوظائف"
    apply_lbl = "Email careers@datacore.com.sa" if not ar else "راسلنا: careers@datacore.com.sa"
    body = hero(ar, ghost, title, h1, intro,
                f'<div style="margin-top:26px"><a class="dcp-btn" href="mailto:{email}">{esc(apply_lbl)}</a></div>')
    inner = ""
    for hh, ps in sections:
        inner += "<section><h2>" + esc(hh) + "</h2>" + "".join("<p>" + esc(p) + "</p>" for p in ps) + "</section>"
    body += (f'<section class="dcp-sec"><div class="dcp-wrap"><div class="dcp-svc-body" '
             f'style="max-width:760px">{inner}</div></div></section>' + cta_band(ar) + footer(ar))
    tt = title + (" | داتاكور للحلول" if ar else " | Datacore Solutions")
    return shell(ar, "", tt, intro[:180], body)

# ── write pages ──────────────────────────────────────────────────────────
for ar in (False, True):
    for kind in ("terms", "privacy"):
        open(os.path.join(ROOT, loc(kind, ar)), "w", encoding="utf-8").write(build_legal(kind, ar))
    open(os.path.join(ROOT, loc("careers", ar)), "w", encoding="utf-8").write(build_careers(ar))
open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8").write(build_404(False))
open(os.path.join(ROOT, "404-ar.html"), "w", encoding="utf-8").write(build_404(True))
print("wrote legal + careers + 404 pages")

# ── SEO / GEO scaffolding ────────────────────────────────────────────────
SVC = json.load(open(r"C:\Users\afnan\Documents\Datacore\Datacore Website\datacore-web\src\data\services-copy.json",
                     encoding="utf-8"))["services"]
pages = ["index", "about-us", "services", "products", "projects", "insights", "contact", "faq", "glossary", "careers", "terms", "privacy"]
urls = []
for p in pages:
    urls += [p + ".html", p + "-ar.html"]
for slug in SVC:
    urls += ["service-" + slug + ".html", "service-" + slug + "-ar.html"]
for slug in ["owis", "aou-council", "psau", "taqeem", "auditorium"]:
    urls += ["project-" + slug + ".html", "project-" + slug + "-ar.html"]
_INS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "insights.json"), encoding="utf-8"))
for _p in _INS["en"]["posts"]:
    urls += ["insight-" + _p["slug"] + ".html", "insight-" + _p["slug"] + "-ar.html"]
for slug in ["av-solutions-provider-saudi-arabia", "elv-low-current-systems-saudi-arabia",
             "network-solutions-provider-riyadh", "structured-cabling-company-riyadh",
             "av-network-integrator-saudi-arabia"]:
    urls += [slug + ".html", slug + "-ar.html"]

import datetime
LASTMOD = datetime.date.today().isoformat()
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemap.org/schemas/sitemap/0.9">'.replace("www.sitemap.org", "www.sitemaps.org")]
for u in urls:
    sm.append(f"  <url><loc>{BASE}/{u}</loc><lastmod>{LASTMOD}</lastmod><changefreq>monthly</changefreq></url>")
sm.append("</urlset>")
open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm))

# AI answer engines + search crawlers, named explicitly so bots that look for
# their own user-agent (rather than the wildcard) see an unambiguous welcome.
# Being crawlable is the precondition for being cited in AI answers and search.
_AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot",
            "anthropic-ai", "PerplexityBot", "Perplexity-User", "Google-Extended", "Googlebot",
            "Bingbot", "Applebot", "Applebot-Extended", "Amazonbot", "DuckDuckBot", "CCBot",
            "Meta-ExternalAgent", "cohere-ai", "YouBot", "Diffbot"]
robots = ("# Datacore Solutions — all user-agents welcome across the whole site\n"
          "User-agent: *\nAllow: /\n\n"
          "# Named answer-engine / search crawlers are explicitly welcome to read, index and cite this site\n\n"
          + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in _AI_BOTS)
          + f"Sitemap: {BASE}/sitemap.xml\n")
open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(robots)

llms = f"""# Datacore Solutions

> Low-current (ELV) systems integrator operating in Saudi Arabia, the UAE and
> India. In-house delivery — design, supply, installation, commissioning and
> maintenance — across nine disciplines and 38 services. Integrating since 2007.

## At a glance
- Founded 2007; 16+ years integrating low-current systems in the Gulf.
- 150+ engineers and technicians; three offices (Riyadh, Dubai, Kozhikode).
- 1,500+ customers served across Saudi Arabia, the UAE and India.
- Coverage in Saudi Arabia: Riyadh, Jeddah, Dammam / Eastern Province, NEOM and the Red Sea giga-projects.

## What sets Datacore apart
- In-house delivery end to end — survey, design, supply, installation, commissioning and maintenance are all done by Datacore's own engineers, not subcontracted.
- Built to standard — TIA-568 / ISO-IEC 11801 cabling, EN 54 voice evacuation, Saudi Building Code (SBC 801), SIRA and Civil-Defense-aligned security.
- Manufacturer-certified engineers backed by in-house training; SLA-backed maintenance with resident engineers where required.
- Bilingual (Arabic / English) team serving Vision 2030 smart-infrastructure programmes.

## Disciplines
- Network infrastructure — structured cabling, fibre, IT networks, UPS, Wi-Fi, IP telephony
- Datacentre — design & implementation, migration, assessment
- Surveillance & security — access control, CCTV, parking, GRMS
- Meeting rooms — video conferencing, booking, SOC/NOC, acoustics, boardrooms
- Audio-visual — auditoriums, smart classrooms, control systems, professional audio and more
- Signage & video walls — digital signage, indoor/outdoor LED, interactive walls
- Public address & fire alarm — PAVA voice evacuation (EN 54), PAGA, fire alarm, BGM
- IPTV & MATV
- Maintenance & staffing — SLA-backed contracts, resident engineers

## Offices
- Riyadh, Saudi Arabia (head office) — +966 11 512 8888
- Dubai, United Arab Emirates — +971 52 753 6070
- Kozhikode, India — +91 495 350 1154

## Key pages
- {BASE}/services.html — all disciplines and services
- {BASE}/products.html — product catalogue and quotation requests
- {BASE}/projects.html — named project case studies
- {BASE}/faq.html — frequently asked questions
- {BASE}/glossary.html — plain-language definitions of ELV, AV & ICT terms
- {BASE}/contact.html — enquiry form and office locations

## Case studies
- {BASE}/project-owis.html — One World International School, Riyadh — AV, ICT & security for a new campus, one integrator
- {BASE}/project-psau.html — Prince Sattam bin Abdulaziz University, Al-Kharj — campus-wide smart classrooms & auditorium
- {BASE}/project-taqeem.html — TAQEEM (Saudi Authority for Accredited Valuers), Riyadh — HQ-wide AV standardisation
- {BASE}/project-auditorium.html — Arab Open University, Riyadh — auditorium rebuilt around a direct-view LED wall
- {BASE}/project-aou-council.html — Arab Open University, Riyadh — council-chamber AV modernisation

## Insights (articles)
- {BASE}/insight-what-is-a-public-address-system.html — public address vs. voice evacuation (PA/VA) and the EN 54 standards
- {BASE}/insight-impact-of-5g-on-passive-networks.html — how 5G densification drives fibre counts, pathways and containment
- {BASE}/insight-active-vs-passive-network-infrastructure.html — the active/passive split and why the passive layer is the one to get right
- {BASE}/insight-structured-cabling-standards-explained.html — TIA-568, ISO/IEC 11801 and what Cat6A/OM4 actually mean
- {BASE}/insight-single-mode-vs-multimode-fibre.html — choosing OS2 vs OM3/OM4 fibre for backbone and data-centre links
- {BASE}/insight-data-centre-design-essentials.html — power, cooling, containment and DCIM for a Tier-rated build
- {BASE}/insight-designing-cctv-for-coverage.html — how many cameras, placement and coverage planning
- {BASE}/insight-choosing-an-elv-contractor-saudi-arabia.html — what to check before appointing an ELV/low-current contractor in KSA
- {BASE}/insight-voice-evacuation-en54-sbc801.html — EN 54 vs the Saudi Building Code (SBC 801) for voice alarm
- {BASE}/insight-led-video-wall-pixel-pitch.html — pixel pitch, viewing distance and choosing an indoor LED wall
- {BASE}/insight-why-annual-maintenance-contracts-matter.html — what an ELV AMC covers and why it protects uptime

## Location & solution guides
- {BASE}/elv-low-current-systems-saudi-arabia.html — ELV / low-current systems across Saudi Arabia
- {BASE}/av-solutions-provider-saudi-arabia.html — audio-visual solutions provider in Saudi Arabia
- {BASE}/av-network-integrator-saudi-arabia.html — combined AV + network integration in Saudi Arabia
- {BASE}/network-solutions-provider-riyadh.html — network infrastructure solutions in Riyadh
- {BASE}/structured-cabling-company-riyadh.html — structured cabling contractor in Riyadh

## Selected clients
NEOM, Saudi Central Bank (SAMA), King Abdullah Financial District (KAFD), STC, Riyad Bank, SABB, Bank Al Bilad, Mobily, Zain, Ma'aden, Marafiq, Al Tayyar Travels, Mawhiba Foundation, Prince Sattam bin Abdulaziz University, Arab Open University, Ministry of Communications and IT (MCIT), National Housing Company, Almarai, Landmark, Qiddiya.

Datacore Solutions is a registered Saudi company — Commercial Registration (CR) 7002812043, VAT 311206394100003. Head office: Dabbab Complex, Riyadh, Saudi Arabia. Enquiries: sales@datacore.com.sa · +966 11 512 8888.
"""
open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8").write(llms)

# humans.txt — the people/tech behind the site (a small professionalism signal)
humans = f"""/* DATACORE SOLUTIONS */
ELV / AV / ICT systems integrator — Saudi Arabia, UAE & India, since 2007.
Site: {BASE}
Enquiries: sales@datacore.com.sa

/* OFFICES */
Riyadh, Saudi Arabia (head office) — +966 11 512 8888
Dubai, United Arab Emirates — +971 52 753 6070
Kozhikode, India — +91 495 350 1154

/* SITE */
Built with: HTML5, CSS3, progressive enhancement, JSON-LD structured data
Languages: English & Arabic (RTL), self-hosted fonts
Last updated: {LASTMOD}
"""
open(os.path.join(ROOT, "humans.txt"), "w", encoding="utf-8").write(humans)

# security.txt (RFC 9116) — a contact path for anyone reporting a vulnerability
import datetime as _dt
_expires = (_dt.date.today() + _dt.timedelta(days=365)).isoformat() + "T00:00:00.000Z"
security = (f"Contact: mailto:info@datacore.com.sa\n"
            f"Expires: {_expires}\n"
            f"Preferred-Languages: en, ar\n"
            f"Canonical: {BASE}/.well-known/security.txt\n")
os.makedirs(os.path.join(ROOT, ".well-known"), exist_ok=True)
open(os.path.join(ROOT, ".well-known", "security.txt"), "w", encoding="utf-8").write(security)
open(os.path.join(ROOT, "security.txt"), "w", encoding="utf-8").write(security)  # root fallback for scanners that check /

print("wrote sitemap.xml (", len(urls), "urls), robots.txt, llms.txt, humans.txt, security.txt")
