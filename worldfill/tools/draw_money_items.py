#!/usr/bin/env python3
"""Step 23b: draws the 16x16 item pictures of money you can hold (flat pixel art like the other items), one per look.

Writes, for every look of Denominations.Form (eternal/.../money/Denominations.java):
  eternal/src/main/resources/assets/eternalengine/textures/item/<id>.png
  eternal/src/main/resources/assets/eternalengine/models/item/<id>.json   (item/generated)
  the item's fallback name in eternal/src/main/resources/assets/eternalengine/lang/en_us.json
and worldfill/pictures/money_items.png, all looks side by side at 8x with their names, for checking by eye
(pictures/ is kept with the workspace; folders named "out" are not).
All pictures are our own drawings (no photos of real coins).
"""
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(ROOT, "eternal/src/main/resources/assets/eternalengine")
TEX = os.path.join(ASSETS, "textures/item")
MODELS = os.path.join(ASSETS, "models/item")
LANG = os.path.join(ASSETS, "lang/en_us.json")
SHEET = os.path.join(ROOT, "worldfill/pictures/money_items.png")

# id -> name when the piece carries no money; must match Denominations.Form (itemId, title).
LOOKS = [
    ("coin_gold", "Gold coin"),
    ("coin_silver", "Silver coin"),
    ("coin_copper", "Copper coin"),
    ("coin_holed", "Holed coin"),
    ("coin_nickel", "Coin"),
    ("banknote", "Banknote"),
    ("cowrie", "Cowrie shells"),
    ("cacao_bean", "Cacao beans"),
    ("silver_weighed", "Silver by weight"),
    ("copper_weighed", "Copper by weight"),
    ("manilla", "Manillas"),
    ("shell_money", "Shell money"),
    ("salt_bar", "Salt bars"),
    ("cloth_bolt", "Homespun cloth"),
    ("pelt", "Beaver pelts"),
    ("bullet_coin", "Bullet coin"),
]


class Pic:
    def __init__(self):
        self.im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))

    def px(self, x, y, c):
        if 0 <= x < 16 and 0 <= y < 16:
            self.im.putpixel((x, y), c + (255,) if len(c) == 3 else c)

    def get(self, x, y):
        return self.im.getpixel((x, y)) if 0 <= x < 16 and 0 <= y < 16 else (0, 0, 0, 0)

    def clear(self, x, y):
        if 0 <= x < 16 and 0 <= y < 16:
            self.im.putpixel((x, y), (0, 0, 0, 0))

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def outline(self, c):
        """A dark edge around every drawn pixel that touches empty space."""
        filled = {(x, y) for y in range(16) for x in range(16) if self.get(x, y)[3] > 0}
        for (x, y) in filled:
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (nx, ny) not in filled:
                    self.px(x, y, c)
                    break


def inside_ellipse(x, y, cx, cy, rx, ry):
    return ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0


def coin(p, cx, cy, r, base, rim, hi, dark, ring=True):
    """A round piece lit from the upper left: rim, a bright upper-left edge, a shaded lower-right edge, a raised ring."""
    for y in range(16):
        for x in range(16):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx, dy)
            if d > r:
                continue
            c = base
            if d > r - 1.0:
                c = rim
            elif d > r - 2.0:
                c = hi if dx + dy < 0 else dark
            elif ring and r - 3.2 < d <= r - 2.4:
                c = dark if dx + dy < 0 else hi
            p.px(x, y, c)


def poly(p, pts, c, scale=8):
    """Fill a polygon given in pixel units (supersampled, then a pixel is in when half of it is covered)."""
    big = Image.new("L", (16 * scale, 16 * scale), 0)
    ImageDraw.Draw(big).polygon([(x * scale, y * scale) for x, y in pts], fill=255)
    small = big.resize((16, 16), Image.BOX)
    for y in range(16):
        for x in range(16):
            if small.getpixel((x, y)) >= 128:
                p.px(x, y, c)


# ------------------------------------------------------------------------------------------------------ the looks

def coin_gold():
    p = Pic()
    coin(p, 8, 8, 7.0, (232, 184, 48), (128, 86, 18), (255, 236, 140), (184, 134, 30))
    # a crown: three points over a band
    dark, hi = (150, 104, 22), (255, 226, 120)
    for x in (6, 8, 10):
        p.px(x, 6, dark)
    p.rect(6, 7, 10, 7, dark)
    p.rect(6, 8, 10, 9, (206, 158, 38))
    p.line(6, 10, 10, 10, dark)
    p.px(7, 8, hi)
    return p


def coin_silver():
    p = Pic()
    coin(p, 8, 8, 7.0, (198, 203, 210), (100, 106, 116), (250, 252, 255), (150, 156, 166))
    # a head in profile, facing right
    head, shade = (150, 156, 166), (120, 126, 136)
    p.rect(7, 5, 9, 9, head)
    p.px(10, 7, head)
    p.px(10, 8, shade)
    p.rect(6, 6, 6, 8, shade)
    p.rect(7, 10, 9, 10, shade)
    p.px(8, 6, (230, 234, 240))
    return p


def coin_copper():
    p = Pic()
    coin(p, 8, 8, 7.0, (194, 110, 58), (100, 52, 22), (238, 170, 120), (148, 80, 38))
    dark = (126, 64, 28)
    p.line(8, 5, 8, 10, dark)  # a value stroke and a small wreath
    p.px(7, 5, dark)
    p.rect(7, 10, 9, 10, dark)
    p.px(5, 9, (216, 140, 86))
    p.px(11, 9, (216, 140, 86))
    return p


def coin_holed():
    p = Pic()
    coin(p, 8, 8, 7.0, (150, 128, 64), (78, 64, 26), (198, 178, 106), (112, 94, 42), ring=False)
    rim = (78, 64, 26)
    # the square hole with its raised square rim
    p.rect(6, 6, 9, 9, (112, 94, 42))
    for x in range(6, 10):
        for y in range(6, 10):
            if x in (6, 9) or y in (6, 9):
                p.px(x, y, rim)
    p.rect(7, 7, 8, 8, (0, 0, 0, 0))
    for x, y in ((7, 7), (8, 7), (7, 8), (8, 8)):
        p.clear(x, y)
    # four characters around the hole
    ch = (96, 80, 34)
    for x, y in ((7, 3), (8, 3), (7, 12), (8, 12), (3, 7), (3, 8), (12, 7), (12, 8)):
        p.px(x, y, ch)
    # the red cord that strings the cash, through the hole
    cord = (176, 40, 34)
    for x, y in ((0, 9), (1, 9), (2, 9), (13, 6), (14, 6), (15, 6)):
        p.px(x, y, cord)
    p.px(7, 8, cord)
    p.px(8, 7, cord)
    return p


def coin_nickel():
    p = Pic()
    coin(p, 8, 8, 6.5, (178, 188, 198), (92, 100, 112), (230, 236, 242), (140, 148, 160))
    # reeded edge marks and a big value numeral
    for a in range(0, 360, 30):
        x = round(8 + 6.0 * math.cos(math.radians(a)) - 0.5)
        y = round(8 + 6.0 * math.sin(math.radians(a)) - 0.5)
        p.px(x, y, (120, 128, 140))
    num = (110, 118, 130)
    p.line(7, 5, 7, 10, num)
    p.line(9, 5, 9, 10, num)
    p.line(9, 5, 10, 5, num)
    p.line(9, 10, 10, 10, num)
    p.line(10, 5, 10, 10, num)
    return p


def banknote():
    p = Pic()
    paper, edge, frame, ink = (214, 226, 188), (66, 98, 62), (150, 172, 122), (84, 116, 76)
    p.rect(0, 4, 15, 11, paper)
    for x in range(16):
        p.px(x, 4, edge)
        p.px(x, 11, edge)
    for y in range(4, 12):
        p.px(0, y, edge)
        p.px(15, y, edge)
    for x in range(2, 14):
        p.px(x, 5, frame)
        p.px(x, 10, frame)
    # a portrait oval on the left, the value on the right, a seal in between
    for y in range(6, 10):
        for x in range(2, 6):
            if inside_ellipse(x, y, 4.0, 8.0, 2.1, 2.3):
                p.px(x, y, ink)
    p.px(3, 7, (190, 206, 166))
    p.rect(11, 6, 13, 6, ink)
    p.rect(13, 7, 13, 9, ink)
    p.rect(11, 9, 12, 9, ink)
    p.px(8, 7, (176, 70, 60))
    p.px(9, 8, (176, 70, 60))
    p.px(8, 8, (200, 96, 80))
    # a second note peeking out behind
    for x in range(2, 15):
        p.px(x, 3, (186, 200, 160))
    p.px(14, 3, edge)
    return p


def cowrie_shell(p, cx, cy, rx, ry):
    base, shade, line, slit, tooth = (244, 236, 214), (212, 198, 164), (150, 128, 92), (92, 70, 48), (226, 214, 186)
    for y in range(16):
        for x in range(16):
            if inside_ellipse(x, y, cx, cy, rx, ry):
                dx = x + 0.5 - cx
                p.px(x, y, shade if dx > rx * 0.35 else base)
    p.outline(line)
    top, bottom = int(cy - ry + 2), int(cy + ry - 2)
    sx = int(cx - 0.5)
    for y in range(top, bottom + 1):
        p.px(sx, y, slit)
        if (y - top) % 2 == 1:
            p.px(sx - 1, y, tooth)
            p.px(sx + 1, y, tooth)


def cowrie():
    back = Pic()
    cowrie_shell(back, 11.0, 6.5, 3.6, 5.0)
    p = Pic()
    cowrie_shell(p, 6.5, 9.0, 4.4, 6.2)
    back.im.alpha_composite(p.im)
    out = Pic()
    out.im = back.im
    return out


def cacao_bean():
    p = Pic()
    beans = [(4.5, 9.0, 2.8, 4.2), (9.0, 6.0, 2.8, 4.2), (11.5, 11.0, 2.8, 4.0)]
    base, hi, line, seam = (112, 62, 30), (156, 96, 52), (58, 30, 12), (82, 42, 18)
    for cx, cy, rx, ry in beans:
        q = Pic()
        for y in range(16):
            for x in range(16):
                if inside_ellipse(x, y, cx, cy, rx, ry):
                    q.px(x, y, hi if (x + 0.5 - cx) + (y + 0.5 - cy) < -1.5 else base)
        q.outline(line)
        for y in range(int(cy - ry + 2), int(cy + ry - 1)):
            q.px(int(cx), y, seam)
        p.im.alpha_composite(q.im)
    return p


def silver_weighed():
    p = Pic()
    base, hi, dark, line = (196, 202, 210), (246, 248, 252), (146, 152, 162), (84, 90, 100)
    # hacksilver: a cut bar, a bent piece of a neck ring and half a coin, ready for the scales
    poly(p, [(0.8, 9.6), (11.2, 7.2), (12.8, 11.0), (2.4, 13.8)], base)
    for y in range(16):
        for x in range(16):
            dx, dy = x + 0.5 - 11.0, y + 0.5 - 6.2
            d = math.hypot(dx, dy)
            if 2.3 <= d <= 4.4 and dy <= 0.6:
                p.px(x, y, base)
            if x <= 4 and math.hypot(x + 0.5 - 4.6, y + 0.5 - 4.6) <= 3.4:
                p.px(x, y, base)
    p.outline(line)
    p.line(2, 10, 10, 8, hi)
    p.line(3, 12, 11, 10, dark)
    p.px(8, 4, hi)
    p.px(9, 3, hi)
    p.px(10, 2, hi)
    p.px(2, 3, hi)
    p.px(2, 4, hi)
    p.px(3, 6, dark)
    # a cut mark on the bar and a peck mark on the half coin
    p.px(6, 10, line)
    p.px(6, 11, dark)
    p.px(3, 4, dark)
    return p


def copper_weighed():
    p = Pic()
    base, hi, dark, line = (190, 108, 56), (236, 164, 112), (146, 78, 38), (94, 46, 18)
    # an ingot with hollow sides (the "ox hide" shape)
    poly(p, [(1, 3), (8, 4.8), (15, 3), (12.8, 8), (15, 13), (8, 11.2), (1, 13), (3.2, 8)], base)
    p.outline(line)
    p.line(3, 4, 7, 5, hi)
    p.line(9, 5, 13, 4, hi)
    p.line(4, 6, 4, 10, hi)
    p.line(11, 6, 11, 10, dark)
    p.line(4, 11, 12, 11, dark)
    p.px(8, 8, dark)
    return p


def manilla():
    p = Pic()
    base, hi, dark = (178, 122, 58), (226, 176, 104), (104, 64, 26)
    # an open ring, its opening at the bottom, with flared ends
    for y in range(16):
        for x in range(16):
            dx, dy = x + 0.5 - 8, y + 0.5 - 7.5
            d = math.hypot(dx, dy)
            ang = math.degrees(math.atan2(dy, dx))
            if 4.0 <= d <= 6.4 and not (55 < ang < 125):
                p.px(x, y, hi if dy < -2 and dx < 2 else base)
    for cx, cy in ((4.4, 12.0), (11.6, 12.0)):
        for y in range(16):
            for x in range(16):
                if inside_ellipse(x, y, cx, cy, 1.9, 1.7):
                    p.px(x, y, base)
    p.outline(dark)
    p.px(4, 11, hi)
    p.px(11, 11, hi)
    return p


def shell_money():
    p = Pic()
    # small olive shells (nzimbu), each with a dark spire and a slit, in a little heap: two behind, three in front
    out, white, grey, slit, spire = (92, 86, 78), (242, 240, 232), (200, 196, 186), (150, 144, 132), (58, 52, 46)
    shape = ["..s.", ".owo", "owgo", "owgo", "oxgo", "owgo", ".oo."]
    colours = {"o": out, "w": white, "g": grey, "x": slit, "s": spire}
    for sx, sy in ((3, 1), (8, 2), (0, 8), (5, 9), (10, 8)):
        for dy, row in enumerate(shape):
            for dx, ch in enumerate(row):
                if ch != ".":
                    p.px(sx + dx, sy + dy, colours[ch])
    p.px(14, 13, white)
    p.px(14, 14, out)
    p.px(13, 14, out)
    return p


def salt_bar():
    p = Pic()
    salt, shade, line, band, bandd = (234, 230, 220), (196, 190, 176), (124, 116, 102), (128, 84, 42), (90, 56, 26)
    poly(p, [(0.5, 6), (2, 4.5), (14, 4.5), (15.5, 6), (15.5, 10), (14, 11.5), (2, 11.5), (0.5, 10)], salt)
    for x in range(16):
        for y in range(9, 12):
            if p.get(x, y)[3]:
                p.px(x, y, shade)
    p.outline(line)
    for bx in (4, 11):
        for y in range(4, 12):
            if p.get(bx, y)[3]:
                p.px(bx, y, band)
                p.px(bx + 1, y, bandd)
    p.px(7, 6, (250, 248, 242))
    p.px(8, 6, (250, 248, 242))
    return p


def cloth_bolt():
    p = Pic()
    wool, stripe, line, end, endd = (152, 132, 104), (126, 108, 84), (76, 62, 46), (182, 162, 130), (110, 92, 70)
    p.rect(1, 4, 11, 12, wool)
    for x in range(1, 12):
        for y in range(4, 13):
            if (x + y) % 3 == 0:
                p.px(x, y, stripe)
    for y in range(16):
        for x in range(16):
            if inside_ellipse(x, y, 12.0, 8.5, 3.0, 4.6):
                p.px(x, y, end)
    p.outline(line)
    for x, y in ((12, 8), (12, 9), (11, 8), (13, 7), (11, 10), (13, 10), (12, 6)):
        p.px(x, y, endd)
    p.px(12, 8, (90, 74, 56))
    # the loose end hanging down
    p.rect(2, 13, 6, 14, wool)
    p.line(2, 15, 6, 15, line)
    p.px(1, 13, line)
    p.px(1, 14, line)
    p.px(7, 13, line)
    p.px(7, 14, line)
    return p


def pelt():
    p = Pic()
    hoop, hoopd, fur, furl, line = (196, 166, 112), (140, 112, 66), (104, 68, 38), (142, 98, 58), (58, 36, 18)
    # a beaver skin stretched round on a willow hoop
    for y in range(16):
        for x in range(16):
            d = math.hypot(x + 0.5 - 8, y + 0.5 - 8)
            if d <= 7.5:
                p.px(x, y, hoop if d > 6.4 else (furl if (x * 7 + y * 3) % 5 == 0 else fur))
    for y in range(16):
        for x in range(16):
            d = math.hypot(x + 0.5 - 8, y + 0.5 - 8)
            if 6.4 < d <= 7.5 and (x + y) % 4 == 0:
                p.px(x, y, hoopd)
    p.outline(line)
    for y in range(4, 12):  # the lighter belly fur down the middle
        p.px(8, y, furl)
    p.px(7, 6, furl)
    p.px(9, 9, furl)
    return p


def bullet_coin():
    p = Pic()
    base, hi, dark, line = (202, 206, 214), (250, 252, 255), (140, 146, 156), (88, 94, 104)
    # a silver lump bent round into a ball, the ends meeting in a cleft at the bottom
    for y in range(16):
        for x in range(16):
            dx, dy = x + 0.5 - 8, y + 0.5 - 8.5
            d = math.hypot(dx, dy)
            if d <= 6.0:
                c = base
                if d > 4.4:
                    c = dark if dx + dy > 0 else base
                if math.hypot(dx + 2, dy + 2) < 1.8:
                    c = hi
                p.px(x, y, c)
    p.outline(line)
    for y in range(10, 15):
        p.px(8, y, line)
    p.px(7, 13, dark)
    p.px(9, 13, dark)
    # the stamps: a wheel (chakra) and the reign's mark
    for x, y in ((8, 4), (7, 5), (9, 5), (8, 6)):
        p.px(x, y, dark)
    p.px(8, 5, line)
    p.px(11, 8, dark)
    p.px(11, 9, dark)
    return p


DRAW = {
    "coin_gold": coin_gold, "coin_silver": coin_silver, "coin_copper": coin_copper, "coin_holed": coin_holed,
    "coin_nickel": coin_nickel, "banknote": banknote, "cowrie": cowrie, "cacao_bean": cacao_bean,
    "silver_weighed": silver_weighed, "copper_weighed": copper_weighed, "manilla": manilla,
    "shell_money": shell_money, "salt_bar": salt_bar, "cloth_bolt": cloth_bolt, "pelt": pelt,
    "bullet_coin": bullet_coin,
}


def main():
    os.makedirs(TEX, exist_ok=True)
    os.makedirs(MODELS, exist_ok=True)
    pics = []
    for item_id, title in LOOKS:
        im = DRAW[item_id]().im
        im.save(os.path.join(TEX, f"{item_id}.png"))
        with open(os.path.join(MODELS, f"{item_id}.json"), "w", encoding="utf-8") as f:
            json.dump({"parent": "minecraft:item/generated", "textures": {"layer0": f"eternalengine:item/{item_id}"}},
                      f, indent=2)
            f.write("\n")
        pics.append((item_id, title, im))
    with open(LANG, encoding="utf-8") as f:
        lang = json.load(f)
    for item_id, title in LOOKS:
        lang[f"item.eternalengine.{item_id}"] = title
    with open(LANG, "w", encoding="utf-8") as f:
        json.dump(lang, f, indent=2, ensure_ascii=False)
        f.write("\n")
    # the sheet: 4 x 4 at 8x with names
    s, gap, label = 8, 14, 16
    cols = 4
    rows = (len(pics) + cols - 1) // cols
    w = cols * (16 * s + gap) + gap
    h = rows * (16 * s + label + gap) + gap
    sheet = Image.new("RGBA", (w, h), (58, 58, 64, 255))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for i, (item_id, title, im) in enumerate(pics):
        x = gap + (i % cols) * (16 * s + gap)
        y = gap + (i // cols) * (16 * s + label + gap)
        sheet.alpha_composite(Image.new("RGBA", (16 * s, 16 * s), (139, 139, 139, 255)), (x, y))
        sheet.alpha_composite(im.resize((16 * s, 16 * s), Image.NEAREST), (x, y))
        draw.text((x, y + 16 * s + 3), title, fill=(235, 235, 235, 255), font=font)
    os.makedirs(os.path.dirname(SHEET), exist_ok=True)
    sheet.save(SHEET)
    print(f"{len(pics)} looks: textures, models and names written; sheet {SHEET}")


if __name__ == "__main__":
    main()
