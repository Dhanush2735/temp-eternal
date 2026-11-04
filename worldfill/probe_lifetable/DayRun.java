package com.eternalengine.lifeprobe;

import com.eternalengine.people.DayRound;
import com.eternalengine.people.DayRound.Day;
import com.eternalengine.people.DayRound.Prayers;
import com.eternalengine.people.DayRound.Season;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Checks the day-round register with no Minecraft and no Gradle: twenty rounds, every place and
 * year covered, the twenty-one written cases, the four market cycles that are not seven days
 * long, and the arithmetic of market day and rest day over a stretch of counted days.
 */
public final class DayRun {

    private static int checks;
    private static final List<String> failures = new ArrayList<>();

    private static void ok(boolean pass, String what) {
        checks++;
        if (!pass) {
            failures.add(what);
            System.out.println("FAIL  " + what);
        }
    }

    private static void eq(String what, int got, int want) {
        checks++;
        if (got != want) {
            failures.add(what + ": got " + got + ", want " + want);
            System.out.println("FAIL  " + what + ": got " + got + ", want " + want);
        }
    }

    private static final int[] YEARS = {-10000, -5000, -3000, -2000, -1000, -500, -250, -1, 1, 100,
            250, 500, 750, 1000, 1250, 1348, 1450, 1500, 1600, 1688, 1700, 1750, 1800, 1841, 1900,
            1925, 1950, 1975, 1980, 2000, 2020, 2026};

    // name, lat, lon, year, urban, expected round, expected season ("" for the latitude's own)
    private static final Object[][] CASES = {
            {"Rome 100", 41.90, 12.50, 100, false, "roman_italy", ""},
            {"Athens -400", 37.98, 23.73, -400, false, "classical_world", ""},
            {"London 1300", 51.51, -0.13, 1300, false, "medieval_world", ""},
            {"London 1500", 51.51, -0.13, 1500, false, "late_medieval", ""},
            {"London 1700", 51.51, -0.13, 1700, false, "early_modern_england", ""},
            {"Bavaria 1700", 48.14, 11.58, 1700, false, "early_modern_europe", ""},
            {"London 1850, a town", 51.51, -0.13, 1850, true, "industrial_town", ""},
            {"London 1900", 51.51, -0.13, 1900, false, "world_1900", ""},
            {"London 2020", 51.51, -0.13, 2020, false, "modern_world", ""},
            {"Cairo 1000", 30.04, 31.24, 1000, false, "islamic_world", "egypt_three_seasons"},
            {"Cairo 2020", 30.04, 31.24, 2020, false, "modern_mena", ""},
            {"Jakarta 1700", -6.21, 106.85, 1700, false, "java_pasaran", ""},
            {"Bali 1700", -8.50, 115.20, 1700, false, "bali_triwara", ""},
            {"Tenochtitlan 1500", 19.43, -99.13, 1500, false, "mesoamerica_tianguis", ""},
            {"Delhi 1700", 28.61, 77.21, 1700, false, "early_modern_world", "india_six_seasons"},
            {"Beijing 1700", 39.90, 116.41, 1700, false, "early_modern_world", "china_terms"},
            {"Jerusalem 2020", 31.78, 35.22, 2020, false, "modern_israel", ""},
            {"Amazonia -9000", -3.10, -60.02, -9000, false, "foraging_band", ""},
            {"Amazonia -5000", -3.10, -60.02, -5000, false, "early_farming", ""},
            {"Amazonia -1500", -3.10, -60.02, -1500, false, "bronze_world", ""},
            {"Yakutsk 2020", 62.03, 129.73, 2020, false, "modern_world", ""},
    };

    // the cycles that are not seven days long, and the places that made them
    private static final Object[][] MARKETS = {
            {"roman_italy", 41.90, 12.50, 100, 56, 8},       // 56 days, every eighth
            {"java_pasaran", -6.21, 106.85, 1700, 35, 5},    // 35 days, every fifth
            {"bali_triwara", -8.50, 115.20, 1700, 210, 3},   // 210 days, every third
            {"mesoamerica_tianguis", 19.43, -99.13, 1500, 35, 7},
    };

    static int run() {
        DayRound t = DayRound.get();
        System.out.println();
        System.out.println("=== the day round: " + t.count() + " rounds, " + t.seasonCount()
                + " season rows, " + t.faithCount() + " faiths ===");
        eq("rounds", t.count(), 20);
        eq("season rows", t.seasonCount(), 3);
        eq("faiths", t.faithCount(), 7);

        // -------------------------------------------------- every place, every year
        int holes = 0;
        for (String[] s : HomeRun.SPOTS) {
            for (int y : YEARS) {
                if (t.at(Double.parseDouble(s[1]), Double.parseDouble(s[2]), y) == null) {
                    holes++;
                    System.out.println("FAIL  no day round for " + s[0] + " in " + y);
                }
            }
        }
        ok(holes == 0, holes + " place-year combinations with no day");

        // -------------------------------------------------- the written cases
        for (Object[] c : CASES) {
            Day d = t.at((Double) c[1], (Double) c[2], (Integer) c[3], (Boolean) c[4]);
            ok(d != null && d.id().equals(c[5]),
                    (String) c[0] + ": wanted " + c[5] + ", got " + (d == null ? "none" : d.id()));
            Season sn = t.seasons((Double) c[1], (Double) c[2], (Integer) c[3]);
            String want = (String) c[6];
            boolean seasonOk = want.isEmpty() ? (sn.id().equals("tropical")
                    || sn.id().equals("temperate")) : sn.id().equals(want);
            ok(seasonOk, (String) c[0] + ": wanted season " + (want.isEmpty() ? "from latitude"
                    : want) + ", got " + sn.id());
        }

        // -------------------------------------------------- the market cycle, counted
        System.out.println();
        System.out.println("--- the market cycle, counted over a stretch of days ---");
        for (Object[] c : MARKETS) {
            Day d = t.at((Double) c[1], (Double) c[2], (Integer) c[3], false);
            ok(d != null && d.id().equals(c[0]), "cannot reach " + c[0]);
            if (d == null) {
                continue;
            }
            int span = (Integer) c[4];
            int hits = 0;
            for (long day = 1; day <= span; day++) {
                if (t.isMarketDay((Double) c[1], (Double) c[2], (Integer) c[3], day)) {
                    hits++;
                }
            }
            int want = span / (Integer) c[5];
            eq(c[0] + " market days in " + span, hits, want);
            System.out.printf("  %-22s every %-2d days -> %3d market days in %3d  (the %s)%n",
                    d.id(), d.market(), hits, span, d.marketName());
        }

        // -------------------------------------------------- the day of rest
        System.out.println();
        System.out.println("--- the day on which nobody works ---");
        eq("London 1300 rest day", t.at(51.51, -0.13, 1300).rest(), 0);
        eq("Cairo 1000 rest day", t.at(30.04, 31.24, 1000).rest(), 5);
        eq("Jerusalem 2020 rest day", t.at(31.78, 35.22, 2020).rest(), 6);
        eq("Amazonia -9000 rest day", t.at(-3.10, -60.02, -9000).rest(), -1);
        ok(t.isRestDay(51.51, -0.13, 1300, 0), "Sunday should be the rest day in London 1300");
        ok(!t.isRestDay(51.51, -0.13, 1300, 1), "Monday should not be, in London 1300");
        ok(t.isRestDay(30.04, 31.24, 1000, 5), "Friday should be the rest day in Cairo 1000");
        int restDays = 0;
        for (int wd = 0; wd < 7; wd++) {
            if (t.isRestDay(-3.10, -60.02, -9000, wd)) {
                restDays++;
            }
        }
        eq("a band has no day of rest at all", restDays, 0);
        int without = 0;
        for (Day d : allRounds(t)) {
            if (!d.hasRestDay()) {
                without++;
            }
        }
        System.out.println("  " + without + " of the " + t.count()
                + " rounds have no day of the week on which nobody works");
        ok(without >= 8, "most of history should have no weekly day of rest, only " + without);

        // -------------------------------------------------- the hours
        System.out.println();
        System.out.println("--- how long the day is ---");
        Day factory = t.at(51.51, -0.13, 1850, true);
        for (Day d : allRounds(t)) {
            ok(d.hours() <= factory.hours(),
                    d.id() + ": " + d.hours() + "h, longer than the factory's " + factory.hours());
        }
        Day modern = t.at(51.51, -0.13, 2020);
        Day turn = t.at(51.51, -0.13, 1900);
        ok(modern.hours() < turn.hours() && turn.hours() < factory.hours(),
                "the clock rows should shorten: factory " + factory.hours() + ", 1900 "
                        + turn.hours() + ", now " + modern.hours());
        Day band = t.at(-3.10, -60.02, -9000);
        System.out.println("  factory " + factory.hours() + "h   1900 " + turn.hours()
                + "h   now " + modern.hours() + "h   and a band of foragers, " + band.hours() + "h");
        ok(band.hours() < modern.hours(),
                "a forager's day is shorter than a modern one — this is the finding, not a bug");

        // -------------------------------------------------- the seasons
        System.out.println();
        System.out.println("--- how the year is cut ---");
        String[][] seasons = {{"Cairo", "30.04", "31.24", "1000"},
                {"Cairo", "30.04", "31.24", "2020"}, {"Delhi", "28.61", "77.21", "1700"},
                {"Beijing", "39.90", "116.41", "1700"}, {"Lagos", "6.52", "3.38", "2020"},
                {"London", "51.51", "-0.13", "2020"}, {"Sydney", "-33.87", "151.21", "2020"}};
        for (String[] s : seasons) {
            Season sn = t.seasons(Double.parseDouble(s[1]), Double.parseDouble(s[2]),
                    Integer.parseInt(s[3]));
            System.out.println("  " + s[0] + " " + s[3] + ": " + sn.count() + " — "
                    + String.join(", ", sn.names()));
        }
        eq("Cairo 1000 seasons", t.seasons(30.04, 31.24, 1000).count(), 3);
        eq("Cairo 2020 seasons", t.seasons(30.04, 31.24, 2020).count(), 4);
        eq("Delhi 1700 seasons", t.seasons(28.61, 77.21, 1700).count(), 6);
        eq("Lagos 2020 seasons", t.seasons(6.52, 3.38, 2020).count(), 2);
        ok(t.seasons(30.04, 31.24, 2020).names().get(0).equals("spring"),
                "Cairo has four seasons now, because the Nile stopped flooding in 1902");

        // -------------------------------------------------- the set hours of a faith
        System.out.println();
        System.out.println("--- how many times a day one stops ---");
        String[][] faiths = {{"islam", "5"}, {"christianity", "8"}, {"judaism", "3"},
                {"hinduism", "3"}, {"sikhism", "3"}, {"buddhism", "2"}, {"none", "0"},
                {"something else", "0"}};
        for (String[] f : faiths) {
            Prayers p = t.prayers(f[0]);
            eq(f[0] + " prayer times", p.count(), Integer.parseInt(f[1]));
            System.out.println("  " + f[0] + ": " + p.count() + (p.count() == 0 ? ""
                    : " — " + String.join(", ", p.names())));
        }
        ok(t.prayers("ISLAM").count() == 5, "faith lookup should not care about case");
        // the number a lay person keeps is not always the number the faith sets out
        eq("Christianity sets out eight hours", t.prayers("christianity").count(), 8);
        eq("but a parish keeps two", t.prayers("christianity").keptToday(), 2);
        eq("Islam is five and kept five", t.prayers("islam").keptToday(), 5);
        for (String[] f : faiths) {
            Prayers pr = t.prayers(f[0]);
            ok(pr.keptToday() <= pr.count(),
                    f[0] + ": keeps " + pr.keptToday() + " of " + pr.count() + " set hours");
        }

        // -------------------------------------------------- what the game says
        System.out.println();
        System.out.println("--- what the game says ---");
        Object[][] words = {{"London 1300", 51.51, -0.13, 1300, false, "christianity"},
                {"London 1700", 51.51, -0.13, 1700, false, "christianity"},
                {"London 1850, a town", 51.51, -0.13, 1850, true, "christianity"},
                {"Cairo 1000", 30.04, 31.24, 1000, false, "islam"},
                {"Jakarta 1700", -6.21, 106.85, 1700, false, "islam"},
                {"Amazonia -9000", -3.10, -60.02, -9000, false, "none"}};
        for (Object[] w : words) {
            System.out.println("  " + w[0] + ": " + t.line((Double) w[1], (Double) w[2],
                    (Integer) w[3], (Boolean) w[4], (String) w[5]));
        }

        System.out.println();
        System.out.println(failures.isEmpty() ? "ALL " + checks + " CHECKS PASSED"
                : failures.size() + " of " + checks + " CHECKS FAILED");
        for (String f : failures) {
            System.out.println("  - " + f);
        }
        return failures.isEmpty() ? 0 : 1;
    }

    private static List<Day> allRounds(DayRound t) {
        List<Day> out = new ArrayList<>();
        for (String[] s : HomeRun.SPOTS) {
            for (int y : YEARS) {
                Day d = t.at(Double.parseDouble(s[1]), Double.parseDouble(s[2]), y);
                if (d != null && !contains(out, d)) {
                    out.add(d);
                }
            }
        }
        return out;
    }

    private static boolean contains(List<Day> list, Day d) {
        for (Day x : list) {
            if (x.id().equals(d.id())) {
                return true;
            }
        }
        return false;
    }

    public static void main(String[] args) {
        System.exit(run());
    }
}
