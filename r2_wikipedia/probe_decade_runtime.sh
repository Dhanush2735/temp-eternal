#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JAVA_HOME="${JAVA_HOME:-/home/user/.cache/jdk17download}"
GSON="${GSON_JAR:-/home/user/.cache/r2_storage/gson-2.10.1.jar}"
PACK="${1:-$ROOT/eternal/src/main/resources/data/eternalengine/eternal/history/events_wikipedia_decades.json.gz}"
TMP="$(mktemp -d /home/user/.cache/r2_storage/decade-probe-XXXXXX)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/classes" "$TMP/res/data/eternalengine/eternal/history"
RES="$TMP/res/data/eternalengine/eternal/history"
cp "$PACK" "$RES/events_wikipedia_decades.json.gz"
printf '%s\n' '{"packs":["events_wikipedia_decades.json.gz"]}' > "$RES/index.json"
"$JAVA_HOME/bin/javac" -encoding UTF-8 -cp "$GSON" -d "$TMP/classes" \
 "$ROOT/r2_wikipedia/java_probe/com/eternalengine/civilization/HistoricalPresence.java" \
 "$ROOT/r2_wikipedia/java_probe/com/eternalengine/knowledge/KnowledgeDate.java" \
 "$ROOT/r2_wikipedia/java_probe/com/eternalengine/knowledge/DatedEvents.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/civilization/SettlementRank.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/civilization/SettlementYearEstimator.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/civilization/HistoryGazetteer.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/knowledge/NewsIndex.java" \
 "$ROOT/r2_wikipedia/java_probe/DecadeRuntimeProbe.java"
"$JAVA_HOME/bin/java" -Xmx768m -cp "$TMP/classes:$TMP/res:$GSON" DecadeRuntimeProbe
if [[ "${2:-}" == "full" ]]; then
 echo 'Testing full installed resource tree...'
 "$JAVA_HOME/bin/java" -Xmx1536m -cp "$TMP/classes:$ROOT/eternal/src/main/resources:$GSON" DecadeRuntimeProbe full
fi
