import com.eternalengine.civilization.Civilization;
import com.eternalengine.civilization.CivilizationManager;
import com.eternalengine.civilization.HistoricalPresence;

import java.util.Optional;

/**
 * Board 17: <b>does anyone stand after their own civilization has fallen?</b>
 *
 * <p>Found by reading a real save: Anyang in 430 BC held 29 Shang townspeople (the Shang fell in
 * 1046 BC), and one person in five in the whole register stood under a civilization that had already
 * ended. The cause was {@code HistoricalPresence.spawnCivId()}: it answered from the site's
 * {@code civHint}, which names who FOUNDED a place, without asking the year.
 *
 * <p>This probe asks the same question the game asks, at the places that were actually played, and
 * then sweeps the world: <b>every answer must be a sentinel or a civilization that stands in that
 * year.</b> It is the guard, not a demonstration — if the old behaviour comes back, this goes red.
 */
public final class EraCivProbe {
    static int ok;
    static int bad;

    static void check(boolean good, String what, String detail) {
        if (good) {
            ok++;
            System.out.println("OK   " + what);
        } else {
            bad++;
            System.out.println("FAIL " + what + "  --  " + detail);
        }
    }

    static boolean sentinel(String id) {
        return id == null || id.isBlank() || id.equals("neutral") || id.equals("present")
                || id.equals("ohm") || id.equals("witness");
    }

    /** The five places the user actually played, plus the sharpest cases from the route. */
    static final Object[][] PLAYED = {
            // name, lat, lon, year, what the answer must NOT be (null = anything alive is fine)
            {"Ur", 30.9630, 46.1030, -2500, null},
            {"Giza", 29.9792, 31.1338, -2500, null},
            {"Anyang", 36.1257, 114.3132, -1200, null},
            {"Anyang", 36.1257, 114.3132, -430, "china_shang"},   // the save's defect: 616 years after the fall
            {"Indus site (32.45,69.04)", 32.4500, 69.0400, -1200, "indus_valley"}, // a century after the fall
            {"Mohenjo-daro", 27.3294, 68.1386, -2500, null},
            {"Rome", 41.9028, 12.4964, 100, null},
            {"Athens", 37.9838, 23.7275, -430, null},
            {"Tenochtitlan", 19.4326, -99.1332, 1500, null},
            {"Cusco", -13.5319, -71.9675, 1500, null},
            {"Baghdad", 33.3152, 44.3661, 900, null},
            {"London", 51.5074, -0.1278, 1700, null},
            {"Hyderabad", 17.3850, 78.4867, 1948, null},
    };

    public static void main(String[] args) {
        CivilizationManager m = new CivilizationManager();
        m.loadCivilizations(null, null);
        System.out.println("civilizations known: " + m.ids().size());

        for (Object[] row : PLAYED) {
            String name = (String) row[0];
            double lat = (Double) row[1];
            double lon = (Double) row[2];
            int year = (Integer) row[3];
            String forbidden = (String) row[4];

            HistoricalPresence.Result r = HistoricalPresence.query(m, lat, lon, year);
            String id = r.spawnCivId();
            Optional<Civilization> civ = m.getCivilization(id);
            String state;
            boolean alive;
            if (sentinel(id)) {
                state = "no civilization named (honest: the record names none)";
                alive = true;
            } else if (civ.isEmpty()) {
                state = "NOT IN THE TABLE";
                alive = false;
            } else {
                alive = civ.get().isActiveInYear(year);
                state = civ.get().name() + " (founded " + civ.get().foundingYear()
                        + ", fell " + civ.get().fallYear() + ")";
            }
            System.out.printf("  %-26s %6d  %-26s %s%n", name, year, id, state);
            check(alive, name + " " + year + ": the people belong to a civilization standing that year", id + " -> " + state);
            if (forbidden != null) {
                check(!forbidden.equals(id),
                        name + " " + year + ": not " + forbidden + " (that civilization had already fallen)",
                        "answered " + id);
            }
        }

        // The sweep: every continent, every era band, 6,000 points, 14 years each. Nothing may stand
        // under a civilization that is not alive in that year.
        int points = 0;
        int named = 0;
        int outside = 0;
        String firstWrong = null;
        java.util.Random rnd = new java.util.Random(20261023L);
        int[] years = {-3000, -2500, -1200, -430, 100, 500, 900, 1100, 1300, 1500, 1700, 1850, 1948, 2020};
        for (int i = 0; i < 6000; i++) {
            double lat = Math.toDegrees(Math.asin(2.0d * rnd.nextDouble() - 1.0d));
            if (Math.abs(lat) > 75) {
                continue;
            }
            double lon = rnd.nextDouble() * 360.0d - 180.0d;
            for (int year : years) {
                HistoricalPresence.Result r = HistoricalPresence.query(m, lat, lon, year);
                String id = r.spawnCivId();
                if (sentinel(id)) {
                    continue;
                }
                points++;
                Optional<Civilization> civ = m.getCivilization(id);
                if (civ.isEmpty()) {
                    outside++;
                    if (firstWrong == null) {
                        firstWrong = String.format(java.util.Locale.ROOT, "%.2f,%.2f %d -> %s (not in the table)",
                                lat, lon, year, id);
                    }
                    continue;
                }
                named++;
                if (!civ.get().isActiveInYear(year)) {
                    outside++;
                    if (firstWrong == null) {
                        firstWrong = String.format(java.util.Locale.ROOT, "%.2f,%.2f %d -> %s (%s, fell %d)",
                                lat, lon, year, id, civ.get().name(), civ.get().fallYear());
                    }
                }
            }
        }
        check(outside == 0,
                "the sweep: " + named + " named answers over the whole world, every one alive in its year",
                outside + " outside their civilization's years, e.g. " + firstWrong);

        System.out.println();
        System.out.println("EraCiv: " + ok + " passed, " + bad + " failed");
        if (bad > 0) {
            System.exit(1);
        }
    }
}
