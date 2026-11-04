package com.eternalengine.lifeprobe;

import com.eternalengine.people.LifeTable;
import com.eternalengine.people.LifeTable.Life;
import com.eternalengine.people.LifeTable.Marriage;
import com.eternalengine.people.LifeTable.Mortality;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Step 38 (D2, D17, and the life-span half of C20): the life table, checked outside the game.
 *
 * <p>The numbers in {@code curve()} are computed independently in Python by
 * {@code worldfill/build_life_table.py --selftest}, so this is a cross-check of two
 * implementations of the same arithmetic, not a restatement of the Java.
 */
public final class LifeRun {

    private static int checks = 0;
    private static int failed = 0;

    public static void main(String[] args) {
        LifeTable t = LifeTable.get();
        System.out.println("life table: " + t.source());
        System.out.println();

        ok(t.mortalityCount() == 30, "30 mortality rows, got " + t.mortalityCount());
        ok(t.marriageCount() == 14, "14 marriage rows, got " + t.marriageCount());
        System.out.println();

        lookup(t);
        curve(t);
        invariants(t);
        sampling(t);
        marriage(t);
        words(t);

        System.out.println();
        System.out.printf(Locale.ROOT, "%d checks passed, %d failed%n", checks - failed, failed);
        if (failed > 0) {
            System.exit(1);
        }
    }

    // ------------------------------------------------------------------ which row where

    private static void lookup(LifeTable t) {
        System.out.println("which regime:");
        String[][] cases = {
                {"Hyderabad 1500", "17.39", "78.49", "1500", "late_medieval"},
                {"Hyderabad 1348", "17.39", "78.49", "1348", "medieval_world"},
                {"Hyderabad 1948", "17.39", "78.49", "1948", "nineteen_hundred"},
                {"London 1300", "51.51", "-0.13", "1300", "medieval_europe"},
                {"London 1350", "51.51", "-0.13", "1350", "black_death"},
                {"London 1750", "51.51", "-0.13", "1750", "eighteenth_england"},
                {"London 1830", "51.51", "-0.13", "1830", "nineteenth_england"},
                {"Paris 1750", "48.86", "2.35", "1750", "eighteenth_france"},
                {"Rome 100", "41.90", "12.50", "100", "classical_rome"},
                {"Athens -400", "37.98", "23.73", "-400", "classical_greece"},
                {"Baghdad 900", "33.31", "44.36", "900", "medieval_islam"},
                {"Delhi 1850", "28.61", "77.21", "1850", "nineteenth_india"},
                {"Chang'an 750", "34.27", "108.90", "750", "east_asia_old"},
                {"Kyoto 2020", "35.01", "135.77", "2020", "modern_japan"},
                {"Cusco 1400", "-13.53", "-71.97", "1400", "late_medieval"},
                {"Cahokia 1100", "38.65", "-90.06", "1100", "medieval_world"},
        };
        for (String[] c : cases) {
            Mortality m = t.mortalityAt(Double.parseDouble(c[1]), Double.parseDouble(c[2]),
                    Integer.parseInt(c[3]));
            ok(m != null && c[4].equals(m.id()), c[0] + ": wanted " + c[4] + ", got "
                    + (m == null ? "nothing" : m.id()));
        }

        // the urban penalty: the same year, thirty miles apart, twelve years of life apart
        Mortality liverpool = t.mortalityAt(53.40d, -2.98d, 1840, true);
        Mortality lancashire = t.mortalityAt(53.75d, -2.70d, 1840, false);
        Mortality leeds = t.mortalityAt(53.80d, -1.55d, 1840, true);
        ok("industrial_city".equals(liverpool.id()), "Liverpool as a town: industrial_city, got "
                + liverpool.id());
        ok("nineteenth_england".equals(lancashire.id()), "Lancashire: nineteenth_england, got "
                + lancashire.id());
        ok("industrial_town".equals(leeds.id()), "Leeds as a town: industrial_town, got "
                + leeds.id());
        ok(liverpool.atBirth() < lancashire.atBirth() - 8.0d,
                "the town costs more than eight years: " + liverpool.atBirth() + " vs "
                        + lancashire.atBirth());
        System.out.printf(Locale.ROOT, "  1840: Liverpool %s %.0f, Leeds %s %.0f, Lancashire %s %.0f%n",
                liverpool.id(), liverpool.atBirth(), leeds.id(), leeds.atBirth(),
                lancashire.id(), lancashire.atBirth());

        // every place and every year gets an answer
        double[][] spots = {{17.39, 78.49}, {51.51, -0.13}, {41.90, 12.50}, {34.27, 108.90},
                {-13.53, -71.97}, {16.77, -3.01}, {-33.87, 151.21}, {38.65, -90.06}};
        int holes = 0;
        for (double[] s : spots) {
            for (int year = -10000; year <= 2026; year += 7) {
                if (t.mortalityAt(s[0], s[1], year) == null
                        || t.marriageAt(s[0], s[1], year) == null) {
                    holes++;
                }
            }
        }
        ok(holes == 0, "no holes in coverage, found " + holes);
        System.out.println();
    }

    // ------------------------------------------------------------------ the curve, cross-checked

    /** (regime, lat, lon, year, urban, e0, e15, dies@15, S(15), S(50), S(70), max). */
    private static void curve(LifeTable t) {
        System.out.println("the curve, cross-checked against the Python implementation:");
        System.out.printf(Locale.ROOT, "  %-20s %5s %5s %7s %7s %7s %7s %5s%n", "regime", "e0",
                "e15", "dies@15", "S(15)", "S(50)", "S(70)", "max");
        Object[][] rows = {
                {"classical_greece", 37.98d, 23.73d, -400, false, 26.5d, 36.0d, 51.0d, 0.454d,
                        0.233d, 0.084d, 85},
                {"classical_rome", 41.90d, 12.50d, 100, false, 27.5d, 36.4d, 51.4d, 0.514d,
                        0.293d, 0.091d, 93},
                {"medieval_europe", 51.51d, -0.13d, 1300, false, 31.5d, 29.2d, 44.2d, 0.669d,
                        0.242d, 0.067d, 90},
                {"black_death", 51.51d, -0.13d, 1350, false, 20.0d, 25.0d, 40.0d, 0.410d,
                        0.118d, 0.023d, 90},
                {"nineteenth_england", 51.75d, -1.25d, 1840, false, 40.0d, 41.6d, 56.6d, 0.683d,
                        0.444d, 0.222d, 90},
                {"nineteenth_india", 28.61d, 77.21d, 1850, false, 25.0d, 32.0d, 47.0d, 0.460d,
                        0.206d, 0.064d, 93},
                {"industrial_city", 53.40d, -2.98d, 1840, true, 30.0d, 32.0d, 47.0d, 0.578d,
                        0.265d, 0.073d, 90},
                {"industrial_town", 53.80d, -1.55d, 1840, true, 32.0d, 34.0d, 49.0d, 0.597d,
                        0.300d, 0.096d, 88},
                {"modern_2000", 17.39d, 78.49d, 2010, false, 70.0d, 60.0d, 75.0d, 0.926d,
                        0.808d, 0.674d, 89},
                {"modern_aids_africa", -24.65d, 25.91d, 2000, false, 45.0d, 45.0d, 60.0d, 0.717d,
                        0.518d, 0.270d, 87},
                {"modern_japan", 35.68d, 139.69d, 2020, false, 82.0d, 68.0d, 83.0d, 0.987d,
                        0.948d, 0.843d, 92},
        };
        for (Object[] r : rows) {
            String id = (String) r[0];
            Mortality m = t.mortalityAt((Double) r[1], (Double) r[2], (Integer) r[3],
                    (Boolean) r[4]);
            ok(m != null && id.equals(m.id()), "curve " + id + ": got "
                    + (m == null ? "nothing" : m.id()));
            if (m == null) {
                continue;
            }
            double e0 = t.expectancy(m, 0);
            double e15 = t.expectancy(m, 15);
            double s15 = t.survives(m, 15);
            double s50 = t.survives(m, 50);
            double s70 = t.survives(m, 70);
            int max = t.maxAge(m);
            near(id + " e0", e0, (Double) r[5]);
            near(id + " e15", e15, (Double) r[6]);
            near(id + " dies@15", 15 + e15, (Double) r[7]);
            near(id + " S(15)", s15, (Double) r[8]);
            near(id + " S(50)", s50, (Double) r[9]);
            near(id + " S(70)", s70, (Double) r[10]);
            ok(Math.abs(max - (Integer) r[11]) <= 2, id + " max age " + max + " vs " + r[11]);
            System.out.printf(Locale.ROOT, "  %-20s %5.1f %5.1f %7.1f %7.3f %7.3f %7.3f %5d%n",
                    id, e0, e15, 15 + e15, s15, s50, s70, max);
        }
        System.out.println();
    }

    // ------------------------------------------------------------------ what must always be true

    private static void invariants(LifeTable t) {
        System.out.println("invariants:");

        // The one that matters: a fifteen-year-old must expect to outlive a newborn's span, or
        // the mod has built a world with no grandparents in it — which is the error this whole
        // table exists to avoid.
        int bad = 0;
        for (int year : new int[]{-5000, -2000, -400, 1, 500, 900, 1348, 1500, 1700, 1800, 1850,
                1900, 1950, 2000, 2026}) {
            for (double[] s : new double[][]{{17.39, 78.49}, {51.51, -0.13}, {41.90, 12.50},
                    {34.27, 108.90}, {-13.53, -71.97}, {16.77, -3.01}}) {
                Mortality m = t.mortalityAt(s[0], s[1], year);
                if (m == null) {
                    continue;
                }
                for (int age : new int[]{1, 5, 15, 25, 45}) {
                    double now = age + t.expectancy(m, age);
                    double before = (age - 1) + t.expectancy(m, age - 1);
                    if (now < before - 0.5d) {
                        bad++;
                    }
                }
            }
        }
        ok(bad == 0, "surviving a year never lowers the age you expect to die at, " + bad
                + " exceptions");

        // nobody lives past 130, and everybody is born alive
        int absurd = 0;
        for (int year = -10000; year <= 2026; year += 37) {
            Mortality m = t.mortalityAt(17.39d, 78.49d, year);
            if (m == null) {
                continue;
            }
            if (t.maxAge(m) > 125 || t.survives(m, 0) != 1.0d) {
                absurd++;
            }
        }
        ok(absurd == 0, "no impossible ages, " + absurd + " exceptions");

        // The distinction the table exists for. A game that reads "life expectancy 31" and
        // thereupon kills everyone at thirty builds a village with no grandmothers in it. The
        // record says otherwise: a fifteen-year-old who has survived the dangerous years can
        // expect a dozen more years than the headline figure names.
        System.out.println("  what the headline figure hides:");
        int flat = 0;
        for (int year : new int[]{-2000, -400, 500, 1000, 1340, 1500, 1700, 1800, 1850, 1900}) {
            Mortality m = t.mortalityAt(51.51d, -0.13d, year);
            if (m == null) {
                continue;
            }
            double at15 = 15.0d + t.expectancy(m, 15);
            double gap = at15 - m.atBirth();
            if (m.atBirth() < 45.0d) {
                ok(gap > 5.0d, (year < 0 ? "BC " + -year : String.valueOf(year)) + ": a "
                        + "fifteen-year-old expects " + Math.round(gap) + " years more than the "
                        + "headline figure");
            }
            if (at15 <= m.atBirth()) {
                flat++;
            }
            System.out.printf(Locale.ROOT, "    %5d  e0 %4.1f, but a fifteen-year-old reaches "
                    + "%4.1f  (+%.1f)%n", year, m.atBirth(), at15, gap);
        }
        ok(flat == 0, "surviving childhood is always worth something, " + flat + " exceptions");

        // the curve runs down, never up: nobody is more likely to be alive at 70 than at 50
        int rising = 0;
        for (int year = -3000; year <= 2026; year += 11) {
            Mortality m = t.mortalityAt(51.51d, -0.13d, year);
            if (m == null) {
                continue;
            }
            for (int age = 1; age < t.maxAge(m); age++) {
                if (t.survives(m, age) > t.survives(m, age - 1) + 1.0e-9d) {
                    rising++;
                }
            }
        }
        ok(rising == 0, "survival never rises with age, " + rising + " exceptions");
        System.out.println();
    }

    // ------------------------------------------------------------------ drawing lives

    private static void sampling(LifeTable t) {
        System.out.println("a thousand lives:");
        int[][] spotsYears = {{1850, 1800}, {1300, 1300}, {-400, -400}, {1700, 1700}, {2010, 2010}};
        double[][] spots = {{51.51, -0.13}, {51.51, -0.13}, {37.98, 23.73}, {17.39, 78.49},
                {17.39, 78.49}};
        for (int i = 0; i < spotsYears.length; i++) {
            int year = spotsYears[i][0];
            double lat = spots[i][0];
            double lon = spots[i][1];
            Mortality m = t.mortalityAt(lat, lon, year);
            List<Integer> ages = new ArrayList<>();
            for (long s = 0; s < 4000; s++) {
                ages.add(t.deathAge(m, s));
            }
            double mean = ages.stream().mapToInt(Integer::intValue).average().orElse(0.0d);
            long past60 = ages.stream().filter(a -> a >= 60).count();
            long past15 = ages.stream().filter(a -> a >= 15).count();
            // A death age is a whole number of years, and the discrete mean of an integer draw
            // sits half a year above the continuous e0 (E[K] = sum over k of S(k) = e0 + 0.5).
            // Four thousand lives carry a standard error of about half a year on top of that.
            near(year + " mean lifespan", mean, m.atBirth() + 0.5d, 1.5d);

            // the whole point: a world where nobody reaches sixty is a world with no grandmothers
            // in it, and the sources say otherwise
            if (m.atBirth() >= 28.0d) {
                ok(past60 * 100.0d / ages.size() > 10.0d,
                        year + ": more than a tenth live to sixty (" + past60 + " of "
                                + ages.size() + ")");
            }
            ok(past15 * 100.0d / ages.size() > 20.0d,
                    year + ": more than a fifth reach fifteen (" + past15 + ")");
            System.out.printf(Locale.ROOT,
                    "  %5d  %-20s mean %.1f (e0 %.1f), %2d%% reach 60, %2d%% reach 15%n",
                    year, m.id(), mean, m.atBirth(), Math.round(past60 * 100.0d / ages.size()),
                    Math.round(past15 * 100.0d / ages.size()));
        }

        // the same salt gives the same person, or a remembered villager comes back someone else
        Life a = t.life(12345L, 1800, 51.51d, -0.13d, false);
        Life b = t.life(12345L, 1800, 51.51d, -0.13d, false);
        ok(a.equals(b), "the same salt gives the same person");
        Life c = t.life(12346L, 1800, 51.51d, -0.13d, false);
        ok(!a.equals(c) || a.deathYear() == c.deathYear(), "a different salt may differ");

        System.out.println();
        System.out.println("six lives:");
        long[] salts = {1L, 7L, 31L, 512L, 90210L, 7777777L};
        for (long s : salts) {
            Life life = t.life(s, 1348, 17.39d, 78.49d, false);
            System.out.printf(Locale.ROOT, "  %-58s %s%n", life.describe(),
                    life.mortality().name());
        }
        for (long s : salts) {
            Life life = t.life(s, 1800, 51.51d, -0.13d, true);
            System.out.printf(Locale.ROOT, "  %-58s %s%n", life.describe(),
                    life.mortality().name());
        }
        System.out.println();
    }

    // ------------------------------------------------------------------ marriage

    private static void marriage(LifeTable t) {
        System.out.println("marriage and children:");
        Object[][] cases = {
                {"London 1700", 51.51d, -0.13d, 1700},
                {"Paris 1700", 48.86d, 2.35d, 1700},
                {"Chang'an 1800", 34.27d, 108.90d, 1800},
                {"Delhi 1850", 28.61d, 77.21d, 1850},
                {"Cusco 1500", -13.53d, -71.97d, 1500},
                {"Hyderabad 1948", 17.39d, 78.49d, 1948},
                {"Hyderabad 2020", 17.39d, 78.49d, 2020},
        };
        for (Object[] c : cases) {
            Marriage g = t.marriageAt((Double) c[1], (Double) c[2], (Integer) c[3]);
            ok(g != null, c[0] + ": a marriage row");
            if (g == null) {
                continue;
            }
            // Hajnal: west of the line women marry in the middle twenties, east of it in the teens
            if ("hajnal_west".equals(g.id()) || "hajnal_england_1650".equals(g.id())) {
                ok(g.wife() >= 23.0d, c[0] + ": western women marry late (" + g.wife() + ")");
                ok(g.celibate() >= 8, c[0] + ": and a tenth or more never marry ("
                        + g.celibate() + "%)");
            }
            if ("qing_china".equals(g.id())) {
                ok(g.husband() <= 23.0d, c[0] + ": Chinese men marry young (" + g.husband() + ")");
                ok(g.celibate() >= 15, c[0] + ": and many never marry at all (" + g.celibate()
                        + "%)");
            }
            double mean = 0.0d;
            int never = 0;
            for (long s = 0; s < 3000; s++) {
                int age = t.marriageAge(g, false, s);
                if (age < 0) {
                    never++;
                } else {
                    mean += age;
                }
            }
            mean /= Math.max(1, 3000 - never);
            // the floor at fourteen biases the mean upward on the rows whose mean sits near it,
            // so this is a tolerance and not an equality
            near(c[0] + " sampled marriage age", mean, g.wife(), 0.5d);
            ok(Math.abs(never * 100.0d / 3000 - g.celibate()) < 4.0d,
                    c[0] + ": celibacy " + Math.round(never * 100.0d / 3000) + "% vs "
                            + g.celibate() + "%");
            System.out.printf(Locale.ROOT, "  %-16s %-22s wives %.1f, husbands %.1f, %2d%% never,"
                    + " %.1f children%n", c[0], g.id(), g.wife(), g.husband(), g.celibate(),
                    g.births());
        }
        System.out.println();
    }

    // ------------------------------------------------------------------ words

    private static void words(LifeTable t) {
        System.out.println("how it reads:");
        Object[][] cases = {{"Athens", 37.98d, 23.73d, -400}, {"Rome", 41.90d, 12.50d, 100},
                {"London", 51.51d, -0.13d, 1350}, {"London", 51.51d, -0.13d, 1830},
                {"Delhi", 28.61d, 77.21d, 1850}, {"Hyderabad", 17.39d, 78.49d, 1948},
                {"Hyderabad", 17.39d, 78.49d, 2020}, {"Cahokia", 38.65d, -90.06d, 1100}};
        for (Object[] c : cases) {
            System.out.printf(Locale.ROOT, "  %-10s %5d  %s%n", c[0], (Integer) c[3],
                    t.mortalityLine((Double) c[1], (Double) c[2], (Integer) c[3]));
            System.out.printf(Locale.ROOT, "  %-10s %5s  %s%n", "", "",
                    t.marriageLine((Double) c[1], (Double) c[2], (Integer) c[3]));
            String clerk = t.says("scribe", (Double) c[1], (Double) c[2], (Integer) c[3]);
            String farmer = t.says("farmer", (Double) c[1], (Double) c[2], (Integer) c[3]);
            ok(!clerk.isEmpty() && !farmer.isEmpty(), c[0] + ": something is said");
            ok(clerk.startsWith("It is reckoned"), "a clerk says: " + clerk);
            ok(farmer.startsWith("Folk here say"), "a farmer says: " + farmer);
        }
        System.out.println();
    }

    // ------------------------------------------------------------------ the check itself

    private static void ok(boolean cond, String what) {
        checks++;
        if (!cond) {
            failed++;
            System.out.println("  FAIL: " + what);
        }
    }

    private static void near(String what, double got, double want) {
        near(what, got, want, 0.06d);
    }

    private static void near(String what, double got, double want, double tolerance) {
        checks++;
        if (Math.abs(got - want) > tolerance) {
            failed++;
            System.out.printf(Locale.ROOT, "  FAIL: %s: %.3f vs %.3f%n", what, got, want);
        }
    }
}
