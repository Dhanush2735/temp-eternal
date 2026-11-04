#!/usr/bin/env bash
# A syntax gate for Java the Gradle build cannot reach from here.
#
# This workspace has no Gradle cache and no Minecraft jars, so most of the mod cannot be compiled.
# javac reports PARSE errors before it resolves any symbol, so a compile with an empty classpath
# still catches a missing brace, a stray semicolon, an unclosed string or a bad switch label. It
# does NOT catch a wrong type, a missing method or a bad import: those stay "cannot find symbol"
# and are filtered out. Weak, but far better than nothing.
#
# TWO LESSONS IT LEARNED THE HARD WAY (step 46 part 6):
#
#  1. It used to check a fixed list of ten files left over from step 37. Step 46 parts 2-6 added
#     Vehicles, Traffic, VehicleMods, VehicleModGate and others, none of which was on the list, so
#     "no syntax errors" was being reported about files that had never been seen. A gate that
#     watches a fixed list stops watching when the project moves. It now checks EVERY file.
#  2. It used to run javac once per file, which is one dependency resolution per file and took
#     over half an hour for the whole mod. It now runs ONCE and attributes each diagnostic to its
#     file, which is the same answer in about a minute.
#
# Usage: ./syntax_gate.sh [file.java ...]      exit 1 on any syntax error
set -uo pipefail
JDK="${JDK17:-/home/user/.cache/jdk-17.0.20.1+1}"
MOD=/home/user/eternal
LOG=$(mktemp)
OUT=$(mktemp -d)
trap 'rm -rf "$OUT"; rm -f "$LOG"' EXIT

if [ ! -x "$JDK/bin/javac" ]; then JDK=/home/user/.cache/jdk17; fi
if [ ! -x "$JDK/bin/javac" ]; then
  echo "no JDK: run probe_calendars.sh once to provision one"; exit 2
fi

if [ "$#" -eq 0 ]; then
  mapfile -t FILES < <(find "$MOD/src/main/java" -name '*.java' | sort)
  set -- "${FILES[@]}"
fi
echo "checking $# files"

# The shapes of a parse error. "cannot find symbol", "package ... does not exist" and
# "cannot access" are NOT syntax and are expected with no Minecraft on the classpath.
SYNTAX='expected|illegal|reached end of file|not a statement|unclosed|class, interface, enum, or record|invalid method declaration|orphaned|duplicate class|unexpected type|is already defined|unreachable statement'

"$JDK/bin/javac" -J-Xmx1200m -Xmaxerrs 200000 -nowarn -proc:none -encoding UTF-8 -d "$OUT" \
  -sourcepath "$MOD/src/main/java" "$@" > "$LOG" 2>&1

# A syntax error is printed as  <file>:<line>: error: <message>
bad=0
while IFS= read -r line; do
  msg="${line#*error: }"
  if printf '%s' "$msg" | grep -qE "$SYNTAX"; then
    echo "SYNTAX  ${line#$MOD/src/main/java/}"
    bad=1
  fi
done < <(grep -E ': error: ' "$LOG")

total=$(grep -cE ': error: ' "$LOG" || true)
echo
if [ "$bad" -eq 0 ]; then
  echo "no syntax errors  ($total diagnostics, all unresolved symbols - expected without Minecraft jars)"
else
  echo "SYNTAX ERRORS above  ($total diagnostics in total)"
fi
exit "$bad"
