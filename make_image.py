"""Render the world's news of Saturday 21 November 2026 as one 1024x1024
newspaper front page: assets/entry.png.

Offline renderer only. The graded entrypoint is main.py, which copies the
pre-rendered PNG into the output directory (stdlib only, no Pillow).
"""

from __future__ import annotations

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

PAPER = (247, 240, 221)
INK = (28, 28, 28)
RED = (163, 22, 33)
NAVY = (18, 32, 62)
STEEL = (47, 93, 138)
GOLD = (201, 162, 39)
LIGHT = (244, 241, 232)

SERIF_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
]
SERIF = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
]
SANS_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def _load(candidates, size):
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def serif_bold(size):
    return _load(SERIF_BOLD, size)


def serif(size):
    return _load(SERIF, size)


def sans_bold(size):
    return _load(SANS_BOLD, size)


def _tracked_centered(draw, cx, y, text, font, fill, tracking):
    total = sum(draw.textlength(ch, font=font) for ch in text)
    total += tracking * max(len(text) - 1, 0)
    x = cx - total / 2
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking


def _wrap(draw, text, font, width):
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=font) <= width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def _lines(draw, x, y, text, font, fill, width, leading):
    for line in _wrap(draw, text, font, width):
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def _rule(draw, x0, y, x1, fill=INK, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def _fit_headline(draw, text, width, start=15):
    """Shrink a headline until it fits one line, else truncate with ellipsis."""
    size = start
    while size > 11:
        font = serif_bold(size)
        if draw.textlength(text, font=font) <= width:
            return font, text
        size -= 1
    font = serif_bold(11)
    while len(text) > 4 and draw.textlength(text + "…", font=font) > width:
        text = text[:-1]
    return font, text + "…"


def _body_two_lines(draw, text, font, width, leading, x, y):
    """Draw at most two wrapped lines; truncate the second with ellipsis."""
    lines = _wrap(draw, text, font, width)
    if len(lines) > 2:
        lines = lines[:2]
        while len(lines[1]) > 4 and draw.textlength(lines[1] + "…", font=font) > width:
            lines[1] = lines[1][:-1]
        lines[1] = lines[1] + "…"
    for line in lines:
        draw.text((x, y), line, font=font, fill=INK)
        y += leading
    return y


def render(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead ----
    d.text((512, 10), "THE WORLD", font=serif_bold(72), fill=INK, anchor="ma")
    _tracked_centered(d, 512, 88, "IN ONE IMAGE", serif_bold(22), INK, 10)
    _rule(d, 36, 116, 988, INK, 3)
    _rule(d, 36, 122, 988, INK, 1)
    d.text((512, 130), "SATURDAY \u00b7 21 NOVEMBER 2026", font=serif_bold(22), fill=RED, anchor="ma")
    _rule(d, 36, 158, 988, RED, 2)

    # ---- Lead: Geneva, killer robots ----
    d.text((36, 168), "GENEVA \u2014 TOP STORY", font=sans_bold(17), fill=RED)
    hl_font, hl_text = _fit_headline(
        d, "UN states agree to draft \u2018killer robot\u2019 rules by 2028", 952, start=32)
    d.text((36, 190), hl_text, font=hl_font, fill=INK)
    y = _lines(d, 36, 228,
               "128 countries at the UN weapons convention in Geneva agreed "
               "early on Saturday to spend two years drawing up rules on AI "
               "weapons that kill without human control.",
               serif(15), INK, 952, 19)
    d.text((36, y + 4), "Only to \u2018elaborate\u2019, not negotiate \u2014 Russia blocked the binding word.",
           font=serif_bold(16), fill=RED)
    _rule(d, 36, y + 28, 988, INK, 2)
    grid_top = y + 38

    # ---- 30 more stories, 3 columns x 10 rows ----
    items = [
        ("MARKETS", "Wall Street slides into correction",
         "S&P 500 fell 3.7% on Friday and the Dow 1.9%, both now over 10% below their peaks."),
        ("RIYADH", "Houthis fire at Riyadh again",
         "Saudi air defences downed three Houthi ballistic missiles over Riyadh early on Saturday."),
        ("GAZA", "22,000 children killed in Gaza",
         "Gaza's health ministry says over 22,000 Palestinian children have been killed in the war."),
        ("GAZA", "Israeli strikes kill seven in Gaza",
         "Seven Palestinians killed, 12 wounded in Israeli attacks across Gaza despite a ceasefire."),
        ("WHITE HOUSE", "Trump defends Putin ties",
         "Trump defended his Putin ties after the Shenzhen summit; Zelensky: 'Putin is a killer.'"),
        ("TEHRAN", "Trump weighs new strikes on Iran",
         "Trump weighs new strikes on Iran as Israel presses for swift action, officials say."),
        ("BRUSSELS", "Trump: Europe must defund Ukraine",
         "Trump told European leaders to stop funding Ukraine after his Putin summit."),
        ("KYIV", "Kyiv hits Russian missile launchers",
         "Ukraine says it hit three Russian ballistic missile platforms and an air-defence system."),
        ("ULAANBAATAR", "Mongolian president resigns",
         "The president's resignation opens the way for early elections in Mongolia, officials say."),
        ("MYANMAR", "Myanmar, China reject ICJ ruling",
         "Myanmar and China protested the World Court's genocide ruling against Myanmar as unjust."),
        ("TALLINN", "Moscow: Estonia builds 'Iron Curtain'",
         "Moscow accused Estonia of erecting a new 'Iron Curtain' with border curbs and vowed to respond."),
        ("TOKYO", "Japan core inflation hits 2.2%",
         "Japan's core inflation rose to 2.2% in October, official data showed on Saturday."),
        ("TOKYO", "Japan\u2013China ties hit record low",
         "Japan was sidelined by China as ties between the two hit a record low, reports say."),
        ("MADRID", "Spain extends banking tax for housing",
         "Spain plans to extend its banking tax to fund housing policies, the prime minister said."),
        ("BERLIN", "Berlin students protest rearmament",
         "Berlin students protested against rearmament and mandatory military service in the capital."),
        ("ROME", "Italy clears Tesla self-driving",
         "Italy gave Tesla's self-driving tech conditional approval ahead of an EU-wide ruling."),
        ("BRAS\u00cdLIA", "Bolsonaro hospitalised in Bras\u00edlia",
         "Former president Jair Bolsonaro was hospitalised with an intestinal obstruction, his office said."),
        ("PORT-AU-PRINCE", "Salvadoran troops killed in Haiti",
         "Salvadoran troops in Haiti lost soldiers to explosives, officials said on Saturday."),
        ("WASHINGTON", "FBI crime database 'hacked'",
         "The FBI's crime database was hacked, CNN reported, amid a week of US outages."),
        ("CYBER", "USDA hit by cyberattack",
         "The US Agriculture Department was hit by a cyberattack; the FBI is probing it."),
        ("CAPITOL", "Senate fast-tracks energy projects",
         "The US Senate passed a bill fast-tracking energy and datacenter projects by easing green rules."),
        ("LOS ANGELES", "GTA 6 smashes $4.9bn sales record",
         "GTA 6 smashed records with nearly $4.9bn in first-day sales, reports said."),
        ("NEW YORK", "Van Gogh sells for record $190m",
         "A Van Gogh painting sold for an unprecedented $190m at auction, setting a new record."),
        ("U.S. COURTS", "Judge backs $7.25bn Roundup deal",
         "A judge endorsed a $7.25bn settlement for Roundup pesticide cancer claims."),
        ("BEIRUT", "Europe eyes UN force role in Lebanon",
         "Europeans push to replace UN peacekeepers in Lebanon as they seek a bigger Middle East role."),
        ("LAS VEGAS", "Russell takes Las Vegas pole",
         "George Russell took pole for the Las Vegas Grand Prix, 0.098s clear of Sainz; Verstappen fifth."),
        ("ANTALYA", "COP31 runs into overtime",
         "Climate talks ran past their deadline as the draft deal still omits any fossil-fuel phase-out."),
        ("FLORIDA", "Record floods swamp Florida coast",
         "Record floods swamped Florida's coast; the St. Johns River broke a 73-year record."),
        ("MUSCAT", "Two tankers hit near Hormuz",
         "Two tankers were hit by unknown projectiles near Khasab; no casualties."),
        ("KRYVYI RIH", "Two killed in Kryvyi Rih strikes",
         "Russian strikes on Kryvyi Rih killed a child and a paramedic and wounded dozens."),
    ]
    cols = 3
    margin, gut = 36, 16
    col_w = (W - 2 * margin - (cols - 1) * gut) // cols
    grid_bottom = 950
    row_h = (grid_bottom - grid_top) // 10
    for idx, (kick, head, body) in enumerate(items):
        r, c = divmod(idx, cols)
        x = margin + c * (col_w + gut)
        cy = grid_top + r * row_h
        d.text((x, cy), kick, font=sans_bold(11), fill=RED)
        hf, ht = _fit_headline(d, head, col_w, start=15)
        d.text((x, cy + 14), ht, font=hf, fill=INK)
        _body_two_lines(d, body, serif(12), col_w, 14, x, cy + 33)

    # ---- Footer ----
    _rule(d, 36, 960, 988, INK, 1)
    d.text((512, 970), "21 NOVEMBER 2026 \u00b7 31 STORIES FROM AROUND THE WORLD",
           font=serif_bold(16), fill=INK, anchor="ma")

    img.save(path, "PNG")
    return path


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "assets", "entry.png")
    render(out)
    print(out)


if __name__ == "__main__":
    main()
