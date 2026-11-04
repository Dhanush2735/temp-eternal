import com.eternalengine.civilization.Civilization;
import com.eternalengine.civilization.CivilizationManager;
import com.eternalengine.civilization.HistoricalPresence;
import com.eternalengine.civilization.WhoBelongsHere;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * Board 17b: <b>the sick, not just the newborn.</b>
 *
 * <p>The first fix taught the spawner to ask the year before it named anybody's people. That repairs
 * every person drawn from then on — and leaves everyone already standing in a saved world exactly as
 * the old rule made them, which is the world the defect was found in. {@link WhoBelongsHere} asks the
 * same question again of people who are already there, and this probe tests that rule directly, on
 * the tables, without a world:
 *
 * <ul>
 *   <li>names that are right are left alone (no churn, no coat of paint on a Roman);</li>
 *   <li>names that are wrong are replaced by a civilization that stands in that year, or by an honest
 *       "none" when nobody holds the ground;</li>
 *   <li>doing it twice changes nothing the second time;</li>
 *   <li>and over a spread of places and years, no repaired person is ever left outside their
 *       civilization's years.</li>
 * </ul>
 */
public final class RepairProbe {
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

    static boolean none(String id) {
        return id == null || id.isBlank() || id.equals("neutral") || id.equals("present")
                || id.equals("ohm") || id.equals("witness");
    }

    /** A person is in order when they name no civilization, or one that stood in that year. */
    static boolean honest(CivilizationManager m, String id, int year) {
        if (none(id)) {
            return true;
        }
        var civ = m.getCivilization(id);
        return civ.isPresent() && civ.get().isActiveInYear(year);
    }

    public static void main(String[] args) {
        CivilizationManager m = new CivilizationManager();
        m.loadCivilizations(null, null);
        System.out.println("civilizations known: " + m.ids().size());

        // ── 1. the two cases the save actually showed ────────────────────────────────────────────
        String anyang = WhoBelongsHere.rightCivFor(m, 36.1257, 114.3132, -430, "china_shang");
        check("china_zhou".equals(anyang),
                "Anyang 430 BC: a person carrying china_shang is put right (now " + anyang + ")",
                "still " + anyang + " — the Shang fell in 1046 BC");

        String indus = WhoBelongsHere.rightCivFor(m, 32.4500, 69.0400, -1200, "indus_valley_civilization");
        check(honest(m, indus, -1200),
                "the Indus site 1200 BC: a person carrying the dangling indus_valley_civilization id is put"
                        + " right (now " + indus + ")", "still " + indus);

        // ── 2. a name that is already right is not touched ───────────────────────────────────────
        String rome = WhoBelongsHere.rightCivFor(m, 41.9028, 12.4964, 100, "rome");
        check("rome".equals(rome), "Rome 100 CE: a Roman is left alone", "was changed to " + rome);
        String neutral = WhoBelongsHere.rightCivFor(m, 0.0, -140.0, 1500, "neutral");
        check("neutral".equals(neutral), "open ocean 1500: a person with no civilization is left alone",
                "was changed to " + neutral);
        String shangThen = WhoBelongsHere.rightCivFor(m, 36.1257, 114.3132, -1200, "china_shang");
        check("china_shang".equals(shangThen), "Anyang 1200 BC: a Shang is left alone",
                "was changed to " + shangThen);

        // ── 3. a polity spelling that names nothing ──────────────────────────────────────────────
        String jin = WhoBelongsHere.rightCivFor(m, 36.1257, 114.3132, -430, "jin");
        check(honest(m, jin, -430), "a person carrying the ruler-register spelling 'jin' is given a real"
                + " civilization in 430 BC (now " + jin + ")", "still " + jin);

        // ── 4. idempotent: the second pass changes nothing ───────────────────────────────────────
        String twice = WhoBelongsHere.rightCivFor(m, 36.1257, 114.3132, -430, anyang);
        check(java.util.Objects.equals(anyang, twice),
                "the repair is idempotent: running it again leaves " + anyang + " in place", "became " + twice);

        // ── 5. a spread of the world: nobody repaired is left outside their years ────────────────
        Random rnd = new Random(17L);
        List<String> ids = new ArrayList<>(m.ids());
        int years[] = {-3000, -2000, -1200, -430, 100, 900, 1500, 1948};
        int repaired = 0;
        int changed = 0;
        int wrong = 0;
        String firstWrong = null;
        for (int i = 0; i < 3000; i++) {
            double lat = -60.0 + rnd.nextDouble() * 130.0;
            double lon = -180.0 + rnd.nextDouble() * 360.0;
            int year = years[rnd.nextInt(years.length)];
            // the person is given a civilization that is almost never the right one for that year
            String carried = ids.get(rnd.nextInt(ids.size()));
            String after = WhoBelongsHere.rightCivFor(m, lat, lon, year, carried);
            if (after == null) {
                continue;
            }
            repaired++;
            if (!after.equals(carried)) {
                changed++;
            }
            if (!honest(m, after, year)) {
                wrong++;
                if (firstWrong == null) {
                    firstWrong = String.format(java.util.Locale.ROOT, "%.2f,%.2f in %d: %s -> %s",
                            lat, lon, year, carried, after);
                }
            }
        }
        check(repaired > 2500 && wrong == 0,
                "the sweep: " + repaired + " people asked again over 8 years, " + changed + " of them put"
                        + " right, and not one left outside their civilization's years",
                wrong + " left outside, e.g. " + firstWrong);

        // ── 6. the same answer as a fresh spawn at that place ───────────────────────────────────
        int same = 0;
        int differ = 0;
        for (int i = 0; i < 400; i++) {
            double lat = -60.0 + rnd.nextDouble() * 130.0;
            double lon = -180.0 + rnd.nextDouble() * 360.0;
            int year = years[rnd.nextInt(years.length)];
            String fresh = HistoricalPresence.query(m, lat, lon, year).spawnCivId();
            String repairedId = WhoBelongsHere.rightCivFor(m, lat, lon, year, "jin");
            if (fresh == null || fresh.isBlank()) {
                fresh = "neutral";
            }
            if (fresh.equals(repairedId)) {
                same++;
            } else {
                differ++;
            }
        }
        check(differ == 0, "a repaired person is given exactly what a person born there this year would"
                + " be given (" + same + " of " + (same + differ) + " agree)", differ + " disagree");

        System.out.println();
        System.out.println("Repair: " + ok + " passed, " + bad + " failed");
        if (bad > 0) {
            System.exit(1);
        }
    }
}
