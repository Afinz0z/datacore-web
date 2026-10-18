/* Datacore product catalogue engine. Left faceted sidebar (category group / type / brand,
   multi-select, live cross-filtered counts), a photo grid shown a page at a time, and a
   request (RFQ) basket persisted per browser. The page carries the first page of cards and the
   starting filters; the full catalogue comes from assets1/data/products-data.js
   (window.DCP_PRODUCTS, written by build_products.py). No backend: submitting the request
   shows a reference number, same as the contact form. */
(function () {
  var D = window.DCP_DATA, RAW = window.DCP_PRODUCTS; if (!D || !RAW) return;
  var L = D.labels, AR = D.lang === 'ar', PAGE = D.page || 24;
  var KEY = 'dcp-rfq2';   // basket is { sku: qty }
  var basket = load();

  function load() { try { var v = JSON.parse(localStorage.getItem(KEY)); if (Array.isArray(v)) { var o = {}; v.forEach(function (s) { o[s] = 1; }); return o; } return (v && typeof v === 'object') ? v : {}; } catch (e) { return {}; } }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(basket)); } catch (e) {} }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]; }); }
  function num(n) { return n.toLocaleString('en-US'); }
  function glyph(g) {
    return '<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" ' +
      'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      (D.glyphs[g] || D.glyphs.rack || '') + '</svg>';
  }

  // ── catalogue: [sku, name, brand#, category#, icon, photo, specs, description, inStock,
  //    supporting products (row numbers), products it fits (row numbers)] ──
  var GROUP = {}, GORDER = [];
  RAW.groups.forEach(function (g) { GROUP[g[0]] = AR ? g[2] : g[1]; GORDER.push(g[0]); });
  var BY = {};
  var P = RAW.p.map(function (r) {
    var c = RAW.cats[r[3]];
    var p = { sku: r[0], n: r[1], b: r[2] > -1 ? RAW.brands[r[2]] : '', ck: c[0], c: AR ? c[1] : c[0], grp: c[2],
      g: r[4], photo: r[5], specs: r[6] || [], avail: r[8] ? 'stock' : 'lead', kids: r[9] || [], fits: r[10] || [] };
    p.t = (p.n + ' ' + p.b + ' ' + p.sku + ' ' + c[0] + ' ' + c[1] + ' ' + GROUP[p.grp] + ' ' +
      p.specs.map(function (s) { return s[1]; }).join(' ') + ' ' + (r[7] || '')).toLowerCase();
    BY[p.sku] = p;
    return p;
  });
  P.forEach(function (p) {   // row numbers -> products
    p.kids = p.kids.map(function (i) { return P[i]; }); p.fits = p.fits.map(function (i) { return P[i]; });
  });
  var hasStock = P.some(function (p) { return p.avail === 'stock'; });
  // requests saved before a catalogue update may name products that are gone
  Object.keys(basket).forEach(function (s) { if (!BY[s]) delete basket[s]; }); save();

  function availName(a) { return a === 'stock' ? L.in_stock : L.on_order; }
  // the specs a card shows: the first four short enough for one line (same rule as build_products.card_specs)
  function cardSpecs(p) { return p.specs.filter(function (s) { return s[1].length <= 48; }).slice(0, 4); }
  function relHTML(p) {
    var b = '';
    if (p.kids.length) b += '<button type="button" class="dcp-more" data-rel="' + esc(p.sku) + '">' + L.rel_acc.replace('{n}', p.kids.length) + '</button>';
    if (p.fits.length) b += '<button type="button" class="dcp-more" data-rel="' + esc(p.sku) + '">' + L.rel_for.replace('{n}', p.fits.length) + '</button>';
    return b ? '<div class="dcp-card-rel">' + b + '</div>' : '';
  }
  function cardHTML(p) {
    var specs = cardSpecs(p).map(function (s) {
      return '<div><dt>' + esc(s[0]) + '</dt><dd dir="ltr">' + esc(s[1]) + '</dd></div>';
    }).join('');
    var av = p.avail === 'stock'
      ? '<span class="dcp-badge stock">' + L.in_stock + '</span>'
      : '<span class="dcp-badge lead">' + L.on_order + '</span>';
    var media = p.photo
      ? '<div class="dcp-card-photo"><img src="' + D.photoDir + esc(p.photo) + '" alt="' + esc(p.n) + '" width="600" height="600" decoding="async"></div>'
      : '<div class="dcp-card-photo dcp-noimg"><span class="dcp-card-ic">' + glyph(p.g) + '</span></div>';
    return '<article class="dcp-card" data-sku="' + esc(p.sku) + '">' + media +
      '<div class="dcp-card-top">' + (p.b ? '<span class="dcp-card-brand" dir="ltr">' + esc(p.b) + '</span>' : '<span class="dcp-card-brand"></span>') + av + '</div>' +
      '<h3 dir="auto">' + esc(p.n) + '</h3>' +
      '<div class="dcp-card-meta"><span class="dcp-tag">' + esc(p.c) + '</span></div>' +
      '<dl class="dcp-specs">' + specs + '</dl>' + relHTML(p) +
      '<div class="dcp-card-sku" dir="ltr">' + esc(p.sku) + '</div>' +
      '<div class="dcp-add-row">' +
        '<div class="dcp-qty">' +
          '<button class="dcp-qb" type="button" data-q="-1" aria-label="Decrease quantity">−</button>' +
          '<input class="dcp-qn" type="text" inputmode="numeric" value="1" aria-label="Quantity" data-sku="' + esc(p.sku) + '">' +
          '<button class="dcp-qb" type="button" data-q="1" aria-label="Increase quantity">+</button>' +
        '</div>' +
        '<button class="dcp-add" type="button" data-sku="' + esc(p.sku) + '">' + L.add + '</button>' +
      '</div></article>';
  }

  // ── faceted state + filtering (multi-select) ────────────────────
  var S = { q: '', grp: [], cat: [], brand: [], avail: [], rel: '' };
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
      var words = S.q.toLowerCase().split(/\s+/);
      for (var i = 0; i < words.length; i++) if (p.t.indexOf(words[i]) < 0) return false;
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
    var m = {}, get = GET[dim];
    base().forEach(function (p) { if (match(p, dim)) { var v = get(p); if (v != null) m[v] = (m[v] || 0) + 1; } });
    return m;
  }

  // ── left sidebar ────────────────────────────────────────────────
  var facetsEl = document.getElementById('dcp-facets');
  function fgroup(title, dim, counts, limit, order) {
    var all = Object.keys(counts);
    S[dim].forEach(function (s) { if (all.indexOf(s) < 0) all.push(s); });
    if (order) all.sort(function (a, b) { return order.indexOf(a) - order.indexOf(b); });
    else all.sort(function (a, b) { return LABEL[dim](a).localeCompare(LABEL[dim](b), AR ? 'ar' : 'en'); });
    var open = all.length <= limit || S['_m_' + dim];
    var list = open ? all : all.slice(0, limit);
    var h = '<div class="dcp-fgroup"><h4>' + esc(title) + '</h4>';
    list.forEach(function (v) {
      var c = counts[v] || 0, on = S[dim].indexOf(v) > -1;
      h += '<label class="' + (c === 0 && !on ? 'off' : '') + '"><input type="checkbox" data-dim="' + dim +
        '" value="' + esc(v) + '"' + (on ? ' checked' : '') + '><span>' + esc(LABEL[dim](v)) +
        '</span><span class="dcp-fc">' + c + '</span></label>';
    });
    if (all.length > list.length)
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
    facetsEl.innerHTML = h;
  }

  // ── results a page at a time, count, active chips ───────────────
  var grid = document.getElementById('dcp-grid');
  var countEl = document.getElementById('dcp-count'), chipsEl = document.getElementById('dcp-chips'),
    emptyEl = document.getElementById('dcp-empty'), moreBtn = document.getElementById('dcp-more');
  var results = P, shown = 0;
  var countTop = document.getElementById('dcp-count');
  function showCount() {
    countEl.innerHTML = results.length > shown
      ? L.showing.replace('{n}', '<b>' + num(shown) + '</b>').replace('{t}', num(results.length))
      : '<b>' + num(results.length) + '</b> ' + (results.length === 1 ? L.product_one : L.product_many);
    emptyEl.hidden = results.length > 0;
    if (moreBtn) moreBtn.hidden = shown >= results.length;
  }
  function apply() {
    results = base().filter(function (p) { return match(p, null); });
    shown = Math.min(PAGE, results.length);
    grid.innerHTML = results.slice(0, shown).map(cardHTML).join('');
    showCount(); renderChips(); syncButtons();
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
        '" data-val="' + esc(x[1]) + '" aria-label="' + L.remove + '">&times;</button></span>';
    }).join('');
  }

  facetsEl.addEventListener('change', function (ev) {
    var d = ev.target.getAttribute('data-dim'); if (!d) return;
    var v = ev.target.value, arr = S[d], i = arr.indexOf(v);
    if (ev.target.checked) { if (i < 0) arr.push(v); } else if (i > -1) arr.splice(i, 1);
    apply(); renderFacets();
  });
  facetsEl.addEventListener('click', function (ev) {
    if (ev.target.id === 'dcp-clearall') { DIMS.forEach(function (d) { S[d] = []; }); S.rel = ''; apply(); renderFacets(); return; }
    var m = ev.target.getAttribute('data-more'); if (m) { S['_m_' + m] = true; renderFacets(); }
  });
  chipsEl.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-chip]'); if (!b) return;
    var d = b.getAttribute('data-chip'), v = b.getAttribute('data-val');
    if (d === 'rel') S.rel = '';
    else { var i = S[d].indexOf(v); if (i > -1) S[d].splice(i, 1); }
    apply(); renderFacets();
  });
  var search = document.getElementById('dcp-search'), typing;
  search.addEventListener('input', function () {
    clearTimeout(typing);
    typing = setTimeout(function () { S.q = search.value.trim(); apply(); renderFacets(); }, 120);
  });
  var mobBtn = document.getElementById('dcp-mobfilter');
  if (mobBtn) mobBtn.addEventListener('click', function () {
    var on = facetsEl.classList.toggle('open'); mobBtn.setAttribute('aria-expanded', String(on));
  });

  // ── request (RFQ) basket ────────────────────────────────────────
  var drawer = document.getElementById('dcp-drawer'), list = document.getElementById('dcp-rlist'),
    fab = document.getElementById('dcp-fab'), fabN = document.getElementById('dcp-fabn'),
    scrim = document.getElementById('dcp-scrim');
  // move fixed overlays out of #dc-content (its dark-mode filter would trap
  // position:fixed against it instead of the viewport)
  [fab, scrim, drawer].forEach(function (el) { if (el) document.body.appendChild(el); });
  function inBasket(sku) { return basket[sku] > 0; }
  function count() { return Object.keys(basket).length; }
  function flyToCart(btn) {
    if (matchMedia('(prefers-reduced-motion:reduce)').matches) return;
    var card = btn.closest('.dcp-card'), ph = card && card.querySelector('.dcp-card-photo');
    if (!ph || fab.hidden) return;
    var r = ph.getBoundingClientRect(), t = fab.getBoundingClientRect();
    var fly = document.createElement('div');
    fly.style.cssText = 'position:fixed;z-index:2000;pointer-events:none;border-radius:8px;overflow:hidden;background:#12211f;'
      + 'left:' + r.left + 'px;top:' + r.top + 'px;width:' + r.width + 'px;height:' + r.height + 'px;'
      + 'transition:transform .6s cubic-bezier(.5,-.35,.35,1),opacity .6s';
    var im = ph.querySelector('img');
    if (im) { fly.style.backgroundImage = 'url(' + im.src + ')'; fly.style.backgroundSize = 'cover'; fly.style.backgroundPosition = 'center'; }
    document.body.appendChild(fly);
    requestAnimationFrame(function () {
      var dx = t.left + t.width / 2 - (r.left + r.width / 2), dy = t.top + t.height / 2 - (r.top + r.height / 2);
      fly.style.transform = 'translate(' + dx + 'px,' + dy + 'px) scale(.12)'; fly.style.opacity = '.35';
    });
    setTimeout(function () { fly.remove(); }, 640);
  }
  var lastN = -1;
  function syncButtons() {
    grid.querySelectorAll('.dcp-add').forEach(function (btn) {
      var on = inBasket(btn.dataset.sku);
      btn.classList.toggle('on', on);
      btn.textContent = on ? L.added : L.add;
    });
    grid.querySelectorAll('.dcp-qn').forEach(function (inp) {   // reflect a saved quantity on the card
      if (inBasket(inp.dataset.sku)) inp.value = basket[inp.dataset.sku];
    });
    var n = count();
    fabN.textContent = n;
    fab.hidden = n === 0;
    if (lastN !== -1 && n !== lastN) {   // pulse the badge + nudge the cart when the count changes
      fabN.classList.remove('dcp-bump'); void fabN.offsetWidth; fabN.classList.add('dcp-bump');
      fab.classList.remove('dcp-added'); void fab.offsetWidth; fab.classList.add('dcp-added');
    }
    lastN = n;
  }
  function renderList() {
    var keys = Object.keys(basket);
    if (!keys.length) { list.innerHTML = '<p class="dcp-rempty">' + L.r_empty + '</p>'; return; }
    list.innerHTML = keys.map(function (sku) {
      var p = BY[sku]; if (!p) return '';
      return '<li><div><strong>' + esc(p.n) + '</strong><span dir="ltr">' + (p.b ? esc(p.b) + ' &middot; ' : '') + esc(p.sku) + '</span></div>' +
        '<div class="dcp-rqty">' +
          '<button type="button" class="dcp-rq" data-sku="' + esc(sku) + '" data-q="-1" aria-label="Decrease quantity">−</button>' +
          '<span>' + basket[sku] + '</span>' +
          '<button type="button" class="dcp-rq" data-sku="' + esc(sku) + '" data-q="1" aria-label="Increase quantity">+</button>' +
        '</div>' +
        '<button type="button" class="dcp-rrm" data-sku="' + esc(sku) + '" aria-label="' + L.remove + '">&times;</button></li>';
    }).join('');
  }
  grid.addEventListener('click', function (e) {
    var rl = e.target.closest('[data-rel]');
    if (rl) {
      S.rel = rl.getAttribute('data-rel'); S.q = ''; search.value = '';
      DIMS.forEach(function (d) { S[d] = []; });
      apply(); renderFacets();
      countTop.scrollIntoView({ block: 'start' });
      return;
    }
    var qb = e.target.closest('.dcp-qb');
    if (qb) {   // +/- on a card adjusts its quantity (and the basket if already added)
      var inp = qb.parentNode.querySelector('.dcp-qn');
      inp.value = Math.max(1, (parseInt(inp.value, 10) || 1) + (+qb.dataset.q));
      if (inBasket(inp.dataset.sku)) { basket[inp.dataset.sku] = +inp.value; save(); syncButtons(); renderList(); }
      return;
    }
    var btn = e.target.closest('.dcp-add'); if (!btn) return;
    var sku = btn.dataset.sku, adding = !inBasket(sku);
    if (inBasket(sku)) { delete basket[sku]; }
    else { var qn = btn.parentNode.querySelector('.dcp-qn'); basket[sku] = Math.max(1, parseInt(qn.value, 10) || 1); }
    save(); syncButtons(); renderList();
    if (adding) flyToCart(btn);
  });
  grid.addEventListener('change', function (e) {   // typed quantity
    var inp = e.target.closest('.dcp-qn'); if (!inp) return;
    inp.value = Math.max(1, parseInt(inp.value, 10) || 1);
    if (inBasket(inp.dataset.sku)) { basket[inp.dataset.sku] = +inp.value; save(); syncButtons(); renderList(); }
  });
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
    fab.focus();
  }
  fab.addEventListener('click', openD);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeD(); });
  document.getElementById('dcp-dclose').addEventListener('click', closeD);
  scrim.addEventListener('click', closeD);
  document.getElementById('dcp-clear').addEventListener('click', function () {
    basket = {}; save(); syncButtons(); renderList();
  });
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

  renderFacets(); apply(); renderList();
})();
