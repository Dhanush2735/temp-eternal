#!/usr/bin/env bash
# Step 26 (I6): memory and load time of every data register, from the mod's own loaders. Build first
# (tools/gradle_compile.sh). Usage: probe_memory.sh [extra java sources compiled with the probe ...]
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
OUT=/home/user/.cache/wf_probe_memory
rm -rf "$OUT"; mkdir -p "$OUT"
CP="$MOD/build/classes/java/main:$(cat /home/user/.cache/wf_probe_commands/runtime_cp.txt)"
"$JDK/bin/javac" -J-Xmx400m -encoding UTF-8 -nowarn -proc:none -cp "$CP" -d "$OUT" "$@" /home/user/worldfill/probes/MemoryProbe.java
"$JDK/bin/java" -Xmx900m -XX:+UseSerialGC -Dfile.encoding=UTF-8 -cp "$OUT:$MOD/src/main/resources:$CP" MemoryProbe
