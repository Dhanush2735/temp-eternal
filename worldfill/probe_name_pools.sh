#!/usr/bin/env bash
# Step 17, fix B: which name list townspeople get at a place (probes/NamePoolProbe.java), with the real name database
# and the mod's own language data. Build first (tools/gradle_compile.sh). Exit code 1 if a place gets the wrong list.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
CPFILE=/home/user/.cache/wf_probe_commands/runtime_cp.txt
OUT=/home/user/.cache/wf_probe_name_pools
[ -s "$CPFILE" ] || { echo "no $CPFILE: run tools/run_test_server.sh once (or the printEeClasspath init script)"; exit 2; }
rm -rf "$OUT"; mkdir -p "$OUT"
CP="$MOD/build/classes/java/main:$MOD/src/main/resources:$(cat "$CPFILE")"   # step 30a: the resources from src (build/resources may be stale or missing)
"$JDK/bin/javac" -J-Xmx300m -encoding UTF-8 -nowarn -proc:none -cp "$CP" -d "$OUT" /home/user/worldfill/probes/NamePoolProbe.java
"$JDK/bin/java" -Xmx400m -cp "$OUT:$CP" NamePoolProbe
