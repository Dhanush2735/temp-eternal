#!/usr/bin/env bash
# A real Forge 1.20.1 dedicated server with the mod (and Terra++), inside the sandbox, to run /ee check all
# for real. It starts what `gradlew runServer` would start, but without Gradle staying in memory: Gradle and a
# server together do not fit in this sandbox's 2 GB.
#
#   EE_ACCEPT_EULA=1 run_test_server.sh run   start the server in the foreground (an agent: as a background
#                                             process). EE_ACCEPT_EULA=1 writes run/eula.txt, i.e. accepts the
#                                             Minecraft EULA (https://aka.ms/MinecraftEULA) for this local test.
#   run_test_server.sh check                  send "ee check all", wait for the summary, print it and any FAIL lines.
#                                             The mod writes no file (step 15): every line is in run/logs/latest.log,
#                                             marked [EE check]; this script copies them to ~/.cache/ee_server/reports/
#   run_test_server.sh send "<command>"       any console command, without the slash ("ee data install", "stop")
#   EE_SPAWN_MONSTERS=1 ... run               let Minecraft spawn monsters by itself (step 21: to test the mod's
#                                             [minecraftMobs] settings); otherwise spawn-monsters=false
#   EE_TEST_HELPER=1 ... run                  also load the sandbox-only test helper mod (tools/build_test_helper.sh):
#                                             "eetest crowd start <x> <z> <year> <population>" runs the crowd code
#                                             (CrowdFigures.ensure) for a fake player, as if a player stood there
#   run_test_server.sh stop                   save the world and stop
#   run_test_server.sh clean                  stop, then delete eternal/run (world, logs, configs, eula.txt)
#
# Build first: tools/gradle_compile.sh. The first `run` also asks Gradle once for processResources (mods.toml
# needs its ${...} filled in) and for the launch settings (build/classpath/runServer_minecraftClasspath.txt).
#
# The world is flat, small and peaceful, on 127.0.0.1:25599 only. -Dproduction makes Forge behave as in the real
# game: in a development run Forge throws when a server config value is read before the world has loaded it, in
# the real game it quietly uses the default. (SimulationTickScheduler did that during start-up until step 14;
# since then it reads the server config only when a world starts.)
#
# Since step 14 history pauses while nobody is online (pauseWhenEmpty, on by default), and this test server has
# no player: put "pauseWhenEmpty = false" under [general] in run/config/eternalengine-common.toml to let the
# year and the world systems run. Edit config files in place (Forge's watcher misses a file replaced by
# sed -i), or run "ee reload" afterwards.
# A watchdog kills the server if the sandbox drops below 110 MB of free memory.
#
# Since step 11 the mod installs its foundation data into a new world when the world starts, so the first
# check of a new world passes too (section 2 says the data was installed then).
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
RUN="$MOD/run"
D=/home/user/.cache/ee_server
FIFO="$D/cmd"
PIDFILE="$D/server.pid"
CPOUT=/home/user/.cache/wf_probe_commands
CPFILE="$CPOUT/runtime_cp.txt"
MCCP="$MOD/build/classpath/runServer_minecraftClasspath.txt"
mkdir -p "$D/reports" "$CPOUT"

# Alive and not a zombie (an exited server stays a zombie until its parent reaps it, and kill -0 still works).
running() {
  [ -s "$PIDFILE" ] || return 1
  local st
  st=$(ps -o stat= -p "$(cat "$PIDFILE")" 2>/dev/null) || return 1
  [ -n "$st" ] && [ "${st#Z}" = "$st" ]
}

gradle() {
  (cd "$MOD" && JAVA_HOME="$JDK" GRADLE_USER_HOME=/home/user/.cache/gradle sh gradlew -q "$@" --no-daemon --project-cache-dir /home/user/.cache/eternal_project_cache \
      --console=plain -Dorg.gradle.jvmargs="-Xmx560m -XX:+UseSerialGC -XX:MaxMetaspaceSize=320m" \
      -Dorg.gradle.workers.max=1)
}

prepare() {
  [ -x "$JDK/bin/java" ] || { echo "no JDK 17 at $JDK: run libs/get_jdk17.sh"; exit 2; }
  [ -d "$MOD/build/classes/java/main/com/eternalengine" ] || { echo "not built: run tools/gradle_compile.sh"; exit 2; }
  if [ ! -s "$CPFILE" ] || [ "$MOD/build.gradle" -nt "$CPFILE" ]; then
    cat > "$CPOUT/printcp.gradle" <<'GRADLE'
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
    gradle -I "$CPOUT/printcp.gradle" printEeClasspath -PcpOut="$CPFILE"
  fi
  local toml="$MOD/build/resources/main/META-INF/mods.toml" tasks=()
  if [ ! -f "$toml" ] || [ -n "$(find "$MOD/src/main/resources" -type f -newer "$toml" -print -quit)" ]; then
    tasks+=(processResources)
  fi
  [ -s "$MCCP" ] || tasks+=(genIntellijRuns)
  if [ ${#tasks[@]} -gt 0 ]; then
    local had_idea=0
    [ -d "$MOD/.idea" ] && had_idea=1
    echo "asking Gradle for: ${tasks[*]}"
    gradle "${tasks[@]}"
    # genIntellijRuns is only wanted for the classpath file it writes; do not leave IDE files behind.
    [ "$had_idea" = 1 ] || rm -rf "$MOD/.idea"
    touch "$toml"
  fi
}

cmd_run() {
  running && { echo "already running (pid $(cat "$PIDFILE"))"; exit 1; }
  prepare
  mkdir -p "$RUN"
  # The sandbox-only test helper mod (tools/build_test_helper.sh): in run/mods only when asked for.
  rm -f "$RUN/mods/eetesthelper.jar"
  if [ "${EE_TEST_HELPER:-0}" = 1 ]; then
    [ -s /home/user/.cache/ee_testhelper/eetesthelper.jar ] || { echo "build it first: tools/build_test_helper.sh"; exit 2; }
    mkdir -p "$RUN/mods"; cp /home/user/.cache/ee_testhelper/eetesthelper.jar "$RUN/mods/"
    echo "with the test helper mod (eetest crowd start|status|stop)"
  fi
  if [ "${EE_ACCEPT_EULA:-0}" = 1 ]; then
    printf '# Local test server for /ee check all (sandbox only, never public).\neula=true\n' > "$RUN/eula.txt"
  fi
  grep -qs '^eula=true' "$RUN/eula.txt" || { echo "run/eula.txt does not accept the EULA: set EE_ACCEPT_EULA=1"; exit 2; }
  [ -f "$RUN/server.properties" ] || cat > "$RUN/server.properties" <<'EOF'
level-type=minecraft\:flat
level-name=world
online-mode=false
server-ip=127.0.0.1
server-port=25599
view-distance=3
simulation-distance=3
spawn-protection=0
max-players=2
generate-structures=false
spawn-npcs=false
spawn-animals=false
spawn-monsters=false
sync-chunk-writes=false
motd=ee check test
EOF
  # Step 21: EE_SPAWN_MONSTERS=1 lets Minecraft spawn monsters by itself, to test the mod's own [minecraftMobs]
  # settings; without it the test world stays peaceful, as before.
  if [ "${EE_SPAWN_MONSTERS:-0}" = 1 ]; then
    sed -i 's/^spawn-monsters=.*/spawn-monsters=true/' "$RUN/server.properties"
  else
    sed -i 's/^spawn-monsters=.*/spawn-monsters=false/' "$RUN/server.properties"
  fi
  local cp mp
  cp="$(cat "$CPFILE")"
  mp=$(tr ':' '\n' <<< "$cp" | grep -E "bootstraplauncher|securejarhandler|/asm-commons/|/asm-util/|/asm-analysis/|/asm-tree/|/org.ow2.asm/asm/|JarJarFileSystems" | paste -sd: -)
  cd "$RUN"
  rm -f "$FIFO"; mkfifo "$FIFO"
  exec 3<>"$FIFO"   # held open by the server too, so its console never sees end-of-input
  echo $$ > "$PIDFILE"   # exec below keeps this pid
  (
    while sleep 2; do
      running || break
      avail=$(awk '/MemAvailable/ {print int($2/1024)}' /proc/meminfo)
      if [ "$avail" -lt 110 ]; then
        echo "WATCHDOG: only ${avail} MB of memory left, killing the server"
        kill -9 "$(cat "$PIDFILE")"
        break
      fi
    done
  ) &
  export MOD_CLASSES="eternalengine%%$MOD/build/resources/main:eternalengine%%$MOD/build/classes/java/main"
  export MCP_MAPPINGS=official_1.20.1
  exec "$JDK/bin/java" ${EE_XMX:--Xmx850m} -Xms200m -XX:+UseSerialGC -XX:ReservedCodeCacheSize=96m \
    -Dfile.encoding=UTF-8 -Dproduction=true -Djava.net.preferIPv6Addresses=system \
    -DlegacyClassPath.file="$MCCP" \
    -DignoreList=bootstraplauncher,securejarhandler,asm-commons,asm-util,asm-analysis,asm-tree,asm,JarJarFileSystems,client-extra,fmlcore,javafmllanguage,lowcodelanguage,mclanguage,forge- \
    -DmergeModules=jna-5.10.0.jar,jna-platform-5.10.0.jar \
    -p "$mp" --add-modules ALL-MODULE-PATH \
    --add-opens java.base/java.util.jar=cpw.mods.securejarhandler \
    --add-opens java.base/java.lang.invoke=cpw.mods.securejarhandler \
    --add-exports java.base/sun.security.util=cpw.mods.securejarhandler \
    --add-exports jdk.naming.dns/com.sun.jndi.dns=java.naming \
    -cp "$cp" cpw.mods.bootstraplauncher.BootstrapLauncher \
    --launchTarget forgeserveruserdev --gameDir . --fml.forgeVersion 47.2.0 --fml.mcVersion 1.20.1 \
    --fml.forgeGroup net.minecraftforge --fml.mcpVersion 20230612.114412 --nogui <&3
}

send() {
  running || { echo "the server is not running"; exit 1; }
  printf '%s\n' "$*" > "$FIFO"
}

cmd_check() {
  local log="$RUN/logs/latest.log" from line out
  # Wait until the mod has finished starting (the first check would otherwise find it half-loaded).
  for _ in $(seq 1 90); do
    grep -q "Server startup complete" "$log" 2>/dev/null && break
    running || { echo "the server is not running"; exit 1; }
    sleep 2
  done
  from=$(wc -l < "$log")
  send "ee check all"
  for _ in $(seq 1 90); do
    line=$(tail -n +"$((from + 1))" "$log" | grep -a "\[EE check\] end of check: .* passed" | tail -1 || true)
    [ -n "$line" ] && break
    sleep 2
  done
  [ -n "$line" ] || { echo "no summary after 3 minutes; see $log"; exit 1; }
  # Since step 15 the mod writes no report file: every line is in latest.log, marked [EE check].
  out="$D/reports/ee_check_$(date +%Y-%m-%d_%H-%M-%S).log"
  tail -n +"$((from + 1))" "$log" | grep -a "\[EE check\]" > "$out" || true
  echo "${line#*\[EE check\] end of check: }"
  grep -a -A1 "\[EE check\] *\[FAIL\]" "$out" || true
  echo "$(wc -l < "$out") lines marked [EE check] in $log (a copy: $out)"
  case "$line" in *" 0 failed"*) exit 0 ;; *) exit 1 ;; esac
}

cmd_stop() {
  running || { echo "not running"; return 0; }
  send "stop"
  for _ in $(seq 1 60); do running || { echo "stopped"; return 0; }; sleep 1; done
  echo "did not stop in 60 s, killing"; kill -9 "$(cat "$PIDFILE")" || true
}

case "${1:-}" in
  run) cmd_run ;;
  check) cmd_check ;;
  send) shift; send "$@" ;;
  stop) cmd_stop ;;
  clean) cmd_stop; rm -rf "$RUN"; echo "removed $RUN" ;;
  *) sed -n '2,24p' "$0"; exit 2 ;;
esac
