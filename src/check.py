#!/usr/bin/env python3
"""Post-build checks. Run from src/:  python3 build.py && python3 check.py"""
import os, re, sys, subprocess, tempfile, shutil
from html.parser import HTMLParser

# cp1252 consoles/pipes cannot print the check marks — force UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.normpath(os.path.join(HERE, "..", "dist"))
VOID = {'br','img','input','meta','link','hr','path','circle','rect','source','use',
        'area','col','polygon','line','ellipse','polyline','stop'}
fails = []
warns = []

class P(HTMLParser):
    def __init__(s): super().__init__(); s.st=[]; s.bad=[]
    def handle_starttag(s,t,a):
        if t not in VOID: s.st.append(t)
    def handle_endtag(s,t):
        if t in VOID: return
        if s.st and s.st[-1]==t: s.st.pop()
        elif t in s.st:
            while s.st and s.st.pop()!=t: pass
            s.bad.append(f'unclosed before </{t}>')
        else: s.bad.append(f'stray </{t}>')

# 1. no direction-locked CSS
css = open(os.path.join(HERE,"css.py"), encoding="utf-8").read()
phys = re.findall(r'(?:margin|padding|border)-(?:left|right)\s*:'
                  r'|float\s*:\s*(?:left|right)'
                  r'|text-align\s*:\s*(?:left|right)', css)
if phys: fails.append(f"RTL: physical properties in css.py -> {set(phys)}")

# 2. brand teal never carries text
# --brand on a dark background is fine (5.8:1 on --ink); mark those
# with a trailing /* ok-on-dark */ comment. Everything else is a failure.
for line in css.splitlines():
    if re.search(r'\bcolor\s*:\s*var\(--brand\)', line) and 'ok-on-dark' not in line:
        fails.append(f"CONTRAST: --brand carries text at 2.83:1 -> {line.strip()[:70]}")

files = sorted(f for f in os.listdir(DIST) if f.endswith(".html"))
# 7 pages + terms/privacy/404 + 38 service details, in two languages
if len(files) < 96: fails.append(f"BUILD: expected at least 96 pages, got {len(files)}")

NODE = shutil.which("node")
if not NODE: warns.append("node not found — inline JS syntax check skipped")

for f in files:
    src = open(os.path.join(DIST,f), encoding="utf-8").read()
    p = P(); p.feed(src)
    if p.st or p.bad: fails.append(f"HTML {f}: {p.bad[:2] or p.st}")
    # 3. internal links resolve
    for h in {h for h in re.findall(r'href="([^"#?:]+\.html)[^"]*"', src)}:
        if not os.path.exists(os.path.join(DIST,h)):
            fails.append(f"LINK {f}: -> {h} missing")
    # 4. lang/dir correct
    m = re.search(r'<html lang="(\w+)" dir="(\w+)"', src)
    want = ("ar","rtl") if f.endswith("-ar.html") else ("en","ltr")
    if not m or m.groups() != want:
        fails.append(f"LANG {f}: got {m.groups() if m else None}, want {want}")
    # 5. inline JS parses (temp file: portable path, UTF-8 for the Arabic strings)
    if NODE:
        for js in re.findall(r'<script>(.*?)</script>', src, re.S):
            fd, tmp = tempfile.mkstemp(suffix=".js")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as t: t.write(js)
                r = subprocess.run([NODE,"--check",tmp], capture_output=True)
                if r.returncode:
                    fails.append(f"JS {f}: syntax error — "
                                 f"{r.stderr.decode('utf-8','replace').splitlines()[:1]}")
            finally:
                os.unlink(tmp)

for w in warns: print("  ! " + w)
if fails:
    print("\n".join("  ✗ " + x for x in fails)); sys.exit(1)
print(f"  ✓ {len(files)} pages — structure, links, lang/dir, JS, RTL, contrast")
