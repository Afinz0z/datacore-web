# -*- coding: utf-8 -*-
"""Generate the mirror's Products catalogue (EN+AR) in the live look: faceted
search (category / brand / availability / text) over the 37-item catalogue, plus
a request (RFQ) basket. Reuses the shell/header/footer helpers from build_pages."""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_pages import shell, hero, cta_band, footer, esc, loc, STR, ROOT, I_ARROW, VER

DATA = r"C:\Users\afnan\Documents\Datacore\Datacore Website\datacore-web\src\data"
PRODUCTS = json.load(open(os.path.join(DATA, "products.json"), encoding="utf-8"))
GLYPHS = json.load(open(os.path.join(DATA, "glyphs.json"), encoding="utf-8"))

CAT_AR = {
  "Access control": "التحكم في الدخول", "Audio visual": "الأنظمة السمعية والبصرية",
  "Networking": "الشبكات", "Power": "الطاقة", "Public address": "النداء الآلي",
  "Structured cabling": "الكابلات المهيكلة", "Surveillance": "المراقبة",
}
LABELS = {
 "en": {
   "search": "Search", "search_ph": "Model, brand or SKU…", "category": "Category",
   "brand": "Brand", "availability": "Availability", "all": "All",
   "in_stock": "In stock", "on_order": "On order",
   "showing": "Showing {n} of {t} products", "reset": "Reset filters",
   "empty": "No products match those filters.",
   "add": "Add to request", "added": "Added \u2713",
   "req_title": "Your request", "remove": "Remove", "clear": "Clear all",
   "r_empty": "Your request is empty. Add products from the catalogue.",
   "r_name": "Your name", "r_co": "Company", "r_mail": "Email", "r_tel": "Phone",
   "r_msg": "Notes (optional)", "r_send": "Request a quotation",
   "ok_h": "Request sent", "ok_p": "Your reference is {ref}. We\u2019ll price {n} item(s) and reply within one working day.",
 },
 "ar": {
   "search": "بحث", "search_ph": "الطراز أو العلامة أو الرمز…", "category": "الفئة",
   "brand": "العلامة التجارية", "availability": "التوفر", "all": "الكل",
   "in_stock": "متوفر", "on_order": "حسب الطلب",
   "showing": "عرض {n} من {t} منتجاً", "reset": "إعادة تعيين",
   "empty": "لا توجد منتجات مطابقة لهذه المرشحات.",
   "add": "أضف إلى الطلب", "added": "أُضيف \u2713",
   "req_title": "طلبك", "remove": "إزالة", "clear": "مسح الكل",
   "r_empty": "طلبك فارغ. أضف منتجات من الكتالوج.",
   "r_name": "الاسم", "r_co": "الشركة", "r_mail": "البريد الإلكتروني", "r_tel": "رقم الجوال",
   "r_msg": "ملاحظات (اختياري)", "r_send": "اطلب عرض سعر",
   "ok_h": "تم إرسال الطلب", "ok_p": "رقمك المرجعي {ref}. سنسعّر {n} عنصراً ونرد خلال يوم عمل واحد.",
 },
}

def opts(values, cur_ar):
    return ''.join(f'<option value="{esc(v)}">{esc(cur_ar.get(v, v) if cur_ar else v)}</option>'
                   for v in values)

def build_products(ar):
    lang = 'ar' if ar else 'en'
    s = STR[lang]; L = LABELS[lang]
    cats = sorted(set(p['c'] for p in PRODUCTS))
    brands = sorted(set(p['b'] for p in PRODUCTS))
    tools = f"""<div class="dcp-tools">
  <div class="fld"><label for="f-search">{esc(L['search'])}</label>
    <input id="f-search" type="search" placeholder="{esc(L['search_ph'])}" autocomplete="off"></div>
  <div class="fld"><label for="f-cat">{esc(L['category'])}</label>
    <select id="f-cat"><option value="">{esc(L['all'])}</option>{opts(cats, CAT_AR if ar else None)}</select></div>
  <div class="fld"><label for="f-brand">{esc(L['brand'])}</label>
    <select id="f-brand"><option value="">{esc(L['all'])}</option>{opts(brands, None)}</select></div>
  <div class="fld"><label for="f-avail">{esc(L['availability'])}</label>
    <select id="f-avail"><option value="">{esc(L['all'])}</option>
      <option value="stock">{esc(L['in_stock'])}</option>
      <option value="lead">{esc(L['on_order'])}</option></select></div>
</div>
<div class="dcp-toolrow"><span class="dcp-count" id="dcp-count"></span>
  <button class="dcp-clearbtn" id="dcp-reset" type="button">{esc(L['reset'])}</button></div>
<div class="dcp-grid" id="dcp-grid"></div>
<p id="dcp-empty" class="dcp-count" hidden>{esc(L['empty'])}</p>"""

    drawer = f"""<button class="dcp-fab" id="dcp-fab" type="button" hidden>{esc(L['req_title'])}
  <span class="dcp-fabn" id="dcp-fabn">0</span></button>
<div class="dcp-scrim" id="dcp-scrim" hidden></div>
<aside class="dcp-drawer" id="dcp-drawer" role="dialog" aria-modal="true" aria-hidden="true" aria-label="{esc(L['req_title'])}">
  <div class="dcp-dhead"><h2>{esc(L['req_title'])}</h2>
    <button class="dcp-dclose" id="dcp-dclose" type="button" aria-label="Close">&times;</button></div>
  <div class="dcp-dbody" id="dcp-dbody">
    <ul id="dcp-rlist"></ul>
    <button class="dcp-clearbtn" id="dcp-clear" type="button">{esc(L['clear'])}</button>
    <form class="dcp-rform" id="dcp-rform" novalidate>
      <div class="dcp-field"><label for="r-name">{esc(L['r_name'])}</label><input id="r-name" required></div>
      <div class="dcp-field"><label for="r-co">{esc(L['r_co'])}</label><input id="r-co"></div>
      <div class="dcp-field"><label for="r-mail">{esc(L['r_mail'])}</label><input id="r-mail" type="email" required></div>
      <div class="dcp-field"><label for="r-tel">{esc(L['r_tel'])}</label><input id="r-tel" type="tel"></div>
      <div class="dcp-field"><label for="r-msg">{esc(L['r_msg'])}</label><textarea id="r-msg" rows="3"></textarea></div>
      <button class="dcp-btn" type="submit">{esc(L['r_send'])} {I_ARROW}</button>
    </form>
  </div>
</aside>"""

    body = (hero(ar, 'GEAR' if not ar else 'منتجات', s['pr_title'], s['pr_title'], s['pr_lede'])
      + f'<section class="dcp-sec"><div class="dcp-wrap">{tools}</div></section>'
      + cta_band(ar) + footer(ar) + drawer)

    data = {"lang": lang, "products": PRODUCTS, "glyphs": GLYPHS,
            "catMap": (CAT_AR if ar else {}), "labels": L}
    js = ('<script>window.DCP_DATA=' + json.dumps(data, ensure_ascii=False) + ';</script>'
          '<script src="dc-products.js?v=' + VER + '"></script>')
    title = ('المنتجات | داتاكور للحلول' if ar else 'Products | Datacore Solutions')
    return shell(ar, 'products', title, s['pr_lede'], body, extra_js=js)

for ar in (False, True):
    name = loc('products', ar)
    open(os.path.join(ROOT, name), "w", encoding="utf-8").write(build_products(ar))
    print("wrote", name)
print("done")
