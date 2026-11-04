#!/usr/bin/env bash
# Step 18d: the world calendar (probes/CalendarProbe.java): the date rules on made-up Minecraft times, with the
# mod's real WorldCalendar and TerraTimeBridge code (no server needed). Build first (tools/gradle_compile.sh).
# Exit code 1 if a check fails.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
CPFILE=/home/user/.cache/wf_probe_commands/runtime_cp.txt
OUT=/home/user/.cache/wf_probe_calendar
[ -s "$CPFILE" ] || { echo "no $CPFILE: run tools/run_test_server.sh once (or the printEeClasspath init script)"; exit 2; }
rm -rf "$OUT"; mkdir -p "$OUT"
# Resources straight from the source tree: compileJava alone does not copy them to build/resources.
CP="$MOD/build/classes/java/main:$MOD/src/main/resources:$(cat "$CPFILE")"
"$JDK/bin/javac" -J-Xmx300m -encoding UTF-8 -nowarn -proc:none -cp "$CP" -d "$OUT" /home/user/worldfill/probes/CalendarProbe.java
"$JDK/bin/java" -Xmx500m -Dfile.encoding=UTF-8 -Dsun.stdout.encoding=UTF-8 -cp "$OUT:$CP" CalendarProbe
