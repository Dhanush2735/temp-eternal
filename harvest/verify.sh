#!/usr/bin/env bash
# Verify the installed events_wikipedia.json actually loads through the mod's real
# HistoryGazetteer, and re-measure density. Self-healing: re-fetches the JDK/gson and
# recompiles the harness if a sandbox re-provision wiped them (this has happened).
#
# Usage: ./verify.sh
set -uo pipefail
cd /home/user/harvest

# JDK 17 lives outside the saved workspace (a JDK is ~300 MB; the snapshot cap is ~128 MB).
# ~/.cache is on the main disk and is never snapshotted; libs/get_jdk17.sh re-creates it,
# pinned to Temurin 17.0.20.1+1 and checked against its sha256.
JDK="${JDK17:-/home/user/.cache/jdk17}"
GSON=/home/user/libs/gson-2.10.1.jar
MOD=/home/user/eternal
H="$MOD/src/main/resources/data/eternalengine/eternal/history"
OUT=/tmp/lc

echo "== 1. toolchain =="
if [ ! -x "$JDK/bin/java" ] || ! "$JDK/bin/java" -version >/dev/null 2>&1; then
  echo "  JDK missing/broken -> libs/get_jdk17.sh $JDK"
  bash /home/user/libs/get_jdk17.sh "$JDK" | tail -2
fi
echo "  java: $("$JDK/bin/java" -version 2>&1 | head -1)"
if [ ! -f "$GSON" ]; then
  echo "  gson missing -> re-fetching"
  mkdir -p /home/user/libs
  curl -sSL -m 60 -o "$GSON" \
    "https://repo1.maven.org/maven2/com/google/code/gson/gson/2.10.1/gson-2.10.1.jar"
fi
echo "  gson: $(ls -la "$GSON" | awk '{print $5}') bytes"

echo "== 2. index.json registration =="
if grep -q -E '"events_wikipedia\.json(\.gz)?"' "$H/index.json"; then
  echo "  events_wikipedia.json(.gz) is registered"
else
  echo "  WARNING: not registered -- a re-provision likely reverted index.json."
  echo "  Re-add \"events_wikipedia.json\" to the packs array before trusting the load."
fi

echo "== 3. compile harness (real gazetteer + verbatim haversine stub + probes) =="
rm -rf "$OUT"; mkdir -p "$OUT" /tmp/stubsrc/com/eternalengine/civilization
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
"$JDK/bin/javac" -encoding UTF-8 -cp "$GSON" -d "$OUT" \
  "$MOD/src/main/java/com/eternalengine/civilization/HistoryGazetteer.java" \
  "$MOD/src/main/java/com/eternalengine/civilization/SettlementRank.java" \
  "$MOD/src/main/java/com/eternalengine/civilization/SettlementYearEstimator.java" \
  /tmp/stubsrc/com/eternalengine/civilization/HistoricalPresence.java \
  "$MOD/LoadCheck.java" "$MOD/DensityProbe.java" 2>&1 | grep -vE "warning:|^Note:" | head
echo "  classes built: $(find "$OUT" -name '*.class' | wc -l)"

echo "== 4. LoadCheck (mod's real HistoryGazetteer load path) =="
CP="$OUT:$MOD/src/main/resources:$GSON"
"$JDK/bin/java" -Dfile.encoding=UTF-8 -cp "$CP" LoadCheck 2>&1 | sed -n '1,16p'

echo "== 5. DensityProbe =="
"$JDK/bin/java" -Dfile.encoding=UTF-8 -cp "$CP" DensityProbe 2>&1 | sed -n '1,17p'
