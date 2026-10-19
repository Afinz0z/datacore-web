# -*- coding: utf-8 -*-
"""Check the built site before it is published (CI runs this after the four build scripts):

  * every local link, image, script, stylesheet and srcset entry on every page points at a file that exists
  * every address in sitemap.xml exists
  * every page has a title

    python check_site.py

Prints each problem and exits 1 when anything is broken, so a broken build is never deployed.
Standard library only, like the build scripts."""
import html, os, re, sys, urllib.parse

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
CODE = re.compile(r'<(script|style|template)[^>]*>.*?</\1>', re.S | re.I)      # strings in scripts are not links
ATTR = re.compile(r'''(?:href|src)\s*=\s*"([^"]*)"|srcset\s*=\s*"([^"]*)"''', re.I)
OUTSIDE = re.compile(r'^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//|#)')                    # http:, mailto:, tel:, data:, //host, #anchor


def targets(doc):
    for href, srcset in ATTR.findall(CODE.sub(' ', doc)):
        for v in ([href] if href else [part.strip().split(' ')[0] for part in srcset.split(',')]):
            v = html.unescape(v.strip())
            if v and not OUTSIDE.match(v):
                yield v


def exists(ref):
    path = urllib.parse.unquote(urllib.parse.urlsplit(ref).path)
    if not path:                                   # "?brand=x" on the same page
        return True
    if path.startswith('/'):
        return False                               # the site is served from a sub-path; links must be relative
    full = os.path.normpath(os.path.join(ROOT, path))
    if path.endswith('/'):
        full = os.path.join(full, 'index.html')
    return os.path.isfile(full)


def main():
    pages = sorted(f for f in os.listdir(ROOT) if f.endswith('.html'))
    missing, untitled, checked = {}, [], 0
    for name in pages:
        doc = open(os.path.join(ROOT, name), encoding='utf-8', errors='replace').read()
        if not re.search(r'<title>\s*[^<\s][^<]*</title>', doc, re.I):
            untitled.append(name)
        for ref in set(targets(doc)):
            checked += 1
            if not exists(ref):
                missing.setdefault(ref, []).append(name)
    sm = os.path.join(ROOT, 'sitemap.xml')
    absent = []
    if os.path.exists(sm):
        for loc in re.findall(r'<loc>([^<]+)</loc>', open(sm, encoding='utf-8').read()):
            page = urllib.parse.urlsplit(loc).path.rsplit('/', 1)[-1] or 'index.html'
            if not os.path.isfile(os.path.join(ROOT, page)):
                absent.append(page)
    print(f'{len(pages)} pages, {checked:,} local links checked')
    for ref, where in sorted(missing.items()):
        print(f'  missing: {ref}  (on {len(where)} page(s), e.g. {", ".join(where[:3])})')
    for page in absent:
        print(f'  in the sitemap but not built: {page}')
    for page in untitled:
        print(f'  no title: {page}')
    broken = len(missing) + len(absent) + len(untitled)
    print('site check: ' + ('OK' if not broken else f'{broken} problem(s)'))
    return 1 if broken else 0


if __name__ == '__main__':
    sys.exit(main())
