#!/usr/bin/env bash
# Step 37 (A2: the calendar this place actually uses). Builds the calendar pack, compiles the
# register against the mod's own data, and runs it over eighteen known Chinese New Year dates,
# the Hijri, Julian, Saka, Vikram and Fasli conversions, and a spread of places and years.
#
# Pure Java plus Gson: no Forge, no Minecraft jars, no gradle. Provisions a JDK 17 and Gson into
# .cache the first time it runs.
#
# Usage: ./probe_calendars.sh        Exit code 1 if any check fails.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CACHE=/home/user/.cache
JDK="$CACHE/jdk-17.0.20.1+1"
GSON="$CACHE/gson.jar"
WORK="$CACHE/calcheck"
MOD="$HERE/../eternal"
RES="$MOD/src/main/resources"
REPORT="$HERE/logs/step37_calendars_check.txt"

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

echo "building the calendar and beliefs packs ..."
python3 "$HERE/build_calendars.py" || exit 1
python3 "$HERE/build_beliefs.py" || exit 1

rm -rf "$WORK"; mkdir -p "$WORK/src/com/eternalengine/calprobe" "$WORK/out"
cp "$HERE"/probe_calendars/CalendarsRun.java "$WORK/src/com/eternalengine/calprobe/"
cp "$HERE"/probe_calendars/TravelRun.java "$WORK/src/com/eternalengine/calprobe/"
cp "$HERE"/probe_calendars/BeliefsRun.java "$WORK/src/com/eternalengine/calprobe/"
# NewsService needs Minecraft; lift the two step-37 methods out of it into a runner
python3 "$HERE/probe_calendars_lift.py" "$WORK/src/com/eternalengine/calprobe/NewsRun.java"

echo "compiling the register ..."
"$JDK/bin/javac" -nowarn -proc:none -encoding UTF-8 -d "$WORK/out" -cp "$GSON" \
  -sourcepath "$MOD/src/main/java:$STUBS" \
  "$MOD/src/main/java/com/eternalengine/knowledge/Calendars.java" \
  "$MOD/src/main/java/com/eternalengine/civilization/RulerRegister.java" \
  "$MOD/src/main/java/com/eternalengine/technology/TechnologyAtlas.java" \
  "$MOD/src/main/java/com/eternalengine/news/NewsTravel.java" \
  "$MOD/src/main/java/com/eternalengine/news/NewsEras.java" \
  "$MOD/src/main/java/com/eternalengine/news/NewsChannels.java" \
  "$MOD/src/main/java/com/eternalengine/civilization/Rumour.java" \
  "$MOD/src/main/java/com/eternalengine/knowledge/Beliefs.java" \
  "$WORK/src/com/eternalengine/calprobe/CalendarsRun.java" \
  "$WORK/src/com/eternalengine/calprobe/TravelRun.java" \
  "$WORK/src/com/eternalengine/calprobe/NewsRun.java" \
  "$WORK/src/com/eternalengine/calprobe/BeliefsRun.java" > "$WORK/javac.log" 2>&1 || {
    echo "COMPILE FAILED:"; grep -v "unmappable" "$WORK/javac.log" | head -40; exit 1; }
grep -v "unmappable\|warning" "$WORK/javac.log" | head -20 || true

set +e
"$JDK/bin/java" -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 \
  -cp "$WORK/out:$RES:$GSON" com.eternalengine.calprobe.CalendarsRun 2>&1 \
  | tee "$REPORT"
RC=${PIPESTATUS[0]}
set -e

echo
echo "running the travel register ..."
set +e
"$JDK/bin/java" -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 \
  -cp "$WORK/out:$RES:$GSON" com.eternalengine.calprobe.TravelRun 2>&1 | tee -a "$REPORT"
RC2=${PIPESTATUS[0]}
set -e

echo
echo "running the news-by-era register ..."
set +e
"$JDK/bin/java" -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 \
  -cp "$WORK/out:$RES:$GSON" com.eternalengine.calprobe.NewsRun 2>&1 | tee -a "$REPORT"
RC3=${PIPESTATUS[0]}
set -e

echo
echo "running the beliefs register ..."
set +e
"$JDK/bin/java" -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 \
  -cp "$WORK/out:$RES:$GSON" com.eternalengine.calprobe.BeliefsRun 2>&1 | tee -a "$REPORT"
RC4=${PIPESTATUS[0]}
set -e

echo
echo "report written to $REPORT"
[ "$RC" -eq 0 ] && [ "$RC2" -eq 0 ] && [ "$RC3" -eq 0 ] && [ "$RC4" -eq 0 ]
