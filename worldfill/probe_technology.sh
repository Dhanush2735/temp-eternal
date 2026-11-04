#!/usr/bin/env bash
# Step 30a (C16): the technology atlas and the country grid (TechnologyProbe). Checks the two data files first
# (build_country_grid.py --check, build_technology_atlas.py --check).
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
SRC=$MOD/src/main/java/com/eternalengine
OUT=/home/user/.cache/wf_probe_technology
rm -rf "$OUT"; mkdir -p "$OUT"
CP="$MOD/build/classes/java/main:$(cat /home/user/.cache/wf_probe_commands/runtime_cp.txt)"
python3 /home/user/worldfill/build_country_grid.py --check
python3 /home/user/worldfill/build_technology_atlas.py --check
"$JDK/bin/javac" -J-Xmx400m -encoding UTF-8 -nowarn -proc:none -cp "$CP" -d "$OUT" \
  "$SRC/civilization/CountryGrid.java" "$SRC/technology/TechnologyAtlas.java" "$SRC/civilization/EventNews.java" \
  "$SRC/knowledge/LocalCards.java" "$SRC/vehicle/VehicleType.java" \
  /home/user/worldfill/probes/TechnologyProbe.java
"$JDK/bin/java" -Xmx900m -XX:+UseSerialGC -Dfile.encoding=UTF-8 -cp "$OUT:$MOD/src/main/resources:$CP" TechnologyProbe
