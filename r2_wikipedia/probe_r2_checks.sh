#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; JAVA_HOME="${JAVA_HOME:-/tmp/eternal-java17}"; GSON="${GSON_JAR:-$ROOT/tools/jars/gson.jar}"
TMP="$(mktemp -d /tmp/eternal-r2-checks-XXXXXX)";trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/classes" "$TMP/res/data/eternalengine/eternal/history"
"$JAVA_HOME/bin/javac" -encoding UTF-8 -cp "$GSON" -d "$TMP/classes" \
 "$ROOT/r2_wikipedia/java_probe/com/eternalengine/civilization/HistoricalPresence.java" \
 "$ROOT/r2_wikipedia/java_probe/com/eternalengine/knowledge/KnowledgeDate.java" \
 "$ROOT/r2_wikipedia/java_probe/com/eternalengine/knowledge/DatedEvents.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/civilization/WaterChanges.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/civilization/Disasters.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/civilization/SettlementRank.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/civilization/SettlementYearEstimator.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/civilization/HistoryGazetteer.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/knowledge/NewsIndex.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/civilization/R2EventChecks.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/testing/R2PeopleChecks.java" \
 "$ROOT/r2_wikipedia/java_probe/R2ChecksProbe.java"
"$JAVA_HOME/bin/java" -Xmx1000m -cp "$TMP/classes:$TMP/res:$ROOT/eternal/src/main/resources:$GSON" R2ChecksProbe
