# -*- coding: utf-8 -*-
"""Check the built site before it is published (CI runs this after the four build scripts):

  * every local link, image, script, stylesheet and srcset entry on every page points at a file that exists
    inside the published folder (not in _build, readme.txt or .gitignore, which are not published)
  * every other link is http, https, mailto or tel
  * every address in sitemap.xml is https://www.datacore.com.sa/<page>.html and the page exists
  * every JSON-LD block parses and holds no "<", and no inline script holds "<!--" or "<script"
  * every page has a title

    python check_site.py

Prints each problem and exits 1 when anything is broken, so a broken build is never deployed.
Standard library only, like the build scripts."""
import html, json, os, re, sys, urllib.parse
import xml.etree.ElementTree as ET

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
CODE = re.compile(r'<(script|style|template)[^>]*>.*?</\1>', re.S | re.I)      # strings in scripts are not links
ATTR = re.compile(r'''(?:href|src)\s*=\s*"([^"]*)"|srcset\s*=\s*"([^"]*)"''', re.I)
SCHEME = re.compile(r'^([a-zA-Z][a-zA-Z0-9+.-]*):')
SCHEMES = {'http', 'https', 'mailto', 'tel'}
NOT_LOCAL = re.compile(r'^[a-zA-Z]:|[\\\x00-\x1f]')                           # drive letters, backslashes, controls
UNPUBLISHED = {'_build', 'readme.txt', '.gitignore'}                          # left out by the deploy workflow
URL_SPACE = ''.join(map(chr, range(33)))                                      # browsers strip these from both ends
SCRIPT = re.compile(r'<!--.*?-->|<script\b([^>]*)>(.*?)</script\s*>', re.S | re.I)   # a script in a comment never runs
LD = re.compile(r'''\btype\s*=\s*["']?\s*application/ld\+json\b''', re.I)
PAGE = re.compile(r'^https://www\.datacore\.com\.sa/([a-z0-9][a-z0-9-]*\.html)$')
SITEMAP = '{http://www.sitemaps.org/schemas/sitemap/0.9}'


def targets(doc):
    for href, srcset in ATTR.findall(CODE.sub(' ', doc)):
        for v in ([href] if href else [part.strip().split(' ')[0] for part in srcset.split(',')]):
            v = re.sub(r'[\t\n\r]', '', html.unescape(v)).strip(URL_SPACE)
            if v and not v.startswith('#'):
                yield v


def problem(ref):
    """What is wrong with a link, or None when it is fine."""
    m = SCHEME.match(ref)
    if m:
        return None if m.group(1).lower() in SCHEMES else 'link type not allowed'
    parts = urllib.parse.urlsplit(ref)
    path = urllib.parse.unquote(parts.path)
    if not path and not parts.netloc:              # "?brand=x" on the same page
        return None
    if parts.netloc or path.startswith('/') or NOT_LOCAL.search(ref) or NOT_LOCAL.search(path):
        return 'not a relative link'               # the site is served from a sub-path; links must be relative
    target = os.path.join(ROOT, path)
    if path.endswith('/'):
        target = os.path.join(target, 'index.html')
    full = os.path.realpath(target)
    if not os.path.normcase(full).startswith(os.path.normcase(ROOT) + os.sep):
        return 'outside the site folder'
    if full[len(ROOT) + 1:].split(os.sep)[0].lower() in UNPUBLISHED:
        return 'not published'
    return None if os.path.isfile(full) else 'missing'


def script_problems(doc):
    for m in SCRIPT.finditer(doc):
        attrs, body = m.groups()
        if body is None:                           # an HTML comment
            continue
        if LD.search(attrs):
            if '<' in body:
                yield 'JSON-LD holds "<"'
            try:
                json.loads(body)
            except ValueError:
                yield 'JSON-LD does not parse'
        elif re.search(r'<!--|<script', body, re.I):
            yield 'inline script holds "<!--" or "<script"'


def sitemap_problems():
    try:
        locs = [(el.text or '').strip() for el in ET.parse(os.path.join(ROOT, 'sitemap.xml')).iter(SITEMAP + 'loc')]
    except (OSError, ET.ParseError) as e:
        return [f'sitemap.xml cannot be read: {e}']
    if not locs:
        return ['sitemap.xml lists no pages']
    out = []
    for loc in locs:
        m = PAGE.match(loc)
        if not m:
            out.append(f'not a page address on www.datacore.com.sa in the sitemap: {loc!r}')
        elif not os.path.isfile(os.path.join(ROOT, m.group(1))):
            out.append(f'in the sitemap but not built: {m.group(1)}')
    return out


def main():
    pages = sorted(f for f in os.listdir(ROOT) if f.endswith('.html'))
    bad, scripts, untitled, checked = {}, {}, [], 0
    for name in pages:
        doc = open(os.path.join(ROOT, name), encoding='utf-8', errors='replace').read()
        if not re.search(r'<title>\s*[^<\s][^<]*</title>', doc, re.I):
            untitled.append(name)
        for ref in set(targets(doc)):
            checked += 1
            why = problem(ref)
            if why:
                bad.setdefault((why, ref), []).append(name)
        for why in set(script_problems(doc)):
            scripts.setdefault(why, []).append(name)
    absent = sitemap_problems()
    print(f'{len(pages)} pages, {checked:,} links checked')
    for (why, ref), where in sorted(bad.items()):
        print(f'  {why}: {ref}  (on {len(where)} page(s), e.g. {", ".join(where[:3])})')
    for why, where in sorted(scripts.items()):
        print(f'  {why}  (on {len(where)} page(s), e.g. {", ".join(where[:3])})')
    for line in absent:
        print('  ' + line)
    for page in untitled:
        print(f'  no title: {page}')
    broken = len(bad) + sum(map(len, scripts.values())) + len(absent) + len(untitled)
    print('site check: ' + ('OK' if not broken else f'{broken} problem(s)'))
    return 1 if broken else 0


if __name__ == '__main__':
    sys.exit(main())
