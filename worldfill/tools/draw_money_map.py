#!/usr/bin/env python3
"""Step 23a: a picture of the world's money - every land cell of the ruler register coloured by its money, in a few
years. Grey = barter (no money), white = a placeholder ("silver and copper coins" / "local money"), the sea dark.
Writes worldfill/pictures/money_world.png (pictures/ is kept with the workspace; folders named "out" are not).
Uses money_coverage.py's copy of the table lookup."""
import colorsys
import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import money_coverage as mc  # noqa: E402

YEARS = [1300, 1800, 2026]
SCALE = 2  # pixels per half-degree cell
W, H = 720 * SCALE, 300 * SCALE  # latitude -60..90
OUT = "/home/user/worldfill/pictures/money_world.png"


def colour(money_id):
    h = int(hashlib.md5(money_id.encode()).hexdigest()[:8], 16)
    hue = (h % 360) / 360.0
    sat = 0.45 + (h // 360 % 40) / 100.0
    val = 0.65 + (h // 14400 % 30) / 100.0
    r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
    return int(r * 255), int(g * 255), int(b * 255)


def main():
    reg = mc.Register(mc.RULERS)
    table = mc.Table(mc.MONEY)
    panels = []
    font = ImageFont.load_default()
    for year in YEARS:
        img = Image.new("RGB", (W, H + 22), (18, 28, 48))
        px = img.load()
        counts = {"named": 0, "barter": 0, "placeholder": 0}
        monies = set()
        for cell in reg.cells:
            lat, lon = cell[0], cell[1]
            if lat < -60:
                continue
            row = table.at(lat, lon, year, lambda y, c=cell: reg.ruler(c, y))
            kind = mc.classify(table, row)
            counts[kind] += 1
            if kind == "barter":
                c = (150, 150, 150)
            elif kind == "placeholder":
                c = (255, 255, 255)
            else:
                c = colour(row["money"])
                monies.add(row["money"])
            x0 = int((lon + 180.0) / 0.5 - 0.5) * SCALE
            y0 = int((90.0 - lat) / 0.5 - 0.5) * SCALE + 22
            for dx in range(SCALE):
                for dy in range(SCALE):
                    if 0 <= x0 + dx < W and 22 <= y0 + dy < H + 22:
                        px[x0 + dx, y0 + dy] = c
        d = ImageDraw.Draw(img)
        d.text((8, 5), f"{year}: {len(monies)} kinds of money on land; cells: {counts['named']} money,"
                       f" {counts['barter']} barter (grey), {counts['placeholder']} placeholder (white)",
               fill=(240, 240, 240), font=font)
        panels.append(img)
        print(year, len(monies), counts)
    sheet = Image.new("RGB", (W, (H + 22) * len(panels) + 26), (10, 14, 24))
    d = ImageDraw.Draw(sheet)
    d.text((8, 7), "Money of the world (step 23a): each colour is one money; grey = no money (barter);"
                   " white = no money named (placeholder: lakes, empty islands)", fill=(255, 255, 255), font=font)
    for i, p in enumerate(panels):
        sheet.paste(p, (0, 26 + i * (H + 22)))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sheet.save(OUT, optimize=True)
    print("wrote", OUT, sheet.size)


if __name__ == "__main__":
    main()
