package com.eternalengine.calprobe;

import com.eternalengine.knowledge.Calendars;
import com.eternalengine.knowledge.Calendars.Chinese;
import com.eternalengine.knowledge.Calendars.Date;
import com.eternalengine.knowledge.Calendars.Region;
import com.eternalengine.knowledge.Calendars.Regnal;
import com.eternalengine.knowledge.Calendars.System;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Step 37 (A2): run the calendar register against the mod's own data and a set of known dates.
 *
 * <p>The Chinese dates are the ones most worth proving, so eighteen known Chinese New Year dates
 * from 1966 to 2026 are checked here, including 21 January 1966 (the earliest the new year can
 * fall) and 20 February 1985 (a year with a leap month). Every check here can fail.
 */
public final class CalendarsRun {

    private static int passed;
    private static final List<String> failures = new ArrayList<>();

    static long ed(int y, int m, int d) {
        return LocalDate.of(y, m, d).toEpochDay();
    }

    static void ok(boolean b, String what) {
        if (b) {
            passed++;
        } else {
            failures.add(what);
        }
    }

    static void eq(Object want, Object got, String what) {
        boolean b = want == null ? got == null : want.equals(got);
        if (b) {
            passed++;
        } else {
            failures.add(what + ": wanted " + want + ", got " + got);
        }
    }

    public static void main(String[] args) {
        Calendars c = Calendars.get();
        java.lang.System.out.println("source: " + c.source());
        java.lang.System.out.println("regions: " + c.regionCount());
        java.lang.System.out.println();

        // ------------------------------------------------------------- the pack itself
        ok(c.regionCount() >= 30, "the pack should carry its region table, got " + c.regionCount());
        int unsourced = 0;
        for (Region r : c.regions()) {
            if (r.source() == null || r.source().isEmpty()) {
                unsourced++;
            }
        }
        eq(0, unsourced, "regions with no source article");

        // ------------------------------------------------------------- Chinese: 18 known new years
        int[][] known = {
                {1966, 1, 21}, {1970, 2, 6}, {1975, 2, 11}, {1980, 2, 16},
                {1983, 2, 13}, {1984, 2, 2}, {1985, 2, 20}, {1996, 2, 19},
                {2000, 2, 5}, {2008, 2, 7}, {2019, 2, 5}, {2020, 1, 25},
                {2021, 2, 12}, {2022, 2, 1}, {2023, 1, 22}, {2024, 2, 10},
                {2025, 1, 29}, {2026, 2, 17},
        };
        for (int[] k : known) {
            long want = ed(k[0], k[1], k[2]);
            long got = Calendars.chineseNewYearOnOrBefore(want + 40);
            eq(LocalDate.ofEpochDay(want), LocalDate.ofEpochDay(got), "Chinese new year " + k[0]);
        }

        // a Chinese date has to be a real month and a real day
        for (long probe : new long[] {ed(2026, 2, 17), ed(2026, 10, 16), ed(1948, 9, 14),
                ed(1900, 6, 15), ed(1700, 1, 1), ed(1000, 3, 3), ed(622, 7, 19), ed(-500, 5, 5)}) {
            Chinese ci = Calendars.chineseInfo(probe);
            boolean good = ci.month() >= 1 && ci.month() <= 12 && ci.day() >= 1 && ci.day() <= 30
                    && ci.ganzhi() != null && !ci.ganzhi().isEmpty()
                    && ci.newYear() <= probe && probe - ci.newYear() < 400;
            ok(good, "Chinese date at day " + probe + " came out as " + ci);
        }
        Date ch = Calendars.chinese(ed(2026, 10, 16));
        eq(false, ch.approximate(), "the Chinese date is computed, so it is not approximate");
        eq("Bingwu", ch.yearText(), "the year name of 2026");
        java.lang.System.out.println("today in Chinese:  " + ch.text());

        // ------------------------------------------------------------- Hijri
        eq("1 Ramadan 1445 AH", Calendars.hijri(ed(2024, 3, 11)).text(), "Hijri 2024-03-11");
        eq("1 Muharram 1445 AH", Calendars.hijri(ed(2023, 7, 19)).text(), "Hijri 2023-07-19");
        eq("10 Dhu al-Qadah 1367 AH", Calendars.hijri(ed(1948, 9, 14)).text(), "Hijri 1948-09-14");
        eq("1 Muharram 1 AH", Calendars.hijri(ed(622, 7, 19)).text(), "Hijri epoch");

        // ------------------------------------------------------------- Julian
        // 1700 was a leap year in the Julian calendar and not in the Gregorian, so the gap
        // between the two opened from ten days to eleven that March
        eq("29 February 1700", Calendars.julian(ed(1700, 3, 11)).text(), "Julian 1700-03-11");
        eq("12 March 1700", Calendars.julian(ed(1700, 3, 23)).text(), "Julian 1700-03-23");
        eq("5 October 1582", Calendars.julian(ed(1582, 10, 15)).text(), "Julian 1582-10-15");

        // ------------------------------------------------------------- Saka, Vikram, Fasli
        eq("1 Chaitra 1946 Saka", Calendars.saka(ed(2024, 3, 21)).text(), "Saka 2024-03-21");
        eq(1870, Calendars.saka(ed(1948, 9, 14)).year(), "Saka year of 1948-09-14");
        eq(2005, Calendars.vikram(ed(1948, 9, 14)).year(), "Vikram year of 1948-09-14");
        eq(1358, Calendars.fasli(ed(1948, 9, 14)).year(), "Fasli year of 1948-09-14");
        eq(1357, Calendars.fasli(ed(1948, 3, 1)).year(), "Fasli year of 1948-03-01 (before July)");
        ok(Calendars.vikram(ed(1948, 9, 14)).approximate(), "the Vikram month is approximate");
        ok(!Calendars.saka(ed(1948, 9, 14)).approximate(), "the Saka date is exact");

        // ------------------------------------------------------------- exactness is declared
        for (System s : new System[] {System.GREGORIAN, System.JULIAN, System.HIJRI,
                System.SAKA, System.CHINESE}) {
            ok(s.exact(), s.label() + " should be exact");
        }
        for (System s : new System[] {System.VIKRAM, System.FASLI, System.REGNAL}) {
            ok(!s.exact(), s.label() + " should be flagged approximate");
        }

        // ------------------------------------------------------------- which calendar, where
        List<System> hyderabad = c.usedAt(17.39d, 78.49d, 1948);
        eq(System.FASLI, hyderabad.get(0), "Hyderabad 1948 writes Fasli first");
        ok(hyderabad.contains(System.HIJRI), "Hyderabad 1948 also keeps the Hijri year");
        ok(hyderabad.contains(System.SAKA), "Hyderabad 1948 also keeps the Saka year");

        eq(System.JULIAN, c.primaryAt(51.5d, -0.1d, 1700), "London 1700 is Julian");
        eq(System.GREGORIAN, c.primaryAt(51.5d, -0.1d, 1800), "London 1800 is Gregorian");
        eq(System.JULIAN, c.primaryAt(55.75d, 37.6d, 1900), "Moscow 1900 is Julian");
        eq(System.GREGORIAN, c.primaryAt(55.75d, 37.6d, 1930), "Moscow 1930 is Gregorian");
        eq(System.HIJRI, c.primaryAt(30.0d, 31.2d, 1300), "Cairo 1300 is Hijri");
        eq(System.CHINESE, c.primaryAt(39.9d, 116.4d, 1700), "Beijing 1700 is Chinese");
        eq(System.GREGORIAN, c.primaryAt(39.9d, 116.4d, 1950), "Beijing 1950 is Gregorian");
        eq(System.VIKRAM, c.primaryAt(28.6d, 77.2d, 1700), "Delhi 1700 is Vikram");
        eq(System.HIJRI, c.primaryAt(16.8d, -3.0d, 1500), "Timbuktu 1500 is Hijri");
        eq(System.SAKA, c.primaryAt(17.39d, 78.49d, 100),
                "Hyderabad in AD 100 is dated by the Saka era, not by a Christian year");

        // a place the pack knows nothing about still gets an answer, and it is the mod's own date
        ok(!c.usedAt(-20.0d, -140.0d, 1500).isEmpty(), "an empty ocean still gets a date");

        // ------------------------------------------------------------- the dateline
        String line = c.dateline(17.39d, 78.49d, ed(1948, 9, 14));
        ok(line.contains("Fasli 1358"), "the Hyderabad dateline is Fasli 1358, got: " + line);
        java.lang.System.out.println("Hyderabad, 14 September 1948:");
        for (Date d : c.at(17.39d, 78.49d, ed(1948, 9, 14))) {
            java.lang.System.out.println("    " + d.system().label() + ": " + d.text()
                    + (d.approximate() ? "   (approximate)" : ""));
        }
        java.lang.System.out.println("    dateline: " + line);
        java.lang.System.out.println();

        // ------------------------------------------------------------- regnal years
        Optional<Regnal> r = Calendars.regnal(17.39d, 78.49d, 1948);
        ok(r.isPresent(), "Hyderabad 1948 has a ruler on record");
        r.ifPresent(reg -> {
            ok(reg.year() >= 1, "a year of a rule is at least 1, got " + reg.year());
            ok(!reg.text().isEmpty(), "the regnal text is not empty");
            java.lang.System.out.println("Hyderabad 1948: " + reg.text());
        });
        eq(false, Calendars.regnal(0.0d, -140.0d, 1900).isPresent(),
                "the middle of the Pacific has no ruler, and empty is not permission");

        // ------------------------------------------------------------- the words
        eq("first", Calendars.ordinal(1), "ordinal 1");
        eq("twelfth", Calendars.ordinal(12), "ordinal 12");
        eq("twenty-first", Calendars.ordinal(21), "ordinal 21");
        eq("fortieth", Calendars.ordinal(40), "ordinal 40");
        eq("ninety-ninth", Calendars.ordinal(99), "ordinal 99");
        eq("128th", Calendars.ordinal(128), "ordinal 128");

        // ------------------------------------------------------------- a spread of places
        java.lang.System.out.println("what a few places would have written:");
        double[][] spots = {{17.39d, 78.49d}, {51.5d, -0.1d}, {55.75d, 37.6d}, {30.0d, 31.2d},
                {28.6d, 77.2d}, {39.9d, 116.4d}, {35.0d, 135.8d}, {41.9d, 12.5d},
                {-13.5d, -72.0d}, {6.3d, 5.6d}};
        String[] names = {"Hyderabad", "London", "Moscow", "Cairo", "Delhi", "Beijing", "Kyoto",
                "Rome", "Cusco", "Benin"};
        for (int year : new int[] {1000, 1500, 1700, 1900, 1948}) {
            java.lang.System.out.println("  in " + year + ":");
            for (int i = 0; i < spots.length; i++) {
                long day = LocalDate.of(year, 6, 15).toEpochDay();
                List<Date> dates = c.at(spots[i][0], spots[i][1], day);
                StringBuilder sb = new StringBuilder();
                for (Date d : dates) {
                    if (sb.length() > 0) {
                        sb.append(" / ");
                    }
                    sb.append(d.text());
                }
                java.lang.System.out.println("    " + names[i] + ": " + sb);
                for (String note : c.notesAt(spots[i][0], spots[i][1], year)) {
                    java.lang.System.out.println("        ! " + note);
                }
            }
        }

        java.lang.System.out.println();
        java.lang.System.out.println(passed + " checks passed, " + failures.size() + " failed");
        for (String f : failures) {
            java.lang.System.out.println("  FAIL: " + f);
        }
        if (!failures.isEmpty()) {
            java.lang.System.exit(1);
        }
    }
}
