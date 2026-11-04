#!/usr/bin/env bash
# Step 41 (D11, C11): the presence register ("who was here, and why") and the kinship register
# ("who was whose parent, and what house"). Checks the packs first, then the two Java registers.
#
# It compiles the registers on their own, against a plain JDK 17 and Gson, and not through Gradle:
# that way it runs in a few seconds and needs no Minecraft classpath. The mod build gets the same
# sources from tools/gradle_compile.sh.
set -euo pipefail
HERE=/home/user/worldfill
CACHE=/home/user/tools
JDK="${JDK17:-$CACHE/jdk17}"
[ -x "$JDK/bin/javac" ] || { echo "no JDK 17 at $JDK; set JDK17=... or run tools/gradle_compile.sh"; exit 2; }
GSON=$CACHE/jars/gson.jar
# A JDK and Gson are not part of the workspace snapshot, so fetch them if they are missing: the
# registers are plain Java 17 and need nothing else.
if [ ! -x "$JDK/bin/javac" ]; then
  echo "fetching a JDK 17 into $JDK ..."
  mkdir -p "$JDK"
  curl -sSL -o "$CACHE/jdk17.tar.gz" \
    "https://api.adoptium.net/v3/binary/latest/17/ga/linux/x64/jdk/hotspot/normal/eclipse" \
    && tar xzf "$CACHE/jdk17.tar.gz" -C "$JDK" --strip-components=1 \
    && rm -f "$CACHE/jdk17.tar.gz"
fi
if [ ! -s "$GSON" ]; then
  echo "fetching Gson into $GSON ..."
  mkdir -p "$CACHE/jars"
  curl -sSL -o "$GSON" "https://repo1.maven.org/maven2/com/google/code/gson/gson/2.10.1/gson-2.10.1.jar"
fi
[ -x "$JDK/bin/javac" ] || { echo "no JDK 17 at $JDK; set JDK17=... or run tools/gradle_compile.sh"; exit 2; }
[ -s "$GSON" ] || { echo "no Gson at $GSON"; exit 2; }
MOD=/home/user/eternal
SRC=$MOD/src/main/java/com/eternalengine
OUT=$CACHE/wf_probe_famous41
rm -rf "$OUT"; mkdir -p "$OUT"
python3 "$HERE/build_presence.py" --check
python3 "$HERE/build_kinship.py" --check
"$JDK/bin/javac" -J-Xmx600m -encoding UTF-8 -nowarn -proc:none -cp "$GSON" -d "$OUT" \
  "$SRC/data/TileStore.java" "$SRC/data/TileCache.java" \
  "$SRC/civilization/Presence.java" \
  "$SRC/civilization/Kinship.java" "$SRC/civilization/FamousChecks.java" \
  "$SRC/clock/Timeline.java" \
  "$HERE/probes/FamousStep41Probe.java"
"$JDK/bin/java" -Xmx900m -XX:+UseSerialGC -Dfile.encoding=UTF-8 \
  -cp "$OUT:$MOD/src/main/resources:$GSON" FamousStep41Probe
