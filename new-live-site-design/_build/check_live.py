# -*- coding: utf-8 -*-
"""Check the published site: every page in its sitemap, plus the shared scripts, stylesheets and catalogue
data, must answer 200. The daily "Site check" workflow runs this and opens a GitHub issue when it fails.

    python check_live.py https://afinz0z.github.io/datacore-web [--report report.md]

The sitemap lists the final domain; each address is checked on the base given here, so the check follows
wherever the site is published. Standard library only."""
import concurrent.futures as cf, datetime, re, sys, time, urllib.error, urllib.parse, urllib.request

UA = 'DatacoreSiteCheck/1.0 (+daily check of the Datacore website)'


def get(url, method='GET'):
    req = urllib.request.Request(url, method=method, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, (r.read() if method == 'GET' else b'')
    except urllib.error.HTTPError as e:
        return e.code, b''
    except Exception as e:                               # timeouts, DNS, resets
        return str(e.__class__.__name__), b''


def check(url):
    for attempt in range(3):                             # a single network blip is not a broken page
        code, _ = get(url, 'HEAD')
        if code == 200:
            return url, 200
        time.sleep(2 * (attempt + 1))
    return url, code


def main(base, report):
    base = base.rstrip('/')
    code, body = get(base + '/sitemap.xml')
    if code != 200:
        pages, problems = [], [('sitemap.xml', code)]
    else:
        pages = [urllib.parse.urlsplit(u).path.rsplit('/', 1)[-1] or 'index.html'
                 for u in re.findall(r'<loc>([^<]+)</loc>', body.decode('utf-8', 'replace'))]
        problems = []
    shared = ['dc-overlay.css', 'dc-overlay.js', 'dc-pages.css', 'dc-products.js', 'dc-forms.js', 'dc-consent.js',
              '404.html', 'robots.txt']
    home = get(base + '/products.html')[1].decode('utf-8', 'replace')
    shared += re.findall(r'(assets1/data/products-(?:data|text)\.js\?v=[0-9a-f]+)', home)
    urls = [base + '/' + p for p in dict.fromkeys(pages + shared)]
    with cf.ThreadPoolExecutor(8) as ex:
        for url, code in ex.map(check, urls):
            if code != 200:
                problems.append((url[len(base) + 1:], code))
    stamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    lines = [f'Site check of {base} on {stamp}: {len(urls):,} addresses, {len(problems)} not answering.', '']
    lines += [f'- `{p}`: {c}' for p, c in sorted(problems, key=lambda x: str(x[0]))]
    if problems:
        lines += ['', 'Fix the page or its link, push, and the next daily check closes this issue.']
    text = '\n'.join(lines)
    print(text)
    if report:
        open(report, 'w', encoding='utf-8').write(text + '\n')
    return 1 if problems else 0


if __name__ == '__main__':
    args = sys.argv[1:]
    rep = None
    if '--report' in args:
        i = args.index('--report'); rep = args[i + 1]; del args[i:i + 2]
    if len(args) != 1:
        sys.exit(__doc__)
    sys.exit(main(args[0], rep))
