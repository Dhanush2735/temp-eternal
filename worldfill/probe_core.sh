#!/usr/bin/env bash
# Step 14 core probe: the pure parts of the core changes (vote counting, Terra++ day rounding, the per-system
# safety net), outside the game.
# Compiles the changed sources it needs with the probe against the last Gradle build and the runtime classpath.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
SRC=/home/user/eternal/src/main/java
CLS=/home/user/eternal/build/classes/java/main
CP="$CLS:$(cat /home/user/.cache/wf_probe_commands/runtime_cp.txt)"
OUT=/tmp/ee_core_probe
rm -rf "$OUT"; mkdir -p "$OUT"
"$JDK/bin/javac" -J-Xmx400m -encoding UTF-8 -nowarn -proc:none -cp "$CP" -sourcepath "$SRC" -d "$OUT" \
  "$SRC/com/eternalengine/clock/SimulationClockManager.java" "$SRC/com/eternalengine/terrabridge/TerraTimeBridge.java" \
  "$SRC/com/eternalengine/core/SystemRunner.java" \
  /home/user/worldfill/probes/CoreProbe.java
"$JDK/bin/java" -Xmx300m -cp "$OUT:$CP" CoreProbe
