#!/usr/bin/env bash
# Step 35 (B22 stars, B23 the sky through time, B2 water that moved, B3 land use, B21 climate,
# B25 water works): run the sky registers, the sky part of /ee check, and the six step-35 Terra++
# hooks, against the mod's own data and nothing else.
#
# The registers are pure Java plus Gson, so this needs no Forge, no Minecraft jars and no gradle.
# It provisions a JDK 17 and Gson into .cache the first time it runs.
#
# What it does:
#   1. compiles com/eternalengine/sky straight out of the mod tree;
#   2. lifts HistoryChecks' sky() part into a stand-alone runner (HistoryChecks itself needs
#      Minecraft to compile) and runs it -- 33 checks;
#   3. lifts the six TerraOsmBridge hooks the same way and answers a few places with each.
#
# Usage: ./probe_sky.sh            Exit code 1 if any check fails.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CACHE=/home/user/.cache
JDK="$CACHE/jdk-17.0.20.1+1"
GSON="$CACHE/gson.jar"
WORK="$CACHE/skycheck"
MOD="$HERE/../eternal"
RES="$MOD/src/main/resources"
SRC="$MOD/src/main/java/com/eternalengine/sky"
REPORT="$HERE/logs/step35_sky_check.txt"

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

rm -rf "$WORK"; mkdir -p "$WORK/src/com/eternalengine/sky" "$WORK/src2/com/eternalengine/sky" "$WORK/out"
cp "$SRC"/*.java "$WORK/src/com/eternalengine/sky/"

# lift HistoryChecks' sky part: the Section class, yearText, and everything from the
# "step 35: the sky" banner down to the houses() method.
python3 - "$MOD/src/main/java/com/eternalengine/civilization/HistoryChecks.java" \
          "$WORK/src2/com/eternalengine/sky/SkyCheckRun.java" <<'PY'
import sys
src, dst = sys.argv[1], sys.argv[2]
lines = open(src, encoding="utf-8").read().splitlines(keepends=True)
status   = next(l for l in lines if "public enum Status" in l)
linerec  = next(l for l in lines if "public record Line(" in l)
i  = next(n for n, l in enumerate(lines) if "public static final class Section {" in l)
j  = next(n for n, l in enumerate(lines) if n > i and l.rstrip() == "    }")
section  = "".join(lines[i:j + 1])
i  = next(n for n, l in enumerate(lines) if "step 35: the sky" in l)
j  = next(n for n, l in enumerate(lines) if "private static void houses(Section s) {" in l)
methods  = "".join(lines[i:j])
i  = next(n for n, l in enumerate(lines) if "public static String yearText(int year)" in l)
yeartext = "".join(lines[i:i + 3])
open(dst, "w", encoding="utf-8").write(
'''package com.eternalengine.sky;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/** HistoryChecks' sky part, lifted out of the mod so it can be run without Minecraft. */
public final class SkyCheckRun {

    enum Part { SKY }

    ''' + status.strip() + '''

    ''' + linerec.strip() + '''

''' + section + '''
''' + methods + '''
    ''' + yeartext + '''
    public static void main(String[] args) {
        Section s = new Section(Part.SKY);
        long t0 = System.nanoTime();
        sky(s);
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
print("lifted HistoryChecks.sky()")
PY

# lift the six step-35 hooks out of TerraOsmBridge, which needs Forge to compile
python3 - "$MOD/src/main/java/com/eternalengine/terrabridge/TerraOsmBridge.java" \
          "$WORK/src2/com/eternalengine/sky/HooksRun.java" <<'PY'
import sys
src, dst = sys.argv[1], sys.argv[2]
lines = open(src, encoding="utf-8").read().splitlines(keepends=True)
i = next(n for n, l in enumerate(lines) if "step 35: land, water, climate, sky" in l)
# stop at step 36's banner, not at CachedResult: the step-36 hooks now sit between the two
j = next(n for n, l in enumerate(lines) if n > i and "step 36: what struck here" in l)
hooks = "".join(lines[i:j])
hooks = "\n".join((x[4:] if x.startswith("    ") else x) for x in hooks.split("\n"))
import re
for sig in ["public LandUse landUseAt(double lat",
            "public List<WaterChange> waterChangedBy(double lat",
            "public List<WaterWork> worksNear(double lat",
            "public Climate periodsAt(double lat",
            "public Sky starsOver(double lat",
            "public List<Eclipse> eclipseAt(double lat"]:
    hooks = hooks.replace(sig, sig.replace("public ", "public static "), 1)
open(dst, "w", encoding="utf-8").write(
'''package com.eternalengine.sky;

import com.eternalengine.civilization.LandUseGrid;
import com.eternalengine.civilization.WaterChanges;
import com.eternalengine.civilization.WaterWorks;
import com.eternalengine.climate.ClimatePeriods;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import javax.annotation.Nullable;

/** TerraOsmBridge's six step-35 hooks, lifted out of the mod: no Forge, no Minecraft. */
public final class HooksRun {

    private static final class Log { void warn(String s) { } void warn(String s, Object a) { } }
    private static final Log LOGGER = new Log();

''' + hooks + '''
    public static void main(String[] args) {
        System.out.println("=== landUseAt: what the land was used for ===");
        for (double[] q : new double[][]{{32.53, 46.83, -3000}, {30.50, 73.00, 1900},
                {23.00, 6.00, 1000}, {-3.10, -60.02, 1500}, {72.00, -40.00, 1000},
                {40.78, -73.97, 1900}}) {
            LandUse u = landUseAt(q[0], q[1], (int) q[2]);
            System.out.printf(Locale.ROOT, "  %7.2f,%8.2f %6d  %s%n", q[0], q[1], (int) q[2],
                    u == null ? "nothing (water)" : u.shortName() + " / " + u.level()
                            + " / " + u.name());
        }
        System.out.println("\\n=== waterChangedBy: the water that moved ===");
        for (double[] q : new double[][]{{52.70, 5.30, 1900}, {52.70, 5.30, 1960},
                {45.00, 59.00, 2010}, {30.96, 46.10, -2500}, {23.00, 6.00, 1000}}) {
            List<WaterChange> c = waterChangedBy(q[0], q[1], (int) q[2]);
            System.out.printf(Locale.ROOT, "  %7.2f,%8.2f %6d  %s%n", q[0], q[1], (int) q[2],
                    c.isEmpty() ? "nothing recorded" : c.get(0).name() + ": " + c.get(0).change()
                            + " in " + c.get(0).year() + (c.get(0).stillStanding() ? ", still so" : ""));
        }
        System.out.println("\\n=== worksNear: the water works standing then ===");
        for (double[] q : new double[][]{{41.8925, 12.4853, 100, 25}, {-33.8688, 151.2093, 1850, 25},
                {27.3242, 68.1356, -2500, 10}}) {
            List<WaterWork> w = worksNear(q[0], q[1], (int) q[2], q[3]);
            System.out.printf(Locale.ROOT, "  %8.3f,%9.3f %6d  %d works%n", q[0], q[1], (int) q[2], w.size());
            for (int i = 0; i < Math.min(4, w.size()); i++) {
                System.out.println("        " + w.get(i).name() + " (" + w.get(i).kind() + ", "
                        + w.get(i).from() + (w.get(i).to() == null ? "" : "-" + w.get(i).to()) + ")");
            }
        }
        System.out.println("\\n=== periodsAt: the climate of the era ===");
        for (double[] q : new double[][]{{20.68, -88.57, 900}, {17.39, 78.49, 1877},
                {51.5074, -0.1278, 1816}, {-13.5163, -71.9785, 1650}, {30.9625, 46.1031, -2500}}) {
            Climate c = periodsAt(q[0], q[1], (int) q[2]);
            System.out.printf(Locale.ROOT, "  %8.3f,%9.3f %6d  %s  (%.2f C, %.0f%% rain, %.2f harvest)%n",
                    q[0], q[1], (int) q[2],
                    c.plain() ? "no named period reaches it" : c.periods().get(0).name()
                            + " and " + (c.periods().size() - 1) + " more",
                    c.temperatureCelsius(), c.rainPercent(), c.harvestFraction());
        }
        System.out.println("\\n=== starsOver: the sky of the age ===");
        for (double[] q : new double[][]{{30.9625, 46.1031, -2500}, {17.385, 78.4867, 1948}}) {
            double jd = SkyStars.julianDay((int) q[2], 6, 21, 22.0d);
            Sky s = starsOver(q[0], q[1], jd, 10.0d, 4.0d);
            System.out.printf(Locale.ROOT, "  %8.3f,%9.3f %6d  %d stars up, pole star %s%n",
                    q[0], q[1], (int) q[2], s.above().size(),
                    s.poleStar() == null ? "none" : s.poleStar().name());
            if (s.brightest() != null) {
                System.out.println("        brightest: " + s.brightest().name() + " "
                        + s.brightest().where());
            }
        }
        System.out.println("\\n=== eclipseAt: what the sky did in these years ===");
        for (double[] q : new double[][]{{26.0, 32.0, 2025, 2028}, {36.36, 43.15, -765, -760},
                {40.5, 34.0, -586, -582}}) {
            List<Eclipse> e = eclipseAt(q[0], q[1], (int) q[2], (int) q[3], 0.05d);
            System.out.printf(Locale.ROOT, "  %7.2f,%8.2f %d..%d  %d seen%n", q[0], q[1],
                    (int) q[2], (int) q[3], e.size());
            for (int i = 0; i < Math.min(3, e.size()); i++) {
                Eclipse x = e.get(i);
                System.out.printf(Locale.ROOT, "        %d-%02d-%02d %-8s %s at %4.1f h UT%n",
                        x.year(), x.month(), x.day(), x.type(), x.howMuch(), x.utHours());
            }
        }
    }
}
''')
print("lifted the six step-35 hooks")
PY

# javax.annotation.Nullable is the one thing the hooks need that is not in the JDK
mkdir -p "$WORK/stub/javax/annotation"
cat > "$WORK/stub/javax/annotation/Nullable.java" <<'EOF'
package javax.annotation;
import java.lang.annotation.*;
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.METHOD, ElementType.FIELD, ElementType.PARAMETER, ElementType.TYPE_USE})
public @interface Nullable {}
EOF

cd "$WORK"
echo "compiling the three sky registers ..."
"$JDK/bin/javac" -encoding UTF-8 -Xlint:all -cp "$GSON" -d out $(find src -name '*.java')
echo "compiling the two lifted runners ..."
"$JDK/bin/javac" -encoding UTF-8 -nowarn -proc:none -cp "$GSON:out" \
  -sourcepath "$MOD/src/main/java:$WORK/stub" -d out src2/com/eternalengine/sky/*.java

echo
echo "==================== the sky part of /ee check ===================="
"$JDK/bin/java" -Xmx2g -Dfile.encoding=UTF-8 -cp "$GSON:out:$RES" \
  com.eternalengine.sky.SkyCheckRun | tee "$REPORT"
BAD=${PIPESTATUS[0]}
echo
echo "==================== the six step-35 Terra++ hooks ===================="
"$JDK/bin/java" -Xmx2g -Dfile.encoding=UTF-8 -cp "$GSON:out:$RES" \
  com.eternalengine.sky.HooksRun | tee -a "$REPORT"
echo
echo "report: $REPORT"
exit $BAD
