#!/usr/bin/env bash
# Board 17b: the same rule, applied to people who are already in the world (RepairProbe).
# Asks WhoBelongsHere to put right a person carrying a civilization that did not stand that year,
# and checks that names already correct are left alone and the repair never leaves anyone outside their years.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
OUT=/home/user/.cache/wf_repair
rm -rf "$OUT"; mkdir -p "$OUT"
CP="$MOD/build/classes/java/main:$(cat /home/user/.cache/wf_probe_commands/runtime_cp.txt)"
"$JDK/bin/javac" -J-Xmx400m -encoding UTF-8 -nowarn -proc:none -cp "$CP" -d "$OUT" \
  /home/user/worldfill/probes/RepairProbe.java
"$JDK/bin/java" -Xmx1400m -XX:+UseSerialGC -Dfile.encoding=UTF-8 \
  -cp "$OUT:$MOD/src/main/resources:$CP" RepairProbe
