import com.eternalengine.buildings.FamousBuildings;
import com.eternalengine.buildings.FamousBuildings.Building;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * Step 32 (B8, B16, B19): famous buildings, walls and ruins by year.
 *
 * Runs the mod's own register outside Minecraft, over the world-wide test set, and asks the two
 * questions that matter: does the right thing stand in the right year, and does nothing stand
 * before its time.
 */
public final class BuildingsProbe {

    static int ok;
    static int bad;

    /** name, lat, lon, year -- the world-wide test set (SYSTEMS_PLAN.md part 9). */
    static final Object[][] PLACES = {
        {"Ur", 30.9625, 46.1031, -2500}, {"Giza", 29.9792, 31.1342, -2500},
        {"Mohenjo-daro", 27.3242, 68.1356, -2500}, {"Anyang", 36.1000, 114.3500, -1200},
        {"Athens", 37.9838, 23.7275, -430}, {"Pataliputra", 25.6110, 85.1410, -300},
        {"Rome", 41.8902, 12.4922, 100}, {"Teotihuacan", 19.6925, -98.8438, 500},
        {"Chang'an", 34.2660, 108.9510, 750}, {"Baghdad", 33.3150, 44.3660, 900},
        {"Greenland Norse", 61.1550, -45.5170, 1000}, {"Cahokia", 38.6500, -90.0600, 1100},
        {"Angkor", 13.4125, 103.8670, 1150}, {"Great Zimbabwe", -20.2730, 30.9330, 1300},
        {"Timbuktu", 16.7730, -3.0070, 1350}, {"Tenochtitlan", 19.4330, -99.1330, 1500},
        {"Cusco", -13.5320, -71.9670, 1500}, {"the Amazon", -3.1000, -60.0000, 1500},
        {"Vijayanagara", 15.3350, 76.4600, 1520}, {"Delhi", 28.6139, 77.2090, 1650},
        {"Edo", 35.6895, 139.6917, 1700}, {"London", 51.5070, -0.1280, 1700},
        {"Paris", 48.8566, 2.3522, 1789}, {"Sydney", -33.8688, 151.2093, 1850},
        {"New York", 40.7128, -74.0060, 1920}, {"Hyderabad", 17.3616, 78.4747, 1948},
        {"Lagos", 6.5244, 3.3792, 1960}, {"Moscow", 55.7558, 37.6173, 1980},
        {"Sao Paulo", -23.5505, -46.6333, 2020}, {"Yakutsk", 62.0339, 129.7331, 1900},
        {"the Sahara", 23.0000, 11.0000, 1000},
    };

    static void check(boolean good, String what, String detail) {
        if (good) {
            ok++;
            System.out.println("OK   " + what);
        } else {
            bad++;
            System.out.println("FAIL " + what + "  -- " + detail);
        }
    }

    public static void main(String[] args) {
        long t0 = System.nanoTime();
        FamousBuildings f = FamousBuildings.get();
        check(f.loaded(), "the register loads: " + f.summary() + " in " + f.loadMillis()
            + " ms (" + f.estimatedCount() + " years estimated, " + f.withEndCount()
            + " with an end date, " + f.holyCount() + " also holy places)",
            String.valueOf(f.problem()));
        if (!f.loaded()) {
            System.out.println("\n" + ok + " ok, " + bad + " failed");
            System.exit(1);
        }

        // ---- 1. the world-wide test set --------------------------------------
        System.out.println("\n=== what stands in each test place (25 km) ===");
        int answered = 0;
        List<String> empty = new ArrayList<>();
        for (Object[] p : PLACES) {
            String name = (String) p[0];
            double lat = (Double) p[1];
            double lon = (Double) p[2];
            int year = (Integer) p[3];
            List<Building> near = f.near(lat, lon, year, 25.0d, Integer.MAX_VALUE);
            if (!near.isEmpty()) {
                answered++;
            } else {
                empty.add(name);
            }
            System.out.printf("  %-18s %6d  %3d  %s%n", name, year, near.size(),
                f.names(lat, lon, year, 25.0d, 4));
        }
        check(answered >= 28, answered + " of " + PLACES.length + " test places have something"
            + " standing in their year", "only " + answered);
        System.out.println("  empty: " + empty
            + "   (the Amazon and the Sahara are meant to be empty; Greenland Norse is a"
            + " gazetteer gap, see step32_part2_notes.md)");

        // ---- 2. nothing stands before its time --------------------------------
        System.out.println("\n=== nothing stands before its time ===");
        int violations = 0;
        int checked = 0;
        Random rnd = new Random(20261015L);
        List<Building> sample = new ArrayList<>();
        for (Object[] p : PLACES) {
            sample.addAll(f.near((Double) p[1], (Double) p[2], (Integer) p[3], 400.0d,
                Integer.MAX_VALUE));
        }
        for (Building b : sample) {
            checked++;
            if (b.standsIn(b.from() - 1)) {
                violations++;
                if (violations <= 5) {
                    System.out.println("    stands before it was built: " + b.name()
                        + " from " + b.from());
                }
            }
        }
        check(violations == 0, checked + " buildings near the test places: none stands in the year"
            + " before it was built", violations + " do");

        int standingAfterEnd = 0;
        for (Building b : sample) {
            if (b.to() != Integer.MAX_VALUE && b.standsIn(b.to())) {
                standingAfterEnd++;
                if (standingAfterEnd <= 5) {
                    System.out.println("    still standing in its end year: " + b.name()
                        + " " + b.from() + ".." + b.to());
                }
            }
        }
        check(standingAfterEnd == 0, "a building with an end year is gone by that year (B19 ruins)",
            standingAfterEnd + " are not");

        // ---- 3. a few sentences ----------------------------------------------
        System.out.println("\n=== what the player is told ===");
        // lat, lon, year
        double[][] tour = {
            {41.8902, 12.4922, 100}, {27.3242, 68.1356, -2500}, {15.3350, 76.4600, 1520},
            {19.6925, -98.8438, 500}, {51.5070, -0.1280, 1700}, {17.3616, 78.4747, 1948},
            {-20.2730, 30.9330, 1300}, {36.1000, 114.3500, -1200}, {25.6110, 85.1410, -300},
        };
        for (double[] t : tour) {
            System.out.printf("  %6d  %s%n", (int) t[2], f.line(t[0], t[1], (int) t[2], 25.0d, 3));
        }
        int silent = 0;
        for (double[] t : tour) {
            if (f.line(t[0], t[1], (int) t[2], 25.0d, 3).isEmpty()) {
                silent++;
            }
        }
        check(silent == 0, "every place on the tour gets a sentence", silent + " say nothing");

        // ---- 4. B19: ruins -------------------------------------------------------
        System.out.println("\n=== B19: in ruins by that year ===");
        int[][] ruins = {
            {15, 335000, 76, 460000, 1600},    // Hampi after 1565
            {15, 335000, 76, 460000, 1400},    // and not before it
            {27, 324200, 68, 135600, -1000},   // Mohenjo-daro after 1900 BC
            {27, 324200, 68, 135600, -2500},   // and not while it stood
            {41, 890200, 12, 492200, 1500},    // Rome: plenty in ruins by 1500
            {-20, 273000, 30, 933000, 1600},   // Great Zimbabwe after 1450
        };
        for (int[] t : ruins) {
            double lat = t[0] + t[1] / 1_000_000.0d;
            double lon = t[2] + t[3] / 1_000_000.0d;
            System.out.printf("  %6d  %s%n", t[4], f.ruinLine(lat, lon, t[4], 25.0d, 2));
        }
        boolean hampi1600 = f.ruinsNear(15.335, 76.46, 1600, 25.0d, 40).stream()
                .anyMatch(b -> b.name().contains("Hampi"));
        boolean hampi1400 = f.ruinsNear(15.335, 76.46, 1400, 25.0d, 40).stream()
                .anyMatch(b -> b.name().contains("Hampi"));
        boolean md1000bc = f.ruinsNear(27.3242, 68.1356, -1000, 25.0d, 40).stream()
                .anyMatch(b -> b.name().contains("Mohenjo-daro"));
        boolean md2500bc = f.ruinsNear(27.3242, 68.1356, -2500, 25.0d, 40).stream()
                .anyMatch(b -> b.name().contains("Mohenjo-daro"));
        check(hampi1600 && !hampi1400 && md1000bc && !md2500bc, "ruins are ruins after their end "
                + "year and not before: Hampi in 1600 but not 1400, Mohenjo-daro in 1000 BC but "
                + "not 2500 BC", "Hampi 1600 " + hampi1600 + ", Hampi 1400 " + hampi1400
                + ", Mohenjo-daro -1000 " + md1000bc + ", Mohenjo-daro -2500 " + md2500bc);
        check(f.ruinCount() > 400, f.ruinCount() + " buildings are known to be ruins (Wikidata "
                + "says so even where it never recorded the year they fell)", "too few");

        // ---- 5. B16: walls, gates and forts --------------------------------------
        System.out.println("\n=== B16: walls, gates and forts ===");
        double[][] def = {{41.8902, 12.4922, 300}, {41.8902, 12.4922, 100},
            {51.5070, -0.1280, 200}, {31.7760, 35.2350, 100}, {-20.2730, 30.9330, 1300}};
        for (double[] t : def) {
            System.out.printf("  %6d  %s%n", (int) t[2], f.defencesLine(t[0], t[1], (int) t[2], 25.0d, 3));
        }
        boolean rome300 = f.defencesNear(41.8902, 12.4922, 300, 25.0d, 40).stream()
                .anyMatch(b -> b.name().contains("Aurelian"));
        boolean rome100 = f.defencesNear(41.8902, 12.4922, 100, 25.0d, 40).stream()
                .anyMatch(b -> b.name().contains("Aurelian"));
        check(rome300 && !rome100, "walls stand in their own year: the Aurelian Walls in Rome in "
                + "300 and not in 100 (they were built from 271)", "300 " + rome300 + ", 100 " + rome100);
        check(f.defenceCount() > 1_000, f.defenceCount() + " walls, gates and forts (castles are "
                + "left out of B16: a castle is a fortified house, not a city's defences)",
                "too few");

        // ---- 6. is it fast enough to call per tick? ---------------------------
        long t1 = System.nanoTime();
        int calls = 20000;
        for (int i = 0; i < calls; i++) {
            Object[] p = PLACES[i % PLACES.length];
            f.near((Double) p[1], (Double) p[2], (Integer) p[3], 25.0d, 8);
        }
        long perCall = (System.nanoTime() - t1) / calls;
        System.out.println("\n" + calls + " lookups in " + (System.nanoTime() - t1) / 1_000_000
            + " ms (" + perCall / 1000 + " us each)");
        check(perCall < 500_000, "a lookup is fast enough to call while the player moves",
            perCall / 1000 + " us");

        System.out.println("\ntotal " + (System.nanoTime() - t0) / 1_000_000 + " ms");
        System.out.println(ok + " ok, " + bad + " failed");
        System.exit(bad == 0 ? 0 : 1);
    }
}
