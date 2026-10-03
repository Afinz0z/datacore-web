# -*- coding: utf-8 -*-
"""Generate the mirror's Products catalogue (EN+AR) in the live look: faceted
search (category / brand / availability / text) over the 37-item catalogue, plus
a request (RFQ) basket. Reuses the shell/header/footer helpers from build_pages."""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_pages import shell, hero, cta_band, footer, esc, loc, STR, ROOT, I_ARROW, VER, SITE

DATA = os.path.dirname(os.path.abspath(__file__))  # data files bundled in _build/
def _load_products():
    """Products are one file each under content/products/<sku>.json (specs as a
    list of {label,value} for CMS editing). Rebuild the flat list the catalogue
    JS + schema expect (specs back to a dict, original order)."""
    import glob
    d = os.path.dirname(os.path.abspath(__file__))
    items = [json.load(open(f, encoding="utf-8"))
             for f in glob.glob(os.path.join(d, "content", "products", "*.json"))]
    items.sort(key=lambda e: (e.get("order", 9999), str(e.get("sku", ""))))
    out = []
    for e in items:
        prod = {}
        for k, v in e.items():           # preserve original key order + all fields
            if k == "order":
                continue
            prod[k] = {s["label"]: s["value"] for s in v} if k == "specs" else v
        out.append(prod)
    return out
PRODUCTS = _load_products()
GLYPHS = json.load(open(os.path.join(DATA, "glyphs.json"), encoding="utf-8"))

# real product photos live at assets1/images/products/<sku>.<ext>; filenames
# sanitise "/" and spaces. Build sku -> local path (glyph fallback if absent).
_PDIR = os.path.join(ROOT, "assets1", "images", "products")
_PFILES = {os.path.splitext(f)[0]: f for f in os.listdir(_PDIR)} if os.path.isdir(_PDIR) else {}
def _photo(sku):
    for k in (sku, sku.replace('/', '_'), sku.replace(' ', '-'),
              sku.replace('/', '_').replace(' ', '-'), sku.replace(' ', '')):
        if k in _PFILES:
            return "assets1/images/products/" + _PFILES[k]
    return None
PHOTOS = {p["sku"]: _photo(p["sku"]) for p in PRODUCTS if _photo(p["sku"])}

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
   "refine": "Refine", "filters": "Filters", "product_one": "product", "product_many": "products",
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
   "refine": "تصفية", "filters": "المرشحات", "product_one": "منتج", "product_many": "منتجاً",
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


def _jesc(s):
    """The escaping dc-products.js uses (& < > " only), so server and script markup match."""
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def cards_html(ar):
    """The product cards, written into the page so crawlers that don't run JavaScript see the
    catalogue. Mirrors the card template in dc-products.js, which adopts these cards on load."""
    L = LABELS['ar' if ar else 'en']
    cat = CAT_AR if ar else {}
    out = []
    for p in PRODUCTS:
        specs = ''.join(f'<div><dt>{_jesc(k)}</dt><dd dir="ltr">{_jesc(v)}</dd></div>'
                        for k, v in list((p.get('specs') or {}).items())[:4])
        av = (f'<span class="dcp-badge stock">{L["in_stock"]}</span>' if p.get('avail') == 'stock'
              else f'<span class="dcp-badge lead">{L["on_order"]}</span>')
        photo = PHOTOS.get(p['sku'])
        if photo:
            media = f'<div class="dcp-card-photo"><img src="{_jesc(photo)}" alt="{_jesc(p["n"])}" loading="lazy"></div>'
        else:
            glyph = GLYPHS.get(p.get('g')) or GLYPHS.get('rack') or ''
            media = ('<div class="dcp-card-photo dcp-noimg"><span class="dcp-card-ic">'
                     '<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" '
                     'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                     + glyph + '</svg></span></div>')
        out.append(
            f'<article class="dcp-card" data-sku="{_jesc(p["sku"])}">' + media +
            f'<div class="dcp-card-top"><span class="dcp-card-brand" dir="ltr">{_jesc(p["b"])}</span>{av}</div>'
            f'<h3>{_jesc(p["n"])}</h3>'
            f'<div class="dcp-card-meta"><span class="dcp-tag">{_jesc(cat.get(p["c"], p["c"]))}</span></div>'
            f'<dl class="dcp-specs">{specs}</dl>'
            f'<div class="dcp-card-sku" dir="ltr">{_jesc(p["sku"])}</div>'
            '<div class="dcp-add-row"><div class="dcp-qty">'
            '<button class="dcp-qb" type="button" data-q="-1" aria-label="Decrease quantity">−</button>'
            f'<input class="dcp-qn" type="text" inputmode="numeric" value="1" aria-label="Quantity" data-sku="{_jesc(p["sku"])}">'
            '<button class="dcp-qb" type="button" data-q="1" aria-label="Increase quantity">+</button>'
            f'</div><button class="dcp-add" type="button" data-sku="{_jesc(p["sku"])}">{L["add"]}</button></div>'
            '</article>')
    return ''.join(out)

def build_products(ar):
    lang = 'ar' if ar else 'en'
    s = STR[lang]; L = LABELS[lang]
    search_svg = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                  'stroke-width="2.2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>')
    tools = f"""<div class="dcp-cat-shell">
  <aside class="dcp-facets" id="dcp-facets" aria-label="{esc(L['refine'])}"></aside>
  <div class="dcp-cat-main">
    <div class="dcp-searchbar">
      <div class="dcp-search-in">{search_svg}<input id="dcp-search" type="search"
        placeholder="{esc(L['search_ph'])}" autocomplete="off" aria-label="{esc(L['search'])}"></div>
      <button class="dcp-mobfilter" id="dcp-mobfilter" type="button" aria-expanded="false"
        aria-controls="dcp-facets">{esc(L['filters'])}</button>
    </div>
    <div class="dcp-catbar"><span class="dcp-count" id="dcp-count"></span></div>
    <div class="dcp-chips" id="dcp-chips"></div>
    <div class="dcp-grid" id="dcp-grid">{cards_html(ar)}</div>
    <p id="dcp-empty" class="dcp-count" hidden>{esc(L['empty'])}</p>
  </div>
</div>"""

    drawer = f"""<button class="dcp-fab" id="dcp-fab" type="button" hidden><svg class="dcp-fab-ic" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="9" cy="20" r="1.35"/><circle cx="18" cy="20" r="1.35"/><path d="M2.5 3h2.3l2.2 11.4a1.6 1.6 0 0 0 1.6 1.3h8.2a1.6 1.6 0 0 0 1.55-1.2L21.5 7H6.3"/></svg><span class="dcp-fab-t">{esc(L['req_title'])}</span>
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

    data = {"lang": lang, "products": PRODUCTS, "glyphs": GLYPHS, "photos": PHOTOS,
            "catMap": (CAT_AR if ar else {}), "labels": L}
    js = ('<script>window.DCP_DATA=' + json.dumps(data, ensure_ascii=False) + ';</script>'
          '<script src="dc-products.js?v=' + VER + '"></script>')
    title = ('المنتجات | داتاكور للحلول' if ar else 'Products | Datacore Solutions')
    # CollectionPage + ItemList of the real product categories (the cards themselves are in the
    # HTML too, see cards_html). Quote-based B2B — no fabricated prices.
    purl = SITE + "/" + loc("products", ar)
    prodschema = {"@context": "https://schema.org", "@type": "CollectionPage",
        "@id": purl + "#catalog", "url": purl,
        "name": ("المنتجات — أجهزة الشبكات والأمن والصوتيات والبنية التحتية" if ar
                 else "Products — Network, Security, Audio-Visual & Infrastructure Hardware"),
        "description": s['pr_lede'], "isPartOf": {"@id": SITE + "/#website"},
        "about": {"@id": SITE + "/#org"}, "inLanguage": lang,
        "mainEntity": {"@type": "ItemList", "numberOfItems": len(PRODUCTS),
            "name": ("منتجات الكتالوج" if ar else "Catalogue products"),
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": {
                "@type": "Product", "name": p["n"], "sku": p["sku"], "mpn": p["sku"],
                "brand": {"@type": "Brand", "name": p["b"]}, "category": p["c"]}}
                for i, p in enumerate(PRODUCTS)]}}
    # The facet sidebar scrolls (max-height + overflow-y in dc-pages.css). Hide the
    # scrollbar entirely (it read as a divider) while keeping wheel/trackpad scroll,
    # and drop the reserved scrollbar-gutter (set to stable in dc-pages.css) so no
    # empty lane is left behind. Page-scoped, products-only — no VER bump.
    scrollbar_css = ('<style>'
        '.dcp-facets{scrollbar-width:none;-ms-overflow-style:none;scrollbar-gutter:auto}'
        '.dcp-facets::-webkit-scrollbar{width:0;height:0;display:none}'
        '</style>')
    sch = ('<script type="application/ld+json">' + json.dumps(prodschema, ensure_ascii=False)
           + '</script>' + scrollbar_css)
    return shell(ar, 'products', title, s.get('pr_desc', s['pr_lede']), body, extra_head=sch, extra_js=js)

for ar in (False, True):
    name = loc('products', ar)
    open(os.path.join(ROOT, name), "w", encoding="utf-8").write(build_products(ar))
    print("wrote", name)
print("done")
