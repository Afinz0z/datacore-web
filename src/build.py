# -*- coding: utf-8 -*-
import re, os, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from css import CSS
from content import C, PARTNERS, SOCIALS, OFFICE_GEO
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.normpath(os.path.join(HERE, "..", "dist"))
os.makedirs(OUT, exist_ok=True)
PAGES = ["index","about","services","products","projects","insights","contact"]

# ── logo ──────────────────────────────────────────────────────────────────
_svg = open(os.path.join(HERE,"assets","Logo.svg"), encoding="utf-8").read().strip()
_svg = re.sub(r'^<svg ', '<svg role="img" aria-label="Datacore Solutions" ', _svg)
LOGO       = _svg                                  # dark ink, for white header
LOGO_LIGHT = _svg.replace("#1A1B1F", "#FFFFFF")    # white ink, for dark footer

# ── catalogue data ───────────────────────────────────────────────────────
# Swap products.json for a live /api/products fetch when the back end exists.
# Nothing else in this file needs to change.
import json as _json
_D = os.path.join(HERE, "data")
_load = lambda n: _json.load(open(os.path.join(_D, n), encoding="utf-8"))
P_DATA  = "const P = "     + _json.dumps(_load("products.json"), ensure_ascii=False) + ";"
P_GLYPH = "const GLYPH = " + _json.dumps(_load("glyphs.json"),   ensure_ascii=False) + ";"
P_ICO   = ('const ico=(g,s)=>`<svg width="${s}" height="${s}" viewBox="0 0 24 24" '
           'fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
           'stroke-linejoin="round">${GLYPH[g]||GLYPH.switch}</svg>`;\n')

SOC_SVG = {
 "linkedin":'<svg width="19" height="19" viewBox="0 0 24 24" fill="currentColor"><path d="M4.98 '
            '3.5a2.5 2.5 0 11-.02 5 2.5 2.5 0 01.02-5zM3 9h4v12H3zM10 9h3.8v1.7h.05c.53-.95 '
            '1.83-1.95 3.77-1.95 4.03 0 4.78 2.5 4.78 5.75V21h-4v-5.6c0-1.34-.03-3.06-1.9-3.06'
            '-1.9 0-2.2 1.45-2.2 2.96V21h-4z"/></svg>',
 "instagram":'<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
             'stroke-width="1.9"><rect x="3" y="3" width="18" height="18" rx="5"/>'
             '<circle cx="12" cy="12" r="4"/>'
             '<circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>',
 "facebook":'<svg width="19" height="19" viewBox="0 0 24 24" fill="currentColor"><path d="M14 '
            '9h3V6h-3c-2.2 0-4 1.8-4 4v2H8v3h2v7h3v-7h3l1-3h-4v-2c0-.55.45-1 1-1z"/></svg>',
}
def soc_icons(cls=""):
    return "".join(
        f'<a href="{u}" aria-label="Datacore on {n}" rel="noopener me" target="_blank">'
        f'{SOC_SVG[k]}</a>' for k, u, n in SOCIALS)

def soc_buttons():
    return '<div class="socrow">' + "".join(
        f'<a href="{u}" rel="noopener me" target="_blank">{SOC_SVG[k]}<span>{n}</span></a>'
        for k, u, n in SOCIALS) + '</div>'

def maps_embed(idx, l):
    geo, q = OFFICE_GEO[idx]
    return ("https://www.google.com/maps?q=" + (geo or quote(q)) +
            f"&hl={l}&z=16&output=embed")

def maps_link(idx):
    geo, q = OFFICE_GEO[idx]
    return "https://www.google.com/maps/dir/?api=1&destination=" + quote(geo or q)

def url(page, l):
    return f"{page}.html" if l == "en" else f"{page}-ar.html"

def e(s):
    return html.escape(str(s), quote=False)

# ══════════════════════════════════════════════════════════════════════════
#  SHELL
# ══════════════════════════════════════════════════════════════════════════
def head(l, page, title, desc, extra_css=""):
    t = C[l]
    alt = url(page, t['other'])
    return f"""<!DOCTYPE html>
<html lang="{t['lang']}" dir="{t['dir']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="alternate" hreflang="{t['other_lang']}" href="{alt}">
<link rel="alternate" hreflang="{t['lang']}" href="{url(page,l)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{t['font']}&display=swap" rel="stylesheet">
<style>{CSS}{extra_css}</style>
</head>
<body>
<a class="skip" href="#main">{t['skip']}</a>
"""

def header(l, page):
    t = C[l]
    nav = "".join(
        f'<a href="{url(k,l)}"{" aria-current=\"page\"" if k==page or (k=="index" and page=="index") else ""}>{v}</a>'
        for k, v in t['nav'])
    return f"""<header class="hdr">
  <div class="wrap">
    <a class="logo" href="{url('index',l)}" aria-label="Datacore Solutions">{LOGO}</a>
    <nav class="mainnav" aria-label="Main">{nav}</nav>
    <div class="hdr-cta">
      <a class="lang" href="{url(page,t['other'])}" lang="{t['other_lang']}"
         hreflang="{t['other_lang']}">{t['other_label']}</a>
      <a class="btn btn-p" href="{url('contact',l)}">{t['consult']}</a>
      <button class="burger" aria-label="{t['menu']}" aria-expanded="false">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="2"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
      </button>
    </div>
  </div>
</header>
<main id="main">"""

def phead(l, page, title, lede):
    t = C[l]
    crumb = f'<a href="{url("index",l)}">{t["home"]}</a><span>/</span><span>{title}</span>'
    return f"""<section class="phead"><div class="wrap">
  <nav class="crumbs" aria-label="Breadcrumb">{crumb}</nav>
  <h1>{title}</h1><p>{lede}</p>
</div></section>"""

def cta(l):
    t = C[l]
    return f"""<section class="cta"><div class="wrap">
  <div><h2>{t['cta_h']}</h2><p>{t['cta_p']}</p></div>
  <div class="btns">
    <a class="btn btn-p" href="{url('contact',l)}">{t['consult']}</a>
    <a class="btn btn-s" href="/assets1/images/DC COMPANY PROFILE.pdf">{t['profile']}</a>
  </div>
</div></section>"""

def footer(l):
    t = C[l]
    company = "".join(f'<li><a href="{url(k,l)}">{v}</a></li>' for k, v in t['f_links'])
    company += f'<li><a href="/career">{t["f_careers"]}</a></li>'
    svc = "".join(f'<li><a href="{url("services",l)}#{d[0]}">{d[1]}</a></li>'
                  for d in t['disc'][:4])
    svc += f'<li><a href="{url("services",l)}">{t["f_all_disc"]}</a></li>'
    offices = "".join(
        f'<div class="office"><strong>{o[0]}</strong>'
        f'<p>{o[1]}<br>{o[2]}<br>{o[3]}</p>'
        f'<a href="tel:{o[5]}" dir="ltr">{o[4]}</a></div>' for o in t['offices'])
    return f"""</main>
<footer class="ftr"><div class="wrap">
  <div class="ftr-top">
    <div>
      <div class="logo">{LOGO_LIGHT}</div>
      <p style="margin-top:16px;max-width:38ch;color:#9AA3A8;font-size:.9375rem">{t['brand_line']}</p>
    </div>
    <div><h4>{t['f_company']}</h4><ul>{company}</ul></div>
    <div><h4>{t['f_services']}</h4><ul>{svc}</ul></div>
    <div><h4>{t['f_touch']}</h4><ul>
      <li><a href="{url('products',l)}">{t['f_catalogue']}</a></li>
      <li><a href="{url('contact',l)}">{t['get_quote']}</a></li>
      <li><a href="mailto:sales@datacore.com.sa" dir="ltr">sales@datacore.com.sa</a></li>
      <li><a href="mailto:careers@datacore.com.sa" dir="ltr">careers@datacore.com.sa</a></li>
      <li><a href="https://wa.me/966115128888">{t['f_whatsapp']}</a></li>
    </ul></div>
  </div>
  <div class="offices">{offices}</div>
  <div class="ftr-btm">
    <span>{t['f_rights']}</span>
    <a href="/terms-service">{t['f_terms']}</a>
    <a href="/privacy-policy">{t['f_privacy']}</a>
    <span class="legal">{t['f_legal']}</span>
    <div class="soc">{soc_icons()}
    </div>
  </div>
</div></footer>
<script>
const b=document.querySelector('.burger'),n=document.querySelector('.mainnav');
b&&b.addEventListener('click',()=>{{
  const o=b.getAttribute('aria-expanded')==='true';
  b.setAttribute('aria-expanded',String(!o));
  n.style.cssText=o?'':'display:flex;flex-direction:column;position:absolute;top:76px;'+
    'inset-inline:0;background:#fff;border-bottom:1px solid var(--line);'+
    'padding:20px var(--gutter);gap:4px;margin:0';
}});
</script>
</body></html>"""

# ── shared blocks ─────────────────────────────────────────────────────────
def disc_cards(l):
    t = C[l]
    out = []
    for slug, name, subs, std, _ in t['disc']:
        lis = "".join(f"<li>{s}</li>" for s in subs)
        out.append(f'<article id="{slug}"><h3><a href="{url("services",l)}#{slug}">{name}</a>'
                   f'</h3><ul>{lis}</ul><p class="mono std" dir="ltr">{std}</p></article>')
    return '<div class="disc">' + "".join(out) + '</div>'

def proj_cards(l):
    t = C[l]
    out = []
    for sector, city, title, body, kit, client, scope in t['proj']:
        k = "".join(f'<a href="{url("products",l)}">{x}</a>' for x in kit)
        out.append(f"""<article class="proj">
  <div class="band"><span>{sector}</span><span>{city}</span></div>
  <div class="in"><h3>{title}</h3><p>{body}</p>
    <div class="kit">{k}</div>
    <dl><dt>{t['p_client']}</dt><dd>{client}</dd>
        <dt>{t['p_scope']}</dt><dd>{scope}</dd></dl>
  </div></article>""")
    return '<div class="projs">' + "".join(out) + '</div>'

def partners_grid():
    return '<div class="partners">' + "".join(f"<span>{p}</span>" for p in PARTNERS) + '</div>'

def timeline(l):
    return '<div class="tl">' + "".join(
        f'<article><time datetime="{y}">{y}</time><h3>{h}</h3><p>{p}</p></article>'
        for y, h, p in C[l]['tl']) + '</div>'

def posts(l, large_first=False):
    t = C[l]
    out = []
    for i, (date, by, title, body) in enumerate(t['posts']):
        cls = "post post-lg" if (large_first and i == 0) else "post"
        inner = (f'<div><span class="by">{date} · {by}</span><h3><a href="/blog">{title}</a></h3></div>'
                 f'<p>{body}</p>') if (large_first and i == 0) else \
                (f'<span class="by">{date} · {by}</span><h3><a href="/blog">{title}</a></h3>'
                 f'<p>{body}</p>')
        out.append(f'<article class="{cls}">{inner}</article>')
    return '<div class="posts">' + "".join(out) + '</div>'

# ══════════════════════════════════════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════════════════════════════════════
def page_index(l):
    t = C[l]
    stack = "".join(
        f'<a href="{url("services",l)}#{d[0]}" style="animation-delay:{.05*(i+1):.2f}s">'
        f'<span class="n">{i+1:02d}</span><span>{d[1]}</span>'
        f'<span class="c">{len(d[2])}</span></a>'
        for i, d in enumerate(t['disc']))
    stats = "".join(f'<div class="stat"><i></i><b dir="ltr">{n}</b><span>{s}</span></div>'
                    for n, s in t['stats'])
    return f"""<section class="hero"><div class="wrap">
  <div>
    <span class="eyebrow">{t['h_eyebrow']}</span>
    <h1>{t['h_title']}</h1>
    <p class="lede">{t['h_lede']}</p>
    <div class="hero-cta">
      <a class="btn btn-p" href="{url('contact',l)}">{t['consult']}</a>
      <a class="btn btn-s" href="{url('projects',l)}">{t['see_projects']}</a>
    </div>
  </div>
  <div class="stack">
    <header><strong>{t['h_stack']}</strong><span class="mono">{t['h_scope']}</span></header>
    {stack}
  </div>
</div></section>

<section class="stats" aria-label="{t['h_stack']}"><div class="wrap">{stats}</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head split"><h2>{t['h_disc_title']}</h2><p>{t['h_disc_lede']}</p></div>
  {disc_cards(l)}
</div></section>

<section class="sec sec-alt"><div class="wrap">
  <div class="sec-head split"><h2>{t['h_proj_title']}</h2><p>{t['h_proj_lede']}</p></div>
  {proj_cards(l)}
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><h2>{t['h_tl_title']}</h2><p>{t['h_tl_lede']}</p></div>
  {timeline(l)}
</div></section>

<section class="sec sec-alt"><div class="wrap">
  <div class="sec-head"><h2>{t['h_part_title']}</h2><p>{t['h_part_lede']}</p></div>
  {partners_grid()}
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head split"><h2>{t['h_ins_title']}</h2><p>{t['h_ins_lede']}</p></div>
  {posts(l)}
</div></section>
{cta(l)}"""

def page_about(l):
    t = C[l]
    story = "".join(f"<p style='margin-bottom:var(--s2)'>{p}</p>" for p in t['a_story'])
    vals = "".join(f'<div class="val"><span class="n">{i+1:02d}</span><h3>{h}</h3><p>{p}</p></div>'
                   for i, (h, p) in enumerate(t['a_vals']))
    stats = "".join(f'<div class="stat"><i></i><b dir="ltr">{n}</b><span>{s}</span></div>'
                    for n, s in t['stats'])
    return f"""{phead(l,'about',t['a_title'],t['a_lede'])}
<section class="stats"><div class="wrap">{stats}</div></section>
<section class="sec"><div class="wrap">
  <div class="sec-head split">
    <h2>{t['a_story_h']}</h2>
    <div style="color:var(--ink-2);font-size:1.0625rem">{story}</div>
  </div>
  {timeline(l)}
</div></section>
<section class="sec sec-alt"><div class="wrap">
  <div class="sec-head"><h2>{t['a_vals_h']}</h2></div>
  <div class="vals">{vals}</div>
</div></section>
<section class="sec"><div class="wrap">
  <div class="sec-head split"><h2>{t['a_where_h']}</h2><p>{t['a_where']}</p></div>
  {partners_grid()}
</div></section>
{cta(l)}"""

def page_services(l):
    t = C[l]
    chips = f'<a class="on" href="#">{t["s_all"]}</a>' + "".join(
        f'<a href="#{d[0]}">{d[1]}</a>' for d in t['disc'])
    cats = []
    for i, (slug, name, subs, std, blurb) in enumerate(t['disc']):
        cards = "".join(
            f'<article class="svc"><h3><a href="/service-details/{j}">{s}</a></h3>'
            f'<p>{t["svc_blurbs"].get(s,"")}</p>'
            f'<a class="more" href="/service-details/{j}">{t["read"]} →</a></article>'
            for j, s in enumerate(subs))
        cats.append(f"""<section class="cat" id="{slug}">
  <div class="cat-head">
    <div><span class="num">{i+1:02d} — {len(subs)}</span><h2>{name}</h2></div>
    <div><p>{blurb}</p><p class="mono" style="margin-top:14px" dir="ltr">{std}</p></div>
  </div>
  <div class="svcs">{cards}</div>
</section>""")
    return f"""{phead(l,'services',t['s_title'],t['s_lede'])}
<div class="wrap"><div class="filters">{chips}</div>{"".join(cats)}</div>
{cta(l)}"""

def page_projects(l):
    t = C[l]
    feats = "".join(f'<div class="val"><span class="n">{i+1:02d}</span><h3>{h}</h3><p>{p}</p></div>'
                    for i, (h, p) in enumerate(t['pj_feat']))
    sectors = sorted({p[0] for p in t['proj']})
    chips = f'<a class="on" href="#">{t["s_all"]}</a>' + "".join(
        f'<a href="#">{s}</a>' for s in sectors)
    return f"""{phead(l,'projects',t['pj_title'],t['pj_lede'])}
<section class="sec"><div class="wrap">
  <div class="filters" style="margin-bottom:var(--s4)">{chips}</div>
  {proj_cards(l)}
</div></section>
<section class="sec sec-alt"><div class="wrap">
  <div class="sec-head"><h2>{t['pj_feat_h']}</h2></div>
  <div class="vals">{feats}</div>
</div></section>
{cta(l)}"""

def page_insights(l):
    t = C[l]
    return f"""{phead(l,'insights',t['i_title'],t['i_lede'])}
<section class="sec"><div class="wrap">{posts(l, large_first=True)}</div></section>
{cta(l)}"""

def page_contact(l):
    import json
    t = C[l]
    f = t['c_f']
    title_js = json.dumps(t['map_h'], ensure_ascii=False)
    opts = "".join(f"<option>{o}</option>" for o in t['c_types'])
    offices = "".join(f"""<div class="office-card"><h3>{o[0]}</h3>
      <p>{o[1]}<br>{o[2]}<br>{o[3]}</p>
      <div class="rows"><a href="tel:{o[5]}" dir="ltr">{o[4]}</a></div>
      <a class="dirlink" href="{maps_link(i)}" rel="noopener" target="_blank">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          stroke-width="1.8"><path d="M12 21s7-6.3 7-11a7 7 0 10-14 0c0 4.7 7 11 7 11z"/>
          <circle cx="12" cy="10" r="2.6"/></svg>{t['directions']} →</a>
      </div>""" for i, o in enumerate(t['offices']))
    return f"""{phead(l,'contact',t['c_title'],t['c_lede'])}
<section class="sec"><div class="wrap"><div class="contact-grid">
  <div>
    <div class="sec-head" style="margin-bottom:var(--s3)"><h2>{t['c_offices_h']}</h2></div>
    <div class="offices-grid">{offices}</div>
    <div class="sec-head" style="margin:var(--s4) 0 var(--s2)"><h2>{t['c_other_h']}</h2></div>
    <div class="office-card"><div class="rows">
      <a href="mailto:sales@datacore.com.sa" dir="ltr">sales@datacore.com.sa</a>
      <a href="mailto:info@datacore.com.sa" dir="ltr">info@datacore.com.sa</a>
      <a href="mailto:careers@datacore.com.sa" dir="ltr">careers@datacore.com.sa</a>
      <a href="https://wa.me/966115128888">{t['f_whatsapp']}</a>
    </div></div>

    <div class="sec-head" style="margin:var(--s4) 0 var(--s2)"><h2>{t['follow_h']}</h2></div>
    <p style="color:var(--ink-2)">{t['follow_p']}</p>
    {soc_buttons()}
  </div>
  <div>
    <form class="form" onsubmit="return false">
      <div class="sec-head" style="margin-bottom:var(--s3)"><h2>{t['c_form_h']}</h2></div>
      <div class="two">
        <div class="field"><label for="cn">{f['name']}</label><input id="cn" required></div>
        <div class="field"><label for="cc">{f['company']}</label><input id="cc"></div>
      </div>
      <div class="two">
        <div class="field"><label for="ce">{f['email']}</label>
          <input id="ce" type="email" dir="ltr" required></div>
        <div class="field"><label for="cp">{f['phone']}</label>
          <input id="cp" type="tel" dir="ltr" placeholder="+966"></div>
      </div>
      <div class="field"><label for="ct">{f['type']}</label>
        <select id="ct">{opts}</select></div>
      <div class="field"><label for="cj">{f['project']}
        <span class="hint">— {f['project_hint']}</span></label><input id="cj"></div>
      <div class="field"><label for="cm">{f['msg']}</label>
        <textarea id="cm" rows="5"></textarea></div>
      <button class="btn btn-p" type="submit">{f['send']}</button>
      <p class="formnote">{f['note']}</p>
    </form>
  </div>
</div>

<div class="sec-head" style="margin:var(--s6) 0 var(--s3)"><h2>{t['map_h']}</h2></div>
<div class="map" id="map" data-src="{maps_embed(0,l)}">
  <button class="map-face" id="mapFace" aria-label="{t['map_load']}">
    <span class="pin"><svg width="17" height="17" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" stroke-width="2"><path d="M12 21s7-6.3 7-11a7 7 0 10-14 0c0 4.7 7 11 7 11z"/>
      <circle cx="12" cy="10" r="2.6"/></svg></span>
    <strong>{t['offices'][0][1]} — {t['offices'][0][3]}</strong>
    <span>{t['map_note']}</span>
    <span class="btn btn-s" aria-hidden="true">{t['map_load']}</span>
  </button>
</div>
<p class="map-cap">{t['offices'][0][2]}, {t['offices'][0][3]} ·
  <a href="{maps_link(0)}" rel="noopener" target="_blank">{t['directions']}</a></p>
</div></section>
<script>
/* Map facade: nothing loads from Google until the visitor asks for it.
   Keeps the embed off the critical path and out of pre-consent cookies. */
const mf=document.getElementById('mapFace'),mw=document.getElementById('map');
mf&&mf.addEventListener('click',()=>{{
  const f=document.createElement('iframe');
  f.src=mw.dataset.src; f.loading='lazy'; f.title={title_js};
  f.referrerPolicy='no-referrer-when-downgrade';
  f.allowFullscreen=true; mw.innerHTML=''; mw.appendChild(f);
}});
</script>"""

# ── products page (catalogue) ─────────────────────────────────────────────
PROD_CSS = """
.cat-shell{display:grid;grid-template-columns:250px minmax(0,1fr);gap:var(--s4);
  align-items:start;padding-block:var(--s4) var(--s6)}
.facets{position:sticky;top:96px}
.fgroup{border-bottom:1px solid var(--line);padding:14px 0}
.fgroup:first-child{padding-top:0}
.fgroup>h3{margin:0 0 9px;font-size:.8125rem;font-weight:600;color:var(--ink-2);
  display:flex;justify-content:space-between;align-items:center}
.fgroup label{display:flex;align-items:center;gap:9px;padding:3px 0;font-size:.875rem;cursor:pointer}
.fgroup input{accent-color:var(--accent);width:15px;height:15px;flex:none}
.fgroup label span:last-child{margin-inline-start:auto;color:var(--ink-3);font-size:.75rem}
.fgroup label.off{opacity:.38}
.clear-all,.more{font-size:.8125rem;color:var(--accent);text-decoration:underline;padding:0}
.bar{display:flex;align-items:center;gap:12px;margin-bottom:14px;flex-wrap:wrap}
.count{font-size:.875rem;color:var(--ink-2)}
.count b{color:var(--ink)}
.bar-r{margin-inline-start:auto;display:flex;gap:8px;align-items:center}
select.sort{border:1px solid var(--line-2);background:var(--surface);border-radius:2px;
  padding:7px 10px;font-size:.875rem}
.vtog{display:flex;border:1px solid var(--line-2);border-radius:2px;overflow:hidden;
  background:var(--surface)}
.vtog button{padding:7px 10px;display:flex;color:var(--ink-2)}
.vtog button[aria-pressed=true]{background:var(--ink);color:#fff}
.chips{display:flex;gap:7px;flex-wrap:wrap;width:100%}
.chip{background:var(--surface);border:1px solid var(--line-2);border-radius:20px;
  padding:3px 8px 3px 11px;font-size:.8125rem;display:flex;align-items:center;gap:6px}
.pgrid{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(255px,1fr))}
.plist{display:flex;flex-direction:column;gap:9px}
.pcard{background:var(--surface);border:1px solid var(--line);border-radius:2px;
  display:flex;flex-direction:column;overflow:hidden}
.pcard:hover{border-color:var(--line-2)}
.pcard .thumb{background:var(--paper);height:132px;display:flex;align-items:center;
  justify-content:center;border-bottom:1px solid var(--line);cursor:pointer;color:#8A9299}
.pcard .body{padding:12px;display:flex;flex-direction:column;gap:7px;flex:1}
.pmeta{font-size:.75rem;color:var(--ink-2);display:flex;gap:6px}
.pmeta b{color:var(--ink);font-weight:600}
.pcard h4{margin:0;font-size:.9375rem;font-weight:500;line-height:1.35;cursor:pointer}
.pcard h4:hover{color:var(--accent)}
.sku{font-family:'IBM Plex Mono',monospace;font-size:.8125rem;direction:ltr;text-align:start}
.specs{display:flex;flex-wrap:wrap;gap:5px}
.spec{background:var(--paper);border:1px solid var(--line);border-radius:2px;
  padding:2px 6px;font-size:.75rem;color:var(--ink-2)}
.stock{font-size:.8125rem;display:flex;align-items:center;gap:6px;margin-top:auto}
.stock i{width:7px;height:7px;border-radius:50%;background:var(--brand);flex:none}
.stock.lead i{background:var(--amber)}.stock.lead{color:var(--amber)}
.add{display:flex;gap:7px;padding:0 12px 12px}
.add input{width:56px;border:1px solid var(--line-2);border-radius:2px;padding:7px 8px;
  text-align:center;direction:ltr}
.add button{flex:1;background:var(--ink);color:#fff;border-radius:2px;padding:7px 10px;
  font-size:.875rem;font-weight:500}
.add button:hover{background:var(--accent-d)}
.add button.in{background:var(--accent)}
.prow{background:var(--surface);border:1px solid var(--line);border-radius:2px;display:grid;
  grid-template-columns:56px minmax(0,2.2fr) minmax(0,1.6fr) 140px 150px;gap:14px;
  align-items:center;padding:10px 12px}
.prow .thumb{height:44px;background:var(--paper);border:1px solid var(--line);border-radius:2px;
  display:flex;align-items:center;justify-content:center;color:#8A9299;cursor:pointer}
.prow h4{margin:0;font-size:.9375rem;font-weight:500;cursor:pointer}
.prow .add{padding:0}
.empty{background:var(--surface);border:1px dashed var(--line-2);border-radius:2px;
  padding:44px 24px;text-align:center}
.loadmore{margin:18px auto 0;display:block;border:1px solid var(--line-2);
  background:var(--surface);border-radius:2px;padding:10px 26px;font-weight:500}
.scrim{position:fixed;inset:0;background:rgba(26,27,31,.42);z-index:60;opacity:0;
  pointer-events:none;transition:opacity .2s}
.scrim.on{opacity:1;pointer-events:auto}
.drawer{position:fixed;top:0;bottom:0;inset-inline-end:0;width:min(470px,100%);
  background:var(--surface);z-index:61;display:flex;flex-direction:column;
  transform:translateX(102%);transition:transform .24s cubic-bezier(.3,.7,.3,1)}
html[dir=rtl] .drawer{transform:translateX(-102%)}
.drawer.on{transform:none}
.drawer>header{padding:16px 20px;border-bottom:1px solid var(--line);display:flex;
  align-items:center;gap:12px}
.drawer>header h2{margin:0;font-size:1.0625rem;font-weight:600}
.drawer>header button{margin-inline-start:auto;font-size:1.5rem;line-height:1;color:var(--ink-2)}
.dbody{overflow-y:auto;flex:1;padding:20px}
.dfoot{border-top:1px solid var(--line);padding:16px 20px;background:var(--paper)}
.pd-hero{background:var(--paper);border:1px solid var(--line);height:190px;display:flex;
  align-items:center;justify-content:center;color:#8A9299;margin-bottom:16px}
.stable{width:100%;border-collapse:collapse;margin-top:16px;font-size:.875rem}
.stable th{text-align:start;font-weight:500;color:var(--ink-2);padding:8px 0;
  border-bottom:1px solid var(--line);width:44%;vertical-align:top}
.stable td{padding:8px 0;border-bottom:1px solid var(--line)}
.line{display:grid;grid-template-columns:1fr auto;gap:4px 12px;padding:14px 0;
  border-bottom:1px solid var(--line)}
.line h5{margin:0;font-size:.9375rem;font-weight:500}
.line .lmeta{color:var(--ink-2);font-size:.8125rem}
.line .lctl{grid-column:2;grid-row:1/3;display:flex;flex-direction:column;align-items:end;gap:7px}
.line .lctl input{width:62px;border:1px solid var(--line-2);border-radius:2px;padding:6px;
  text-align:center;direction:ltr}
.line .lctl button{font-size:.8125rem;color:var(--ink-2);text-decoration:underline}
.line textarea{grid-column:1/-1;width:100%;border:1px solid var(--line-2);border-radius:2px;
  padding:7px 9px;font-size:.8125rem;min-height:34px;margin-top:6px}
.payload{background:var(--ink);color:#9FE6D6;border-radius:2px;padding:14px;
  font-family:'IBM Plex Mono',monospace;font-size:.75rem;line-height:1.6;overflow-x:auto;
  white-space:pre;margin-top:14px;direction:ltr;text-align:start}
.toast{position:fixed;inset-inline-end:20px;bottom:20px;background:var(--ink);color:#fff;
  padding:12px 18px;border-radius:2px;z-index:70;font-size:.875rem;transform:translateY(140%);
  transition:transform .22s;display:flex;gap:10px;align-items:center}
.toast.on{transform:none}
.toast i{width:7px;height:7px;border-radius:50%;background:var(--brand)}
.psearch{position:relative;max-width:620px;margin-top:var(--s3)}
.psearch input{width:100%;padding:12px 40px;border:1px solid var(--line-2);border-radius:2px;
  background:var(--surface)}
.psearch svg{position:absolute;inset-inline-start:13px;top:13px;color:var(--ink-3)}
.mobfilter{display:none}
@media(max-width:1080px){.prow{grid-template-columns:56px minmax(0,1fr) 150px}
  .prow .rspecs,.prow .rstock{display:none}}
@media(max-width:900px){
  .cat-shell{grid-template-columns:1fr}
  .facets{position:static;display:none;background:var(--surface);border:1px solid var(--line);
    padding:14px}
  .facets.on{display:block}
  .mobfilter{display:inline-flex;gap:8px;align-items:center;border:1px solid var(--line-2);
    background:var(--surface);border-radius:2px;padding:7px 13px;font-size:.875rem}
}
"""

PROD_STR = {
 'en':{'refine':'Refine','clear':'Clear all','f_cat':'Category','f_brand':'Brand',
   'f_avail':'Availability','in_stock':'In stock','on_order':'On order','lead_time':'Lead time',
   'days':'days','product':'product','products':'products','add':'Add to request',
   'added':'Added','loadmore':'Load more','details':'Product details',
   'datasheet':'Download datasheet (PDF)','rfq_title':'Your request',
   'rfq_empty_h':'Nothing added yet',
   'rfq_empty_p':'Browse the catalogue and add the parts you need. You can adjust quantities '
                 'before sending.',
   'remove':'Remove','ph_note':'Note for this line — variant, colour, mounting…',
   'f_name':'Your name','f_company':'Company','f_email':'Email','f_phone':'Phone',
   'f_project':'Project','ph_project':'e.g. Riyadh HQ — Level 3 fit-out','f_msg':'Anything else',
   'send':'Send request','units':'units',
   'send_note':"You'll get an acknowledgement immediately and a priced quotation within one "
               "working day.",
   'empty_h':'No products match those filters',
   'empty_p':'Try removing a filter or searching a part number.',
   'toast_added':'added to your request','filters':'Filters','rfq':'Request for quote',
   'ph_search':'Search by part number, brand or description','received':'Request received',
   'received_p':'Reference RFQ-2026-0417. Sales will come back to you within one working day.',
   'posts_to':'This is what posts to POST /api/rfq in the real build:',
   's_rel':'Sort: relevance','s_az':'Name A–Z','s_brand':'Brand','s_avail':'In stock first'},
 'ar':{'refine':'تصفية','clear':'مسح الكل','f_cat':'الفئة','f_brand':'العلامة التجارية',
   'f_avail':'التوفر','in_stock':'متوفر','on_order':'تحت الطلب','lead_time':'مدة التوريد',
   'days':'يوم','product':'منتج','products':'منتج','add':'أضف إلى الطلب','added':'تمت الإضافة',
   'loadmore':'عرض المزيد','details':'تفاصيل المنتج','datasheet':'تحميل ورقة البيانات (PDF)',
   'rfq_title':'طلبك','rfq_empty_h':'لم تتم إضافة أي شيء بعد',
   'rfq_empty_p':'تصفح الكتالوج وأضف القطع التي تحتاجها. يمكنك تعديل الكميات قبل الإرسال.',
   'remove':'إزالة','ph_note':'ملاحظة لهذا البند — الطراز، اللون، طريقة التركيب…',
   'f_name':'الاسم','f_company':'الشركة','f_email':'البريد الإلكتروني','f_phone':'رقم الجوال',
   'f_project':'المشروع','ph_project':'مثال: المقر الرئيسي بالرياض — الدور الثالث',
   'f_msg':'ملاحظات إضافية','send':'إرسال الطلب','units':'وحدة',
   'send_note':'ستصلك رسالة تأكيد فوراً وعرض سعر خلال يوم عمل واحد.',
   'empty_h':'لا توجد منتجات مطابقة','empty_p':'جرب إزالة أحد عوامل التصفية أو البحث برقم القطعة.',
   'toast_added':'أُضيف إلى طلبك','filters':'عوامل التصفية','rfq':'طلب عرض سعر',
   'ph_search':'ابحث برقم القطعة أو العلامة التجارية أو الوصف','received':'تم استلام طلبك',
   'received_p':'رقم الطلب RFQ-2026-0417. سيتواصل معك فريق المبيعات خلال يوم عمل واحد.',
   'posts_to':'هذا ما يُرسل إلى POST /api/rfq في النسخة النهائية:',
   's_rel':'الترتيب: الأنسب','s_az':'الاسم أ–ي','s_brand':'العلامة التجارية',
   's_avail':'المتوفر أولاً'},
}

def page_products(l):
    t = C[l]
    s = PROD_STR[l]
    import json
    return f"""<section class="phead"><div class="wrap">
  <nav class="crumbs"><a href="{url('index',l)}">{t['home']}</a><span>/</span>
    <span>{t['pr_title']}</span></nav>
  <h1>{t['pr_title']}</h1><p>{t['pr_lede']}</p>
  <div class="psearch">
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      stroke-width="2.2"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>
    <input id="q" type="search" placeholder="{s['ph_search']}" autocomplete="off"
      aria-label="{s['ph_search']}">
  </div>
</div></section>

<div class="wrap"><div class="cat-shell">
  <aside class="facets" id="facets"></aside>
  <div>
    <div class="bar">
      <button class="mobfilter" id="mobFilter">{s['filters']}</button>
      <span class="count" id="count"></span>
      <div class="bar-r">
        <button class="btn btn-p" id="openRfq">{s['rfq']} <b id="rfqCount">0</b></button>
        <select class="sort" id="sort" aria-label="Sort">
          <option value="rel">{s['s_rel']}</option><option value="az">{s['s_az']}</option>
          <option value="brand">{s['s_brand']}</option><option value="avail">{s['s_avail']}</option>
        </select>
        <div class="vtog">
          <button id="vGrid" aria-pressed="true" aria-label="Grid">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
            <rect x="3" y="3" width="8" height="8" rx="1"/><rect x="13" y="3" width="8" height="8" rx="1"/>
            <rect x="3" y="13" width="8" height="8" rx="1"/><rect x="13" y="13" width="8" height="8" rx="1"/></svg></button>
          <button id="vList" aria-pressed="false" aria-label="List">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            stroke-width="2.2"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button>
        </div>
      </div>
      <div class="chips" id="chips"></div>
    </div>
    <div id="results"></div>
    <button class="loadmore" id="loadmore" hidden>{s['loadmore']}</button>
  </div>
</div></div>

<div class="scrim" id="scrim"></div>
<aside class="drawer" id="pdDrawer" aria-hidden="true">
  <header><h2>{s['details']}</h2><button class="x" aria-label="Close">&times;</button></header>
  <div class="dbody" id="pdBody"></div><div class="dfoot" id="pdFoot"></div>
</aside>
<aside class="drawer" id="rfqDrawer" aria-hidden="true">
  <header><h2>{s['rfq_title']}</h2><button class="x" aria-label="Close">&times;</button></header>
  <div class="dbody" id="rfqBody"></div><div class="dfoot" id="rfqFoot"></div>
</aside>
<div class="toast" id="toast"><i></i><span id="toastMsg"></span></div>

<script>
{P_DATA}
{P_GLYPH}
{P_ICO}
const SPEC_FACETS=["PoE","Resolution","Type","Category","Rack","Standard"];
const S={{q:"",cat:[],brand:[],avail:[],spec:{{}},sort:"rel",view:"grid",shown:12,rfq:[]}};
const L={json.dumps(s, ensure_ascii=False)};
const T=k=>L[k]||k, PAGE=12, $=q=>document.querySelector(q);
const esc=x=>String(x).replace(/[&<>"]/g,c=>({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}}[c]));

function match(p,skip){{
  if(S.q){{const t=(p.sku+" "+p.n+" "+p.b+" "+p.c).toLowerCase();
    if(!S.q.toLowerCase().split(/\\s+/).every(w=>t.includes(w)))return false;}}
  if(skip!=="cat"&&S.cat.length&&!S.cat.includes(p.c))return false;
  if(skip!=="brand"&&S.brand.length&&!S.brand.includes(p.b))return false;
  if(skip!=="avail"&&S.avail.length&&!S.avail.includes(p.avail))return false;
  for(const k in S.spec){{if(skip==="spec:"+k)continue;
    if(S.spec[k].length&&!S.spec[k].includes(p.specs[k]))return false;}}
  return true;
}}
const results=()=>{{let r=P.filter(p=>match(p,null));
  if(S.sort==="az")r.sort((a,b)=>a.n.localeCompare(b.n));
  if(S.sort==="brand")r.sort((a,b)=>a.b.localeCompare(b.b)||a.n.localeCompare(b.n));
  if(S.sort==="avail")r.sort((a,b)=>(a.avail==="stock"?0:1)-(b.avail==="stock"?0:1));
  return r;}};
function tally(dim,get){{const m={{}};P.filter(p=>match(p,dim)).forEach(p=>{{
  const v=get(p); if(v!=null)m[v]=(m[v]||0)+1;}}); return m;}}
function fgroup(title,dim,counts,selected,limit){{
  const all=[...new Set([...Object.keys(counts),...selected])].sort();
  const open=all.length<=(limit||7)||S["_m_"+dim], list=open?all:all.slice(0,limit||7);
  let h=`<div class="fgroup"><h3>${{esc(title)}}</h3>`;
  list.forEach(v=>{{const c=counts[v]||0,on=selected.includes(v);
    h+=`<label class="${{c===0&&!on?"off":""}}"><input type="checkbox" data-dim="${{esc(dim)}}"
      value="${{esc(v)}}" ${{on?"checked":""}}><span>${{esc(v)}}</span><span>${{c}}</span></label>`;}});
  if(all.length>list.length)h+=`<button class="more" data-more="${{esc(dim)}}">+${{all.length-list.length}}</button>`;
  return h+`</div>`;}}
function renderFacets(){{
  const n=S.cat.length+S.brand.length+S.avail.length+Object.values(S.spec).flat().length;
  let h=`<div class="fgroup"><h3><span>${{T("refine")}}</span>${{n?`<button class="clear-all"
    id="clearAll">${{T("clear")}}</button>`:""}}</h3></div>`;
  h+=fgroup(T("f_cat"),"cat",tally("cat",p=>p.c),S.cat,9);
  h+=fgroup(T("f_brand"),"brand",tally("brand",p=>p.b),S.brand,7);
  h+=fgroup(T("f_avail"),"avail",tally("avail",p=>p.avail==="stock"?T("in_stock"):T("on_order")),
      S.avail.map(v=>v==="stock"?T("in_stock"):T("on_order")),4);
  SPEC_FACETS.forEach(k=>{{const c=tally("spec:"+k,p=>p.specs[k]);
    if(Object.keys(c).length>1)h+=fgroup(k,"spec:"+k,c,S.spec[k]||[],6);}});
  $("#facets").innerHTML=h;}}
const stockHtml=p=>p.avail==="stock"?`<div class="stock"><i></i>${{T("in_stock")}}</div>`
  :`<div class="stock lead"><i></i>${{T("lead_time")}} ${{p.lead}} ${{T("days")}}</div>`;
function addHtml(p){{const c=S.rfq.find(l=>l.sku===p.sku);
  return `<div class="add"><input type="number" min="1" value="${{c?c.qty:1}}"
    aria-label="Qty" data-qty="${{esc(p.sku)}}"><button data-add="${{esc(p.sku)}}"
    class="${{c?"in":""}}">${{c?T("added"):T("add")}}</button></div>`;}}
const chipsOf=p=>Object.entries(p.specs).slice(0,3).map(([k,v])=>
  `<span class="spec">${{esc(v)}}</span>`).join("");
function renderResults(){{
  const r=results(),sl=r.slice(0,S.shown);
  $("#count").innerHTML=`<b>${{r.length}}</b> ${{r.length===1?T("product"):T("products")}}`;
  const ch=[];S.cat.forEach(v=>ch.push(["cat",v]));S.brand.forEach(v=>ch.push(["brand",v]));
  S.avail.forEach(v=>ch.push(["avail",v==="stock"?T("in_stock"):T("on_order")]));
  Object.entries(S.spec).forEach(([k,vs])=>vs.forEach(v=>ch.push(["spec:"+k,v])));
  $("#chips").innerHTML=ch.map(([d,v])=>`<span class="chip">${{esc(v)}}<button
    data-chip="${{esc(d)}}" data-val="${{esc(v)}}" aria-label="Remove">&times;</button></span>`).join("");
  if(!r.length){{$("#results").innerHTML=`<div class="empty"><h3>${{T("empty_h")}}</h3>
    <p style="color:var(--ink-2);margin:6px 0 16px">${{T("empty_p")}}</p>
    <button class="loadmore" id="clearAll2">${{T("clear")}}</button></div>`;
    $("#loadmore").hidden=true;return;}}
  if(S.view==="grid"){{$("#results").className="pgrid";
    $("#results").innerHTML=sl.map(p=>`<article class="pcard">
      <div class="thumb" data-open="${{esc(p.sku)}}">${{ico(p.g,46)}}</div>
      <div class="body"><div class="pmeta"><b>${{esc(p.b)}}</b><span>·</span><span>${{esc(p.c)}}</span></div>
      <h4 data-open="${{esc(p.sku)}}">${{esc(p.n)}}</h4><div class="sku">${{esc(p.sku)}}</div>
      <div class="specs">${{chipsOf(p)}}</div>${{stockHtml(p)}}</div>${{addHtml(p)}}</article>`).join("");
  }}else{{$("#results").className="plist";
    $("#results").innerHTML=sl.map(p=>`<article class="prow">
      <div class="thumb" data-open="${{esc(p.sku)}}">${{ico(p.g,24)}}</div>
      <div><h4 data-open="${{esc(p.sku)}}">${{esc(p.n)}}</h4><div class="pmeta"><b>${{esc(p.b)}}</b>
        <span>·</span><span class="sku">${{esc(p.sku)}}</span></div></div>
      <div class="specs rspecs">${{chipsOf(p)}}</div><div class="rstock">${{stockHtml(p)}}</div>
      ${{addHtml(p)}}</article>`).join("");}}
  $("#loadmore").hidden=r.length<=S.shown;}}
const renderCount=()=>$("#rfqCount").textContent=S.rfq.reduce((a,l)=>a+l.qty,0);
const render=()=>{{renderFacets();renderResults();renderCount();}};
function openProduct(sku){{const p=P.find(x=>x.sku===sku);if(!p)return;
  $("#pdBody").innerHTML=`<div class="pd-hero">${{ico(p.g,74)}}</div>
    <div class="pmeta"><b>${{esc(p.b)}}</b><span>·</span><span>${{esc(p.c)}}</span></div>
    <h3 style="margin:6px 0 4px;font-size:1.1875rem">${{esc(p.n)}}</h3>
    <div class="sku">${{esc(p.sku)}}</div>${{stockHtml(p)}}
    <table class="stable">${{Object.entries(p.specs).map(([k,v])=>
      `<tr><th>${{esc(k)}}</th><td>${{esc(v)}}</td></tr>`).join("")}}</table>
    <a href="#" onclick="return false" style="display:inline-block;margin-top:16px">${{T("datasheet")}}</a>`;
  $("#pdFoot").innerHTML=addHtml(p);show("#pdDrawer");}}
function addToRfq(sku,qty){{const l=S.rfq.find(x=>x.sku===sku);
  if(l)l.qty=qty;else S.rfq.push({{sku,qty,note:""}});
  toast(`${{sku}} — ${{T("toast_added")}}`);render();
  if($("#rfqDrawer").classList.contains("on"))renderRfq();}}
function renderRfq(){{
  if(!S.rfq.length){{$("#rfqBody").innerHTML=`<div class="empty"><h3>${{T("rfq_empty_h")}}</h3>
    <p style="color:var(--ink-2);margin-top:6px">${{T("rfq_empty_p")}}</p></div>`;
    $("#rfqFoot").innerHTML=`<button class="btn btn-p" style="width:100%;justify-content:center"
      disabled>${{T("send")}}</button>`;return;}}
  $("#rfqBody").innerHTML=S.rfq.map(l=>{{const p=P.find(x=>x.sku===l.sku);
    return `<div class="line"><h5>${{esc(p.n)}}</h5>
      <div class="lmeta"><span class="sku">${{esc(p.sku)}}</span> · ${{esc(p.b)}}</div>
      <div class="lctl"><input type="number" min="1" value="${{l.qty}}" data-rqty="${{esc(l.sku)}}"
        aria-label="Qty"><button data-del="${{esc(l.sku)}}">${{T("remove")}}</button></div>
      <textarea data-note="${{esc(l.sku)}}" placeholder="${{T("ph_note")}}">${{esc(l.note)}}</textarea>
    </div>`;}}).join("")+`<div style="margin-top:22px">
    <div class="two"><div class="field"><label>${{T("f_name")}}</label><input id="rName"></div>
    <div class="field"><label>${{T("f_company")}}</label><input id="rCo"></div></div>
    <div class="two"><div class="field"><label>${{T("f_email")}}</label>
      <input id="rEmail" type="email" dir="ltr"></div>
    <div class="field"><label>${{T("f_phone")}}</label><input id="rPhone" type="tel" dir="ltr"
      placeholder="+966"></div></div>
    <div class="field"><label>${{T("f_project")}}</label><input id="rProj"
      placeholder="${{T("ph_project")}}"></div>
    <div class="field"><label>${{T("f_msg")}}</label><textarea id="rMsg" rows="3"></textarea></div></div>`;
  $("#rfqFoot").innerHTML=`<button class="btn btn-p" id="send"
    style="width:100%;justify-content:center">${{T("send")}} — ${{S.rfq.reduce((a,l)=>a+l.qty,0)}}
    ${{T("units")}}</button><p class="formnote">${{T("send_note")}}</p>`;}}
const show=s=>{{$("#scrim").classList.add("on");$(s).classList.add("on");
  $(s).setAttribute("aria-hidden","false");document.body.style.overflow="hidden";}};
const hideAll=()=>{{$("#scrim").classList.remove("on");
  document.querySelectorAll(".drawer").forEach(d=>{{d.classList.remove("on");
    d.setAttribute("aria-hidden","true");}});document.body.style.overflow="";}};
let tt;const toast=m=>{{$("#toastMsg").textContent=m;$("#toast").classList.add("on");
  clearTimeout(tt);tt=setTimeout(()=>$("#toast").classList.remove("on"),2400);}};

$("#q").addEventListener("input",e=>{{S.q=e.target.value;S.shown=PAGE;render();}});
$("#sort").addEventListener("change",e=>{{S.sort=e.target.value;renderResults();}});
$("#vGrid").addEventListener("click",()=>{{S.view="grid";$("#vGrid").ariaPressed="true";
  $("#vList").ariaPressed="false";renderResults();}});
$("#vList").addEventListener("click",()=>{{S.view="list";$("#vList").ariaPressed="true";
  $("#vGrid").ariaPressed="false";renderResults();}});
$("#loadmore").addEventListener("click",()=>{{S.shown+=PAGE;renderResults();}});
$("#mobFilter").addEventListener("click",()=>$("#facets").classList.toggle("on"));
$("#facets").addEventListener("change",ev=>{{const d=ev.target.dataset.dim;if(!d)return;
  let v=ev.target.value,arr;
  if(d==="cat")arr=S.cat;else if(d==="brand")arr=S.brand;
  else if(d==="avail"){{arr=S.avail;v=(v===T("in_stock"))?"stock":"lead";}}
  else{{const k=d.slice(5);S.spec[k]=S.spec[k]||[];arr=S.spec[k];}}
  const i=arr.indexOf(v);ev.target.checked?(i<0&&arr.push(v)):(i>-1&&arr.splice(i,1));
  S.shown=PAGE;render();}});
$("#facets").addEventListener("click",ev=>{{
  if(ev.target.dataset.more){{S["_m_"+ev.target.dataset.more]=true;renderFacets();}}
  if(ev.target.id==="clearAll"){{S.cat=[];S.brand=[];S.avail=[];S.spec={{}};S.shown=PAGE;render();}}}});
$("#chips").addEventListener("click",ev=>{{const d=ev.target.dataset.chip;if(!d)return;
  const v=ev.target.dataset.val;
  if(d==="cat")S.cat=S.cat.filter(x=>x!==v);
  else if(d==="brand")S.brand=S.brand.filter(x=>x!==v);
  else if(d==="avail"){{const k=(v===T("in_stock"))?"stock":"lead";S.avail=S.avail.filter(x=>x!==k);}}
  else{{const k=d.slice(5);S.spec[k]=(S.spec[k]||[]).filter(x=>x!==v);}}
  render();}});
document.addEventListener("click",ev=>{{
  const o=ev.target.closest("[data-open]");if(o){{openProduct(o.dataset.open);return;}}
  const a=ev.target.closest("[data-add]");
  if(a){{const sku=a.dataset.add,qi=(a.closest(".add")||document)
    .querySelector(`[data-qty="${{CSS.escape(sku)}}"]`);
    addToRfq(sku,Math.max(1,parseInt(qi&&qi.value)||1));return;}}
  if(ev.target.id==="clearAll2"){{S.cat=[];S.brand=[];S.avail=[];S.spec={{}};S.q="";
    $("#q").value="";render();}}
  if(ev.target.closest("#openRfq")){{renderRfq();show("#rfqDrawer");}}
  if(ev.target.closest(".drawer > header .x")||ev.target.id==="scrim")hideAll();}});
$("#rfqBody").addEventListener("input",ev=>{{
  if(ev.target.dataset.rqty){{const l=S.rfq.find(x=>x.sku===ev.target.dataset.rqty);
    l.qty=Math.max(1,parseInt(ev.target.value)||1);renderCount();
    $("#rfqFoot").querySelector("button").textContent=
      `${{T("send")}} — ${{S.rfq.reduce((a,x)=>a+x.qty,0)}} ${{T("units")}}`;}}
  if(ev.target.dataset.note)S.rfq.find(x=>x.sku===ev.target.dataset.note).note=ev.target.value;}});
$("#rfqBody").addEventListener("click",ev=>{{if(ev.target.dataset.del){{
  S.rfq=S.rfq.filter(l=>l.sku!==ev.target.dataset.del);renderRfq();render();}}}});
$("#rfqFoot").addEventListener("click",ev=>{{if(ev.target.id!=="send")return;
  const payload={{contact:{{name:$("#rName").value||"—",company:$("#rCo").value||"—",
    email:$("#rEmail").value||"—",phone:$("#rPhone").value||"—"}},
    project:$("#rProj").value||"—",message:$("#rMsg").value||"",
    lines:S.rfq.map(l=>({{sku:l.sku,qty:l.qty,note:l.note}})),
    locale:document.documentElement.lang,source:"web-catalogue"}};
  $("#rfqBody").innerHTML=`<div class="empty" style="border-style:solid">
    <h3>${{T("received")}}</h3><p style="color:var(--ink-2);margin-top:6px">${{T("received_p")}}</p></div>
    <p class="formnote" style="text-align:start;margin-top:18px">${{T("posts_to")}}</p>
    <div class="payload">${{esc(JSON.stringify(payload,null,2))}}</div>`;
  $("#rfqFoot").innerHTML="";S.rfq=[];renderCount();render();}});
document.addEventListener("keydown",ev=>{{if(ev.key==="Escape")hideAll();}});
render();
</script>"""

# ══════════════════════════════════════════════════════════════════════════
META = {
 'index':   ("Low-current systems integration in Saudi Arabia | Datacore Solutions",
             "Datacore designs, supplies, installs and maintains network, datacentre, security, "
             "audio-visual and life-safety systems across Saudi Arabia and the UAE. Since 2007.",
             "تكامل أنظمة التيار الخفيف في السعودية | داتاكور للحلول",
             "تصميم وتوريد وتركيب وصيانة أنظمة الشبكات ومراكز البيانات والأمن والأنظمة السمعية "
             "والبصرية والسلامة في السعودية والإمارات. منذ 2007."),
 'about':   ("About Datacore | Low-current integrator in Riyadh since 2007",
             "Founded in Jeddah in 2007, Datacore now delivers nine low-current disciplines "
             "in-house from Riyadh, Dubai and Kozhikode.",
             "من نحن | داتاكور، تكامل أنظمة التيار الخفيف منذ 2007",
             "تأسست في جدة عام 2007، وتنفذ داتاكور اليوم تسعة تخصصات في التيار الخفيف بكوادرها "
             "من الرياض ودبي وكوزيكود."),
 'services':("Services | 38 low-current services across nine disciplines | Datacore",
             "Network infrastructure, datacentre, surveillance, meeting rooms, audio-visual, "
             "signage, public address, IPTV and maintenance — all delivered in-house.",
             "خدماتنا | 38 خدمة في التيار الخفيف عبر تسعة تخصصات | داتاكور",
             "البنية التحتية للشبكات ومراكز البيانات والمراقبة وقاعات الاجتماعات والأنظمة "
             "السمعية والبصرية واللافتات والنداء الآلي و IPTV والصيانة."),
 'products':("Product catalogue | Request a quote | Datacore Solutions",
             "Browse network, security and audio-visual hardware and build a request for "
             "quotation. Priced quotations with lead times within one working day.",
             "كتالوج المنتجات | اطلب عرض سعر | داتاكور للحلول",
             "تصفح أجهزة الشبكات والأمن والأنظمة السمعية والبصرية وأنشئ طلب عرض سعر. عروض "
             "مسعّرة مع مدد التوريد خلال يوم عمل واحد."),
 'projects':("Projects | AOU, PSAU and TAQEEM case studies | Datacore",
             "Named clients, stated scope and the equipment deployed on recent low-current "
             "and audio-visual projects across Saudi Arabia.",
             "مشاريعنا | دراسات حالة | داتاكور",
             "عملاء بالاسم ونطاق عمل محدد والأجهزة المركّبة في مشاريع حديثة للتيار الخفيف "
             "والأنظمة السمعية والبصرية في المملكة."),
 'insights':("Technical notes | Datacore Solutions",
             "Notes from our engineers on public address standards, passive networks and the "
             "decisions that come up on real projects.",
             "ملاحظات تقنية | داتاكور للحلول",
             "ملاحظات من مهندسينا حول مواصفات أنظمة النداء والشبكات السلبية والقرارات التي "
             "تتكرر في المشاريع الفعلية."),
 'contact':("Contact | Riyadh, Dubai and Kozhikode | Datacore Solutions",
            "Send a BOQ, a schedule of materials or drawings and we return a priced scope and "
            "programme. Offices in Riyadh, Dubai and Kozhikode.",
            "تواصل معنا | الرياض ودبي وكوزيكود | داتاكور للحلول",
            "أرسل جدول الكميات أو المواد أو المخططات وسنعود بنطاق مسعّر وبرنامج زمني. مكاتبنا "
            "في الرياض ودبي وكوزيكود."),
}
BODY = {'index':page_index,'about':page_about,'services':page_services,
        'products':page_products,'projects':page_projects,'insights':page_insights,
        'contact':page_contact}

written = []
for l in ("en","ar"):
    for p in PAGES:
        m = META[p]
        title, desc = (m[0], m[1]) if l == "en" else (m[2], m[3])
        extra = PROD_CSS if p == "products" else ""
        doc = head(l,p,title,desc,extra) + header(l,p) + BODY[p](l) + footer(l)
        path = os.path.join(OUT, url(p,l))
        open(path,"w",encoding="utf-8").write(doc)
        written.append((url(p,l), round(len(doc)/1024,1)))

for n,k in written:
    print(f"{n:26s} {k:>7} KB")
print(f"\n{len(written)} pages written to {OUT}")
