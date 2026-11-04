#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JAVA_HOME="${JAVA_HOME:-/home/user/.cache/jdk17download}"
GSON="${GSON_JAR:-/home/user/.cache/r2_storage/gson-2.10.1.jar}"
PACK="${1:-$ROOT/eternal/src/main/resources/data/eternalengine/eternal/history/events_wikipedia.json.gz}"
TMP="$(mktemp -d /home/user/.cache/r2_storage/event-probe-XXXXXX)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/classes" "$TMP/res/data/eternalengine/eternal/history"
RES="$TMP/res/data/eternalengine/eternal/history"
cp "$PACK" "$RES/events_wikipedia.json.gz"
python3 - "$RES" <<'PY'
import gzip,json,sys
from pathlib import Path
p=Path(sys.argv[1]);p.joinpath('index.json').write_text(json.dumps({'packs':['events_wikipedia.json.gz','events_wikipedia_decades.json.gz','events_wikipedia_regional.json.gz']}))
for name,title,start,end,lat,lon,confidence in [
 ('events_wikipedia_decades.json.gz','synthetic decade',2750,2751,-82,42,'wikipedia_coord'),
 ('events_wikipedia_regional.json.gz','synthetic regional',2750,2751,-80,41,'wikipedia_region'),
 ('deccan_events.json.gz','synthetic hand inclusive',2800,2803,-70,20,'gazetteer_1909')]:
 doc={'id':name,'sites':[],'events':[{'id':title,'name':title,'start':start,'end':end,'lat':lat,'lon':lon,'radiusKm':20,'kind':'incident','effect':'note','confidence':confidence}]}
 with gzip.open(p/name,'wt',encoding='utf8') as f:json.dump(doc,f)
PY
"$JAVA_HOME/bin/javac" -encoding UTF-8 -cp "$GSON" -d "$TMP/classes" \
 "$ROOT/r2_wikipedia/java_probe/com/eternalengine/civilization/HistoricalPresence.java" \
 "$ROOT/r2_wikipedia/java_probe/com/eternalengine/knowledge/KnowledgeDate.java" \
 "$ROOT/r2_wikipedia/java_probe/com/eternalengine/knowledge/DatedEvents.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/civilization/SettlementRank.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/civilization/SettlementYearEstimator.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/civilization/HistoryGazetteer.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/knowledge/NewsIndex.java" \
 "$ROOT/r2_wikipedia/java_probe/EventRuntimeProbe.java"
"$JAVA_HOME/bin/java" -Xmx768m -cp "$TMP/classes:$TMP/res:$GSON" EventRuntimeProbe
if [[ "${2:-}" == "full" ]]; then
  echo 'Testing the full current resources (not the staged copy)...'
  "$JAVA_HOME/bin/java" -Xmx1536m -cp "$TMP/classes:$ROOT/eternal/src/main/resources:$GSON" EventRuntimeProbe full
fi
