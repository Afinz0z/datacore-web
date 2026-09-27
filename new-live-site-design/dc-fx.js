/* Datacore mirror — lightweight motion for the generated pages: scroll-reveal
   of sections/cards and a count-up on the stats band. Reveal classes are added
   by JS, so with JS off (or reduced-motion) everything is simply visible.
   The live pages keep their own AOS; this only runs on the new pages. */
(function () {
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ── scroll reveal ───────────────────────────────────────────────
  // NB: product catalogue cards (.dcp-card) are deliberately NOT revealed —
  // there are 37 of them with lazy images, and a reveal that misfires would
  // leave the catalogue blank. They render immediately; images lazy-load.
  var sel = '.dcp-sec, .dcp-proj, .dcp-post, .dcp-method-step, .dcp-featcell, .dcp-stat';
  function setupReveal() {
    // Only animate blocks that start below the fold and fit on one screen.
    // Anything already on screen stays as first painted, and a block taller than
    // the screen (an article body, the catalogue, the insights list) is never
    // faded out: hiding it made the page body vanish while it opened.
    var fold = window.innerHeight;
    var items = [].slice.call(document.querySelectorAll(sel)).filter(function (el) {
      var r = el.getBoundingClientRect();
      return r.top > fold && r.height < fold;
    });
    items.forEach(function (el) { el.classList.add('dcx-reveal'); });
    // threshold 0 = reveal as soon as any part is on screen (a ratio such as
    // 0.12 can never be reached by a block several screens tall)
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('dcx-in'); io.unobserve(e.target); }
      });
    }, { threshold: 0, rootMargin: '0px 0px -8% 0px' });
    items.forEach(function (el) { io.observe(el); });
    // safety net: whatever the observer misses, reveal it so content is never
    // stuck invisible (e.g. programmatic scrolls, background tabs, odd engines)
    setTimeout(function () { items.forEach(function (el) { el.classList.add('dcx-in'); }); }, 2200);
  }
  if (!reduce && 'IntersectionObserver' in window) {
    // a page Chrome renders ahead of a click (speculation rules) is measured
    // once it is actually shown, against the real viewport
    if (document.prerendering) document.addEventListener('prerenderingchange', setupReveal, { once: true });
    else setupReveal();
  }

  // ── count-up on the stats band ──────────────────────────────────
  // Each stat number carries data-count="<target>" and optional
  // data-suffix (e.g. "+"). We start the tween the first time it scrolls
  // into view, then stop observing it.
  var nums = [].slice.call(document.querySelectorAll('[data-count]'));
  function run(el) {
    var target = parseInt(el.getAttribute('data-count'), 10) || 0;
    var suffix = el.getAttribute('data-suffix') || '';
    if (reduce) { el.textContent = target + suffix; return; }
    countUp(el, target, suffix);
  }

  // counts el from 0 up to target over ~1.2 s with an ease-out, then writes the
  // exact final value (rounding never leaves it one short)
  function countUp(el, target, suffix) {
    var t0 = null, dur = 1200;
    function frame(ts) {
      if (t0 === null) t0 = ts;
      var p = Math.min((ts - t0) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);       // ease-out cubic: decelerates in
      el.textContent = Math.round(eased * target) + suffix;
      if (p < 1) requestAnimationFrame(frame);
      else el.textContent = target + suffix;    // last frame lands exactly on target
    }
    requestAnimationFrame(frame);
  }

  if (nums.length) {
    if ('IntersectionObserver' in window) {
      var io2 = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { run(e.target); io2.unobserve(e.target); }
        });
      }, { threshold: 0.5 });
      nums.forEach(function (el) { io2.observe(el); });
    } else {
      nums.forEach(run);
    }
  }
})();
