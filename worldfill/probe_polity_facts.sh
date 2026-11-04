#!/usr/bin/env bash
# R2-d2: can every polity the register names say its name and its years?
set -uo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"; GSON=/home/user/libs/gson-2.10.1.jar
MOD=/home/user/eternal; HERE=/home/user/worldfill; OUT=/home/user/.cache/wf_probe_polityfacts
rm -rf "$OUT"; mkdir -p "$OUT"
"$JDK/bin/javac" -J-Xmx900m -encoding UTF-8 -nowarn -proc:none -cp "$GSON" \
  -sourcepath "$HERE/stubs:$HERE/stubs_headless:$MOD/src/main/java" -d "$OUT" \
  "$HERE/probes/PolityFactsProbe.java" || { echo "COMPILE FAILED"; exit 2; }
"$JDK/bin/java" -Xmx1600m -Dfile.encoding=UTF-8 -cp "$OUT:$MOD/src/main/resources:$GSON" PolityFactsProbe
