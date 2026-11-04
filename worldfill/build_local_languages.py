import io
#!/usr/bin/env python3
"""Step 7.3: where languages are spoken, from Glottolog 5.3 -> history/local_languages.json.gz.

Glottolog (Hammarström, Forkel, Haspelmath & Bank, Glottolog 5.3, CC BY 4.0) gives one map point per
language (8,304 languages). Kept: living languages (ISO 639-3 Language_Type L, from SIL's code
table), no sign languages. Each row: [name, lat, lon, major], major = 1 when the language has an
ISO 639-1 two-letter code (the big languages: Telugu, French, Pashto...).

How the mod uses it (EventNews.cultureLine): from AD 1500 on, the nearest major language within
300 km is "the language of the people here", said next to the state's own languages ("The court
speaks Persian; people here speak Telugu"). Before 1500 it is not used: a point is where a language
is spoken today (Arabic in Egypt only after the 7th century, Turkish in Anatolia after the 11th).
"""
import csv, gzip, json, os, sys

sys.path.insert(0, "/home/user/worldfill")
import modpack as M  # noqa: E402

SRC = os.path.expanduser("~/.cache/srcdata/glottolog")
OUT = f"{M.HISTORY}/local_languages.json.gz"


def main():
    iso = {r["Id"]: r for r in csv.DictReader(open(f"{SRC}/iso-639-3.tab", encoding="utf-8"), delimiter="\t")}
    rows = []
    for r in csv.DictReader(open(f"{SRC}/languages_and_dialects_geo.csv", encoding="utf-8")):
        if r["level"] != "language" or not r["latitude"] or not r["isocodes"]:
            continue
        code = r["isocodes"].split()[0]
        info = iso.get(code)
        if not info or info["Language_Type"] != "L" or "sign language" in r["name"].lower():
            continue
        rows.append([r["name"], round(float(r["latitude"]), 3), round(float(r["longitude"]), 3),
                     1 if info.get("Part1") else 0])
    rows.sort(key=lambda x: (-x[3], x[0]))
    doc = {"format": 1,
           "source": ("Glottolog 5.3 (Hammarström, Forkel, Haspelmath & Bank; CC BY 4.0), languages_and_dialects_geo.csv; "
                      "living status and ISO 639-1 codes from the SIL ISO 639-3 code table. worldfill/build_local_languages.py"),
           "note": "rows are [name, lat, lon, major]; one point per language, where it is spoken today; major = has an ISO 639-1 code",
           "languages": rows}
    with open(OUT + ".tmp", "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(OUT + ".tmp", OUT)
    print(json.dumps({"languages": len(rows), "major": sum(r[3] for r in rows), "bytes": os.path.getsize(OUT)}))


if __name__ == "__main__":
    main()
