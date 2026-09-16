# -*- coding: utf-8 -*-
"""Generate branded topic thumbnails for the insight articles (the ones whose
img is dc-insight-<slug>.webp). Clean, on-brand: dark charcoal ground, a teal
glow, a category eyebrow + the article title in Texta. 1122x612 (2x of 561x306)."""
import os, json, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
IMGDIR = os.path.join(ROOT, "assets1", "images")
FONTS = os.path.join(ROOT, "fonts")
INS = json.load(open(os.path.join(HERE, "insights.json"), encoding="utf-8"))

W, H = 1122, 612
INK = (18, 20, 26)          # #12141a charcoal ground
TEAL = (0, 179, 166)        # #00b3a6 brand teal
TEAL_T = (51, 195, 181)     # #33c3b5 text teal
WHITE = (238, 240, 240)

# slug -> category eyebrow
CAT = {
  "choosing-an-elv-contractor-saudi-arabia": "Buyer's guide",
  "structured-cabling-standards-explained": "Network infrastructure",
  "data-centre-design-essentials": "Data centre",
  "single-mode-vs-multimode-fibre": "Network infrastructure",
  "wifi-site-survey-guide": "Network infrastructure",
  "designing-cctv-for-coverage": "Surveillance & security",
  "access-control-credentials-compared": "Surveillance & security",
  "voice-evacuation-en54-sbc801": "Life safety",
  "hybrid-meeting-room-av": "Audio-visual",
  "led-video-wall-pixel-pitch": "Digital signage",
  "smart-building-elv-convergence": "Smart buildings",
  "control-room-soc-noc-design": "Audio-visual",
  "iptv-for-enterprise-hospitality": "IPTV",
  "digital-signage-that-works": "Digital signage",
  "why-annual-maintenance-contracts-matter": "Support & AMC",
  "what-are-elv-low-current-systems": "ELV explained",
}

def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

def teal_glow():
    """a soft teal radial glow, bottom-left."""
    g = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(g)
    cx, cy, r = 120, H + 40, 520
    for i in range(r, 0, -6):
        a = int(150 * (1 - i / r))
        gd.ellipse([cx - i, cy - i, cx + i, cy + i], fill=a)
    g = g.filter(ImageFilter.GaussianBlur(40))
    layer = Image.new("RGB", (W, H), TEAL)
    out = Image.new("RGB", (W, H), INK)
    out.paste(layer, (0, 0), g)
    return out

def dot_grid(img):
    """faint dot grid, top-right quadrant, for texture."""
    d = ImageDraw.Draw(img, "RGBA")
    for y in range(60, 300, 34):
        for x in range(W - 420, W - 40, 34):
            d.ellipse([x, y, x + 3, y + 3], fill=(255, 255, 255, 18))
    return img

def make(slug, title, cat):
    img = teal_glow()
    img = dot_grid(img)
    d = ImageDraw.Draw(img)
    # eyebrow
    eb = font("TextaBold.ttf", 26)
    d.text((64, 92), cat.upper(), font=eb, fill=TEAL_T)
    # title, wrapped
    tf = font("TextaHeavy.ttf", 62)
    lines = textwrap.wrap(title, width=22)[:4]
    y = 150
    for ln in lines:
        d.text((64, y), ln, font=tf, fill=WHITE)
        y += 74
    # teal underline
    d.rectangle([66, y + 14, 66 + 96, y + 20], fill=TEAL)
    # footer wordmark
    wf = font("TextaMedium.ttf", 26)
    d.text((64, H - 60), "Datacore  ", font=wf, fill=(150, 160, 165))
    wmw = d.textlength("Datacore  ", font=wf)
    d.text((64 + wmw, H - 60), "Insights", font=wf, fill=TEAL_T)
    out = os.path.join(IMGDIR, "dc-insight-" + slug + ".webp")
    img.save(out, "WEBP", quality=88, method=6)
    return out

n = 0
for p in INS["en"]["posts"]:
    if str(p.get("img", "")).startswith("dc-insight-"):
        cat = CAT.get(p["slug"], "Datacore Insights")
        make(p["slug"], p["title"], cat)
        n += 1
print("generated", n, "insight thumbnails")
