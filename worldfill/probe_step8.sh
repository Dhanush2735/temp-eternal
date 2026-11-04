#!/usr/bin/env bash
# Step 8 probe. REPAIRED 2026-10-22: compiled against build/classes/java/main (Gradle-only) before;
# now uses -sourcepath + stubs, like probe_here.sh, so it runs without a Minecraft classpath.
set -uo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"; GSON=/home/user/libs/gson-2.10.1.jar
MOD=/home/user/eternal; HERE=/home/user/worldfill; OUT=/home/user/.cache/wf_probe_step8
rm -rf "$OUT"; mkdir -p "$OUT"
"$JDK/bin/javac" -J-Xmx900m -encoding UTF-8 -nowarn -proc:none -cp "$GSON" \
  -sourcepath "$HERE/stubs:$HERE/stubs_headless:$MOD/src/main/java" -d "$OUT" \
  "$HERE/probes/Step8Probe.java" || { echo "COMPILE FAILED"; exit 2; }
"$JDK/bin/java" -Xmx1400m -Dfile.encoding=UTF-8 -cp "$OUT:$MOD/src/main/resources:$GSON" Step8Probe "$@"
