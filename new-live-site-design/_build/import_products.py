# -*- coding: utf-8 -*-
"""Replace the product catalogue with the inventory export (the "Products-All-Categories" xlsx).

    python import_products.py path/to/Products-All-Categories-<date>.xlsx [--skipped skipped.csv]

Writes one file per active product to content/products/<sku>.json and deletes the files of
products that are no longer in the export. Only public fields are copied: part number, name,
brand, category, department, description and specifications. Prices, fees, distributors, lead
times, Zoho IDs and the names of the staff who created records are never read into the site.
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
# looked up (Oct 2026): 853.319 and 151.413 are beamZ article numbers, MASK4CT-BL is a Biamp speaker.
BRAND_BY_SKU = {'853.319': 'beamZ', '151.413': 'beamZ', 'MASK4CT-BL': 'Biamp'}
# Manufacturer values that are not a maker's name: the card shows no brand rather than these.
NO_BRAND = {'generic', 'local', 'queue management system'}
# Rows that only reserve a slot in the inventory system ("Custom-1", "Rack", "Structure").
PLACEHOLDER = re.compile(r'^(custom|structure|rack|wap|pc)(-\d+)?$', re.I)
TBA = re.compile(r'^tba(-\d+)?$', re.I)
DASHES = re.compile('[‐‑‒–—−]')


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


def clean(s):
    return ' '.join(DASHES.sub('-', str(s or '')).split())


def read_sheet(path, name):
    """Rows of one worksheet as lists of strings (zipfile + ElementTree, no openpyxl)."""
    z = zipfile.ZipFile(path)
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rid = next(s.get(R + 'id') for s in wb.iter(M + 'sheet') if s.get('name') == name)
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    target = next(r.get('Target') for r in rels if r.get('Id') == rid).lstrip('/')
    target = target if target.startswith('xl/') else 'xl/' + target
    shared = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).iter(M + 'si'):
            shared.append(''.join(t.text or '' for t in si.iter(M + 't')))
    rows = []
    for row in ET.fromstring(z.read(target)).iter(M + 'row'):
        vals = {}
        for c in row.iter(M + 'c'):
            letters = re.match(r'[A-Z]+', c.get('r')).group(0)
            col = 0
            for ch in letters:
                col = col * 26 + ord(ch) - 64
            v, t = c.find(M + 'v'), c.get('t')
            if t == 's':
                val = shared[int(v.text)] if v is not None else ''
            elif t == 'inlineStr':
                val = ''.join(x.text or '' for x in c.iter(M + 't'))
            else:
                val = v.text if v is not None else ''
            vals[col - 1] = val
        if vals:
            rows.append([vals.get(i, '') for i in range(max(vals) + 1)])
    return rows


def plain(htm):
    t = re.sub(r'(?i)<br\s*/?>|</p>', ' ', str(htm or ''))
    return clean(html.unescape(re.sub(r'<[^>]+>', ' ', t)))


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


def classification(d, info):
    """What the export's classification columns say: product type, series and sale unit. Cards show
    these until the product's specifications have been checked against the manufacturer; the free-text
    Specifications column of the export is not published (it is too often wrong)."""
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


def main(xlsx, skipped_csv=None):
    rows = read_sheet(xlsx, 'Products')
    hi = next(i for i, r in enumerate(rows) if 'Part Number' in r)
    head = rows[hi]
    data = [dict(zip(head, r + [''] * (len(head) - len(r)))) for r in rows[hi + 1:]]
    data = [d for d in data if clean(d.get('Part Number'))]
    groups, resolve = load_categories()
    gorder = {k: i for i, k in enumerate(groups)}
    unknown, blanked, changed = Counter(), Counter(), Counter()
    skipped, items = [], []
    for d in data:
        sku, name = clean(d['Part Number']), clean(d['Product Name'])
        raw_brand, cat, dept = clean(d['Manufacturer']), clean(d['Category']), clean(d['Department']).upper()
        why = ('Inactive in the inventory system' if clean(d.get('Status')).upper() != 'ACTIVE'
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
        if re.match(r'(?i)^(tba|n/?a)\b', desc) or desc.lower() == name.lower():
            desc = ''
        entry = {'sku': sku, 'order': 0, 'n': name or sku, 'b': brand, 'c': cat, 'dept': dept, 'avail': 'lead'}
        if desc:
            entry['d'] = desc
        entry['specs'] = classification(d, info)
        items.append((info, entry, d))

    # Bundles: the export lists the supporting products on each main product and the main products on
    # each supporting one. Join both directions, keeping only products that are on the site.
    on_site = {_key(e['sku']): e['sku'] for _, e, _ in items}
    kids = {}
    for _, e, d in items:
        for c in _list(d.get('Supporting Products (Children)')):
            if _key(c) in on_site and _key(c) != _key(e['sku']):
                kids.setdefault(e['sku'], set()).add(on_site[_key(c)])
        for p in _list(d.get('Supporting For (Parents)')):
            if _key(p) in on_site and _key(p) != _key(e['sku']):
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
    written, kept_checks = set(), 0
    for i, (_, e, _) in enumerate(items, 1):
        e['order'] = i
        stem = base = safe_name(e['sku'])
        n = 2
        while stem in written:            # two SKUs that only differ in punctuation
            stem = f'{base}-{n}'; n += 1
        written.add(stem)
        path = os.path.join(OUT, stem + '.json')
        if os.path.exists(path):          # specs checked against the manufacturer survive a re-import
            old = json.load(open(path, encoding='utf-8'))
            if old.get('checked'):
                e['specs'] = old.get('specs', [])
                for k in ('src', 'checked'):
                    if old.get(k):
                        e[k] = old[k]
                kept_checks += 1
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(e, f, ensure_ascii=False, indent=1)
            f.write('\n')
    removed = 0
    for f in os.listdir(OUT):
        if f.endswith('.json') and f[:-5] not in written:
            os.remove(os.path.join(OUT, f)); removed += 1

    print(f'{len(items)} products written, {removed} old files removed, {kept_checks} kept their checked specs')
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
                w.writerow([clean(d['Part Number']), clean(d['Product Name']), clean(d['Manufacturer']),
                            clean(d['Category']), clean(d['Department']), why, note])
        print('skipped rows listed in', skipped_csv)
    print('brand corrected from the export:', dict(changed) or 'none')
    print('no brand shown (export does not name the maker):', dict(blanked))
    print('categories not in product_categories.json (shown under Other):', dict(unknown) or 'none')
    print('by group:', dict(Counter(i['grp'] for i, _, _ in items).most_common()))
    print('with classification specs:', sum(1 for _, e, _ in items if e['specs']),
          '| with description:', sum(1 for _, e, _ in items if 'd' in e))


if __name__ == '__main__':
    args = sys.argv[1:]
    out = None
    if '--skipped' in args:
        i = args.index('--skipped'); out = args[i + 1]; del args[i:i + 2]
    if len(args) != 1:
        sys.exit(__doc__)
    main(args[0], out)
