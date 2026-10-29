# -*- coding: utf-8 -*-
"""Replace the product catalogue with the inventory export (the "Products-All-Categories" xlsx).

    python import_products.py path/to/Products-All-Categories-<date>.xlsx [--skipped skipped.csv] [--allow-shrink]

Writes one file per active product to content/products/<sku>.json and deletes the files of
products that are no longer in the export. When the export gives fewer than half as many products
as there were files, nothing is deleted unless --allow-shrink is given, and when it gives none,
nothing is deleted at all. Only public fields are copied: part number, name, brand, category,
department, description and specifications. Prices, fees, distributors, lead times, Zoho IDs and
the names of the staff who created records are never read into the site. The free-text
Specifications column is published for products without checked specs, so its rows labelled with a
price, cost, distributor, supplier, lead time, margin or discount, or giving an amount of money, are
dropped, and so is a description that gives an amount of money.
Standard library only, like the other build scripts."""
import html, json, os, re, sys, zipfile
import xml.etree.ElementTree as ET
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from product_data import safe_name, load_categories

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'content', 'products')
M = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
MAX_PART = 64 * 2**20        # unpacked bytes of one workbook part; the Oct 2026 export's sheet is 7.6 MB
MAX_COL = 16384              # column XFD, the last one Excel has
MAX_CELLS = 20_000_000

# Display names for brands whose export spelling is all capitals or carries a legal suffix.
BRAND = {
    'HIKVISION': 'Hikvision', 'BOSCH': 'Bosch', 'Commscope': 'CommScope', 'HUAWEI': 'Huawei',
    'ARUBA': 'Aruba', 'Dahua Technology': 'Dahua', 'Lenel S2': 'LenelS2', 'SAMSUNG': 'Samsung',
    'FINOSEL Intelligent Networks': 'Finosel', 'Datwyler IT Infra Solutions LLC': 'Datwyler',
    'SUPREMA': 'Suprema', 'd&b Audiotechnik': 'd&b audiotechnik', 'HP | Poly': 'HP Poly',
    'BIAMP': 'Biamp', 'APC (Schneider Electric)': 'APC', 'HANWHA VISION': 'Hanwha Vision',
    'HID global': 'HID', 'PLANET NETWORKING &COMMUNICATION': 'PLANET', '3M(Corning)': 'Corning',
    'CORNING Inc.': 'Corning', 'EXCEL': 'Excel', 'AVAYA': 'Avaya',
    'GAMMA FACTORY FOR METAL INDS.': 'Gamma', 'Gallagher Security': 'Gallagher',
    'RitchField Network Solutions FZC': 'RitchField', 'SAPLING': 'Sapling',
    'R&M (Reichle & De-Massari AG)': 'R&M', 'AVTECH Room Alert System': 'AVTECH',
    'AXIS COMMUNICATIONS': 'Axis', 'GRANDSTREAM': 'Grandstream', 'Vingcard (Assaabloy)': 'Vingcard',
    'Salto Inspired Acess': 'Salto', 'ACTI': 'ACTi', 'ACTi Connecting Vision': 'ACTi',
    'ATLONA': 'Atlona', 'SEAGATE': 'Seagate', 'SYSTIMAX®': 'SYSTIMAX',
    'Screen Int': 'Screen International', 'TRASSIR GLOBAL FZC LLC': 'TRASSIR',
    'AVAYO MIDDLE EAST CO. LTD': 'Avayo', 'CAME Gulf FZCO': 'CAME', 'Qlight Co., Ltd.': 'Qlight',
    'TP- Link': 'TP-Link', 'Matrix Telecom &Security': 'Matrix',
    'Network Technologies Inc. (NTI)': 'NTI', 'Intelligent Lectern Systems (ILS)': 'ILS',
    'Gianni Industries (GEM)': 'GEM', 'PRYSMIAN': 'Prysmian', 'SHARP': 'Sharp', 'BeIN': 'beIN',
    'EnGenius Networks': 'EnGenius', 'Assa Abloy': 'ASSA ABLOY', 'B-Tech AV Mounts': 'B-Tech',
    'Phenyx pro': 'Phenyx Pro', 'LegrandAV-Chief': 'Chief', 'LegrandAV-Da-Lite': 'Da-Lite',
    'LegrandAV- Middle Atlantic': 'Middle Atlantic', 'LegrandAV-Vaddio': 'Vaddio',
    'LegrandAV- C2G': 'C2G', 'Beamz': 'beamZ',
}
# The export files some products under a placeholder instead of the maker. These part numbers were
# looked up (Oct 2026): 853.319 and 151.413 are beamZ article numbers, MASK4CT-BL is a Biamp speaker,
# XGS-6311-12X is a PLANET switch (its own name says so; the export names CommScope).
BRAND_BY_SKU = {'853.319': 'beamZ', '151.413': 'beamZ', 'MASK4CT-BL': 'Biamp', 'XGS-6311-12X': 'PLANET'}
# Categories the export gets wrong: MASK4CT-BL is a loudspeaker filed under "Queue Management System".
CATEGORY_BY_SKU = {'MASK4CT-BL': 'Speaker'}
# Supporting-product links that are wrong (screen outside the mount's range, or no fit at all); see the file.
_LINK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'product_links_fix.json')
BAD_LINKS = ({(x['parent'], x['child']) for x in json.load(open(_LINK_FILE, encoding='utf-8'))['remove']}
             if os.path.exists(_LINK_FILE) else set())
# Manufacturer values that are not a maker's name: the card shows no brand rather than these.
NO_BRAND = {'generic', 'local', 'queue management system'}
# Rows that only reserve a slot in the inventory system ("Custom-1", "Rack", "Structure").
PLACEHOLDER = re.compile(r'^(custom|structure|rack|wap|pc)(-\d+)?$', re.I)
TBA = re.compile(r'^tba(-\d+)?$', re.I)
# Models the maker marks as discontinued on its own site, with that page as proof. They stay off the site.
_DISC_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'product_discontinued.json')
DISCONTINUED = json.load(open(_DISC_FILE, encoding='utf-8')) if os.path.exists(_DISC_FILE) else {}
DASHES = re.compile('[%s]' % ''.join(map(chr, (0x2010, 0x2011, 0x2012, 0x2013, 0x2014, 0x2212))))   # hyphen and dash variants
INVISIBLE = re.compile('[%s]' % ''.join(map(chr, (0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF, 0xAD))))   # zero-width, soft hyphen


def brand_for(raw, sku, name, desc):
    """The brand a card shows, or '' when the export doesn't name the maker."""
    if sku in BRAND_BY_SKU:
        return BRAND_BY_SKU[sku]
    if raw.lower() == 'queue management system':     # Orchestra is Qmatic's queue-management platform
        text = f'{name} {desc}'
        if re.search(r'\b(qmatic|orchestra)\b', text, re.I):
            return 'Qmatic'
        if re.search(r'\btp-link\b', text, re.I):
            return 'TP-Link'
        return ''
    return '' if raw.lower() in NO_BRAND else BRAND.get(raw, raw)


def skip_reason(raw_brand, cat, sku, name):
    """Why a row stays off the site, or None. Every skipped row is listed in the --skipped file."""
    if TBA.match(raw_brand) or TBA.match(cat) or TBA.match(sku) or TBA.match(name):
        return 'Marked TBA (to be assigned)'
    if PLACEHOLDER.match(sku) and (PLACEHOLDER.match(name) or name.lower() == sku.lower()):
        return 'Placeholder entry, not a real product'
    if raw_brand.lower() in ('custom', 'rack', 'pc', 'wap', 'structure'):
        return 'No brand or model (custom or unspecified item)'
    return None


# bullets pasted from Word's Symbol and Wingdings fonts arrive as private-use characters that show as boxes
SYMBOL_FONT = re.compile('[%s-%s]' % (chr(0xF000), chr(0xF0FF)))


def clean(s):
    return ' '.join(DASHES.sub('-', SYMBOL_FONT.sub(' ' + chr(0x2022) + ' ', INVISIBLE.sub('', str(s or '')))).split())


def _text(el):
    """The visible text of a shared or inline string: its <t> or its rich-text runs, without the
    phonetic runs (<rPh>) Excel keeps hidden."""
    out = []
    for x in el:
        if x.tag == M + 't':
            out.append(x.text or '')
        elif x.tag == M + 'r':
            out.extend(t.text or '' for t in x.findall(M + 't'))
    return ''.join(out)


def read_sheet(path, name):
    """Rows of one worksheet as lists of strings (zipfile + ElementTree, no openpyxl)."""
    with zipfile.ZipFile(path) as z:
        def part(n):
            if z.getinfo(n).file_size > MAX_PART:
                raise ValueError(f'{n} in {path} unpacks to more than {MAX_PART >> 20} MB')
            return ET.fromstring(z.read(n))
        wb = part('xl/workbook.xml')
        rid = next(s.get(R + 'id') for s in wb.iter(M + 'sheet') if s.get('name') == name)
        rels = part('xl/_rels/workbook.xml.rels')
        target = next(r.get('Target') for r in rels if r.get('Id') == rid).lstrip('/')
        target = target if target.startswith('xl/') else 'xl/' + target
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            shared = [_text(si) for si in part('xl/sharedStrings.xml').iter(M + 'si')]
        sheet = part(target)
    rows, cells = [], 0
    for row in sheet.iter(M + 'row'):
        vals = {}
        for c in row.iter(M + 'c'):
            ref = c.get('r') or ''
            m = re.fullmatch(r'([A-Z]{1,3})\d*', ref)
            if not m:                         # no cell reference to place it by
                continue
            col = 0
            for ch in m.group(1):
                col = col * 26 + ord(ch) - 64
            if col > MAX_COL:
                continue
            v, t = c.find(M + 'v'), c.get('t')
            if t == 's':
                i = (v.text or '').strip() if v is not None else ''
                if i and not (i.isdecimal() and int(i) < len(shared)):
                    raise ValueError(f'cell {ref} of {name} points at shared string {i!r}, which does not exist')
                val = shared[int(i)] if i else ''
            elif t == 'inlineStr':
                val = _text(c.find(M + 'is')) if c.find(M + 'is') is not None else ''
            else:
                val = v.text if v is not None else ''
            vals[col - 1] = val
        if vals:
            cells += max(vals) + 1
            if cells > MAX_CELLS:
                raise ValueError(f'{name} in {path} has more than {MAX_CELLS} cells')
            rows.append([vals.get(i, '') for i in range(max(vals) + 1)])
    return rows


def plain(htm):
    t = re.sub(r'(?i)<br\s*/?>|</p>', ' ', str(htm or ''))
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    return clean(re.sub(r'</?[A-Za-z!?][^<>]*>', ' ', t))     # &lt;script&gt; is a tag again once unescaped


# one name per spec, whichever spelling the export used
SYNONYM = {'product type': 'Type', 'color': 'Colour', 'colour': 'Colour'}


def label_case(s):
    """Sentence case that keeps acronyms: 'Mounting Type' -> 'Mounting type', 'IR Distance' -> 'IR distance'."""
    words = clean(s).strip(' :-').split(' ')
    out = []
    for i, w in enumerate(words):
        if i == 0:
            w = w.capitalize() if w.isupper() and len(w) > 4 else w[:1].upper() + w[1:]
        elif (w[:1].isupper() and w[1:].islower()) or (w.isupper() and len(w) > 5):
            w = w.lower()
        out.append(w)
    label = ' '.join(out)
    return SYNONYM.get(label.lower(), label)


def parse_specs(text):
    out, seen = [], set()
    for line in str(text or '').splitlines():
        if ':' not in line:
            continue
        k, v = line.split(':', 1)
        k, v = label_case(k), clean(v)
        if not k or not v or v.lower() in ('-', 'n/a', 'na', 'tba', 'none', 'nil') or k.lower() in seen:
            continue
        if re.fullmatch(r'IP\d{2}', v, re.I) and 'protection' not in k.lower():
            k = 'Ingress protection'   # the export has protection ratings filed under other labels
            if k.lower() in seen:
                continue
        seen.add(k.lower())
        out.append({'label': k, 'value': v})
    return out


def code_like(name, sku):
    """True when the name is only a model code ("DIN-AO8", "TLP Pro 725C"): every token has a digit
    or is four letters or fewer."""
    if re.sub(r'[^a-z0-9]', '', name.lower()) == re.sub(r'[^a-z0-9]', '', sku.lower()):
        return True
    toks = re.findall(r'[A-Za-z0-9]+', name)
    return bool(toks) and all(any(ch.isdigit() for ch in w) or len(w) <= 4 for w in toks)


GENERIC_EXTRA = {'system', 'unit', 'accessory', 'accessories', 'kit', 'set', 'device', 'module', 'battery', 'cable',
                 'mount', 'wall', 'ceiling', 'bracket', 'panel', 'single', 'double', 'manager', 'box'}


def generic_name(name, info, cat):
    """True when the name is only a product kind ("Speaker", "Wireless Access Point"), no model or size."""
    words = re.findall(r'[A-Za-z]+', name)
    if not words or re.search(r'\d', name) or len(words) > 4:
        return False
    vocab = set(re.findall(r'[a-z]+', f"{info['en']} {cat}".lower())) | GENERIC_EXTRA
    return all(w.lower() in vocab or w.lower().rstrip('s') in vocab for w in words)


def readable_name(name, desc, brand):
    """For a code-only name, the first phrase of the product's own description with the brand and the
    code taken off the front, followed by the code: "One-Gang MAAP Mounting Frame - Black (CPM101)".
    Returns the name unchanged when the description has no usable phrase."""
    import difflib
    if not desc:
        return name
    desc = SYMBOL_FONT.sub(chr(0x2022), desc)
    phrase = re.split(r'\s*(?:\u2022|;|\||\.\s)\s*', desc.strip(' \u2022'))[0]
    # a title run into a sentence: "Amplifier, 75 W The AMP-X75 provides..." (but not Samsung's "The Wall")
    phrase = re.split(r'\s+(?=(?:The|This|These|It|Its)\s+(?:\S+\s+){0,2}(?:is|are|provides|offers|delivers|'
                      r'features|has|allows|enables|combines|supports|brings|gives|lets)\b)', phrase)[0]
    phrase = clean(phrase).strip(' -:,')
    for _ in range(2):                         # the export sometimes misspells the brand ("FONOSEL")
        head, _, rest = phrase.partition(' ')
        if brand and rest and difflib.SequenceMatcher(None, head.lower().strip(','), brand.lower()).ratio() >= 0.75:
            phrase = rest.lstrip(' ,:-')
        if name and phrase.lower().startswith(name.lower()):
            phrase = phrase[len(name):].lstrip(' ,:-')
    if (not re.search(r'[A-Za-z]{3,}\W+(?:\w+\W+)*?[A-Za-z]{3,}', phrase) or phrase[:1] in '(*+_'
            or re.search(r'[_=]|\*\s*\d|\*\s*$', phrase)):
        return name
    if len(phrase) > 70:
        cut = phrase[:70]
        phrase = cut[:cut.rfind(', ')] if cut.rfind(', ') > 30 else cut[:cut.rfind(' ')]
        phrase = phrase.rstrip(' ,-:(')
        phrase = re.sub(r'(?i)(?:\s+(?:and|with|for|of|the|to|in|or|&|-))+$', '', phrase)   # no dangling "and"
    if phrase.isupper():                       # "RECHARGEABLE BATTERY" -> "Rechargeable Battery"
        phrase = ' '.join(w if any(c.isdigit() for c in w) or len(w) <= 3 else w.capitalize() for w in phrase.split())
    key = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
    return phrase if key(name) in key(phrase) else f'{phrase} ({name})'


def described_name(name, desc, brand):
    """For a generic name, the description's first phrase, led by the generic word when the phrase lacks it:
    "Monitor" -> "43-55-Inch Indoor Wall-Mounted Digital Signage Monitor"."""
    phrase = readable_name('\x00', desc, brand)          # same cleaning, without a code to strip
    if phrase == '\x00':
        return name
    phrase = phrase.replace(' (\x00)', '')
    have = {w.lower()[:5] for w in re.findall(r'[A-Za-z]+', phrase)}
    if len(re.findall(r'[A-Za-z0-9]+', phrase)) <= len(re.findall(r'[A-Za-z]+', name)):
        return name
    if all(w.lower()[:5] in have for w in re.findall(r'[A-Za-z]+', name)):
        return phrase
    return f'{name}, {phrase}'[:90].rsplit(' ', 1)[0] if len(name) + len(phrase) > 88 else f'{name}, {phrase}'


NOT_A_SPEC = re.compile(r'^(product name|name|model|model name|brand|manufacturer|part number|sku|price|cost)$', re.I)
# commercial terms that must not reach the site, anywhere in a label
PRIVATE = re.compile(r'pric(?:e|ing)|cost|distributor|supplier|lead[\s_-]*time|(?:profit|gross|net)\s+margin|^margin$|discount', re.I)
# an amount of money: SAR, USD, $, or the Arabic riyal (ر.س, ريال, ﷼) next to a number
_CUR = r'(?:(?<![A-Za-z])(?:SAR|USD)(?![A-Za-z])|\$|\u0631\.\s?\u0633|\u0631\u064a\u0627\u0644|\ufdfc)'
MONEY = re.compile(r'%s[\s:.]*\d|\d\s*%s' % (_CUR, _CUR), re.I)


def sheet_rows(d):
    """The export's own Specifications, for products whose maker's pages could not supply checked ones.
    The website publishes them, labelled as inventory data not checked against the maker, so rows
    that name a price, cost, distributor, supplier, lead time, margin or discount, or give an amount
    of money, are dropped."""
    return [s for s in parse_specs(d.get('Specifications'))
            if not NOT_A_SPEC.search(s['label']) and not PRIVATE.search(s['label'])
            and not MONEY.search(s['value']) and len(s['label']) <= 45 and len(s['value']) <= 220]


def classification(d, info):
    """What the export's classification columns say: product type, series and sale unit. Cards show
    these until the product's specifications have been checked against the manufacturer, together
    with the export's free-text Specifications where it has usable rows (sheet_rows())."""
    out = []
    ptype = clean(d.get('Product Type'))
    if ptype and ptype.lower() not in info['en'].lower():
        ptype = re.sub(r'(?<=[A-Za-z])-(?=[A-Za-z])', ' ', ptype)
        out.append({'label': 'Type', 'value': ptype[:1].upper() + ptype[1:].lower() if ptype.isupper() else ptype})
    if clean(d.get('Series')):
        out.append({'label': 'Series', 'value': clean(d['Series'])})
    unit = clean(d.get('Unit'))
    if unit and unit.lower() not in ('each', 'pcs'):
        out.append({'label': 'Unit', 'value': unit})
    return out


def _key(s):
    return re.sub(r'\s+', '', str(s or '')).upper()


def _list(s):
    return [x for x in (clean(v) for v in str(s or '').split(',')) if x]


def csv_cell(s):
    """Text Excel won't run as a formula: a cell starting with = + - @ tab or CR gets a leading apostrophe."""
    s = str(s)
    return "'" + s if s[:1] in ('=', '+', '-', '@', '\t', '\r') else s


def main(xlsx, skipped_csv=None, allow_shrink=False):
    rows = read_sheet(xlsx, 'Products')
    hi = next(i for i, r in enumerate(rows) if 'Part Number' in r)
    head = rows[hi]
    data = [dict(zip(head, r + [''] * (len(head) - len(r)))) for r in rows[hi + 1:]]
    data = [d for d in data if clean(d.get('Part Number'))]
    groups, resolve = load_categories()
    gorder = {k: i for i, k in enumerate(groups)}
    unknown, blanked, changed = Counter(), Counter(), Counter()
    skipped, items, priced = [], [], 0
    for d in data:
        sku, name = clean(d['Part Number']), clean(d['Product Name'])
        raw_brand, cat, dept = clean(d['Manufacturer']), clean(d['Category']), clean(d['Department']).upper()
        cat = CATEGORY_BY_SKU.get(sku, cat)
        why = ('Inactive in the inventory system' if clean(d.get('Status')).upper() != 'ACTIVE'
               else 'Discontinued by the maker' if sku in DISCONTINUED
               else skip_reason(raw_brand, cat, sku, name))
        if why:
            skipped.append((d, why)); continue
        brand = brand_for(raw_brand, sku, name, plain(d.get('Description')))
        if not brand:
            blanked[raw_brand] += 1
        elif brand != BRAND.get(raw_brand, raw_brand):
            changed[f'{raw_brand} -> {brand}'] += 1
        info = resolve(cat, dept)
        if not info['known']:
            unknown[cat] += 1
        desc = plain(d.get('Description'))
        if MONEY.search(desc):
            priced += 1
            desc = ''
        if re.match(r'(?i)^(tba|n/?a)\b', desc) or desc.lower() == name.lower():
            desc = ''
        entry = {'sku': sku, 'order': 0, 'n': name or sku, 'b': brand, 'c': cat, 'dept': dept, 'avail': 'lead'}
        if code_like(name or sku, sku):           # a code alone: give visitors words to read and search
            better = readable_name(name or sku, desc, brand or raw_brand)
        elif generic_name(name, info, cat):         # a kind alone ("Speaker"): say which one
            better = described_name(name, desc, brand or raw_brand)
        else:
            better = entry['n']
        if better != entry['n']:
            entry['model'] = entry['n']
            entry['n'] = better
        tail = re.search(r'\s*\(([^()]+)\)$', entry['n'])   # "Switch License (Huawei)": the card already shows the brand
        if tail and brand and _key(tail.group(1)).lower() == _key(brand).lower() and tail.start() > 3:
            entry['n'] = entry['n'][:tail.start()]
        if desc:
            entry['d'] = desc
        cls = classification(d, info)
        rows = sheet_rows(d)
        if rows:                                  # type first, then the export's specs, then series and unit
            seen = {r['label'].lower() for r in rows}
            entry['specs'] = ([c for c in cls if c['label'] == 'Type' and 'type' not in seen] + rows
                              + [c for c in cls if c['label'] != 'Type' and c['label'].lower() not in seen])
            entry['spec_src'] = 'inventory'
        else:
            entry['specs'] = cls
        items.append((info, entry, d))

    # Bundles: the export lists the supporting products on each main product and the main products on
    # each supporting one. Join both directions, keeping only products that are on the site.
    on_site = {_key(e['sku']): e['sku'] for _, e, _ in items}
    kids = {}
    for _, e, d in items:
        for c in _list(d.get('Supporting Products (Children)')):
            if _key(c) in on_site and _key(c) != _key(e['sku']) and (e['sku'], on_site[_key(c)]) not in BAD_LINKS:
                kids.setdefault(e['sku'], set()).add(on_site[_key(c)])
        for p in _list(d.get('Supporting For (Parents)')):
            if _key(p) in on_site and _key(p) != _key(e['sku']) and (on_site[_key(p)], e['sku']) not in BAD_LINKS:
                kids.setdefault(on_site[_key(p)], set()).add(e['sku'])
    parents = {}
    for p, cs in kids.items():
        for c in cs:
            parents.setdefault(c, set()).add(p)
    for _, e, _ in items:
        if e['sku'] in kids:
            e['acc'] = sorted(kids[e['sku']])
        if e['sku'] in parents:
            e['for'] = sorted(parents[e['sku']])

    catsize = Counter(i['en'] for i, _, _ in items)
    items.sort(key=lambda x: (gorder.get(x[0]['grp'], 99), -catsize[x[0]['en']], x[0]['en'].lower(),
                              x[1]['b'].lower(), x[1]['n'].lower(), x[1]['sku']))
    os.makedirs(OUT, exist_ok=True)
    before = sum(1 for f in os.listdir(OUT) if f.lower().endswith('.json'))
    written, kept_checks = set(), 0       # lower-case stems: Windows treats AB-1.json and ab-1.json as one file
    for i, (_, e, _) in enumerate(items, 1):
        e['order'] = i
        stem = base = safe_name(e['sku'])
        n = 2
        while stem.lower() in written:    # two SKUs that only differ in punctuation or case
            stem = f'{base}-{n}'; n += 1
        written.add(stem.lower())
        path = os.path.join(OUT, stem + '.json')
        old = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}
        # specs checked against the manufacturer survive a re-import, but only for the same SKU:
        # after a SKU change another product can end up with this file name
        if _key(old.get('sku')) == _key(e['sku']):
            if old.get('checked'):
                e['specs'] = old.get('specs', [])
                e.pop('spec_src', None)
                for k in ('src', 'checked', 'src_kind', 'src_name'):
                    if old.get(k):
                        e[k] = old[k]
                kept_checks += 1
            if old.get('videos'):             # official videos from the maker's page survive too
                e['videos'] = old['videos']
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(e, f, ensure_ascii=False, indent=1)
            f.write('\n')
    removed = 0
    stale = [f for f in os.listdir(OUT) if f.lower().endswith('.json') and f[:-5].lower() not in written]
    if stale and not written:
        print(f'No product came through, so the {len(stale)} old product files were not deleted. '
              'Check the export (a renamed Status column, for one, marks every row inactive).')
    elif stale and len(written) * 2 < before and not allow_shrink:
        print(f'Only {len(written)} products came through against {before} files before, so the '
              f'{len(stale)} old product files were not deleted. Check the export, and if the catalogue '
              'really shrank, run again with --allow-shrink.')
    else:
        for f in stale:
            os.remove(os.path.join(OUT, f)); removed += 1

    print(f'{len(items)} products written, {removed} old files removed, {kept_checks} kept their checked specs')
    if priced:
        print(f'descriptions left out because they give an amount of money: {priced}')
    print(f'bundles: {len(kids)} products with supporting products, {len(parents)} supporting products linked')
    print(f'skipped {len(skipped)}:', dict(Counter(w for _, w in skipped)))
    if skipped_csv:
        import csv
        all_keys = {_key(d['Part Number']) for d in data}
        with open(skipped_csv, 'w', encoding='utf-8-sig', newline='') as f:   # BOM so Excel reads UTF-8
            w = csv.writer(f)
            w.writerow(['Part number', 'Product name', 'Manufacturer in export', 'Category in export',
                        'Department', 'Reason', 'Note'])
            for d, why in skipped:
                bundled = [c for c in _list(d.get('Supporting Products (Children)')) if _key(c) in all_keys]
                note = (f'Has {len(bundled)} supporting products, which are on the site' if bundled else '')
                if why == 'Discontinued by the maker':
                    note = '; '.join(x for x in (DISCONTINUED[clean(d['Part Number'])]['page'], note) if x)
                w.writerow([csv_cell(x) for x in (clean(d['Part Number']), clean(d['Product Name']),
                            clean(d['Manufacturer']), clean(d['Category']), clean(d['Department']), why, note)])
        print('skipped rows listed in', skipped_csv)
    print('brand corrected from the export:', dict(changed) or 'none')
    print('no brand shown (export does not name the maker):', dict(blanked))
    print('categories not in product_categories.json (shown under Other):', dict(unknown) or 'none')
    print('by group:', dict(Counter(i['grp'] for i, _, _ in items).most_common()))
    print('renamed from a code-only name:', sum(1 for _, e, _ in items if 'model' in e))
    print('with classification specs:', sum(1 for _, e, _ in items if e['specs']),
          '| with description:', sum(1 for _, e, _ in items if 'd' in e))


if __name__ == '__main__':
    args = sys.argv[1:]
    out = None
    shrink = '--allow-shrink' in args
    if shrink:
        args.remove('--allow-shrink')
    if '--skipped' in args:
        i = args.index('--skipped'); out = args[i + 1]; del args[i:i + 2]
    if len(args) != 1:
        sys.exit(__doc__)
    main(args[0], out, shrink)
