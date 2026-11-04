#!/usr/bin/env bash
# Step 24: Minecraft's trade screen with townspeople (probes/TradeProbe.java), with the mod's real code and data: the
# rules of the two slots, every money paying from a day's pay, small change, selling, changing any amount, bigger and
# smaller pieces, and pictures of the screen drawn with the game's own pictures and font (probes/out/screen_trade_*.png,
# copies in pictures/). No server, no game needed. Never run it while the test server runs (memory).
# Exit code 1 if a check fails.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
CPFILE=/home/user/.cache/wf_probe_commands/runtime_cp.txt
OUT=/home/user/.cache/wf_probe_trade
[ -s "$CPFILE" ] || { echo "no $CPFILE: run tools/run_test_server.sh once (or the printEeClasspath init script)"; exit 2; }
rm -rf "$OUT"; mkdir -p "$OUT"
CP="$MOD/build/classes/java/main:$MOD/src/main/resources:$(cat "$CPFILE")"
"$JDK/bin/javac" -J-Xmx350m -encoding UTF-8 -nowarn -proc:none -cp "$CP" -sourcepath "$MOD/src/main/java" -d "$OUT" \
  /home/user/worldfill/probes/TalkLayoutProbe.java /home/user/worldfill/probes/ScreenProbe.java \
  /home/user/worldfill/probes/TradeProbe.java
"$JDK/bin/java" -Xmx700m -Djava.awt.headless=true -Dfile.encoding=UTF-8 -Dsun.stdout.encoding=UTF-8 -cp "$OUT:$CP" TradeProbe
