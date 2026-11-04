#!/usr/bin/env bash
# Step 43 part 2 (J2, sounds of the era): the registers, compiled on their own against a
# plain JDK 17 and Gson and not through Gradle, so they run in seconds and need no Minecraft
# classpath. The mod build gets the same sources from tools/gradle_compile.sh.
#
# This one pulls in three more registers than step 42's did -- LeaderRegister (whose faith of a
# state the voice rows hang off), TechnologyAtlas (the machines) and CultureAtlas (the one faith
# vocabulary) -- and all three are Minecraft-free, so the probe still runs the very code the
# game runs.
set -euo pipefail
HERE=/home/user/worldfill
TOOLS="${TOOLS:-/home/user/.cache/tools}"   # outside the snapshot: re-fetched on demand
JDK="${JDK17:-$TOOLS/jdk17}"
GSON=$TOOLS/jars/gson.jar
if [ ! -x "$JDK/bin/javac" ]; then
  echo "fetching a JDK 17 into $JDK ..."
  mkdir -p "$JDK"
  curl -sSL -o "$TOOLS/jdk17.tar.gz" \
    "https://api.adoptium.net/v3/binary/latest/17/ga/linux/x64/jdk/hotspot/normal/eclipse" \
    && tar xzf "$TOOLS/jdk17.tar.gz" -C "$JDK" --strip-components=1 && rm -f "$TOOLS/jdk17.tar.gz"
fi
if [ ! -s "$GSON" ]; then
  echo "fetching Gson into $GSON ..."
  mkdir -p "$TOOLS/jars"
  curl -sSL -o "$GSON" "https://repo1.maven.org/maven2/com/google/code/gson/gson/2.10.1/gson-2.10.1.jar"
fi
[ -x "$JDK/bin/javac" ] || { echo "no JDK 17 at $JDK; set JDK17=..."; exit 2; }
MOD=/home/user/eternal
SRC=$MOD/src/main/java/com/eternalengine
OUT=$TOOLS/wf_probe_step43
rm -rf "$OUT"; mkdir -p "$OUT"
python3 "$HERE/build_soundscape.py" >/dev/null
"$JDK/bin/javac" -J-Xmx600m -encoding UTF-8 -nowarn -proc:none -cp "$GSON" -d "$OUT" \
  "$SRC/data/TileStore.java" "$SRC/data/TileCache.java" \
  "$SRC/civilization/CountryGrid.java" "$SRC/civilization/SocialOrder.java" \
  "$SRC/civilization/RulerRegister.java" "$SRC/civilization/LawRegister.java" \
  "$SRC/civilization/LeaderRegister.java" "$SRC/civilization/CultureAtlas.java" \
  "$SRC/civilization/SettlementRank.java" \
  "$SRC/clock/Timeline.java" \
  "$SRC/population/SettlementDensity.java" \
  "$SRC/civilization/Justice.java" "$SRC/civilization/Borders.java" \
  "$SRC/civilization/Soundscape.java" \
  "$SRC/technology/TechnologyAtlas.java" \
  "$HERE/probes/Step43Probe.java"
"$JDK/bin/java" -Xmx900m -XX:+UseSerialGC -Dfile.encoding=UTF-8 \
  -cp "$OUT:$MOD/src/main/resources:$GSON" Step43Probe
