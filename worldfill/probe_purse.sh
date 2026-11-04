#!/usr/bin/env bash
# Step 19a: the money table and the purse (probes/PurseProbe.java) with the mod's real code and data, the ruler
# register included (no server needed). Build first (tools/gradle_compile.sh); the money package is also compiled
# straight from the sources, so a quick check works before the Gradle build. Exit code 1 if a check fails.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
CPFILE=/home/user/.cache/wf_probe_commands/runtime_cp.txt
OUT=/home/user/.cache/wf_probe_purse
[ -s "$CPFILE" ] || { echo "no $CPFILE: run tools/run_test_server.sh once (or the printEeClasspath init script)"; exit 2; }
rm -rf "$OUT"; mkdir -p "$OUT"
# Resources straight from the source tree: compileJava alone does not copy them to build/resources.
CP="$MOD/build/classes/java/main:$MOD/src/main/resources:$(cat "$CPFILE")"
"$JDK/bin/javac" -J-Xmx300m -encoding UTF-8 -nowarn -proc:none -cp "$CP" -sourcepath "$MOD/src/main/java" -d "$OUT" \
  /home/user/worldfill/probes/PurseProbe.java
"$JDK/bin/java" -Xmx500m -Dfile.encoding=UTF-8 -Dsun.stdout.encoding=UTF-8 -cp "$OUT:$CP" PurseProbe
