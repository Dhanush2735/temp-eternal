#!/usr/bin/env bash
# Step 34 (B12 roads, B14 railways, B15 waterways, B18 industry, B24 what lies under the ground,
# B26 rest houses): rebuild the three packs, compile the three registers against nothing but Gson,
# and run the probe, which answers the 31 test places in their own years and checks the gate.
#
# The registers are pure Java plus Gson, so this needs no Forge, no Minecraft jars and no gradle.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
LIBS=/home/user/.cache/wf_libs
MOD=/home/user/eternal
REPORT=/home/user/worldfill/logs/step34_ways_report.txt
SRC=$MOD/src/main/java/com/eternalengine
OUT=/home/user/.cache/wf_bc

if [ ! -x "$JDK/bin/javac" ]; then
  echo "fetching a JDK 17 into $JDK ..."
  mkdir -p "$JDK"
  curl -sL --retry 3 -o /tmp/jdk17.tar.gz \
    "https://api.adoptium.net/v3/binary/latest/17/ga/linux/x64/jdk/hotspot/normal/eclipse"
  tar xzf /tmp/jdk17.tar.gz -C "$JDK" --strip-components=1
fi
mkdir -p "$LIBS"
[ -f "$LIBS/gson.jar" ] || curl -sL -o "$LIBS/gson.jar" \
  https://repo1.maven.org/maven2/com/google/code/gson/gson/2.10.1/gson-2.10.1.jar

# the packs: the works and the minerals from what is on disk, the grid from the OpenHistoricalMap
# tiles fetched so far (it is rebuilt as the fetch goes on)
# The build needs the 122,080 Wikidata rows fetched in part 2 (build/ways/raw, 100 MB+, and build/
# is not kept between sessions). Like the minerals pack below, when the source is absent the pack
# that ships is checked and left alone, instead of the whole probe dying on a FileNotFoundError
# (found by the full sweep of 2026-10-23, marking board 10).
if [ -f /home/user/worldfill/build/ways/raw/labels.json ]; then
  python3 /home/user/worldfill/build_ways_works.py
else
  echo "  (no raw ways fetch on disk: checking the ways pack that ships; rebuild with"
  echo "   python3 worldfill/fetch_ways_wd.py --fetch --labels)"
fi
python3 /home/user/worldfill/build_ways_works.py --check
# the minerals pack needs the 137 MB USGS file, which is not kept between runs; without it the
# pack already in the mod is checked and left alone
if [ -f /home/user/worldfill/build/minerals/raw/mrds.csv ]; then
  python3 /home/user/worldfill/build_minerals.py
fi
python3 /home/user/worldfill/build_minerals.py --check
# The grid is assembled from build/ohm/tiles and build/ways/raw; with neither on disk the builder
# now refuses (guard in build_ways_grid.py) rather than replacing the shipped pack with roads only.
if [ -d /home/user/worldfill/build/ohm/tiles ] || [ -f /home/user/worldfill/build/ways/raw/labels.json ]; then
  python3 /home/user/worldfill/build_ways_grid.py
else
  echo "  (no OHM tiles or ways rows on disk: checking the grid that ships)"
fi
python3 /home/user/worldfill/build_ways_grid.py --check

rm -rf "$OUT"; mkdir -p "$OUT"
"$JDK/bin/javac" -J-Xmx600m -encoding UTF-8 -nowarn -proc:none -cp "$LIBS/gson.jar" -d "$OUT" \
  "$SRC/civilization/WaysGrid.java" \
  "$SRC/civilization/WaysWorks.java" \
  "$SRC/civilization/Minerals.java"
"$JDK/bin/javac" -J-Xmx600m -encoding UTF-8 -nowarn -proc:none -cp "$LIBS/gson.jar:$OUT" \
  -d "$OUT" /home/user/worldfill/probes/WaysProbe.java

# the public hook needs more of the mod than the registers do: TerraOsmBridge pulls in the logger,
# the config, one coordinate check and the famous buildings of step 32. Five stubs cover the parts
# that are Minecraft's; none of them touches dating or the answer.
"$JDK/bin/javac" -J-Xmx600m -encoding UTF-8 -nowarn -proc:none -cp "$LIBS/gson.jar:$OUT" \
  -sourcepath "/home/user/worldfill/probes/buildings/stubs:$SRC/../.." -d "$OUT" \
  "$SRC/buildings/FamousBuildings.java" \
  "$SRC/technology/TechnologyAtlas.java" \
  "$SRC/civilization/SettlementRank.java" \
  "$SRC/civilization/CountryGrid.java" \
  "$SRC/terrabridge/TerraOsmBridge.java" \
  /home/user/worldfill/probes/WaysHookProbe.java 2>&1 | grep -vE "^Note:|warning" | head -20 || true

echo "STEP 34 (B12, B14, B15, B18, B24, B26) - roads, railways, waterways, industry, minerals" \
  > "$REPORT"
echo "run: $(date -u '+%Y-%m-%d %H:%M UTC')" >> "$REPORT"
for f in ways.grid.gz ways_works.json.gz minerals.json.gz; do
  echo "pack: $f $(stat -c %s "$MOD/src/main/resources/data/eternalengine/eternal/history/$f") bytes" \
    >> "$REPORT"
done

echo "=== the registers ===" | tee -a "$REPORT"
"$JDK/bin/java" -Xmx1200m -XX:+UseSerialGC -Dfile.encoding=UTF-8 \
  -cp "$OUT:$MOD/src/main/resources:$LIBS/gson.jar" WaysProbe 2>&1 | tee -a "$REPORT"
reg=${PIPESTATUS[0]}

echo
echo "=== the Terra++ hook ===" | tee -a "$REPORT"
"$JDK/bin/java" -Xmx1200m -XX:+UseSerialGC -Dfile.encoding=UTF-8 \
  -cp "$OUT:$MOD/src/main/resources:$LIBS/gson.jar" WaysHookProbe 2>&1 | tee -a "$REPORT"
hook=${PIPESTATUS[0]}

echo
echo "report: $REPORT"
[ "$reg" -eq 0 ] && [ "$hook" -eq 0 ]
