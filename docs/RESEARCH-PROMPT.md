# Prompt to paste into the browsing-enabled Claude session

Copy everything between the lines. Attach nothing — it is self-contained.

Ask it to give you the result **as a downloadable file**, then upload that file
back into the build session.

---

You have web access. I need you to act as a research assistant gathering source
material for a website rebuild. Do not design anything, do not write any code,
and do not give me opinions on the site — another session is handling that. Your
only job is to collect material accurately and hand it back in one file.

**Company:** Datacore Solutions — a low-current / ELV systems integrator
headquartered in Riyadh, with entities in Dubai (DCS Advanced Technologies
L.L.C) and Kozhikode, India (Artifitia Solutions LLP). Founded Jeddah 2007.
Site: https://www.datacore.com.sa — it serves English at `?lang=en` and Arabic
at `?lang=ar` on every URL.

Work through the six tasks below. If something 404s or is blocked, say so
explicitly in the output rather than guessing or filling the gap from general
knowledge. **Never invent content.** If a page has no text where you expected
text, write `[EMPTY]`.

## Task 1 — Service detail pages (highest priority)

Fetch all 38 of these at `https://www.datacore.com.sa/service-details/<slug>`
and copy the **full body copy verbatim**, not a summary. I need the real
marketing text, headings, any bullet lists, and any named standards, brands or
specifications mentioned.

```
structured-cabling-solutions          fiber-optic-solutions
it-network-solutions                  ups-systems
wifi-solutions                        ip-telephony-solutions
data-center-design-amp-implementation-services
data-centre-migration-services-       data-centre-assessment-amp-recommendations
access-control-solutions              video-surveillance-solutions-amp-cctv
parking-management-system             grms-solutions-
video-conference-solution             room-amp-desk-booking-system
soc-noc-room-solution                 acoustic-amp-lighting-solutions
smart-meeting-room-amp-boardroom-solution
auditorium                            smart-class-rooms
smart-building-solutions              control-system
interpreter-system                    home-cinema-solution
professional-audio                    master-clock-system
digital-signage-solutions             indoor-led-video-wall
outdoor-led-video-wall                interactive-video-walls-tiles
pava-public-address-amp-voice-evacuation-system
paga-public-address-and-general-alarm-system
fire-alarm-systems                    bgm-background-music-system
iptv-solution                         matv-solution
annual-maintenance-contracts          full-time-staffing-solution
```

For each, also record the `<title>` and `<meta name="description">`.

## Task 2 — Arabic source text

This is important and easy to skip. For each of these, fetch the `?lang=ar`
version and copy the **existing Arabic verbatim**:

- `/` , `/about-us` , `/services` , `/project` , `/contact-us` , `/blog`
- the 38 service-detail slugs above

I am writing new Arabic and need to match the company's established
terminology — specifically how they render "low current", "public address",
"voice evacuation", "structured cabling" and the nine discipline names. Give me
their exact wording, even where it looks wrong or machine-translated. Flag
anything that is obviously machine-translated or where the Arabic page falls
back to English.

## Task 3 — Image inventory

I need to know what photography already exists. For every page you visit, list
every content image (ignore icons, logos and decorative SVGs) as:

| Page | Full image URL | Alt text | Apparent subject |

Their media paths are `/imgserver/uploads/attachments/` and
`/imgserver/uploads/compressed/`. Flag any image that appears to be a
placeholder (filenames like `01.png`–`05.png`) versus a real photograph, and
flag any that look like genuine photographs of Datacore's own installations as
opposed to stock imagery.

## Task 4 — Remaining pages

Copy verbatim:
- `/project` and all project detail pages under `/projects/<slug>` — start from
  `smart-modernization-of-aou-council-room`, `smart-classrooms-for-psau-campus`,
  `comprehensive-av-solution-for-taqeem-hq`,
  `auditorium-av-solution-for-university`, and use the page's filters/search to
  find any others not listed on page one
- `/blog` and every post under `/blogs/<slug>` — full article text
- `/career` and `/careers/site-supervisor`
- `/terms-service` and `/privacy-policy` — full text

## Task 5 — Technical facts

- Does `https://www.datacore.com.sa/sitemap.xml` exist? If so, list every URL in
  it — this is the fastest way to catch pages the list above misses.
- Contents of `/robots.txt`.
- Does `datacore.com.sa` redirect to `www.datacore.com.sa` or the reverse?
- Are the Commercial Registration (CR) number or VAT number published anywhere
  on the site or in `/assets1/images/DC COMPANY PROFILE.pdf`? Quote them exactly
  if found. If not found, say so — do not guess.
- Any ISO certifications, manufacturer partner tiers, or Saudi/Gulf compliance
  claims stated anywhere on the site. Quote them verbatim.

## Task 6 — Social accounts

- https://www.linkedin.com/company/datacore-solutions
- https://www.instagram.com/datacore_sa/
- https://www.facebook.com/www.datacore.com.sa/

For each: follower count, posting frequency over the last twelve months, and
the ten most recent posts (date, caption text, and what the image shows).
I specifically want to identify **posts containing photographs of Datacore's own
completed installations**, with the direct image URL where you can get it.

If these are blocked to automated access, say so plainly — do not substitute
guesses or general knowledge about the company.

## Output format

One markdown file, `datacore-research.md`, using this structure. Create it as an
actual downloadable file, not just chat text.

```
# Datacore — research pass 2

## 0. Coverage report
[What you successfully fetched, what failed, what was blocked. Be specific.]

## 1. Service detail pages
### <slug>
**URL:** …
**Title:** …
**Meta description:** …
**English copy:**
[verbatim]
**Arabic copy:**
[verbatim, or NOT AVAILABLE]

## 2. Project detail pages
[same pattern]

## 3. Blog posts
[same pattern]

## 4. Careers / Terms / Privacy
[same pattern]

## 5. Image inventory
[the table]

## 6. Technical facts
[sitemap URLs, robots.txt, canonical host, CR/VAT, certifications]

## 7. Social accounts
[per platform, with the ten recent posts and any installation photo URLs]
```

Two rules for the whole job. **Verbatim means verbatim** — do not tidy,
shorten or rewrite the company's copy, because I am comparing it against a
rewrite and need the original. And **mark every gap explicitly** rather than
leaving it silent, because a missing section reads as "this page had no content"
and that will end up as a wrong decision downstream.

---

## After you get the file

Upload `datacore-research.md` back into the build session. Then, separately,
gather the actual photographs — which the browsing session cannot hand over as
files:

1. **Ask your PMs for the handover photo sets** for AOU council room, PSAU
   classrooms, TAQEEM HQ and the university auditorium. These are worth more
   than everything else on this page combined. Wide shots of the finished room,
   plus one detail shot of a rack or a control interface.
2. **Pull the best images off your own Instagram and Facebook** — you have
   access to the originals, which will be higher resolution than what is
   published.
3. **Product photography** for the catalogue comes from manufacturer partner
   portals (Crestron, Extron, Shure, Bosch, Hikvision, Axis and so on), not from
   manual searching. At 1,000+ SKUs that is the only workable route, and the
   images are licensed for partner use.
4. **Client consent** — confirm AOU, PSAU and TAQEEM permit both the naming and
   the photographs before anything is published.

Upload whatever you gather here and I will size, compress, lazy-load and caption
them into the build.
