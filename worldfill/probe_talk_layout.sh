#!/usr/bin/env bash
# Step 18c: the talk box on every screen size (probes/TalkLayoutProbe.java), with text measured from Minecraft's own
# font pictures, and pictures of the box in probes/out/. Build first (tools/gradle_compile.sh). Exit code 1 if a check fails.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
CPFILE=/home/user/.cache/wf_probe_commands/runtime_cp.txt
OUT=/home/user/.cache/wf_probe_talk_layout
[ -s "$CPFILE" ] || { echo "no $CPFILE: run tools/run_test_server.sh once (or the printEeClasspath init script)"; exit 2; }
rm -rf "$OUT"; mkdir -p "$OUT"
CP="$MOD/build/classes/java/main:$MOD/src/main/resources:$(cat "$CPFILE")"
"$JDK/bin/javac" -J-Xmx300m -encoding UTF-8 -nowarn -proc:none -cp "$CP" -d "$OUT" /home/user/worldfill/probes/TalkLayoutProbe.java
"$JDK/bin/java" -Xmx500m -Djava.awt.headless=true -Dfile.encoding=UTF-8 -Dsun.stdout.encoding=UTF-8 -cp "$OUT:$CP" TalkLayoutProbe
