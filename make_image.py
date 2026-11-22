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


def _lines(draw, x, y, text, font, fill, width, leading, max_lines=None):
    lines = _wrap(draw, text, font, width)
    if max_lines is not None and len(lines) > max_lines:
        raise ValueError("lead body needs %d lines (max %d)" % (len(lines), max_lines))
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def _rule(draw, x0, y, x1, fill=INK, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def _fit_headline(draw, text, width, start=15):
    """Shrink a headline until it fits one line; never truncate or ellipsis."""
    size = start
    while size >= 11:
        font = serif_bold(size)
        if draw.textlength(text, font=font) <= width:
            return font, text
        size -= 1
    raise ValueError("headline does not fit: %r" % (text,))


def _body_block(draw, text, font, width, leading, x, y, max_lines):
    """Draw the wrapped body, at most max_lines; raise if it needs more.

    No truncation, no ellipsis: a body that does not fit is an error.
    Returns the lowest pixel reached (bottom of the last line).
    """
    lines = _wrap(draw, text, font, width)
    if len(lines) > max_lines:
        raise ValueError("body needs %d lines (max %d): %r"
                         % (len(lines), max_lines, text))
    bottom = y
    for line in lines:
        draw.text((x, y), line, font=font, fill=INK)
        bottom = max(bottom, draw.textbbox((x, y), line, font=font)[3])
        y += leading
    return bottom


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
               "at 04:45 on Saturday, after five days of talks, to spend two "
               "years drawing up rules on AI weapons that kill without human "
               "control. Only \u2018elaborate\u2019, not \u2018negotiate\u2019 \u2014 Russia "
               "blocked the binding word, while the US, Russia and Israel "
               "oppose binding rules.",
               serif(15), INK, 952, 19, max_lines=4)
    d.text((36, y + 4), "Thirteen years of talks; UN chief Guterres set a 2026 deadline \u2014 campaigners call it watered down.",
           font=serif_bold(16), fill=RED)
    _rule(d, 36, y + 28, 988, INK, 2)
    grid_top = y + 38

    # ---- 24 more stories, 3 columns x 8 rows ----
    items = [
        ("MARKETS", "Wall Street slides into correction",
         "The S&P 500 fell 3.7% to 6,910, its seventh straight drop; the Dow lost 1.9% and the Nasdaq 5.3%, erasing its 2026 gains. A flat Anthropic IPO and a reported Nvidia accounting probe drove the sell-off."),
        ("RIYADH", "Houthis fire at Riyadh again",
         "Saudi defences downed three Houthi ballistic missiles over Riyadh on Saturday, the second attack in three days. Two days earlier a Houthi strike damaged the PIF Tower, the city\u2019s tallest skyscraper."),
        ("GAZA", "22,000 children killed in Gaza",
         "More than 22,000 Palestinian children have been killed and 45,000 wounded since October 2023, Gaza\u2019s foreign ministry said, with 71,000 orphaned. Over 11,000 suffered permanent disabilities."),
        ("WHITE HOUSE", "Trump calls Putin his \u2018friend\u2019",
         "Trump called Putin his \u2018friend\u2019. Zelensky told CNN: \u2018For us, he is an enemy... he\u2019s a killer.\u2019 Hours later Russia fired 110 missiles and 400 drones at Ukraine, killing at least nine."),
        ("TEHRAN", "Trump weighs new strikes on Iran",
         "Trump is weighing new strikes on Iran but said he is \u2018not rushing\u2019 a decision until after the New Year. Israel presses for a joint four-to-seven-day air campaign; two US carrier groups are nearby."),
        ("BRUSSELS", "Trump: Europe must defund Ukraine",
         "Joining a Coalition of the Willing meeting by phone, Trump urged Europe to stop spending billions on Ukraine. Europe reaffirmed support \u2018as long as necessary\u2019 and pledged \u20ac70bn in military aid for 2026."),
        ("MYANMAR", "Myanmar, China reject ICJ ruling",
         "Myanmar rejected as \u2018unfair\u2019 the ruling that its forces committed genocide; China called it unhelpful. The 9\u20136 judgment is the first in the court\u2019s 80-year history to find a state guilty of genocide."),
        ("TALLINN", "Moscow: Estonia builds \u2018Iron Curtain\u2019",
         "Estonia will close all five road crossings with Russia from 1 December for six months after a GRU-ordered arson plot against drone maker Threod Systems. Moscow called it a \u2018new Iron Curtain\u2019."),
        ("TOKYO", "Japan core inflation hits 2.2%",
         "Japan\u2019s core inflation hit 2.2% in October, above the Bank of Japan\u2019s 2% target for a second month, pointing to a December rate rise. Rice fell 30% on the year, but energy rose 2.2% as subsidies expired."),
        ("MADRID", "Spain extends banking tax for housing",
         "Prime Minister Pedro S\u00e1nchez will extend the banking levy to 2027, raising \u20ac1.4bn for housing. The tax runs at 1\u20137% of lenders\u2019 income; a snap election is set for 29 November after housing protests."),
        ("BERLIN", "Berlin students protest rearmament",
         "Tens of thousands marched in over 100 German cities against conscription and rearmament. In Berlin, about 10,000 chanted \u2018Never again conscription\u2019 as Merz seeks Europe\u2019s strongest army."),
        ("ROME", "Italy clears Tesla self-driving",
         "Italy gave provisional approval to Tesla Assisted Driving, the first major EU market to do so and the 12th European country, minister Matteo Salvini said. It costs \u20ac99 a month; a full EU vote is due in December."),
        ("BRAS\u00cdLIA", "Bolsonaro hospitalised in Bras\u00edlia",
         "Jailed ex-president Jair Bolsonaro, 71, was hospitalised in Bras\u00edlia with a near-complete intestinal obstruction. He has had nine operations since a 2018 stabbing and is serving a 27-year coup-plot sentence."),
        ("CYBER", "USDA hit by cyberattack",
         "Hackers breached the US Agriculture Department\u2019s farmer-payment system, forcing officials to reset every database password and take loan software offline for a week. The department says no data was lost."),
        ("CAPITOL", "Senate passes energy bill, 62\u201333",
         "The Senate passed the Bipartisan American Affordability and Jobs Act 62\u201333, speeding permits for power plants and making data centres pay their full grid costs \u2014 about $55bn over a decade."),
        ("LOS ANGELES", "GTA 6 smashes $3.79bn record",
         "GTA 6 made $3.79bn in first-day sales, Take-Two said, the biggest entertainment launch in history, with 32.5 million copies sold. It beats GTA V\u2019s $800m first day and Avengers: Endgame\u2019s $2.95bn lifetime gross."),
        ("NEW YORK", "Van Gogh sells for record $190m",
         "Van Gogh\u2019s \u2018Blossoming Chestnut Trees\u2019 (1890) sold for $190.4m at Sotheby\u2019s, a record for the artist, to dealer William Acquavella. The Fischer heirs settled their claim the day before the sale."),
        ("U.S. COURTS", "Judge backs $7.25bn Roundup deal",
         "A Missouri judge approved Bayer\u2019s $7.25bn settlement of Roundup cancer claims, paid over 21 years \u2014 $10,000 to $165,000 per person with non-Hodgkin lymphoma. The judge said Bayer might have gone bankrupt instead."),
        ("BEIRUT", "Europe eyes UN force role in Lebanon",
         "France will present a UN plan for thousands of European troops to replace UN peacekeepers in Lebanon when UNIFIL\u2019s mandate ends on 31 December. The US prefers a smaller mission; Israel opposes it."),
        ("LAS VEGAS", "Verstappen inherits Vegas pole",
         "Max Verstappen inherits pole in Las Vegas after Kimi Antonelli, fastest at 1:33.893, took a five-place penalty for a new engine. George Russell is second, Lando Norris third; both Ferraris went out in Q2."),
        ("ANTALYA", "COP31 runs into overtime",
         "Climate talks in Antalya ran into overtime as the draft deal omits any fossil-fuel phase-out and drops a $120bn adaptation target. The EU\u2019s climate chief said it is \u2018a good deal or no deal\u2019."),
        ("FLORIDA", "Record floods swamp Florida coast",
         "The St. Johns River near Cocoa hit 18.76 feet, breaking its 1953 record, after up to 24 inches of rain drowned Florida\u2019s Space Coast. Sixty-five homes were evacuated; flooding may last into mid-December."),
        ("MUSCAT", "Two tankers hit near Hormuz",
         "Two tankers were hit by unknown projectiles near Khasab, Oman, on Saturday \u2014 one on the stern 11 miles north, one in the engine room 17 miles east. No casualties were reported; Iran blamed a mine."),
        ("KRYVYI RIH", "Two killed in Kryvyi Rih strikes",
         "Russian missiles struck Kryvyi Rih on Friday, killing a seven-year-old boy and a 20-year-old paramedic and wounding 60, including six children, as drones hit rescuers in a \u2018double-tap\u2019 attack."),
    ]
    cols = 3
    margin, gut = 36, 16
    col_w = (W - 2 * margin - (cols - 1) * gut) // cols
    grid_bottom = 958
    row_h = (grid_bottom - grid_top) // 8
    for idx, (kick, head, body) in enumerate(items):
        r, c = divmod(idx, cols)
        x = margin + c * (col_w + gut)
        cy = grid_top + r * row_h
        d.text((x, cy), kick, font=sans_bold(10), fill=RED)
        hf, ht = _fit_headline(d, head, col_w, start=14)
        d.text((x, cy + 10), ht, font=hf, fill=INK)
        bottom = _body_block(d, body, serif(10.5), col_w, 12, x, cy + 28, 4)
        if bottom > cy + row_h:
            raise ValueError("cell overflows its row: %r" % (kick,))

    # ---- Footer ----
    _rule(d, 36, 966, 988, INK, 1)
    d.text((512, 976), "21 NOVEMBER 2026 \u00b7 25 STORIES FROM AROUND THE WORLD",
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
