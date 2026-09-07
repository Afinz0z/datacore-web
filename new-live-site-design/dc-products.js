/* Datacore mirror — product catalogue engine. The page sets window.DCP_DATA
   (products, glyphs, localized labels, lang) then loads this. Faceted filter
   + text search + a request (RFQ) basket persisted per browser. No backend:
   submitting the request shows a reference number, same as the contact form. */
(function () {
  var D = window.DCP_DATA; if (!D) return;
  var L = D.labels, AR = D.lang === 'ar';
  var KEY = 'dcp-rfq';
  var basket = load();

  function load() { try { return JSON.parse(sessionStorage.getItem(KEY)) || []; } catch (e) { return []; } }
  function save() { try { sessionStorage.setItem(KEY, JSON.stringify(basket)); } catch (e) {} }
  function bySku(s) { for (var i = 0; i < D.products.length; i++) if (D.products[i].sku === s) return D.products[i]; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]; }); }

  // ── build the grid ──────────────────────────────────────────────
  var grid = document.getElementById('dcp-grid');
  function glyph(g) {
    return '<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" ' +
      'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      (D.glyphs[g] || D.glyphs.rack || '') + '</svg>';
  }
  D.products.forEach(function (p) {
    var specs = Object.keys(p.specs || {}).slice(0, 4).map(function (k) {
      return '<div><dt>' + esc(k) + '</dt><dd dir="ltr">' + esc(p.specs[k]) + '</dd></div>';
    }).join('');
    var av = p.avail === 'stock'
      ? '<span class="dcp-badge stock">' + L.in_stock + '</span>'
      : '<span class="dcp-badge lead">' + L.on_order + '</span>';
    var cat = D.catMap[p.c] || p.c;
    var el = document.createElement('article');
    el.className = 'dcp-card';
    el.dataset.cat = p.c; el.dataset.brand = p.b; el.dataset.avail = p.avail;
    el.dataset.search = (p.n + ' ' + p.b + ' ' + p.sku + ' ' + cat).toLowerCase();
    el.innerHTML =
      '<div class="dcp-card-top"><span class="dcp-card-ic">' + glyph(p.g) + '</span>' +
      '<span class="dcp-card-brand" dir="ltr">' + esc(p.b) + '</span></div>' +
      '<h3>' + esc(p.n) + '</h3>' +
      '<div class="dcp-card-meta"><span class="dcp-tag">' + esc(cat) + '</span>' + av + '</div>' +
      '<dl class="dcp-specs">' + specs + '</dl>' +
      '<div class="dcp-card-sku" dir="ltr">' + esc(p.sku) + '</div>' +
      '<button class="dcp-add" type="button" data-sku="' + esc(p.sku) + '">' + L.add + '</button>';
    grid.appendChild(el);
  });
  var cards = [].slice.call(grid.children);

  // ── facets + search ─────────────────────────────────────────────
  var fCat = document.getElementById('f-cat'), fBrand = document.getElementById('f-brand'),
    fAvail = document.getElementById('f-avail'), fSearch = document.getElementById('f-search'),
    count = document.getElementById('dcp-count'), empty = document.getElementById('dcp-empty');
  function apply() {
    var c = fCat.value, b = fBrand.value, a = fAvail.value, q = fSearch.value.trim().toLowerCase();
    var shown = 0;
    cards.forEach(function (el) {
      var ok = (!c || el.dataset.cat === c) && (!b || el.dataset.brand === b) &&
        (!a || el.dataset.avail === a) && (!q || el.dataset.search.indexOf(q) > -1);
      el.hidden = !ok; if (ok) shown++;
    });
    count.textContent = L.showing.replace('{n}', shown).replace('{t}', cards.length);
    empty.hidden = shown > 0;
  }
  [fCat, fBrand, fAvail].forEach(function (s) { s.addEventListener('change', apply); });
  fSearch.addEventListener('input', apply);
  document.getElementById('dcp-reset').addEventListener('click', function () {
    fCat.value = ''; fBrand.value = ''; fAvail.value = ''; fSearch.value = ''; apply();
  });

  // ── request (RFQ) basket ────────────────────────────────────────
  var drawer = document.getElementById('dcp-drawer'), list = document.getElementById('dcp-rlist'),
    fab = document.getElementById('dcp-fab'), fabN = document.getElementById('dcp-fabn'),
    scrim = document.getElementById('dcp-scrim');
  // The overlay wraps page content in #dc-content, which takes a `filter` in
  // dark mode — and a filtered ancestor makes position:fixed resolve against
  // it, not the viewport. Move these fixed overlays out to <body> so they
  // float correctly and stay out of the invert (they're themed by hand).
  [fab, scrim, drawer].forEach(function (el) { if (el) document.body.appendChild(el); });
  function inBasket(sku) { return basket.indexOf(sku) > -1; }
  function syncButtons() {
    grid.querySelectorAll('.dcp-add').forEach(function (btn) {
      var on = inBasket(btn.dataset.sku);
      btn.classList.toggle('on', on);
      btn.textContent = on ? L.added : L.add;
    });
    fabN.textContent = basket.length;
    fab.hidden = basket.length === 0;
  }
  function renderList() {
    if (!basket.length) { list.innerHTML = '<p class="dcp-rempty">' + L.empty + '</p>'; return; }
    list.innerHTML = basket.map(function (sku) {
      var p = bySku(sku); if (!p) return '';
      return '<li><div><strong>' + esc(p.n) + '</strong><span dir="ltr">' + esc(p.b) + ' · ' + esc(p.sku) + '</span></div>' +
        '<button type="button" class="dcp-rrm" data-sku="' + esc(sku) + '" aria-label="' + L.remove + '">&times;</button></li>';
    }).join('');
  }
  grid.addEventListener('click', function (e) {
    var btn = e.target.closest('.dcp-add'); if (!btn) return;
    var sku = btn.dataset.sku;
    if (inBasket(sku)) basket.splice(basket.indexOf(sku), 1); else basket.push(sku);
    save(); syncButtons(); renderList();
  });
  list.addEventListener('click', function (e) {
    var btn = e.target.closest('.dcp-rrm'); if (!btn) return;
    basket.splice(basket.indexOf(btn.dataset.sku), 1); save(); syncButtons(); renderList();
  });
  function openD() { drawer.classList.add('open'); scrim.hidden = false; drawer.setAttribute('aria-hidden', 'false'); }
  function closeD() { drawer.classList.remove('open'); scrim.hidden = true; drawer.setAttribute('aria-hidden', 'true'); }
  fab.addEventListener('click', openD);
  document.getElementById('dcp-dclose').addEventListener('click', closeD);
  scrim.addEventListener('click', closeD);
  document.getElementById('dcp-clear').addEventListener('click', function () {
    basket = []; save(); syncButtons(); renderList();
  });

  // submit RFQ → reference number (no backend)
  var form = document.getElementById('dcp-rform');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!form.checkValidity()) { form.reportValidity(); return; }
    if (!basket.length) { alert(L.empty); return; }
    var ref = 'RFQ-' + Date.now().toString(36).toUpperCase().slice(-6);
    var body = document.getElementById('dcp-dbody');
    body.innerHTML = '<div class="dcp-rok" role="status"><h3>' + L.ok_h + '</h3><p>' +
      L.ok_p.replace('{ref}', '<strong>' + ref + '</strong>').replace('{n}', basket.length) + '</p></div>';
    basket = []; save(); syncButtons();
  });

  syncButtons(); renderList(); apply();
})();
