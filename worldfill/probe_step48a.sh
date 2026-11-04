#!/usr/bin/env bash
# Step 48 part 2 (G1): what counts as a change. Runs the real ChangeRecord and Chronicler against a
# plain JDK 17, no Minecraft.
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
OUT=$TOOLS/wf_probe_step48a
rm -rf "$OUT"; mkdir -p "$OUT"
"$JDK/bin/javac" -J-Xmx900m -encoding UTF-8 -nowarn -proc:none -cp "$GSON" \
  -sourcepath "$SRC:$HERE/stubs" -d "$OUT" \
  "$HERE/stubs/org/slf4j/Logger.java" \
  "$HERE/stubs/com/mojang/logging/LogUtils.java" \
  "$HERE/stubs/javax/annotation/Nullable.java" \
  "$HERE/probes/Step48ChangeProbe.java"
"$JDK/bin/java" -Xmx1400m -XX:+UseSerialGC -Dfile.encoding=UTF-8 -Dsun.stdout.encoding=UTF-8 \
  -cp "$OUT:$MOD/src/main/resources:$GSON" Step48ChangeProbe
