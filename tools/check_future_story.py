#!/usr/bin/env python3
"""Validate the 2027-3000 story against the engine's own rules, before any Java touches it."""
import json, re, sys

JAVA = "/home/user/eternal/src/main/java/com/eternalengine/story/UniverseStory.java"
F = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/history/future_story.json"

# Read the guard words out of the Java, so this check cannot drift from the engine's real rule.
src = open(JAVA).read()
blk = src[src.index("GUARD_WORDS = List.of("):]
blk = blk[:blk.index(");")]
GUARD = re.findall(r'"([a-z]+)"', blk)
print("guard words read from UniverseStory.java:", len(GUARD))

d = json.load(open(F))
fails = []

# 1. provenance everywhere
for layer in ("computed", "projected", "authored"):
    for i, it in enumerate(d[layer]):
        if not it.get("provenance"):
            fails.append("%s[%d] has no provenance" % (layer, i))
        if it["provenance"] != layer.upper():
            fails.append("%s[%d] is marked %s" % (layer, i, it["provenance"]))

# 2. authored lines must be signed
for it in d["authored"]:
    if not it.get("author"):
        fails.append("an authored line is unsigned: " + it["text"][:50])

# 3. the guard: a PROJECTED line may never name a ruler, a war, a disaster or a price
for it in d["projected"]:
    low = it["text"].lower()
    hit = [w for w in GUARD if re.search(r"\b" + w + r"\b", low)]
    if hit:
        fails.append("projected %d-%d names %s" % (it["from"], it["to"], hit))

# 4. chronology
def year(s):
    return int(s[:4])

for it in d["computed"] + d["authored"]:
    y = year(it["date"])
    if not (2027 <= y <= 3000):
        fails.append("%s falls outside 2027-3000" % it["date"])

# 5. is the story actually a story? every century needs something, and the last must be the far end
scenes = sorted(d["authored"], key=lambda x: x["date"])
comps = sorted(d["computed"], key=lambda x: x["date"])
print("\n=== layers ===")
print("COMPUTED %3d  (%s to %s)" % (len(comps), comps[0]["date"], comps[-1]["date"]))
print("PROJECTED %2d  (%d to %d)" % (len(d["projected"]), d["projected"][0]["from"], d["projected"][-1]["to"]))
print("AUTHORED %3d  (%s to %s)" % (len(scenes), scenes[0]["date"], scenes[-1]["date"]))
print("\nfirst scene: {} - {}".format(scenes[0]["date"], scenes[0]["text"][:70]))
print("last scene : {} - {}".format(scenes[-1]["date"], scenes[-1]["text"][:70]))

print("\n=== century coverage (anything at all) ===")
for c in range(2000, 3100, 100):
    lo, hi = max(c, 2027), min(c + 99, 3000)
    comp = len([x for x in comps if lo <= year(x["date"]) <= hi])
    auth = len([x for x in scenes if lo <= year(x["date"]) <= hi])
    proj = len([x for x in d["projected"] if not (x["to"] < lo or x["from"] > hi)])
    flag = "" if (comp or auth or proj) else "   <-- EMPTY"
    print("  %d-%d  computed %3d  authored %2d  projected %s%s" % (lo, hi, comp, auth,
                                                                  "yes" if proj else "no ", flag))

# 6. every chapter must hang on something real, of the kind it claims
comp_dates = {x["date"] for x in d["computed"]}
cent = {(x["from"], x["to"]) for x in d["computed"] if x.get("kind") == "century" or "from" in x} | \
       {(x["from"], x["to"]) for x in d.get("centuryFacts", [])}
prop_years = set()
import os as _os
_pj = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/history/prophecies.json"
if _os.path.exists(_pj):
    for it in json.load(open(_pj))["items"]:
        prop_years.add(it["start"])
for x in d["authored"]:
    kind = x.get("anchorKind", "none")
    y = year(x["date"])
    if kind == "sky" and x["date"] not in comp_dates:
        fails.append("chapter %s claims a sky event that is not in the data" % x["date"])
    if kind == "prophecy" and y not in prop_years:
        fails.append("chapter %s claims a prophecy the corpus does not hold" % x["date"])
    if kind == "century" and not any(a <= y <= b for (a, b) in cent):
        fails.append("chapter %s claims a century fact that is not listed" % x["date"])
kinds = {}
for x in d["authored"]:
    kinds[x.get("anchorKind", "none")] = kinds.get(x.get("anchorKind", "none"), 0) + 1
print("\n=== what the chapters hang on ===")
print(kinds)
print("\n=== chapters hung on real events ===")
for x in sorted(d["authored"], key=lambda y: y["date"]):
    mark = "fact" if x.get("anchored") else "fic "
    print("  %s %-11s %-34s %s" % (mark, x["date"], x["chapter"][:34], x["text"][:52]))

print("\n=== failures ===")
print("none" if not fails else "\n".join("  " + f for f in fails))
sys.exit(1 if fails else 0)
