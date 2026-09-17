/* Datacore — cookie consent + Google Tag Manager (GTM-TPKMT6DS), Consent Mode v2.
 *
 * Load this EARLY in <head> on every page. It:
 *   1. sets Consent Mode defaults to DENIED (analytics/ads) for everyone,
 *   2. re-applies a previously stored choice (localStorage 'dc-consent'),
 *   3. loads GTM (which, under Consent Mode, holds cookie-setting tags until
 *      consent is granted),
 *   4. shows a consent banner once — Accept grants, Decline keeps denied.
 * No tracking cookies are set until the visitor clicks Accept.
 */
(function () {
  var GTM_ID = 'GTM-TPKMT6DS';
  var KEY = 'dc-consent';

  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;

  // 1. default everything off (safe for every jurisdiction)
  gtag('consent', 'default', {
    ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied',
    analytics_storage: 'denied', functionality_storage: 'granted',
    security_storage: 'granted', wait_for_update: 500
  });

  // 2. re-apply a stored choice
  var choice = null;
  try { choice = localStorage.getItem(KEY); } catch (e) {}
  function grant() {
    gtag('consent', 'update', {
      ad_storage: 'granted', ad_user_data: 'granted',
      ad_personalization: 'granted', analytics_storage: 'granted'
    });
  }
  if (choice === 'granted') grant();

  // 3. load GTM (tags stay held until consent under Consent Mode)
  (function (w, d, s, l, i) {
    w[l] = w[l] || []; w[l].push({ 'gtm.start': new Date().getTime(), event: 'gtm.js' });
    var f = d.getElementsByTagName(s)[0], j = d.createElement(s),
        dl = l != 'dataLayer' ? '&l=' + l : '';
    j.async = true; j.src = 'https://www.googletagmanager.com/gtm.js?id=' + i + dl;
    f.parentNode.insertBefore(j, f);
  })(window, document, 'script', 'dataLayer', GTM_ID);

  // 4. banner — only if no prior choice
  if (choice === 'granted' || choice === 'denied') return;

  function save(v) {
    try { localStorage.setItem(KEY, v); } catch (e) {}
    if (v === 'granted') grant();
    var b = document.getElementById('dc-cookie');
    if (b) b.parentNode.removeChild(b);
  }

  function build() {
    if (document.getElementById('dc-cookie')) return;
    var st = document.createElement('style');
    st.textContent =
      '#dc-cookie{position:fixed;inset-block-end:18px;inset-inline-start:18px;z-index:2147483000;' +
      'max-width:392px;background:#171a20;color:#eef0f0;border:1px solid rgba(255,255,255,.10);' +
      'border-radius:14px;box-shadow:0 12px 34px rgba(0,0,0,.28);padding:18px 20px 16px;' +
      "font-family:'Texta',system-ui,-apple-system,'Segoe UI',sans-serif;line-height:1.5;font-size:14.5px}" +
      '#dc-cookie h4{margin:0 0 5px;font-size:15.5px;font-weight:700;color:#fff}' +
      '#dc-cookie p{margin:0 0 13px;color:#c3c7cc}' +
      '#dc-cookie a{color:#33c3b5;text-decoration:underline}' +
      '#dc-cookie .dc-ck-row{display:flex;gap:10px;flex-wrap:wrap}' +
      '#dc-cookie button{flex:1 1 auto;min-width:120px;font:inherit;font-weight:600;font-size:14px;' +
      'border-radius:8px;padding:10px 16px;cursor:pointer;border:1px solid transparent;transition:filter .2s,background .2s}' +
      '#dc-cookie .dc-ck-yes{background:#00a99a;color:#00201d}' +
      '#dc-cookie .dc-ck-yes:hover{filter:brightness(1.08)}' +
      '#dc-cookie .dc-ck-no{background:transparent;color:#eef0f0;border-color:rgba(255,255,255,.22)}' +
      '#dc-cookie .dc-ck-no:hover{background:rgba(255,255,255,.08)}' +
      '#dc-cookie button:focus-visible{outline:2px solid #33c3b5;outline-offset:2px}' +
      '@media(max-width:600px){#dc-cookie{inset-inline:12px;inset-block-end:84px;max-width:none}}' +
      '@media(prefers-reduced-motion:no-preference){#dc-cookie{animation:dcCkIn .35s ease both}' +
      '@keyframes dcCkIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}}';
    document.head.appendChild(st);

    var el = document.createElement('div');
    el.id = 'dc-cookie';
    el.setAttribute('role', 'dialog');
    el.setAttribute('aria-live', 'polite');
    el.setAttribute('aria-label', 'Cookie consent');
    var priv = (document.documentElement.lang === 'ar') ? 'privacy-ar.html' : 'privacy.html';
    var ar = (document.documentElement.lang === 'ar');
    el.innerHTML =
      '<h4>' + (ar ? 'نحترم خصوصيتك' : 'We value your privacy') + '</h4>' +
      '<p>' + (ar
        ? 'نستخدم ملفات تعريف الارتباط لفهم كيفية استخدام الموقع وتحسينه. لا تُفعَّل أدوات التحليل إلا بموافقتك. '
        : 'We use cookies to understand how the site is used and improve it. Analytics only run if you accept. ') +
      '<a href="' + priv + '">' + (ar ? 'سياسة الخصوصية' : 'Privacy Policy') + '</a></p>' +
      '<div class="dc-ck-row">' +
      '<button type="button" class="dc-ck-yes">' + (ar ? 'أوافق' : 'Accept') + '</button>' +
      '<button type="button" class="dc-ck-no">' + (ar ? 'رفض' : 'Decline') + '</button>' +
      '</div>';
    document.body.appendChild(el);
    el.querySelector('.dc-ck-yes').addEventListener('click', function () { save('granted'); });
    el.querySelector('.dc-ck-no').addEventListener('click', function () { save('denied'); });
  }

  if (document.readyState !== 'loading') build();
  else document.addEventListener('DOMContentLoaded', build);
})();
