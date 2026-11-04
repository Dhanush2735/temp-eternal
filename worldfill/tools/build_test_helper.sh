#!/usr/bin/env bash
# Build the sandbox-only test helper mod (worldfill/testmod: EeTestHelper drives CrowdFigures.ensure with a fake
# player) into ~/.cache/ee_testhelper/eetesthelper.jar. run_test_server.sh copies it into run/mods only when
# EE_TEST_HELPER=1, and removes it otherwise. It is compiled against the mod's Gradle classes and the dev
# (official-names) Minecraft classpath, so it runs only on the test server, never in a real game.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
SRC=/home/user/worldfill/testmod
CPFILE=/home/user/.cache/wf_probe_commands/runtime_cp.txt
OUT=/home/user/.cache/ee_testhelper
[ -s "$CPFILE" ] || { echo "no $CPFILE: run tools/run_test_server.sh once (or the printEeClasspath init script)"; exit 2; }
rm -rf "$OUT/classes"; mkdir -p "$OUT/classes/META-INF"
"$JDK/bin/javac" -J-Xmx300m -encoding UTF-8 -nowarn -proc:none \
  -cp "$MOD/build/classes/java/main:$(cat "$CPFILE")" -d "$OUT/classes" "$SRC/src/eetest/helper/EeTestHelper.java"
cp "$SRC/META-INF/mods.toml" "$OUT/classes/META-INF/"
rm -f "$OUT/eetesthelper.jar"
(cd "$OUT/classes" && "$JDK/bin/jar" --create --file "$OUT/eetesthelper.jar" .)
echo "built $OUT/eetesthelper.jar"
