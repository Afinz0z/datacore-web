/* Datacore mirror — product catalogue engine. Left faceted sidebar (category /
   brand / availability, multi-select, live cross-filtered counts) + a photo
   grid + a request (RFQ) basket persisted per browser. No backend: submitting
   the request shows a reference number, same as the contact form. */
(function () {
  var D = window.DCP_DATA; if (!D) return;
  var L = D.labels, AR = D.lang === 'ar';
  var P = D.products;
  var KEY = 'dcp-rfq2';   // basket is now { sku: qty }
  var basket = load();

  function load() { try { var v = JSON.parse(sessionStorage.getItem(KEY)); if (Array.isArray(v)) { var o = {}; v.forEach(function (s) { o[s] = 1; }); return o; } return (v && typeof v === 'object') ? v : {}; } catch (e) { return {}; } }
  function save() { try { sessionStorage.setItem(KEY, JSON.stringify(basket)); } catch (e) {} }
  function bySku(s) { for (var i = 0; i < P.length; i++) if (P[i].sku === s) return P[i]; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]; }); }
  function glyph(g) {
    return '<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" ' +
      'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      (D.glyphs[g] || D.glyphs.rack || '') + '</svg>';
  }
  function catName(c) { return D.catMap[c] || c; }
  function availName(a) { return a === 'stock' ? L.in_stock : L.on_order; }

  // ── build every card once (photo grid); filtering just toggles .hidden ──
  var grid = document.getElementById('dcp-grid');
  P.forEach(function (p) {
    var chips = Object.keys(p.specs || {}).slice(0, 3).map(function (k) {
      return '<span class="dcp-chip" dir="ltr">' + esc(p.specs[k]) + '</span>';
    }).join('');
    var el = document.createElement('article');
    el.className = 'dcp-card'; el._p = p;
    el.innerHTML =
      '<div class="dcp-card-media"><span class="dcp-card-ic">' + glyph(p.g) + '</span></div>' +
      '<div class="dcp-card-sub" dir="ltr">' + esc(p.b) + ' &middot; ' + esc(catName(p.c)) + '</div>' +
      '<h3>' + esc(p.n) + '</h3>' +
      '<div class="dcp-card-sku" dir="ltr">' + esc(p.sku) + '</div>' +
      '<div class="dcp-chips">' + chips + '</div>' +
      '<div class="dcp-avail ' + (p.avail === 'stock' ? 'stock' : 'lead') + '"><span class="dot"></span>' + esc(availName(p.avail)) + '</div>' +
      '<div class="dcp-add-row">' +
        '<div class="dcp-qty">' +
          '<button class="dcp-qb" type="button" data-q="-1" aria-label="Decrease quantity">−</button>' +
          '<input class="dcp-qn" type="text" inputmode="numeric" value="1" aria-label="Quantity" data-sku="' + esc(p.sku) + '">' +
          '<button class="dcp-qb" type="button" data-q="1" aria-label="Increase quantity">+</button>' +
        '</div>' +
        '<button class="dcp-add" type="button" data-sku="' + esc(p.sku) + '">' + L.add + '</button>' +
      '</div>';
    grid.appendChild(el);
  });
  var cards = [].slice.call(grid.children);

  // ── faceted state + filtering (multi-select) ────────────────────
  var S = { q: '', cat: [], brand: [], avail: [] };
  function match(p, skip) {
    if (S.q) {
      var t = (p.n + ' ' + p.b + ' ' + p.sku + ' ' + p.c + ' ' +
        Object.keys(p.specs || {}).map(function (k) { return p.specs[k]; }).join(' ')).toLowerCase();
      if (!S.q.toLowerCase().split(/\s+/).every(function (w) { return t.indexOf(w) > -1; })) return false;
    }
    if (skip !== 'cat' && S.cat.length && S.cat.indexOf(p.c) < 0) return false;
    if (skip !== 'brand' && S.brand.length && S.brand.indexOf(p.b) < 0) return false;
    if (skip !== 'avail' && S.avail.length && S.avail.indexOf(p.avail) < 0) return false;
    return true;
  }
  // counts for a dimension ignore that dimension's own selection (so you can
  // still see and add sibling options), but respect every other active filter
  function tally(dim, get) {
    var m = {};
    P.forEach(function (p) { if (match(p, dim)) { var v = get(p); if (v != null) m[v] = (m[v] || 0) + 1; } });
    return m;
  }

  // ── left sidebar ────────────────────────────────────────────────
  var facetsEl = document.getElementById('dcp-facets');
  function fgroup(title, dim, counts, selected, label, limit) {
    var all = Object.keys(counts);
    selected.forEach(function (s) { if (all.indexOf(s) < 0) all.push(s); });
    all.sort();
    var open = all.length <= (limit || 8) || S['_m_' + dim];
    var list = open ? all : all.slice(0, limit || 8);
    var h = '<div class="dcp-fgroup"><h4>' + esc(title) + '</h4>';
    list.forEach(function (v) {
      var c = counts[v] || 0, on = selected.indexOf(v) > -1;
      h += '<label class="' + (c === 0 && !on ? 'off' : '') + '"><input type="checkbox" data-dim="' + esc(dim) +
        '" value="' + esc(v) + '"' + (on ? ' checked' : '') + '><span>' + esc(label(v)) +
        '</span><span class="dcp-fc">' + c + '</span></label>';
    });
    if (all.length > list.length)
      h += '<button class="dcp-more" type="button" data-more="' + esc(dim) + '">+ ' + (all.length - list.length) + '</button>';
    return h + '</div>';
  }
  function renderFacets() {
    var n = S.cat.length + S.brand.length + S.avail.length;
    var h = '<div class="dcp-fhead"><span>' + L.refine + '</span>' +
      (n ? '<button class="dcp-clearall" type="button" id="dcp-clearall">' + L.clear + '</button>' : '') + '</div>';
    h += fgroup(L.category, 'cat', tally('cat', function (p) { return p.c; }), S.cat, catName, 9);
    h += fgroup(L.brand, 'brand', tally('brand', function (p) { return p.b; }), S.brand, function (v) { return v; }, 8);
    h += fgroup(L.availability, 'avail', tally('avail', function (p) { return p.avail; }), S.avail, availName, 4);
    facetsEl.innerHTML = h;
  }

  // ── results, count, active chips ────────────────────────────────
  var countEl = document.getElementById('dcp-count'), chipsEl = document.getElementById('dcp-chips'),
    emptyEl = document.getElementById('dcp-empty');
  function apply() {
    var shown = 0;
    cards.forEach(function (el) { var ok = match(el._p, null); el.hidden = !ok; if (ok) shown++; });
    countEl.innerHTML = '<b>' + shown + '</b> ' + (shown === 1 ? L.product_one : L.product_many);
    emptyEl.hidden = shown > 0;
    renderChips();
  }
  function renderChips() {
    var ch = [];
    S.cat.forEach(function (v) { ch.push(['cat', v, catName(v)]); });
    S.brand.forEach(function (v) { ch.push(['brand', v, v]); });
    S.avail.forEach(function (v) { ch.push(['avail', v, availName(v)]); });
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
    if (ev.target.id === 'dcp-clearall') { S.cat = []; S.brand = []; S.avail = []; apply(); renderFacets(); return; }
    var m = ev.target.getAttribute('data-more'); if (m) { S['_m_' + m] = true; renderFacets(); }
  });
  chipsEl.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-chip]'); if (!b) return;
    var d = b.getAttribute('data-chip'), v = b.getAttribute('data-val'), i = S[d].indexOf(v);
    if (i > -1) S[d].splice(i, 1); apply(); renderFacets();
  });
  var search = document.getElementById('dcp-search');
  search.addEventListener('input', function () { S.q = search.value.trim(); apply(); renderFacets(); });
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
    var card = btn.closest('.dcp-card'), ph = card && card.querySelector('.dcp-card-media');
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
    if (!keys.length) { list.innerHTML = '<p class="dcp-rempty">' + L.empty + '</p>'; return; }
    list.innerHTML = keys.map(function (sku) {
      var p = bySku(sku); if (!p) return '';
      return '<li><div><strong>' + esc(p.n) + '</strong><span dir="ltr">' + esc(p.b) + ' &middot; ' + esc(p.sku) + '</span></div>' +
        '<div class="dcp-rqty">' +
          '<button type="button" class="dcp-rq" data-sku="' + esc(sku) + '" data-q="-1" aria-label="Decrease quantity">−</button>' +
          '<span>' + basket[sku] + '</span>' +
          '<button type="button" class="dcp-rq" data-sku="' + esc(sku) + '" data-q="1" aria-label="Increase quantity">+</button>' +
        '</div>' +
        '<button type="button" class="dcp-rrm" data-sku="' + esc(sku) + '" aria-label="' + L.remove + '">&times;</button></li>';
    }).join('');
  }
  grid.addEventListener('click', function (e) {
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
  function openD() { drawer.classList.add('open'); scrim.hidden = false; drawer.setAttribute('aria-hidden', 'false'); }
  function closeD() { drawer.classList.remove('open'); scrim.hidden = true; drawer.setAttribute('aria-hidden', 'true'); }
  fab.addEventListener('click', openD);
  document.getElementById('dcp-dclose').addEventListener('click', closeD);
  scrim.addEventListener('click', closeD);
  document.getElementById('dcp-clear').addEventListener('click', function () {
    basket = {}; save(); syncButtons(); renderList();
  });
  var form = document.getElementById('dcp-rform');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!form.checkValidity()) { form.reportValidity(); return; }
    if (!count()) { alert(L.empty); return; }
    var ref = 'RFQ-' + Date.now().toString(36).toUpperCase().slice(-6);
    var body = document.getElementById('dcp-dbody');
    body.innerHTML = '<div class="dcp-rok" role="status"><h3>' + L.ok_h + '</h3><p>' +
      L.ok_p.replace('{ref}', '<strong>' + ref + '</strong>').replace('{n}', count()) + '</p></div>';
    basket = {}; save(); syncButtons();
  });

  renderFacets(); apply(); syncButtons(); renderList();
})();
