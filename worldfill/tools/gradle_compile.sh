#!/usr/bin/env bash
# Compile the whole mod (gradlew compileJava) inside this 2 GB sandbox without freezing it.
#
# ForgeGradle forks helper JVMs (renamer, access transformer) next to the Gradle daemon; the
# first attempt on 2026-10-11 ran out of memory and froze the sandbox. This script caps every
# JVM's heap and runs a watchdog that kills the build if available memory falls below 150 MB.
# Caches live in ~/.cache/gradle (never snapshotted). Log: ~/.cache/gradle_compile.log
set -u
export JAVA_HOME=/home/user/.cache/jdk17
export GRADLE_USER_HOME=/home/user/.cache/gradle
# Heaps can be lowered for the first, heavy ForgeGradle setup run: TOOL_XMX=300m DAEMON_XMX=420m
TOOL_XMX="${TOOL_XMX:-420m}"; DAEMON_XMX="${DAEMON_XMX:-560m}"; METASPACE="${METASPACE:-320m}"
export JAVA_TOOL_OPTIONS="-Xmx${TOOL_XMX} -XX:+UseSerialGC -XX:TieredStopAtLevel=1 -XX:ReservedCodeCacheSize=48m -Xss512k"
LOG=/home/user/.cache/gradle_compile.log
: > "$LOG"
(
  while sleep 2; do
    avail=$(awk '/MemAvailable/ {print int($2/1024)}' /proc/meminfo)
    if [ "$avail" -lt 150 ]; then
      echo "WATCHDOG: MemAvailable ${avail} MB < 150 MB, killing the build" >> "$LOG"
      pkill -9 -f GradleDaemon; pkill -9 -f GradleWrapperMain; pkill -9 -f renamer; pkill -9 -f accesstransformers
      break
    fi
    pgrep -f GradleWrapperMain >/dev/null || break
  done
) &
WD=$!
cd /home/user/eternal
sh gradlew compileJava --no-daemon --console=plain --project-cache-dir /home/user/.cache/eternal_project_cache \
  -Dorg.gradle.jvmargs="-Xmx${DAEMON_XMX} -XX:+UseSerialGC -XX:MaxMetaspaceSize=${METASPACE} -XX:TieredStopAtLevel=1 -XX:ReservedCodeCacheSize=64m" \
  -Dorg.gradle.workers.max=1 >> "$LOG" 2>&1
CODE=$?
echo "GRADLE EXIT $CODE" >> "$LOG"
kill $WD 2>/dev/null
exit $CODE
