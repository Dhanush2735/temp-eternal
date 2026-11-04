#!/usr/bin/env bash
# The crowd spawner's crash of 2026-10-12 outside the game: probes/CrowdBoxProbe.java runs the old and the fixed
# box of CrowdFigures.occupiedInChunk through Minecraft's own entity storage (EntitySectionStorage), at the
# user's chunk in Hyderabad, at chunk 0,0 and near the world border. Build first (tools/gradle_compile.sh); the
# Minecraft classpath file comes from tools/run_test_server.sh or the printEeClasspath init script.
# Exit code 1 if a check fails.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
CPFILE=/home/user/.cache/wf_probe_commands/runtime_cp.txt
OUT=/home/user/.cache/wf_probe_crowd_box
[ -s "$CPFILE" ] || { echo "no $CPFILE: run tools/run_test_server.sh once (or the printEeClasspath init script)"; exit 2; }
rm -rf "$OUT"; mkdir -p "$OUT"
CP="$MOD/build/classes/java/main:$(cat "$CPFILE")"
"$JDK/bin/javac" -J-Xmx300m -encoding UTF-8 -nowarn -proc:none -cp "$CP" -d "$OUT" /home/user/worldfill/probes/CrowdBoxProbe.java
"$JDK/bin/java" -Xmx300m -cp "$OUT:$CP" CrowdBoxProbe
