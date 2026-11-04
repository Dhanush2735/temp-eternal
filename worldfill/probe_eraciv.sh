#!/usr/bin/env bash
# Board 17: nobody stands after their own civilization has fallen (EraCivProbe).
# Asks HistoricalPresence for the places that were actually played, then sweeps the world: every
# answer must be a sentinel or a civilization that is alive in that year.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
OUT=/home/user/.cache/wf_eraciv
rm -rf "$OUT"; mkdir -p "$OUT"
CP="$MOD/build/classes/java/main:$(cat /home/user/.cache/wf_probe_commands/runtime_cp.txt)"
"$JDK/bin/javac" -J-Xmx400m -encoding UTF-8 -nowarn -proc:none -cp "$CP" -d "$OUT" \
  /home/user/worldfill/probes/EraCivProbe.java
"$JDK/bin/java" -Xmx1400m -XX:+UseSerialGC -Dfile.encoding=UTF-8 \
  -cp "$OUT:$MOD/src/main/resources:$CP" EraCivProbe
