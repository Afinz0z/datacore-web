# Colour tokens per theme. The dark set is a designed palette, not an
# inversion: bands/footer stay dark in both themes (--band), and image
# wells stay light in both (--well) so brand logos and white-background
# product photos remain legible. The accent brightens in dark mode and its
# button text flips to a deep teal-black (--accent-contrast) for contrast.
_LIGHT = """
  color-scheme:light;
  --bg:#FFFFFF;
  --ink:#1A1B1F; --ink-2:#565C61; --ink-3:#7C848A;
  --paper:#F4F7F6; --surface:#FFFFFF; --line:#E2E8E6; --line-2:#CBD5D2;
  --brand:#00ACA1;        /* logo teal - 2.83:1, fills and marks only      */
  --accent:#00776F;       /* same hue at 5.43:1 - all text and buttons     */
  --accent-d:#005A54; --accent-contrast:#FFFFFF;
  --mint:#EAF6F4; --amber:#8A5A0F;
  --band:#1A1B1F; --band-sub:#A6B0B2; --well:#F4F7F6;
  --hdr-bg:rgba(255,255,255,.94);
  --focus-ring:rgba(0,119,111,.13);
"""
_DARK = """
  color-scheme:dark;
  --bg:#131417;
  --ink:#E8EAEB; --ink-2:#ABB3B6; --ink-3:#848C91;
  --paper:#17181C; --surface:#1C1E23; --line:#2A2E33; --line-2:#3B4147;
  --brand:#00ACA1;
  --accent:#3BC0B3;       /* brightened for dark ground - 7.5:1 on --bg    */
  --accent-d:#5FD9CC; --accent-contrast:#07211E;
  --mint:#152220; --amber:#D9A54A;
  --band:#101114; --band-sub:#8F979B; --well:#EDF1F0;
  --hdr-bg:rgba(19,20,23,.92);
  --focus-ring:rgba(59,192,179,.24);
"""

CSS = r"""
/* ═══════════════════════════════════════════════════════════════════════
   Datacore — shared stylesheet
   Written entirely with CSS logical properties (margin-inline, inset-inline,
   text-align:start) so the Arabic build needs no separate RTL stylesheet.
   Setting dir="rtl" on <html> mirrors the whole layout.
   Themes: light tokens on :root; dark tokens under [data-theme="dark"] and,
   for no-JS visitors, under prefers-color-scheme (a head script resolves
   the stored/system choice before first paint).
   ═══════════════════════════════════════════════════════════════════════ */
:root{@@LIGHT@@
  --sans:'Archivo',system-ui,-apple-system,'Segoe UI',sans-serif;
  --display:'Bricolage Grotesque','Archivo',system-ui,sans-serif;
  --mono:'IBM Plex Mono',ui-monospace,Menlo,monospace;
  --shell:1280px; --gutter:clamp(20px,5vw,56px);
  --s1:8px; --s2:16px; --s3:30px; --s4:52px; --s5:84px; --s6:124px;
  --lh:1.6;
}
:root[data-theme="dark"]{@@DARK@@}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){@@DARK@@}
}
/* Arabic: different family, looser leading, mono falls back to the Arabic sans */
html[dir=rtl]{
  --sans:'IBM Plex Sans Arabic','Archivo',system-ui,sans-serif;
  --display:'IBM Plex Sans Arabic',system-ui,sans-serif;
  --mono:'IBM Plex Sans Arabic',system-ui,sans-serif;
  --lh:1.9;
}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{scroll-behavior:smooth;scroll-padding-top:88px}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{margin:0;font-family:var(--sans);font-size:17px;line-height:var(--lh);
  color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased}
img,svg{max-width:100%;display:block}
button,input,select,textarea{font:inherit;color:inherit}
button{cursor:pointer;border:0;background:none}
a{color:var(--accent);text-underline-offset:3px}
h1,h2,h3,h4{margin:0;line-height:1.14;letter-spacing:-.02em;font-weight:700}
/* the display face carries page and section titles; cards stay in Archivo */
h1,h2{font-family:var(--display);letter-spacing:-.01em;line-height:1.08}
html[dir=rtl] h1,html[dir=rtl] h2,html[dir=rtl] h3,html[dir=rtl] h4{
  line-height:1.45;letter-spacing:0}
p,ul,ol,dl{margin:0}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:2px}
@media (prefers-reduced-motion:reduce){
  *{animation:none!important;transition:none!important}
  /* the hero stack items rest at opacity:0 and are revealed by the animation —
     with animation off they must be shown outright or they never appear */
  .stack a{opacity:1;transform:none}
}

.wrap{max-width:var(--shell);margin-inline:auto;padding-inline:var(--gutter)}
.mono{font-family:var(--mono);font-size:.75rem;letter-spacing:.06em;color:var(--ink-3)}
html[dir=rtl] .mono{letter-spacing:0;font-size:.8125rem}
.skip{position:absolute;inset-inline-start:-9999px;top:0;background:var(--band);
  color:#fff;padding:12px 20px;z-index:100;text-decoration:none}
.skip:focus{inset-inline-start:0}
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}

/* ── buttons ─────────────────────────────────────────────────────────── */
.btn{display:inline-flex;align-items:center;gap:8px;border-radius:2px;font-weight:600;
  font-size:1rem;padding:13px 24px;text-decoration:none;white-space:nowrap}
.btn-p{background:var(--accent);color:var(--accent-contrast)}
.btn-p:hover{background:var(--accent-d)}
.btn-s{border:1px solid var(--line-2);color:var(--ink)}
.btn-s:hover{border-color:var(--ink)}

/* ── header ──────────────────────────────────────────────────────────── */
.hdr{position:sticky;top:0;z-index:50;background:var(--hdr-bg);
  -webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);
  border-bottom:1px solid var(--line)}
.hdr .wrap{display:flex;align-items:center;gap:var(--s4);height:76px}
.logo{flex:none;display:block}
.logo svg{height:46px;width:auto}
/* the inline logo's ink-coloured paths must lighten on a dark header */
[data-theme="dark"] .hdr .logo svg [fill="#1A1B1F"]{fill:#EDEFEF}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]) .hdr .logo svg [fill="#1A1B1F"]{fill:#EDEFEF}
}
.mainnav{display:flex;gap:var(--s3);margin-inline-start:auto}
.mainnav a{color:var(--ink);text-decoration:none;font-size:1rem;font-weight:500;
  padding:6px 0;border-bottom:2px solid transparent}
.mainnav a:hover{border-bottom-color:var(--line-2)}
.mainnav a[aria-current]{font-weight:700;border-bottom-color:var(--accent)}
.hdr-cta{display:flex;gap:var(--s1);align-items:center}
.lang{font-family:var(--mono);font-size:.75rem;color:var(--ink-2);border:1px solid var(--line);
  padding:7px 10px;border-radius:2px;text-decoration:none;white-space:nowrap}
.lang:hover{border-color:var(--ink-2)}
/* theme toggle: moon shown in light (click -> dark), sun shown in dark */
.tbtn{display:flex;padding:8px;border:1px solid var(--line);border-radius:2px;
  color:var(--ink-2)}
.tbtn:hover{border-color:var(--ink-2);color:var(--ink)}
.tbtn .tsun{display:none}
[data-theme="dark"] .tbtn .tsun{display:block}
[data-theme="dark"] .tbtn .tmoon{display:none}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]) .tbtn .tsun{display:block}
  :root:not([data-theme="light"]) .tbtn .tmoon{display:none}
}
.burger{display:none;padding:8px}
.burger .x{display:none}
.burger[aria-expanded=true] .x{display:block}
.burger[aria-expanded=true] .bars{display:none}
.menu-cta{display:none}

/* ── page header block ───────────────────────────────────────────────── */
.phead{background:linear-gradient(180deg,var(--mint),var(--bg));
  border-bottom:1px solid var(--line);position:relative;overflow:hidden}
.phead::after{content:"";position:absolute;inset-block:0;inset-inline-end:-12%;
  width:55%;pointer-events:none;
  background:radial-gradient(460px 320px at 68% 38%,rgba(0,172,161,.16),transparent 70%)}
.phead .wrap{padding-block:var(--s5) var(--s4);position:relative;z-index:1}
.phead h1{font-size:clamp(2.4rem,4.8vw,3.7rem);max-width:18ch}
.phead p{margin-top:var(--s3);color:var(--ink-2);font-size:1.1875rem;max-width:60ch}
.crumbs{font-family:var(--mono);font-size:.75rem;color:var(--ink-3);margin-bottom:var(--s2);
  display:flex;gap:8px;flex-wrap:wrap}
.crumbs a{color:var(--ink-3);text-decoration:none}
.crumbs a:hover{color:var(--accent)}

/* ── hero (home) ─────────────────────────────────────────────────────── */
/* One cinematic moment: real rack photography under an ink veil with a
   slowly drifting teal aurora. Deliberately identical in both themes. */
.hero{position:relative;border-bottom:1px solid var(--line);overflow:hidden;
  background:#0C0E10 url('assets/photos/stock-datacentre.jpg') center/cover no-repeat}
.hero::before{content:"";position:absolute;inset:0;
  background:linear-gradient(100deg,rgba(9,11,13,.94) 26%,rgba(9,11,13,.62) 62%,
    rgba(0,90,84,.38) 100%)}
html[dir=rtl] .hero::before{
  background:linear-gradient(-100deg,rgba(9,11,13,.94) 26%,rgba(9,11,13,.62) 62%,
    rgba(0,90,84,.38) 100%)}
.hero::after{content:"";position:absolute;inset:-30%;pointer-events:none;
  background:
    radial-gradient(640px 420px at 16% 28%,rgba(0,172,161,.30),transparent 62%),
    radial-gradient(760px 520px at 88% 78%,rgba(0,119,111,.26),transparent 65%);
  filter:blur(46px);animation:aurora 17s ease-in-out infinite alternate}
@keyframes aurora{from{transform:translate3d(0,0,0)}to{transform:translate3d(4%,3%,0)}}
@media (prefers-reduced-motion:reduce){.hero::after{animation:none}}
.hero .wrap{position:relative;z-index:1;
  display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);
  gap:var(--s6);padding-block:var(--s5) var(--s5);align-items:center}
.hero h1{color:#fff}
.hero .eyebrow{color:#6FE0D4}
.hero .lede{color:#C4CCCE}
.hero .lede b{color:#fff}
.hero .btn-s{border-color:rgba(255,255,255,.35);color:#fff}
.hero .btn-s:hover{border-color:#fff}
.hero .stack{box-shadow:0 40px 70px -35px rgba(0,0,0,.65)}
.eyebrow{display:inline-flex;align-items:center;gap:10px;font-family:var(--mono);
  font-size:.8125rem;letter-spacing:.08em;color:var(--accent);margin-bottom:var(--s2)}
.eyebrow::before{content:"";width:28px;height:2px;background:var(--brand)}
html[dir=rtl] .eyebrow{letter-spacing:0}
.hero h1{font-size:clamp(2.75rem,5.4vw,4.35rem);max-width:15ch;font-weight:800}
.hero .lede{margin-top:var(--s3);font-size:1.25rem;max-width:54ch}
.hero-cta{display:flex;gap:12px;margin-top:var(--s4);flex-wrap:wrap}

.stack{border:1px solid var(--line);background:var(--surface);border-radius:3px}
.stack header{padding:16px 20px;border-bottom:1px solid var(--line);display:flex;
  justify-content:space-between;align-items:baseline;background:var(--paper)}
.stack header strong{font-size:.9375rem;font-weight:600}
.stack a{display:grid;grid-template-columns:22px 1fr auto;gap:14px;align-items:center;
  padding:13px 20px;border-bottom:1px solid var(--line);text-decoration:none;
  color:var(--ink);font-size:1rem;opacity:0;transform:translateY(6px);animation:rise .5s forwards}
.stack a:last-child{border-bottom:0}
.stack a:hover{background:var(--mint)}
.stack .n{font-family:var(--mono);font-size:.75rem;color:var(--ink-3)}
.stack .c{font-family:var(--mono);font-size:.75rem;color:var(--accent)}
@keyframes rise{to{opacity:1;transform:none}}

/* ── stats ───────────────────────────────────────────────────────────── */
.stats{background:var(--band);color:#fff}
.stats .wrap{display:grid;grid-template-columns:repeat(4,1fr);gap:var(--s4);padding-block:var(--s4)}
.stat b{display:block;font-size:clamp(2.3rem,3.8vw,3.2rem);font-weight:700;
  letter-spacing:-.03em;font-variant-numeric:tabular-nums;line-height:1;direction:ltr;
  text-align:start}
/* the figure box is direction:ltr (digits), so in RTL its text-align must be
   flipped by hand or the number hugs the wrong edge while its label sits right */
html[dir=rtl] .stat b{text-align:end}
.stat span{display:block;margin-top:10px;font-size:.875rem;color:var(--band-sub)}
.stat i{display:block;width:24px;height:2px;background:var(--brand);margin-bottom:16px}

/* ── sections ────────────────────────────────────────────────────────── */
.sec{padding-block:var(--s6)}
.sec-tight{padding-block:var(--s4) var(--s6)}
.sec-alt{background:var(--paper);border-block:1px solid var(--line)}
.sec-head{max-width:62ch;margin-bottom:var(--s4)}
.sec-head h2{font-size:clamp(1.9rem,3.4vw,2.7rem)}
.sec-head p{margin-top:var(--s2);color:var(--ink-2);font-size:1.125rem}
.sec-head.split{max-width:none;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);
  gap:var(--s4);align-items:end}
.sec-head.split p{margin-top:0}

/* ── discipline cards ────────────────────────────────────────────────── */
/* Card grids use per-cell borders pulled under the container border with
   -1px margins, NOT a 1px-gap over a dark background: with the gap trick a
   partially-filled last row shows the container background as a grey hole. */
.disc{display:grid;grid-template-columns:repeat(3,1fr);border:1px solid var(--line);
  overflow:hidden}
.disc article{background:var(--surface);padding:var(--s3);display:flex;flex-direction:column;
  gap:12px;border-inline-end:1px solid var(--line);border-block-end:1px solid var(--line);
  margin-inline-end:-1px;margin-block-end:-1px}
.disc article:hover{background:var(--mint)}
.disc h3{font-size:1.1875rem;font-weight:600}
.disc h3 a{color:var(--ink);text-decoration:none}
.disc h3 a:hover{color:var(--accent)}
.disc ul{padding:0;list-style:none;display:flex;flex-wrap:wrap;gap:6px}
.disc li{font-size:.875rem;color:var(--ink-2);background:var(--paper);
  border:1px solid var(--line);padding:3px 10px;border-radius:2px}
.disc article:hover li{background:var(--surface)}
.disc .std{margin-top:auto;padding-top:12px;border-top:1px solid var(--line)}

/* ── services hub ────────────────────────────────────────────────────── */
.filters{display:flex;gap:8px;flex-wrap:wrap;padding-block:var(--s3);
  border-bottom:1px solid var(--line);position:sticky;top:76px;background:var(--hdr-bg);
  -webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);z-index:20}
.filters a,.filters button{border:1px solid var(--line-2);border-radius:2px;padding:7px 14px;
  font-size:.875rem;text-decoration:none;color:var(--ink);background:var(--surface)}
.filters a:hover,.filters button:hover{border-color:var(--ink)}
.filters .on{background:var(--band);color:#fff;border-color:var(--band)}
.cat{padding-block:var(--s5);border-bottom:1px solid var(--line);
  scroll-margin-top:150px /* clear the sticky header + chip bar on anchor jumps */}
.cat:last-child{border-bottom:0}
.disc article{scroll-margin-top:110px}
.cat-head{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.3fr);gap:var(--s4);
  align-items:start;margin-bottom:var(--s4)}
.cat-head .num{font-family:var(--mono);font-size:.75rem;color:var(--accent);
  display:block;margin-bottom:10px}
.cat-head h2{font-size:clamp(1.6rem,2.9vw,2.2rem)}
.cat-head p{color:var(--ink-2)}
.svcs{display:grid;grid-template-columns:repeat(3,1fr);border:1px solid var(--line);
  overflow:hidden}
.svc{background:var(--surface);padding:0;display:flex;flex-direction:column;
  border-inline-end:1px solid var(--line);border-block-end:1px solid var(--line);
  margin-inline-end:-1px;margin-block-end:-1px}
.svc-top{background:var(--well);height:120px;display:flex;align-items:center;
  justify-content:center;padding:18px;border-bottom:1px solid var(--line)}
.svc-top img{max-height:100%;max-width:60%;transition:transform .25s}
.svc:hover .svc-top img{transform:scale(1.06)}
.svc-in{padding:var(--s3);display:flex;flex-direction:column;gap:10px;flex:1}
.svc:hover{background:var(--mint)}
.svc h3{font-size:1.125rem;font-weight:600}
.svc h3 a{color:var(--ink);text-decoration:none}
.svc h3 a:hover{color:var(--accent)}
.svc p{font-size:.9375rem;color:var(--ink-2)}
.svc .more{margin-top:auto;font-size:.8125rem;font-weight:600;text-decoration:none}

/* ── projects ────────────────────────────────────────────────────────── */
.projs{display:grid;grid-template-columns:repeat(2,1fr);gap:var(--s3)}
.proj{border:1px solid var(--line);background:var(--surface);display:flex;flex-direction:column}
.proj:hover{border-color:var(--line-2)}
.proj .band{background:var(--band);color:#fff;padding:10px 20px;display:flex;
  justify-content:space-between;font-family:var(--mono);font-size:.75rem;letter-spacing:.05em}
html[dir=rtl] .proj .band{letter-spacing:0;font-size:.8125rem}
.proj .band span:last-child{color:var(--brand)} /* ok-on-dark: 5.8:1 on --ink */
.proj .in{padding:var(--s3);display:flex;flex-direction:column;gap:14px;flex:1}
.proj h3{font-size:1.375rem}
.proj>.in>p{color:var(--ink-2);font-size:.9375rem}
.proj dl{display:grid;grid-template-columns:auto 1fr;gap:6px 16px;font-size:.875rem;
  border-top:1px solid var(--line);padding-top:14px;margin-top:auto}
.proj dt{color:var(--ink-3)}
.proj dd{margin:0}
.kit{display:flex;flex-wrap:wrap;gap:6px}
.kit a{font-size:.75rem;font-family:var(--mono);border:1px solid var(--line-2);
  padding:3px 8px;border-radius:2px;text-decoration:none;color:var(--accent)}
.kit a:hover{background:var(--mint)}

/* ── timeline ────────────────────────────────────────────────────────── */
.tl{display:grid;grid-template-columns:repeat(5,1fr);gap:var(--s3);
  border-top:2px solid var(--line);padding-top:var(--s3)}
.tl article{position:relative}
.tl article::before{content:"";position:absolute;top:calc(-1 * var(--s3) - 6px);
  inset-inline-start:0;width:10px;height:10px;border-radius:50%;background:var(--brand);
  outline:3px solid var(--bg)}
.tl time{font-family:var(--mono);font-size:.8125rem;color:var(--accent);display:block;direction:ltr}
html[dir=rtl] .tl time{text-align:start}
.tl h3{font-size:1rem;font-weight:600;margin-block:8px 6px}
.tl p{font-size:.875rem;color:var(--ink-2)}

/* ── values ──────────────────────────────────────────────────────────── */
.vals{display:grid;grid-template-columns:repeat(3,1fr);border:1px solid var(--line);
  overflow:hidden}
.val{background:var(--surface);padding:var(--s3);display:flex;flex-direction:column;gap:10px;
  border-inline-end:1px solid var(--line);border-block-end:1px solid var(--line);
  margin-inline-end:-1px;margin-block-end:-1px}
.val .vico{height:104px;display:flex;align-items:center;justify-content:flex-start;
  margin-bottom:4px}
.val .vico img{max-height:100%;width:auto}
.val .n{font-family:var(--mono);font-size:.75rem;color:var(--accent)}
.val h3{font-size:1.1875rem;font-weight:600}
.val p{font-size:1rem;color:var(--ink-2)}

/* ── partners ────────────────────────────────────────────────────────── */
.partners{display:grid;grid-template-columns:repeat(7,1fr);border:1px solid var(--line);
  overflow:hidden}
.partners span{background:var(--surface);padding:22px 10px;text-align:center;font-weight:600;
  font-size:.9375rem;color:var(--ink-2);display:flex;align-items:center;justify-content:center;
  direction:ltr;border-inline-end:1px solid var(--line);border-block-end:1px solid var(--line);
  margin-inline-end:-1px;margin-block-end:-1px}

/* ── insights ────────────────────────────────────────────────────────── */
.posts{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--s3)}
.post{border-top:2px solid var(--ink);padding-top:var(--s2);display:flex;
  flex-direction:column;gap:10px}
.post h3{font-size:1.1875rem;font-weight:600}
.post h3 a{color:var(--ink);text-decoration:none}
.post h3 a:hover{color:var(--accent)}
.post p{font-size:.9375rem;color:var(--ink-2)}
.post .by{font-family:var(--mono);font-size:.75rem;color:var(--ink-3)}
.post-lg{grid-column:span 3;border-top-width:3px;display:grid;
  grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:var(--s4);align-items:start}
.post-lg h3{font-size:1.75rem;margin-top:8px}
.post-lg>div>p{margin-top:14px;max-width:58ch}
.post-lg .pimg img{aspect-ratio:auto}

/* ── contact ─────────────────────────────────────────────────────────── */
.chero{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);
  gap:var(--s5);align-items:center}
.quick{background:var(--surface);border:1px solid var(--line);border-radius:8px;
  padding:22px 26px;box-shadow:0 18px 40px -28px rgba(26,27,31,.35)}
.quick h3{font-family:var(--mono);font-size:.75rem;letter-spacing:.06em;
  text-transform:uppercase;color:var(--ink-3);font-weight:500;margin-bottom:6px}
html[dir=rtl] .quick h3{letter-spacing:0}
.quick a{display:flex;gap:11px;align-items:center;padding:12px 0;
  border-bottom:1px solid var(--line);text-decoration:none;font-weight:500}
.quick a:last-of-type{border-bottom:0}
.quick a:hover{color:var(--accent)}
.quick svg{flex:none;color:var(--accent)}
.quick .formnote{text-align:start;margin-top:10px}
@media(max-width:1080px){.chero{grid-template-columns:1fr;gap:var(--s3)}}
.contact-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:var(--s6)}
.offices-grid{display:grid;gap:var(--s3)}
/* offices + map band: cards column beside the live map */
.geo-grid{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,3fr);gap:var(--s4);
  align-items:stretch}
.geo-grid .offices-list{display:flex;flex-direction:column;gap:14px}
.office-card[data-off]{cursor:pointer}
.office-card.on{border-color:var(--accent);box-shadow:inset 3px 0 0 var(--brand)}
html[dir=rtl] .office-card.on{box-shadow:inset -3px 0 0 var(--brand)}
.map-col{display:flex;flex-direction:column;min-width:0}
.map-col .map{flex:1;aspect-ratio:auto;min-height:420px}
@media(max-width:1080px){.geo-grid{grid-template-columns:1fr}
  .map-col .map{aspect-ratio:16/10;min-height:0}}
.office-card{border:1px solid var(--line);padding:var(--s3);background:var(--surface)}
.office-card h3{font-size:1.0625rem;font-weight:600;margin-bottom:10px}
.office-card p{color:var(--ink-2);font-size:.9375rem}
.office-card .rows{margin-top:14px;display:grid;gap:6px;font-size:.9375rem}
.office-card a{text-decoration:none;font-weight:500}
.office-card a:hover{text-decoration:underline}
.form{border:1px solid var(--line);padding:var(--s4);background:var(--paper)}
.field{margin-bottom:var(--s2)}
.field label{display:block;font-size:.875rem;font-weight:500;margin-bottom:6px}
.field .hint{font-weight:400;color:var(--ink-3);font-size:.8125rem}
.field input,.field select,.field textarea{width:100%;border:1px solid var(--line-2);
  border-radius:2px;padding:11px 13px;background:var(--surface)}
.field input:focus,.field textarea:focus,.field select:focus{border-color:var(--accent);outline:0;
  box-shadow:0 0 0 3px var(--focus-ring)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:var(--s2)}
.form .btn-p{width:100%;justify-content:center;padding:14px}
.formnote{margin-top:14px;font-size:.8125rem;color:var(--ink-2);text-align:center}

/* ── map facade ──────────────────────────────────────────────────────── */
.map{border:1px solid var(--line);background:var(--paper);position:relative;
  aspect-ratio:16/10;display:flex;align-items:center;justify-content:center;overflow:hidden}
.map iframe{width:100%;height:100%;border:0;display:block}
.map-face{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:14px;text-align:center;padding:var(--s3);cursor:pointer;
  background:
    repeating-linear-gradient(0deg,transparent 0 38px,var(--line) 38px 39px),
    repeating-linear-gradient(90deg,transparent 0 38px,var(--line) 38px 39px),
    var(--paper)}
.map-face:hover{background-color:var(--mint)}
.map-face .pin{width:34px;height:34px;border-radius:50%;background:var(--brand);
  display:flex;align-items:center;justify-content:center;color:#fff;
  box-shadow:0 0 0 8px rgba(0,172,161,.18)}
.map-face strong{font-size:1rem;font-weight:600}
.map-face span{font-size:.875rem;color:var(--ink-2);max-width:44ch}
.map-cap{margin-top:12px;font-size:.8125rem;color:var(--ink-3)}
.map-tabs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
.map-tabs button{border:1px solid var(--line-2);border-radius:2px;padding:7px 14px;
  font-size:.875rem;background:var(--surface)}
.map-tabs button:hover{border-color:var(--ink)}
.map-tabs button[aria-pressed=true]{background:var(--ink);color:#fff;border-color:var(--ink)}
.dirlink{display:inline-flex;align-items:center;gap:7px;font-size:.875rem;font-weight:500;
  text-decoration:none;margin-top:10px}
.dirlink:hover{text-decoration:underline}

/* ── full-width photo band (about) ───────────────────────────────────── */
.band-img{height:clamp(220px,32vw,400px);border-bottom:1px solid var(--line);
  background:#101114 url('assets/photos/stock-patching.jpg') center/cover no-repeat}

/* ── photography ─────────────────────────────────────────────────────── */
figure.ph{margin:0;border:1px solid var(--line);background:var(--surface);
  border-radius:3px;overflow:hidden}
figure.ph img{width:100%;height:auto;display:block}
figure.ph.crop img{aspect-ratio:4/3;object-fit:cover}
figure.ph figcaption{font-size:.8125rem;color:var(--ink-3);padding:9px 14px;
  border-top:1px solid var(--line)}
.gal{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.gal-2{grid-template-columns:repeat(2,1fr)}
.gal figure.ph.wide{grid-column:1/-1}
figure.ph.wide img{aspect-ratio:auto;object-fit:unset}
/* the two team photos: side by side, equal height, NO cropping and no
   upscaling — at 432px tall the panorama renders at ~765px, just under
   its native 800px, so it stays sharp and nobody is cut off */
.gal-team{display:flex;gap:14px;align-items:stretch;flex-wrap:wrap}
.gal-team figure.ph{display:flex;flex-direction:column}
.gal-team figure.ph img{height:432px;width:auto}
.gal-team figcaption{margin-top:auto}
@media(max-width:1150px){.gal-team{flex-direction:column;align-items:flex-start}
  .gal-team figure.ph img{height:auto;width:100%;max-width:800px}
  .gal-team figure.ph{max-width:800px;width:100%}}
.duo{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);
  gap:var(--s4);align-items:start}
@media(max-width:860px){.gal{grid-template-columns:1fr 1fr}
  .duo{grid-template-columns:1fr}}
@media(max-width:560px){.gal{grid-template-columns:1fr}}

/* ── service detail pages ────────────────────────────────────────────── */
.svc-grid{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:var(--s5);
  align-items:start;padding-block:var(--s5)}
.svc-body{max-width:72ch}
.svc-body h2{font-size:clamp(1.35rem,2.4vw,1.75rem);margin-top:var(--s4)}
.svc-body h2:first-child{margin-top:0}
.svc-body p{margin-top:var(--s2);color:var(--ink-2)}
.svc-body ul{margin:var(--s2) 0 0;padding-inline-start:22px;display:flex;
  flex-direction:column;gap:8px;color:var(--ink-2)}
.svc-body figure.ph{margin-top:var(--s3)}
.svc-aside{position:sticky;top:96px;display:flex;flex-direction:column;gap:var(--s3)}
.svc-aside .box{border:1px solid var(--line);background:var(--surface);
  border-radius:3px;padding:18px 20px}
.svc-aside h3{font-size:.8125rem;font-family:var(--mono);letter-spacing:.06em;
  color:var(--ink-3);font-weight:500;margin-bottom:12px;text-transform:uppercase}
html[dir=rtl] .svc-aside h3{letter-spacing:0}
.svc-aside ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:9px}
.svc-aside a{text-decoration:none;font-size:.9375rem}
.svc-aside a:hover{text-decoration:underline}
.svc-aside .btn{justify-content:center}
@media(max-width:1080px){.svc-grid{grid-template-columns:1fr}
  .svc-aside{position:static}}

/* ── social row ──────────────────────────────────────────────────────── */
.socrow{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}
.socrow a{display:inline-flex;align-items:center;gap:9px;border:1px solid var(--line-2);
  border-radius:2px;padding:9px 15px;text-decoration:none;color:var(--ink);
  font-size:.875rem;font-weight:500}
.socrow a:hover{border-color:var(--accent);color:var(--accent)}

/* ── CTA band ────────────────────────────────────────────────────────── */
.cta{background:var(--mint);border-block:1px solid var(--line)}
.cta .wrap{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:var(--s4);
  align-items:center;padding-block:var(--s4)}
.cta h2{font-size:clamp(1.6rem,2.8vw,2.25rem)}
.cta p{margin-top:10px;color:var(--ink-2);max-width:56ch}
.cta .btns{display:flex;gap:12px;flex-wrap:wrap}

/* ── footer ──────────────────────────────────────────────────────────── */
.ftr{background:var(--band);color:#C6CCCF;font-size:.9375rem}
.ftr-blurb{margin-top:16px;max-width:38ch;color:#9AA3A8;font-size:.9375rem}
.ftr a{color:#C6CCCF;text-decoration:none}
.ftr a:hover{color:#fff;text-decoration:underline}
.ftr-top{display:grid;grid-template-columns:1.4fr repeat(3,1fr);gap:var(--s4);
  padding-block:var(--s5) var(--s4)}
.ftr h4{font-size:.75rem;font-family:var(--mono);letter-spacing:.08em;color:#7C868A;
  margin-bottom:14px;font-weight:500}
html[dir=rtl] .ftr h4{letter-spacing:0;font-size:.8125rem}
.ftr ul{padding:0;list-style:none;display:flex;flex-direction:column;gap:9px}
.ftr .logo svg{height:44px}
.offices{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--s3);
  border-top:1px solid #2E3237;padding-block:var(--s3)}
.office strong{display:block;color:#fff;font-weight:600;margin-bottom:6px}
.office p{color:#9AA3A8;font-size:.875rem}
.office a{display:inline-block;margin-top:6px;font-family:var(--mono);font-size:.8125rem;
  direction:ltr}
.ftr-btm{border-top:1px solid #2E3237;padding-block:var(--s3);display:flex;gap:var(--s3);
  flex-wrap:wrap;align-items:center;font-size:.8125rem;color:#7C868A}
.ftr-btm .soc{margin-inline-start:auto;display:flex;gap:14px}
.ftr-btm .soc a{display:flex;padding:6px}
.legal{font-family:var(--mono);font-size:.75rem;color:#6B7478;direction:ltr}

/* ── responsive ──────────────────────────────────────────────────────── */
@media(max-width:1080px){
  .disc,.svcs,.vals{grid-template-columns:repeat(2,1fr)}
  .partners{grid-template-columns:repeat(4,1fr)}
  .tl{grid-template-columns:repeat(2,1fr);gap:var(--s4)}
  .ftr-top{grid-template-columns:1fr 1fr}
  .cat-head{grid-template-columns:1fr;gap:var(--s2)}
  .contact-grid{grid-template-columns:1fr;gap:var(--s5)}
}
@media(max-width:860px){
  .hero .wrap{grid-template-columns:1fr;gap:var(--s4);padding-block:var(--s4) var(--s5)}
  .mainnav,.hdr-cta .btn{display:none}
  .burger{display:block;margin-inline-start:auto}
  .mainnav.open{display:flex;flex-direction:column;position:absolute;top:76px;
    inset-inline:0;background:var(--surface);border-bottom:1px solid var(--line);
    box-shadow:0 20px 32px -20px rgba(26,27,31,.35);
    padding:10px var(--gutter) 22px;gap:0;margin:0}
  .mainnav.open a{padding:13px 0;border-bottom:1px solid var(--line);font-size:1.0625rem}
  .mainnav.open a:last-of-type{border-bottom:0}
  .mainnav.open .menu-cta{display:inline-flex;margin-top:12px;background:var(--accent);
    color:var(--accent-contrast);border-radius:2px;justify-content:center;font-weight:600;
    padding:13px 20px;border-bottom:0}
  .stats .wrap{grid-template-columns:1fr 1fr;gap:var(--s3)}
  .projs,.posts,.offices,.disc,.svcs,.vals,.two{grid-template-columns:1fr}
  .partners{grid-template-columns:repeat(2,1fr)}
  .post-lg{grid-column:auto;grid-template-columns:1fr;gap:var(--s2)}
  .sec-head.split,.cta .wrap{grid-template-columns:1fr;gap:var(--s2)}
  .tl{grid-template-columns:1fr}
  .sec{padding-block:var(--s5)}
  .partners span{padding:16px}
  .filters{position:static}
}

/* ── brand marquee ───────────────────────────────────────────────────── */
.marq{overflow:hidden;border:1px solid var(--line);background:var(--well);
  border-radius:3px;position:relative;
  -webkit-mask-image:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent);
  mask-image:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent)}
.marq-track{display:flex;align-items:center;gap:64px;padding:26px 32px;
  width:max-content;animation:marq 36s linear infinite;direction:ltr}
.marq:hover .marq-track{animation-play-state:paused}
.marq img{height:30px;width:auto;flex:none}
@keyframes marq{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@media (prefers-reduced-motion:reduce){
  .marq-track{animation:none;width:auto;flex-wrap:wrap;justify-content:center}
  .marq-track img.dup{display:none}
  .marq{-webkit-mask-image:none;mask-image:none}}

/* ── scroll reveal (JS adds .rev, then .in when visible) ─────────────── */
.rev{opacity:0;transform:translateY(14px);
  transition:opacity .5s ease,transform .5s ease}
.rev.in{opacity:1;transform:none}
@media (prefers-reduced-motion:reduce){.rev{opacity:1;transform:none;transition:none}}

/* ── chat bubble ─────────────────────────────────────────────────────── */
.chatb{position:fixed;inset-inline-end:20px;bottom:20px;z-index:80;
  width:56px;height:56px;border-radius:50%;background:var(--accent);
  color:var(--accent-contrast);
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 10px 26px -8px rgba(0,90,84,.55)}
.chatb::before{content:"";position:absolute;inset:0;border-radius:50%;
  border:2px solid var(--brand);opacity:0;
  animation:chatping 2.6s ease-out 2.2s 2}
@keyframes chatping{0%{transform:scale(1);opacity:.7}
  70%{transform:scale(1.55);opacity:0}100%{transform:scale(1.55);opacity:0}}
@media (prefers-reduced-motion:reduce){.chatb::before{animation:none}}
.chatb:hover{background:var(--accent-d)}
.chatb .x{display:none}
.chatb[aria-expanded=true] .bub{display:none}
.chatb[aria-expanded=true] .x{display:block}
.chatp{position:fixed;inset-inline-end:20px;bottom:88px;z-index:80;
  width:min(356px,calc(100vw - 40px));background:var(--surface);
  border:1px solid var(--line);border-radius:10px;overflow:hidden;
  box-shadow:0 28px 60px -18px rgba(26,27,31,.42);
  transform:translateY(12px);opacity:0;visibility:hidden;
  transition:opacity .22s,transform .22s,visibility 0s .22s}
.chatp.on{opacity:1;transform:none;visibility:visible;
  transition:opacity .22s,transform .22s}
.chatp header{background:var(--band);color:#fff;padding:16px 18px;
  display:flex;gap:12px;align-items:center}
.chatp .cava{width:40px;height:40px;border-radius:50%;background:#fff;flex:none;
  display:flex;align-items:center;justify-content:center;position:relative}
.chatp .cava img{width:24px;height:24px}
.chatp .cava::after{content:"";position:absolute;inset-inline-end:0;bottom:0;
  width:10px;height:10px;border-radius:50%;background:var(--brand);
  border:2px solid var(--band)}
.chatp header strong{font-size:1rem;display:block}
.chatp header p{color:#A6B0B2;font-size:.8125rem;margin-top:2px}
.chatp .acts{padding:14px;display:flex;flex-direction:column;gap:8px}
.chatp .acts a,.chatp .acts button{display:flex;align-items:center;gap:11px;
  border:1px solid var(--line);border-radius:6px;padding:12px 14px;
  font-size:.9375rem;font-weight:500;text-decoration:none;color:var(--ink);
  background:var(--surface);text-align:start;width:100%}
.chatp .acts a::after,.chatp .acts button::after{content:"›";
  margin-inline-start:auto;color:var(--ink-3);font-size:1.1rem}
html[dir=rtl] .chatp .acts a::after,
html[dir=rtl] .chatp .acts button::after{content:"‹"}
.chatp .acts a:hover,.chatp .acts button:hover{border-color:var(--accent);
  color:var(--accent);background:var(--mint)}
.chatp .acts a:hover::after,.chatp .acts button:hover::after{color:var(--accent)}
.chatp .acts svg{flex:none;color:var(--accent)}
.chatp .note{padding:0 16px 14px;font-size:.75rem;color:var(--ink-3)}
@media (prefers-reduced-motion:reduce){.chatp{transition:none}}

/* ── imagery on cards ────────────────────────────────────────────────── */
.proj .pimg{border-bottom:1px solid var(--line);background:var(--paper)}
.proj .pimg img{width:100%;height:190px;object-fit:cover;display:block}
.post .pimg{border:1px solid var(--line);border-radius:3px;overflow:hidden;
  background:var(--paper)}
.post .pimg img{width:100%;aspect-ratio:561/306;object-fit:cover;display:block}
.svc h3{display:flex;align-items:center;gap:10px}
.svc .ico{width:34px;height:34px;flex:none;display:flex;align-items:center;
  justify-content:center;background:var(--well);border-radius:3px;padding:5px}
.svc .ico img{max-width:100%;max-height:100%}
.svc-art{background:var(--mint)}
.svc-art img{aspect-ratio:16/9;object-fit:contain;padding:26px}

/* ── print ───────────────────────────────────────────────────────────── */
@media print{
  /* always print the light palette, whatever theme the screen used */
  :root,:root[data-theme="dark"]{
    --bg:#fff;--surface:#fff;--paper:#fff;--mint:#fff;--well:#fff;
    --ink:#000;--ink-2:#333;--ink-3:#555;--line:#bbb;--line-2:#999;
    --accent:#000;--accent-d:#000;--accent-contrast:#fff;--band:#fff;
    --band-sub:#333}
  .hdr,.ftr,.cta,.map,.map-tabs,.filters,.skip,.hero-cta,.socrow,.soc,
  .drawer,.scrim,.toast,.burger,.loadmore,.mobfilter,.chatb,.chatp,
  .tbtn{display:none!important}
  .rev{opacity:1!important;transform:none!important}
  body{background:#fff;color:#000}
  .sec,.cat,.phead .wrap{padding-block:16px}
  a{color:#000;text-decoration:none}
  .stats{background:#fff;color:#000;border-block:1px solid #999}
  .stat span{color:#333}
}
"""

# inject the per-theme token sets (kept as one source of truth above)
CSS = CSS.replace("@@LIGHT@@", _LIGHT).replace("@@DARK@@", _DARK)
