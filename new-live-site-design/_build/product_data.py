# -*- coding: utf-8 -*-
"""Shared by import_products.py and build_products.py: photo file names and the
category map (display names, Arabic, filter group, card icon)."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
_RESERVED = {'CON', 'PRN', 'AUX', 'NUL'} | {f'{p}{i}' for p in ('COM', 'LPT') for i in range(1, 10)}


def safe_name(sku):
    """File-name stem for a product: the SKU with anything outside A-Z a-z 0-9 . _ - turned into '_'.
    Used for content/products/<stem>.json and assets1/images/products/<stem>.webp."""
    s = re.sub(r'[^A-Za-z0-9._-]+', '_', str(sku).strip()).strip('._') or 'item'
    return '_' + s if s.upper() in _RESERVED else s


def _key(s):
    return ' '.join(str(s or '').split()).lower()


def load_categories():
    """-> (groups, resolve). groups: ordered {key: (en, ar)}. resolve(category, dept) -> dict with
    en, ar, grp, g. Unknown categories fall into 'other' with their own name in both languages."""
    raw = json.load(open(os.path.join(HERE, 'product_categories.json'), encoding='utf-8'))
    groups = {k: tuple(v) for k, v in raw['groups'].items()}
    table = {}
    for k, v in raw['categories'].items():
        cat, _, dept = k.partition('|')
        table[(_key(cat), dept.upper())] = v

    def resolve(category, dept=''):
        v = table.get((_key(category), str(dept or '').upper())) or table.get((_key(category), ''))
        if not v:
            name = ' '.join(str(category or '').split()) or 'Other'
            return {'en': name, 'ar': name, 'grp': 'other', 'g': 'rack', 'known': False}
        return {'en': v[0], 'ar': v[1], 'grp': v[2], 'g': v[3], 'known': True}

    return groups, resolve
