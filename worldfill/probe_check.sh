#!/usr/bin/env bash
# The history part of /ee check, outside the game: HistoryChecks against the mod's compiled classes and
# resources (build first: tools/gradle_compile.sh). Arguments: part ids (data places rulers talk events
# index coverage speed); none = all. Exit code 1 if a check fails.
#
# FAST=1 recompiles only the civilization sources newer than the Gradle classes (for editing the checks
# without a Gradle run); the in-game build is always the Gradle one.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
GSON=/home/user/libs/gson-2.10.1.jar
MOD=/home/user/eternal
OUT=/home/user/.cache/wf_probe_check
CLS="$MOD/build/classes/java/main"
rm -rf "$OUT"; mkdir -p "$OUT/fast" "$OUT/probe"
CP="$CLS:$GSON"
# step 26: the key (core/WorldKey) names Minecraft types, so the game's runtime classpath goes on too when known
RCP=/home/user/.cache/wf_probe_commands/runtime_cp.txt
if [ -s "$RCP" ]; then CP="$CP:$(cat "$RCP")"; fi
if [ "${FAST:-0}" = "1" ]; then
  SRC=$(find "$MOD/src/main/java/com/eternalengine/civilization" "$MOD/src/main/java/com/eternalengine/data" \
             "$MOD/src/main/java/com/eternalengine/core/WorldKey.java" "$MOD/src/main/java/com/eternalengine/core/WorldQuery.java" \
             -name '*.java' -newer "$CLS/com/eternalengine/civilization/HistoryGazetteer.class" 2>/dev/null || true)
  if [ -n "$SRC" ]; then
    "$JDK/bin/javac" -J-Xmx500m -encoding UTF-8 -nowarn -proc:none -cp "$CP" -d "$OUT/fast" $SRC
    CP="$OUT/fast:$CP"
  fi
fi
"$JDK/bin/javac" -encoding UTF-8 -nowarn -cp "$CP" -d "$OUT/probe" /home/user/worldfill/probes/CheckProbe.java
"$JDK/bin/java" -Xmx900m -Dfile.encoding=UTF-8 -cp "$OUT/probe:$MOD/src/main/resources:$CP" CheckProbe "$@"
