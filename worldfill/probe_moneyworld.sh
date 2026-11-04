#!/usr/bin/env bash
# Step 23a: the money of the whole world (probes/MoneyWorldProbe.java) with the mod's
# real code and data, the ruler register and the HYDE grid included (no server needed). The sources are compiled with the probe
# (-sourcepath), so it works before the Gradle build. Never run it while the test server runs (memory).
# Exit code 1 if a check fails.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
CPFILE=/home/user/.cache/wf_probe_commands/runtime_cp.txt
OUT=/home/user/.cache/wf_probe_moneyworld
[ -s "$CPFILE" ] || { echo "no $CPFILE: run tools/run_test_server.sh once (or the printEeClasspath init script)"; exit 2; }
rm -rf "$OUT"; mkdir -p "$OUT"
# Resources straight from the source tree: compileJava alone does not copy them to build/resources.
CP="$MOD/build/classes/java/main:$MOD/src/main/resources:$(cat "$CPFILE")"
"$JDK/bin/javac" -J-Xmx300m -encoding UTF-8 -nowarn -proc:none -cp "$CP" -sourcepath "$MOD/src/main/java" -d "$OUT" \
  /home/user/worldfill/probes/MoneyWorldProbe.java
"$JDK/bin/java" -Xmx500m -Dfile.encoding=UTF-8 -Dsun.stdout.encoding=UTF-8 -cp "$OUT:$CP" MoneyWorldProbe
