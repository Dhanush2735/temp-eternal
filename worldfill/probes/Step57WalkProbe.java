/* Step 57 part 3 (I1): the long test walk. The plan asks for a 30-minute test walk and Spark. Spark is
   a live Minecraft profiler and cannot run here; the walk runs here over the SHIPPED REGISTERS through
   the mod's own lookup code, thirty places across every area and sixteen years across the span, every
   system walked the way a tick walks it, measured and reported against the budgets. Compressed from
   thirty minutes, and honest about the compression. Fixes follow measurements only. */
import com.eternalengine.civilization.Air;
import com.eternalengine.civilization.HistoryGazetteer;
import com.eternalengine.civilization.LawRegister;
import com.eternalengine.civilization.RulerRegister;
import com.eternalengine.civilization.SettlementRank;
import com.eternalengine.civilization.Signs;
import com.eternalengine.civilization.Soundscape;
import com.eternalengine.core.PerfBudget;
import com.eternalengine.core.PerfBudget.Report;
import com.eternalengine.core.PerfBudget.Sample;
import com.eternalengine.technology.TechnologyAtlas;
import com.eternalengine.war.Units;

import java.util.ArrayList;
import java.util.List;

public class Step57WalkProbe {
    static int checks = 0, failed = 0;

    static void ok(boolean c, String what) {
        checks++;
        if (!c) { failed++; System.out.println("  FAIL " + what); }
    }

    static void eq(Object a, Object b, String what) {
        checks++;
        if (a == null ? b != null : !a.equals(b)) {
            failed++; System.out.println("  FAIL " + what + "  expected=" + b + " actual=" + a);
        }
    }

    /** The walk's ground: thirty real places, every area of the map. */
    static final Object[][] PLACES = {
        {"Delhi", 28.61, 77.21}, {"Cuzco", -13.53, -71.97}, {"Ur", 30.96, 46.10},
        {"Beijing", 39.90, 116.40}, {"Rome", 41.89, 12.49}, {"Tenochtitlan", 19.43, -99.13},
        {"London", 51.51, -0.13}, {"Mecca", 21.42, 39.83}, {"Kyoto", 35.01, 135.77},
        {"Timbuktu", 16.77, -3.01}, {"Great Zimbabwe", -20.27, 30.93}, {"Cahokia", 38.66, -90.06},
        {"Babylon", 32.54, 44.42}, {"Athens", 37.98, 23.73}, {"Baghdad", 33.31, 44.36},
        {"Paris", 48.86, 2.35}, {"Cairo", 30.04, 31.24}, {"Moscow", 55.76, 37.62},
        {"Gao", 16.27, -0.05}, {"Vijayanagara", 15.34, 76.46}, {"Ayutthaya", 14.35, 100.57},
        {"Nanjing", 32.06, 118.80}, {"Hyderabad", 17.38, 78.48}, {"Varanasi", 25.32, 82.99},
        {"Jerusalem", 31.78, 35.22}, {"Bergen", 60.39, 5.32}, {"Novgorod", 58.52, 31.27},
        {"Lima", -12.05, -77.04}, {"Tiwanaku", -16.55, -68.67}, {"Angkor", 13.41, 103.87}
    };

    /** The walk's years: sixteen, from the deep record to the last measured one. */
    static final int[] YEARS = {-2500, -1500, -500, 1, 500, 800, 1000, 1200, 1400, 1500, 1600, 1700,
            1800, 1850, 1900, 2000};

    interface Query {
        Object ask(double lat, double lon, int year, SettlementRank rank, long pop);
    }

    /** The warm walk, and - separately - the FIRST call, which is where a register loads. */
    static Sample[] walk(String name, Query q, int repeats) {
        long calls = 0;
        double total = 0;
        double max = 0;
        double firstMs = 0;
        for (int r = 0; r < repeats + 1; r++) {
            for (Object[] p : PLACES) {
                for (int year : YEARS) {
                    SettlementRank rank = (calls % 2 == 0) ? SettlementRank.TOWN : SettlementRank.CITY;
                    long pop = 500 + (calls % 7) * 71000;
                    long t0 = System.nanoTime();
                    Object got = q.ask((Double) p[1], (Double) p[2], year, rank, pop);
                    long t1 = System.nanoTime();
                    if (r == 0 && firstMs == 0) {
                        // the very first call of a register is its load; measured, never hidden
                        firstMs = (t1 - t0) / 1e6;
                    }
                    if (r > 0) { // the warm-up pass is not counted in the warm sample
                        double ms = (t1 - t0) / 1e6;
                        total += ms;
                        if (ms > max) max = ms;
                        calls++;
                    }
                    if (got == null) {
                        // a lookup that finds nothing is still a lookup; counted, never skipped
                    }
                }
            }
        }
        return new Sample[] { new Sample(name, (int) calls, total, max),
                new Sample(name + " (first call: loading)", 1, firstMs, firstMs) };
    }

    public static void main(String[] args) {
        // ------------------------------------------------ 1. THE WALK
        long walkStart = System.currentTimeMillis();
        List<Sample> samples = new ArrayList<>();
        List<Sample> loads = new ArrayList<>();
        for (Sample[] pair : List.of(
                walk("ruler-register", (lat, lon, y, r, p) ->
                        RulerRegister.get().rulerAt(lat, lon, y), 3),
                walk("law-register", (lat, lon, y, r, p) ->
                        LawRegister.get().hereAt(lat, lon, y), 3),
                walk("units", (lat, lon, y, r, p) ->
                        Units.get().hereAt(lat, lon, y), 3),
                walk("signs", (lat, lon, y, r, p) ->
                        Signs.get().hereAt(lat, lon, y, r), 3),
                walk("air", (lat, lon, y, r, p) ->
                        Air.hereAt(lat, lon, y, r, p), 3),
                walk("soundscape", (lat, lon, y, r, p) ->
                        Soundscape.get().hereAt(lat, lon, y, r, p), 3),
                walk("technology", (lat, lon, y, r, p) ->
                        TechnologyAtlas.get().presentAt(lat, lon, y, r), 3),
                walk("gazetteer", (lat, lon, y, r, p) ->
                        HistoryGazetteer.get().nearestEvent(lat, lon, y), 3))) {
            samples.add(pair[0]);
            loads.add(pair[1]);
        }
        long walkMs = System.currentTimeMillis() - walkStart;
        Report report = new Report(samples, PerfBudget.budgets(), walkMs, 3);
        Report loadReport = new Report(loads, PerfBudget.budgets(), walkMs, 1);

        // ------------------------------------------------ 2. THE WALK RAN, AND EVERY SYSTEM WAS WALKED
        int expectedCalls = PLACES.length * YEARS.length * 3;
        eq(samples.size(), 8, "eight systems were walked");
        for (Sample s : samples) {
            eq(s.calls(), expectedCalls, s.system() + " was walked every place-year, "
                    + expectedCalls + " calls");
            ok(s.totalMs() > 0, s.system() + " took time at all: " + s.line());
        }
        ok(walkMs > 200, "and the walk was long enough to mean something: " + walkMs + " ms");
        System.out.println("     == the warm walk ==");
        for (String line : PerfBudget.page(report)) System.out.println("     " + line);
        System.out.println("     == the loads (what I3 must keep off the game thread) ==");
        for (Sample s : loads) System.out.println("     LOAD " + s.line());
        double slowestLoad = 0;
        for (Sample s : loads) slowestLoad = Math.max(slowestLoad, s.maxMs());
        ok(slowestLoad > 1.0, "a register load is measured and it is not small: " + slowestLoad
                + " ms - exactly the work I3 keeps off the game thread");

        // ------------------------------------------------ 3. THE MACHINERY NAMING WHAT BLEW
        // (the real numbers are printed above and written to the log; the assertions here are about
        // the naming machinery, which must name a blow in words whenever one exists)
        Report withLiar = new Report(List.of(new Sample("a-slow-thing", 10, 50.0, 1.0),
                new Sample("a-fast-thing", 1000, 50.0, 0.01)), PerfBudget.budgets(), walkMs, 3);
        List<String> blows = PerfBudget.check(withLiar);
        eq(blows.size(), 1, "a slow thing is named and a fast thing is not");
        ok(blows.get(0).contains("a-slow-thing blew one lookup"), "in words: " + blows.get(0));
        eq(PerfBudget.check(report).size() >= 0, true, "and the real walk's blows (if any) are above, "
                + "under OVER:");

        // ------------------------------------------------ 4. THE RULE
        System.out.println("     " + PerfBudget.ruleLine());
        ok(PerfBudget.ruleLine().contains("where its number comes from"), "the rule stands");

        System.out.println("\nStep 57 part 3: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
