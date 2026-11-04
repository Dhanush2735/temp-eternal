#!/usr/bin/env bash
# /ee check all through Minecraft's own command dispatcher, outside the game: the real command tree
# (EeOperationalCheck.node()) run as an operator with no player and no server (probes/CommandHarness.java).
# Build first: tools/gradle_compile.sh. The Minecraft/Forge classpath is asked from Gradle once.
#
#   probe_commands.sh                         the default set below
#   probe_commands.sh "ee check all"          any commands, without the slash; "!" in front = as a non-operator
#
# Expected without a server: section 1 fails ("the simulation is not running"); everything else runs.
# Since step 15 the check writes no file: every line goes to the log, marked [EE check] (here: the console
# output below and $OUT/logs/latest.log); the harness's "chat" gets two short lines.
# Since step 10 there are no single checks: "ee check list", "ee check places", "ee check goto 3" must be
# syntax errors.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
OUT=/home/user/.cache/wf_probe_commands
CPFILE="$OUT/runtime_cp.txt"
mkdir -p "$OUT/classes"
if [ ! -s "$CPFILE" ] || [ "$MOD/build.gradle" -nt "$CPFILE" ]; then
  cat > "$OUT/printcp.gradle" <<'GRADLE'
allprojects {
    afterEvaluate {
        tasks.register('printEeClasspath') {
            doLast {
                new File(project.findProperty('cpOut').toString()).text = sourceSets.main.runtimeClasspath.asPath
            }
        }
    }
}
GRADLE
  (cd "$MOD" && JAVA_HOME="$JDK" GRADLE_USER_HOME=/home/user/.cache/gradle sh gradlew -q --project-cache-dir /home/user/.cache/eternal_project_cache -I "$OUT/printcp.gradle" \
      printEeClasspath -PcpOut="$CPFILE" --no-daemon --console=plain \
      -Dorg.gradle.jvmargs="-Xmx560m -XX:+UseSerialGC -XX:MaxMetaspaceSize=320m" -Dorg.gradle.workers.max=1)
fi
CP="$MOD/build/classes/java/main:$MOD/src/main/resources:$(cat "$CPFILE")"
"$JDK/bin/javac" -nowarn -encoding UTF-8 -cp "$CP" -d "$OUT/classes" /home/user/worldfill/probes/CommandHarness.java
if [ $# -eq 0 ]; then
  set -- "!ee check all" "ee check list" "ee check places" "ee check goto 3" "ee check all extra" "ee check all"
fi
# Run from the scratch folder: Minecraft's logger writes logs/latest.log into the working directory.
cd "$OUT"
"$JDK/bin/java" -Xmx900m -Dfile.encoding=UTF-8 -cp "$OUT/classes:$CP" CommandHarness "$@" 2>&1 | grep -v "Advanced terminal"
