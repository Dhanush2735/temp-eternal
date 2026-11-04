#!/usr/bin/env bash
# Step 29 (C2, C3, C4, C5, C6, C28): towns through time and the ties between states (TownsProbe). Checks the two
# data files first (build_towns.py --check, build_relations.py --check).
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
SRC=$MOD/src/main/java/com/eternalengine
OUT=/home/user/.cache/wf_probe_towns
rm -rf "$OUT"; mkdir -p "$OUT"
CP="$MOD/build/classes/java/main:$(cat /home/user/.cache/wf_probe_commands/runtime_cp.txt)"
python3 /home/user/worldfill/build_towns.py --check
python3 /home/user/worldfill/build_relations.py --check
"$JDK/bin/javac" -J-Xmx400m -encoding UTF-8 -nowarn -proc:none -cp "$CP" -d "$OUT" \
  "$SRC/civilization/TownFacts.java" "$SRC/civilization/StateRelations.java" "$SRC/civilization/EventNews.java" \
  "$SRC/knowledge/LocalCards.java" "$SRC/civilization/HistoryGazetteer.java" \
  /home/user/worldfill/probes/TownsProbe.java
"$JDK/bin/java" -Xmx900m -XX:+UseSerialGC -Dfile.encoding=UTF-8 -cp "$OUT:$MOD/src/main/resources:$CP" TownsProbe
