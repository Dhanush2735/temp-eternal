#!/usr/bin/env bash
# Step 51 part 2 (G8): a branch saved as its differences from its parent.
# ChangeRecord and the town pack against a plain JDK 17 and Gson, no Minecraft.
#
# NOTE: stubs_headless comes first in the sourcepath so knowledge/KnowledgeDate compiles without the
# Minecraft clock; see the comment in stubs_headless/com/eternalengine/clock/SimulationClockManager.java.
# NOTE: must use $JDK17/bin/javac, not the system javac: the system one predates records.
set -euo pipefail
HERE=/home/user/worldfill
TOOLS="${TOOLS:-/home/user/.cache/tools}"
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
SRC=$MOD/src/main/java
OUT=$TOOLS/wf_probe_step54a
rm -rf "$OUT"; mkdir -p "$OUT"
"$JDK/bin/javac" -J-Xmx900m -encoding UTF-8 -nowarn -proc:none -cp "$GSON" \
  -sourcepath "$HERE/stubs_headless:$SRC:$HERE/stubs" -d "$OUT" \
  "$HERE/stubs/org/slf4j/Logger.java" \
  "$HERE/stubs/com/mojang/logging/LogUtils.java" \
  "$HERE/stubs/javax/annotation/Nullable.java" \
  "$HERE/probes/Step54LandProbe.java"
"$JDK/bin/java" -Xmx1400m -XX:+UseSerialGC -Dfile.encoding=UTF-8 -Dsun.stdout.encoding=UTF-8 \
  -cp "$OUT:$MOD/src/main/resources:$GSON" Step54LandProbe
