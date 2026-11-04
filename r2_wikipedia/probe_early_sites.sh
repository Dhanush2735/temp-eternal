#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; JAVA_HOME="${JAVA_HOME:-/tmp/eternal-java17}";GSON="${GSON_JAR:-$ROOT/tools/jars/gson.jar}"
TMP="$(mktemp -d /tmp/eternal-site-probe-XXXXXX)";trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/classes" "$TMP/res/data/eternalengine/eternal/history"
if [[ "${1:-}" == stage ]]; then
  cp /home/user/.cache/r2_storage/early_site_stage/{americas.json,places_pleiades.json.gz} "$TMP/res/data/eternalengine/eternal/history/"
fi
"$JAVA_HOME/bin/javac" -encoding UTF-8 -cp "$GSON" -d "$TMP/classes" \
 "$ROOT"/r2_wikipedia/java_probe/site_stubs/org/slf4j/Logger.java \
 "$ROOT"/r2_wikipedia/java_probe/site_stubs/com/eternalengine/EternalEngineMod.java \
 "$ROOT"/r2_wikipedia/java_probe/site_stubs/com/eternalengine/core/WorldStateManager.java \
 "$ROOT"/r2_wikipedia/java_probe/site_stubs/com/eternalengine/civilization/{RulerRegister,Civilization,CivilizationManager}.java \
 "$ROOT"/r2_wikipedia/java_probe/com/eternalengine/civilization/HistoricalPresence.java \
 "$ROOT"/eternal/src/main/java/com/eternalengine/civilization/{SettlementRank,SettlementYearEstimator,HistoryGazetteer,CivHints,CivSynthesis}.java \
 "$ROOT"/r2_wikipedia/java_probe/EarlySiteProbe.java
"$JAVA_HOME/bin/java" -Xmx1536m -cp "$TMP/classes:$TMP/res:$ROOT/eternal/src/main/resources:$GSON" EarlySiteProbe
