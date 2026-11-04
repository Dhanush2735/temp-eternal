#!/usr/bin/env bash
# Step 30b (C13, C14, C17, C26, C27): reading, scripts, measures, wealth, holy places, festivals (CultureProbe). Checks
# the data first (build_culture.py --check).
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
SRC=$MOD/src/main/java/com/eternalengine
OUT=/home/user/.cache/wf_probe_culture
rm -rf "$OUT"; mkdir -p "$OUT"
CP="$MOD/build/classes/java/main:$(cat /home/user/.cache/wf_probe_commands/runtime_cp.txt)"
python3 /home/user/worldfill/build_culture.py --check
"$JDK/bin/javac" -J-Xmx400m -encoding UTF-8 -nowarn -proc:none -cp "$CP" -d "$OUT" \
  "$SRC/civilization/CultureAtlas.java" "$SRC/civilization/EventNews.java" "$SRC/knowledge/LocalCards.java" \
  /home/user/worldfill/probes/CultureProbe.java
"$JDK/bin/java" -Xmx900m -XX:+UseSerialGC -Dfile.encoding=UTF-8 -cp "$OUT:$MOD/src/main/resources:$CP" CultureProbe
