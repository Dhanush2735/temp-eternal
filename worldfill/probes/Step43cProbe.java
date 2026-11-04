import com.eternalengine.civilization.Air;
import com.eternalengine.civilization.CountryGrid;
import com.eternalengine.civilization.SettlementRank;
import com.eternalengine.climate.ClimatePeriods;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Step 43 part 4 (J4, sky and air: smoke, haze, dust).
 *
 * <p>The check that matters most is the one that looks like a bug report: taking the first active
 * climate period naively puts <b>100% of the world in drought from 2000 BC to AD 1800</b>, because
 * the Meghalayan stage is recorded with {@code radiusKm = 0} — "everywhere" — at severity 1. So
 * the severity gate is not a refinement here; it is the whole difference between a geological
 * background and the worst year to be alive.
 */
public class Step43cProbe {

    static int checks;
    static final List<String> problems = new ArrayList<>();

    static void check(String what, boolean ok, String detail) {
        checks++;
        if (!ok) {
            problems.add(what + " -- " + detail);
            System.out.println("FAIL " + what);
            System.out.println("       " + detail);
        } else {
            System.out.println("ok   " + what);
        }
    }

    static Air.Here at(String name, double lat, double lon, int year, long pop) {
        Air.Here h = Air.hereAt(lat, lon, year, SettlementRank.CITY, pop);
        System.out.printf("     %-18s sky=%-20s smoke=%d dust=%d haze=%d%n",
                name, h.sky(), h.smoke(), h.dust(), h.haze());
        System.out.printf("     %-18s   %s%n", "", h.line());
        return h;
    }

    public static void main(String[] args) {
        System.out.println("=== 1. the Meghalayan trap: a global stage is not weather ===");
        // radiusKm 0 means "everywhere", severity 1 means "barely anything". A naive reading of
        // the climate register says the whole world was in drought for 3,800 years.
        ClimatePeriods cp = ClimatePeriods.get();
        check("the climate register loads", cp.loaded() && cp.count() > 0,
                "loaded=" + cp.loaded() + " count=" + cp.count());
        Air.Here rome1000 = at("Rome 1000", 41.89, 12.49, 1000, 40000L);
        check("a global severity-1 stage does NOT make the air dusty", rome1000.dust() == 0,
                "Rome 1000 dust=" + rome1000.dust() + " (the Meghalayan stage runs -2250..1850)");

        System.out.println();
        System.out.println("=== 2. but a real volcanic winter does ===");
        Air.Here tambora = at("Berlin 1816", 52.52, 13.40, 1816, 200000L);
        Air.Here y536 = at("Rome 536", 41.89, 12.49, 536, 30000L);
        check("Tambora's year without a summer dims the sky", tambora.haze() >= 2,
                "Berlin 1816 haze=" + tambora.haze());
        check("the volcanic winter of 536 dims the sky", y536.haze() >= 2,
                "Rome 536 haze=" + y536.haze());
        Air.Here berlin1810 = at("Berlin 1810", 52.52, 13.40, 1810, 200000L);
        check("and six years earlier it does not", berlin1810.haze() < tambora.haze(),
                "1810 haze=" + berlin1810.haze() + " against 1816 haze=" + tambora.haze());

        System.out.println();
        System.out.println("=== 3. drought puts dust up ===");
        Air.Here sahara = at("Sahara -2000", 22.0, 15.0, -2000, 0L);
        check("the end of the African Humid Period is dusty", sahara.dust() >= 2,
                "Sahara -2000 dust=" + sahara.dust());
        Air.Here delhi1899 = at("Delhi 1899", 28.61, 77.21, 1899, 200000L);
        check("the failed monsoon of 1896-99 is dusty", delhi1899.dust() >= 1,
                "Delhi 1899 dust=" + delhi1899.dust());

        System.out.println();
        System.out.println("=== 4. smoke follows the ironworks, per country and dated ===");
        Air.Here manc1850 = at("Manchester 1850", 53.48, -2.24, 1850, 400000L);
        Air.Here manc1700 = at("Manchester 1700", 53.48, -2.24, 1700, 10000L);
        Air.Here beijing1850 = at("Beijing 1850", 39.90, 116.40, 1850, 600000L);
        check("industrial Manchester is smoky", manc1850.smoke() >= 2,
                "Manchester 1850 smoke=" + manc1850.smoke());
        check("and 150 years earlier it is not", manc1700.smoke() < manc1850.smoke(),
                "1700 smoke=" + manc1700.smoke() + " against 1850 smoke=" + manc1850.smoke());
        check("Beijing in 1850 is not yet industrial", beijing1850.smoke() < manc1850.smoke(),
                "Beijing 1850 smoke=" + beijing1850.smoke()
                        + " (the ironworks reach China in 1905)");

        System.out.println();
        System.out.println("=== 5. every town with hearths is a little smoky ===");
        Air.Here hamlet = at("a hamlet, 1300", 52.0, 0.5, 1300, 40L);
        Air.Here city = at("a city, 1300", 52.0, 0.5, 1300, 100000L);
        check("a city is smokier than a hamlet of the same year",
                city.smoke() >= hamlet.smoke(), "hamlet=" + hamlet.smoke() + " city=" + city.smoke());
        Air.Here empty = at("empty steppe", 48.0, 68.0, 1300, 0L);
        check("with nobody in it there is no smoke at all", empty.smoke() == 0,
                "empty smoke=" + empty.smoke());

        System.out.println();
        System.out.println("=== 6. most of the world, most of the time, has clear air ===");
        // Two of these years are chosen to fall inside a volcanic winter (536 and 1816), because
        // they last two or three years each and a century-spaced sweep would step over every one
        // and report that the haze never fires.
        int[] years = {-2000, -1000, 0, 500, 536, 1000, 1300, 1500, 1700, 1800, 1816, 1850, 1900, 1950, 2000};
        int total = 0, clear = 0, smoky = 0, dusty = 0, hazy = 0;
        for (int year : years) {
            int yT = 0, yC = 0, yS = 0, yD = 0, yH = 0;
            for (double lat = -56; lat <= 70; lat += 8.0d) {
                for (double lon = -178; lon <= 178; lon += 8.0d) {
                    String cc = CountryGrid.get().codeAt(lat, lon);
                    if (cc == null || cc.isBlank()) {
                        continue;
                    }
                    Air.Here h = Air.hereAt(lat, lon, year, SettlementRank.TOWN, 5000L);
                    total++;
                    yT++;
                    if (h.clear()) {
                        clear++;
                        yC++;
                    }
                    if (h.smoke() > 0) {
                        smoky++;
                        yS++;
                    }
                    if (h.dust() > 0) {
                        dusty++;
                        yD++;
                    }
                    if (h.haze() > 0) {
                        hazy++;
                        yH++;
                    }
                }
            }
            System.out.printf(Locale.ROOT, "     %6d  %5d places  %4d clear  %4d smoky  %4d dusty"
                    + "  %4d hazy%n", year, yT, yC, yS, yD, yH);
        }
        check("the world is not uniformly filthy", clear * 100 / Math.max(1, total) >= 20,
                clear + " of " + total + " place-years had clear air");
        check("but smoke does reach a real share of the modern world", smoky > 0,
                smoky + " place-years had smoke");
        System.out.printf(Locale.ROOT, "     --- %d place-years: %d clear, %d smoky, %d dusty, "
                + "%d hazy%n", total, clear, smoky, dusty, hazy);

        System.out.println();
        System.out.println("=== the sky, in the voice of the register ===");
        Object[][] spots = {{53.48, -2.24, 1850, 400000L, "Manchester 1850"},
            {53.48, -2.24, 1700, 10000L, "Manchester 1700"},
            {52.52, 13.40, 1816, 200000L, "Berlin 1816"},
            {41.89, 12.49, 536, 30000L, "Rome 536"},
            {22.0, 15.0, -2000, 0L, "Sahara 2000BC"},
            {39.90, 116.40, 1000, 400000L, "Kaifeng 1000"},
            {-13.53, -71.97, 1400, 20000L, "Cuzco 1400"},
            {48.86, 2.35, 1900, 2000000L, "Paris 1900"}};
        for (Object[] p : spots) {
            System.out.printf("     %-16s %s%n", p[4],
                    Air.lineAt((Double) p[0], (Double) p[1], (Integer) p[2],
                            SettlementRank.CITY, (Long) p[3]));
        }

        System.out.println();
        System.out.println(checks + " checks, " + problems.size() + " problem(s)");
        if (!problems.isEmpty()) {
            for (String p : problems) {
                System.out.println("  " + p);
            }
            System.exit(1);
        }
    }
}
