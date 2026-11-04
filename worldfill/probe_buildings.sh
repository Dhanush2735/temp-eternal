#!/usr/bin/env bash
# Step 32 (B8, B16, B19): famous buildings, walls and ruins by year.
#
# Runs the mod's own register (com.eternalengine.buildings.FamousBuildings) outside Minecraft,
# over the 31 world-wide test places, and asks the two questions that matter: does the right thing
# stand in the right year, and does nothing stand before its time.
#
#   bash probe_buildings.sh          # writes logs/step32_buildings_report.txt
#
# There is no gradle build here, so the two things the register needs that are not in the JDK are
# supplied on the classpath: gson, and a stub of javax.annotation.Nullable (34 classes of the mod
# import it; Java 17 dropped it from the JDK). Nothing of the mod is re-implemented -- the register
# and the pack it reads are the real files.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
MOD=/home/user/eternal
GSON=/home/user/libs/gson-2.10.1.jar
HERE=/home/user/worldfill
OUT=/home/user/.cache/wf_probe_buildings
REPORT="$HERE/logs/step32_buildings_report.txt"

[ -x "$JDK/bin/java" ] || bash /home/user/libs/get_jdk17.sh "$JDK" | tail -2
rm -rf "$OUT"; mkdir -p "$OUT" "$HERE/logs"

RES="$MOD/src/main/resources"

echo "compiling FamousBuildings ..."
"$JDK/bin/javac" -J-Xmx400m -encoding UTF-8 -nowarn -proc:none -cp "$GSON" \
  -sourcepath "$HERE/probes/buildings/stubs:$MOD/src/main/java" -d "$OUT" \
  "$MOD/src/main/java/com/eternalengine/buildings/FamousBuildings.java" \
  "$HERE/probes/BuildingsProbe.java" 2>&1 | grep -vE "^Note:|warning" | head -20 || true

# The public hook needs more of the mod than the register does: TerraOsmBridge pulls in the
# logger, the config and one coordinate check. Five stubs cover them (probe.sh does the same for
# HistoricalPresence). None of them touches dating or the answer.
echo "compiling the Terra++ hook ..."
"$JDK/bin/javac" -J-Xmx400m -encoding UTF-8 -nowarn -proc:none -cp "$GSON" \
  -sourcepath "$HERE/probes/buildings/stubs:$MOD/src/main/java" -d "$OUT" \
  "$MOD/src/main/java/com/eternalengine/terrabridge/TerraOsmBridge.java" \
  "$HERE/probes/BuildingsHookProbe.java" 2>&1 | grep -vE "^Note:|warning" | head -20 || true

{
  echo "STEP 32 (B8, B16, B19) - famous buildings, walls and ruins by year"
  echo "run: $(date -u '+%Y-%m-%d %H:%M UTC')"
  echo "pack: $(ls -l "$RES/data/eternalengine/eternal/history/buildings_famous.json.gz" | awk '{print $5" bytes"}')"
  echo
} | tee "$REPORT"

echo "=== the register ===" | tee -a "$REPORT"
"$JDK/bin/java" -Xmx900m -Dfile.encoding=UTF-8 -cp "$OUT:$RES:$GSON" \
  BuildingsProbe 2>&1 | tee -a "$REPORT"

echo | tee -a "$REPORT"
echo "=== the Terra++ hook ===" | tee -a "$REPORT"
"$JDK/bin/java" -Xmx900m -Dfile.encoding=UTF-8 -cp "$OUT:$RES:$GSON" \
  BuildingsHookProbe 2>&1 | tee -a "$REPORT"

echo
echo "report: $REPORT"
