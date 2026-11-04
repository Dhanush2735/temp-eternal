#!/usr/bin/env python3
"""Score the prophecy corpus against the record, and write the tables used in the report."""
import json
from collections import Counter, defaultdict

doc = json.load(open("/home/user/testrun/verify/prophecy_corpus.json"))
C = doc["claims"]

def bucket(v):
    if v.startswith("HIT (postdiction)"):
        return "postdiction"
    return {"MISS": "miss", "MISS (as a date)": "miss", "HIT": "hit", "PARTIAL": "partial",
            "OPEN": "open", "UNJUDGEABLE": "unjudgeable"}[v]

for c in C:
    c["b"] = bucket(c["verdict"])
    c["lead"] = (c["claimYear"] - c["textYear"]) if not c["postdiction"] else (c["claimYear"] - c["textYear"])

tot = Counter(c["b"] for c in C)
checkable = [c for c in C if c["b"] != "unjudgeable"]
resolved = [c for c in C if c["b"] in ("hit", "miss", "postdiction")]
opens = [c for c in C if c["b"] == "open"]

print("=== OVERALL ===")
print("claims                 : %d from %d named sources/claimants" % (len(C), len({c["source"] for c in C})))
print("checkable (not vague)  : %d  (%.0f%%)" % (len(checkable), 100.0 * len(checkable) / len(C)))
print("vague / unjudgeable    : %d  (%.0f%%)" % (tot["unjudgeable"], 100.0 * tot["unjudgeable"] / len(C)))
print("resolved (date passed) : %d" % len(resolved))
print("  MISS                 : %d" % tot["miss"])
print("  HIT                  : %d  (of which postdictions: %d)" % (tot["hit"] + tot["postdiction"], tot["postdiction"]))
print("  genuine HIT, written before the event: %d" % tot["hit"])
print("still OPEN (after 2026): %d" % len(opens))
print()
print("hit rate among resolved : %.1f%%  (%d of %d)" %
      (100.0 * (tot["hit"] + tot["postdiction"]) / max(1, len(resolved)),
       tot["hit"] + tot["postdiction"], len(resolved)))
print("hit rate, postdictions excluded : %.1f%%  (%d of %d)" %
      (100.0 * tot["hit"] / max(1, len(resolved)), tot["hit"], len(resolved)))

print()
print("=== BY SOURCE ===")
print("%-34s %5s %5s %5s %5s %5s" % ("source", "n", "miss", "hit", "vague", "open"))
rows = []
for src, cs in sorted(defaultdict(list, {s: [c for c in C if c["source"] == s]
                                         for s in {c["source"] for c in C}}).items()):
    k = Counter(c["b"] for c in cs)
    rows.append((src, len(cs), k["miss"], k["hit"] + k["postdiction"], k["unjudgeable"], k["open"]))
for r in sorted(rows, key=lambda r: (-r[1], r[0])):
    print("%-34s %5d %5d %5d %5d %5d" % r)

print()
print("=== LEAD TIME (how far ahead the claim was made) ===")
leads = sorted(c["lead"] for c in C if c["b"] != "unjudgeable")
import statistics
print("median lead : %.0f years" % statistics.median(leads))
print("mean lead   : %.0f years" % statistics.mean(leads))
print("longest     : %d years (%s)" % (max(leads), [c["source"] for c in C if c["lead"] == max(leads)][0]))
for lo, hi, name in [(-10000, 0, "written after the event (postdiction)"), (0, 25, "0-25 years"),
                     (25, 100, "26-100 years"), (100, 1000, "101-1000"), (1000, 10 ** 9, "over 1000")]:
    n = len([c for c in C if c["b"] != "unjudgeable" and lo <= c["lead"] < hi])
    print("  %-38s %d" % (name, n))

print()
print("=== RECALCULATION (the same claimant moving the date after failure) ===")
groups = defaultdict(list)
for c in C:
    groups[(c["source"], c["claimant"])].append(c)
for (src, cl), cs in sorted(groups.items()):
    if len(cs) > 1 and len({c["claimYear"] for c in cs}) > 1:
        print("  %-28s %-26s %s" % (src, cl, " -> ".join(str(int(c["claimYear"])) for c in sorted(cs, key=lambda c: c["claimYear"]))))

print()
print("=== THE SIX STILL OPEN ===")
for c in sorted(opens, key=lambda c: c["claimYear"]):
    print("  %-9s %-12s lead %5.0f y  %s" % (int(c["claimYear"]), c["source"][:12], c["lead"], c["claim"][:78]))

# write a markdown table of every claim, grouped by verdict, for the report
with open("/home/user/testrun/verify/prophecy_scoreboard.md", "w") as f:
    f.write("| # | source | text written | claims | lead | verdict | note |\n|---|---|---|---|---|---|---|\n")
    for i, c in enumerate(sorted(C, key=lambda c: c["claimYear"]), 1):
        yrs = str(int(c["claimYear"]))
        if c["claimYear"] < 0:
            yrs = "%d BCE" % -int(c["claimYear"])
        f.write("| %d | %s | %s | %s | %+d | %s | %s |\n" % (
            i, c["source"], c["textYear"], yrs, c["lead"], c["verdict"],
            (c["note"] or c["evidence"])[:110].replace("|", "/")))
print()
print("wrote testrun/verify/prophecy_scoreboard.md")
