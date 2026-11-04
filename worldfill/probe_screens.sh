#!/usr/bin/env bash
# Steps 19c-19f: the news and shop checks and the trade, newspaper and map screens (probes/ScreenProbe.java) with the
# mod's real code and data, drawn with the game's own font into probes/out/screen_*.png (no server, no game needed).
# The sources are compiled with the probe (-sourcepath). Never run it while the test server runs (memory).
# Exit code 1 if a check fails.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
CPFILE=/home/user/.cache/wf_probe_commands/runtime_cp.txt
OUT=/home/user/.cache/wf_probe_screens
[ -s "$CPFILE" ] || { echo "no $CPFILE: run tools/run_test_server.sh once (or the printEeClasspath init script)"; exit 2; }
rm -rf "$OUT"; mkdir -p "$OUT"
CP="$MOD/build/classes/java/main:$MOD/src/main/resources:$(cat "$CPFILE")"
"$JDK/bin/javac" -J-Xmx350m -encoding UTF-8 -nowarn -proc:none -cp "$CP" -sourcepath "$MOD/src/main/java" -d "$OUT" \
  /home/user/worldfill/probes/TalkLayoutProbe.java /home/user/worldfill/probes/ScreenProbe.java
"$JDK/bin/java" -Xmx700m -Djava.awt.headless=true -Dfile.encoding=UTF-8 -Dsun.stdout.encoding=UTF-8 -cp "$OUT:$CP" ScreenProbe
