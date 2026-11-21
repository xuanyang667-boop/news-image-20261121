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


def render(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead ----
    d.text((512, 20), "THE WORLD", font=serif_bold(88), fill=INK, anchor="ma")
    _tracked_centered(d, 512, 122, "IN ONE IMAGE", serif_bold(28), INK, 14)
    _rule(d, 44, 164, 980, INK, 3)
    _rule(d, 44, 170, 980, INK, 1)
    d.text((512, 180), "SATURDAY \u00b7 21 NOVEMBER 2026", font=serif_bold(27), fill=RED, anchor="ma")
    _rule(d, 44, 222, 980, RED, 2)

    # ---- Lead: Geneva, killer robots ----
    d.text((44, 236), "GENEVA \u2014 TOP STORY", font=sans_bold(24), fill=RED)
    y = _lines(d, 44, 266, "UN states agree to draft \u2018killer robot\u2019 rules by 2028",
               serif_bold(38), INK, 520, 43)
    y = _lines(d, 44, y + 8,
               "128 countries at the UN weapons convention in Geneva agreed "
               "early on Saturday to spend two years drawing up rules on AI "
               "weapons that kill without human control.",
               serif(20), INK, 520, 25)
    d.text((44, y + 8), "Only to \u2018elaborate\u2019, not negotiate.", font=serif_bold(21), fill=RED)

    # ---- Lead panel: globe over Geneva ----
    d.rectangle([600, 236, 980, 516], fill=NAVY)
    cx, cy, r = 790, 348, 66
    for sx, sy in [(640, 262), (700, 300), (930, 282), (900, 330), (660, 420), (940, 430)]:
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=LIGHT)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=LIGHT, width=3)
    d.ellipse([cx - 28, cy - r, cx + 28, cy + r], outline=LIGHT, width=2)
    d.ellipse([cx - 58, cy - r + 18, cx + 58, cy + r - 18], outline=LIGHT, width=2)
    d.line([(cx - r, cy), (cx + r, cy)], fill=LIGHT, width=2)
    d.line([(cx - 52, cy - 40), (cx + 52, cy - 40)], fill=LIGHT, width=2)
    d.line([(cx - 52, cy + 40), (cx + 52, cy + 40)], fill=LIGHT, width=2)
    d.rectangle([600, 458, 980, 516], fill=STEEL)
    d.text((790, 466), "Russia blocked the word", font=sans_bold(20), fill=LIGHT, anchor="ma")
    d.text((790, 490), "\u2018negotiate\u2019", font=sans_bold(20), fill=LIGHT, anchor="ma")

    _rule(d, 44, 552, 980, INK, 2)

    # ---- Markets: Wall Street correction ----
    d.text((44, 566), "MARKETS", font=sans_bold(24), fill=RED)
    y = _lines(d, 44, 594, "Wall Street slides into correction",
               serif_bold(36), INK, 456, 42)
    y = _lines(d, 44, y + 8,
               "S&P 500 fell 3.7% on Friday and the Dow 1.9%, both now "
               "more than 10% below their peaks as the AI sell-off deepened.",
               serif(19), INK, 456, 22)
    base = 810
    for i, h in enumerate((48, 36, 22)):
        x0 = 44 + i * 76
        d.rectangle([x0, base - h, x0 + 52, base], fill=RED if i < 2 else GOLD)
    _rule(d, 44, base, 300, INK, 2)
    d.text((300, 762), "-3.7%", font=serif_bold(38), fill=RED)

    # ---- Riyadh: Houthi missiles intercepted ----
    d.text((540, 566), "RIYADH", font=sans_bold(24), fill=RED)
    y = _lines(d, 540, 594, "Houthis fire at Riyadh again",
               serif_bold(30), INK, 440, 38)
    y = _lines(d, 540, y + 8,
               "Saudi air defences downed three Houthi ballistic missiles "
               "over Riyadh early on Saturday.",
               serif(19), INK, 440, 22)
    # skyline silhouette
    for x0, w, h in [(540, 34, 22), (582, 26, 34), (616, 40, 26), (664, 24, 18), (696, 30, 30)]:
        d.rectangle([x0, 806 - h, x0 + w, 806], fill=NAVY)
    # missile trail + interception burst
    d.line([(700, 736), (652, 776)], fill=GOLD, width=3)
    d.ellipse([640, 764, 664, 788], fill=GOLD)
    for dx, dy in [(0, -18), (0, 18), (-18, 0), (18, 0),
                   (-13, -13), (13, -13), (-13, 13), (13, 13)]:
        d.line([(652, 776), (652 + dx, 776 + dy)], fill=GOLD, width=2)
    d.text((740, 772), "3 missiles", font=serif_bold(34), fill=RED)

    _rule(d, 44, 822, 980, INK, 2)

    # ---- Also on 21 November ----
    d.text((44, 836), "ALSO ON 21 NOVEMBER", font=sans_bold(27), fill=INK)
    columns = [
        ("COP31 \u00b7 ANTALYA", "Talks run into overtime as the draft still omits fossil fuels."),
        ("FLORIDA", "Record floods swamp the coast; St. Johns River breaks a 73-year record."),
        ("OMAN", "Two tankers hit near Hormuz; UKMTO reports strikes, no casualties."),
        ("KRYVYI RIH", "Russia strikes again overnight; two killed, dozens hurt."),
    ]
    for i, (kick, text) in enumerate(columns):
        x = 44 + i * 239
        d.text((x, 874), kick, font=sans_bold(17), fill=RED)
        _lines(d, x, 898, text, serif(17), INK, 219, 23)

    _rule(d, 44, 980, 980, INK, 1)
    d.text((512, 990), "21 NOVEMBER 2026 \u00b7 THE WORLD\u2019S NEWS IN ONE IMAGE",
           font=serif_bold(19), fill=INK, anchor="ma")

    img.save(path, "PNG")
    return path


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "assets", "entry.png")
    render(out)
    print(out)


if __name__ == "__main__":
    main()
