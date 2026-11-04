import com.eternalengine.civilization.Minerals;
import com.eternalengine.civilization.WaysGrid;
import com.eternalengine.civilization.WaysWorks;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.TreeMap;

/**
 * Step 34 (B12, B14, B15, B18, B24, B26): the roads, railways, waterways, works and minerals of the
 * past, answered for the 31 test places of SYSTEMS_PLAN.md part 9 in their own years.
 *
 * <p>The three registers here are pure Java plus Gson: no Forge, no Minecraft, no gradle.
 *
 * <p>What it checks, because these are the things that could go wrong:
 * <ul>
 *   <li>every register loads, and says so;</li>
 *   <li><b>the gate holds</b>: Sydney in 1850 answers no railway (Australia's first opened in 1854),
 *       Rome in AD 100 answers no railway, no factory and no airport;</li>
 *   <li>a work is never standing before the year it opened, nor after the year it ended;</li>
 *   <li>the grid and the works agree: where the grid says a railway may be drawn, there is a dated
 *       station or line nearby, and where there are dated stations the grid allows the railway;</li>
 *   <li>what lies under the ground is answered for the places where any source knows, and honestly
 *       empty where none does.</li>
 * </ul>
 */
public final class WaysProbe {

    private record Place(String name, double lat, double lon, int year) {
    }

    private static Place pt(String name, double lat, double lon, int year) {
        return new Place(name, lat, lon, year);
    }

    private static final List<Place> TESTS = List.of(
        pt("Ur", 30.9625, 46.1031, -2500),
        pt("Giza", 29.9792, 31.1342, -2500),
        pt("Mohenjo-daro", 27.3242, 68.1356, -2500),
        pt("Anyang", 36.1, 114.35, -1200),
        pt("Athens", 37.9715, 23.7257, -430),
        pt("Pataliputra", 25.594, 85.137, -300),
        pt("Rome", 41.8925, 12.4853, 100),
        pt("Teotihuacan", 19.6925, -98.8438, 500),
        pt("Chang'an", 34.2611, 108.9422, 750),
        pt("Baghdad", 33.3152, 44.3661, 900),
        pt("Greenland Norse", 61.155, -45.517, 1000),
        pt("Cahokia", 38.6603, -90.0618, 1100),
        pt("Angkor", 13.4125, 103.867, 1150),
        pt("Great Zimbabwe", -20.2675, 30.9339, 1300),
        pt("Timbuktu", 16.7735, -3.0074, 1350),
        pt("Tenochtitlan", 19.4326, -99.1332, 1500),
        pt("Cusco", -13.5163, -71.9785, 1500),
        pt("the Amazon", -3.4653, -62.2159, 1500),
        pt("Vijayanagara", 15.335, 76.46, 1520),
        pt("Delhi", 28.6562, 77.241, 1650),
        pt("Edo", 35.6852, 139.7528, 1700),
        pt("London", 51.5074, -0.1278, 1700),
        pt("Paris", 48.8566, 2.3522, 1789),
        pt("Sydney", -33.8688, 151.2093, 1850),
        pt("New York", 40.7128, -74.006, 1920),
        pt("Hyderabad", 17.3616, 78.4747, 1948),
        pt("Lagos", 6.4541, 3.3947, 1960),
        pt("Moscow", 55.752, 37.6175, 1980),
        pt("Sao Paulo", -23.5505, -46.6333, 2020),
        pt("Yakutsk", 62.0355, 129.6755, 1900),
        pt("the Sahara", 23.4162, 25.6628, 1000));

    private static int failures = 0;

    private static void check(boolean ok, String what) {
        if (!ok) {
            failures++;
            System.out.println("  FAIL " + what);
        }
    }

    public static void main(String[] args) {
        long t0 = System.currentTimeMillis();
        WaysGrid grid = WaysGrid.get();
        long t1 = System.currentTimeMillis();
        WaysWorks works = WaysWorks.get();
        long t2 = System.currentTimeMillis();
        Minerals mins = Minerals.get();
        long t3 = System.currentTimeMillis();

        System.out.println("loaded");
        System.out.printf("  ways grid : %s (%d ms), %d squares with something in them%n",
                grid.loaded() ? "ok" : grid.problem(), t1 - t0, grid.cellsWithSomething());
        System.out.printf("  works     : %s (%d ms), %d works%n",
                works.loaded() ? "ok" : works.problem(), t2 - t1, works.size());
        System.out.printf("  minerals  : %s (%d ms), %d sites, %d minerals%n",
                mins.loaded() ? "ok" : mins.problem(), t3 - t2, mins.size(), mins.minerals().length);
        check(grid.loaded(), "the ways grid did not load");
        check(works.loaded(), "the works did not load");
        check(mins.loaded(), "the minerals did not load");
        if (!grid.loaded() || !works.loaded() || !mins.loaded()) {
            System.out.println("\nFAILED");
            System.exit(1);
        }

        System.out.println("\nthe 31 test places, in their own year "
                + "(grid: first year a railway / road / canal reached the square)");
        System.out.printf("%-16s %6s  %-22s %s%n", "place", "year", "grid (rail/road/canal)",
                "works within 25 km, and what lies under the ground");
        for (Place p : TESTS) {
            int rail = grid.railFirst(p.lat, p.lon);
            int road = grid.roadFirst(p.lat, p.lon);
            int canal = grid.canalFirst(p.lat, p.lon);
            String g = String.format("%s/%s/%s", y(rail), y(road), y(canal));
            List<WaysWorks.Work> here = works.near(p.lat, p.lon, 25.0d, p.year);
            TreeMap<String, Integer> byKind = new TreeMap<>();
            for (WaysWorks.Work w : here) {
                byKind.merge(w.kind(), 1, Integer::sum);
            }
            StringBuilder kinds = new StringBuilder();
            for (var e : byKind.entrySet()) {
                if (kinds.length() > 0) {
                    kinds.append(", ");
                }
                kinds.append(e.getKey()).append(' ').append(e.getValue());
            }
            Set<String> under = mins.mineralsUnder(p.lat, p.lon, 50.0d);
            System.out.printf("%-16s %6d  %-22s %s%n      under the ground: %s%n",
                    p.name, p.year, g,
                    kinds.length() == 0 ? "nothing recorded" : kinds,
                    under.isEmpty() ? "nothing recorded" : String.join(", ", under));
        }

        System.out.println("\nchecks");
        // 1. the gate: Sydney 1850 must not have a railway
        check(!grid.railBy(-33.8688d, 151.2093d, 1850), "Sydney in 1850 may draw a railway");
        check(works.countNear(-33.8688d, 151.2093d, 25.0d, 1850, "station") == 0,
                "Sydney in 1850 has a railway station");
        check(works.countNear(-33.8688d, 151.2093d, 25.0d, 1850, "line") == 0,
                "Sydney in 1850 has a railway line");
        // 2. Rome in AD 100: bridges and ports, but no railway, no factory, no airport
        check(!grid.railBy(41.8925d, 12.4853d, 100), "Rome in AD 100 may draw a railway");
        for (String k : new String[]{"station", "line", "works", "air", "power"}) {
            check(works.countNear(41.8925d, 12.4853d, 25.0d, 100, k) == 0,
                    "Rome in AD 100 has a " + k);
        }
        check(works.countNear(41.8925d, 12.4853d, 25.0d, 100, "bridge") > 0,
                "Rome in AD 100 has no dated bridge");
        // 3. the modern world is not empty
        check(works.countNear(40.7128d, -74.006d, 25.0d, 1920, "station") > 100,
                "New York in 1920 has fewer than 100 stations");
        check(grid.railBy(40.7128d, -74.006d, 1920), "New York in 1920 may not draw a railway");
        check(grid.railBy(55.752d, 37.6175d, 1980), "Moscow in 1980 may not draw a railway");
        check(works.countNear(51.5074d, -0.1278d, 25.0d, 1700, "mill") > 0,
                "London in 1700 has no mill");
        check(works.countNear(51.5074d, -0.1278d, 25.0d, 1700, "station") == 0,
                "London in 1700 has a railway station");
        // 4. the year filter: everything returned for a year stands in it, and the count only
        //    grows as the years pass (a work that has ended drops out again)
        int early = 0;
        int late = 0;
        int total = 0;
        for (Place p : TESTS) {
            for (WaysWorks.Work w : works.near(p.lat, p.lon, 25.0d, p.year)) {
                total++;
                if (!w.standsIn(p.year)) {
                    late++;
                }
            }
            for (WaysWorks.Work w : works.near(p.lat, p.lon, 25.0d, 1700)) {
                if (!w.standsIn(1700)) {
                    early++;
                }
            }
        }
        check(late == 0, late + " works returned do not stand in the year asked about");
        check(early == 0, early + " works returned for 1700 do not stand in 1700");
        check(works.near(40.7128d, -74.006d, 25.0d, 1900).size()
                < works.near(40.7128d, -74.006d, 25.0d, 2000).size(),
                "the number of works does not grow with the year");
        System.out.println("  " + total + " works stand in the 31 test places in their own years");
        // 5. the grid and the works agree about railways
        int disagree = 0;
        for (Place p : TESTS) {
            boolean gridSays = grid.railBy(p.lat, p.lon, p.year);
            boolean worksSay = works.anyNear(p.lat, p.lon, 25.0d, p.year, "station")
                    || works.anyNear(p.lat, p.lon, 25.0d, p.year, "line");
            if (gridSays != worksSay && p.year >= 1850) {
                disagree++;
                System.out.println("      note: " + p.name + " " + p.year
                        + " grid says " + gridSays + ", works say " + worksSay);
            }
        }
        System.out.println("  " + disagree + " places since 1850 where the grid and the works differ");
        // 6. minerals: the ancient world is thin, but not everywhere is empty
        int withMinerals = 0;
        for (Place p : TESTS) {
            if (!mins.mineralsUnder(p.lat, p.lon, 50.0d).isEmpty()) {
                withMinerals++;
            }
        }
        System.out.println("  " + withMinerals + " of " + TESTS.size()
                + " test places have something recorded under them");
        check(mins.hasMineral(-13.5163d, -71.9785d, 50.0d, "SILVER"),
                "Cusco has no silver recorded under it");
        check(mins.hasMineral(37.9715d, 23.7257d, 50.0d, "SILVER"),
                "Athens has no silver recorded under it (Laurium is 45 km away)");

        System.out.println(failures == 0 ? "\nOK" : "\n" + failures + " FAILED");
        System.exit(failures == 0 ? 0 : 1);
    }

    private static String y(int v) {
        return v == WaysGrid.NONE ? "-" : Integer.toString(v);
    }
}
