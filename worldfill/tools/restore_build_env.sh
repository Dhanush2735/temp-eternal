#!/usr/bin/env bash
# Restore everything the build and the tests need after the sandbox lost ~/.cache (it is not part of the workspace
# snapshots): the JDK 17, Gradle's caches and a first full compile, the mod's runtime classpath for the probes, and the
# test helper mod for the test server. Run it in the background (it takes 10-25 minutes, most of it ForgeGradle's
# first setup); the log is ~/.cache/restore_build_env.log, and the last line says RESTORE DONE or RESTORE FAILED.
#
#   tools/restore_build_env.sh
set -u
LOG=/home/user/.cache/restore_build_env.log
mkdir -p /home/user/.cache
: > "$LOG"
step() { echo "== $(date +%H:%M:%S) $*" >> "$LOG"; }
fail() { echo "RESTORE FAILED: $*" >> "$LOG"; exit 1; }

step "JDK 17"
bash /home/user/libs/get_jdk17.sh >> "$LOG" 2>&1 || fail "JDK"

step "first compile (ForgeGradle setup)"
cd /home/user/worldfill
ok=0
for attempt in 1 2 3; do
  TOOL_XMX=300m DAEMON_XMX=420m METASPACE=280m bash tools/gradle_compile.sh
  cat /home/user/.cache/gradle_compile.log >> "$LOG"
  pkill -f "[G]radleDaemon" 2>/dev/null
  sleep 8
  if grep -q "GRADLE EXIT 0" /home/user/.cache/gradle_compile.log; then ok=1; break; fi
  step "compile attempt $attempt failed; again"
done
[ "$ok" = 1 ] || fail "compile"

step "runtime classpath"
OUT=/home/user/.cache/wf_probe_commands
mkdir -p "$OUT"
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
(cd /home/user/eternal && JAVA_HOME=/home/user/.cache/jdk17 GRADLE_USER_HOME=/home/user/.cache/gradle sh gradlew -q \
    --project-cache-dir /home/user/.cache/eternal_project_cache -I "$OUT/printcp.gradle" printEeClasspath \
    -PcpOut="$OUT/runtime_cp.txt" --no-daemon --console=plain \
    -Dorg.gradle.jvmargs="-Xmx560m -XX:+UseSerialGC -XX:MaxMetaspaceSize=320m" -Dorg.gradle.workers.max=1) >> "$LOG" 2>&1
pkill -f "[G]radleDaemon" 2>/dev/null
[ -s "$OUT/runtime_cp.txt" ] || fail "runtime classpath"

step "test helper mod"
bash /home/user/worldfill/tools/build_test_helper.sh >> "$LOG" 2>&1 || fail "test helper"

step "RESTORE DONE"
echo "RESTORE DONE" >> "$LOG"
