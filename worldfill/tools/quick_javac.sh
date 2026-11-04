#!/usr/bin/env bash
# Quick type check of changed mod sources (seconds instead of a Gradle build): compiles the given .java files
# against the last Gradle build (build/classes) and the mod's runtime classpath into a throw-away folder.
# It proves the files compile together; the real build is still tools/gradle_compile.sh.
#
#   tools/quick_javac.sh core/SimulationEngine.java clock/SimulationClockManager.java ...
#   (paths relative to eternal/src/main/java/com/eternalengine, or absolute)
#
# Needs ~/.cache/wf_probe_commands/runtime_cp.txt (written by tools/run_test_server.sh's first run, or by the
# printEeClasspath Gradle init script it contains).
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
SRC=/home/user/eternal/src/main/java/com/eternalengine
CLS=/home/user/eternal/build/classes/java/main
CPFILE=/home/user/.cache/wf_probe_commands/runtime_cp.txt
OUT=/tmp/ee_quick_javac
[ -s "$CPFILE" ] || { echo "no $CPFILE: run tools/run_test_server.sh once (or the printEeClasspath init script)"; exit 2; }
files=()
for f in "$@"; do
  case "$f" in
    /*) files+=("$f") ;;
    *) files+=("$SRC/$f") ;;
  esac
done
rm -rf "$OUT"; mkdir -p "$OUT"
"$JDK/bin/javac" -J-Xmx400m -encoding UTF-8 -nowarn -proc:none -implicit:none \
  -cp "$CLS:$(cat "$CPFILE")" -sourcepath /home/user/eternal/src/main/java -d "$OUT" "${files[@]}"
echo "quick javac OK (${#files[@]} files)"
rm -rf "$OUT"
