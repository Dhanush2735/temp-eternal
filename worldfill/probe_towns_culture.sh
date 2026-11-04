#!/usr/bin/env bash
# Step 33 (B9, B11, B13, B20, E14, E16, B25): what a town is made of, where and when.
#
# Checks the data files first (build_building_culture.py rebuilds the pack from the hand-written
# table and reports how much of the world each row carries), then compiles the register and its
# three dependencies against nothing but Gson -- none of them touch Minecraft -- and runs the probe,
# which answers for the 31 test places and for the places where the ranking rule was in doubt.
#
# The register is pure Java plus Gson, so this needs no Forge, no Minecraft jars and no gradle.
# It does need a JDK 17 (records): the script fetches one into .cache if it is not there.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
LIBS=/home/user/.cache/wf_libs
MOD=/home/user/eternal
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

python3 /home/user/worldfill/build_building_culture.py

rm -rf "$OUT"; mkdir -p "$OUT"
"$JDK/bin/javac" -J-Xmx400m -encoding UTF-8 -nowarn -proc:none -cp "$LIBS/gson.jar" -d "$OUT" \
  "$SRC/towns/BuildingCulture.java" "$SRC/civilization/CountryGrid.java" \
  "$SRC/civilization/SettlementRank.java" "$SRC/technology/TechnologyAtlas.java"
"$JDK/bin/javac" -J-Xmx400m -encoding UTF-8 -nowarn -proc:none -cp "$LIBS/gson.jar:$OUT" \
  -d "$OUT" /home/user/worldfill/probes/BuildingCultureProbe.java
"$JDK/bin/java" -Xmx900m -XX:+UseSerialGC -Dfile.encoding=UTF-8 \
  -cp "$OUT:$MOD/src/main/resources:$LIBS/gson.jar" BuildingCultureProbe
