#!/usr/bin/env bash
# Step 26 (A4): the famous people from tiles against the master file: the same answers at the world sample and the
# test places in 14 years, plus memory and time. Rebuild the tiles first if the master changed (build_tiles.py).
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
SRC=$MOD/src/main/java/com/eternalengine
OUT=/home/user/.cache/wf_probe_tiles
rm -rf "$OUT"; mkdir -p "$OUT"
CP="$MOD/build/classes/java/main:$(cat /home/user/.cache/wf_probe_commands/runtime_cp.txt)"
python3 /home/user/worldfill/build_tiles.py --check
"$JDK/bin/javac" -J-Xmx400m -encoding UTF-8 -nowarn -proc:none -cp "$CP" -d "$OUT" \
  "$SRC/data/TileStore.java" "$SRC/data/TileCache.java" "$SRC/civilization/FamousPeople.java" \
  "$SRC/civilization/RulerRegister.java" /home/user/worldfill/probes/TilesProbe.java
"$JDK/bin/java" -Xmx900m -XX:+UseSerialGC -Dfile.encoding=UTF-8 -cp "$OUT:$MOD/src/main/resources:$CP" TilesProbe
