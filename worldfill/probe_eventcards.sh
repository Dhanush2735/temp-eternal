#!/usr/bin/env bash
# Step 28 (C8, C9, C21, known problems 39 and 40): event cards, the cause-and-effect graph, natural events, occupied and
# disputed land (EventCardsProbe). Checks the event file first (build_event_cards.py --check).
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
SRC=$MOD/src/main/java/com/eternalengine
OUT=/home/user/.cache/wf_probe_eventcards
rm -rf "$OUT"; mkdir -p "$OUT"
CP="$MOD/build/classes/java/main:$(cat /home/user/.cache/wf_probe_commands/runtime_cp.txt)"
python3 /home/user/worldfill/build_event_cards.py --check
"$JDK/bin/javac" -J-Xmx400m -encoding UTF-8 -nowarn -proc:none -cp "$CP" -d "$OUT" \
  "$SRC/knowledge/CardStore.java" "$SRC/knowledge/PlaceCards.java" "$SRC/knowledge/LocalCards.java" \
  "$SRC/civilization/EventNews.java" "$SRC/civilization/OccupiedLands.java" "$SRC/civilization/HistoryGazetteer.java" \
  /home/user/worldfill/probes/EventCardsProbe.java
"$JDK/bin/java" -Xmx900m -XX:+UseSerialGC -Dfile.encoding=UTF-8 -cp "$OUT:$MOD/src/main/resources:$CP" EventCardsProbe
