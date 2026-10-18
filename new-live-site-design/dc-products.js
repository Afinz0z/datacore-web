/* Datacore product catalogue engine. Left faceted sidebar (category group / type / brand,
   multi-select, live cross-filtered counts), a photo grid shown a page at a time, and a
   request (RFQ) basket persisted per browser. The page carries the first page of cards and the
   starting filters; the catalogue comes from assets1/data/products-data.js (window.DCP_PRODUCTS),
   and descriptions, full spec lists and sources from products-text.js (window.DCP_TEXT), loaded
   once the page has drawn. Both are written by build_products.py.
   Also here: search and filters kept in the address, sorting, suggestions under the search box,
   a quick view per product, recently viewed products, comparing up to four products, a filter
   sheet on phones, and a request list that can be shared as a link or saved as CSV.
   No backend: requests go through dcpDeliver() in dc-forms.js. */
(function () {
  var D = window.DCP_DATA, RAW = window.DCP_PRODUCTS; if (!D || !RAW) return;
  var L = D.labels, AR = D.lang === 'ar', PAGE = D.page || 24, LOW = D.lowAfter || 12, PRE = D.preset || {};
  var KEY = 'dcp-rfq2', SEEN = 'dcp-seen';   // basket is { sku: qty }; recently viewed is [sku]
  var basket = load();

  function load() { try { var v = JSON.parse(localStorage.getItem(KEY)); if (Array.isArray(v)) { var o = {}; v.forEach(function (s) { o[s] = 1; }); return o; } return (v && typeof v === 'object') ? v : {}; } catch (e) { return {}; } }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(basket)); } catch (e) {} }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]; }); }
  function num(n) { return n.toLocaleString('en-US'); }
  function glyph(g, size) {
    return '<svg viewBox="0 0 24 24" width="' + (size || 30) + '" height="' + (size || 30) + '" fill="none" stroke="currentColor" ' +
      'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      (D.glyphs[g] || D.glyphs.rack || '') + '</svg>';
  }
  function fmtDate(iso) {
    var d = new Date(iso + 'T00:00:00');
    if (isNaN(d)) return iso;
    try { return new Intl.DateTimeFormat(AR ? 'ar-u-ca-gregory-nu-latn' : 'en-GB', { day: 'numeric', month: 'long', year: 'numeric' }).format(d); }
    catch (e) { return iso; }
  }

  // letters and digits only, so "DM NVX 360", "dm-nvx-360" and "DMNVX360" all meet (Arabic letters kept)
  var NONWORD = new RegExp('[^a-z0-9' + String.fromCharCode(0x600) + '-' + String.fromCharCode(0x6ff) + ']+', 'g');
  function compact(s) { return String(s).toLowerCase().replace(NONWORD, ''); }
  // words visitors type for things the catalogue names differently
  var SYN = { tv: ['display', 'monitor'], screen: ['display', 'monitor', 'screen'], monitor: ['monitor', 'display'],
    cctv: ['camera', 'surveillance', 'recorder'], cam: ['camera'], mic: ['microphone', 'mic'], microphone: ['microphone', 'mic'],
    amp: ['amplifier', 'amp'], wifi: ['wireless', 'wi-fi', 'access point', 'wifi'], 'wi-fi': ['wireless', 'wi-fi', 'access point'],
    ap: ['access point'], loudspeaker: ['speaker'], licence: ['licence', 'license'], license: ['license', 'licence'],
    fiber: ['fiber', 'fibre'], fibre: ['fibre', 'fiber'], cabinet: ['cabinet', 'rack'], rack: ['rack', 'cabinet'],
    nvr: ['nvr', 'network video recorder'], dvr: ['dvr', 'recorder'], pa: ['public address', 'paging', 'pa/va'],
    touchscreen: ['touch'], videobar: ['video bar', 'videobar'], colour: ['colour', 'color'], color: ['color', 'colour'],
    grey: ['grey', 'gray'], gray: ['gray', 'grey'], conferencing: ['conference'], patchcord: ['patch cord'] };
  function terms(q) {   // each typed word becomes the ways it could appear
    return q.toLowerCase().split(/\s+/).filter(Boolean).map(function (w) {
      var alts = [w];
      if (w.length > 4 && /ies$/.test(w)) alts.push(w.slice(0, -3) + 'y');
      if (w.length > 4 && /(ch|sh|x|ss)es$/.test(w)) alts.push(w.slice(0, -2));
      if (w.length > 3 && /[^s]s$/.test(w)) alts.push(w.slice(0, -1));
      alts.forEach(function (a) { (SYN[a] || []).forEach(function (s) { if (alts.indexOf(s) < 0) alts.push(s); }); });
      return alts;
    });
  }
  function hit(p, alts) {
    for (var i = 0; i < alts.length; i++) {
      if (p.t.indexOf(alts[i]) > -1) return true;
      var c = compact(alts[i]);
      if (c.length > 1 && p.tc.indexOf(c) > -1) return true;
    }
    // a code typed without a word in the middle: "tlp725c" for "TLP Pro 725C"
    var parts = compact(alts[0]).match(/[a-z]+|[0-9]+[a-z]*/g);
    if (parts && parts.length > 1 && /[a-z]/.test(alts[0]) && /[0-9]/.test(alts[0]) && compact(alts[0]).length > 4)
      return parts.every(function (x) { return p.tc.indexOf(x) > -1; }) && (p.nc || p.tc).indexOf(parts[0]) > -1;
    return false;
  }
  var QT = [];

  // ── catalogue: [sku, name, brand#, category#, icon, photo, card specs, (unused), inStock,
  //    supporting products (row numbers), products it fits (row numbers), own page, small photo] ──
  var GROUP = {}, GORDER = [];
  RAW.groups.forEach(function (g) { GROUP[g[0]] = AR ? g[2] : g[1]; GORDER.push(g[0]); });
  var BY = {};
  var P = RAW.p.map(function (r) {
    var c = RAW.cats[r[3]];
    var p = { sku: r[0], n: r[1], b: r[2] > -1 ? RAW.brands[r[2]] : '', ck: c[0], c: AR ? c[1] : c[0], cx: c[0] + ' ' + c[1], grp: c[2],
      g: r[4], photo: r[5], specs: r[6] || [], card: r[6] || [], note: r[7] || '', d: '', avail: r[8] ? 'stock' : 'lead', kids: r[9] || [], fits: r[10] || [],
      page: r[11] ? r[11] + (AR ? '-ar' : '') + '.html' : '', sm: !!r[12], src: '', checked: '', model: '', keys: [] };
    index(p);
    BY[p.sku] = p;
    return p;
  });
  function index(p) {   // what search looks through
    p.t = (p.n + ' ' + p.b + ' ' + p.sku + ' ' + p.model + ' ' + p.cx + ' ' + GROUP[p.grp] + ' ' +
      p.specs.map(function (s) { return s[1]; }).join(' ') + ' ' + (p.d || p.note)).toLowerCase();
    p.tc = compact(p.t); p.nc = compact(p.n + ' ' + p.sku);
  }
  P.forEach(function (p, i) { p.i = i; });
  P.forEach(function (p) {   // row numbers -> products
    p.kids = p.kids.map(function (i) { return P[i]; }); p.fits = p.fits.map(function (i) { return P[i]; });
  });
  var hasStock = P.some(function (p) { return p.avail === 'stock'; });
  // requests saved before a catalogue update may name products that are gone
  Object.keys(basket).forEach(function (s) { if (!BY[s]) delete basket[s]; }); save();

  // descriptions, full spec lists, model codes and the maker's page arrive in a second file
  var TEXT = false, textWait = [];
  function withText(cb) {
    if (TEXT || !D.textUrl) { cb(); return; }
    textWait.push(cb);
    if (textWait.length > 1) return;
    var sc = document.createElement('script'); sc.src = D.textUrl; sc.async = true;
    sc.onerror = function () {   // try again on the next request for it; meanwhile show what the cards know
      sc.remove();
      var w = textWait; textWait = []; w.forEach(function (f) { f(); });
    };
    sc.onload = function () {
      var T = window.DCP_TEXT || {};
      P.forEach(function (p, i) {
        p.d = (T.d && T.d[i]) || '';
        if (T.s && T.s[i]) p.specs = T.s[i];
        if (T.src && T.src[i]) { p.src = T.src[i][0]; p.checked = T.src[i][1]; }
        if (T.m && T.m[i]) p.model = T.m[i];
        if (T.k && T.k[i]) p.keys = T.k[i];   // shared spec names, row by row (spec_names.json)
        index(p);
      });
      TEXT = true;
      var w = textWait; textWait = []; w.forEach(function (f) { f(); });
    };
    document.head.appendChild(sc);
  }

  function availName(a) { return a === 'stock' ? L.in_stock : L.on_order; }
  // the card's spec lines and description note are chosen by build_products (card_specs, card_note)
  function cardSpecs(p) { return p.card; }
  function alt(p) { return p.photo.indexOf('brands/') === 0 ? ((D.logoAlt || {})[p.b] || p.b) + ' logo' : p.n; }
  function smallSrc(p) { return D.photoDir + esc(p.sm ? p.photo.replace('/', '/sm/') : p.photo); }
  function imgHTML(p, i, big) {   // same markup as build_products.img_html
    var src = D.photoDir + esc(p.photo);
    var set = !big && p.sm ? ' srcset="' + smallSrc(p) + ' 300w, ' + src + ' 600w" sizes="' + D.sizes + '"' : '';
    return '<img src="' + src + '"' + set + ' alt="' + esc(alt(p)) + '" width="600" height="600" decoding="async"' +
      (i >= LOW ? ' fetchpriority="low"' : '') + '>';
  }
  function thumb(p) {   // small picture for lists: suggestions, recently viewed, related, compare
    return p.photo ? '<span class="dcp-th"><img src="' + smallSrc(p) + '" alt="" width="300" height="300" decoding="async"></span>'
      : '<span class="dcp-th dcp-noimg">' + glyph(p.g, 22) + '</span>';
  }
  function miniHTML(p) {
    return '<button type="button" class="dcp-mini" data-open="' + esc(p.sku) + '">' + thumb(p) +
      '<span class="dcp-mini-t" dir="auto">' + esc(p.n) + '</span><span class="dcp-mini-b" dir="ltr">' + esc(p.b || p.sku) + '</span></button>';
  }
  function brandHTML(p) { return p.b ? '<span class="dcp-card-brand" dir="ltr">' + esc(p.b) + '</span>' : '<span class="dcp-card-brand"></span>'; }
  function availHTML(p) {
    return p.avail === 'stock' ? '<span class="dcp-badge stock">' + L.in_stock + '</span>' : '<span class="dcp-badge lead">' + L.on_order + '</span>';
  }
  function relHTML(p) {
    var b = '';
    if (p.kids.length) b += '<button type="button" class="dcp-more" data-rel="' + esc(p.sku) + '">' + L.rel_acc.replace('{n}', p.kids.length) + '</button>';
    if (p.fits.length) b += '<button type="button" class="dcp-more" data-rel="' + esc(p.sku) + '">' + L.rel_for.replace('{n}', p.fits.length) + '</button>';
    return b ? '<div class="dcp-card-rel">' + b + '</div>' : '';
  }
  function qtyHTML(p) {   // same markup as build_products.qty_html
    return '<div class="dcp-add-row"><div class="dcp-qty">' +
      '<button class="dcp-qb" type="button" data-q="-1" aria-label="' + esc(L.dec) + '">&minus;</button>' +
      '<input class="dcp-qn" type="text" inputmode="numeric" value="1" aria-label="' + esc(L.qty) + '" data-sku="' + esc(p.sku) + '">' +
      '<button class="dcp-qb" type="button" data-q="1" aria-label="' + esc(L.inc) + '">+</button>' +
      '</div><button class="dcp-add" type="button" data-sku="' + esc(p.sku) + '">' + L.add + '</button></div>';
  }
  function cmpBox(p) {
    return '<label class="dcp-cmp"><input type="checkbox" data-cmp="' + esc(p.sku) + '"' + (cmp.indexOf(p.sku) > -1 ? ' checked' : '') +
      '><span>' + L.cmp + '</span></label>';
  }
  function cardHTML(p, i) {   // same markup as build_products.card_html
    var specs = cardSpecs(p).map(function (s) {
      return '<div><dt>' + esc(s[0]) + '</dt><dd dir="ltr">' + esc(s[1]) + '</dd></div>';
    }).join('');
    var block = (specs ? '<dl class="dcp-specs">' + specs + '</dl>' : '') +
      (p.note ? '<p class="dcp-card-d" dir="auto">' + esc(p.note) + '</p>' : '');
    var media = p.photo
      ? '<div class="dcp-card-photo">' + imgHTML(p, i) + '</div>'
      : '<div class="dcp-card-photo dcp-noimg"><span class="dcp-card-ic">' + glyph(p.g) + '</span></div>';
    var name = p.page
      ? '<a class="dcp-open" href="' + esc(p.page) + '" data-open="' + esc(p.sku) + '">' + esc(p.n) + '</a>'
      : '<button type="button" class="dcp-open" data-open="' + esc(p.sku) + '">' + esc(p.n) + '</button>';
    return '<article class="dcp-card" data-sku="' + esc(p.sku) + '">' + media +
      '<div class="dcp-card-top">' + brandHTML(p) + availHTML(p) + '</div>' +
      '<h3 dir="auto">' + name + '</h3>' +
      '<div class="dcp-card-meta"><span class="dcp-tag">' + esc(p.c) + '</span></div>' +
      block + relHTML(p) +
      '<div class="dcp-card-sub"><span class="dcp-card-sku" dir="ltr">' + esc(p.sku) + '</span>' + cmpBox(p) + '</div>' +
      qtyHTML(p) + '</article>';
  }

  // keep the focus inside an open window
  function trap(e, root) {
    if (e.key !== 'Tab') return;
    var f = [].filter.call(root.querySelectorAll('a[href],button:not([disabled]),input,select,textarea'), function (x) { return x.offsetParent !== null; });
    if (!f.length) return;
    if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
    else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
  }
  function copyText(text, btn) {
    var done = function () { if (!btn) return; var t = btn.textContent; btn.textContent = L.copied; setTimeout(function () { btn.textContent = t; }, 1800); };
    if (navigator.clipboard && window.isSecureContext) { navigator.clipboard.writeText(text).then(done, function () { fallback(); }); return; }
    fallback();
    function fallback() {
      var ta = document.createElement('textarea'); ta.value = text; ta.setAttribute('readonly', ''); ta.style.cssText = 'position:fixed;opacity:0';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(); } catch (e) { window.prompt('', text); }
      ta.remove();
    }
  }

  // ── faceted state + filtering (multi-select) ────────────────────
  var S = { q: '', grp: [], cat: [], brand: [], avail: [], rel: '', sort: '' };
  function base() {
    if (!S.rel || !BY[S.rel]) return P;
    var p = BY[S.rel], seen = {}, out = [];
    [p].concat(p.kids, p.fits).forEach(function (x) { if (!seen[x.sku]) { seen[x.sku] = 1; out.push(x); } });
    return out;
  }
  var DIMS = ['grp', 'cat', 'brand', 'avail'];
  var GET = { grp: function (p) { return p.grp; }, cat: function (p) { return p.ck; },
    brand: function (p) { return p.b || null; }, avail: function (p) { return p.avail; } };
  var CAT_LABEL = {};
  P.forEach(function (p) { CAT_LABEL[p.ck] = p.c; });
  var LABEL = { grp: function (v) { return GROUP[v] || v; }, cat: function (v) { return CAT_LABEL[v] || v; },
    brand: function (v) { return v; }, avail: availName };
  function match(p, skip) {
    if (S.q) {
      for (var i = 0; i < QT.length; i++) if (!hit(p, QT[i])) return false;
    }
    for (var j = 0; j < DIMS.length; j++) {
      var d = DIMS[j];
      if (d !== skip && S[d].length && S[d].indexOf(GET[d](p)) < 0) return false;
    }
    return true;
  }
  // counts for a dimension ignore that dimension's own selection (so you can
  // still see and add sibling options), but respect every other active filter
  function tally(dim) {
    QT = terms(S.q);
    var m = {}, get = GET[dim];
    base().forEach(function (p) { if (match(p, dim)) { var v = get(p); if (v != null) m[v] = (m[v] || 0) + 1; } });
    return m;
  }
  // a category page opens on its own group; that alone is not a filter the visitor chose
  function onPreset() { return !!(PRE.grp && S.grp.join('|') === PRE.grp.join('|')); }
  function idle() {
    return !S.q && !S.rel && !S.cat.length && !S.brand.length && !S.avail.length && (!S.grp.length || onPreset());
  }

  // ── search and filters live in the address, so a view can be shared and Back works ──
  var search = document.getElementById('dcp-search'), sortEl = document.getElementById('dcp-sort'), openSku = '';
  function readURL() {
    var u = new URLSearchParams(location.search), any = false;
    S.q = (u.get('q') || '').trim(); if (S.q) any = true;
    DIMS.forEach(function (d) { if (u.has(d)) any = true; S[d] = u.getAll(d).filter(Boolean); });
    S.rel = BY[u.get('rel')] ? u.get('rel') : '';
    S.sort = /^(name|brand)$/.test(u.get('sort') || '') ? u.get('sort') : '';
    if (!any && !S.rel && PRE.grp) S.grp = PRE.grp.slice();
    search.value = S.q;
    if (sortEl) sortEl.value = S.sort;
    return u;
  }
  function writeURL(push) {
    var u = new URLSearchParams();
    if (S.q) u.set('q', S.q);
    DIMS.forEach(function (d) {
      if (d === 'grp' && PRE.grp) {
        if (onPreset()) return;
        if (!S.grp.length) { u.set('grp', ''); return; }   // the visitor cleared the page's own group
      }
      S[d].forEach(function (v) { u.append(d, v); });
    });
    if (S.rel) u.set('rel', S.rel);
    if (S.sort) u.set('sort', S.sort);
    if (openSku) u.set('p', openSku);
    var qs = u.toString(), url = location.pathname + (qs ? '?' + qs : '');
    if (url === location.pathname + location.search) return;
    try { history[push ? 'pushState' : 'replaceState'](null, '', url); } catch (e) {}
  }
  function stateKey() { return JSON.stringify([S.q, S.grp, S.cat, S.brand, S.avail, S.rel, S.sort]); }
  window.addEventListener('popstate', function () {
    var before = stateKey(), u = readURL();
    if (stateKey() !== before) { apply(); renderFacets(); }
    var p = u.get('p');
    if (p && BY[p]) openQV(p, true); else closeQV(true);
  });

  // ── left sidebar ────────────────────────────────────────────────
  var facetsEl = document.getElementById('dcp-facets');
  function fgroup(title, dim, counts, limit, order) {
    var all = Object.keys(counts);
    S[dim].forEach(function (s) { if (all.indexOf(s) < 0) all.push(s); });
    var picker = dim === 'brand' || dim === 'cat';
    if (order) all.sort(function (a, b) { return order.indexOf(a) - order.indexOf(b); });
    else if (picker) all.sort(function (a, b) { return (counts[b] || 0) - (counts[a] || 0) || LABEL[dim](a).localeCompare(LABEL[dim](b), AR ? 'ar' : 'en'); });
    else all.sort(function (a, b) { return LABEL[dim](a).localeCompare(LABEL[dim](b), AR ? 'ar' : 'en'); });
    var open = all.length <= limit || (!picker && S['_m_' + dim]);
    var list = open ? all : all.slice(0, limit);
    if (picker) S[dim].forEach(function (s) { if (list.indexOf(s) < 0) list.push(s); });
    var h = '<div class="dcp-fgroup"><h4>' + esc(title) + '</h4>';
    list.forEach(function (v) {
      var c = counts[v] || 0, on = S[dim].indexOf(v) > -1;
      h += '<label class="' + (c === 0 && !on ? 'off' : '') + '"><input type="checkbox" data-dim="' + dim +
        '" value="' + esc(v) + '"' + (on ? ' checked' : '') + '><span>' + esc(LABEL[dim](v)) +
        '</span><span class="dcp-fc">' + c + '</span></label>';
    });
    if (picker && all.length > limit)
      h += '<button class="dcp-more" type="button" data-pick="' + dim + '">' + (dim === 'brand' ? L.all_brands : L.all_types).replace('{n}', num(Object.keys(counts).length)) + '</button>';
    else if (all.length > list.length)
      h += '<button class="dcp-more" type="button" data-more="' + dim + '">+ ' + (all.length - list.length) + '</button>';
    return h + '</div>';
  }
  function renderFacets() {
    var n = S.grp.length + S.cat.length + S.brand.length + S.avail.length + (S.rel ? 1 : 0);
    var h = '<div class="dcp-fhead"><span>' + L.refine + '</span>' +
      (n ? '<button class="dcp-clearall" type="button" id="dcp-clearall">' + L.clear + '</button>' : '') + '</div>';
    h += fgroup(L.category, 'grp', tally('grp'), 12, GORDER);
    h += fgroup(L.type, 'cat', tally('cat'), 8);
    h += fgroup(L.brand, 'brand', tally('brand'), 8);
    if (hasStock) h += fgroup(L.availability, 'avail', tally('avail'), 4);   // only when stock differs
    facetsEl.innerHTML = '<div id="dcp-reqslot"></div>' + h;
    drawReq();
  }
  // on desktop the request button sits at the top of the sidebar, which stays in view, instead of
  // floating over the cards (phones keep the floating one; the sidebar is a sheet there)
  var CART = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="9" cy="20" r="1.35"/><circle cx="18" cy="20" r="1.35"/><path d="M2.5 3h2.3l2.2 11.4a1.6 1.6 0 0 0 1.6 1.3h8.2a1.6 1.6 0 0 0 1.55-1.2L21.5 7H6.3"/></svg>';
  function drawReq() {
    var slot = document.getElementById('dcp-reqslot'); if (!slot) return;
    var n = Object.keys(basket).length;
    slot.innerHTML = n ? '<button type="button" class="dcp-reqbtn" id="dcp-reqbtn">' + CART + '<span>' + L.req_title +
      '</span><span class="dcp-fabn">' + n + '</span></button>' : '';
  }
  function shown_(el) { return !!el && el.getBoundingClientRect().width > 0; }

  // ── results a page at a time, count, active chips ───────────────
  var grid = document.getElementById('dcp-grid');
  var countEl = document.getElementById('dcp-count'), chipsEl = document.getElementById('dcp-chips'),
    emptyEl = document.getElementById('dcp-empty'), moreBtn = document.getElementById('dcp-more');
  var results = P, shown = 0;
  function showCount() {
    countEl.innerHTML = results.length > shown
      ? L.showing.replace('{n}', '<b>' + num(shown) + '</b>').replace('{t}', num(results.length))
      : '<b>' + num(results.length) + '</b> ' + (results.length === 1 ? L.product_one : L.product_many);
    emptyEl.hidden = results.length > 0;
    if (moreBtn) moreBtn.hidden = shown >= results.length;
  }
  function byName(a, b) { return a.n.localeCompare(b.n, 'en', { numeric: true, sensitivity: 'base' }) || a.i - b.i; }
  function apply(how) {   // how: 'push' or 'replace' records the view in the address; nothing leaves it alone
    QT = terms(S.q);
    results = base().filter(function (p) { return match(p, null); });
    if (S.sort === 'name') results.sort(byName);
    else if (S.sort === 'brand') results.sort(function (a, b) { return (!a.b) - (!b.b) || a.b.localeCompare(b.b, 'en', { sensitivity: 'base' }) || byName(a, b); });
    else if (S.q) {   // best first: the exact model, then names holding every word, then the rest
      var qc = compact(S.q);
      var rank = function (p) {
        if (compact(p.sku) === qc || p.nc.indexOf(qc) === 0) return 0;
        if (p.nc.indexOf(qc) > -1) return 1;
        var nm = { t: (p.n + ' ' + p.sku).toLowerCase(), tc: p.nc };
        return QT.every(function (a) { return hit(nm, a); }) ? 2 : 3;
      };
      results = results.map(function (p) { return [rank(p), p.i, p]; })
        .sort(function (a, b) { return a[0] - b[0] || a[1] - b[1]; }).map(function (x) { return x[2]; });
    }
    shown = Math.min(PAGE, results.length);
    grid.innerHTML = results.slice(0, shown).map(cardHTML).join('');
    showCount(); renderChips(); syncButtons(); drawRecent(); sheetCount(); noteEmpty();
    if (how) writeURL(how === 'push');
  }
  function more() {
    var from = shown;
    shown = Math.min(shown + PAGE, results.length);
    grid.insertAdjacentHTML('beforeend', results.slice(from, shown).map(cardHTML).join(''));
    showCount(); syncButtons();
  }
  if (moreBtn) moreBtn.addEventListener('click', more);
  function renderChips() {
    var ch = [];
    if (S.rel && BY[S.rel]) ch.push(['rel', S.rel, L.rel_chip.replace('{n}', BY[S.rel].n)]);
    DIMS.forEach(function (d) { S[d].forEach(function (v) { ch.push([d, v, LABEL[d](v)]); }); });
    chipsEl.innerHTML = ch.map(function (x) {
      return '<span class="dcp-chip">' + esc(x[2]) + '<button type="button" data-chip="' + x[0] +
        '" data-val="' + esc(x[1]) + '" aria-label="' + L.remove + ': ' + esc(x[2]) + '">&times;</button></span>';
    }).join('');
  }
  // searches that find nothing tell us what visitors expect to find; recorded only with analytics consent
  var emptyT;
  function noteEmpty() {
    clearTimeout(emptyT);
    if (!S.q || results.length) return;
    var q = S.q;
    emptyT = setTimeout(function () {
      if (S.q === q && window.google_tag_manager && window.dataLayer)
        window.dataLayer.push({ event: 'dcp_search_none', search_term: q, page_language: D.lang });
    }, 1500);
  }

  facetsEl.addEventListener('change', function (ev) {
    var d = ev.target.getAttribute('data-dim'); if (!d) return;
    var v = ev.target.value, arr = S[d], i = arr.indexOf(v);
    if (ev.target.checked) { if (i < 0) arr.push(v); } else if (i > -1) arr.splice(i, 1);
    apply('push'); renderFacets();
  });
  facetsEl.addEventListener('click', function (ev) {
    if (ev.target.closest('#dcp-reqbtn')) { openD(); return; }
    if (ev.target.id === 'dcp-clearall') { DIMS.forEach(function (d) { S[d] = []; }); S.rel = ''; apply('push'); renderFacets(); return; }
    var m = ev.target.getAttribute('data-more'); if (m) { S['_m_' + m] = true; renderFacets(); }
    var pk = ev.target.getAttribute('data-pick'); if (pk) openPick(pk, ev.target);
  });
  if (sortEl) sortEl.addEventListener('change', function () { S.sort = sortEl.value; apply('push'); });

  // -- picker window for brands and types: search, a category filter, the starting letters, and
  //    every value in columns. Ticks wait in "pending" until "Show N products" applies them. --
  var pick = null, pickDim = '', pending = [], pickLetter = '', pickGrp = '', pickQ = '';
  function initial(s) { var c = s.trim().charAt(0).toUpperCase(); return /[0-9]/.test(c) ? '#' : c; }
  function buildPick() {
    pick = document.createElement('div');
    pick.className = 'dcp-pick'; pick.hidden = true;
    pick.innerHTML = '<div class="dcp-pick-bg" data-close="1"></div>' +
      '<div class="dcp-pick-box" role="dialog" aria-modal="true" aria-labelledby="dcp-pick-h">' +
        '<div class="dcp-pick-head"><h2 id="dcp-pick-h"></h2><span class="dcp-pick-n" id="dcp-pick-n"></span>' +
          '<button class="dcp-pick-x" type="button" data-close="1" aria-label="' + L.close + '">&times;</button></div>' +
        '<div class="dcp-pick-tools"><div class="dcp-search-in"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>' +
          '<input id="dcp-pick-q" type="search" autocomplete="off"></div>' +
          '<label class="dcp-pick-sel"><span>' + L.in_cat + '</span><select id="dcp-pick-grp"></select></label></div>' +
        '<div class="dcp-pick-az" id="dcp-pick-az" role="group"></div>' +
        '<div class="dcp-pick-list" id="dcp-pick-list"></div>' +
        '<div class="dcp-pick-foot"><button class="dcp-clearall" type="button" id="dcp-pick-clear">' + L.clear_sel + '</button>' +
          '<span class="dcp-pick-sum" id="dcp-pick-sum"></span>' +
          '<button class="dcp-btn" type="button" id="dcp-pick-go"></button></div>' +
      '</div>';
    document.body.appendChild(pick);
    pick.addEventListener('click', function (e) {
      if (e.target.closest('[data-close]')) { closePick(); return; }
      var lb = e.target.closest('[data-letter]');
      if (lb) { pickLetter = lb.getAttribute('data-letter'); drawPick(); return; }
      if (e.target.id === 'dcp-pick-clear') { pending = []; drawPick(); return; }
      if (e.target.closest('#dcp-pick-go')) { S[pickDim] = pending.slice(); closePick(); apply('push'); renderFacets(); }
    });
    pick.addEventListener('change', function (e) {
      if (e.target.id === 'dcp-pick-grp') { pickGrp = e.target.value; drawPick(); return; }
      var v = e.target.getAttribute('data-v'); if (v == null) return;
      var i = pending.indexOf(v);
      if (e.target.checked) { if (i < 0) pending.push(v); } else if (i > -1) pending.splice(i, 1);
      drawFoot();
    });
    var typing2;
    pick.querySelector('#dcp-pick-q').addEventListener('input', function (e) {
      clearTimeout(typing2); typing2 = setTimeout(function () { pickQ = e.target.value.trim().toLowerCase(); drawPick(); }, 100);
    });
    pick.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { e.stopPropagation(); closePick(); return; }
      trap(e, pick);
    });
  }
  // counts for each value under every other active filter, optionally within one category group
  function pickCounts() {
    var m = {}, get = GET[pickDim];
    base().forEach(function (p) {
      if ((!pickGrp || p.grp === pickGrp) && match(p, pickDim)) { var v = get(p); if (v != null) m[v] = (m[v] || 0) + 1; }
    });
    return m;
  }
  function drawPick() {
    var counts = pickCounts(), lab = LABEL[pickDim];
    var vals = Object.keys(counts);
    pending.forEach(function (s) { if (vals.indexOf(s) < 0) vals.push(s); });
    vals.sort(function (a, b) { return lab(a).localeCompare(lab(b), AR ? 'ar' : 'en', { sensitivity: 'base' }); });
    var letters = [];
    vals.forEach(function (v) { var c = initial(lab(v)); if (letters.indexOf(c) < 0) letters.push(c); });
    if (pickLetter && letters.indexOf(pickLetter) < 0) pickLetter = '';
    pick.querySelector('#dcp-pick-az').innerHTML =
      '<button type="button" data-letter="" aria-pressed="' + (!pickLetter) + '">' + L.all + '</button>' +
      letters.map(function (c) { return '<button type="button" data-letter="' + esc(c) + '" aria-pressed="' + (pickLetter === c) + '">' + esc(c) + '</button>'; }).join('');
    var list = vals.filter(function (v) {
      return (!pickLetter || initial(lab(v)) === pickLetter) && (!pickQ || lab(v).toLowerCase().indexOf(pickQ) > -1);
    });
    var h = '', last = '';
    list.forEach(function (v) {
      var c = initial(lab(v)), n = counts[v] || 0, on = pending.indexOf(v) > -1;
      if (c !== last) { h += '<h3>' + esc(c) + '</h3>'; last = c; }
      h += '<label class="' + (n === 0 && !on ? 'off' : '') + '"><input type="checkbox" data-v="' + esc(v) + '"' + (on ? ' checked' : '') +
        '><span dir="auto">' + esc(lab(v)) + '</span><span class="dcp-fc">' + n + '</span></label>';
    });
    pick.querySelector('#dcp-pick-list').innerHTML = h || '<p class="dcp-pick-none">' + (pickDim === 'brand' ? L.no_brand : L.no_type) + '</p>';
    pick.querySelector('#dcp-pick-n').textContent = L.pick_n.replace('{n}', num(list.length));
    drawFoot();
  }
  function drawFoot() {
    var keep = S[pickDim]; S[pickDim] = pending;               // count the results as if applied
    var n = base().filter(function (p) { return match(p, null); }).length;
    S[pickDim] = keep;
    pick.querySelector('#dcp-pick-sum').textContent = pending.length ? L.picked.replace('{n}', pending.length) : '';
    pick.querySelector('#dcp-pick-go').textContent = L.show_n.replace('{n}', num(n));
  }
  function openPick(dim) {
    if (!pick) buildPick();
    pickDim = dim; pending = S[dim].slice(); pickLetter = ''; pickQ = '';
    pickGrp = S.grp.length === 1 ? S.grp[0] : '';
    pick.querySelector('#dcp-pick-h').textContent = dim === 'brand' ? L.brand : L.type;
    var q = pick.querySelector('#dcp-pick-q'); q.value = ''; q.placeholder = dim === 'brand' ? L.find_brand : L.find_type;
    pick.querySelector('#dcp-pick-grp').innerHTML = '<option value="">' + L.any_cat + '</option>' +
      GORDER.map(function (g) { return '<option value="' + g + '"' + (g === pickGrp ? ' selected' : '') + '>' + esc(GROUP[g]) + '</option>'; }).join('');
    drawPick();
    pick.hidden = false; document.documentElement.classList.add('dcp-pick-open');
    q.focus();
  }
  function closePick() {
    pick.hidden = true;
    if (!sheet || sheet.hidden) document.documentElement.classList.remove('dcp-pick-open');
    var back = document.querySelector('#dcp-facets [data-pick="' + pickDim + '"]');
    if (back) back.focus();
  }
  chipsEl.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-chip]'); if (!b) return;
    var d = b.getAttribute('data-chip'), v = b.getAttribute('data-val');
    if (d === 'rel') S.rel = '';
    else { var i = S[d].indexOf(v); if (i > -1) S[d].splice(i, 1); }
    apply('push'); renderFacets();
  });

  // ── search box with suggestions ─────────────────────────────────
  var ac = document.getElementById('dcp-ac'), acIdx = -1, typing;
  search.addEventListener('input', function () {
    clearTimeout(typing);
    typing = setTimeout(function () { S.q = search.value.trim(); apply('replace'); renderFacets(); drawAC(); }, 120);
  });
  function drawAC() {
    if (!ac) return;
    if (!S.q || document.activeElement !== search || !results.length) { hideAC(); return; }
    var top = results.slice(0, 6);
    acIdx = -1; search.removeAttribute('aria-activedescendant');
    ac.innerHTML = top.map(function (p, i) {
      return '<div class="dcp-ac-it" role="option" id="dcp-ac-' + i + '" data-open="' + esc(p.sku) + '" aria-selected="false">' + thumb(p) +
        '<span class="dcp-ac-t"><span dir="auto">' + esc(p.n) + '</span><small dir="ltr">' + esc((p.b ? p.b + '  ' : '') + p.sku) + '</small></span></div>';
    }).join('') + (results.length > top.length
      ? '<div class="dcp-ac-it dcp-ac-all" role="option" id="dcp-ac-' + top.length + '" data-acall="1" aria-selected="false">' + L.ac_all.replace('{n}', num(results.length)) + '</div>' : '');
    ac.hidden = false; search.setAttribute('aria-expanded', 'true');
  }
  function hideAC() {
    if (!ac) return;
    ac.hidden = true; search.setAttribute('aria-expanded', 'false'); search.removeAttribute('aria-activedescendant'); acIdx = -1;
  }
  function pickAC(el) {
    hideAC();
    if (el.hasAttribute('data-acall')) { countEl.scrollIntoView({ block: 'start' }); return; }
    openQV(el.getAttribute('data-open'));
  }
  if (ac) {
    ac.addEventListener('mousedown', function (e) { e.preventDefault(); });   // keep the focus in the box
    ac.addEventListener('click', function (e) { var it = e.target.closest('[role=option]'); if (it) pickAC(it); });
    search.addEventListener('keydown', function (e) {
      if (ac.hidden) { if (e.key === 'ArrowDown' && S.q) drawAC(); return; }
      var opts = ac.querySelectorAll('[role=option]');
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        acIdx = e.key === 'ArrowDown' ? (acIdx + 1) % opts.length : (acIdx <= 0 ? opts.length - 1 : acIdx - 1);
        opts.forEach(function (o, i) { o.setAttribute('aria-selected', String(i === acIdx)); });
        search.setAttribute('aria-activedescendant', opts[acIdx].id);
        opts[acIdx].scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'Enter') {
        if (acIdx > -1) { e.preventDefault(); pickAC(opts[acIdx]); } else hideAC();
      } else if (e.key === 'Escape') { e.stopPropagation(); hideAC(); }
    });
    search.addEventListener('blur', function () { setTimeout(hideAC, 120); });
    search.addEventListener('focus', function () { if (S.q) drawAC(); });
  }

  // ── recently viewed (this browser only) ─────────────────────────
  var recentEl = document.getElementById('dcp-recent');
  var seen = (function () { try { var v = JSON.parse(localStorage.getItem(SEEN)); return Array.isArray(v) ? v.filter(function (s) { return BY[s]; }) : []; } catch (e) { return []; } })();
  function noteSeen(sku) {
    seen = [sku].concat(seen.filter(function (s) { return s !== sku; })).slice(0, 12);
    try { localStorage.setItem(SEEN, JSON.stringify(seen)); } catch (e) {}
  }
  function drawRecent() {
    if (!recentEl) return;
    if (!idle() || !seen.length) { recentEl.hidden = true; recentEl.innerHTML = ''; return; }
    recentEl.hidden = false;
    recentEl.innerHTML = '<div class="dcp-recent-head"><h2>' + L.recent + '</h2><button type="button" class="dcp-clearall" data-seen-clear="1">' +
      L.recent_clear + '</button></div><div class="dcp-recent-row">' + seen.map(function (s) { return miniHTML(BY[s]); }).join('') + '</div>';
  }
  if (recentEl) recentEl.addEventListener('click', function (e) {
    if (e.target.closest('[data-seen-clear]')) { seen = []; try { localStorage.removeItem(SEEN); } catch (x) {} drawRecent(); return; }
    var o = e.target.closest('[data-open]'); if (o) openQV(o.getAttribute('data-open'));
  });

  // ── quick view: everything about one product without leaving the catalogue ──
  var qv = null, qvPushed = false, qvBack = null;
  function buildQV() {
    qv = document.createElement('div'); qv.className = 'dcp-pick dcp-qv'; qv.hidden = true;
    qv.innerHTML = '<div class="dcp-pick-bg" data-qclose="1"></div>' +
      '<div class="dcp-pick-box" role="dialog" aria-modal="true" aria-labelledby="dcp-qv-h">' +
      '<button class="dcp-pick-x dcp-qv-x" type="button" data-qclose="1" aria-label="' + L.close + '">&times;</button>' +
      '<div class="dcp-qv-body" id="dcp-qv-body"></div></div>';
    document.body.appendChild(qv);
    qv.addEventListener('click', function (e) {
      if (e.target.closest('[data-qclose]')) { closeQV(); return; }
      var o = e.target.closest('[data-open]'); if (o) { openQV(o.getAttribute('data-open')); return; }
      var rl = e.target.closest('[data-rel]'); if (rl) { closeQV(); showRel(rl.getAttribute('data-rel')); return; }
      var cp = e.target.closest('[data-copy]');
      if (cp) { var p = BY[openSku]; copyText(p && p.page ? new URL(p.page, location.href).href : location.href, cp); return; }
      actions(e);
    });
    qv.addEventListener('change', changes);
    qv.addEventListener('keydown', function (e) { if (e.key === 'Escape') { e.stopPropagation(); closeQV(); } else trap(e, qv); });
  }
  function qvHTML(p) {
    var specs = p.specs.map(function (s) { return '<div><dt>' + esc(s[0]) + '</dt><dd dir="ltr">' + esc(s[1]) + '</dd></div>'; }).join('');
    var note = p.src
      ? '<p class="dcp-qv-src">' + esc(L.qv_checked.replace('{d}', fmtDate(p.checked))) + ' <a href="' + esc(p.src) + '" target="_blank" rel="noopener nofollow">' + L.qv_maker + '</a></p>'
      : (TEXT && specs ? '<p class="dcp-qv-src">' + L.qv_inv + '</p>' : '');
    function rel(title, list) {
      if (!list.length) return '';
      return '<section class="dcp-qv-rel"><h3>' + title + ' <span class="dcp-fc">' + list.length + '</span></h3><div class="dcp-recent-row">' +
        list.slice(0, 8).map(miniHTML).join('') + '</div>' +
        (list.length > 8 ? '<button type="button" class="dcp-more" data-rel="' + esc(p.sku) + '">' + L.qv_all + '</button>' : '') + '</section>';
    }
    return '<div class="dcp-qv-grid">' +
      (p.photo ? '<div class="dcp-card-photo">' + imgHTML(p, 0, true) + '</div>'
               : '<div class="dcp-card-photo dcp-noimg"><span class="dcp-card-ic">' + glyph(p.g, 48) + '</span></div>') +
      '<div class="dcp-qv-info"><div class="dcp-card-top">' + brandHTML(p) + availHTML(p) + '</div>' +
        '<h2 id="dcp-qv-h" dir="auto">' + esc(p.n) + '</h2>' +
        '<p class="dcp-qv-meta"><span class="dcp-tag">' + esc(p.c) + '</span><span class="dcp-card-sku" dir="ltr">' + esc(p.sku) + '</span></p>' +
        (p.d ? '<p class="dcp-qv-d" dir="auto">' + esc(p.d) + '</p>' : '') + qtyHTML(p) +
        '<div class="dcp-qv-links">' + (p.page ? '<a href="' + esc(p.page) + '">' + L.qv_page + '</a>' : '') +
          '<button type="button" class="dcp-more" data-copy="1">' + L.qv_link + '</button>' + cmpBox(p) + '</div>' +
      '</div></div>' +
      (specs ? '<section class="dcp-qv-specs"><h3>' + L.qv_specs + '</h3><dl>' + specs + '</dl>' + note + '</section>' : '') +
      rel(L.qv_acc, p.kids) + rel(L.qv_for, p.fits);
  }
  function openQV(sku, fromHistory) {
    var p = BY[sku]; if (!p) return;
    if (!qv) buildQV();
    var wasOpen = !qv.hidden;
    if (!wasOpen) qvBack = document.activeElement;
    openSku = sku;
    var body = qv.querySelector('#dcp-qv-body');
    var draw = function () { if (openSku === sku) { body.innerHTML = qvHTML(p); syncButtons(); } };
    draw(); withText(draw);
    body.scrollTop = 0;
    qv.hidden = false; document.documentElement.classList.add('dcp-pick-open');
    qv.querySelector('.dcp-qv-x').focus();
    noteSeen(sku);
    if (!fromHistory) { writeURL(!wasOpen); if (!wasOpen) qvPushed = true; }
  }
  function closeQV(fromHistory) {
    if (!qv || qv.hidden) return;
    qv.hidden = true; document.documentElement.classList.remove('dcp-pick-open'); openSku = '';
    if (fromHistory) qvPushed = false;
    else if (qvPushed) { qvPushed = false; history.back(); }
    else writeURL(false);
    drawRecent();
    if (qvBack && qvBack.focus && document.contains(qvBack)) qvBack.focus();
  }
  function showRel(sku) {
    S.rel = sku; S.q = ''; search.value = '';
    DIMS.forEach(function (d) { S[d] = []; });
    apply('push'); renderFacets();
    countEl.scrollIntoView({ block: 'start' });
  }

  // ── compare up to four products ─────────────────────────────────
  var cmp = [], tray = null, cmpv = null, cmpMsg = '', cmpT;
  function setCmp(sku, on) {
    var i = cmp.indexOf(sku);
    if (on && i < 0) {
      if (cmp.length >= 4) { cmpMsg = L.cmp_max; clearTimeout(cmpT); cmpT = setTimeout(function () { cmpMsg = ''; syncCmp(); }, 3500); }
      else cmp.push(sku);
    }
    if (!on && i > -1) cmp.splice(i, 1);
    syncCmp();
  }
  function syncCmp() {
    document.querySelectorAll('[data-cmp]').forEach(function (b) { b.checked = cmp.indexOf(b.getAttribute('data-cmp')) > -1; });
    if (!tray) {
      if (!cmp.length) return;
      tray = document.createElement('div'); tray.className = 'dcp-tray'; tray.setAttribute('role', 'region'); tray.setAttribute('aria-label', L.cmp_h);
      document.body.appendChild(tray);
      tray.addEventListener('click', function (e) {
        if (e.target.closest('[data-cmp-go]')) openCmp();
        else if (e.target.closest('[data-cmp-clear]')) { cmp = []; syncCmp(); }
        else { var x = e.target.closest('[data-cmp-x]'); if (x) setCmp(x.getAttribute('data-cmp-x'), false); }
      });
    }
    tray.hidden = !cmp.length;
    tray.innerHTML = '<div class="dcp-tray-items">' + cmp.map(function (s) {
        var p = BY[s]; return '<span class="dcp-tray-it" title="' + esc(p.n) + '">' + thumb(p) + '<button type="button" data-cmp-x="' + esc(s) + '" aria-label="' + esc(L.remove + ': ' + p.n) + '">&times;</button></span>';
      }).join('') + '</div>' +
      '<button type="button" class="dcp-btn" data-cmp-go="1"' + (cmp.length < 2 ? ' disabled' : '') + '>' + L.cmp_n.replace('{n}', cmp.length) + '</button>' +
      '<button type="button" class="dcp-clearall" data-cmp-clear="1">' + L.cmp_clear + '</button>' +
      (cmpMsg ? '<span class="dcp-tray-msg" role="status">' + cmpMsg + '</span>' : '');
  }
  function openCmp() {
    if (cmp.length < 2) return;
    withText(function () {
      if (!cmpv) {
        cmpv = document.createElement('div'); cmpv.className = 'dcp-pick dcp-cmpv'; cmpv.hidden = true;
        cmpv.innerHTML = '<div class="dcp-pick-bg" data-cclose="1"></div><div class="dcp-pick-box" role="dialog" aria-modal="true" aria-labelledby="dcp-cmp-h">' +
          '<div class="dcp-pick-head"><h2 id="dcp-cmp-h">' + L.cmp_h + '</h2>' +
          '<button class="dcp-pick-x" type="button" data-cclose="1" aria-label="' + L.close + '">&times;</button></div>' +
          '<div class="dcp-cmpv-body"></div></div>';
        document.body.appendChild(cmpv);
        cmpv.addEventListener('click', function (e) {
          if (e.target.closest('[data-cclose]')) { closeCmp(); return; }
          var o = e.target.closest('[data-open]'); if (o) { closeCmp(); openQV(o.getAttribute('data-open')); return; }
          var mo = e.target.closest('[data-cmp-more]');
          if (mo) {   // details only one of the products lists
            var open = mo.getAttribute('aria-expanded') !== 'true';
            cmpv.querySelectorAll('.dcp-cmp-more').forEach(function (r) { r.hidden = !open; });
            mo.setAttribute('aria-expanded', String(open));
            mo.textContent = open ? L.cmp_less : L.cmp_more.replace('{n}', mo.getAttribute('data-cmp-more'));
            return;
          }
          actions(e);
        });
        cmpv.addEventListener('keydown', function (e) { if (e.key === 'Escape') { e.stopPropagation(); closeCmp(); } else trap(e, cmpv); });
      }
      var ps = cmp.map(function (s) { return BY[s]; });
      var row = function (th, cells, more) {
        return '<tr' + (more ? ' class="dcp-cmp-more" hidden' : '') + '><th scope="row">' + th + '</th>' +
          cells.map(function (c) { return '<td>' + c + '</td>'; }).join('') + '</tr>';
      };
      // one value, with the maker's own label underneath when it words the spec differently
      var val = function (s, name) {
        return '<div><span dir="ltr">' + esc(s[1]) + '</span>' +
          (s[0].toLowerCase() !== String(name).toLowerCase() ? '<small class="dcp-cmp-lab" dir="ltr">' + esc(s[0]) + '</small>' : '') + '</div>';
      };
      var used = ps.map(function () { return {}; }), body = '';
      // 1. the shared names (spec_names.json), in their order, so the same measure sits on one row
      (D.specNames || []).forEach(function (kn) {
        var cells = ps.map(function (p, j) {
          var out = [];
          p.specs.forEach(function (s, i) { if (p.keys[i] === kn[0]) { used[j][i] = 1; out.push(s); } });
          return out;
        });
        if (cells.some(function (c) { return c.length; }))
          body += row(esc(kn[1]), cells.map(function (c) { return c.map(function (s) { return val(s, kn[1]); }).join(''); }));
      });
      // 2. other rows the makers label alike on two or more products; 3. the rest, behind a button
      var rest = {}, order = [];
      ps.forEach(function (p, j) {
        p.specs.forEach(function (s, i) {
          if (used[j][i]) return;
          var k = s[0].toLowerCase();
          if (!rest[k]) { rest[k] = { label: s[0], cells: ps.map(function () { return []; }) }; order.push(k); }
          rest[k].cells[j].push(s);
        });
      });
      var many = function (k) { return rest[k].cells.filter(function (c) { return c.length; }).length > 1; };
      var shared = order.filter(many), own = order.filter(function (k) { return !many(k); });
      var restRow = function (k, more) {
        return row(esc(rest[k].label), rest[k].cells.map(function (c) { return c.map(function (s) { return val(s, rest[k].label); }).join(''); }), more);
      };
      body += shared.map(function (k) { return restRow(k); }).join('');
      if (own.length) body += '<tr class="dcp-cmp-toggle"><td colspan="' + (ps.length + 1) + '"><button type="button" class="dcp-more" data-cmp-more="' +
        own.length + '" aria-expanded="false">' + L.cmp_more.replace('{n}', own.length) + '</button></td></tr>' +
        own.map(function (k) { return restRow(k, true); }).join('');
      cmpv.querySelector('.dcp-cmpv-body').innerHTML = '<table class="dcp-cmpt"><thead><tr><td></td>' +
        ps.map(function (p) { return '<th scope="col">' + miniHTML(p) + '</th>'; }).join('') + '</tr></thead><tbody>' +
        row(L.brand, ps.map(function (p) { return '<span dir="ltr">' + esc(p.b) + '</span>'; })) +
        row(L.category, ps.map(function (p) { return esc(p.c); })) +
        row(L.part, ps.map(function (p) { return '<span class="dcp-card-sku" dir="ltr">' + esc(p.sku) + '</span>'; })) +
        body +
        row('', ps.map(function (p) { return '<button class="dcp-add" type="button" data-sku="' + esc(p.sku) + '">' + L.add + '</button>'; })) +
        '</tbody></table>';
      syncButtons();
      cmpv.hidden = false; document.documentElement.classList.add('dcp-pick-open');
      cmpv.querySelector('.dcp-pick-x').focus();
    });
  }
  function closeCmp() {
    cmpv.hidden = true; document.documentElement.classList.remove('dcp-pick-open');
    var go = tray && tray.querySelector('[data-cmp-go]'); if (go) go.focus();
  }

  // ── filters in a sheet from the bottom on phones ────────────────
  var mobBtn = document.getElementById('dcp-mobfilter'), sheet = null, facetsHome = document.createComment('facets');
  function openSheet() {
    if (!sheet) {
      sheet = document.createElement('div'); sheet.className = 'dcp-pick dcp-sheet'; sheet.hidden = true;
      sheet.innerHTML = '<div class="dcp-pick-bg" data-sclose="1"></div><div class="dcp-sheet-box" role="dialog" aria-modal="true" aria-labelledby="dcp-sheet-h">' +
        '<div class="dcp-sheet-head"><h2 id="dcp-sheet-h">' + L.filters + '</h2><button class="dcp-pick-x" type="button" data-sclose="1" aria-label="' + L.close + '">&times;</button></div>' +
        '<div class="dcp-sheet-body"></div><div class="dcp-sheet-foot"><button class="dcp-btn" type="button" data-sclose="1" id="dcp-sheet-go"></button></div></div>';
      document.body.appendChild(sheet);
      sheet.addEventListener('click', function (e) { if (e.target.closest('[data-sclose]')) closeSheet(); });
      sheet.addEventListener('keydown', function (e) { if (e.key === 'Escape' && (!pick || pick.hidden)) closeSheet(); else trap(e, sheet); });
    }
    facetsEl.parentNode.insertBefore(facetsHome, facetsEl);   // the sidebar moves into the sheet and back
    sheet.querySelector('.dcp-sheet-body').appendChild(facetsEl);
    sheetCount();
    sheet.hidden = false; document.documentElement.classList.add('dcp-pick-open');
    mobBtn.setAttribute('aria-expanded', 'true');
    sheet.querySelector('.dcp-pick-x').focus();
  }
  function closeSheet() {
    if (!sheet || sheet.hidden) return;
    facetsHome.parentNode.insertBefore(facetsEl, facetsHome); facetsHome.remove();
    sheet.hidden = true; document.documentElement.classList.remove('dcp-pick-open');
    mobBtn.setAttribute('aria-expanded', 'false'); mobBtn.focus();
    countEl.scrollIntoView({ block: 'start' });
  }
  function sheetCount() { var b = sheet && sheet.querySelector('#dcp-sheet-go'); if (b) b.textContent = L.show_n.replace('{n}', num(results.length)); }
  if (mobBtn) mobBtn.addEventListener('click', openSheet);

  // ── request (RFQ) basket ────────────────────────────────────────
  var drawer = document.getElementById('dcp-drawer'), list = document.getElementById('dcp-rlist'),
    fab = document.getElementById('dcp-fab'), fabN = document.getElementById('dcp-fabn'),
    scrim = document.getElementById('dcp-scrim'), rtools = document.getElementById('dcp-rtools');
  // move fixed overlays out of #dc-content (its dark-mode filter would trap
  // position:fixed against it instead of the viewport)
  [fab, scrim, drawer].forEach(function (el) { if (el) document.body.appendChild(el); });
  function inBasket(sku) { return basket[sku] > 0; }
  function count() { return Object.keys(basket).length; }
  function flyToCart(btn) {
    if (matchMedia('(prefers-reduced-motion:reduce)').matches) return;
    var card = btn.closest('#dcp-grid .dcp-card'), ph = card && card.querySelector('.dcp-card-photo');
    var to = shown_(document.getElementById('dcp-reqbtn')) ? document.getElementById('dcp-reqbtn') : fab;
    if (!ph || !shown_(to)) return;
    var r = ph.getBoundingClientRect(), t = to.getBoundingClientRect();
    var fly = document.createElement('div');
    fly.style.cssText = 'position:fixed;z-index:2000;pointer-events:none;border-radius:8px;overflow:hidden;background:#12211f;'
      + 'left:' + r.left + 'px;top:' + r.top + 'px;width:' + r.width + 'px;height:' + r.height + 'px;'
      + 'transition:transform .6s cubic-bezier(.5,-.35,.35,1),opacity .6s';
    var im = ph.querySelector('img');
    if (im) { fly.style.backgroundImage = 'url(' + (im.currentSrc || im.src) + ')'; fly.style.backgroundSize = 'cover'; fly.style.backgroundPosition = 'center'; }
    document.body.appendChild(fly);
    requestAnimationFrame(function () {
      var dx = t.left + t.width / 2 - (r.left + r.width / 2), dy = t.top + t.height / 2 - (r.top + r.height / 2);
      fly.style.transform = 'translate(' + dx + 'px,' + dy + 'px) scale(.12)'; fly.style.opacity = '.35';
    });
    setTimeout(function () { fly.remove(); }, 640);
  }
  var lastN = -1;
  function syncButtons() {
    document.querySelectorAll('.dcp-add').forEach(function (btn) {
      var on = inBasket(btn.dataset.sku);
      btn.classList.toggle('on', on);
      btn.textContent = on ? L.added : L.add;
    });
    document.querySelectorAll('.dcp-qn').forEach(function (inp) {   // reflect a saved quantity
      if (inBasket(inp.dataset.sku)) inp.value = basket[inp.dataset.sku];
    });
    var n = count();
    fabN.textContent = n;
    fab.hidden = n === 0;
    drawReq();
    if (lastN !== -1 && n !== lastN) {   // pulse the badge + nudge the cart when the count changes
      fabN.classList.remove('dcp-bump'); void fabN.offsetWidth; fabN.classList.add('dcp-bump');
      fab.classList.remove('dcp-added'); void fab.offsetWidth; fab.classList.add('dcp-added');
    }
    lastN = n;
  }
  function renderList(note) {
    var keys = Object.keys(basket);
    if (rtools) rtools.hidden = !keys.length;
    var head = note ? '<li class="dcp-rnote" role="status">' + esc(note) + '</li>' : '';
    if (!keys.length) { list.innerHTML = head + '<p class="dcp-rempty">' + L.r_empty + '</p>'; return; }
    list.innerHTML = head + keys.map(function (sku) {
      var p = BY[sku]; if (!p) return '';
      return '<li><div><strong>' + esc(p.n) + '</strong><span dir="ltr">' + (p.b ? esc(p.b) + ' &middot; ' : '') + esc(p.sku) + '</span></div>' +
        '<div class="dcp-rqty">' +
          '<button type="button" class="dcp-rq" data-sku="' + esc(sku) + '" data-q="-1" aria-label="' + esc(L.dec) + '">&minus;</button>' +
          '<span>' + basket[sku] + '</span>' +
          '<button type="button" class="dcp-rq" data-sku="' + esc(sku) + '" data-q="1" aria-label="' + esc(L.inc) + '">+</button>' +
        '</div>' +
        '<button type="button" class="dcp-rrm" data-sku="' + esc(sku) + '" aria-label="' + esc(L.remove + ': ' + p.n) + '">&times;</button></li>';
    }).join('');
  }
  // quantity buttons and Add, wherever a product is shown (cards, quick view, compare)
  function actions(e) {
    var qb = e.target.closest('.dcp-qb');
    if (qb) {
      var inp = qb.parentNode.querySelector('.dcp-qn');
      inp.value = Math.max(1, (parseInt(inp.value, 10) || 1) + (+qb.dataset.q));
      if (inBasket(inp.dataset.sku)) { basket[inp.dataset.sku] = +inp.value; save(); syncButtons(); renderList(); }
      return;
    }
    var btn = e.target.closest('.dcp-add'); if (!btn) return;
    var sku = btn.dataset.sku, adding = !inBasket(sku);
    if (!adding) delete basket[sku];
    else { var row = btn.closest('.dcp-add-row'), qn = row && row.querySelector('.dcp-qn'); basket[sku] = Math.max(1, qn ? parseInt(qn.value, 10) || 1 : 1); }
    save(); syncButtons(); renderList();
    if (adding) flyToCart(btn);
  }
  function changes(e) {   // a typed quantity or a compare tick
    var c = e.target.closest('[data-cmp]'); if (c) { setCmp(c.getAttribute('data-cmp'), c.checked); return; }
    var inp = e.target.closest('.dcp-qn'); if (!inp) return;
    inp.value = Math.max(1, parseInt(inp.value, 10) || 1);
    if (inBasket(inp.dataset.sku)) { basket[inp.dataset.sku] = +inp.value; save(); syncButtons(); renderList(); }
  }
  grid.addEventListener('click', function (e) {
    var rl = e.target.closest('[data-rel]'); if (rl) { showRel(rl.getAttribute('data-rel')); return; }
    var o = e.target.closest('[data-open]');
    if (o) { if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return; e.preventDefault(); openQV(o.getAttribute('data-open')); return; }
    var ph = e.target.closest('.dcp-card-photo'); if (ph) { openQV(ph.closest('.dcp-card').getAttribute('data-sku')); return; }
    actions(e);
  });
  grid.addEventListener('change', changes);
  list.addEventListener('click', function (e) {
    var qb = e.target.closest('.dcp-rq');
    if (qb) { var s = qb.dataset.sku; basket[s] = Math.max(1, (basket[s] || 1) + (+qb.dataset.q)); save(); syncButtons(); renderList(); return; }
    var btn = e.target.closest('.dcp-rrm'); if (!btn) return;
    delete basket[btn.dataset.sku]; save(); syncButtons(); renderList();
  });
  // the request drawer takes the focus while open and hands it back to the basket button
  function openD() {
    drawer.classList.add('open'); scrim.hidden = false; drawer.setAttribute('aria-hidden', 'false');
    document.getElementById('dcp-dclose').focus();
  }
  function closeD() {
    if (!drawer.classList.contains('open')) return;
    drawer.classList.remove('open'); scrim.hidden = true; drawer.setAttribute('aria-hidden', 'true');
    var rb = document.getElementById('dcp-reqbtn');
    if (shown_(rb)) rb.focus(); else if (shown_(fab)) fab.focus();
  }
  fab.addEventListener('click', openD);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeD(); });
  drawer.addEventListener('keydown', function (e) { if (drawer.classList.contains('open')) trap(e, drawer); });
  document.getElementById('dcp-dclose').addEventListener('click', closeD);
  scrim.addEventListener('click', closeD);
  document.getElementById('dcp-clear').addEventListener('click', function () {
    basket = {}; save(); syncButtons(); renderList();
  });
  // a request can travel as a link (the list rides in the address) or as a spreadsheet
  function shareLink() {
    var items = Object.keys(basket).map(function (s) { return [s, basket[s]]; });
    return location.href.split(/[?#]/)[0] + '?rfq=' + encodeURIComponent(JSON.stringify(items));
  }
  function csvCell(c) {
    c = String(c);
    if (/^[=+\-@]/.test(c)) c = "'" + c;   // a part number such as "=X" must not become a spreadsheet formula
    return /[",\r\n]/.test(c) ? '"' + c.replace(/"/g, '""') + '"' : c;
  }
  function downloadCSV() {
    var rows = [[L.part, L.product, L.brand, L.qty]].concat(Object.keys(basket).map(function (s) {
      var p = BY[s]; return [s, p ? p.n : s, p ? p.b : '', basket[s]];
    }));
    var csv = String.fromCharCode(0xFEFF) + rows.map(function (r) { return r.map(csvCell).join(','); }).join('\r\n');
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    a.download = 'datacore-request-' + new Date().toISOString().slice(0, 10) + '.csv';
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  }
  var shareBtn = document.getElementById('dcp-share'), csvBtn = document.getElementById('dcp-csv');
  if (shareBtn) shareBtn.addEventListener('click', function () { copyText(shareLink(), shareBtn); });
  if (csvBtn) csvBtn.addEventListener('click', downloadCSV);
  function takeShared(u) {
    var raw = u.get('rfq'), n = 0; if (!raw) return 0;
    try {
      JSON.parse(raw).forEach(function (x) { if (x && BY[x[0]]) { basket[x[0]] = Math.max(1, parseInt(x[1], 10) || 1); n++; } });
    } catch (e) { return 0; }
    save(); return n;
  }
  var form = document.getElementById('dcp-rform');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!form.checkValidity()) { form.reportValidity(); return; }
    if (!count()) { renderList(); return; }
    var ref = 'RFQ-' + Date.now().toString(36).toUpperCase().slice(-6);
    var n = count();
    var items = Object.keys(basket).map(function (sku) {
      var p = BY[sku]; return '- ' + (p ? p.n : sku) + ' [' + sku + '] x ' + basket[sku];
    }).join('\n');
    var gv = function (id) { var el = document.getElementById(id); return el ? el.value : ''; };
    var fd = { name: gv('r-name'), company: gv('r-co'), email: gv('r-mail'),
               phone: gv('r-tel'), notes: gv('r-msg'), reference: ref, products: '\n' + items };
    var subj = (AR ? 'طلب عرض سعر من الموقع' : 'Product request (RFQ) from the website') + ': ' + (fd.name || '');
    var btn = form.querySelector('button[type=submit]'); if (btn) { btn.disabled = true; }
    // deliver via the shared helper (POST to the inbox if a key is set, else open the visitor's email)
    (window.dcpDeliver ? window.dcpDeliver(fd, subj) : Promise.resolve()).then(function () {
      var body = document.getElementById('dcp-dbody');
      body.innerHTML = '<div class="dcp-rok" role="status"><h3>' + L.ok_h + '</h3><p>' +
        L.ok_p.replace('{ref}', '<strong>' + ref + '</strong>').replace('{n}', n) + '</p></div>';
      basket = {}; save(); syncButtons();
    });
  });

  // ── start: the address decides the view; a shared list or ?req=1 opens the request ──
  var u0 = readURL(), shared = takeShared(u0);
  renderFacets(); apply(); renderList(shared === 1 ? L.shared_one : shared ? L.shared.replace('{n}', num(shared)) : '');
  if (u0.get('p') && BY[u0.get('p')]) openQV(u0.get('p'), true);
  if (shared || u0.has('req')) openD();
  if (u0.has('rfq') || u0.has('req')) writeURL(false);
  setTimeout(function () { withText(function () { if (S.q) apply(); }); }, 30);
})();
