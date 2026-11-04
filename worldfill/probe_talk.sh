#!/usr/bin/env bash
# Talk probe. REPAIRED 2026-10-22: same -sourcepath change as probe_step8.sh.
set -uo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"; GSON=/home/user/libs/gson-2.10.1.jar
MOD=/home/user/eternal; HERE=/home/user/worldfill; OUT=/home/user/.cache/wf_probe_talk
rm -rf "$OUT"; mkdir -p "$OUT"
"$JDK/bin/javac" -J-Xmx900m -encoding UTF-8 -nowarn -proc:none -cp "$GSON" \
  -sourcepath "$HERE/stubs:$HERE/stubs_headless:$MOD/src/main/java" -d "$OUT" \
  "$HERE/probes/TalkProbe.java" || { echo "COMPILE FAILED"; exit 2; }
"$JDK/bin/java" -Xmx1400m -Dfile.encoding=UTF-8 -cp "$OUT:$MOD/src/main/resources:$GSON" TalkProbe "$@"
