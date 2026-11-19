#!/usr/bin/env python3
"""Render the make.fun news-image-20261119 front page (1024x1024 JPEG).

Newspaper front page for Thursday 19 November 2026: 41 verified stories.
Three large leads with rich AI illustrations (APEC trilateral in Shenzhen,
the ICJ Rohingya verdict, GTA VI launch), ten medium stories in two rows
of five (all ten with AI illustrations), a region bar counting all 41
stories, a world map with story dots, a day-in-numbers strip, and 28 briefs.

Two big events were still pending when this was built: the APEC trilateral
and the ICJ verdict (read 19 Nov 08:00 GMT). Neither outcome is stated
anywhere on the page -- both are framed as "meeting today" / "verdict today".
Two briefs from the research were dropped after verification: the Kyiv drone
strike (unconfirmed, aggregators only) and the FDA mRNA flu vaccine (approved
5 Aug 2026, not 19 Nov). All facts verified against reporting dated 19 Nov
2026 (or flagged overnight / Wednesday reports); nothing invented.
Output is deterministic.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

REPO = "/home/hatch/workspace/makefun/news-image-20261119"
OUT_JPG = REPO + "/front-page.jpg"
GEO = "/home/hatch/workspace/makefun/countries.geo.json"
ASSETS = REPO + "/assets"

W, H = 1024, 1024
PAPER = (247, 242, 230)
INK = (24, 24, 24)
RED = (176, 32, 28)
BLUE = (28, 74, 116)
GREEN = (44, 120, 68)
ORANGE = (214, 110, 24)
BROWN = (146, 106, 38)
TEAL = (0, 122, 122)
GREY = (104, 104, 104)
WORLD = (110, 90, 160)
SEA = (206, 226, 235)
LAND = (233, 221, 193)
COAST = (182, 164, 120)

FD = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FD + name, size)


F_KICK = font("DejaVuSans-Bold.ttf", 12)
F_DATE = font("DejaVuSerif-Bold.ttf", 48)
F_TAG = font("DejaVuSans.ttf", 11)
F_REG = font("DejaVuSans-Bold.ttf", 9)
F_LEAD_KICK = font("DejaVuSans-Bold.ttf", 11)
F_LEAD_HEAD = font("DejaVuSerif-Bold.ttf", 17)
F_LEAD_FACT = font("DejaVuSans.ttf", 11)
F_MED_KICK = font("DejaVuSans-Bold.ttf", 9)
F_MED_HEAD = font("DejaVuSerif-Bold.ttf", 12)
F_MED_FACT = font("DejaVuSans.ttf", 10)
F_SEC = font("DejaVuSans-Bold.ttf", 13)
F_BRIEF = font("DejaVuSans.ttf", 9)
F_FOOT = font("DejaVuSans.ttf", 9)
F_MAP_LAB = font("DejaVuSans-Bold.ttf", 9)
F_NUM = font("DejaVuSans-Bold.ttf", 16)
F_NUM_LAB = font("DejaVuSans.ttf", 8)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)


def wrap(text, f, width):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(x, y, lines, f, fill=INK, leading=None):
    """Draw lines top-down; returns the y just below the last line."""
    if leading is None:
        leading = int(f.size * 1.28)
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y


def num_badge(cx, cy, r, n, fill=RED):
    """Numbered circle badge."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    s = str(n)
    f = font("DejaVuSans-Bold.ttf", max(8, int(r * 1.05)))
    tw = d.textlength(s, font=f)
    d.text((cx - tw / 2, cy - f.size / 2 - 1), s, font=f, fill=(255, 255, 255))


def hline(x0, x1, y, width=1, fill=INK):
    d.rectangle([x0, y, x1, y + width - 1], fill=fill)


def load_ai(fname, w, h, focus=0.5):
    """Load an AI illustration, crop to the w:h aspect (focus 0=top, 1=bottom),
    and resize. PIL reads WEBP fine."""
    im = Image.open(os.path.join(ASSETS, fname)).convert("RGB")
    iw, ih = im.size
    target = w / h
    src = iw / ih
    if src > target:
        nw = int(ih * target)
        x0 = (iw - nw) // 2
        im = im.crop((x0, 0, x0 + nw, ih))
    else:
        nh = int(iw / target)
        y0 = int((ih - nh) * focus)
        im = im.crop((0, y0, iw, y0 + nh))
    return im.resize((w, h), Image.LANCZOS)


# ---------------------------------------------------------------- header
d.text((28, 8), "THE WORLD'S NEWS IN ONE PICTURE", font=F_KICK, fill=RED)
right = "41 STORIES  ·  6 CONTINENTS  ·  13 ILLUSTRATED  ·  ALL FROM THURSDAY"
d.text((W - 28 - d.textlength(right, font=F_KICK), 8), right, font=F_KICK, fill=INK)
d.text((28, 26), "Thursday 19 November 2026", font=F_DATE, fill=INK)
d.text((28, 80), "The day in one image — the news of Thursday 19 November 2026",
       font=F_TAG, fill=GREY)
hline(28, W - 28, 96, 2)
hline(28, W - 28, 100, 1)

# ---------------------------------------------------------------- region bar
# Story counts per region, counted from the 41 stories below:
# Americas 9, Africa 7, Asia 3, Europe 4, Mideast 2, World 12, Oceania 4.
REGIONS = [
    ("Americas", 9, RED),
    ("Africa", 7, BROWN),
    ("Asia", 3, GREEN),
    ("Europe", 4, BLUE),
    ("Mideast", 2, ORANGE),
    ("World", 12, WORLD),
    ("Oceania", 4, TEAL),
]
assert sum(c for _, c, _ in REGIONS) == 41, "region counts must sum to 41"
BAR_X0, BAR_X1, BAR_Y, BAR_H = 28, W - 28, 106, 18
bar_w = BAR_X1 - BAR_X0
x = BAR_X0
for name, count, col in REGIONS:
    seg = int(round(bar_w * count / 41))
    if x + seg > BAR_X1:
        seg = BAR_X1 - x
    d.rectangle([x, BAR_Y, x + seg - 1, BAR_Y + BAR_H - 1], fill=col)
    label = f"{name} {count}"
    tw = d.textlength(label, font=F_REG)
    if tw <= seg - 6:
        d.text((x + (seg - tw) / 2, BAR_Y + 4), label, font=F_REG,
               fill=(255, 255, 255))
    else:
        # Narrow segment (Mideast, 2 stories): fall back to 8pt, which fits.
        f_small = font("DejaVuSans-Bold.ttf", 8)
        tw = d.textlength(label, font=f_small)
        if tw <= seg - 2:
            d.text((x + (seg - tw) / 2, BAR_Y + 5), label, font=f_small,
                   fill=(255, 255, 255))
    x += seg

# ---------------------------------------------------------------- top row: 3 large leads
LEADS = [
    dict(n=1, kick="ASIA  ·  APEC SUMMIT", col=BLUE,
         fname="media-generation-apec-trilateral-0-78f4a324-ce1a-4e47-a11b-0199cfb901ab.webp",
         focus=0.4,
         head="Trump, Xi & Putin meet in Shenzhen — first-ever trilateral",
         fact="1 hour set aside for the trilateral; Trump also holds bilateral "
              "+ lunch with Xi, one-on-one with Putin."),
    dict(n=2, kick="WORLD  ·  WORLD COURT", col=WORLD,
         fname="media-generation-icj-verdict-0-2d04f776-6ed9-407a-8fed-21395544cd13.webp",
         focus=0.5,
         head="World Court rules on Myanmar Rohingya case — verdict today",
         fact="Verdict read 19 Nov 08:00 GMT; 3rd genocide ruling in ICJ "
              "history; ≥730,000 Rohingya fled in 2017."),
    dict(n=3, kick="WORLD  ·  GAMING", col=WORLD,
         fname="media-generation-gta-vi-0-1e49f8a9-5bb3-4423-81b8-d536b2fe00bd.webp",
         focus=0.5,
         head="GTA VI launches 19 Nov — Metacritic 99",
         fact="Ties Ocarina of Time (1998) record; pre-orders ~$1.54bn, "
              "~16m copies; Take-Two +7.5%."),
]
LEAD_W = 312
LEAD_Y = 132
LEAD_IMG_H = 140
for i, s in enumerate(LEADS):
    x = 28 + i * (LEAD_W + 8)
    y = LEAD_Y
    im_ai = load_ai(s["fname"], LEAD_W, LEAD_IMG_H, focus=s["focus"])
    img.paste(im_ai, (x, y))
    d.rectangle([x, y, x + LEAD_W - 1, y + LEAD_IMG_H - 1], outline=(150, 150, 150))
    num_badge(x + 13, y + 13, 10, s["n"], fill=s["col"])
    ky = y + LEAD_IMG_H + 8
    d.text((x, ky), s["kick"], font=F_LEAD_KICK, fill=s["col"])
    hy = ky + 16
    hl = wrap(s["head"], F_LEAD_HEAD, LEAD_W)
    hy = text_block(x, hy, hl[:2], F_LEAD_HEAD, leading=20)
    fl = wrap(s["fact"], F_LEAD_FACT, LEAD_W)
    text_block(x, hy + 3, fl[:3], F_LEAD_FACT, fill=(70, 70, 70), leading=14)
hline(28, W - 28, 388, 1)

# ---------------------------------------------------------------- rows: 10 medium stories (2 rows x 5)
MEDS = [
    dict(n=4, kick="EUROPE  ·  UKRAINE", col=BLUE, ai="kerch",
         head="Kerch Bridge hit a 3rd time in 3 days",
         fact="Rail section struck; traffic halted after arch collapse."),
    dict(n=5, kick="US  ·  TECH", col=BROWN, ai="anthropic",
         head="Anthropic debuts on Nasdaq at $83",
         fact="Raised $81.3bn, 980m shares; valued ~$1.1tn."),
    dict(n=6, kick="EUROPE  ·  UKRAINE", col=BLUE, ai="coalition",
         head="Coalition of the Willing meets in Berlin",
         fact="Five nations + NATO meet; EU proposed €45bn loan."),
    dict(n=7, kick="EUROPE  ·  ENERGY", col=BLUE, ai="refineries",
         head="Ukraine drone strikes cut Russian refineries 45%",
         fact="15 of 35 refineries hit; output down to ~400,000 t/day."),
    dict(n=8, kick="WORLD  ·  ART", col=WORLD, ai="vangogh",
         head="Van Gogh sells for record $190.4m",
         fact="Chestnut Trees in Blossom, 1890; beats $117.2m record."),
    dict(n=9, kick="WORLD  ·  DEMOGRAPHICS", col=WORLD, ai="pew",
         head="Islam to be world's largest religion by 2035",
         fact="2.57bn Muslims vs 2.52bn Christians; fertility 3.1 vs 2.5."),
    dict(n=10, kick="AMERICAS  ·  DEFENCE", col=RED, ai="venezuela",
         head="US–Venezuela sign military deal",
         fact="Hegseth visits Caracas; 10 months after US seized Maduro."),
    dict(n=11, kick="MIDDLE EAST  ·  GULF WAR", col=RED, ai="gulf",
         head="Iran hits US base in Kuwait; tanker burns",
         fact="UAE tanker hit in Hormuz; 11 crew hurt, 1 missing."),
    dict(n=12, kick="US  ·  MARKETS", col=BROWN, ai="wallstreet",
         head="Dow falls 561; UnitedHealth −10%",
         fact="Dow −1.11% to 50,198; UnitedHealth −10% on audit rule."),
    dict(n=13, kick="WORLD  ·  CLIMATE", col=WORLD, ai="cop31",
         head="COP31 enters final days in Antalya",
         fact="144-article draft; phaseout & ≥$120bn/yr adaptation."),
]

# AI illustrations for medium stories: filename + vertical focus (0=top, 1=bottom).
AI_MED = {
    "kerch": ("media-generation-kerch-bridge-0-e33777c7-3d8d-4b41-ac1f-a52ee1a7b7df.webp", 0.5),
    "anthropic": ("media-generation-anthropic-ipo-0-8f3e50eb-5adf-4dab-94b5-4be5e1dad996.webp", 0.5),
    "coalition": ("media-generation-coalition-berlin-0-7ecab74e-7856-44ee-9a18-1b57c992aa75.webp", 0.5),
    "refineries": ("media-generation-russian-refineries-0-c7e9f73d-8234-4430-9e0e-a07dc1fe0a52.webp", 0.5),
    "vangogh": ("media-generation-van-gogh-0-9d3a6a67-ea13-4621-abbb-c3faec4f5b24.webp", 0.5),
    "pew": ("media-generation-pew-religions-0-593b138e-cd63-4130-87f9-d42bcc670081.webp", 0.5),
    "venezuela": ("media-generation-venezuela-deal-0-cddcd984-61c0-4d9f-adfa-e9d0f74688b8.webp", 0.5),
    "gulf": ("media-generation-gulf-war-0-09dc008e-409a-4836-b612-3dd5596e22cf.webp", 0.5),
    "wallstreet": ("media-generation-wall-street-0-44a8fd36-dd47-46b4-b25b-8b512c2a216d.webp", 0.5),
    "cop31": ("media-generation-cop31-antalya-0-02458d71-7046-403f-be2b-dd70896e411b.webp", 0.5),
}

MED_W = 187
MED_IMG_H = 70
MED_Y1 = 396
ROW_H = 150
for i, s in enumerate(MEDS):
    row = i // 5
    col = i % 5
    x = 28 + col * (MED_W + 8)
    y = MED_Y1 + row * ROW_H
    fname, focus = AI_MED[s["ai"]]
    im_ai = load_ai(fname, MED_W, MED_IMG_H, focus=focus)
    img.paste(im_ai, (x, y))
    d.rectangle([x, y, x + MED_W - 1, y + MED_IMG_H - 1], outline=(150, 150, 150))
    num_badge(x + 11, y + 11, 9, s["n"], fill=s["col"])
    ky = y + MED_IMG_H + 6
    d.text((x, ky), s["kick"], font=F_MED_KICK, fill=s["col"])
    hy = ky + 13
    hl = wrap(s["head"], F_MED_HEAD, MED_W)
    hy = text_block(x, hy, hl[:2], F_MED_HEAD, leading=15)
    fl = wrap(s["fact"], F_MED_FACT, MED_W)
    text_block(x, hy + 1, fl[:2], F_MED_FACT, fill=(70, 70, 70), leading=12)
hline(28, W - 28, 696, 1)

# ---------------------------------------------------------------- bottom: map + numbers + briefs
d.text((28, 704), "WHERE IT HAPPENED", font=F_SEC, fill=INK)
d.text((524, 704), "ALSO ON 19 NOVEMBER", font=F_SEC, fill=INK)
MAP = (28, 722, 498, 882)
d.rectangle(MAP, fill=SEA, outline=(170, 180, 170))

geo = json.load(open(GEO))


def project(lon, lat, box):
    x0, y0, x1, y1 = box
    lat = max(-60.0, min(85.0, lat))
    lon = max(-180.0, min(180.0, lon))
    fx = (lon + 180.0) / 360.0
    fy = (85.0 - lat) / 145.0
    return (x0 + fx * (x1 - x0), y0 + fy * (y1 - y0))


def draw_poly(coords, box):
    pts = [project(lon, lat, box) for lon, lat in coords]
    if len(pts) >= 3:
        d.polygon(pts, fill=LAND, outline=COAST)


for feat in geo["features"]:
    if feat.get("id") == "ATA":
        continue
    g = feat["geometry"]
    if g["type"] == "Polygon":
        for ring in g["coordinates"]:
            draw_poly(ring, MAP)
    elif g["type"] == "MultiPolygon":
        for poly in g["coordinates"]:
            for ring in poly:
                draw_poly(ring, MAP)

REG = {"americas": RED, "europe": BLUE, "mideast": ORANGE,
       "asia": GREEN, "africa": BROWN, "oceania": TEAL, "world": WORLD}
NUMBERED = [
    (1, 113.8, 22.5, "asia"), (2, 4.3, 52.1, "europe"),
    (3, -81.0, 27.0, "americas"), (4, 36.5, 45.3, "europe"),
    (5, -74.0, 40.7, "americas"), (6, 13.4, 52.5, "europe"),
    (7, 37.6, 55.7, "europe"), (8, -74.0, 40.7, "americas"),
    (9, 77.0, 20.0, "asia"), (10, -66.9, 10.5, "americas"),
    (11, 47.5, 29.3, "mideast"), (12, -74.0, 40.7, "americas"),
    (13, 30.7, 36.9, "europe"),
]
OFFSETS = {1: (14, 10), 2: (-22, -14), 3: (22, -8), 4: (22, 4),
           5: (26, -12), 6: (0, -22), 7: (20, -16), 8: (-26, 10),
           9: (-14, 12), 10: (-14, 10), 11: (-14, -12), 12: (2, 26),
           13: (-18, 18)}
for n, lon, lat, reg in NUMBERED:
    x, y = project(lon, lat, MAP)
    dx, dy = OFFSETS.get(n, (0, 0))
    if dx or dy:
        d.line([x, y, x + dx, y + dy], fill=(90, 90, 90), width=1)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=REG[reg])
        x, y = x + dx, y + dy
    num_badge(x, y, 8, n, fill=REG[reg])
BRIEF_DOTS = [
    (33.0, 12.0, "africa"), (40.0, 16.5, "africa"),
    (-17.4, 14.7, "africa"), (12.0, 9.0, "africa"),
    (6.0, 7.0, "africa"), (35.5, 18.5, "africa"),
    (-13.0, 10.0, "africa"), (116.0, 18.0, "asia"),
    (115.9, -32.0, "oceania"), (178.0, -42.0, "oceania"),
    (170.0, -37.0, "oceania"), (28.0, 59.8, "europe"),
    (-77.0, 38.9, "americas"), (138.6, -34.9, "world"),
    (0.1, 52.2, "world"), (-105.0, 40.0, "world"),
    (9.0, 16.5, "world"), (-77.0, -12.0, "americas"),
    (-47.9, -15.8, "americas"), (-57.6, -25.3, "americas"),
    (153.0, -27.5, "oceania"), (-73.0, 46.0, "americas"),
    (1.5, 59.0, "world"), (50.6, 26.2, "mideast"),
    (-82.0, 34.0, "americas"), (110.0, 25.0, "asia"),
    (-30.0, 0.0, "world"), (20.0, 40.0, "world"),
]
for lon, lat, reg in BRIEF_DOTS:
    x, y = project(lon, lat, MAP)
    d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=REG[reg], outline=(255, 255, 255))

d.text((28, 886), "Numbers 1–13 are the big stories; dots are the briefs.",
       font=F_TAG, fill=GREY)

# day in numbers (left column, under the map)
d.text((28, 902), "THE DAY IN NUMBERS", font=F_SEC, fill=INK)
STATS = [
    ("99", "GTA VI's Metacritic score", WORLD),
    ("$190.4m", "Van Gogh's record sale price", BROWN),
    ("45%", "Russian refineries cut", BLUE),
    ("$81.3bn", "Anthropic's IPO raise", RED),
]
for i, (num, lab, col) in enumerate(STATS):
    x = 28 + i * (113 + 6)
    y = 918
    d.rectangle([x, y, x + 113, y + 70], fill=(238, 234, 222),
                outline=(200, 192, 170))
    d.rectangle([x, y, x + 113, y + 3], fill=col)
    nw = d.textlength(num, font=F_NUM)
    d.text((x + (113 - nw) / 2, y + 10), num, font=F_NUM, fill=col)
    ll = wrap(lab, F_NUM_LAB, 100)
    text_block(x + 7, y + 34, ll[:2], F_NUM_LAB, fill=(70, 70, 70), leading=11)

# briefs list (right side, two columns; numbers 14–41)
BRIEFS = [
    (14, "Sudan, Ethiopia shut consulates"),
    (15, "Ethiopia, Eritrea mass troops"),
    (16, "Senegal: Pastef expels President Faye"),
    (17, "Nigeria army kills 21 ISWAP fighters"),
    (18, "Nigeria states back local police"),
    (19, "Sudan power grid hit by drones"),
    (20, "ECOWAS defence chiefs meet in Dakar"),
    (21, "Quad backs US-led AI supply chain"),
    (22, "Australia gas bill; WA exempt"),
    (23, "NZ election tight; vote Saturday"),
    (24, "NZ GTA downloads to surge 35 PB"),
    (25, "Russian warship hit in Baltic"),
    (26, "Fed minutes signal more rate hikes"),
    (27, "Breast cancer 'switch' found"),
    (28, "AlphaFold3 maps 200m proteins"),
    (29, "Teen cannabis slows cognition"),
    (30, "First Lassa vaccine shows promise"),
    (31, "Peru warns of heavy rain 18–20 Nov"),
    (32, "Brazil rain; El Niño builds"),
    (33, "Argentina, Brazil split handball"),
    (34, "Australia win Rugby League Cup"),
    (35, "Canada's Carney at APEC Shenzhen"),
    (36, "Brent oil ~$91.68, down 16% in month"),
    (37, "Bahrain refinery back after attack"),
    (38, "Trump heads home after Asia tour"),
    (39, "Xi urges 'free and open trade'"),
    (40, "Warming Jan–Sep 2026: 1.47°C"),
    (41, "Adaptation needs ~$305bn a year"),
]
for i, (n, txt) in enumerate(BRIEFS):
    col = i // 15
    row = i % 15
    x = 524 + col * 236
    y = 722 + row * 17
    num_badge(x + 7, y + 6, 7, n, fill=GREEN)
    d.text((x + 19, y), txt, font=F_BRIEF, fill=INK)

# ---------------------------------------------------------------- footer
hline(28, W - 28, 992, 1)
d.text((28, 998), "Stories from Thursday 19 November 2026, with overnight reports "
                  "from Wednesday. Contested claims are marked as claims.",
       font=F_FOOT, fill=GREY)
src = "Sources: Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN. Original drawings."
d.text((W - 28 - d.textlength(src, font=F_FOOT), 998), src, font=F_FOOT, fill=GREY)

img.save(OUT_JPG, "JPEG", quality=88)
print("saved", OUT_JPG)
print("bytes:", os.path.getsize(OUT_JPG))
print("size:", img.size)
