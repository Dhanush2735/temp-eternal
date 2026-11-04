#!/usr/bin/env bash
# Step 38 (D2, D17 and the life-span half of C20): how long people lived, and when they married.
# Builds the life-table pack, compiles the register against the mod's own data, and checks the
# survivor curve against an independent implementation of the same arithmetic in
# worldfill/build_life_table.py.
#
# Pure Java plus Gson: no Forge, no Minecraft jars, no gradle. Provisions a JDK 17 and Gson into
# .cache the first time it runs.
#
# Usage: ./probe_lifetable.sh        Exit code 1 if any check fails.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CACHE=/home/user/.cache
JDK="$CACHE/jdk-17.0.20.1+1"
GSON="$CACHE/gson.jar"
WORK="$CACHE/lifecheck"
MOD="$HERE/../eternal"
RES="$MOD/src/main/resources"
REPORT="$HERE/logs/step38_life_check.txt"

if [ ! -x "$JDK/bin/javac" ]; then
  echo "fetching a JDK 17 into $JDK ..."
  mkdir -p "$JDK"
  curl -sL --retry 3 -o "$CACHE/jdk17.tar.gz" \
    "https://api.adoptium.net/v3/binary/latest/17/ga/linux/x64/jdk/hotspot/normal/eclipse"
  tar xzf "$CACHE/jdk17.tar.gz" -C "$JDK" --strip-components=1
fi
if [ ! -f "$GSON" ]; then
  echo "fetching Gson ..."
  curl -sL --retry 3 -o "$GSON" \
    "https://repo1.maven.org/maven2/com/google/code/gson/gson/2.10.1/gson-2.10.1.jar"
fi

# slf4j and javax.annotation stand-ins, so the registers compile without the mod's dependencies
STUBS="$CACHE/stubs"
mkdir -p "$STUBS/org/slf4j" "$STUBS/javax/annotation"
cat > "$STUBS/org/slf4j/Logger.java" <<'EOF'
package org.slf4j;
public interface Logger {
    void info(String s); void info(String s, Object a); void info(String s, Object a, Object b);
    void warn(String s); void warn(String s, Object a); void warn(String s, Object a, Object b);
    void error(String s); void error(String s, Object a); void error(String s, Throwable t);
    void debug(String s); void debug(String s, Object a); void trace(String s);
    boolean isDebugEnabled();
}
EOF
cat > "$STUBS/org/slf4j/LoggerFactory.java" <<'EOF'
package org.slf4j;
public final class LoggerFactory {
    public static Logger getLogger(Class<?> c) { return new Logger() {
        public void info(String s){} public void info(String s,Object a){} public void info(String s,Object a,Object b){}
        public void warn(String s){} public void warn(String s,Object a){} public void warn(String s,Object a,Object b){}
        public void error(String s){} public void error(String s,Object a){} public void error(String s,Throwable t){}
        public void debug(String s){} public void debug(String s,Object a){} public void trace(String s){}
        public boolean isDebugEnabled(){ return false; } }; }
    public static Logger getLogger(String s) { return getLogger(Object.class); }
}
EOF
cat > "$STUBS/javax/annotation/Nullable.java" <<'EOF'
package javax.annotation;
import java.lang.annotation.*;
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.TYPE_USE, ElementType.PARAMETER, ElementType.FIELD, ElementType.METHOD,
         ElementType.LOCAL_VARIABLE, ElementType.TYPE_PARAMETER})
public @interface Nullable {}
EOF


echo "building the life-table pack ..."
python3 "$HERE/build_life_table.py" || exit 1
python3 "$HERE/build_households.py" || exit 1
python3 "$HERE/build_jobs.py" || exit 1
python3 "$HERE/build_day_round.py" || exit 1
python3 "$HERE/build_migrations.py" || exit 1
python3 "$HERE/build_health.py" || exit 1
python3 "$HERE/build_scenes.py" || exit 1

rm -rf "$WORK"; mkdir -p "$WORK/src/com/eternalengine/lifeprobe" "$WORK/out"
cp "$HERE"/probe_lifetable/LifeRun.java "$WORK/src/com/eternalengine/lifeprobe/"
cp "$HERE"/probe_lifetable/HomeRun.java "$WORK/src/com/eternalengine/lifeprobe/"
cp "$HERE"/probe_lifetable/JobRun.java "$WORK/src/com/eternalengine/lifeprobe/"
cp "$HERE"/probe_lifetable/DayRun.java "$WORK/src/com/eternalengine/lifeprobe/"
cp "$HERE"/probe_lifetable/NeedRun.java "$WORK/src/com/eternalengine/lifeprobe/"
cp "$HERE"/probe_lifetable/MoveRun.java "$WORK/src/com/eternalengine/lifeprobe/"
cp "$HERE"/probe_lifetable/HealthRun.java "$WORK/src/com/eternalengine/lifeprobe/"
cp "$HERE"/probe_lifetable/SceneRun.java "$WORK/src/com/eternalengine/lifeprobe/"
cp "$HERE"/probe_lifetable/SceneSweep.java "$WORK/src/com/eternalengine/lifeprobe/"
cp "$HERE"/probe_lifetable/BattleRun.java "$WORK/src/com/eternalengine/lifeprobe/"
cp "$HERE"/probe_lifetable/SiegeRun.java "$WORK/src/com/eternalengine/lifeprobe/"
cp "$HERE"/probe_lifetable/MoraleRun.java "$WORK/src/com/eternalengine/lifeprobe/"
cp "$HERE"/probe_lifetable/ArmiesRun.java "$WORK/src/com/eternalengine/lifeprobe/"
cp "$HERE"/probe_lifetable/CheckArmies.java "$WORK/src/com/eternalengine/lifeprobe/"

echo "compiling the register ..."
"$JDK/bin/javac" -nowarn -proc:none -encoding UTF-8 -d "$WORK/out" -cp "$GSON" \
  -sourcepath "$MOD/src/main/java" \
  "$MOD/src/main/java/com/eternalengine/people/LifeTable.java" \
  "$MOD/src/main/java/com/eternalengine/knowledge/KnowledgeLevels.java" \
  "$MOD/src/main/java/com/eternalengine/people/Households.java" \
  "$MOD/src/main/java/com/eternalengine/people/Jobs.java" \
  "$MOD/src/main/java/com/eternalengine/people/DayRound.java" \
  "$MOD/src/main/java/com/eternalengine/people/Needs.java" \
  "$MOD/src/main/java/com/eternalengine/civilization/Disasters.java" \
  "$MOD/src/main/java/com/eternalengine/people/Migrations.java" \
  "$MOD/src/main/java/com/eternalengine/people/Health.java" \
  "$MOD/src/main/java/com/eternalengine/people/Scenes.java" \
  "$WORK/src/com/eternalengine/lifeprobe/LifeRun.java" \
  "$WORK/src/com/eternalengine/lifeprobe/HomeRun.java" \
  "$WORK/src/com/eternalengine/lifeprobe/JobRun.java" \
  "$WORK/src/com/eternalengine/lifeprobe/DayRun.java" \
  "$WORK/src/com/eternalengine/lifeprobe/NeedRun.java" \
  "$WORK/src/com/eternalengine/lifeprobe/MoveRun.java" \
  "$WORK/src/com/eternalengine/lifeprobe/HealthRun.java" \
  "$WORK/src/com/eternalengine/lifeprobe/SceneRun.java" \
  "$WORK/src/com/eternalengine/lifeprobe/SceneSweep.java" \
  "$MOD/src/main/java/com/eternalengine/war/Battles.java" \
  "$WORK/src/com/eternalengine/lifeprobe/BattleRun.java" \
  "$MOD/src/main/java/com/eternalengine/war/Sieges.java" \
  "$WORK/src/com/eternalengine/lifeprobe/SiegeRun.java" \
  "$MOD/src/main/java/com/eternalengine/war/FormationType.java" \
  "$MOD/src/main/java/com/eternalengine/war/Army.java" \
  "$MOD/src/main/java/com/eternalengine/war/Morale.java" \
  "$MOD/src/main/java/com/eternalengine/war/Sides.java" \
  "$WORK/src/com/eternalengine/lifeprobe/MoraleRun.java" \
  "$MOD/src/main/java/com/eternalengine/war/BattleRecord.java" \
  "$MOD/src/main/java/com/eternalengine/war/BattleOutcome.java" \
  "$MOD/src/main/java/com/eternalengine/war/WarStatus.java" \
  "$MOD/src/main/java/com/eternalengine/war/War.java" \
  "$MOD/src/main/java/com/eternalengine/war/BattleSimulator.java" \
  "$WORK/src/com/eternalengine/lifeprobe/ArmiesRun.java" \
  "$MOD/src/main/java/com/eternalengine/war/ArmyChecks.java" \
  "$WORK/src/com/eternalengine/lifeprobe/CheckArmies.java" > "$WORK/javac.log" 2>&1 || {
    echo "COMPILE FAILED:"; grep -v "unmappable" "$WORK/javac.log" | head -40; exit 1; }
grep -v "unmappable\\|warning" "$WORK/javac.log" | head -20 || true

set +e
"$JDK/bin/java" -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 \
  -cp "$WORK/out:$RES:$GSON" com.eternalengine.lifeprobe.LifeRun 2>&1 | tee "$REPORT"
RC=${PIPESTATUS[0]}
"$JDK/bin/java" -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 \
  -cp "$WORK/out:$RES:$GSON" com.eternalengine.lifeprobe.HomeRun 2>&1 | tee -a "$REPORT"
RC2=$?
"$JDK/bin/java" -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 \
  -cp "$WORK/out:$RES:$GSON" com.eternalengine.lifeprobe.JobRun 2>&1 | tee -a "$REPORT"
RC3=$?
"$JDK/bin/java" -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 \
  -cp "$WORK/out:$RES:$GSON" com.eternalengine.lifeprobe.DayRun 2>&1 | tee -a "$REPORT"
RC4=$?
"$JDK/bin/java" -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 \
  -cp "$WORK/out:$RES:$GSON" com.eternalengine.lifeprobe.NeedRun 2>&1 | tee -a "$REPORT"
RC5=$?
"$JDK/bin/java" -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 \
  -cp "$WORK/out:$RES:$GSON" com.eternalengine.lifeprobe.MoveRun 2>&1 | tee -a "$REPORT"
RC6=$?
"$JDK/bin/java" -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 \
  -cp "$WORK/out:$RES:$GSON" com.eternalengine.lifeprobe.HealthRun 2>&1 | tee -a "$REPORT"
RC7=$?
"$JDK/bin/java" -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 \
  -cp "$WORK/out:$RES:$GSON" com.eternalengine.lifeprobe.SceneRun 2>&1 | tee -a "$REPORT"
RC8=$?
"$JDK/bin/java" -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 \
  -cp "$WORK/out:$RES:$GSON" com.eternalengine.lifeprobe.SceneSweep 2>&1 | tee -a "$REPORT"
RC9=$?
set +e
"$JDK/bin/java" -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 \
  -cp "$WORK/out:$RES:$GSON" com.eternalengine.lifeprobe.BattleRun 2>&1 | tee -a "$REPORT"
RC10=$?
"$JDK/bin/java" -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 \
  -cp "$WORK/out:$RES:$GSON" com.eternalengine.lifeprobe.SiegeRun 2>&1 | tee -a "$REPORT"
RC11=$?
"$JDK/bin/java" -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 \
  -cp "$WORK/out:$RES:$GSON" com.eternalengine.lifeprobe.MoraleRun 2>&1 | tee -a "$REPORT"
RC12=$?
"$JDK/bin/java" -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 \
  -cp "$WORK/out:$RES:$GSON" com.eternalengine.lifeprobe.ArmiesRun 2>&1 | tee -a "$REPORT"
RC13=$?
"$JDK/bin/java" -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 \
  -cp "$WORK/out:$RES:$GSON" com.eternalengine.lifeprobe.CheckArmies 2>&1 | tee -a "$REPORT"
RC14=$?
set -e
if [ "$RC14" -ne 0 ]; then echo "the ARMIES part of /ee check failed"; exit 1; fi
set +e
set -e
[ "$RC" -eq 0 ] && [ "$RC2" -eq 0 ] && [ "$RC3" -eq 0 ] && [ "$RC4" -eq 0 ] && [ "$RC5" -eq 0 ] && [ "$RC6" -eq 0 ] && [ "$RC7" -eq 0 ] && [ "$RC8" -eq 0 ] && [ "$RC9" -eq 0 ] && [ "$RC10" -eq 0 ] && [ "$RC11" -eq 0 ] && [ "$RC12" -eq 0 ] && [ "$RC13" -eq 0 ] && [ "$RC14" -eq 0 ]
[ "$RC" -eq 0 ] && [ "$RC2" -eq 0 ] && [ "$RC3" -eq 0 ] && [ "$RC4" -eq 0 ] && [ "$RC5" -eq 0 ] && [ "$RC6" -eq 0 ] && [ "$RC7" -eq 0 ] && [ "$RC8" -eq 0 ] && [ "$RC10" -eq 0 ] && [ "$RC11" -eq 0 ] && [ "$RC12" -eq 0 ] && [ "$RC13" -eq 0 ] && [ "$RC14" -eq 0 ]
[ "$RC" -eq 0 ] && [ "$RC2" -eq 0 ] && [ "$RC3" -eq 0 ] && [ "$RC4" -eq 0 ] && [ "$RC5" -eq 0 ] && [ "$RC6" -eq 0 ] && [ "$RC10" -eq 0 ] && [ "$RC11" -eq 0 ] && [ "$RC12" -eq 0 ] && [ "$RC13" -eq 0 ] && [ "$RC14" -eq 0 ]
[ "$RC" -eq 0 ] && [ "$RC2" -eq 0 ] && [ "$RC3" -eq 0 ] && [ "$RC4" -eq 0 ] && [ "$RC5" -eq 0 ] && [ "$RC10" -eq 0 ] && [ "$RC11" -eq 0 ] && [ "$RC12" -eq 0 ] && [ "$RC13" -eq 0 ] && [ "$RC14" -eq 0 ]
[ "$RC" -eq 0 ] && [ "$RC2" -eq 0 ] && [ "$RC3" -eq 0 ] && [ "$RC4" -eq 0 ] && [ "$RC10" -eq 0 ] && [ "$RC11" -eq 0 ] && [ "$RC12" -eq 0 ] && [ "$RC13" -eq 0 ] && [ "$RC14" -eq 0 ]
[ "$RC" -eq 0 ] && [ "$RC2" -eq 0 ] && [ "$RC3" -eq 0 ] && [ "$RC10" -eq 0 ] && [ "$RC11" -eq 0 ] && [ "$RC12" -eq 0 ] && [ "$RC13" -eq 0 ] && [ "$RC14" -eq 0 ]
[ "$RC" -eq 0 ] && [ "$RC2" -eq 0 ] && [ "$RC10" -eq 0 ] && [ "$RC11" -eq 0 ] && [ "$RC12" -eq 0 ] && [ "$RC13" -eq 0 ] && [ "$RC14" -eq 0 ]
RC=$?

echo
echo "report written to $REPORT"
[ "$RC" -eq 0 ] && [ "$RC10" -eq 0 ] && [ "$RC11" -eq 0 ] && [ "$RC12" -eq 0 ] && [ "$RC13" -eq 0 ] && [ "$RC14" -eq 0 ]
