#!/usr/bin/env bash
# Measure what the world-fill packs change, through the mod's own HistoryGazetteer.
#
#   bash probe.sh                  # current index.json
#   bash probe.sh --without a.json b.json ...   # same, but as if those packs were not listed
#
# Prints load time, sites per pack, and "% of 400 land points with someone here" by year
# (PresenceProbe). Writes the present-only estimated years to ~/.cache/wf_probe/est_<tag>.tsv.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
GSON=/home/user/libs/gson-2.10.1.jar
MOD=/home/user/eternal
OUT=/home/user/.cache/wf_probe
HIST=data/eternalengine/eternal/history
[ -x "$JDK/bin/java" ] || bash /home/user/libs/get_jdk17.sh "$JDK" | tail -2
mkdir -p "$OUT/classes" /tmp/stubsrc/com/eternalengine/civilization
cat > /tmp/stubsrc/com/eternalengine/civilization/HistoricalPresence.java <<'STUB'
package com.eternalengine.civilization;
public final class HistoricalPresence {
    public static double haversineKm(double lat1, double lon1, double lat2, double lon2) {
        double r = 6371.0d;
        double p1 = Math.toRadians(lat1);
        double p2 = Math.toRadians(lat2);
        double dLat = Math.toRadians(lat2 - lat1);
        double dLon = Math.toRadians(lon2 - lon1);
        double a = Math.sin(dLat / 2.0d) * Math.sin(dLat / 2.0d)
                + Math.cos(p1) * Math.cos(p2) * Math.sin(dLon / 2.0d) * Math.sin(dLon / 2.0d);
        return 2.0d * r * Math.asin(Math.min(1.0d, Math.sqrt(a)));
    }
}
STUB
"$JDK/bin/javac" -encoding UTF-8 -nowarn -cp "$GSON" -d "$OUT/classes" \
  "$MOD/src/main/java/com/eternalengine/civilization/HistoryGazetteer.java" \
  "$MOD/src/main/java/com/eternalengine/civilization/SettlementRank.java" \
  "$MOD/src/main/java/com/eternalengine/civilization/SettlementYearEstimator.java" \
  /tmp/stubsrc/com/eternalengine/civilization/HistoricalPresence.java \
  "$MOD/DensityProbe.java" /home/user/worldfill/probes/PresenceProbe.java 2>&1 | grep -vE "warning:|^Note:" | head || true

RES="$MOD/src/main/resources"
TAG=current
if [ "${1:-}" = "--without" ]; then
  shift
  TAG=without
  ALT="$OUT/res_without"
  rm -rf "$ALT"; mkdir -p "$ALT/$HIST"
  for f in "$RES/$HIST"/*; do ln -s "$f" "$ALT/$HIST/$(basename "$f")"; done
  rm "$ALT/$HIST/index.json"
  python3 - "$RES/$HIST/index.json" "$ALT/$HIST/index.json" "$@" <<'PY'
import json, sys
src, dst, drop = sys.argv[1], sys.argv[2], set(sys.argv[3:])
idx = json.load(open(src))
idx["packs"] = [p for p in idx["packs"] if p not in drop]
json.dump(idx, open(dst, "w"), indent=2)
print("  index without:", sorted(drop))
PY
  RES="$ALT:$RES"
fi
"$JDK/bin/java" -Xmx700m -Dfile.encoding=UTF-8 -cp "$OUT/classes:$RES:$GSON" PresenceProbe "$OUT/est_$TAG.tsv"
