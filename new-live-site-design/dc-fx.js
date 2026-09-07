/* Datacore mirror — lightweight motion for the generated pages: scroll-reveal
   of sections/cards and a count-up on the stats band. Reveal classes are added
   by JS, so with JS off (or reduced-motion) everything is simply visible.
   The live pages keep their own AOS; this only runs on the new pages. */
(function () {
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ── scroll reveal ───────────────────────────────────────────────
  if (!reduce && 'IntersectionObserver' in window) {
    var sel = '.dcp-sec, .dcp-proj, .dcp-post, .dcp-card, .dcp-method-step, .dcp-featcell, .dcp-stat';
    var items = [].slice.call(document.querySelectorAll(sel));
    items.forEach(function (el) { el.classList.add('dcx-reveal'); });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('dcx-in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    items.forEach(function (el) { io.observe(el); });
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

  // TODO(human): implement countUp(el, target, suffix)
  // Animate el.textContent from 0 up to `target` over roughly 1.2s, then set
  // the final value with `suffix` appended. Use requestAnimationFrame. Decide
  // the easing (linear feels mechanical; an ease-out finishes with a nice
  // deceleration) and make sure the very last frame lands exactly on `target`
  // (never target-1 from rounding). Keep it to ~6-10 lines.
  function countUp(el, target, suffix) {
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
