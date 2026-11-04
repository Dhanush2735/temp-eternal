#!/usr/bin/env bash
# Step 36 (B10 building life, B21 player buildings across time, B27 disasters that change the
# land): run the building-life registers, the life part of /ee check, and a set of places through
# them, against the mod's own data and nothing else.
#
# The registers are pure Java plus Gson, so this needs no Forge, no Minecraft jars and no gradle.
# It provisions a JDK 17 and Gson into .cache the first time it runs.
#
# What it does:
#   1. compiles the step-36 registers straight out of the mod tree;
#   2. lifts HistoryChecks' life() part into a stand-alone runner (HistoryChecks itself needs
#      Minecraft to compile) and runs it;
#   3. prints the state of a set of famous places in a set of years, so the answers can be read.
#
# Usage: ./probe_life.sh            Exit code 1 if any check fails.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CACHE=/home/user/.cache
JDK="$CACHE/jdk-17.0.20.1+1"
GSON="$CACHE/gson.jar"
WORK="$CACHE/lifecheck"
MOD="$HERE/../eternal"
RES="$MOD/src/main/resources"
REPORT="$HERE/logs/step36_life_check.txt"

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

# slf4j and javax.annotation stand-ins, so the registers can be compiled without the mod's deps
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

rm -rf "$WORK"; mkdir -p "$WORK/src/com/eternalengine/life" "$WORK/out"
echo "compiling the step-36 registers ..."
"$JDK/bin/javac" -nowarn -proc:none -encoding UTF-8 -d "$WORK/out" -cp "$GSON" \
  -sourcepath "$MOD/src/main/java:$STUBS" \
  "$MOD/src/main/java/com/eternalengine/buildings/PlayerEdits.java" \
  "$MOD/src/main/java/com/eternalengine/civilization/Disasters.java" 2>&1 \
  | grep -v "unmappable\|warning" || true

# lift HistoryChecks' life part: the Section class, and everything from the step-36 banner down
# to the step-35 sky banner.
python3 - "$MOD/src/main/java/com/eternalengine/civilization/HistoryChecks.java" \
          "$WORK/src/com/eternalengine/life/LifeCheckRun.java" <<'PY'
import sys
src, dst = sys.argv[1], sys.argv[2]
lines = open(src, encoding="utf-8").read().splitlines(keepends=True)
status   = next(l for l in lines if "public enum Status" in l)
linerec  = next(l for l in lines if "public record Line(" in l)
i  = next(n for n, l in enumerate(lines) if "public static final class Section {" in l)
j  = next(n for n, l in enumerate(lines) if n > i and l.rstrip() == "    }")
section  = "".join(lines[i:j + 1])
i  = next(n for n, l in enumerate(lines) if "step 36: the life of a building" in l)
j  = next(n for n, l in enumerate(lines) if "step 35: the sky" in l)
methods  = "".join(lines[i:j])
open(dst, "w", encoding="utf-8").write(
'''package com.eternalengine.life;

import com.eternalengine.buildings.BuildingLife;
import com.eternalengine.buildings.FamousBuildings;
import com.eternalengine.buildings.PlayerEdits;
import com.eternalengine.civilization.Disasters;
import com.eternalengine.civilization.Disasters.Disaster;
// The lifted range now reaches step 38's people() section, which names the seven registers of
// com.eternalengine.people; without these the generated runner stops at "cannot find symbol"
// (found by the full sweep of 2026-10-23, marking board 10).
import com.eternalengine.people.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/** HistoryChecks' life part, lifted out of the mod so it can be run without Minecraft. */
public final class LifeCheckRun {

    enum Part { LIFE }

    ''' + status.strip() + '''

    ''' + linerec.strip() + '''

''' + section + '''
''' + methods + '''
    public static void main(String[] args) {
        Section s = new Section(Part.LIFE);
        long t0 = System.nanoTime();
        life(s);
        s.millis = (System.nanoTime() - t0) / 1_000_000L;
        int ok = 0, bad = 0;
        for (Line l : s.lines()) {
            String tag = switch (l.status()) {
                case OK -> l.counted() ? "  ok  " : "  ok .";
                case FAIL -> "  FAIL";
                case KNOWN -> " known";
                case INFO -> "  note";
            };
            System.out.println(tag + "  " + l.text());
            if (l.status() == Status.FAIL) { System.out.println("         -> " + l.detail()); bad++; }
            else if (l.counted() && l.status() == Status.OK) { ok++; }
            if (!l.brief() && !l.detail().isEmpty()) { System.out.println("         (" + l.detail() + ")"); }
        }
        System.out.println("\\n" + ok + " passed, " + bad + " failed, " + s.millis + " ms");
        System.exit(bad == 0 ? 0 : 1);
    }
}
''')
print("lifted HistoryChecks.life()")
PY

echo "running /ee check life ..."
mkdir -p "$(dirname "$REPORT")"
set +e
# -sourcepath: the lifted run names LifeTable, Households and friends by import, and without the
# sources on the path javac stops at "cannot find symbol" for every one of them (found by the full
# sweep of 2026-10-23, marking board 10).
"$JDK/bin/javac" -nowarn -proc:none -encoding UTF-8 -d "$WORK/out" -cp "$WORK/out:$GSON" \
  -sourcepath "$MOD/src/main/java:$STUBS" \
  "$WORK/src/com/eternalengine/life/LifeCheckRun.java" 2>&1 | grep -v "unmappable\|warning" | head -20
"$JDK/bin/java" -cp "$WORK/out:$RES:$GSON" com.eternalengine.life.LifeCheckRun 2>&1 | tee "$REPORT"
RC=${PIPESTATUS[0]}
set -e

# ---------------------------------------------------------------------------------------------
# lift the step-36 hooks out of TerraOsmBridge, which needs Forge to compile, and answer a few
# places with each of them
echo "lifting and running the step-36 Terra++ hooks ..."
mkdir -p "$WORK/src/com/eternalengine/life"
python3 "$HERE/probe_life_lifthooks.py" \
  "$MOD/src/main/java/com/eternalengine/terrabridge/TerraOsmBridge.java" \
  "$WORK/src/com/eternalengine/life/HooksRun.java"

"$JDK/bin/javac" -nowarn -proc:none -encoding UTF-8 -d "$WORK/out" -cp "$WORK/out:$GSON" \
  -sourcepath "$STUBS" "$WORK/src/com/eternalengine/life/HooksRun.java" 2>&1 \
  | grep -v "unmappable\|warning" | head -20 || true
"$JDK/bin/java" -cp "$WORK/out:$RES:$GSON" com.eternalengine.life.HooksRun 2>&1 | tee -a "$REPORT"

echo
echo "report written to $REPORT"
exit "$RC"
