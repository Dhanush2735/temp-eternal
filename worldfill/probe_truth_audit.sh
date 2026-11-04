#!/usr/bin/env bash
# S1: the truth audit pilot - who does the register say ruled here, and is it true?
set -uo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"; GSON=/home/user/libs/gson-2.10.1.jar
MOD=/home/user/eternal; HERE=/home/user/worldfill; OUT=/home/user/.cache/wf_probe_truth
rm -rf "$OUT"; mkdir -p "$OUT"
"$JDK/bin/javac" -J-Xmx900m -encoding UTF-8 -nowarn -proc:none -cp "$GSON" \
  -sourcepath "$HERE/stubs:$HERE/stubs_headless:$MOD/src/main/java" -d "$OUT" \
  "$HERE/probes/TruthAuditProbe.java" || { echo "COMPILE FAILED"; exit 2; }
"$JDK/bin/java" -Xmx1600m -Dfile.encoding=UTF-8 -cp "$OUT:$MOD/src/main/resources:$GSON" TruthAuditProbe
