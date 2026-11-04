#!/usr/bin/env bash
# Step 31 (B7): check Terra++'s buildings and roads by year in the world-wide
# test places.
#
# Compiles Terra++'s OWN dating code out of the user's fork in /home/user/terra3
# and runs it outside Minecraft. Nothing is re-implemented: the Overpass parser
# (OsmStructureIndex.parseElement), the gravity model, the population floors, the
# technology floors and the visibility rule are the real classes. Five things
# cannot compile outside a Forge build and are stubbed in probes/terra/stubs
# (each is documented in its file, and none of them touches dating).
#
#   bash probe_terra.sh              # both passes; writes logs/step31_terra_report.txt
#   bash probe_terra.sh --floors     # offline only: region boxes, floors, empty places
#   bash probe_terra.sh --osm        # needs: python3 terra_check.py --fetch
#
# Fetching is separate because the public Overpass mirrors are unreliable:
# terra_check.py keeps what it has, so re-running it fills the gaps.
set -euo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"
TERRA=/home/user/terra3
GSON=/home/user/libs/gson-2.10.1.jar
HERE=/home/user/worldfill
OUT=/home/user/.cache/wf_probe_terra
REPORT="$HERE/logs/step31_terra_report.txt"

[ -x "$JDK/bin/java" ] || bash /home/user/libs/get_jdk17.sh "$JDK" | tail -2
mkdir -p "$OUT" "$HERE/logs"

echo "compiling Terra++'s dating code from $TERRA ..."
"$JDK/bin/javac" -J-Xmx500m -encoding UTF-8 -nowarn -cp "$GSON" \
  -sourcepath "$HERE/probes/terra/stubs:$TERRA/src/main/java" -d "$OUT" \
  "$HERE/probes/terra/TerraDatingProbe.java" \
  "$TERRA/src/main/java/net/buildtheearth/terraplusplus/generator/osm/OsmStructureIndex.java" \
  "$TERRA/src/main/java/net/buildtheearth/terraplusplus/generator/historical/OsmDateInferencer.java" \
  "$TERRA/src/main/java/net/buildtheearth/terraplusplus/generator/historical/StructureDateEstimator.java" \
  "$TERRA/src/main/java/net/buildtheearth/terraplusplus/generator/historical/HistoricalDateParser.java" \
  2>&1 | grep -vE "^Note:|warning" | head -20 || true

MODE="${1:---all}"
{
  echo "STEP 31 (B7) - Terra++ buildings and roads by year in the test places"
  echo "run: $(date -u '+%Y-%m-%d %H:%M UTC')   mode: $MODE"
  echo "terra3 HEAD: $(git -C "$TERRA" rev-parse --short HEAD 2>/dev/null || echo '?')"
  echo
} | tee "$REPORT"

run() {
  echo "=== $* ===" | tee -a "$REPORT"
  "$JDK/bin/java" -Xmx600m -Dfile.encoding=UTF-8 -cp "$OUT:$GSON" \
    TerraDatingProbe "$@" 2>&1 | tee -a "$REPORT"
  echo | tee -a "$REPORT"
}

case "$MODE" in
  --floors) run --floors ;;
  --holes)  run --holes ;;
  --osm)    run --osm "$HERE/build/terra" ;;
  *)        run --floors; run --holes; run --osm "$HERE/build/terra" ;;
esac

echo "report: $REPORT"
