/* Datacore mirror overlay: the EXACT developed-site header (logo, nav, theme
   toggle, language, consultation button) grafted onto the live pages, with the
   Services dropdown + dark/light + EN/AR. Live body HTML is untouched. */
(function () {
  var path = (location.pathname.split('/').pop() || 'index.html');
  var isAR = /-ar\.html$/.test(path);
  var stem = path.replace(/-ar\.html$/, '').replace(/\.html$/, '') || 'index';
  var live = 'https://www.datacore.com.sa/';
  var q = isAR ? '?lang=ar' : '';
  function localName(base) { return base + (isAR ? '-ar' : '') + '.html'; }
  function langSwap() { return isAR ? (stem + '.html') : (stem + '-ar.html'); }

  var T = isAR ? {
    about: 'من نحن', services: 'خدماتنا', products: 'المنتجات', projects: 'مشاريعنا',
    insights: 'ملاحظات تقنية', contact: 'تواصل معنا', lang: 'English',
    cta: 'اطلب استشارة', theme: 'التبديل بين الوضع الفاتح والداكن', menu: 'القائمة',
    chat_label: 'تحدث معنا', chat_h: 'كيف نساعدك؟', chat_p: 'اختر وسيلة التواصل وسنكمل من هناك.',
    chat_wa: 'محادثة واتساب', chat_call: 'الاتصال بمكتب الرياض', chat_mail: 'مراسلة المبيعات',
    chat_form: 'إرسال استفسار مشروع', call: 'اتصل'
  } : {
    about: 'About', services: 'Services', products: 'Products', projects: 'Projects',
    insights: 'Insights', contact: 'Contact', lang: 'العربية',
    cta: 'Request a consultation', theme: 'Switch between light and dark mode', menu: 'Open menu',
    chat_label: 'Chat with us', chat_h: 'How can we help?', chat_p: 'Pick a channel and we will take it from there.',
    chat_wa: 'Chat on WhatsApp', chat_call: 'Call the Riyadh office', chat_mail: 'Email sales',
    chat_form: 'Send a project enquiry', call: 'Call'
  };

  // 9 disciplines, each with its own services (second-level fly-out)
  var subs = [
  ['network-infrastructure-services','Network Infrastructure Services','البنية التحتية للشبكات',[
    ['structured-cabling-solutions','Structured Cabling Solutions','التمديدات الهيكلية'],
    ['fiber-optic-solutions','Fiber Optic Solutions','الألياف البصرية'],
    ['it-network-solutions','IT Network Solutions','شبكات تقنية المعلومات'],
    ['ups-systems','UPS Systems','أنظمة الطاقة غير المنقطعة'],
    ['wifi-solutions','Wifi Solutions','شبكات الواي فاي'],
    ['ip-telephony-solutions','IP Telephony Solutions','الهاتف عبر الشبكة']]],
  ['datacenter-solutions','Datacenter Solutions','حلول مراكز البيانات',[
    ['data-center-design-amp-implementation-services','Data Center Design & Implementation','تصميم وتنفيذ مراكز البيانات'],
    ['data-centre-migration-services-','Data Centre Migration Services','ترحيل مراكز البيانات'],
    ['data-centre-assessment-amp-recommendations','Assessment & Recommendations','التقييم والتوصيات']]],
  ['surveillance-and-security-solutions','Surveillance & Security Solutions','حلول المراقبة والأمن',[
    ['access-control-solutions','Access Control Solutions','التحكم في الدخول'],
    ['video-surveillance-solutions-amp-cctv','Video Surveillance & CCTV','المراقبة بالكاميرات وأنظمة CCTV'],
    ['parking-management-system','Parking Management System','إدارة المواقف'],
    ['grms-solutions-','GRMS Solutions','أنظمة إدارة الغرف']]],
  ['meeting-room-solutions','Meeting Room Solutions','حلول قاعات الاجتماعات',[
    ['video-conference-solution','Video Conference Solution','الاجتماعات المرئية'],
    ['room-amp-desk-booking-system','Room & Desk Booking System','حجز القاعات والمكاتب'],
    ['soc-noc-room-solution','SOC / NOC Room Solution','غرف العمليات والمراقبة'],
    ['acoustic-amp-lighting-solutions','Acoustic & Lighting Solutions','الصوتيات والإضاءة'],
    ['smart-meeting-room-amp-boardroom-solution','Smart Meeting Room & Boardroom','قاعات مجالس الإدارة']]],
  ['audio-visual-solutions','Audio-Visual Solutions','الحلول السمعية والبصرية',[
    ['auditorium','Auditorium','المسارح والقاعات'],
    ['smart-class-rooms','Smart Class Rooms','الفصول الذكية'],
    ['smart-building-solutions','Smart Building Solutions','المباني الذكية'],
    ['control-system','Control System','أنظمة التحكم'],
    ['interpreter-system','Interpreter System','الترجمة الفورية'],
    ['home-cinema-solution','Home Cinema Solution','السينما المنزلية'],
    ['professional-audio','Professional Audio','الصوتيات الاحترافية'],
    ['master-clock-system','Master Clock System','الساعة المركزية']]],
  ['digital-signage-amp-video-walls','Digital Signage & Video Walls','اللافتات الرقمية وشاشات العرض',[
    ['digital-signage-solutions','Digital Signage Solutions','اللافتات الرقمية'],
    ['indoor-led-video-wall','Indoor LED Video Wall','شاشات LED الداخلية'],
    ['outdoor-led-video-wall','Outdoor LED Video Wall','شاشات LED الخارجية'],
    ['interactive-video-walls-tiles','Interactive Video Walls / Tiles','الشاشات التفاعلية']]],
  ['public-address-and-fire-alarm-system','Public Address & Fire Alarm','النداء الآلي وإنذار الحريق',[
    ['pava-public-address-amp-voice-evacuation-system','PAVA Voice Evacuation','النداء والإخلاء الصوتي'],
    ['paga-public-address-and-general-alarm-system','PAGA General Alarm','النداء والإنذار العام'],
    ['fire-alarm-systems','Fire Alarm Systems','إنذار الحريق'],
    ['bgm-background-music-system','Background Music (BGM)','الموسيقى الخلفية']]],
  ['iptv-solutions','IPTV Solutions','حلول IPTV',[
    ['iptv-solution','IPTV Solution','حلول IPTV'],
    ['matv-solution','MATV Solution','حلول MATV']]],
  ['professional-services','Professional Services','الخدمات الاحترافية',[
    ['annual-maintenance-contracts','Annual Maintenance Contracts','عقود الصيانة السنوية'],
    ['full-time-staffing-solution','Full-time Staffing Solution','توفير الكوادر الدائمة']]]
  ];
  var caret = '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>';
  var caretSide = '<svg class="dcx-c2" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="' + (isAR ? 'M15 6l-6 6 6 6' : 'M9 6l6 6-6 6') + '"/></svg>';
  var subHTML = subs.map(function (s) {
    var kids = s[3].map(function (k) {
      return '<a href="service-' + k[0] + (isAR ? '-ar' : '') + '.html">' + (isAR ? k[2] : k[1]) + '</a>';
    }).join('');
    return '<div class="dcx-parent2"><a href="' + localName('services') + '?id=' + s[0] + '">' +
      (isAR ? s[2] : s[1]) + caretSide + '</a><div class="dcx-sub2">' + kids + '</div></div>';
  }).join('');

  function a(base, label, on) {
    return '<a href="' + localName(base) + '"' + (stem === on ? ' class="on"' : '') + '>' + label + '</a>';
  }
  var navHTML =
    a('about-us', T.about, 'about-us') +
    '<div class="dcx-drop"><a href="' + localName('services') + '" class="dcx-parent' +
      (stem === 'services' ? ' on' : '') + '" aria-haspopup="true">' + T.services + ' ' + caret +
      '</a><div class="dcx-sub">' + subHTML + '</div></div>' +
    a('products', T.products, 'products') +
    a('projects', T.projects, 'projects') +
    a('insights', T.insights, 'insights') +
    a('contact', T.contact, 'contact') +
    '<a class="menu-cta" href="' + localName('contact') + '">' + T.cta + '</a>';

  var moon = '<svg class="tmoon" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20.5 14.5A8.5 8.5 0 019.5 3.5a8.5 8.5 0 1011 11z"/></svg>';
  var sun = '<svg class="tsun" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.6M12 18.9v2.6M2.5 12h2.6M18.9 12h2.6M5 5l1.9 1.9M17.1 17.1L19 19M19 5l-1.9 1.9M6.9 17.1L5 19"/></svg>';
  var bars = '<svg class="bars" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M3 12h18M3 18h18"/></svg>';
  var xic = '<svg class="x" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 5l14 14M19 5L5 19"/></svg>';

  var hdr = document.createElement('header');
  hdr.className = 'hdr';
  hdr.id = 'dcx-hdr';
  hdr.setAttribute('dir', isAR ? 'rtl' : 'ltr');
  hdr.innerHTML =
    '<div class="wrap">' +
      '<a class="logo" href="' + localName('index') + '" aria-label="Datacore Solutions">' +
        '<img src="assets1/images/dc-logo.svg" alt="Datacore Solutions"></a>' +
      '<nav class="mainnav" id="mainnav" aria-label="Main">' + navHTML + '</nav>' +
      '<div class="hdr-cta">' +
        '<button class="tbtn" id="themeT" aria-label="' + T.theme + '">' + moon + sun + '</button>' +
        '<a class="lang" href="' + langSwap() + '">' + T.lang + '</a>' +
        '<a class="btn btn-p" href="' + localName('contact') + '">' + T.cta + '</a>' +
        '<button class="burger" aria-label="' + T.menu + '" aria-expanded="false" aria-controls="mainnav">' + bars + xic + '</button>' +
      '</div>' +
    '</div>';

  // The live pages link to service-details/<slug>; we ship those as flat
  // service-<slug>.html files. The live markup on disk is never modified.
  // Some of these links are injected by the live page's own late scripts
  // (footer / mega-menu) after we mount, and can sit outside #dc-content —
  // so a one-shot rewrite misses them. We (1) rewrite whatever is present
  // now and again on load, for correct hover/SEO, and (2) delegate clicks at
  // the document level as the guarantee, which works no matter when a link
  // appears or whether the rewrite reached it.
  function localSvc(slug) { return 'service-' + slug + (isAR ? '-ar' : '') + '.html'; }
  function slugOf(href) { var m = (href || '').match(/service-details\/([a-z0-9-]+)/i); return m && m[1]; }
  // live absolute path (first segment) -> local page base
  var LINKMAP = {
    '': 'index', 'career': 'careers', 'careers': 'careers',
    'contact-us': 'contact', 'contact': 'contact',
    'projects': 'projects', 'project': 'projects',
    'blogs': 'insights', 'blog': 'insights',
    'terms-service': 'terms', 'terms-of-service': 'terms', 'privacy-policy': 'privacy',
    'about-us': 'about-us', 'about': 'about-us', 'services': 'services', 'service': 'services',
    'products': 'products', 'product': 'products'
  };
  function localFor(href) {
    var s = slugOf(href); if (s) return localSvc(s);
    var m = (href || '').match(/datacore\.com\.sa\/([a-z0-9-]*)/i);
    if (m && LINKMAP.hasOwnProperty(m[1].toLowerCase())) return localName(LINKMAP[m[1].toLowerCase()]);
    return null;   // unmapped datacore link (or external) — leave it alone
  }
  function fixLinks() {
    var as = document.querySelectorAll('a[href*="service-details/"], a[href*="datacore.com.sa"]');
    for (var i = 0; i < as.length; i++) {
      var loc = localFor(as[i].getAttribute('href'));
      if (loc) as[i].setAttribute('href', loc);
    }
  }
  document.addEventListener('click', function (ev) {
    var a = ev.target.closest && ev.target.closest('a[href*="service-details/"], a[href*="datacore.com.sa"]');
    if (!a) return;
    var loc = localFor(a.getAttribute('href') || a.href);
    if (loc) { ev.preventDefault(); location.href = loc; }
  }, true);

  // The live tawk.to chat + reCAPTCHA challenge inject iframes into <body> with
  // random ids (no stable selector), outside our wrappers. Our own chat has no
  // iframe and the office map lives inside #dc-content, so hiding every body-
  // level iframe removes the duplicate chatbot / domain-locked error box only.
  function killWidgets() {
    var fr = document.querySelectorAll('iframe');
    for (var i = 0; i < fr.length; i++) {
      var f = fr[i];
      if (f.closest('#dcx-chat') || f.closest('#dc-content')) continue;
      var host = (f.parentElement && f.parentElement !== document.body) ? f.parentElement : f;
      host.style.setProperty('display', 'none', 'important');
    }
  }

  function mount() {
    if (document.getElementById('dc-content')) return;
    var wrap = document.createElement('div');
    wrap.id = 'dc-content';
    while (document.body.firstChild) wrap.appendChild(document.body.firstChild);
    document.body.appendChild(hdr);
    document.body.appendChild(wrap);
    fixLinks();
    addEventListener('load', fixLinks);
    setTimeout(fixLinks, 1200);
    // tawk.to is now stripped from the live HTML entirely; this only hides the
    // domain-locked reCAPTCHA challenge iframe (appended to <body> on demand)
    killWidgets();
    setTimeout(killWidgets, 2000);
    try { new MutationObserver(killWidgets).observe(document.body, { childList: true }); } catch (e) {}

    document.getElementById('themeT').addEventListener('click', function () {
      var dark = document.documentElement.classList.toggle('dc-dark');
      try { localStorage.setItem('dc-theme', dark ? 'dark' : 'light'); } catch (e) {}
    });
    var nv = document.getElementById('mainnav');
    var bg = hdr.querySelector('.burger');
    bg.addEventListener('click', function () {
      var open = nv.classList.toggle('open');
      bg.setAttribute('aria-expanded', String(open));
    });
    nv.addEventListener('click', function (ev) {
      if (ev.target.closest('a') && nv.classList.contains('open')) {
        nv.classList.remove('open'); bg.setAttribute('aria-expanded', 'false');
      }
    });
    matchMedia('(min-width:901px)').addEventListener('change', function (m) {
      if (m.matches) { nv.classList.remove('open'); bg.setAttribute('aria-expanded', 'false'); }
    });

    buildExtras();
  }

  // ── quick-contact bubble + sticky mobile CTA (added on every page) ──────
  var WA = 'https://wa.me/966115128888';   // Riyadh line — client to confirm WA Business
  var TEL = '+966115128888';
  var MAIL = 'sales@datacore.com.sa';
  function cico(p) {
    return '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" ' +
      'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + p + '</svg>';
  }
  function buildExtras() {
    // quick-contact bubble
    var chat = document.createElement('div');
    chat.id = 'dcx-chat';
    chat.setAttribute('dir', isAR ? 'rtl' : 'ltr');
    chat.innerHTML =
      '<div class="chatp" id="dcxChatP" role="dialog" aria-label="' + T.chat_label + '" hidden>' +
        '<header><strong>' + T.chat_h + '</strong><p>' + T.chat_p + '</p></header>' +
        '<div class="acts">' +
          '<a href="' + WA + '" target="_blank" rel="noopener">' +
            cico('<path d="M21 12a8 8 0 01-11.6 7.2L4 21l1.8-5.4A8 8 0 1121 12z"/>') + T.chat_wa + '</a>' +
          '<a href="tel:' + TEL + '">' +
            cico('<path d="M5 4h4l2 5-2.5 1.5a12 12 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z"/>') + T.chat_call + '</a>' +
          '<a href="mailto:' + MAIL + '">' +
            cico('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>') + T.chat_mail + '</a>' +
          '<a href="' + localName('contact') + '">' +
            cico('<path d="M14 3H6a2 2 0 00-2 2v14a2 2 0 002 2h12a2 2 0 002-2V9z"/><path d="M14 3v6h6M9 14h6M9 17h4"/>') + T.chat_form + '</a>' +
        '</div></div>' +
      '<button class="chatb" id="dcxChatB" aria-expanded="false" aria-controls="dcxChatP" aria-label="' + T.chat_label + '">' +
        '<img class="dcx-logo" src="assets1/images/dc-logo-chat.png" alt="" aria-hidden="true" width="34" height="34">' +
        '<svg class="x" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 5l14 14M19 5L5 19"/></svg>' +
      '</button>';
    document.body.appendChild(chat);
    // scroll-progress bar + back-to-top button (outside #dc-content so position:fixed holds)
    var dcxProg = document.createElement('div'); dcxProg.id = 'dcx-prog'; document.body.appendChild(dcxProg);
    var dcxTop = document.createElement('button'); dcxTop.id = 'dcx-top'; dcxTop.type = 'button';
    dcxTop.setAttribute('aria-label', isAR ? 'العودة إلى الأعلى' : 'Back to top');
    dcxTop.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 19V5M5 12l7-7 7 7"/></svg>';
    document.body.appendChild(dcxTop);
    dcxTop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
    // condense the developed header once the page scrolls (toggles dcx-scrolled → CSS)
    var onDcxScroll = function () {
      var de = document.documentElement, y = window.pageYOffset || de.scrollTop || 0;
      de.classList.toggle('dcx-scrolled', y > 24);
      dcxProg.style.transform = 'scaleX(' + (de.scrollHeight > de.clientHeight ? y / (de.scrollHeight - de.clientHeight) : 0) + ')';
      dcxTop.classList.toggle('show', y > 500);
    };
    window.addEventListener('scroll', onDcxScroll, { passive: true }); onDcxScroll();
    var btn = chat.querySelector('#dcxChatB'), panel = chat.querySelector('#dcxChatP');
    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!open)); panel.hidden = open;
    });
    document.addEventListener('click', function (e) {
      if (!chat.contains(e.target) && btn.getAttribute('aria-expanded') === 'true') {
        btn.setAttribute('aria-expanded', 'false'); panel.hidden = true;
      }
    });
    // First visit only: auto-open the chat once so newcomers see the contact options.
    try {
      if (!localStorage.getItem('dcx-chat-seen')) {
        localStorage.setItem('dcx-chat-seen', '1');
        setTimeout(function () {
          if (btn.getAttribute('aria-expanded') !== 'true') {
            btn.setAttribute('aria-expanded', 'true'); panel.hidden = false;
          }
        }, 1400);
      }
    } catch (e) {}

    // sticky mobile CTA — not on the contact page (it is the destination)
    if (stem !== 'contact') {
      var bar = document.createElement('div');
      bar.id = 'dcx-sticky';
      bar.setAttribute('dir', isAR ? 'rtl' : 'ltr');
      bar.innerHTML =
        '<a class="s-call" href="tel:' + TEL + '">' +
          cico('<path d="M5 4h4l2 5-2.5 1.5a12 12 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z"/>') +
          '<span>' + T.call + '</span></a>' +
        '<a class="s-cta" href="' + localName('contact') + '">' + T.cta + '</a>';
      document.body.appendChild(bar);
      document.documentElement.classList.add('dcx-has-sticky');
    }
  }

  if (document.body) mount();
  else document.addEventListener('DOMContentLoaded', mount);
})();
