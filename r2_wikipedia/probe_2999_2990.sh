#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; JAVA_HOME="${JAVA_HOME:-/tmp/eternal-java17}"; GSON="${GSON_JAR:-$ROOT/tools/jars/gson.jar}"
TMP="$(mktemp -d /tmp/eternal-2980-probe-XXXXXX)";trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/classes" "$TMP/res/data/eternalengine/eternal/history"
if [[ "${1:-}" == stage ]]; then cp /home/user/.cache/r2_storage/2999_2990_context_stage/events_wikipedia_regional.json.gz "$TMP/res/data/eternalengine/eternal/history/"; fi
"$JAVA_HOME/bin/javac" -encoding UTF-8 -cp "$GSON" -d "$TMP/classes" \
 "$ROOT/r2_wikipedia/java_probe/com/eternalengine/civilization/HistoricalPresence.java" \
 "$ROOT/r2_wikipedia/java_probe/com/eternalengine/knowledge/KnowledgeDate.java" \
 "$ROOT/r2_wikipedia/java_probe/com/eternalengine/knowledge/DatedEvents.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/civilization/SettlementRank.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/civilization/SettlementYearEstimator.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/civilization/HistoryGazetteer.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/knowledge/NewsIndex.java" \
 "$ROOT/r2_wikipedia/java_probe/Batch2999Probe.java"
"$JAVA_HOME/bin/java" -Xmx1536m -cp "$TMP/classes:$TMP/res:$ROOT/eternal/src/main/resources:$GSON" Batch2999Probe
