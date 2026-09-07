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
    inner = ""
    for h, ps in sections:
        inner += "<section><h2>" + esc(h) + "</h2>" + "".join("<p>" + esc(p) + "</p>" for p in ps) + "</section>"
    body += (f'<section class="dcp-sec"><div class="dcp-wrap"><div class="dcp-svc-body" '
             f'style="max-width:760px">{inner}</div></div></section>' + cta_band(ar) + footer(ar))
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
    body = (f'<section class="dcp-hero" style="min-height:60vh;display:flex;align-items:center">'
            f'<div class="dcp-ghost" aria-hidden="true">404</div>'
            f'<div class="dcp-wrap"><h1>{esc(h)}</h1><p class="dcp-lede">{esc(p)}</p>'
            f'<div style="margin-top:26px;display:flex;gap:12px;flex-wrap:wrap">'
            f'<a class="dcp-btn" href="{loc("index",ar)}">{esc(b1)}</a>'
            f'<a class="dcp-btn-o" href="{loc("services",ar)}">{esc(b2)}</a></div></div></section>'
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
pages = ["index", "about-us", "services", "products", "projects", "insights", "contact", "careers", "terms", "privacy"]
urls = []
for p in pages:
    urls += [p + ".html", p + "-ar.html"]
for slug in SVC:
    urls += ["service-" + slug + ".html", "service-" + slug + "-ar.html"]

sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemap.org/schemas/sitemap/0.9">'.replace("www.sitemap.org", "www.sitemaps.org")]
for u in urls:
    sm.append(f"  <url><loc>{BASE}/{u}</loc><changefreq>monthly</changefreq></url>")
sm.append("</urlset>")
open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm))

robots = ("User-agent: *\nAllow: /\n\n"
          "# AI / answer engines are welcome to read the site summary\n"
          f"Sitemap: {BASE}/sitemap.xml\n")
open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(robots)

llms = f"""# Datacore Solutions

> Low-current (ELV) systems integrator operating in Saudi Arabia, the UAE and
> India. In-house delivery — design, supply, installation, commissioning and
> maintenance — across nine disciplines and 38 services. Integrating since 2007.

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
- {BASE}/contact.html — enquiry form and office locations

Note: company registration (CR) and VAT numbers shown on the site are placeholders.
"""
open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8").write(llms)
print("wrote sitemap.xml (", len(urls), "urls), robots.txt, llms.txt")
