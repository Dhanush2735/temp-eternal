#!/usr/bin/env bash
# Step 62, "history at your feet": the reading at the plan's test places and years, compiled on
# its own against a plain JDK 17 and Gson and not through Gradle, so it runs in seconds and needs
# no Minecraft classpath. The stubs are FIRST on the sourcepath (KnowledgeDate pulls the clock);
# javac pulls HistoryGazetteer, TownFacts, RulerRegister and their registers in on their own.
# The mod build gets the same sources from tools/gradle_compile.sh.
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
SRC=$MOD/src/main/java
OUT=$TOOLS/wf_probe_here
rm -rf "$OUT"; mkdir -p "$OUT"
"$JDK/bin/javac" -J-Xmx900m -encoding UTF-8 -nowarn -proc:none -cp "$GSON" \
  -sourcepath "$HERE/stubs:$HERE/stubs_headless:$SRC" -d "$OUT" \
  "$SRC/com/eternalengine/here/HereAndNow.java" \
  "$HERE/probes/HereProbe.java"
"$JDK/bin/java" -Xmx1400m -XX:+UseSerialGC -Dfile.encoding=UTF-8 -Dsun.stdout.encoding=UTF-8 \
  -cp "$OUT:$MOD/src/main/resources:$GSON" HereProbe
