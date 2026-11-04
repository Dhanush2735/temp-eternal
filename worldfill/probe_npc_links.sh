#!/usr/bin/env bash
# Turn 50: which civilization villagers in 40 towns belong to, and whether the money/food/faith
# systems (civilization table) have real numbers for it. Build first: tools/gradle_compile.sh.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
GSON=/home/user/libs/gson-2.10.1.jar
MOD=/home/user/eternal
OUT=/home/user/.cache/wf_probe_npc_links
mkdir -p "$OUT"
CP="$MOD/build/classes/java/main:$GSON"
if [ -f /home/user/.cache/wf_probe_commands/runtime_cp.txt ]; then CP="$CP:$(cat /home/user/.cache/wf_probe_commands/runtime_cp.txt)"; fi
"$JDK/bin/javac" -encoding UTF-8 -nowarn -cp "$CP" -d "$OUT" /home/user/worldfill/probes/NpcLinkProbe.java
"$JDK/bin/java" -Xmx700m -Dfile.encoding=UTF-8 -cp "$OUT:$MOD/build/classes/java/main:$MOD/src/main/resources:$CP" NpcLinkProbe
