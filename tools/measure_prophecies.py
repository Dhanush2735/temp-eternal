#!/usr/bin/env python3
"""How much of 2027-3000 do the collected prophecies actually cover? (R2-c pilot, 2026-10-27)

Reports, for every year in the range: how many prophecy items are active, whether any of them is dated to
the day, and whether the only coverage is a long span ("rules for 108 years"), which is not the same thing.
"""
import json

doc = json.load(open("/home/user/eternal/src/main/resources/data/eternalengine/eternal/history/prophecies.json"))
items = doc["items"]

rows = []
for year in range(2027, 3001):
    active = [i for i in items if i["start"] <= year <= i["end"]]
    # A "day-dated" item is one event on one day. A reign that merely *starts* on a date is a span: counting
    # it as day-dated made every year to 3000 look dated, which is exactly the sort of flattering miscount
    # this project keeps having to correct.
    day = [i for i in active if i["day"] and (i["end"] - i["start"]) <= 1]
    yearOnly = [i for i in active if not i["day"] and (i["end"] - i["start"]) <= 5]
    span = [i for i in active if (i["end"] - i["start"]) > 5]
    rows.append((year, len(active), len(day), len(yearOnly), len(span)))

withany = [r for r in rows if r[1]]
onlyspan = [r for r in rows if r[1] and r[2] == 0 and r[3] == 0]
none = [r for r in rows if not r[1]]

print("years 2027-3000            : %d" % len(rows))
print("years with any prophecy    : %d  (%.1f%%)" % (len(withany), 100.0 * len(withany) / len(rows)))
print("  of which day-dated       : %d  (%.1f%%)" % (len([r for r in rows if r[2]]),
                                                      100.0 * len([r for r in rows if r[2]]) / len(rows)))
print("  of which year-window only: %d" % len([r for r in rows if r[3] and not r[2]]))
print("  of which a long span only: %d  (%.1f%%)" % (len(onlyspan), 100.0 * len(onlyspan) / len(rows)))
print("years with nothing at all  : %d" % len(none))
if none:
    print("  empty years              : %s" % ", ".join(str(r[0]) for r in none))
print()
print("decade      any   day-dated   long-span-only")
for d in range(2020, 3000, 10):
    chunk = [r for r in rows if d <= r[0] < d + 10]
    if not chunk:
        continue
    print("%-10s %4d %10d %15d" % ("%d-%d" % (d, d + 9),
                                   len([r for r in chunk if r[1]]),
                                   len([r for r in chunk if r[2]]),
                                   len([r for r in chunk if r[1] and not r[2] and not r[3]])))

# honesty validation
bad = [i["id"] for i in items if not i.get("grade") or not i.get("basis") or not i.get("sourceUrl")]
print()
print("schema problems (no grade/basis/source): %d %s" % (len(bad), bad))
early = [i["id"] for i in items if i["start"] < 2027]
print("items claiming a year before 2027 (must be none): %d %s" % (len(early), early))
print("past claims kept as track record: %d" % len(doc["pastClaims"]))
