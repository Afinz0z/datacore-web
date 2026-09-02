# -*- coding: utf-8 -*-
"""
Every string on the site, in both languages, in one file.
Structure is identical between 'en' and 'ar' so the builder can render either
without branching. Arabic is a first draft — see BUILD-NOTES.md.
"""

# Social accounts — one place, used in the footer and on the contact page.
SOCIALS = [
 ("linkedin",  "https://www.linkedin.com/company/datacore-solutions", "LinkedIn"),
 ("instagram", "https://www.instagram.com/datacore_sa/",              "Instagram"),
 ("facebook",  "https://www.facebook.com/www.datacore.com.sa/",       "Facebook"),
]

# (lat,lng | None, search query). Riyadh coordinates come from the old site's
# embed. Dubai and Kozhikode resolve by address query — confirm the pins.
OFFICE_GEO = [
 ("24.6675676,46.7045394",
  "Datacore Solutions, Dabbab Complex, Dabbab St, Riyadh 12626, Saudi Arabia"),
 (None, "DCS Advanced Technologies L.L.C, Um Hurair Second, Dubai, UAE"),
 (None, "Artifitia Solutions LLP, Sahya Building, Govt Cyberpark, Kozhikode, Kerala 673016"),
]

PARTNERS = ["Crestron","Extron","Shure","Bosch","Honeywell","Suprema","Logitech",
            "Yealink","Lenovo","CommScope","Eaton","ACTi","AET","SMART"]

C = {}

# ══════════════════════════════════════════════════════════════════════════
#  ENGLISH
# ══════════════════════════════════════════════════════════════════════════
C['en'] = {
 'dir':'ltr','lang':'en','other':'ar','other_label':'العربية','other_lang':'ar',
 'font':"family=Archivo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500",

 'nav':[('about','About'),('services','Services'),('products','Products'),
        ('projects','Projects'),('insights','Insights'),('contact','Contact')],
 'brand_line':'Low-current systems integration across Saudi Arabia, the UAE and India. '
               'Integrating since 2007.',
 'consult':'Request a consultation','see_projects':'See our projects',
 'get_quote':'Request a quote','profile':'Company profile (PDF)',
 'skip':'Skip to content','menu':'Open menu','home':'Home','read':'Read more',

 # ── home ──────────────────────────────────────────────────────────────
 'h_eyebrow':'Low-current systems integration',
 'h_title':'Every low-current scope, from one contractor.',
 'h_lede':('Datacore designs, supplies, installs and maintains the systems a building runs on '
           '— networks, datacentres, security, audio-visual and life safety. Since 2007, for '
           '<b>Arab Open University</b>, <b>Prince Sattam bin Abdulaziz University</b>, '
           '<b>TAQEEM</b> and more than a thousand others across Saudi Arabia and the UAE.'),
 'h_stack':'Nine disciplines, 38 services','h_scope':'SCOPE',
 'stats':[('1,000+','Clients served since 2007'),
          ('100+','Engineers and technicians on staff'),
          ('3','Countries: Saudi Arabia, UAE, India'),
          ('19','Years integrating low-current systems')],
 'h_disc_title':'What we install, commission and maintain',
 'h_disc_lede':('Every discipline below is delivered in-house — design, supply, installation, '
                'commissioning, handover documentation and a maintenance contract.'),
 'h_proj_title':'Recent work',
 'h_proj_lede':('Named clients, stated scope, and the equipment we deployed — linked to the '
                'catalogue so you can specify the same parts.'),
 'h_tl_title':'How the scope grew',
 'h_tl_lede':('Each step added a discipline we now deliver in-house, which is how a single '
              'low-current package became possible.'),
 'h_part_title':'Manufacturers we are authorised to install',
 'h_part_lede':('Authorisation matters on a tender: it determines warranty validity, access to '
                'firmware, and whether the manufacturer supports your system after handover.'),
 'h_ins_title':'Technical notes',
 'h_ins_lede':'Written by our engineers from work we have delivered.',

 # ── disciplines ───────────────────────────────────────────────────────
 'disc':[
  ('network','Network infrastructure',
   ['Structured cabling','Fibre optic','IT networks','UPS systems','Wi-Fi','IP telephony'],
   'Cat6A · OM4 · TIA-568 · ISO/IEC 11801',
   'The passive and active layers a building cannot cheaply revisit later — cabling, '
   'containment, switching, wireless and voice.'),
  ('datacentre','Datacentre',
   ['Design & implementation','Migration','Assessment & recommendations'],
   'Containment · power · cooling · DCIM',
   'From a white-space design through to a live migration, including assessment of what '
   'you already have.'),
  ('security','Surveillance & security',
   ['Access control','Video surveillance & CCTV','Parking management','GRMS'],
   'ONVIF · integrated with HR and visitor systems',
   'Who gets in, what was recorded, and how both tie into the systems your operations '
   'team already uses.'),
  ('meeting','Meeting rooms',
   ['Video conferencing','Room & desk booking','SOC / NOC rooms','Acoustics & lighting',
    'Boardrooms'],
   'Teams Rooms · Zoom Rooms · BYOD',
   'Rooms that start on time. Standardised platforms, treated acoustics and one control '
   'interface across the estate.'),
  ('av','Audio-visual',
   ['Auditoriums','Smart classrooms','Smart buildings','Control systems','Interpretation',
    'Home cinema','Professional audio','Master clock'],
   'AV-over-IP · Dante · programmed control',
   'Our largest discipline. Lecture theatres, auditoria and teaching spaces, designed '
   'acoustically and programmed to be operated by non-technical staff.'),
  ('signage','Signage & video walls',
   ['Digital signage','Indoor LED','Outdoor LED','Interactive walls'],
   'Fine-pitch LED · content management',
   'Fine-pitch LED and managed content, from a single lobby screen to a campus-wide '
   'signage network.'),
  ('pava','Public address & fire alarm',
   ['PAVA voice evacuation','PAGA general alarm','Fire alarm','Background music'],
   'EN 54-16 · EN 54-24 · Saudi Building Code',
   'Life-safety systems where the standard is not optional — intelligibility calculations, '
   'certified amplifiers and loudspeakers, and documented commissioning.'),
  ('iptv','IPTV & MATV',
   ['IPTV','MATV'],
   'Hospitality · healthcare · campus distribution',
   'Television and video distribution over the network you already have, or over coax '
   'where that is what the building has.'),
  ('professional','Maintenance & staffing',
   ['Annual maintenance contracts','Full-time staffing'],
   'SLA-backed · on-site resident engineers',
   'What happens after handover. Response-time-backed contracts, and resident engineers '
   'where a site needs someone permanently.'),
 ],

 # ── services hub (per-discipline sub-service blurbs) ──────────────────
 'svc_blurbs':{
  'Structured cabling':'Cat6A and Cat6 copper systems with 25-year manufacturer warranties, '
                       'certified and test-reported per link.',
  'Fibre optic':'OM4 and single-mode backbones, fusion spliced and OTDR tested, with '
                'documented loss budgets.',
  'IT networks':'Switching, routing and segmentation, from a floor closet to a campus core.',
  'UPS systems':'Online double-conversion UPS with battery sizing to your real load, plus '
                'the maintenance schedule that keeps it valid.',
  'Wi-Fi':'Predictive and on-site surveys, then a design that holds up under real device '
          'density rather than an empty floor plate.',
  'IP telephony':'IP PBX and handsets integrated with your directory and contact centre.',
  'Design & implementation':'White space, containment, power distribution, cooling and '
                            'monitoring, delivered as one package.',
  'Migration':'Moving live workloads and physical estate with a rollback plan and a '
              'window your operations team agrees to.',
  'Assessment & recommendations':'An independent look at capacity, resilience and airflow, '
                                 'with a costed remediation list.',
  'Access control':'Card, mobile and biometric credentials, with anti-passback, visitor '
                   'management and HR integration.',
  'Video surveillance & CCTV':'Camera selection driven by the identification distance you '
                              'actually need, with storage sized to your retention policy.',
  'Parking management':'ANPR, barriers and guidance, integrated with access control so one '
                       'credential works everywhere.',
  'GRMS':'Guest room management — lighting, climate and door status on one platform.',
  'Video conferencing':'Certified Teams and Zoom rooms, sized to the table rather than to '
                       'the room.',
  'Room & desk booking':'Panels and back-end integration with your calendar system.',
  'SOC / NOC rooms':'Operations rooms built for continuous occupancy: sightlines, video '
                    'wall geometry, acoustics and glare.',
  'Acoustics & lighting':'Treatment and lighting design so microphones and cameras have '
                         'something to work with.',
  'Boardrooms':'Executive rooms where every control is where the last one was.',
  'Auditoriums':'Line arrays, projection or LED, stage infrastructure and a control system '
                'an events officer can run alone.',
  'Smart classrooms':'Displays, classroom audio and lecture capture, deployed to a repeatable '
                     'standard across a campus.',
  'Smart buildings':'Integration between AV, lighting, HVAC and occupancy so systems stop '
                    'acting independently.',
  'Control systems':'Programmed control — Crestron and equivalent — with interfaces designed '
                    'for the person who actually uses the room.',
  'Interpretation':'Booths, receivers and distribution for multilingual sessions.',
  'Home cinema':'Private residential cinema, calibrated.',
  'Professional audio':'Live sound and installed audio for worship, sport and performance '
                       'spaces.',
  'Master clock':'Synchronised time across a facility, GPS or NTP disciplined.',
  'Digital signage':'Screens, players and a content management system your marketing team '
                    'can run without us.',
  'Indoor LED':'Fine-pitch indoor LED, sized to viewing distance rather than to budget alone.',
  'Outdoor LED':'IP-rated outdoor LED with brightness and redundancy suited to the Gulf '
                'climate.',
  'Interactive walls':'Touch-enabled video walls and tiles for exhibition and command spaces.',
  'PAVA voice evacuation':'Voice evacuation to EN 54-16 and EN 54-24, with intelligibility '
                          'modelling and documented commissioning.',
  'PAGA general alarm':'General alarm for industrial and process environments.',
  'Fire alarm':'Detection and alarm, integrated with evacuation and access control.',
  'Background music':'Zoned background music that shares infrastructure with the PA system.',
  'IPTV':'Live and on-demand video over IP for hospitality, healthcare and campus.',
  'MATV':'Coaxial television distribution where the building already has the pathway.',
  'Annual maintenance contracts':'Response-time-backed cover with scheduled preventive visits '
                                 'and a spares holding.',
  'Full-time staffing':'Resident engineers and technicians placed on your site, managed by us.',
 },

 # ── projects ──────────────────────────────────────────────────────────
 'proj':[
  ('EDUCATION','RIYADH','Smart modernisation of the AOU council room',
   'Rebuilt the council chamber around a single integrated AV system: unified communications '
   'compatibility, wireless BYOD presentation, corrected audio clarity for a reverberant room, '
   'and one control interface the secretariat can actually use.',
   ['AV-over-IP','Ceiling microphones','Control processor'],
   'Arab Open University','Design, supply, install, commission'),
  ('EDUCATION','AL-KHARJ','Smart classrooms across the PSAU campus',
   'Campus-wide rollout of teaching displays, classroom audio and UC-enabled lecture capture, '
   'with centrally managed digital signage tying classrooms, meeting rooms and auditoriums '
   'into one content system.',
   ['Interactive displays','Classroom audio','Signage CMS'],
   'Prince Sattam bin Abdulaziz University','Multi-building campus rollout'),
  ('GOVERNMENT','RIYADH','Comprehensive AV solution for TAQEEM HQ',
   'A single AV standard applied across meeting rooms, executive offices and the in-house '
   'theatre — smart displays, distributed audio, wireless sharing and consistent control, so '
   'every room behaves the same way.',
   ['Wireless presentation','Distributed audio','Commercial displays'],
   'TAQEEM','HQ-wide AV standardisation'),
  ('EDUCATION','RIYADH','University auditorium AV',
   'A 4K LED video wall with full audio-video distribution, BYOD connectivity for visiting '
   'speakers, and iPad-based control for staff running events without a technician in the room.',
   ['LED video wall','Line array','Touch control'],
   'Arab Open University','Auditorium fit-out'),
 ],
 'p_client':'Client','p_scope':'Scope','p_sector':'Sector',

 # ── timeline ──────────────────────────────────────────────────────────
 'tl':[('2007','Founded in Jeddah','IT networking and passive infrastructure.'),
       ('2013','Datacentre','End-to-end datacentre facilities added to the scope.'),
       ('2016','Audio-visual & PA','Entered the AV and public address market.'),
       ('2020','Turnkey low current','Complete low-current packages on mega projects.'),
       ('2023','100+ specialists','Workforce passed one hundred professionals.')],

 # ── about ─────────────────────────────────────────────────────────────
 'a_title':'Nineteen years of executing without fail.',
 'a_lede':('Datacore Solutions is a low-current systems integrator. We were founded in Jeddah '
           'in 2007 doing IT networking and passive infrastructure, and we have added a '
           'discipline roughly every four years since.'),
 'a_story_h':'Our story',
 'a_story':[
  'The company started in Jeddah in 2007 with a narrow scope: IT networking and passive '
  'infrastructure. That is a good place to start, because the passive layer is the part of a '
  'building nobody can cheaply revisit once the ceiling closes.',
  'We opened in Riyadh in 2010, entered the datacentre market in 2013 and the audio-visual '
  'and public address market in 2016. By 2020 we were taking complete low-current scopes as '
  'turnkey packages on mega projects, which is only possible when every discipline is in-house. '
  'The workforce passed one hundred in 2023.',
  'Today that means networks, cabling infrastructure, point-to-point wireless, datacentres, '
  'surveillance and access control, audio-visual, LED displays, professional audio, public '
  'address and fire alarm — delivered from Riyadh, Dubai and Kozhikode. Our success is built '
  'on one commitment: executing every project without fail.'],
 'a_vals_h':'What we hold ourselves to',
 'a_vals':[
  ('Innovation','We adopt technology when it solves a problem on site, not when it appears in '
   'a manufacturer roadmap.'),
  ('Client centricity','The person who operates the room after handover is the person the '
   'design has to satisfy.'),
  ('Integrity','If a scope will not work as drawn, we say so before award, not after.'),
  ('Security','Systems are designed to be defensible — segmented, credentialed and logged.'),
  ('Reliability','Response times are contractual, not aspirational.'),
  ('Progression','Every project should leave the team able to do the next one better.')],
 'a_where_h':'Where we work',
 'a_where':('Head office in Riyadh, a UAE entity in Dubai as DCS Advanced Technologies, and an '
            'engineering office in Kozhikode as Artifitia Solutions. Projects are delivered '
            'across the Kingdom from Riyadh.'),

 # ── insights ──────────────────────────────────────────────────────────
 'i_title':'Technical notes',
 'i_lede':('Notes from our engineers on the decisions that come up on real projects. No '
           'product announcements.'),
 'posts':[
  ('3 March 2026','Systems team','What is a public address system?',
   'Where public address ends and voice evacuation begins, and why the distinction changes '
   'which standard your project has to meet — and therefore what your amplifiers and '
   'loudspeakers have to be certified to.'),
  ('16 February 2026','Network team','The impact of 5G on passive networks',
   'What denser radio deployment does to fibre counts, pathway sizing and containment in a '
   'building you are designing today.'),
  ('3 March 2026','Network team','Active versus passive network infrastructure',
   'A plain explanation of the split, and why the passive layer is the part you cannot '
   'cheaply revisit later.')],

 # ── contact ───────────────────────────────────────────────────────────
 'c_title':'Tell us about the project.',
 'c_lede':('Send a BOQ, a schedule of materials or a set of drawings and we will come back '
           'with a priced scope and a programme. Earlier than that, we will do a site survey.'),
 'c_form_h':'Project enquiry',
 'c_f':{'name':'Your name','company':'Company','email':'Email','phone':'Phone',
        'type':'What do you need?','project':'Project',
        'project_hint':'Building, location, stage',
        'msg':'Scope or question','send':'Send enquiry',
        'note':'We acknowledge every enquiry with a reference number, and reply within one '
               'working day.'},
 'c_types':['A price for a defined scope','A site survey','Maintenance contract',
            'Product quotation','Careers','Something else'],
 'map_h':'Find us',
 'map_load':'Load the map',
 'map_note':'The map loads from Google only when you ask it to, so it does not slow the page '
            'down or set cookies before you choose.',
 'directions':'Directions',
 'follow_h':'Follow us',
 'follow_p':'Project photos and company news go out on LinkedIn and Instagram.',
 'c_offices_h':'Offices',
 'c_other_h':'Other ways to reach us',
 'offices':[
  ('Saudi Arabia — head office','Datacore Solutions','Office 503, Dabbab Complex, Dabbab St.',
   'Riyadh 12626','+966 11 512 8888','+966115128888'),
  ('United Arab Emirates','DCS Advanced Technologies L.L.C','OF09-390, Um Hurair Second',
   'Dubai','+971 52 753 6070','+971527536070'),
  ('India','Artifitia Solutions LLP','No. 26, Sahya Building, Govt Cyberpark',
   'Kozhikode, Kerala 673016','+91 495 350 1154','+914953501154')],

 # ── products ──────────────────────────────────────────────────────────
 'pr_title':'Products',
 'pr_lede':('Network, security, audio-visual and infrastructure hardware supplied and '
            'installed across the Kingdom. Add what you need to a request and our team '
            'returns a priced quotation with lead times.'),

 # ── services hub ──────────────────────────────────────────────────────
 's_title':'Nine disciplines. Thirty-eight services. One contractor.',
 's_lede':('Everything below is delivered in-house: design, supply, installation, '
           'commissioning, handover documentation and a maintenance contract. That is what '
           'makes a single turnkey low-current package possible.'),
 's_all':'All disciplines',

 # ── projects page ─────────────────────────────────────────────────────
 'pj_title':'Projects',
 'pj_lede':('Named clients, stated scope and the equipment deployed. Filter by sector or '
            'discipline.'),
 'pj_feat_h':'How we work on site',
 'pj_feat':[('Innovative engineering','Design decisions justified against the operational '
             'requirement, not the catalogue.'),
            ('Scalable infrastructure','Capacity for the next phase designed in from the '
             'first one.'),
            ('Client-centric approach','The operator, not the specifier, is the user we '
             'design for.'),
            ('End-to-end delivery','One contractor from survey through to maintenance.'),
            ('Proactive service','Faults found on scheduled visits, not by your users.')],

 # ── CTA + footer ──────────────────────────────────────────────────────
 'cta_h':'Have drawings? Send them over.',
 'cta_p':('Share a BOQ, a schedule of materials or a set of drawings and we will come back '
          'with a priced scope and a programme. If you are earlier than that, we will do a '
          'site survey.'),
 'f_company':'COMPANY','f_services':'SERVICES','f_touch':'GET IN TOUCH',
 'f_links':[('about','About us'),('projects','Projects'),('insights','Insights')],
 'f_careers':'Careers','f_catalogue':'Product catalogue','f_whatsapp':'WhatsApp',
 'f_all_disc':'All nine disciplines',
 'f_terms':'Terms of service','f_privacy':'Privacy policy',
 'f_rights':'© 2026 Datacore Solutions',
 'f_legal':'CR 0000000000 · VAT 300000000000003',
}

# ══════════════════════════════════════════════════════════════════════════
#  ARABIC
# ══════════════════════════════════════════════════════════════════════════
C['ar'] = {
 'dir':'rtl','lang':'ar','other':'en','other_label':'English','other_lang':'en',
 'font':"family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Archivo:wght@400;600",

 'nav':[('about','من نحن'),('services','خدماتنا'),('products','المنتجات'),
        ('projects','مشاريعنا'),('insights','مقالات تقنية'),('contact','تواصل معنا')],
 'brand_line':'تكامل أنظمة التيار الخفيف في المملكة العربية السعودية والإمارات والهند. '
               'نعمل في هذا المجال منذ عام 2007.',
 'consult':'اطلب استشارة','see_projects':'اطّلع على مشاريعنا',
 'get_quote':'اطلب عرض سعر','profile':'الملف التعريفي (PDF)',
 'skip':'تخطَّ إلى المحتوى','menu':'افتح القائمة','home':'الرئيسية','read':'اقرأ المزيد',

 'h_eyebrow':'تكامل أنظمة التيار الخفيف',
 'h_title':'جميع أعمال التيار الخفيف، من مقاول واحد.',
 'h_lede':('تقوم داتاكور بتصميم وتوريد وتركيب وصيانة الأنظمة التي يعتمد عليها المبنى: '
           'الشبكات ومراكز البيانات وأنظمة الأمن والأنظمة السمعية والبصرية وأنظمة السلامة. '
           'منذ عام 2007، لصالح <b>الجامعة العربية المفتوحة</b> و<b>جامعة الأمير سطام بن '
           'عبدالعزيز</b> و<b>تقييم</b> وأكثر من ألف عميل في المملكة والإمارات.'),
 'h_stack':'تسعة تخصصات و38 خدمة','h_scope':'النطاق',
 'stats':[('1,000+','عميل منذ عام 2007'),
          ('100+','مهندس وفني ضمن الفريق'),
          ('3','دول: السعودية والإمارات والهند'),
          ('19','عاماً في أنظمة التيار الخفيف')],
 'h_disc_title':'ما نقوم بتركيبه وتشغيله وصيانته',
 'h_disc_lede':('كل تخصص أدناه ننفذه بكوادرنا: التصميم والتوريد والتركيب والتشغيل ووثائق '
                'التسليم وعقد الصيانة.'),
 'h_proj_title':'أعمال حديثة',
 'h_proj_lede':('عملاء بالاسم، ونطاق عمل محدد، والأجهزة التي تم تركيبها — مرتبطة بكتالوج '
                'المنتجات حتى تتمكن من تحديد القطع نفسها.'),
 'h_tl_title':'كيف اتسع نطاق عملنا',
 'h_tl_lede':('أضافت كل مرحلة تخصصاً ننفذه اليوم بكوادرنا، وهذا ما جعل تقديم حزمة تيار خفيف '
              'متكاملة أمراً ممكناً.'),
 'h_part_title':'الشركات المصنعة المعتمدون لتركيب أنظمتها',
 'h_part_lede':('الاعتماد يهم في المناقصات: فهو يحدد سريان الضمان، وإمكانية الوصول إلى '
                'التحديثات البرمجية، ومدى دعم المصنّع للنظام بعد التسليم.'),
 'h_ins_title':'ملاحظات تقنية',
 'h_ins_lede':'بأقلام مهندسينا، من مشاريع نفذناها فعلياً.',

 'disc':[
  ('network','البنية التحتية للشبكات',
   ['التمديدات الهيكلية','الألياف البصرية','شبكات تقنية المعلومات',
    'أنظمة الطاقة غير المنقطعة','شبكات الواي فاي','الهاتف عبر الشبكة'],
   'Cat6A · OM4 · TIA-568 · ISO/IEC 11801',
   'الطبقات السلبية والفعالة التي يصعب تعديلها لاحقاً: التمديدات والمسارات وأجهزة التبديل '
   'والشبكات اللاسلكية والاتصالات الصوتية.'),
  ('datacentre','مراكز البيانات',
   ['التصميم والتنفيذ','الترحيل','التقييم والتوصيات'],
   'المسارات · الطاقة · التبريد · DCIM',
   'من تصميم المساحة البيضاء إلى الترحيل الفعلي، بما في ذلك تقييم ما هو قائم لديكم.'),
  ('security','المراقبة والأمن',
   ['التحكم في الدخول','المراقبة بالكاميرات','إدارة المواقف','أنظمة إدارة الغرف'],
   'ONVIF · التكامل مع أنظمة الموارد البشرية والزوار',
   'من يدخل، وما الذي تم تسجيله، وكيف يرتبط الاثنان بالأنظمة التي يستخدمها فريق التشغيل لديكم.'),
  ('meeting','قاعات الاجتماعات',
   ['الاجتماعات المرئية','حجز القاعات والمكاتب','غرف العمليات والمراقبة','الصوتيات والإضاءة',
    'قاعات مجالس الإدارة'],
   'Teams Rooms · Zoom Rooms · BYOD',
   'قاعات تبدأ في وقتها: منصات موحّدة، ومعالجة صوتية، وواجهة تحكم واحدة في جميع المواقع.'),
  ('av','الأنظمة السمعية والبصرية',
   ['المسارح والقاعات','الفصول الذكية','المباني الذكية','أنظمة التحكم','الترجمة الفورية',
    'السينما المنزلية','الصوتيات الاحترافية','الساعة المركزية'],
   'AV-over-IP · Dante · أنظمة تحكم مبرمجة',
   'أكبر تخصصاتنا. قاعات المحاضرات والمسارح والفصول الدراسية، مصممة صوتياً ومبرمجة ليشغّلها '
   'موظفون غير تقنيين.'),
  ('signage','اللافتات الرقمية وشاشات العرض',
   ['اللافتات الرقمية','شاشات LED الداخلية','شاشات LED الخارجية','الشاشات التفاعلية'],
   'شاشات LED دقيقة · إدارة المحتوى',
   'شاشات LED دقيقة الخطوة ومحتوى مُدار، من شاشة واحدة في المدخل إلى شبكة لافتات على مستوى '
   'الحرم الجامعي.'),
  ('pava','النداء الآلي وإنذار الحريق',
   ['النداء والإخلاء الصوتي','النداء والإنذار العام','إنذار الحريق','الموسيقى الخلفية'],
   'EN 54-16 · EN 54-24 · كود البناء السعودي',
   'أنظمة سلامة لا مجال فيها للتهاون بالمواصفات: حسابات وضوح النطق، ومكبرات ومضخمات معتمدة، '
   'وتشغيل موثّق.'),
  ('iptv','بث الفيديو IPTV و MATV',
   ['IPTV','MATV'],
   'الضيافة · الرعاية الصحية · الحرم الجامعي',
   'توزيع البث التلفزيوني والفيديو عبر الشبكة القائمة، أو عبر الكابل المحوري حيثما كان ذلك '
   'هو المتاح في المبنى.'),
  ('professional','الصيانة والكوادر',
   ['عقود الصيانة السنوية','توفير الكوادر الدائمة'],
   'مدعومة باتفاقية مستوى خدمة · مهندسون مقيمون',
   'ما يحدث بعد التسليم: عقود بأزمنة استجابة ملزمة، ومهندسون مقيمون في المواقع التي تحتاج '
   'وجوداً دائماً.'),
 ],

 'svc_blurbs':{
  'التمديدات الهيكلية':'أنظمة نحاسية Cat6A و Cat6 بضمان مصنّع يمتد 25 عاماً، مع اختبار '
                       'وتقرير لكل وصلة.',
  'الألياف البصرية':'شبكات أساسية OM4 وأحادية النمط، ملحومة ومختبرة بجهاز OTDR مع توثيق '
                    'ميزانية الفقد.',
  'شبكات تقنية المعلومات':'التبديل والتوجيه وتقسيم الشبكات، من خزانة الطابق إلى نواة الحرم.',
  'أنظمة الطاقة غير المنقطعة':'أنظمة UPS بتحويل مزدوج مع تحديد سعة البطاريات وفق الحمل '
                              'الفعلي، وجدول الصيانة الذي يحافظ على صلاحيتها.',
  'شبكات الواي فاي':'مسوحات تنبؤية وميدانية، ثم تصميم يصمد أمام الكثافة الفعلية للأجهزة لا '
                    'أمام مخطط فارغ.',
  'الهاتف عبر الشبكة':'مقاسم IP وأجهزة، متكاملة مع الدليل ومركز الاتصال لديكم.',
  'التصميم والتنفيذ':'المساحة البيضاء والمسارات وتوزيع الطاقة والتبريد والمراقبة، كحزمة واحدة.',
  'الترحيل':'نقل الأحمال التشغيلية والمعدات الفعلية مع خطة تراجع ونافذة زمنية يوافق عليها '
            'فريق التشغيل.',
  'التقييم والتوصيات':'مراجعة مستقلة للسعة والموثوقية وتدفق الهواء، مع قائمة معالجة مسعّرة.',
  'التحكم في الدخول':'بطاقات وهوية عبر الجوال وبصمات حيوية، مع منع المرور المزدوج وإدارة '
                     'الزوار والتكامل مع الموارد البشرية.',
  'المراقبة بالكاميرات':'اختيار الكاميرات بناءً على مسافة التعرّف المطلوبة فعلياً، وسعة تخزين '
                        'محددة وفق سياسة الاحتفاظ لديكم.',
  'إدارة المواقف':'قراءة اللوحات والبوابات والإرشاد، متكاملة مع التحكم في الدخول ليعمل تصريح '
                  'واحد في كل مكان.',
  'أنظمة إدارة الغرف':'إدارة غرف الضيوف — الإضاءة والتكييف وحالة الأبواب على منصة واحدة.',
  'الاجتماعات المرئية':'قاعات معتمدة لمنصتي Teams و Zoom، بمقاس يناسب الطاولة لا الغرفة.',
  'حجز القاعات والمكاتب':'شاشات حجز وتكامل خلفي مع نظام التقويم لديكم.',
  'غرف العمليات والمراقبة':'غرف عمليات مصممة للإشغال المستمر: خطوط الرؤية وهندسة جدار '
                           'الشاشات والصوتيات والوهج.',
  'الصوتيات والإضاءة':'معالجة صوتية وتصميم إضاءة يمنحان الميكروفونات والكاميرات ما تعمل عليه.',
  'قاعات مجالس الإدارة':'قاعات تنفيذية يكون فيها كل زر في موضعه المعتاد.',
  'المسارح والقاعات':'مصفوفات صوتية وأنظمة عرض أو شاشات LED وبنية خشبة المسرح ونظام تحكم '
                     'يديره مسؤول الفعاليات بمفرده.',
  'الفصول الذكية':'شاشات وصوتيات صفية وتسجيل للمحاضرات، بمعيار موحّد قابل للتكرار على مستوى '
                  'الحرم.',
  'المباني الذكية':'التكامل بين الأنظمة السمعية والبصرية والإضاءة والتكييف والإشغال بحيث '
                   'تتوقف الأنظمة عن العمل بمعزل عن بعضها.',
  'أنظمة التحكم':'تحكم مبرمج — Crestron وما يعادله — بواجهات مصممة لمن يستخدم القاعة فعلياً.',
  'الترجمة الفورية':'كبائن وأجهزة استقبال وتوزيع للجلسات متعددة اللغات.',
  'السينما المنزلية':'صالات سينما خاصة، معايرة بالكامل.',
  'الصوتيات الاحترافية':'صوت حي وأنظمة مثبتة لدور العبادة والمنشآت الرياضية وقاعات العروض.',
  'الساعة المركزية':'توقيت موحّد على مستوى المنشأة، منضبط عبر GPS أو NTP.',
  'اللافتات الرقمية':'شاشات ومشغلات ونظام إدارة محتوى يشغّله فريق التسويق لديكم دون الرجوع إلينا.',
  'شاشات LED الداخلية':'شاشات LED داخلية دقيقة الخطوة، بمقاس يحدده مدى المشاهدة لا الميزانية '
                       'وحدها.',
  'شاشات LED الخارجية':'شاشات LED خارجية بتصنيف حماية وسطوع وتكرار يناسب مناخ الخليج.',
  'الشاشات التفاعلية':'جدران وشاشات تفاعلية تعمل باللمس لقاعات المعارض ومراكز القيادة.',
  'النداء والإخلاء الصوتي':'إخلاء صوتي وفق EN 54-16 و EN 54-24، مع نمذجة وضوح النطق وتشغيل '
                           'موثّق.',
  'النداء والإنذار العام':'إنذار عام للبيئات الصناعية ومنشآت العمليات.',
  'إنذار الحريق':'كشف وإنذار، متكامل مع أنظمة الإخلاء والتحكم في الدخول.',
  'الموسيقى الخلفية':'موسيقى خلفية مقسّمة إلى مناطق تشترك في البنية التحتية مع نظام النداء.',
  'IPTV':'بث مباشر وعند الطلب عبر الشبكة لقطاعات الضيافة والرعاية الصحية والحرم الجامعي.',
  'MATV':'توزيع تلفزيوني عبر الكابل المحوري حيث تتوفر المسارات في المبنى أصلاً.',
  'عقود الصيانة السنوية':'تغطية بأزمنة استجابة ملزمة مع زيارات وقائية مجدولة ومخزون قطع غيار.',
  'توفير الكوادر الدائمة':'مهندسون وفنيون مقيمون في موقعكم، تحت إدارتنا.',
 },

 'proj':[
  ('التعليم','الرياض','تحديث قاعة المجلس في الجامعة العربية المفتوحة',
   'أعدنا بناء قاعة المجلس حول نظام سمعي بصري متكامل واحد: توافق مع منصات الاتصال الموحّد، '
   'وعرض لاسلكي من أجهزة الحضور، ومعالجة وضوح الصوت في قاعة عالية الارتداد، وواجهة تحكم '
   'واحدة تستطيع الأمانة استخدامها فعلاً.',
   ['AV-over-IP','ميكروفونات سقفية','معالج تحكم'],
   'الجامعة العربية المفتوحة','تصميم وتوريد وتركيب وتشغيل'),
  ('التعليم','الخرج','فصول ذكية في حرم جامعة الأمير سطام',
   'تنفيذ على مستوى الحرم لشاشات التدريس وصوتيات القاعات وتسجيل المحاضرات المتوافق مع الاتصال '
   'الموحّد، مع لافتات رقمية مُدارة مركزياً تربط الفصول وقاعات الاجتماعات والمسارح في نظام '
   'محتوى واحد.',
   ['شاشات تفاعلية','صوتيات صفية','نظام إدارة اللافتات'],
   'جامعة الأمير سطام بن عبدالعزيز','تنفيذ متعدد المباني على مستوى الحرم'),
  ('حكومي','الرياض','حل سمعي بصري متكامل لمقر تقييم',
   'معيار سمعي بصري واحد مطبّق على قاعات الاجتماعات والمكاتب التنفيذية والمسرح الداخلي: شاشات '
   'ذكية وصوت موزّع ومشاركة لاسلكية وتحكم موحّد، بحيث تتصرف كل قاعة بالطريقة نفسها.',
   ['عرض لاسلكي','صوت موزّع','شاشات تجارية'],
   'تقييم','توحيد المعايير السمعية والبصرية للمقر'),
  ('التعليم','الرياض','أنظمة سمعية وبصرية لمسرح جامعي',
   'شاشة LED بدقة 4K مع توزيع كامل للصوت والصورة، وإمكانية التوصيل من أجهزة المتحدثين '
   'الزائرين، وتحكم عبر iPad يتيح للموظفين إدارة الفعاليات دون وجود فني في القاعة.',
   ['شاشة LED جدارية','مصفوفة صوتية','تحكم باللمس'],
   'الجامعة العربية المفتوحة','تجهيز مسرح'),
 ],
 'p_client':'العميل','p_scope':'النطاق','p_sector':'القطاع',

 'tl':[('2007','التأسيس في جدة','شبكات تقنية المعلومات والبنية التحتية السلبية.'),
       ('2013','مراكز البيانات','إضافة منشآت مراكز البيانات المتكاملة إلى نطاق العمل.'),
       ('2016','الأنظمة السمعية والبصرية','الدخول إلى سوق الأنظمة السمعية والبصرية والنداء الآلي.'),
       ('2020','تيار خفيف متكامل','حزم تيار خفيف كاملة في المشاريع الكبرى.'),
       ('2023','أكثر من 100 متخصص','تجاوز عدد الكوادر مئة متخصص.')],

 'a_title':'تسعة عشر عاماً من التنفيذ دون إخفاق.',
 'a_lede':('داتاكور للحلول شركة متخصصة في تكامل أنظمة التيار الخفيف. تأسست في جدة عام 2007 '
           'في مجال شبكات تقنية المعلومات والبنية التحتية السلبية، وأضافت تخصصاً جديداً كل '
           'أربع سنوات تقريباً منذ ذلك الحين.'),
 'a_story_h':'قصتنا',
 'a_story':[
  'بدأت الشركة في جدة عام 2007 بنطاق محدود: شبكات تقنية المعلومات والبنية التحتية السلبية. '
  'وهي نقطة انطلاق جيدة، لأن الطبقة السلبية هي الجزء الذي يصعب تعديله في المبنى بتكلفة معقولة '
  'بعد إغلاق الأسقف.',
  'افتتحنا في الرياض عام 2010، ودخلنا سوق مراكز البيانات عام 2013، ثم سوق الأنظمة السمعية '
  'والبصرية والنداء الآلي عام 2016. وبحلول عام 2020 كنا نتولى نطاقات التيار الخفيف كاملة '
  'كحزم متكاملة في المشاريع الكبرى، وهو أمر لا يتحقق إلا حين تكون جميع التخصصات داخل الشركة. '
  'وتجاوز عدد الكوادر مئة متخصص عام 2023.',
  'واليوم يشمل ذلك الشبكات والبنية التحتية للتمديدات والاتصال اللاسلكي بين النقاط ومراكز '
  'البيانات وأنظمة المراقبة والتحكم في الدخول والأنظمة السمعية والبصرية وشاشات LED والصوتيات '
  'الاحترافية وأنظمة النداء وإنذار الحريق — تُنفَّذ من الرياض ودبي وكوزيكود. ويقوم نجاحنا على '
  'التزام واحد: تنفيذ كل مشروع دون إخفاق.'],
 'a_vals_h':'ما نلتزم به',
 'a_vals':[
  ('الابتكار','نتبنى التقنية حين تحل مشكلة فعلية في الموقع، لا حين تظهر في خارطة طريق مصنّع.'),
  ('محورية العميل','الشخص الذي يشغّل القاعة بعد التسليم هو من يجب أن يرضيه التصميم.'),
  ('النزاهة','إذا كان النطاق لن يعمل كما هو مرسوم، نقول ذلك قبل الترسية لا بعدها.'),
  ('الأمن','تُصمَّم الأنظمة لتكون قابلة للحماية: مقسّمة ومُصرّح بها وموثّقة السجلات.'),
  ('الموثوقية','أزمنة الاستجابة التزام تعاقدي لا وعد.'),
  ('التطور','يجب أن يترك كل مشروع الفريق أقدر على تنفيذ ما يليه.')],
 'a_where_h':'أين نعمل',
 'a_where':('المقر الرئيسي في الرياض، وكيان في الإمارات بدبي باسم DCS Advanced Technologies، '
            'ومكتب هندسي في كوزيكود باسم Artifitia Solutions. وتُنفَّذ المشاريع في جميع '
            'أنحاء المملكة انطلاقاً من الرياض.'),

 'i_title':'ملاحظات تقنية',
 'i_lede':('ملاحظات من مهندسينا حول القرارات التي تتكرر في المشاريع الفعلية. بلا إعلانات '
           'عن منتجات.'),
 'posts':[
  ('3 مارس 2026','فريق الأنظمة','ما هو نظام النداء الآلي؟',
   'أين ينتهي النداء الآلي وأين يبدأ الإخلاء الصوتي، ولماذا يغيّر هذا التمييز المواصفة التي '
   'يجب أن يستوفيها مشروعك — وبالتالي ما الذي يجب أن تكون مضخماتك ومكبراتك معتمدة وفقه.'),
  ('16 فبراير 2026','فريق الشبكات','أثر الجيل الخامس على الشبكات السلبية',
   'ما الذي يفعله الانتشار الأكثف للاتصالات اللاسلكية بأعداد الألياف وأحجام المسارات '
   'والمجاري في مبنى تصممه اليوم.'),
  ('3 مارس 2026','فريق الشبكات','الشبكات الفعالة مقابل الشبكات السلبية',
   'شرح مباشر للفرق بينهما، ولماذا تكون الطبقة السلبية هي الجزء الذي لا يمكن إعادة النظر '
   'فيه لاحقاً بتكلفة معقولة.')],

 'c_title':'حدّثنا عن المشروع.',
 'c_lede':('أرسل جدول الكميات أو جدول المواد أو المخططات وسنعود إليك بنطاق مسعّر وبرنامج '
           'زمني. وإن كنت في مرحلة أبكر من ذلك، فسنقوم بزيارة ومسح للموقع.'),
 'c_form_h':'استفسار عن مشروع',
 'c_f':{'name':'الاسم','company':'الشركة','email':'البريد الإلكتروني','phone':'رقم الجوال',
        'type':'ما الذي تحتاجه؟','project':'المشروع',
        'project_hint':'المبنى، الموقع، المرحلة',
        'msg':'النطاق أو الاستفسار','send':'إرسال الاستفسار',
        'note':'نؤكد استلام كل استفسار برقم مرجعي، ونرد خلال يوم عمل واحد.'},
 'c_types':['تسعيرة لنطاق محدد','زيارة ومسح للموقع','عقد صيانة',
            'عرض سعر لمنتجات','التوظيف','أمر آخر'],
 'map_h':'موقعنا',
 'map_load':'تحميل الخريطة',
 'map_note':'تُحمَّل الخريطة من جوجل عند طلبك فقط، حتى لا تبطئ الصفحة أو تضع ملفات تعريف '
            'ارتباط قبل موافقتك.',
 'directions':'الاتجاهات',
 'follow_h':'تابعنا',
 'follow_p':'صور المشاريع وأخبار الشركة تُنشر على لينكدإن وإنستغرام.',
 'c_offices_h':'مكاتبنا',
 'c_other_h':'طرق أخرى للتواصل',
 'offices':[
  ('المملكة العربية السعودية — المقر الرئيسي','داتاكور للحلول',
   'مكتب 503، مجمع الضباب، شارع الضباب','الرياض 12626','+966 11 512 8888','+966115128888'),
  ('الإمارات العربية المتحدة','DCS Advanced Technologies L.L.C',
   'OF09-390، أم هرير الثانية','دبي','+971 52 753 6070','+971527536070'),
  ('الهند','Artifitia Solutions LLP','رقم 26، مبنى ساهيا، مدينة الحكومة السيبرانية',
   'كوزيكود، كيرالا 673016','+91 495 350 1154','+914953501154')],

 'pr_title':'المنتجات',
 'pr_lede':('أجهزة الشبكات والأمن والأنظمة السمعية والبصرية والبنية التحتية، نوردها ونركبها '
            'في جميع أنحاء المملكة. أضف ما تحتاجه إلى الطلب وسيعود فريقنا بعرض سعر يتضمن '
            'مدد التوريد.'),

 's_title':'تسعة تخصصات. ثمانٍ وثلاثون خدمة. مقاول واحد.',
 's_lede':('كل ما يلي ننفذه بكوادرنا: التصميم والتوريد والتركيب والتشغيل ووثائق التسليم وعقد '
           'الصيانة. وهذا ما يجعل تقديم حزمة تيار خفيف متكاملة أمراً ممكناً.'),
 's_all':'جميع التخصصات',

 'pj_title':'مشاريعنا',
 'pj_lede':'عملاء بالاسم، ونطاق عمل محدد، والأجهزة المركّبة. صفِّ النتائج حسب القطاع أو التخصص.',
 'pj_feat_h':'كيف نعمل في الموقع',
 'pj_feat':[('هندسة مبتكرة','قرارات تصميمية مبرَّرة بالمتطلب التشغيلي، لا بالكتالوج.'),
            ('بنية قابلة للتوسع','سعة المرحلة القادمة مصممة ضمن المرحلة الأولى.'),
            ('محورية العميل','المشغّل، لا كاتب المواصفة، هو المستخدم الذي نصمم له.'),
            ('تنفيذ متكامل','مقاول واحد من المسح حتى الصيانة.'),
            ('خدمة استباقية','اكتشاف الأعطال في الزيارات المجدولة، لا عبر بلاغات المستخدمين.')],

 'cta_h':'لديك مخططات؟ أرسلها إلينا.',
 'cta_p':('شارك جدول الكميات أو جدول المواد أو المخططات وسنعود إليك بنطاق مسعّر وبرنامج زمني. '
          'وإن كنت في مرحلة أبكر، فسنقوم بزيارة ومسح للموقع.'),
 'f_company':'الشركة','f_services':'الخدمات','f_touch':'تواصل معنا',
 'f_links':[('about','من نحن'),('projects','مشاريعنا'),('insights','مقالات تقنية')],
 'f_careers':'الوظائف','f_catalogue':'كتالوج المنتجات','f_whatsapp':'واتساب',
 'f_all_disc':'جميع التخصصات التسعة',
 'f_terms':'شروط الخدمة','f_privacy':'سياسة الخصوصية',
 'f_rights':'© 2026 داتاكور للحلول',
 'f_legal':'س.ت 0000000000 · الرقم الضريبي 300000000000003',
}
