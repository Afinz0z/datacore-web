# -*- coding: utf-8 -*-
"""Generate the Products catalogue (EN+AR) in the live look: faceted search (category group /
type / brand / text) over the full catalogue, plus a request (RFQ) basket. Reuses the
shell/header/footer helpers from build_pages.

The catalogue is several thousand products, so the page itself carries only the first page of
cards and the starting filters (enough for crawlers and the first paint). Everything else is in
assets1/data/products-data.js, stamped with a hash of its contents, which dc-products.js reads to
filter, search and page through the rest."""
import os, sys, json, hashlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_pages import shell, hero, cta_band, footer, esc, loc, STR, ROOT, I_ARROW, VER, SITE
from product_data import safe_name, load_categories

DATA = os.path.dirname(os.path.abspath(__file__))  # data files bundled in _build/
PAGE = 24                                          # cards per page (first page is in the HTML)
GROUPS, RESOLVE = load_categories()


def _load_products():
    """One file per product under content/products/<sku>.json (written by import_products.py or
    the CMS). Specs stay an ordered list of [label, value]."""
    import glob
    items = [json.load(open(f, encoding="utf-8"))
             for f in glob.glob(os.path.join(DATA, "content", "products", "*.json"))]
    items.sort(key=lambda e: (e.get("order", 999999), str(e.get("sku", ""))))
    out = []
    for e in items:
        cat = RESOLVE(e.get("c"), e.get("dept"))
        out.append({"sku": str(e["sku"]), "n": e.get("n") or str(e["sku"]), "b": e.get("b") or "",
                    "cat": cat, "g": e.get("g") or cat["g"], "avail": e.get("avail") or "lead",
                    "d": e.get("d") or "", "acc": e.get("acc") or [], "for": e.get("for") or [],
                    "specs": [[s["label"], s["value"]] for s in (e.get("specs") or [])
                              if s.get("label") and s.get("value")]})
    return out
GLYPHS = json.load(open(os.path.join(DATA, "glyphs.json"), encoding="utf-8"))

# product photos live at assets1/images/products/<safe_name(sku)>.webp, 600 x 600
_PDIR = os.path.join(ROOT, "assets1", "images", "products")
_PFILES = {}
for _f in (sorted(os.listdir(_PDIR)) if os.path.isdir(_PDIR) else []):
    _k, _ext = os.path.splitext(_f)
    if _k not in _PFILES or _ext.lower() == '.webp':   # prefer the WebP when both exist
        _PFILES[_k] = _f
def _photo(p):
    return _PFILES.get(safe_name(p["sku"]), "")
PHOTO_DIR = "assets1/images/products/"

# Products with a photo come first, each half in catalogue order; photos are added a brand at a
# time, so the first page improves with every batch.
PRODUCTS = sorted(_load_products(), key=lambda p: not _photo(p))
_BY = {p["sku"]: p for p in PRODUCTS}
for _p in PRODUCTS:          # bundle links: supporting products (acc) and the products they fit (for)
    _p["kids"] = [s for s in _p["acc"] if s in _BY]
    _p["fits"] = [s for s in _p["for"] if s in _BY]
for _p in PRODUCTS:          # make the links two-way even if only one side was filled in
    for s in _p["kids"]:
        if _p["sku"] not in _BY[s]["fits"]: _BY[s]["fits"].append(_p["sku"])
    for s in _p["fits"]:
        if _p["sku"] not in _BY[s]["kids"]: _BY[s]["kids"].append(_p["sku"])

LABELS = {
 "en": {
   "search": "Search", "search_ph": "Model, brand or SKU…", "category": "Category", "type": "Type",
   "brand": "Brand", "availability": "Availability", "all": "All",
   "in_stock": "In stock", "on_order": "On order",
   "showing": "Showing {n} of {t} products", "reset": "Reset filters",
   "empty": "No products match those filters.", "more": "Show more",
   "rel_acc": "Supporting products ({n})", "rel_for": "Compatible products ({n})", "rel_chip": "Linked to {n}",
   "refine": "Refine", "filters": "Filters", "product_one": "product", "product_many": "products",
   "add": "Add to request", "added": "Added",
   "req_title": "Your request", "remove": "Remove", "clear": "Clear all",
   "r_empty": "Your request is empty. Add products from the catalogue.",
   "r_name": "Your name", "r_co": "Company", "r_mail": "Email", "r_tel": "Phone",
   "r_msg": "Notes (optional)", "r_send": "Request a quotation",
   "ok_h": "Request sent", "ok_p": "Your reference is {ref}. We’ll price {n} item(s) and reply within one working day.",
 },
 "ar": {
   "search": "بحث", "search_ph": "الطراز أو العلامة أو الرمز…", "category": "الفئة", "type": "النوع",
   "brand": "العلامة التجارية", "availability": "التوفر", "all": "الكل",
   "in_stock": "متوفر", "on_order": "حسب الطلب",
   "showing": "عرض {n} من {t} منتجاً", "reset": "إعادة تعيين",
   "empty": "لا توجد منتجات مطابقة لهذه المرشحات.", "more": "عرض المزيد",
   "rel_acc": "المنتجات الداعمة ({n})", "rel_for": "المنتجات المتوافقة ({n})", "rel_chip": "مرتبط بـ {n}",
   "refine": "تصفية", "filters": "المرشحات", "product_one": "منتج", "product_many": "منتجاً",
   "add": "أضف إلى الطلب", "added": "أُضيف",
   "req_title": "طلبك", "remove": "إزالة", "clear": "مسح الكل",
   "r_empty": "طلبك فارغ. أضف منتجات من الكتالوج.",
   "r_name": "الاسم", "r_co": "الشركة", "r_mail": "البريد الإلكتروني", "r_tel": "رقم الجوال",
   "r_msg": "ملاحظات (اختياري)", "r_send": "اطلب عرض سعر",
   "ok_h": "تم إرسال الطلب", "ok_p": "رقمك المرجعي {ref}. سنسعّر {n} عنصراً ونرد خلال يوم عمل واحد.",
 },
}


def _jesc(s):
    """The escaping dc-products.js uses (& < > " only), so server and script markup match."""
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def card_specs(specs):
    """The specs a card shows: the first four short enough to sit on one line (long feature lists
    stay in the data for search). Same rule as cardSpecs() in dc-products.js."""
    return [s for s in specs if len(s[1]) <= 48][:4]


def rel_html(p, L):
    """Links to the product's bundle: its supporting products and the products it fits. Both open the
    same view (this product with everything linked to it). Same markup as relHTML() in dc-products.js."""
    b = ''
    if p['kids']:
        b += f'<button type="button" class="dcp-more" data-rel="{_jesc(p["sku"])}">{L["rel_acc"].replace("{n}", str(len(p["kids"])))}</button>'
    if p['fits']:
        b += f'<button type="button" class="dcp-more" data-rel="{_jesc(p["sku"])}">{L["rel_for"].replace("{n}", str(len(p["fits"])))}</button>'
    return f'<div class="dcp-card-rel">{b}</div>' if b else ''


def card_html(p, ar):
    """One product card. Mirrors cardHTML() in dc-products.js, which redraws the grid once the
    catalogue data has loaded."""
    L = LABELS['ar' if ar else 'en']
    specs = ''.join(f'<div><dt>{_jesc(k)}</dt><dd dir="ltr">{_jesc(v)}</dd></div>' for k, v in card_specs(p['specs']))
    av = (f'<span class="dcp-badge stock">{L["in_stock"]}</span>' if p['avail'] == 'stock'
          else f'<span class="dcp-badge lead">{L["on_order"]}</span>')
    photo = _photo(p)
    if photo:
        media = (f'<div class="dcp-card-photo"><img src="{PHOTO_DIR}{_jesc(photo)}" alt="{_jesc(p["n"])}" '
                 'width="600" height="600" decoding="async"></div>')
    else:
        glyph = GLYPHS.get(p['g']) or GLYPHS.get('rack') or ''
        media = ('<div class="dcp-card-photo dcp-noimg"><span class="dcp-card-ic">'
                 '<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" '
                 'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                 + glyph + '</svg></span></div>')
    brand = f'<span class="dcp-card-brand" dir="ltr">{_jesc(p["b"])}</span>' if p['b'] else '<span class="dcp-card-brand"></span>'
    return (f'<article class="dcp-card" data-sku="{_jesc(p["sku"])}">' + media +
            f'<div class="dcp-card-top">{brand}{av}</div>'
            f'<h3 dir="auto">{_jesc(p["n"])}</h3>'
            f'<div class="dcp-card-meta"><span class="dcp-tag">{_jesc(p["cat"]["ar" if ar else "en"])}</span></div>'
            f'<dl class="dcp-specs">{specs}</dl>' + rel_html(p, L) +
            f'<div class="dcp-card-sku" dir="ltr">{_jesc(p["sku"])}</div>'
            '<div class="dcp-add-row"><div class="dcp-qty">'
            '<button class="dcp-qb" type="button" data-q="-1" aria-label="Decrease quantity">−</button>'
            f'<input class="dcp-qn" type="text" inputmode="numeric" value="1" aria-label="Quantity" data-sku="{_jesc(p["sku"])}">'
            '<button class="dcp-qb" type="button" data-q="1" aria-label="Increase quantity">+</button>'
            f'</div><button class="dcp-add" type="button" data-sku="{_jesc(p["sku"])}">{L["add"]}</button></div>'
            '</article>')


def _fgroup(title, dim, counts, label, order=None, limit=8):
    """Starting state of one facet group (nothing selected). Mirrors fgroup() in dc-products.js."""
    keys = order if order else sorted(counts, key=lambda k: label(k).lower())
    keys = [k for k in keys if counts.get(k)]
    shown = keys if len(keys) <= limit else keys[:limit]
    h = f'<div class="dcp-fgroup"><h4>{_jesc(title)}</h4>'
    for k in shown:
        h += (f'<label><input type="checkbox" data-dim="{dim}" value="{_jesc(k)}"><span>{_jesc(label(k))}</span>'
              f'<span class="dcp-fc">{counts[k]}</span></label>')
    if len(keys) > len(shown):
        h += f'<button class="dcp-more" type="button" data-more="{dim}">+ {len(keys) - len(shown)}</button>'
    return h + '</div>'


def facets_html(ar):
    L = LABELS['ar' if ar else 'en']; lang = 1 if ar else 0
    grp, cat, brand = {}, {}, {}
    names = {}
    for p in PRODUCTS:
        grp[p['cat']['grp']] = grp.get(p['cat']['grp'], 0) + 1
        ck = p['cat']['en']; names[ck] = p['cat']['ar' if ar else 'en']
        cat[ck] = cat.get(ck, 0) + 1
        if p['b']:
            brand[p['b']] = brand.get(p['b'], 0) + 1
    h = f'<div class="dcp-fhead"><span>{_jesc(L["refine"])}</span></div>'
    h += _fgroup(L['category'], 'grp', grp, lambda k: GROUPS[k][lang], order=list(GROUPS), limit=12)
    h += _fgroup(L['type'], 'cat', cat, lambda k: names[k])
    h += _fgroup(L['brand'], 'brand', brand, lambda k: k)
    return h


def write_data():
    """assets1/data/products-data.js: the whole catalogue in compact arrays, shared by both
    languages. Returns its URL with a content-hash stamp, so a new import is never served stale."""
    groups = [[k, v[0], v[1]] for k, v in GROUPS.items()]
    cats, cidx, brands, bidx = [], {}, [], {}
    rows = []
    idx = {p['sku']: i for i, p in enumerate(PRODUCTS)}
    for p in PRODUCTS:
        c = p['cat']
        key = (c['en'], c['grp'])
        if key not in cidx:
            cidx[key] = len(cats); cats.append([c['en'], c['ar'], c['grp']])
        if p['b'] and p['b'] not in bidx:
            bidx[p['b']] = len(brands); brands.append(p['b'])
        d = p['d']
        if len(d) > 140:
            d = d[:140].rsplit(' ', 1)[0]
        rows.append([p['sku'], p['n'], bidx.get(p['b'], -1), cidx[key], p['g'], _photo(p), p['specs'], d,
                     1 if p['avail'] == 'stock' else 0, [idx[s] for s in p['kids']], [idx[s] for s in p['fits']]])
    body = json.dumps({"groups": groups, "cats": cats, "brands": brands, "p": rows},
                      ensure_ascii=False, separators=(',', ':'))
    js = 'window.DCP_PRODUCTS=' + body + ';\n'
    d = os.path.join(ROOT, 'assets1', 'data')
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'products-data.js'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    print('wrote assets1/data/products-data.js', len(js.encode('utf-8')) // 1024, 'KB,', len(rows), 'products')
    return 'assets1/data/products-data.js?v=' + hashlib.sha1(js.encode('utf-8')).hexdigest()[:10]


def build_products(ar, data_url):
    lang = 'ar' if ar else 'en'
    s = STR[lang]; L = LABELS[lang]
    total = len(PRODUCTS)
    first = PRODUCTS[:PAGE]
    search_svg = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                  'stroke-width="2.2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>')
    count = L['showing'].replace('{n}', f'{len(first):,}').replace('{t}', f'{total:,}')
    tools = f"""<div class="dcp-cat-shell">
  <aside class="dcp-facets" id="dcp-facets" aria-label="{esc(L['refine'])}">{facets_html(ar)}</aside>
  <div class="dcp-cat-main">
    <div class="dcp-searchbar">
      <div class="dcp-search-in">{search_svg}<input id="dcp-search" type="search"
        placeholder="{esc(L['search_ph'])}" autocomplete="off" aria-label="{esc(L['search'])}"></div>
      <button class="dcp-mobfilter" id="dcp-mobfilter" type="button" aria-expanded="false"
        aria-controls="dcp-facets">{esc(L['filters'])}</button>
    </div>
    <div class="dcp-catbar"><span class="dcp-count" id="dcp-count" aria-live="polite">{count}</span></div>
    <div class="dcp-chips" id="dcp-chips"></div>
    <div class="dcp-grid" id="dcp-grid">{''.join(card_html(p, ar) for p in first)}</div>
    <p id="dcp-empty" class="dcp-count" hidden>{esc(L['empty'])}</p>
    <div class="dcp-morewrap"><button class="dcp-btn dcp-btn-o" id="dcp-more" type="button"{'' if total > PAGE else ' hidden'}>{esc(L['more'])}</button></div>
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

    data = {"lang": lang, "labels": L, "glyphs": GLYPHS, "page": PAGE, "photoDir": PHOTO_DIR}
    js = ('<script>window.DCP_DATA=' + json.dumps(data, ensure_ascii=False) + ';</script>'
          f'<script src="{data_url}"></script>'
          '<script src="dc-products.js?v=' + VER + '"></script>')
    title = ('المنتجات | داتاكور للحلول' if ar else 'Products | Datacore Solutions')
    # CollectionPage + ItemList: the full count, and the products on the first page (the rest are
    # in the data file). Quote-based B2B, so no prices.
    purl = SITE + "/" + loc("products", ar)
    prodschema = {"@context": "https://schema.org", "@type": "CollectionPage",
        "@id": purl + "#catalog", "url": purl,
        "name": ("المنتجات: أجهزة الشبكات والأمن والصوتيات والبنية التحتية" if ar
                 else "Products: Network, Security, Audio-Visual & Infrastructure Hardware"),
        "description": s['pr_lede'], "isPartOf": {"@id": SITE + "/#website"},
        "about": {"@id": SITE + "/#org"}, "inLanguage": lang,
        "mainEntity": {"@type": "ItemList", "numberOfItems": total,
            "name": ("منتجات الكتالوج" if ar else "Catalogue products"),
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": dict(
                {"@type": "Product", "name": p["n"], "sku": p["sku"], "mpn": p["sku"],
                 "category": p["cat"]["ar" if ar else "en"]},
                **({"brand": {"@type": "Brand", "name": p["b"]}} if p["b"] else {}))}
                for i, p in enumerate(first)]}}
    # Page-scoped styles, products only (no VER bump needed for these): the facet sidebar scrolls
    # without a visible scrollbar, and the "Show more" button sits centred under the grid.
    page_css = ('<style>'
        '.dcp-facets{scrollbar-width:none;-ms-overflow-style:none;scrollbar-gutter:auto}'
        '.dcp-facets::-webkit-scrollbar{width:0;height:0;display:none}'
        '.dcp-morewrap{display:flex;justify-content:center;margin-top:28px}'
        '.dcp-morewrap .dcp-btn{width:auto;padding:13px 30px}'
        '.dcp-card-rel{display:flex;flex-wrap:wrap;gap:2px 16px}'
        '.dcp-card-rel .dcp-more{padding:0;text-align:start}'
        '</style>')
    sch = ('<script type="application/ld+json">' + json.dumps(prodschema, ensure_ascii=False)
           + '</script>' + page_css)
    return shell(ar, 'products', title, s.get('pr_desc', s['pr_lede']), body, extra_head=sch, extra_js=js)


if __name__ == '__main__':
    url = write_data()
    for ar in (False, True):
        name = loc('products', ar)
        open(os.path.join(ROOT, name), "w", encoding="utf-8").write(build_products(ar, url))
        print("wrote", name)
    print("done")
