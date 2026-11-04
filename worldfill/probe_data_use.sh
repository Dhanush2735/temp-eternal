#!/usr/bin/env bash
# Data-use check (step 13): how much of the history data reaches a player, measured with the mod's own
# lookup code.
#
# REPAIRED 2026-10-22: this used to compile against build/classes/java/main, which only exists after
# a Gradle build, so it could not run here at all and its coverage was silently lost. It now uses the
# -sourcepath pattern probe_here.sh uses: javac pulls in the real classes it needs, the stubs cover
# only what cannot exist outside Minecraft (Forge, Level, a CivilizationManager).
set -uo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
GSON=/home/user/libs/gson-2.10.1.jar
MOD=/home/user/eternal
HERE=/home/user/worldfill
OUT=/home/user/.cache/data_use
mkdir -p "$OUT/probe"
[ -f "$OUT/points.tsv" ] || python3 "$HERE/data_use_sample.py" 1500
"$JDK/bin/javac" -J-Xmx900m -encoding UTF-8 -nowarn -proc:none -cp "$GSON" \
  -sourcepath "$HERE/stubs:$HERE/stubs_headless:$MOD/src/main/java" -d "$OUT/probe" \
  "$HERE/probes/DataUseProbe.java" || { echo "COMPILE FAILED"; exit 2; }
"$JDK/bin/java" -Xmx1400m -Dfile.encoding=UTF-8 -cp "$OUT/probe:$GSON:$MOD/src/main/resources" \
  DataUseProbe "$OUT/points.tsv"
