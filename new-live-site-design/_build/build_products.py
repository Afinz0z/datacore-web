# -*- coding: utf-8 -*-
"""Generate the Products catalogue (EN+AR) in the live look: faceted search (category group /
type / brand / text) over the full catalogue, plus a request (RFQ) basket. Reuses the
shell/header/footer helpers from build_pages.

The catalogue is several thousand products, so the page itself carries only the first page of
cards and the starting filters (enough for crawlers and the first paint). Everything else is in
assets1/data/products-data.js, stamped with a hash of its contents, which dc-products.js reads to
filter, search and page through the rest."""
import datetime, itertools, os, re, sys, json, hashlib, urllib.parse
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_pages import shell, hero, cta_band, footer, esc, loc, STR, ROOT, I_ARROW, VER, SITE, meta_desc
from product_data import safe_name, load_categories

DATA = os.path.dirname(os.path.abspath(__file__))  # data files bundled in _build/
PAGE = 60                                          # cards per page (first page is in the HTML); 60 fills rows of 2 to 6
LOW_AFTER = 12                                     # cards below the first rows fetch their photo at low priority
GROUPS, RESOLVE = load_categories()


def _tidy(label, value):
    """Spacing and capitals the way a datasheet prints them; the words and numbers are unchanged."""
    label = " ".join(str(label).split()).strip(" :")
    value = " ".join(str(value).split())
    value = re.sub(r"\s+([,;:)\]])", r"\1", value)
    value = re.sub(r"([(\[])\s+", r"\1", value)
    value = re.sub(r",(?=[^\s\d])", ", ", value)
    return [label[:1].upper() + label[1:], value]


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
                    "src": e.get("src") or "", "checked": e.get("checked") or "", "model": e.get("model") or "",
                    "src_kind": e.get("src_kind") or "maker", "src_name": e.get("src_name") or "",
                    "videos": e.get("videos") or [],
                    "specs": [_tidy(s["label"], s["value"]) for s in (e.get("specs") or [])
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
def _own_photo(p):
    f = _PFILES.get(safe_name(p["sku"]), "")
    return "products/" + f if f else ""

# Licences, support contracts, warranties and software have nothing to photograph: their cards show
# the maker's logo (assets1/images/brands/<brand>.webp, 600 x 600) instead.
_LDIR = os.path.join(ROOT, "assets1", "images", "brands")
_LOGOS = {os.path.splitext(f)[0] for f in (os.listdir(_LDIR) if os.path.isdir(_LDIR) else [])}
LOGO_ALT = {"Tripleplay": "Uniguest"}          # the logo shown when it is the maker's, not the brand's
_SERVICE = re.compile(r'licen[cs]e|subscription|warranty|smart ?net|support contract|care pack', re.I)
# no plain "software": hardware names carry it ("for Zoom Rooms Software"); software has its own filter group
def is_service(p):
    return p["cat"]["grp"] in ("software", "support") or bool(_SERVICE.search(p["n"] + " " + p["cat"]["en"]))
def _photo(p):
    """Image path under assets1/images/: the product's own photo, or its maker's logo for a service."""
    own = _own_photo(p)
    if own or not (p["b"] and is_service(p)):
        return own
    slug = safe_name(p["b"].lower())
    return "brands/" + slug + ".webp" if slug in _LOGOS else ""
def _alt(p):
    return (LOGO_ALT.get(p["b"], p["b"]) + " logo") if _photo(p).startswith("brands/") else p["n"]
PHOTO_DIR = "assets1/images/"

def _variety(items, keys):
    """Deal products out like cards: one from each pile in turn, piled by the first key, and each pile
    dealt the same way by the next key. Any page then mixes kinds and brands instead of opening on
    one category, and a filtered view stays mixed inside the filter."""
    if not keys or len(items) < 2:
        return items
    piles = {}
    for p in items:
        piles.setdefault(keys[0](p), []).append(p)
    dealt = [_variety(pile, keys[1:]) for pile in piles.values()]
    return [p for row in itertools.zip_longest(*dealt) for p in row if p is not None]


# Products with their own photo come first (logos don't count), each half dealt across filter groups,
# then brands inside a group, then categories inside a brand. Brand comes before category so one
# maker with many photos (Crestron) can't fill the first page.
_VARIETY = [lambda p: p["cat"]["grp"], lambda p: p["b"], lambda p: p["cat"]["en"]]
_ALL = _load_products()
PRODUCTS = (_variety([p for p in _ALL if _own_photo(p)], _VARIETY)
            + _variety([p for p in _ALL if not _own_photo(p)], _VARIETY))
_BY = {p["sku"]: p for p in PRODUCTS}
for _p in PRODUCTS:          # bundle links: supporting products (acc) and the products they fit (for)
    _p["kids"] = [s for s in _p["acc"] if s in _BY]
    _p["fits"] = [s for s in _p["for"] if s in _BY]
for _p in PRODUCTS:          # make the links two-way even if only one side was filled in
    for s in _p["kids"]:
        if _p["sku"] not in _BY[s]["fits"]: _BY[s]["fits"].append(_p["sku"])
    for s in _p["fits"]:
        if _p["sku"] not in _BY[s]["kids"]: _BY[s]["kids"].append(_p["sku"])


def _slug(s):
    return re.sub(r'[^a-z0-9]+', '-', str(s).lower()).strip('-')


# A page of its own for each product with a photo or checked specs, enough to be worth a search result:
# product-<brand>-<sku>.html and -ar.html at the site root (every page's links are relative to the root).
PAGES, _taken = {}, set()
for _p in PRODUCTS:
    if _own_photo(_p) or _p["checked"]:
        _stem = "product-" + "-".join(x for x in (_slug(_p["b"]), _slug(_p["sku"])) if x)
        _s, _n = _stem, 2
        while _s in _taken:
            _s = f"{_stem}-{_n}"; _n += 1
        _taken.add(_s); PAGES[_p["sku"]] = _s
def page_url(p, ar):
    return loc(PAGES[p["sku"]], ar) if p["sku"] in PAGES else ""

# Category pages: one per filter group (not "other"), products-<group>.html, the catalogue opened on it.
GROUP_PAGES = [g for g in GROUPS if g != "other" and any(p["cat"]["grp"] == g for p in PRODUCTS)]
def group_url(g, ar):
    return loc("products-" + g, ar) if g in GROUP_PAGES else loc("products", ar)

# 300 px copies of photos and logos for grids on standard screens (make_thumbs.py), used where present
_SMALL = set()
for _sub in ("products", "brands"):
    _d = os.path.join(ROOT, "assets1", "images", _sub, "sm")
    _SMALL |= {_sub + "/" + f for f in (os.listdir(_d) if os.path.isdir(_d) else [])}
def _small(photo):
    return photo.replace("/", "/sm/", 1) if photo in _SMALL else ""
SIZES = "(max-width: 640px) calc(100vw - 72px), (max-width: 900px) 45vw, 300px"
MONTHS = {"en": ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                 "October", "November", "December"],
          "ar": ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر",
                 "أكتوبر", "نوفمبر", "ديسمبر"]}
# Shared spec names (spec_names.json): each maker's label maps to one name per measure, so a comparison
# lines products up row by row. Product pages and the quick view keep the maker's own labels.
_SPEC = json.load(open(os.path.join(DATA, 'spec_names.json'), encoding='utf-8'))['names']
_SPEC_IDX = {}
for _n in _SPEC:
    for _m in _n['match']:
        _SPEC_IDX.setdefault(_m, []).append(_n)
SPEC_ORDER = list(dict.fromkeys(n['key'] for n in _SPEC))
SPEC_LABEL = {n['key']: (n['en'], n['ar']) for n in _SPEC}


def spec_base(label):
    """'Frequency Range (-10 dB)' -> 'frequency range'; 'Power handling, peak' -> 'power handling'."""
    s = re.sub(r'\([^)]*\)', ' ', label.lower())
    s = re.split(r'\s(?:@|at)\s|,', s)[0]
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def spec_key(label, value, grp):
    for n in _SPEC_IDX.get(spec_base(label), []):
        if (not n.get('groups') or grp in n['groups']) and (not n.get('value') or re.search(n['value'], value)):
            k = n['key']
            return 'peak_power' if k in ('power_handling', 'amp_power') and 'peak' in label.lower() else k
    return ''


def fmt_date(iso, ar):
    try:
        d = datetime.date.fromisoformat(iso)
    except ValueError:
        return iso
    return f"{d.day} {MONTHS['ar' if ar else 'en'][d.month - 1]} {d.year}"

LABELS = {
 "en": {
   "search": "Search", "search_ph": "Model, brand or SKU…", "category": "Category", "type": "Type",
   "brand": "Brand", "availability": "Availability", "all": "All",
   "in_stock": "In stock", "on_order": "On order",
   "showing": "Showing {n} of {t} products", "reset": "Reset filters",
   "empty": "No products match those filters.", "more": "Show more",
   "rel_acc": "Supporting products ({n})", "rel_for": "Compatible products ({n})", "rel_chip": "Linked to {n}",
   "all_brands": "All brands ({n})", "all_types": "All types ({n})", "close": "Close",
   "find_brand": "Find a brand", "find_type": "Find a type", "in_cat": "Category", "any_cat": "All categories",
   "clear_sel": "Clear", "picked": "{n} selected", "show_n": "Show {n} products", "pick_n": "{n} listed",
   "no_brand": "No brand matches. Try another letter or category.", "no_type": "No type matches. Try another letter or category.",
   "refine": "Refine", "filters": "Filters", "product_one": "product", "product_many": "products",
   "add": "Add to request", "added": "Added",
   "req_title": "Your request", "remove": "Remove", "clear": "Clear all",
   "r_empty": "Your request is empty. Add products from the catalogue.",
   "r_name": "Your name", "r_co": "Company", "r_mail": "Email", "r_tel": "Phone",
   "r_msg": "Notes (optional)", "r_send": "Request a quotation",
   "ok_h": "Request sent", "ok_p": "Your reference is {ref}. We’ll price {n} item(s) and reply within one working day.",
   "sort": "Sort", "sort_rec": "Recommended", "sort_name": "Name, A to Z", "sort_brand": "Brand, A to Z",
   "cmp": "Compare", "cmp_n": "Compare {n}", "cmp_h": "Compare products", "cmp_max": "You can compare up to 4 products.",
   "cmp_clear": "Clear", "cmp_more": "Show {n} more details", "cmp_less": "Show fewer details", "part": "Part number", "product": "Product", "qty": "Quantity",
   "dec": "Decrease quantity", "inc": "Increase quantity",
   "qv_specs": "Specifications", "qv_checked": "Checked against the maker's page on {d}.",
   "qv_maker": "Maker's product page",
   "qv_dist": "From {n}'s listing of this exact model (a distributor), checked on {d}; not from the maker's own page.",
   "qv_list": "Distributor listing", "videos": "Videos", "play": "Play video",
   "vid_note": "Official videos from the maker. They load from YouTube (youtube-nocookie.com) only when you press play.", "qv_inv": "From Datacore's inventory record, not yet checked against the maker. Ask us for the full datasheet.",
   "qv_page": "Open product page", "qv_link": "Copy link", "copied": "Link copied",
   "qv_acc": "Supporting products", "qv_for": "Works with", "qv_all": "Show all in the catalogue",
   "recent": "Recently viewed", "recent_clear": "Clear", "ac_all": "See all {n} results",
   "share": "Copy a link to this list", "csv": "Download the list (CSV)",
   "shared": "{n} products from a shared list were added to your request.",
   "shared_one": "1 product from a shared list was added to your request.",
   "browse": "Browse by category", "products": "Products", "back": "Back to the catalogue",
   "open_req": "Open your request", "in_req": "In your request.",
 },
 "ar": {
   "search": "بحث", "search_ph": "الطراز أو العلامة أو الرمز…", "category": "الفئة", "type": "النوع",
   "brand": "العلامة التجارية", "availability": "التوفر", "all": "الكل",
   "in_stock": "متوفر", "on_order": "حسب الطلب",
   "showing": "عرض {n} من {t} منتجاً", "reset": "إعادة تعيين",
   "empty": "لا توجد منتجات مطابقة لهذه المرشحات.", "more": "عرض المزيد",
   "rel_acc": "المنتجات الداعمة ({n})", "rel_for": "المنتجات المتوافقة ({n})", "rel_chip": "مرتبط بـ {n}",
   "all_brands": "كل العلامات ({n})", "all_types": "كل الأنواع ({n})", "close": "إغلاق",
   "find_brand": "ابحث عن علامة تجارية", "find_type": "ابحث عن نوع", "in_cat": "الفئة", "any_cat": "كل الفئات",
   "clear_sel": "مسح", "picked": "المحدد: {n}", "show_n": "عرض {n} منتجاً", "pick_n": "{n} في القائمة",
   "no_brand": "لا توجد علامة مطابقة. جرّب حرفاً أو فئة أخرى.", "no_type": "لا يوجد نوع مطابق. جرّب حرفاً أو فئة أخرى.",
   "refine": "تصفية", "filters": "المرشحات", "product_one": "منتج", "product_many": "منتجاً",
   "add": "أضف إلى الطلب", "added": "أُضيف",
   "req_title": "طلبك", "remove": "إزالة", "clear": "مسح الكل",
   "r_empty": "طلبك فارغ. أضف منتجات من الكتالوج.",
   "r_name": "الاسم", "r_co": "الشركة", "r_mail": "البريد الإلكتروني", "r_tel": "رقم الجوال",
   "r_msg": "ملاحظات (اختياري)", "r_send": "اطلب عرض سعر",
   "ok_h": "تم إرسال الطلب", "ok_p": "رقمك المرجعي {ref}. سنسعّر {n} عنصراً ونرد خلال يوم عمل واحد.",
   "sort": "الترتيب", "sort_rec": "المقترح", "sort_name": "الاسم أبجدياً", "sort_brand": "العلامة التجارية أبجدياً",
   "cmp": "مقارنة", "cmp_n": "قارن {n}", "cmp_h": "مقارنة المنتجات", "cmp_max": "يمكنك مقارنة 4 منتجات كحد أقصى.",
   "cmp_clear": "مسح", "cmp_more": "اعرض {n} تفاصيل أخرى", "cmp_less": "اعرض تفاصيل أقل", "part": "رقم القطعة", "product": "المنتج", "qty": "الكمية",
   "dec": "إنقاص الكمية", "inc": "زيادة الكمية",
   "qv_specs": "المواصفات", "qv_checked": "تمت مطابقتها مع صفحة الشركة المصنعة بتاريخ {d}.",
   "qv_maker": "صفحة المنتج لدى الشركة المصنعة",
   "qv_dist": "من قائمة {n} لهذا الطراز نفسه (موزّع)، تمت مراجعتها بتاريخ {d}؛ وليست من صفحة الشركة المصنعة.",
   "qv_list": "صفحة الموزّع", "videos": "مقاطع الفيديو", "play": "تشغيل الفيديو",
   "vid_note": "مقاطع رسمية من الشركة المصنعة. تُحمَّل من YouTube (youtube-nocookie.com) فقط عند الضغط على التشغيل.", "qv_inv": "من سجل المخزون لدى داتاكور، ولم تُطابَق بعد مع الشركة المصنعة. اطلب منا ورقة المواصفات الكاملة.",
   "qv_page": "افتح صفحة المنتج", "qv_link": "انسخ الرابط", "copied": "تم نسخ الرابط",
   "qv_acc": "المنتجات الداعمة", "qv_for": "يعمل مع", "qv_all": "اعرضها كلها في الكتالوج",
   "recent": "شاهدتها مؤخراً", "recent_clear": "مسح", "ac_all": "اعرض كل النتائج ({n})",
   "share": "انسخ رابطاً لهذه القائمة", "csv": "نزّل القائمة (CSV)",
   "shared": "أُضيف {n} منتجاً من قائمة مشتركة إلى طلبك.",
   "shared_one": "أُضيف منتج واحد من قائمة مشتركة إلى طلبك.",
   "browse": "تصفح حسب الفئة", "products": "المنتجات", "back": "العودة إلى الكتالوج",
   "open_req": "افتح طلبك", "in_req": "في طلبك.",
 },
}


def _jesc(s):
    """The escaping dc-products.js uses (& < > " only), so server and script markup match."""
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


MEASURE = re.compile(r'dimension|size|weight|height|width|depth|length|diameter', re.I)


def card_specs(specs):
    """The specs a card shows: the first four short enough to sit on one line (long feature lists
    stay in the data for search), with a measurement (size, weight) in the last place when the product
    has one and the first four don't. The script shows these as they are (row 6 of the data)."""
    short = [s for s in specs if len(s[1]) <= 48]
    out = short[:4]
    if len(out) == 4 and not any(MEASURE.search(s[0]) for s in out):
        m = next((s for s in short[4:] if MEASURE.search(s[0])), None)
        if m:
            out[3] = m
    return out


def card_note(p):
    """A few lines from the product's own description, for cards with fewer than three spec lines."""
    d = p['d']
    if not d or len(card_specs(p['specs'])) >= 3:
        return ''
    if d.lower().startswith(p['n'].lower()):          # a description that opens by repeating the name
        d = d[len(p['n']):].lstrip(' ,.:;-')
    key = lambda s: re.sub(r'[^a-z0-9]+', '', s.lower())
    if len(d) < 12 or key(d) in key(p['n']):           # says nothing the name doesn't
        return ''
    return d if len(d) <= 150 else d[:150].rsplit(' ', 1)[0].rstrip(' ,;:.') + '…'


def specs_block(p, ar):
    """Spec lines and the description note under one divider; nothing at all when there is neither."""
    specs = ''.join(f'<div><dt>{_jesc(k)}</dt><dd dir="ltr">{_jesc(v)}</dd></div>' for k, v in card_specs(p['specs']))
    note = card_note(p)
    return ((f'<dl class="dcp-specs">{specs}</dl>' if specs else '')
            + (f'<p class="dcp-card-d" dir="auto">{_jesc(note)}</p>' if note else ''))


def rel_html(p, L):
    """Links to the product's bundle: its supporting products and the products it fits. Both open the
    same view (this product with everything linked to it). Same markup as relHTML() in dc-products.js."""
    b = ''
    if p['kids']:
        b += f'<button type="button" class="dcp-more" data-rel="{_jesc(p["sku"])}">{L["rel_acc"].replace("{n}", str(len(p["kids"])))}</button>'
    if p['fits']:
        b += f'<button type="button" class="dcp-more" data-rel="{_jesc(p["sku"])}">{L["rel_for"].replace("{n}", str(len(p["fits"])))}</button>'
    return f'<div class="dcp-card-rel">{b}</div>' if b else ''


def img_html(p, i=0, big=False):
    """The product's photo (or maker's logo), with the 300 px copy offered to standard screens.
    Same markup as imgHTML() in dc-products.js."""
    photo = _photo(p)
    sm = '' if big else _small(photo)
    srcset = f' srcset="{PHOTO_DIR}{_jesc(sm)} 300w, {PHOTO_DIR}{_jesc(photo)} 600w" sizes="{SIZES}"' if sm else ''
    return (f'<img src="{PHOTO_DIR}{_jesc(photo)}"{srcset} alt="{_jesc(_alt(p))}" width="600" height="600" '
            'decoding="async"' + (' fetchpriority="low"' if i >= LOW_AFTER else '') + '>')


def qty_html(p, L):
    return ('<div class="dcp-add-row"><div class="dcp-qty">'
            f'<button class="dcp-qb" type="button" data-q="-1" aria-label="{_jesc(L["dec"])}">&minus;</button>'
            f'<input class="dcp-qn" type="text" inputmode="numeric" value="1" aria-label="{_jesc(L["qty"])}" data-sku="{_jesc(p["sku"])}">'
            f'<button class="dcp-qb" type="button" data-q="1" aria-label="{_jesc(L["inc"])}">+</button>'
            f'</div><button class="dcp-add" type="button" data-sku="{_jesc(p["sku"])}">{L["add"]}</button></div>')


def card_html(p, ar, i=0):
    """One product card. Mirrors cardHTML() in dc-products.js, which redraws the grid once the
    catalogue data has loaded. The name links to the product's own page where it has one; a click
    opens the quick view instead, so the catalogue keeps its place."""
    L = LABELS['ar' if ar else 'en']
    av = (f'<span class="dcp-badge stock">{L["in_stock"]}</span>' if p['avail'] == 'stock'
          else f'<span class="dcp-badge lead">{L["on_order"]}</span>')
    photo = _photo(p)
    if photo:
        media = f'<div class="dcp-card-photo">{img_html(p, i)}</div>'
    else:
        glyph = GLYPHS.get(p['g']) or GLYPHS.get('rack') or ''
        media = ('<div class="dcp-card-photo dcp-noimg"><span class="dcp-card-ic">'
                 '<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" '
                 'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                 + glyph + '</svg></span></div>')
    brand = f'<span class="dcp-card-brand" dir="ltr">{_jesc(p["b"])}</span>' if p['b'] else '<span class="dcp-card-brand"></span>'
    url, sku = page_url(p, ar), _jesc(p["sku"])
    name = (f'<a class="dcp-open" href="{url}" data-open="{sku}">{_jesc(p["n"])}</a>' if url else
            f'<button type="button" class="dcp-open" data-open="{sku}">{_jesc(p["n"])}</button>')
    return (f'<article class="dcp-card" data-sku="{sku}">' + media +
            f'<div class="dcp-card-top">{brand}{av}</div>'
            f'<h3 dir="auto">{name}</h3>'
            f'<div class="dcp-card-meta"><span class="dcp-tag">{_jesc(p["cat"]["ar" if ar else "en"])}</span></div>'
            + specs_block(p, ar) + rel_html(p, L) +
            f'<div class="dcp-card-sub"><span class="dcp-card-sku" dir="ltr">{sku}</span>'
            f'<label class="dcp-cmp"><input type="checkbox" data-cmp="{sku}"><span>{L["cmp"]}</span></label></div>'
            + qty_html(p, L) + '</article>')


def _fgroup(title, dim, counts, label, order=None, limit=8, more=''):
    """Starting state of one facet group (nothing selected). Mirrors fgroup() in dc-products.js: brands
    and types list their largest eight and open the rest in the picker window."""
    keys = order if order else sorted(counts, key=lambda k: (-counts[k], label(k).lower()))
    keys = [k for k in keys if counts.get(k)]
    shown = keys if len(keys) <= limit else keys[:limit]
    h = f'<div class="dcp-fgroup"><h4>{_jesc(title)}</h4>'
    for k in shown:
        h += (f'<label><input type="checkbox" data-dim="{dim}" value="{_jesc(k)}"><span>{_jesc(label(k))}</span>'
              f'<span class="dcp-fc">{counts[k]}</span></label>')
    if more and len(keys) > limit:
        h += f'<button class="dcp-more" type="button" data-pick="{dim}">{_jesc(more.replace("{n}", f"{len(keys):,}"))}</button>'
    elif len(keys) > len(shown):
        h += f'<button class="dcp-more" type="button" data-more="{dim}">+ {len(keys) - len(shown)}</button>'
    return h + '</div>'


def facets_html(ar, items=None, on=None):
    L = LABELS['ar' if ar else 'en']; lang = 1 if ar else 0
    grp, cat, brand = {}, {}, {}
    names = {}
    for p in PRODUCTS:
        grp[p['cat']['grp']] = grp.get(p['cat']['grp'], 0) + 1
    grp_all, grp = grp, {}
    for p in (items or PRODUCTS):
        grp[p['cat']['grp']] = grp.get(p['cat']['grp'], 0) + 1
        ck = p['cat']['en']; names[ck] = p['cat']['ar' if ar else 'en']
        cat[ck] = cat.get(ck, 0) + 1
        if p['b']:
            brand[p['b']] = brand.get(p['b'], 0) + 1
    h = f'<div class="dcp-fhead"><span>{_jesc(L["refine"])}</span></div>'
    g = _fgroup(L['category'], 'grp', grp_all, lambda k: GROUPS[k][lang], order=list(GROUPS), limit=12)
    if on:
        g = g.replace(f'data-dim="grp" value="{_jesc(on)}">', f'data-dim="grp" value="{_jesc(on)}" checked>')
    h += g
    h += _fgroup(L['type'], 'cat', cat, lambda k: names[k], more=L['all_types'])
    h += _fgroup(L['brand'], 'brand', brand, lambda k: k, more=L['all_brands'])
    return h


def write_data():
    """The catalogue for the script, shared by both languages, in two files stamped with a hash of their
    contents (a new import is never served stale). products-data.js holds what cards need and loads
    with the page; products-text.js (descriptions, full spec lists, model codes, the maker's page)
    loads once the page has drawn. Returns both URLs."""
    groups = [[k, v[0], v[1]] for k, v in GROUPS.items()]
    cats, cidx, brands, bidx = [], {}, [], {}
    rows, text = [], {"d": [], "s": {}, "src": {}, "m": {}, "k": {}}
    idx = {p['sku']: i for i, p in enumerate(PRODUCTS)}
    for p in PRODUCTS:
        c = p['cat']
        key = (c['en'], c['grp'])
        if key not in cidx:
            cidx[key] = len(cats); cats.append([c['en'], c['ar'], c['grp']])
        if p['b'] and p['b'] not in bidx:
            bidx[p['b']] = len(brands); brands.append(p['b'])
        photo = _photo(p)
        card = card_specs(p['specs'])
        rows.append([p['sku'], p['n'], bidx.get(p['b'], -1), cidx[key], p['g'], photo, card, card_note(p),
                     1 if p['avail'] == 'stock' else 0, [idx[s] for s in p['kids']], [idx[s] for s in p['fits']],
                     PAGES.get(p['sku'], 0), 1 if _small(photo) else 0])
        i = len(rows) - 1
        d = p['d']
        if len(d) > 360:              # enough of the description for search and the quick view
            d = d[:360].rsplit(' ', 1)[0].rstrip(' ,;:') + '…'
        text['d'].append(d)
        if p['specs'] != card:
            text['s'][i] = p['specs']
        if p['src']:
            text['src'][i] = [p['src'], p['checked']] + ([p['src_kind'], p['src_name']] if p['src_kind'] != 'maker' else [])
        if p['model'] and p['model'] not in p['n']:
            text['m'][i] = p['model']
        keys = [spec_key(l, v, p['cat']['grp']) for l, v in p['specs']]
        if any(keys):
            text['k'][i] = keys
    return (_write_js('products-data.js', 'DCP_PRODUCTS', {"groups": groups, "cats": cats, "brands": brands, "p": rows}),
            _write_js('products-text.js', 'DCP_TEXT', text))


def _write_js(name, var, obj):
    js = f'window.{var}=' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + ';\n'
    d = os.path.join(ROOT, 'assets1', 'data')
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name), 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    print(f'wrote assets1/data/{name}', len(js.encode('utf-8')) // 1024, 'KB')
    return f'assets1/data/{name}?v=' + hashlib.sha1(js.encode('utf-8')).hexdigest()[:10]


def _crumbs(ar, items):
    """Breadcrumb in the hero style: Home, then (label, href) pairs; the last one has no link."""
    home = STR['ar' if ar else 'en']['home']
    parts = [f'<a href="{loc("index", ar)}">{esc(home)}</a>']
    parts += [f'<a href="{href}">{esc(label)}</a>' if href else esc(label) for label, href in items]
    return '<div class="dcp-crumb">' + ' &rsaquo; '.join(parts) + '</div>'


def _hero(ar, crumbs, title, lede_html, ghost=True):
    g = f'<div class="dcp-ghost" aria-hidden="true">{"منتجات" if ar else "GEAR"}</div>' if ghost else ''
    return (f'<section class="dcp-hero">{g}<div class="dcp-wrap">{_crumbs(ar, crumbs)}'
            f'<h1 dir="auto">{esc(title)}</h1><p class="dcp-lede">{lede_html}</p></div></section>')


def _words(xs):
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]


def _lower(c):
    return c if c[:2].isupper() else c[:1].lower() + c[1:]       # "IP camera" stays, "Network switch" drops its capital


def group_text(g, items, ar):
    """Lede and meta description of a category page, written from the catalogue itself."""
    lang = 'ar' if ar else 'en'
    name = GROUPS[g][1 if ar else 0]
    brands = [b for b, _ in Counter(p['b'] for p in items if p['b']).most_common()]
    cats = [c for c, _ in Counter(p['cat'][lang] for p in items).most_common(3)]
    n = len(items)
    if ar:
        bl = '، '.join(brands[:4]) + ('، وغيرها' if len(brands) > 4 else '')
        lede = (f'{n:,} منتجاً في فئة {name} من {bl}. أكثر الأنواع هنا: {"، ".join(cats)}. '
                'ابحث بالطراز أو رقم القطعة، أو صفِّ القائمة حسب النوع والعلامة، ثم أضف ما تحتاجه إلى طلب عرض سعر.')
        desc = (f'{name}: {n:,} منتجاً من {"، ".join(brands[:3])} وغيرها، مع الصور والمواصفات وأرقام القطع. '
                'اطلب عرض سعر من داتاكور للحلول في الرياض.')
    else:
        more = len(brands) - 4
        bl = _words(brands[:4] + ([f'{more} other brands'] if more > 1 else brands[4:5]))
        lede = (f'{n:,} products in {name}, from {bl}. Most common types: {_words([_lower(c) for c in cats])}. '
                'Search by model or part number, or narrow the list by type and brand, then add items to a quotation request.')
        desc = (f'{name} from {", ".join(brands[:3])} and more: {n:,} products with photos, specs and part numbers. '
                'Request a quotation from Datacore Solutions in Riyadh.')
    return lede, meta_desc(desc)


def build_products(ar, urls, g=None):
    """The catalogue page, or with g a category page: the same catalogue opened on one filter group,
    with its own heading, introduction, address and first page of cards."""
    data_url, text_url = urls
    lang = 'ar' if ar else 'en'
    s = STR[lang]; L = LABELS[lang]
    items = PRODUCTS if not g else [p for p in PRODUCTS if p['cat']['grp'] == g]
    total = len(items)
    first = items[:PAGE]
    n_by_grp = Counter(p['cat']['grp'] for p in PRODUCTS)
    search_svg = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                  'stroke-width="2.2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>')
    count = L['showing'].replace('{n}', f'{len(first):,}').replace('{t}', f'{total:,}')
    sort = (f'<label class="dcp-sort"><span>{esc(L["sort"])}</span><select id="dcp-sort">'
            f'<option value="">{esc(L["sort_rec"])}</option><option value="name">{esc(L["sort_name"])}</option>'
            f'<option value="brand">{esc(L["sort_brand"])}</option></select></label>')
    browse = (f'<nav class="dcp-browse" aria-labelledby="dcp-browse-h"><h2 id="dcp-browse-h">{esc(L["browse"])}</h2><ul>'
              + ''.join(f'<li><a href="{group_url(k, ar)}"' + (' aria-current="page"' if k == g else '')
                        + f'>{esc(GROUPS[k][1 if ar else 0])}</a><span class="dcp-fc">{n_by_grp[k]:,}</span></li>'
                        for k in GROUP_PAGES)
              + '</ul></nav>')
    tools = f"""<div class="dcp-cat-shell">
  <aside class="dcp-facets" id="dcp-facets" aria-label="{esc(L['refine'])}">{facets_html(ar, items if g else None, g)}</aside>
  <div class="dcp-cat-main">
    <div class="dcp-searchbar">
      <div class="dcp-search-in">{search_svg}<input id="dcp-search" type="search" role="combobox" aria-autocomplete="list"
        aria-expanded="false" aria-controls="dcp-ac" placeholder="{esc(L['search_ph'])}" autocomplete="off" aria-label="{esc(L['search'])}">
        <div class="dcp-ac" id="dcp-ac" role="listbox" aria-label="{esc(L['search'])}" hidden></div></div>
      <button class="dcp-mobfilter" id="dcp-mobfilter" type="button" aria-expanded="false"
        aria-controls="dcp-facets">{esc(L['filters'])}</button>
    </div>
    <div class="dcp-catbar"><span class="dcp-count" id="dcp-count" aria-live="polite">{count}</span>{sort}</div>
    <div class="dcp-chips" id="dcp-chips"></div>
    <div class="dcp-recent" id="dcp-recent" hidden></div>
    <div class="dcp-grid" id="dcp-grid">{''.join(card_html(p, ar, i) for i, p in enumerate(first))}</div>
    <p id="dcp-empty" class="dcp-count" hidden>{esc(L['empty'])}</p>
    <div class="dcp-morewrap"><button class="dcp-btn dcp-btn-o" id="dcp-more" type="button"{'' if total > PAGE else ' hidden'}>{esc(L['more'])}</button></div>
    {browse}
  </div>
</div>"""

    drawer = f"""<button class="dcp-fab" id="dcp-fab" type="button" hidden><svg class="dcp-fab-ic" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="9" cy="20" r="1.35"/><circle cx="18" cy="20" r="1.35"/><path d="M2.5 3h2.3l2.2 11.4a1.6 1.6 0 0 0 1.6 1.3h8.2a1.6 1.6 0 0 0 1.55-1.2L21.5 7H6.3"/></svg><span class="dcp-fab-t">{esc(L['req_title'])}</span>
  <span class="dcp-fabn" id="dcp-fabn">0</span></button>
<div class="dcp-scrim" id="dcp-scrim" hidden></div>
<aside class="dcp-drawer" id="dcp-drawer" role="dialog" aria-modal="true" aria-hidden="true" aria-label="{esc(L['req_title'])}">
  <div class="dcp-dhead"><h2>{esc(L['req_title'])}</h2>
    <button class="dcp-dclose" id="dcp-dclose" type="button" aria-label="{esc(L['close'])}">&times;</button></div>
  <div class="dcp-dbody" id="dcp-dbody">
    <ul id="dcp-rlist"></ul>
    <div class="dcp-rtools" id="dcp-rtools" hidden><button class="dcp-more" id="dcp-share" type="button">{esc(L['share'])}</button>
      <button class="dcp-more" id="dcp-csv" type="button">{esc(L['csv'])}</button>
      <button class="dcp-clearbtn" id="dcp-clear" type="button">{esc(L['clear'])}</button></div>
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

    if g:
        gname = GROUPS[g][1 if ar else 0]
        lede, desc = group_text(g, items, ar)
        top = _hero(ar, [(L['products'], loc('products', ar)), (gname, '')], gname, esc(lede))
        title = f'منتجات {gname} | داتاكور للحلول' if ar else f'{gname} products | Datacore Solutions'
    else:
        top = hero(ar, 'GEAR' if not ar else 'منتجات', s['pr_title'], s['pr_title'], s['pr_lede'])
        desc = s.get('pr_desc', s['pr_lede'])
        title = ('المنتجات | داتاكور للحلول' if ar else 'Products | Datacore Solutions')
    body = (top + f'<section class="dcp-sec"><div class="dcp-wrap">{tools}</div></section>'
            + cta_band(ar) + footer(ar) + drawer)

    data = {"lang": lang, "labels": L, "glyphs": GLYPHS, "page": PAGE, "lowAfter": LOW_AFTER, "photoDir": PHOTO_DIR,
            "logoAlt": LOGO_ALT, "sizes": SIZES, "textUrl": text_url,
            "specNames": [[k, SPEC_LABEL[k][1 if ar else 0]] for k in SPEC_ORDER], "preset": {"grp": [g]} if g else {}}
    js = ('<script>window.DCP_DATA=' + json.dumps(data, ensure_ascii=False) + ';</script>'
          f'<script src="{data_url}"></script>'
          '<script src="dc-products.js?v=' + VER + '"></script>')
    # CollectionPage + ItemList: the full count, and the products on the first page (the rest are
    # in the data file). Quote-based B2B, so no prices.
    purl = SITE + "/" + (loc("products-" + g, ar) if g else loc("products", ar))
    prodschema = {"@context": "https://schema.org", "@type": "CollectionPage",
        "@id": purl + "#catalog", "url": purl,
        "name": (title.split(' | ')[0] if g else
                 "المنتجات: أجهزة الشبكات والأمن والصوتيات والبنية التحتية" if ar
                 else "Products: Network, Security, Audio-Visual & Infrastructure Hardware"),
        "description": desc, "isPartOf": {"@id": SITE + "/#website"},
        "about": {"@id": SITE + "/#org"}, "inLanguage": lang,
        "mainEntity": {"@type": "ItemList", "numberOfItems": total,
            "name": ("منتجات الكتالوج" if ar else "Catalogue products"),
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": dict(
                {"@type": "Product", "name": p["n"], "sku": p["sku"], "mpn": p["model"] or p["sku"],
                 "category": p["cat"]["ar" if ar else "en"]},
                **({"brand": {"@type": "Brand", "name": p["b"]}} if p["b"] else {}),
                **({"url": SITE + "/" + page_url(p, ar)} if p["sku"] in PAGES else {}))}
                for i, p in enumerate(first)]}}
    sch = ('<script type="application/ld+json">' + json.dumps(prodschema, ensure_ascii=False)
           + '</script><style>' + CAT_CSS + '</style>')
    return shell(ar, 'products', title, desc, body, extra_head=sch, extra_js=js,
                 canon=("products-" + g) if g else None)


def _mini(q, ar):
    """A small linked product (photo, name, brand) for related lists on product pages."""
    photo = _photo(q)
    th = (f'<span class="dcp-th"><img src="{PHOTO_DIR}{_jesc(_small(photo) or photo)}" alt="" width="300" height="300" decoding="async"></span>'
          if photo else f'<span class="dcp-th dcp-noimg"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" '
          f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{GLYPHS.get(q["g"]) or GLYPHS.get("rack") or ""}</svg></span>')
    href = page_url(q, ar) or (loc('products', ar) + '?p=' + urllib.parse.quote(q['sku']))
    return (f'<li><a class="dcp-mini" href="{href}">{th}<span class="dcp-mini-t" dir="auto">{_jesc(q["n"])}</span>'
            f'<span class="dcp-mini-b" dir="ltr">{_jesc(q["b"] or q["sku"])}</span></a></li>')


def build_product_page(p, ar):
    """A product's own page: photo, description, specs with their source, the products it works with,
    and the same quantity and request controls as the catalogue (they share the visitor's request)."""
    lang = 'ar' if ar else 'en'; L = LABELS[lang]
    name, cat, sku, grp = p['n'], p['cat'][lang], p['sku'], p['cat']['grp']
    gname = GROUPS[grp][1 if ar else 0]
    stem = PAGES[sku]
    brand_html = f'<bdi>{esc(p["b"])}</bdi>' if p['b'] else ''
    if ar:
        lede = esc(cat) + (f' من {brand_html}' if p['b'] else '') + f'، {esc(L["part"])} <bdi>{esc(sku)}</bdi>'
    else:
        lede = (f'{brand_html} ' if p['b'] else '') + esc(_lower(cat) if p['b'] else cat) + f', {esc(L["part"]).lower()} <bdi>{esc(sku)}</bdi>'
    photo = _photo(p)
    if photo:
        big = img_html(p, 0, big=True).replace(' decoding=', ' fetchpriority="high" decoding=', 1)   # the page's main image
        media = f'<div class="dcp-card-photo">{big}</div>'
    else:
        media = ('<div class="dcp-card-photo dcp-noimg"><span class="dcp-card-ic"><svg viewBox="0 0 24 24" width="48" height="48" '
                 'fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                 + (GLYPHS.get(p['g']) or GLYPHS.get('rack') or '') + '</svg></span></div>')
    av = (f'<span class="dcp-badge stock">{L["in_stock"]}</span>' if p['avail'] == 'stock'
          else f'<span class="dcp-badge lead">{L["on_order"]}</span>')
    brand = f'<span class="dcp-card-brand" dir="ltr">{_jesc(p["b"])}</span>' if p['b'] else '<span class="dcp-card-brand"></span>'
    desc = f'<p class="dcp-pp-desc" dir="auto">{esc(p["d"])}</p>' if p['d'] else ''
    specs = ''.join(f'<div><dt>{_jesc(k)}</dt><dd dir="ltr">{_jesc(v)}</dd></div>' for k, v in p['specs'])
    if p['src'] and p['src_kind'] == 'distributor':
        note = (f'<p class="dcp-pp-src">{esc(L["qv_dist"].replace("{n}", p["src_name"]).replace("{d}", fmt_date(p["checked"], ar)))} '
                f'<a href="{esc(p["src"])}" target="_blank" rel="noopener nofollow">{esc(L["qv_list"])}</a></p>')
    elif p['src']:
        note = (f'<p class="dcp-pp-src">{esc(L["qv_checked"].replace("{d}", fmt_date(p["checked"], ar)))} '
                f'<a href="{esc(p["src"])}" target="_blank" rel="noopener nofollow">{esc(L["qv_maker"])}</a></p>')
    else:
        note = f'<p class="dcp-pp-src">{esc(L["qv_inv"])}</p>' if specs else ''
    rel = ''
    for title, skus in ((L['qv_acc'], p['kids']), (L['qv_for'], p['fits'])):
        if skus:
            rel += (f'<h2>{esc(title)} <span class="dcp-fc">{len(skus)}</span></h2><ul class="dcp-pp-rel">'
                    + ''.join(_mini(_BY[x], ar) for x in skus[:24]) + '</ul>')
            if len(skus) > 24:
                rel += f'<p><a class="dcp-more" href="{loc("products", ar)}?rel={urllib.parse.quote(sku)}">{esc(L["qv_all"])}</a></p>'
    # official videos: a still from our own photo with a play button; YouTube loads only on press
    vids = ''
    if p['videos']:
        poster = (f'<img src="{PHOTO_DIR}{_jesc(_small(photo) or photo)}" alt="" width="300" height="300" decoding="async">'
                  if photo else                     # no photo: the same category icon the page shows above
                  '<svg class="dcp-vid-ic" viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" '
                  'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                  + (GLYPHS.get(p['g']) or GLYPHS.get('rack') or '') + '</svg>')
        vids = (f'<h2>{esc(L["videos"])}</h2><div class="dcp-pp-vids">'
                + ''.join(f'<figure class="dcp-vid"><button type="button"{"" if photo else " class=" + chr(34) + "dcp-vid-noimg" + chr(34)} data-yt="{_jesc(v["id"])}" '
                          f'aria-label="{esc(L["play"])}: {esc(v["title"])}">{poster}<span class="dcp-vid-play" aria-hidden="true"></span>'
                          f'</button><figcaption dir="auto">{esc(v["title"])}</figcaption></figure>' for v in p['videos'][:3])
                + f'</div><p class="dcp-pp-src">{esc(L["vid_note"])}</p>')
    crumbs = [(L['products'], loc('products', ar)), (gname, group_url(grp, ar)), (name, '')]
    body = (_hero(ar, crumbs, name, lede, ghost=False)
            + f'<section class="dcp-sec dcp-pp"><div class="dcp-wrap">'
            f'<div class="dcp-pp-grid"><div class="dcp-pp-media">{media}</div>'
            f'<div class="dcp-pp-info"><div class="dcp-card-top">{brand}{av}</div>{desc}'
            f'<div class="dcp-pp-buy" data-pp="{_jesc(sku)}">{qty_html(p, L)}'
            f'<p class="dcp-pp-req" id="dcp-pp-req" hidden>{esc(L["in_req"])} <a href="{loc("products", ar)}?req=1">{esc(L["open_req"])}</a></p></div>'
            + (f'<h2>{esc(L["qv_specs"])}</h2><dl class="dcp-pp-specs">{specs}</dl>{note}' if specs else '')
            + '</div></div>' + vids + rel
            + f'<p class="dcp-pp-back"><a href="{group_url(grp, ar)}">{esc(L["back"])}</a></p></div></section>'
            + cta_band(ar) + footer(ar))
    url = SITE + '/' + loc(stem, ar)
    prod = {"@context": "https://schema.org", "@type": "Product", "@id": url + "#product", "url": url,
            "name": name, "sku": sku, "mpn": p["model"] or sku, "category": cat}
    if p['b']:
        prod["brand"] = {"@type": "Brand", "name": p["b"]}
    if p['d']:
        prod["description"] = p['d']
    if _own_photo(p):
        prod["image"] = SITE + "/" + PHOTO_DIR + _own_photo(p)
    if p['specs']:
        prod["additionalProperty"] = [{"@type": "PropertyValue", "name": k, "value": v} for k, v in p['specs']]
    link = lambda x: dict({"@type": "Product", "name": _BY[x]["n"], "sku": x},
                          **({"url": SITE + "/" + page_url(_BY[x], ar)} if x in PAGES else {}))
    if p['kids']:
        prod["isRelatedTo"] = [link(x) for x in p['kids'][:10]]
    if p['fits']:
        prod["isAccessoryOrSparePartFor"] = [link(x) for x in p['fits'][:10]]
    who = f'{p["b"]} {sku}' if p['b'] else sku
    if ar:
        d = f'{name} ({who})، {cat}. المواصفات والصور والمنتجات المرتبطة. اطلب عرض سعر من داتاكور للحلول في الرياض.'
        title = f'{name} | داتاكور'
    else:
        d = f'{name} ({who}), {cat}. Specifications, photos and related products. Request a quotation from Datacore Solutions in Riyadh.'
        title = f'{name}' + (f' | {p["b"]}' if p['b'] and p['b'].lower() not in name.lower() else '') + ' | Datacore'
    # the request lives in the visitor's browser (same key as the catalogue), so a product page can add to it
    script = ('<script>(function(){var K="dcp-rfq2",b={};try{b=JSON.parse(localStorage.getItem(K))||{};}catch(e){}'
              'if(Array.isArray(b)){var o={};b.forEach(function(s){o[s]=1;});b=o;}'
              'var row=document.querySelector("[data-pp]");if(!row)return;var sku=row.getAttribute("data-pp"),'
              'inp=row.querySelector(".dcp-qn"),btn=row.querySelector(".dcp-add"),go=document.getElementById("dcp-pp-req");'
              'var A=' + json.dumps(L['add'], ensure_ascii=False) + ',AD=' + json.dumps(L['added'], ensure_ascii=False) + ';'
              'function save(){try{localStorage.setItem(K,JSON.stringify(b));}catch(e){}}'
              'function sync(){var on=b[sku]>0;btn.textContent=on?AD:A;btn.classList.toggle("on",on);if(on)inp.value=b[sku];go.hidden=!on;}'
              'row.addEventListener("click",function(e){var q=e.target.closest(".dcp-qb");'
              'if(q){inp.value=Math.max(1,(parseInt(inp.value,10)||1)+(+q.getAttribute("data-q")));if(b[sku]>0){b[sku]=+inp.value;save();}return;}'
              'if(e.target.closest(".dcp-add")){if(b[sku]>0)delete b[sku];else b[sku]=Math.max(1,parseInt(inp.value,10)||1);save();sync();}});'
              'inp.addEventListener("change",function(){inp.value=Math.max(1,parseInt(inp.value,10)||1);if(b[sku]>0){b[sku]=+inp.value;save();}});'
              'try{var S="dcp-seen",v=JSON.parse(localStorage.getItem(S))||[];v=[sku].concat(v.filter(function(x){return x!==sku;})).slice(0,12);'
              'localStorage.setItem(S,JSON.stringify(v));}catch(e){}sync();'
              'document.addEventListener("click",function(e){var b=e.target.closest("[data-yt]");if(!b)return;'
              'var f=document.createElement("iframe");f.src="https://www.youtube-nocookie.com/embed/"+encodeURIComponent(b.getAttribute("data-yt"))+"?autoplay=1&rel=0";'
              'f.title=b.getAttribute("aria-label");f.allow="autoplay; encrypted-media; picture-in-picture";f.allowFullscreen=true;'
              'f.className="dcp-vid-frame";b.replaceWith(f);});})();</script>')
    head = ('<script type="application/ld+json">' + json.dumps(prod, ensure_ascii=False) + '</script>'
            '<style>' + PP_CSS + '</style>')
    return shell(ar, 'products', title, meta_desc(d), body, extra_head=head, extra_js=script, canon=stem)


# Page-scoped styles (no VER bump needed for these). Fixed overlays live in <body>, outside the
# dark-mode filter, so they take the page tokens directly.
MINI_CSS = (
    '.dcp-th{flex:none;width:56px;height:56px;border:1px solid var(--dcp-line);border-radius:4px;background:#fff;'
    'display:flex;align-items:center;justify-content:center;overflow:hidden;color:var(--dcp-ink3)}'
    '.dcp-th img{width:100%;height:100%;object-fit:contain}'
    '.dcp-mini{display:grid;grid-template-columns:56px minmax(0,1fr);grid-template-rows:auto auto;column-gap:12px;'
    'align-items:center;text-align:start;width:100%;padding:8px;border:1px solid var(--dcp-line);border-radius:6px;'
    'background:var(--dcp-bg);color:var(--dcp-ink);font:inherit;cursor:pointer;text-decoration:none}'
    '.dcp-mini .dcp-th{grid-row:1/3}'
    '.dcp-mini:hover{border-color:var(--dcp-teal-d)}'
    '.dcp-mini-t{font-size:.86rem;font-weight:600;line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;'
    '-webkit-box-orient:vertical;overflow:hidden;align-self:end}'
    '.dcp-mini-b{font-size:.76rem;color:var(--dcp-ink3);align-self:start}'
    '.dcp-mini:focus-visible{outline:2px solid var(--dcp-teal-d);outline-offset:2px}')

PP_CSS = MINI_CSS + (
    '.dcp-sec.dcp-pp{padding-top:44px}'
    '.dcp-pp-grid{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:clamp(24px,4vw,56px);align-items:start}'
    '.dcp-pp-media{position:sticky;top:96px}'
    '.dcp-pp-media .dcp-card-photo{aspect-ratio:1;border:1px solid var(--dcp-line);border-radius:6px;padding:24px;background:#fff}'
    '.dcp-pp-desc{color:var(--dcp-ink2);max-width:62ch;margin:14px 0 20px;line-height:1.6}'
    '.dcp-pp-buy{max-width:440px;margin-top:18px}'
    '.dcp-pp-req{margin-top:10px;font-size:.9rem;color:var(--dcp-ink2)}'
    '.dcp-pp-req a,.dcp-pp-back a,.dcp-pp-src a{color:var(--dcp-teal-d);font-weight:600}'
    '.dcp-pp h2{font-size:1.2rem;font-weight:700;margin:40px 0 12px;color:var(--dcp-ink)}'
    '.dcp-pp-specs{margin:0;border-top:1px solid var(--dcp-line)}'
    '.dcp-pp-specs>div{display:grid;grid-template-columns:minmax(120px,2fr) 3fr;gap:16px;padding:10px 0;border-bottom:1px solid var(--dcp-line)}'
    '.dcp-pp-specs dt{color:var(--dcp-ink2);font-size:.92rem}'
    '.dcp-pp-specs dd{margin:0;font-size:.92rem;overflow-wrap:anywhere}'
    '.dcp-pp-src{font-size:.85rem;color:var(--dcp-ink3);margin-top:12px}'
    '.dcp-pp-rel{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px}'
    '.dcp-pp-back{margin-top:40px}'
    '.dcp-pp-vids{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}'
    '.dcp-vid{margin:0}'
    '.dcp-vid button{position:relative;display:block;width:100%;aspect-ratio:16/9;border:1px solid var(--dcp-line);border-radius:6px;'
    'background:#fff;cursor:pointer;padding:0;overflow:hidden}'
    '.dcp-vid button img{width:100%;height:100%;object-fit:contain;opacity:.55}'
    '.dcp-vid button.dcp-vid-noimg{background:var(--dcp-soft)}'
    'html.dc-dark .dcp-vid button:not(.dcp-vid-noimg){background:#f2f4f5}'
    '.dcp-vid-ic{position:absolute;top:14px;inset-inline-start:14px;color:var(--dcp-ink2)}'
    '.dcp-vid-play{position:absolute;inset:0;margin:auto;width:64px;height:64px;border-radius:50%;background:#00776f}'
    '.dcp-vid-play:after{content:"";position:absolute;top:50%;left:54%;transform:translate(-50%,-50%);border-style:solid;'
    'border-width:12px 0 12px 20px;border-color:transparent transparent transparent #fff}'
    '.dcp-vid button:hover .dcp-vid-play,.dcp-vid button:focus-visible .dcp-vid-play{background:#005a54}'
    '.dcp-vid button:focus-visible{outline:2px solid var(--dcp-teal-d);outline-offset:2px}'
    '.dcp-vid figcaption{font-size:.86rem;color:var(--dcp-ink2);margin-top:8px;line-height:1.4}'
    '.dcp-vid-frame{width:100%;aspect-ratio:16/9;border:0;border-radius:6px;display:block}'
    '@media(max-width:820px){.dcp-pp-grid{grid-template-columns:1fr}.dcp-pp-media{position:static;max-width:420px}}')

CAT_CSS = (
    '.dcp-facets{scrollbar-width:none;-ms-overflow-style:none;scrollbar-gutter:auto}'
    '.dcp-facets::-webkit-scrollbar{width:0;height:0;display:none}'
    '.dcp-morewrap{display:flex;justify-content:center;margin-top:28px}'
    '.dcp-morewrap .dcp-btn{width:auto;padding:13px 30px}'
    '.dcp-card-rel{display:flex;flex-wrap:wrap;gap:2px 16px}'
    '.dcp-card-rel .dcp-more{padding:0;text-align:start}'
    + '.dcp-facets{scrollbar-width:none;-ms-overflow-style:none;scrollbar-gutter:auto}.dcp-facets::-webkit-scrollbar{width:0;height:0;display:none}.dcp-morewrap{display:flex;justify-content:center;margin-top:28px}.dcp-morewrap .dcp-btn{width:auto;padding:13px 30px}.dcp-card-rel{display:flex;flex-wrap:wrap;gap:2px 16px}.dcp-card-rel .dcp-more{padding:0;text-align:start}html.dcp-pick-open{overflow:hidden}.dcp-pick{position:fixed;inset:0;z-index:100000;display:flex;align-items:center;justify-content:center;padding:24px}.dcp-pick[hidden]{display:none}.dcp-pick-bg{position:absolute;inset:0;background:rgba(10,12,14,.55)}.dcp-pick-box{position:relative;display:flex;flex-direction:column;width:min(1440px,100%);max-height:calc(100dvh - 48px);background:var(--dcp-bg);color:var(--dcp-ink);border:1px solid var(--dcp-line);border-radius:6px;box-shadow:0 30px 80px -24px rgba(0,0,0,.45);overflow:hidden}.dcp-pick-head{display:flex;align-items:baseline;gap:12px;padding:26px 36px 4px}.dcp-pick-head h2{margin:0;font-size:1.35rem;font-weight:700;color:var(--dcp-ink)}.dcp-pick-n{color:var(--dcp-ink3);font-size:.85rem;font-variant-numeric:tabular-nums}.dcp-pick-x{margin-inline-start:auto;align-self:center;background:none;border:0;font-size:1.75rem;line-height:1;color:var(--dcp-ink2);cursor:pointer;padding:0 4px}.dcp-pick-tools{display:flex;flex-wrap:wrap;gap:10px 20px;align-items:center;padding:18px 36px 0}.dcp-pick-tools .dcp-search-in{flex:1 1 260px;min-width:0}.dcp-pick-sel{display:flex;align-items:center;gap:8px;font-size:.85rem;color:var(--dcp-ink2)}.dcp-pick-sel select{font:inherit;font-size:.9rem;color:var(--dcp-ink);background:var(--dcp-bg);border:1px solid var(--dcp-line);border-radius:3px;padding:10px 12px;max-width:260px;cursor:pointer}.dcp-pick-az{display:flex;flex-wrap:wrap;gap:6px;padding:18px 36px;border-bottom:1px solid var(--dcp-line)}.dcp-pick-az button{min-width:29px;height:32px;padding:0 7px;border:1px solid var(--dcp-line);border-radius:3px;background:var(--dcp-bg);font:inherit;font-size:.82rem;font-weight:600;color:var(--dcp-ink2);cursor:pointer}.dcp-pick-az button:hover{border-color:var(--dcp-teal-d);color:var(--dcp-teal-d)}.dcp-pick-az button[aria-pressed=true]{background:#00776f;border-color:#00776f;color:#fff}html.dc-dark .dcp-pick-az button[aria-pressed=true]{background:#0c8074;border-color:#0c8074}.dcp-pick-list{flex:1;min-height:220px;overflow-y:auto;padding:20px 36px 28px;columns:5 210px;column-gap:64px}.dcp-pick-list h3:first-child{margin-top:0}.dcp-pick-list h3{margin:24px 0 8px;padding-bottom:6px;border-bottom:1px solid var(--dcp-line);font-size:.8rem;font-weight:700;color:var(--dcp-teal-d);break-after:avoid}.dcp-pick-list label{display:flex;align-items:center;gap:11px;padding:7px 0;font-size:.92rem;cursor:pointer;break-inside:avoid}.dcp-pick-list label.off{opacity:.4}.dcp-pick-list label>span:first-of-type{min-width:0;overflow-wrap:anywhere}.dcp-pick-list input{accent-color:var(--dcp-teal-d);width:15px;height:15px;flex:none;margin:0}@media(min-width:641px){.dcp-pick-box:has(.dcp-pick-list){height:min(980px,calc(100dvh - 48px))}}.dcp-pick-none{column-span:all;color:var(--dcp-ink2);padding:28px 0}.dcp-pick-foot{display:flex;align-items:center;gap:16px;padding:16px 36px;border-top:1px solid var(--dcp-line);background:var(--dcp-soft)}.dcp-pick-sum{color:var(--dcp-ink2);font-size:.88rem}.dcp .dcp-pick-foot .dcp-btn{width:auto;margin-inline-start:auto;padding:12px 26px}.dcp-pick-x:focus-visible,.dcp-pick-az button:focus-visible,.dcp-pick-sel select:focus-visible{outline:2px solid var(--dcp-teal-d);outline-offset:2px}@media(max-width:640px){.dcp-pick{padding:0}.dcp-pick-box{max-height:100dvh;height:100dvh;border-radius:0;border:0}.dcp-pick-head,.dcp-pick-tools,.dcp-pick-az,.dcp-pick-list,.dcp-pick-foot{padding-inline:16px}.dcp-pick-list{columns:2 140px;column-gap:20px}.dcp-pick-sel{flex:1 1 100%}.dcp-pick-sel select{flex:1;max-width:none}.dcp-pick-az{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none}.dcp-pick-az::-webkit-scrollbar{display:none}.dcp-pick-az button{flex:none}.dcp-pick-head{padding-top:16px}}' + MINI_CSS +
    # card: the name opens the quick view; compare sits beside the part number
    '.dcp .dcp-open{all:unset;cursor:pointer;color:inherit;font:inherit}'
    '.dcp .dcp-open:hover{color:var(--dcp-teal-d);text-decoration:underline;text-underline-offset:3px}'
    '.dcp-open:focus-visible{outline:2px solid var(--dcp-teal-d);outline-offset:2px;border-radius:2px}'
    '.dcp-card-photo{cursor:zoom-in}'
    '.dcp-card-sub{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:auto}'
    '.dcp-card .dcp-add-row{margin-top:0}'
    '.dcp-card-d{margin:0;font-size:.85rem;line-height:1.5;color:var(--dcp-ink2);border-top:1px solid var(--dcp-line);padding-top:12px;'
    'display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden;overflow-wrap:anywhere}'
    '.dcp-specs+.dcp-card-d{border-top:0;padding-top:0}'
    # the request button: in the sidebar on desktop (it never covers a card), floating on phones
    '#dcp-reqslot{position:sticky;top:0;z-index:2;background:var(--dcp-bg);padding-bottom:14px}'
    '#dcp-reqslot:empty{display:none}'
    '.dcp-reqbtn{display:flex;align-items:center;gap:10px;width:100%;padding:12px 14px;border:0;border-radius:6px;'
    'background:var(--dcp-teal-d);color:#fff;font:inherit;font-weight:600;cursor:pointer;text-align:start}'
    '.dcp-reqbtn:hover{background:var(--dcp-teal-dd)}'
    'html.dc-dark .dcp-reqbtn{background:#0c8074}'
    '.dcp-reqbtn .dcp-fabn{margin-inline-start:auto}'
    '.dcp-reqbtn:focus-visible{outline:2px solid var(--dcp-teal-d);outline-offset:2px}'
    '@media(min-width:901px){.dcp-fab{display:none!important}}'
    '@media(max-width:900px){#dcp-reqslot{display:none}}'
    '@media(max-width:600px){.dcp-fab{padding:14px}.dcp-fab-t{position:absolute;width:1px;height:1px;overflow:hidden;'
    'clip:rect(0 0 0 0);white-space:nowrap}}'
    '.dcp-cmp{display:inline-flex;align-items:center;gap:6px;font-size:.78rem;color:var(--dcp-ink2);cursor:pointer;flex:none}'
    '.dcp-cmp input{accent-color:var(--dcp-teal-d);width:14px;height:14px;margin:0}'
    # sort, recently viewed, suggestions
    '.dcp-catbar{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}'
    '.dcp-sort{display:inline-flex;align-items:center;gap:8px;font-size:.85rem;color:var(--dcp-ink2)}'
    '.dcp-sort select{font:inherit;font-size:.88rem;color:var(--dcp-ink);background:var(--dcp-bg);border:1px solid var(--dcp-line);'
    'border-radius:4px;padding:8px 10px;cursor:pointer}'
    '.dcp-recent{margin-bottom:22px}'
    '.dcp-recent-head{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin-bottom:10px}'
    '.dcp-recent-head h2{font-size:.95rem;font-weight:700;margin:0;color:var(--dcp-ink)}'
    '.dcp-recent-row{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(210px,240px);gap:10px;overflow-x:auto;'
    'padding-bottom:6px;scrollbar-width:thin}'
    '.dcp-search-in{position:relative}'
    '.dcp-ac{position:absolute;inset-inline:-1px;top:calc(100% + 6px);z-index:40;background:var(--dcp-bg);border:1px solid var(--dcp-line);'
    'border-radius:6px;box-shadow:0 18px 40px -20px rgba(0,0,0,.35);padding:6px;max-height:420px;overflow-y:auto}'
    '.dcp-ac-it{display:flex;align-items:center;gap:12px;padding:6px 8px;border-radius:4px;cursor:pointer;color:var(--dcp-ink)}'
    '.dcp-ac-it .dcp-th{width:44px;height:44px}'
    '.dcp-ac-it[aria-selected=true],.dcp-ac-it:hover{background:var(--dcp-soft)}'
    '.dcp-ac-t{display:flex;flex-direction:column;min-width:0;font-size:.9rem;font-weight:600;line-height:1.3}'
    '.dcp-ac-t>span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}'
    '.dcp-ac-t small{font-size:.76rem;font-weight:400;color:var(--dcp-ink3)}'
    '.dcp-ac-all{justify-content:center;font-size:.86rem;font-weight:600;color:var(--dcp-teal-d);padding:10px}'
    # browse by category
    '.dcp-browse{margin-top:48px;padding-top:22px;border-top:1px solid var(--dcp-line)}'
    '.dcp-browse h2{font-size:1rem;font-weight:700;margin:0 0 12px;color:var(--dcp-ink)}'
    '.dcp-browse ul{list-style:none;margin:0;padding:0;columns:3 200px;column-gap:28px}'
    '.dcp-browse li{display:flex;justify-content:space-between;gap:10px;padding:5px 0;break-inside:avoid;font-size:.9rem}'
    '.dcp-browse a{color:var(--dcp-ink)}'
    '.dcp-browse a:hover,.dcp-browse a[aria-current]{color:var(--dcp-teal-d)}'
    '.dcp-browse a[aria-current]{font-weight:700}'
    # quick view and compare windows reuse the picker window
    '.dcp-qv .dcp-pick-box{width:min(980px,100%)}'
    '.dcp-qv-x{position:absolute;top:10px;inset-inline-end:12px;z-index:2}'
    '.dcp-qv-body{overflow-y:auto;padding:26px 28px 28px}'
    '.dcp-qv-grid{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:28px;align-items:start}'
    '.dcp-qv-grid .dcp-card-photo{aspect-ratio:1;border:1px solid var(--dcp-line);border-radius:6px;padding:18px;cursor:default}'
    '.dcp-qv-info .dcp-card-top{padding-inline-end:40px}'
    '.dcp-qv-info h2{font-size:1.35rem;font-weight:700;line-height:1.25;margin:10px 0 10px;color:var(--dcp-ink);padding-inline-end:28px}'
    '.dcp-qv-meta{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;margin:0 0 14px}'
    '.dcp-qv-d{color:var(--dcp-ink2);font-size:.93rem;line-height:1.6;margin:0 0 18px}'
    '.dcp-qv-links{display:flex;flex-wrap:wrap;align-items:center;gap:10px 20px;margin-top:16px;font-size:.88rem}'
    '.dcp-qv-links a{color:var(--dcp-teal-d);font-weight:600}'
    '.dcp-qv-links .dcp-more{padding:0}'
    '.dcp-qv-specs h3,.dcp-qv-rel h3{font-size:1rem;font-weight:700;margin:26px 0 8px;color:var(--dcp-ink)}'
    '.dcp-qv-specs dl{margin:0;border-top:1px solid var(--dcp-line)}'
    '.dcp-qv-specs dl>div{display:grid;grid-template-columns:minmax(110px,2fr) 3fr;gap:14px;padding:8px 0;border-bottom:1px solid var(--dcp-line);font-size:.88rem}'
    '.dcp-qv-specs dt{color:var(--dcp-ink2)}.dcp-qv-specs dd{margin:0;overflow-wrap:anywhere}'
    '.dcp-qv-src{font-size:.82rem;color:var(--dcp-ink3);margin-top:10px}'
    '.dcp-qv-src a{color:var(--dcp-teal-d);font-weight:600}'
    '.dcp-qv-rel .dcp-recent-row{grid-auto-columns:minmax(200px,230px)}'
    '.dcp-qv-rel .dcp-more{margin-top:8px}'
    '.dcp-cmpv .dcp-pick-box{width:min(1180px,100%)}'
    '.dcp-cmpv-body{overflow:auto;padding:4px 24px 24px}'
    '.dcp-cmpt{border-collapse:collapse;min-width:100%;font-size:.88rem}'
    '.dcp-cmpt th,.dcp-cmpt td{border-bottom:1px solid var(--dcp-line);padding:9px 12px;text-align:start;vertical-align:top;min-width:180px}'
    '.dcp-cmpt tbody th{color:var(--dcp-ink2);font-weight:600;min-width:140px;position:sticky;inset-inline-start:0;background:var(--dcp-bg)}'
    '.dcp-cmpt thead th{border-bottom:0;padding-top:12px}'
    '.dcp-cmpt .dcp-add{width:100%}'
    '.dcp-cmpt td>div+div{margin-top:8px}'
    '.dcp-cmp-lab{display:block;font-size:.74rem;color:var(--dcp-ink3);margin-top:2px}'
    '.dcp-cmpt .dcp-cmp-toggle td{border-bottom:0;padding-top:14px}'
    # compare tray
    '.dcp-tray{position:fixed;inset-inline:16px;inset-block-end:22px;margin-inline:auto;max-width:620px;z-index:1250;'
    'display:flex;align-items:center;gap:14px;flex-wrap:wrap;padding:10px 14px;background:var(--dcp-bg);color:var(--dcp-ink);'
    'border:1px solid var(--dcp-line);border-radius:8px;box-shadow:0 18px 40px -18px rgba(0,0,0,.45)}'
    '.dcp-tray-items{display:flex;gap:8px;flex:1;min-width:0}'
    '.dcp-tray-it{position:relative}'
    '.dcp-tray-it .dcp-th{width:46px;height:46px}'
    '.dcp-tray-it button{position:absolute;top:-7px;inset-inline-end:-7px;width:20px;height:20px;border-radius:50%;border:1px solid var(--dcp-line);'
    'background:var(--dcp-bg);color:var(--dcp-ink2);font-size:.85rem;line-height:1;cursor:pointer;padding:0}'
    '.dcp .dcp-tray .dcp-btn{width:auto;padding:11px 20px}'
    '.dcp-tray .dcp-btn[disabled]{opacity:.5;cursor:default}'
    '.dcp-tray-msg{flex-basis:100%;font-size:.82rem;color:var(--dcp-ink2)}'
    '@media(max-width:900px){html.dcx-has-sticky .dcp-tray{inset-block-end:84px}}'
    # phone filter sheet
    '.dcp-sheet{align-items:flex-end;padding:0}'
    '.dcp-sheet-box{position:relative;display:flex;flex-direction:column;width:100%;max-height:88dvh;background:var(--dcp-bg);'
    'color:var(--dcp-ink);border-radius:12px 12px 0 0;overflow:hidden}'
    '.dcp-sheet-head{display:flex;align-items:center;justify-content:space-between;padding:14px 16px;border-bottom:1px solid var(--dcp-line)}'
    '.dcp-sheet-head h2{margin:0;font-size:1.1rem;font-weight:700}'
    '.dcp-sheet-body{overflow-y:auto;padding:0 16px}'
    '.dcp-sheet .dcp-facets{display:block;position:static;border:0;background:none;padding:0;margin:0;max-height:none;overflow:visible}'
    '.dcp-sheet-foot{padding:12px 16px;border-top:1px solid var(--dcp-line);background:var(--dcp-soft)}'
    '.dcp .dcp-sheet-foot .dcp-btn{width:100%}'
    # request drawer tools
    '.dcp-rtools{display:flex;flex-wrap:wrap;align-items:center;gap:6px 18px;margin:12px 0 4px}'
    '.dcp-rtools .dcp-more{padding:0}'
    '.dcp-rtools .dcp-clearbtn{margin:0;margin-inline-start:auto}'
    '.dcp-rnote{list-style:none;font-size:.88rem;color:var(--dcp-ink2);background:var(--dcp-soft);border-radius:4px;padding:10px 12px;margin-bottom:10px}'
    'html.dc-dark .dcp-rnote{background:#24272c;color:#c9cdd1}'
    '@media(max-width:700px){.dcp-qv-grid{grid-template-columns:1fr}.dcp-qv-grid .dcp-card-photo{max-width:320px}'
    '.dcp-qv-body{padding:22px 16px}.dcp-cmpv-body{padding:4px 12px 16px}}'
    '@media(prefers-reduced-motion:reduce){.dcp-open:hover{text-decoration:none}}')


if __name__ == '__main__':
    urls = write_data()
    for ar in (False, True):
        name = loc('products', ar)
        open(os.path.join(ROOT, name), "w", encoding="utf-8").write(build_products(ar, urls))
        for g in GROUP_PAGES:
            open(os.path.join(ROOT, loc('products-' + g, ar)), "w", encoding="utf-8").write(build_products(ar, urls, g))
    print('wrote products.html, products-ar.html and', 2 * len(GROUP_PAGES), 'category pages')
    keep = set()
    for p in PRODUCTS:
        if p['sku'] in PAGES:
            for ar in (False, True):
                f = loc(PAGES[p['sku']], ar)
                keep.add(f)
                open(os.path.join(ROOT, f), "w", encoding="utf-8").write(build_product_page(p, ar))
    stale = [f for f in os.listdir(ROOT) if f.startswith('product-') and f.endswith('.html') and f not in keep]
    for f in stale:                    # products that left the catalogue or lost their photo
        os.remove(os.path.join(ROOT, f))
    print('wrote', len(keep), 'product pages, removed', len(stale))
    print("done")
