#!/usr/bin/env python3
"""Step 22: draws the 16x16 item pictures of the history book's forms (flat pixel art like the step-19/20 items).

Writes eternal/src/main/resources/assets/eternalengine/textures/item/history_book_<form>.png for every form except the
notebook (that is the step-20 history_book.png), and /tmp/s22/book_forms_sheet.png, all forms side by side at 12x, for
checking by eye.
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "eternal/src/main/resources/assets/eternalengine/textures/item")


class Pic:
    def __init__(self):
        self.im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))

    def px(self, x, y, c):
        if 0 <= x < 16 and 0 <= y < 16:
            self.im.putpixel((x, y), c + (255,) if len(c) == 3 else c)

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


def parchment():
    p = Pic()
    edge, cream, shade, leather, dark = (92, 66, 40), (236, 220, 178), (210, 190, 142), (122, 74, 38), (80, 48, 24)
    p.rect(2, 1, 13, 14, edge)
    p.rect(3, 2, 12, 13, cream)
    p.rect(3, 2, 4, 13, shade)          # the fold of the limp cover at the spine
    p.rect(12, 3, 12, 13, (246, 238, 214))  # page edges
    p.rect(3, 7, 14, 8, leather)         # the strap
    p.rect(14, 6, 15, 9, dark)           # the toggle
    p.px(15, 7, leather)
    p.rect(6, 4, 10, 4, shade)           # a title line
    p.rect(6, 11, 9, 11, shade)
    return p


def palm_leaf():
    p = Pic()
    wood, wdark, leaf, lshade, cord, ink = (122, 78, 42), (82, 50, 26), (222, 190, 120), (186, 148, 82), (70, 44, 26), (96, 70, 40)
    p.rect(0, 4, 15, 5, wood)            # top board
    p.rect(0, 5, 15, 5, wdark)
    for y in (6, 8, 10):                 # leaves
        p.rect(0, y, 15, y, leaf)
        p.rect(0, y + 1, 15, y + 1, lshade)
    p.rect(0, 12, 15, 13, wood)          # bottom board
    p.rect(0, 13, 15, 13, wdark)
    for x in (2, 6, 9, 12):              # scratched letters
        p.px(x, 7, ink)
        p.px(x + 1, 9, ink)
    p.rect(4, 4, 4, 13, cord)            # the cord through the holes
    p.rect(11, 4, 11, 13, cord)
    p.line(4, 13, 2, 15, cord)
    return p


def birch_bark():
    p = Pic()
    white, shade, black, inner, edge = (238, 234, 222), (206, 200, 186), (46, 44, 42), (200, 150, 98), (150, 120, 90)
    p.rect(1, 3, 14, 14, edge)
    p.rect(2, 4, 13, 13, white)
    p.rect(2, 12, 13, 13, shade)
    for (x, y, n) in ((3, 5, 3), (9, 6, 3), (4, 8, 2), (8, 9, 4), (3, 11, 3), (10, 11, 2)):
        p.rect(x, y, x + n - 1, y, black)   # the dark marks of birch bark
    p.rect(10, 1, 14, 3, edge)           # a curl at the top right, showing the tan inner bark
    p.rect(11, 2, 13, 3, inner)
    p.px(14, 4, inner)
    return p


def bark_paper():
    p = Pic()
    light, dark, edge, red, black = (204, 164, 116), (168, 126, 82), (98, 70, 44), (176, 44, 32), (40, 32, 26)
    xs = [(1, 4), (5, 7), (8, 11), (12, 14)]
    for i, (x0, x1) in enumerate(xs):  # a screenfold seen at a slant: panels up and down
        top = 3 if i % 2 == 0 else 4
        bot = 13 if i % 2 == 0 else 12
        p.rect(x0, top, x1, bot, light if i % 2 == 0 else dark)
        p.rect(x0, top - 1, x1, top - 1, edge)
        p.rect(x0, bot + 1, x1, bot + 1, edge)
    p.rect(2, 5, 3, 6, red)
    p.rect(9, 5, 10, 6, red)
    p.px(2, 9, black)
    p.px(3, 10, black)
    p.px(9, 9, black)
    p.rect(9, 10, 10, 10, black)
    p.rect(6, 7, 6, 8, red)
    p.rect(13, 8, 13, 9, black)
    p.rect(1, 2, 1, 14, edge)
    p.rect(14, 2, 14, 14, edge)
    return p


def papyrus():
    p = Pic()
    sheet, fiber, roll, rdark, tie = (226, 204, 146), (198, 174, 112), (186, 156, 92), (140, 112, 60), (120, 60, 30)
    # a closed roll lying from the bottom left to the top right
    for i in range(11):
        x, y = 2 + i, 13 - i
        p.rect(x - 1, y - 1, x + 1, y + 1, sheet)
    for i in range(11):
        x, y = 2 + i, 13 - i
        p.px(x + 1, y + 1, fiber)        # the lower edge in shade
        p.px(x + 2, y + 1, rdark)
    p.rect(0, 12, 2, 14, roll)           # the ends of the roll
    p.px(1, 13, rdark)
    p.rect(12, 1, 14, 3, roll)
    p.px(13, 2, rdark)
    p.line(6, 10, 8, 8, tie)             # the tie round the middle
    p.line(7, 10, 9, 8, tie)
    p.px(5, 11, fiber)
    p.px(10, 6, fiber)
    return p


def bamboo_slips():
    p = Pic()
    slip, sdark, gap, cord, ink = (200, 196, 118), (160, 156, 82), (96, 92, 50), (112, 62, 30), (52, 46, 30)
    for i in range(5):
        x = 1 + i * 3
        p.rect(x, 1, x + 1, 14, slip)
        p.rect(x + 1, 1, x + 1, 14, sdark)
        p.rect(x + 2, 1, x + 2, 14, gap) if i < 4 else None
        for y in (5, 8, 11):             # brush characters in a column
            p.px(x, y, ink)
    p.rect(0, 3, 15, 3, cord)
    p.rect(0, 12, 15, 12, cord)
    return p


def wax_tablets():
    p = Pic()
    wood, wdark, wax, scratch, stylus = (150, 102, 56), (98, 64, 34), (52, 46, 40), (138, 126, 104), (196, 196, 186)
    for x0 in (0, 8):                    # an open pair of tablets
        p.rect(x0, 2, x0 + 7, 13, wood)
        p.rect(x0 + 1, 3, x0 + 6, 12, wax)
        p.rect(x0, 13, x0 + 7, 13, wdark)
    p.rect(7, 2, 8, 13, wdark)           # the hinge
    for y in (5, 7, 9):
        p.rect(2, y, 5, y, scratch)
        p.rect(10, y, 12, y, scratch)
    p.line(9, 15, 15, 9, stylus)         # the stylus
    p.px(15, 9, (120, 120, 112))
    return p


def clay_tablets():
    p = Pic()
    clay, shade, light, wedge = (170, 134, 96), (132, 100, 68), (196, 162, 122), (90, 66, 44)
    p.rect(3, 1, 12, 14, clay)
    p.rect(2, 2, 13, 13, clay)
    p.rect(3, 1, 12, 1, light)
    p.rect(2, 2, 2, 13, light)
    p.rect(13, 2, 13, 13, shade)
    p.rect(3, 14, 12, 14, shade)
    for y in (4, 7, 10):                 # rows of wedges
        for x in (4, 7, 10):
            p.px(x, y, wedge)
            p.px(x + 1, y, wedge)
            p.px(x, y + 1, wedge)
    return p


def rune_sticks():
    p = Pic()
    wood, wdark, cut = (190, 148, 92), (140, 104, 60), (74, 50, 28)
    for (x0, y0) in ((1, 9), (4, 13)):   # two flat sticks lying across
        for i in range(11):
            x, y = x0 + i, y0 - i * 0.8
            p.rect(int(x), int(y), int(x), int(y) + 1, wood)
            p.px(int(x), int(y) + 2, wdark)
    for (x0, y0) in ((1, 9), (4, 13)):
        for i in (2, 5, 8):              # runes: short upright strokes with a slant
            x, y = x0 + i, int(y0 - i * 0.8)
            p.px(x, y, cut)
            p.px(x, y + 1, cut)
            p.px(x + 1, y, cut)
    return p


def knotted_cords():
    p = Pic()
    main, mdark = (206, 176, 124), (150, 120, 76)
    cords = [(196, 62, 48), (232, 204, 128), (98, 66, 42), (240, 236, 222), (196, 62, 48), (90, 120, 70)]
    p.rect(0, 2, 15, 3, main)
    p.rect(0, 3, 15, 3, mdark)
    knots = [(6, 10), (8, 12), (5, 9), (7, 11, 13), (9, 12), (6, 11)]
    lengths = [13, 14, 12, 15, 13, 14]
    for i, c in enumerate(cords):
        x = 1 + i * 2 + (1 if i >= 3 else 0)
        dark = tuple(max(0, v - 60) for v in c)
        p.rect(x, 4, x, lengths[i], c)
        for k in knots[i]:
            if k <= lengths[i]:
                p.px(x, k, dark)
                p.px(x + 1, k, dark)
    return p


def message_stick():
    p = Pic()
    wood, wdark, ochre, white = (168, 106, 58), (110, 66, 32), (222, 160, 62), (240, 234, 220)
    for i in range(13):                  # a stick from the bottom left to the top right
        x, y = 1 + i, 14 - i
        p.rect(x, y - 1, x + 1, y, wood)
        p.px(x + 1, y + 1, wdark)
    for i in (2, 6, 10):                 # ochre bands
        x, y = 1 + i, 14 - i
        p.px(x, y, ochre)
        p.px(x + 1, y - 1, ochre)
        p.px(x + 1, y, ochre)
    for i in (4, 8, 12):                 # white dots
        p.px(1 + i, 13 - i, white)
    return p


def tally_stick():
    p = Pic()
    wood, light, notch, bark = (194, 154, 98), (220, 186, 132), (92, 62, 32), (120, 86, 50)
    for i in range(12):
        x, y = 2 + i, 13 - i
        p.rect(x - 1, y - 1, x + 1, y + 1, wood)
        p.px(x - 1, y - 1, light)
    p.rect(1, 12, 2, 14, bark)           # bark at both ends
    p.rect(13, 1, 14, 3, bark)
    for i in (2, 4, 6, 8, 10):           # notches along the upper edge
        x, y = 2 + i, 13 - i
        p.px(x - 1, y - 1, notch)
        p.px(x, y - 1, notch)
    return p


FORMS = [("parchment", parchment), ("palm_leaf", palm_leaf), ("birch_bark", birch_bark), ("bark_paper", bark_paper),
         ("papyrus", papyrus), ("bamboo_slips", bamboo_slips), ("wax_tablets", wax_tablets),
         ("clay_tablets", clay_tablets), ("rune_sticks", rune_sticks), ("knotted_cords", knotted_cords),
         ("message_stick", message_stick), ("tally_stick", tally_stick)]


def main():
    os.makedirs(OUT, exist_ok=True)
    pics = [("notebook", Image.open(os.path.join(OUT, "history_book.png")).convert("RGBA"))]
    for name, fn in FORMS:
        im = fn().im
        im.save(os.path.join(OUT, f"history_book_{name}.png"))
        pics.append((name, im))
    s, gap = 12, 10
    sheet = Image.new("RGBA", (len(pics) * (16 * s + gap) - gap, 16 * s), (60, 60, 60, 255))
    for i, (_, im) in enumerate(pics):
        sheet.alpha_composite(im.resize((16 * s, 16 * s), Image.NEAREST), (i * (16 * s + gap), 0))
    os.makedirs("/tmp/s22", exist_ok=True)
    sheet.save("/tmp/s22/book_forms_sheet.png")
    print(f"{len(FORMS)} pictures -> {OUT}")


if __name__ == "__main__":
    main()
