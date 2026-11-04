#!/usr/bin/env bash
# Step 25 (the history data fix): who rules, the language and faith, at the world-wide test places and the places of
# the known problems, from the mod's own lookups. Build first (tools/gradle_compile.sh).
# Usage: probe_historyfix.sh [brief|full|world]
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
GSON=/home/user/libs/gson-2.10.1.jar
MOD=/home/user/eternal
OUT=/home/user/.cache/wf_probe_historyfix
mkdir -p "$OUT"
SRC=$MOD/src/main/java
CP="$MOD/build/classes/java/main:$(cat /home/user/.cache/wf_probe_commands/runtime_cp.txt)"
rm -rf "$OUT"; mkdir -p "$OUT"
# the step-25 sources are compiled with the probe, so it runs before the next Gradle build too
"$JDK/bin/javac" -J-Xmx400m -encoding UTF-8 -nowarn -proc:none -cp "$CP" -d "$OUT" \
  "$SRC/com/eternalengine/civilization/LeaderRegister.java" "$SRC/com/eternalengine/civilization/RulerRegister.java" \
  "$SRC/com/eternalengine/civilization/EventNews.java" "$SRC/com/eternalengine/civilization/FamousPeople.java" \
  "$SRC/com/eternalengine/civilization/HistoryChecks.java" \
  "$SRC/com/eternalengine/civilization/HistoricalPresence.java" "$SRC/com/eternalengine/civilization/HistoryGazetteer.java" \
  "$SRC/com/eternalengine/core/WorldKey.java" "$SRC/com/eternalengine/core/WorldQuery.java" \
  "$SRC/com/eternalengine/data/TileStore.java" "$SRC/com/eternalengine/data/TileCache.java" \
  "$SRC/com/eternalengine/data/DataManifest.java" \
  /home/user/worldfill/probes/HistoryFixProbe.java
"$JDK/bin/java" -Xmx700m -Dfile.encoding=UTF-8 -cp "$OUT:$MOD/src/main/resources:$CP" HistoryFixProbe "${1:-brief}"
