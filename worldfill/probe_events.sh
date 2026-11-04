#!/usr/bin/env bash
# Step-5 event check through the mod's own HistoryGazetteer (see probes/EventProbe.java).
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
GSON=/home/user/libs/gson-2.10.1.jar
MOD=/home/user/eternal
OUT=/home/user/.cache/wf_probe_events
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
  "$MOD/DensityProbe.java" /home/user/worldfill/probes/EventProbe.java 2>&1 | grep -vE "warning:|^Note:" | head || true
"$JDK/bin/java" -Xmx700m -Dfile.encoding=UTF-8 -cp "$OUT/classes:$MOD/src/main/resources:$GSON" EventProbe
