#!/usr/bin/env bash
# THE JOIN TEST. Does the game's own lookup actually find the people the packs file?
#
# Three questions, in order:
#   1. all people      - exact-id agreement rate between famous_people.state and RulerRegister
#   2. which year      - for the misses, is the pack's state right at some OTHER year of the life?
#   3. in game         - standing at year Y, what share of the people alive there are found?
#
# Threshold (written down before the numbers were seen): the game should find at least 95% of the
# people who were alive in a place that year, in EVERY era, and 98% overall. A person the register
# cannot find is a person the player never meets.
set -uo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"; GSON=/home/user/libs/gson-2.10.1.jar
MOD=/home/user/eternal; HERE=/home/user/worldfill; OUT=/home/user/.cache/wf_probe_famousjoin
rm -rf "$OUT"; mkdir -p "$OUT"
"$JDK/bin/javac" -J-Xmx900m -encoding UTF-8 -nowarn -proc:none -cp "$GSON" \
  -sourcepath "$HERE/stubs:$HERE/stubs_headless:$MOD/src/main/java" -d "$OUT" \
  "$HERE/probes/FamousJoinFullProbe.java" "$HERE/probes/FamousYearProbe.java" \
  "$HERE/probes/FamousIngameProbe.java" || { echo "COMPILE FAILED"; exit 2; }
CP="$OUT:$MOD/src/main/resources:$GSON"
echo "=== 1. every person in the pack, against the register ==="
"$JDK/bin/java" -Xmx1600m -Dfile.encoding=UTF-8 -cp "$CP" FamousJoinFullProbe --full 2>&1 >/dev/null
echo
echo "=== 2. when the join misses, which year of the life explains the pack's state? ==="
"$JDK/bin/java" -Xmx1600m -Dfile.encoding=UTF-8 -cp "$CP" FamousYearProbe 4000
echo
echo "=== 3. in the game: standing in year Y, who is found ==="
"$JDK/bin/java" -Xmx1600m -Dfile.encoding=UTF-8 -cp "$CP" FamousIngameProbe 3000 | tee /tmp/ingame.tsv
python3 - <<'PY'
rows=[l.split('\t') for l in open('/tmp/ingame.tsv').read().splitlines()[1:] if l.strip()]
rates=[(int(r[0]), float(r[3].rstrip('%'))) for r in rows if int(r[1])>=20]
if not rates: print('PASS with too few people to judge'); raise SystemExit(0)
worst=min(rates, key=lambda x: x[1]); avg=sum(r for _,r in rates)/len(rates)
print(f"\nworst era: {worst[0]} at {worst[1]:.1f}%   mean: {avg:.1f}%")
ok = all(r>=95.0 for _,r in rates)
print("VERDICT:", "PASS" if ok else f"FAIL - the threshold is 95% every era; {worst[0]} is at {worst[1]:.1f}%")
raise SystemExit(0 if ok else 1)
PY
