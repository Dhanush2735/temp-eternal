#!/usr/bin/env python3
"""Lift the two step-37 methods out of NewsService.java, which needs Minecraft to compile, into
a runner that does not. The mod's date key is YYYYMMDD (KnowledgeDate), so the runner carries a
three-line stand-in for it.

Writes: <work>/src/com/eternalengine/calprobe/NewsRun.java
"""
import sys

SRC = "/home/user/eternal/src/main/java/com/eternalengine/news/NewsService.java"

HEAD = '''package com.eternalengine.calprobe;

import com.eternalengine.civilization.Rumour;
import com.eternalengine.civilization.SettlementRank;
import com.eternalengine.knowledge.Calendars;
import com.eternalengine.news.NewsChannels;
import com.eternalengine.news.NewsChannels.Channel;
import com.eternalengine.news.NewsEras;
import com.eternalengine.news.NewsTravel;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Step 37 (C23 news by era, D8 rumours, and the A2 masthead): the two methods NewsService grew
 * this step, lifted out of it so they can be run without Minecraft, plus checks on the channels
 * and on what a rumour loses on the road. Every check here can fail.
 */
public final class NewsRun {

    private static int passed;
    private static final List<String> failures = new ArrayList<>();

    static void ok(boolean b, String what) {
        if (b) {
            passed++;
        } else {
            failures.add(what);
        }
    }

    static void eq(Object want, Object got, String what) {
        if (want == null ? got == null : want.equals(got)) {
            passed++;
        } else {
            failures.add(what + ": wanted " + want + ", got " + got);
        }
    }

    /** The mod's date key is YYYYMMDD (KnowledgeDate); this is the same three lines. */
    static final class KD {
        static int year(int key) { return Math.floorDiv(key, 10000); }
        static int month(int key) { return Math.floorMod(key, 10000) / 100; }
        static int day(int key) { return Math.floorMod(key, 100); }
    }

'''

TAIL_START = '''
    // ============================================================== the checks

    private static final double HYD_LA = 17.39d, HYD_LO = 78.49d;
    private static final double LONDON_LA = 51.5d, LONDON_LO = -0.13d;
    private static final double ROME_LA = 41.9d, ROME_LO = 12.5d;
    private static final double MOSCOW_LA = 55.75d, MOSCOW_LO = 37.6d;
    private static final double VENICE_LA = 45.44d, VENICE_LO = 12.33d;

    public static void main(String[] args) {
        // ------------------------------------------------------- the masthead, in the local calendar
        String hyderabad = dateLine(HYD_LA, HYD_LO, 19480914);
        ok(hyderabad.contains("Fasli 1358"),
                "the Hyderabad masthead is dated in Fasli: " + hyderabad);
        ok(!hyderabad.contains("TUESDAY"),
                "a Fasli date carries no Christian weekday: " + hyderabad);

        String london = dateLine(LONDON_LA, LONDON_LO, 19480914);
        ok(london.startsWith("TUESDAY"), "London 14 September 1948 was a Tuesday: " + london);
        ok(london.contains("14 September 1948"), "and Gregorian: " + london);

        String moscow = dateLine(MOSCOW_LA, MOSCOW_LO, 17000615);
        ok(moscow.contains("4 June 1700"),
                "Moscow 1700 is eleven days behind (the gap widened in March 1700): " + moscow);
        ok(dateLine(MOSCOW_LA, MOSCOW_LO, 17000311).contains("29 February 1700"),
                "and 11 March 1700 in Moscow is 29 February, a day London did not have: "
                        + dateLine(MOSCOW_LA, MOSCOW_LO, 17000311));
        String rome = dateLine(ROME_LA, ROME_LO, 17000615);
        ok(rome.contains("15 June 1700"), "and Rome is not: " + rome);

        ok(dateLine(HYD_LA, HYD_LO, 19480914).contains("Hyderabad State")
                        || dateLine(HYD_LA, HYD_LO, 17000615).contains("Fasli"),
                "the register has a ruler or a Fasli year for Hyderabad");

        java.lang.System.out.println("mastheads:");
        String[] towns = {"Hyderabad", "London", "Moscow", "Rome", "Beijing", "Cairo", "Delhi",
                "Kyoto", "Cusco"};
        double[][] at = {{HYD_LA, HYD_LO}, {LONDON_LA, LONDON_LO}, {MOSCOW_LA, MOSCOW_LO},
                {ROME_LA, ROME_LO}, {39.9d, 116.4d}, {30.0d, 31.2d}, {28.61d, 77.21d},
                {35.0d, 135.8d}, {-13.5d, -72.0d}};
        for (int year : new int[] {100, 1500, 1700, 1900, 1948}) {
            StringBuilder row = new StringBuilder("  " + year + "  ");
            for (int i = 0; i < towns.length; i++) {
                row.append(towns[i]).append(": ").append(dateLine(at[i][0], at[i][1],
                        year * 10000 + 615)).append("   ");
            }
            java.lang.System.out.println(row);
        }

        // ------------------------------------------------------- C23: the channels
        eq(Channel.CRIER, NewsChannels.main(SettlementRank.CITY, true, LONDON_LA, LONDON_LO, 1500),
                "London in 1500 has a crier and nothing else");
        ok(NewsChannels.here(Channel.NEWSLETTER, SettlementRank.CITY, true, VENICE_LA, VENICE_LO,
                1580), "Venice has handwritten news by 1580");
        ok(!NewsChannels.here(Channel.NEWSLETTER, SettlementRank.CITY, true, LONDON_LA, LONDON_LO,
                1500), "and London does not in 1500");
        eq(Channel.NEWSPAPER, NewsChannels.main(SettlementRank.CITY, true, LONDON_LA, LONDON_LO,
                1700), "London in 1700 has a paper");
        ok(NewsChannels.here(Channel.WIRE, SettlementRank.CITY, true, HYD_LA, HYD_LO, 1900),
                "the wire had reached Hyderabad by 1900");
        ok(!NewsChannels.here(Channel.WIRE, SettlementRank.CITY, true, HYD_LA, HYD_LO, 1830),
                "and had not in 1830");
        ok(!NewsChannels.here(Channel.WIRELESS, SettlementRank.CITY, true, LONDON_LA, LONDON_LO,
                1900), "there was no wireless in 1900");
        ok(NewsChannels.here(Channel.WIRELESS, SettlementRank.CITY, true, LONDON_LA, LONDON_LO,
                1930), "and there was by 1930");
        ok(!NewsChannels.here(Channel.TELEVISION, SettlementRank.CITY, true, LONDON_LA, LONDON_LO,
                1930), "and no television in 1930");
        ok(NewsChannels.here(Channel.INSCRIPTION, SettlementRank.CITY, true, ROME_LA, ROME_LO,
                100), "Rome cuts its news in stone in AD 100");
        ok(!NewsChannels.here(Channel.INSCRIPTION, SettlementRank.VILLAGE, true, ROME_LA, ROME_LO,
                100), "and a village near Rome does not");

        // a village only ever has a crier, and from 1919 a wireless
        List<Channel> village1500 = NewsChannels.inUse(SettlementRank.VILLAGE, true, LONDON_LA,
                LONDON_LO, 1500);
        eq(1, village1500.size(), "a village in 1500 has one channel");
        eq(Channel.CRIER, village1500.get(0), "and it is the crier");

        // nobody announces anything where there is no state
        ok(!NewsChannels.here(Channel.CRIER, SettlementRank.VILLAGE, false, 0.0d, -140.0d, 1500),
                "a crier needs a state with something to announce");

        // ------------------------------------------------------- how old the news is
        ok(NewsChannels.ageDays(Channel.CRIER, 25.0d) < 3.0d,
                "a crier's news is a day or two old");
        ok(NewsChannels.ageDays(Channel.INSCRIPTION, 100.0d) > 30.0d,
                "a stone is cut long after the fact");
        eq(1.0d, NewsChannels.ageDays(Channel.WIRE, 8000.0d), "the wire is a day, always");
        eq(0.0d, NewsChannels.ageDays(Channel.WIRELESS, 8000.0d), "the wireless is the same hour");
        eq("the same hour", NewsChannels.ageText(Channel.WIRELESS, 100.0d), "the wireless in words");
        eq("a day old", NewsChannels.ageText(Channel.WIRE, 100.0d), "the wire in words");
        ok(NewsChannels.ageText(Channel.NEWSPAPER, 4000.0d).contains("weeks")
                        || NewsChannels.ageText(Channel.NEWSPAPER, 4000.0d).contains("months"),
                "a paper's foreign news is weeks old: "
                        + NewsChannels.ageText(Channel.NEWSPAPER, 4000.0d));

        // ------------------------------------------------------- D8: what a rumour loses
        eq("Have you heard? the harvest failed.", Rumour.told("the harvest failed", 0), "no hops");
        eq("Have you heard? the harvest failed.", Rumour.told("the harvest failed", 1), "one hop");
        eq("They say the harvest failed.", Rumour.told("the harvest failed", 3), "three hops");
        ok(Rumour.told("the harvest failed", 5).startsWith("It is said that"), "five hops");
        ok(Rumour.told("the harvest failed", 10).startsWith("There is a story going about"),
                "ten hops");
        ok(Rumour.told("the harvest failed", 20).startsWith("Word comes of something"),
                "twenty hops");
        eq("a great many died", Rumour.roundNumbers("300 died"), "a number rounds first");
        ok(Rumour.told("300 died", 12).contains("a great many"), "and goes by the retelling");

        Rumour.Carried near = Rumour.carried("the harvest failed", 1000, 30.0d, 10.0d, 30.0d,
                10.05d, false);
        eq(0, near.hops(), "the next village is no hops at all");
        ok(near.days() < 1.0d, "and the word is there the same day, got " + near.days());
        ok(!near.stale(), "and it is not stale");

        Rumour.Carried far = Rumour.carried("the emperor died", 100, ROME_LA, ROME_LO, 39.9d,
                116.4d, false);
        ok(far.hops() > 100, "Rome to China is a great many hops, got " + far.hops());
        ok(far.stale(), "and whatever it was is over by the time it gets there");
        ok(far.text().contains("Word comes of something"), "and the thing itself is gone: "
                + far.text());

        Rumour.Carried mid = Rumour.carried("the harvest failed", 1500, ROME_LA, ROME_LO, 48.86d,
                2.35d, false);
        ok(mid.hops() >= 20, "Rome to Paris is a long rumour, got " + mid.hops());
        ok(!mid.stale(), "and it gets there inside two years, in " + mid.days() + " days");
        ok(!mid.text().isEmpty(), "with something left of it");

        java.lang.System.out.println();
        java.lang.System.out.println("what is left of a rumour:");
        String[][] journeys = {{"the next village", "the harvest failed"},
                {"Rome to Paris", "the harvest failed"}, {"Rome to Antioch", "the emperor died"},
                {"Rome to China", "the emperor died"}};
        double[][] legs = {{30.0d, 10.0d, 30.0d, 10.05d}, {ROME_LA, ROME_LO, 48.86d, 2.35d},
                {ROME_LA, ROME_LO, 36.2d, 36.16d}, {ROME_LA, ROME_LO, 39.9d, 116.4d}};
        for (int i = 0; i < journeys.length; i++) {
            Rumour.Carried c = Rumour.carried(journeys[i][1], 1500, legs[i][0], legs[i][1],
                    legs[i][2], legs[i][3], false);
            java.lang.System.out.println("  " + journeys[i][0] + " (" + (int) c.km() + " km, "
                    + c.hops() + " hops, " + (int) Math.round(c.days()) + " days): " + c.text());
        }

        // ------------------------------------------------------- the channels through time
        java.lang.System.out.println();
        java.lang.System.out.println("how the news reached a city (C = crier, N = newsletter,"
                + " P = paper, W = wire, R = wireless, T = television, S = stone):");
        String[] names = {"London", "Rome", "Hyderabad", "Beijing", "Cusco"};
        double[][] pts = {{LONDON_LA, LONDON_LO}, {ROME_LA, ROME_LO}, {HYD_LA, HYD_LO},
                {39.9d, 116.4d}, {-13.5d, -72.0d}};
        int[] years = {100, 1000, 1400, 1500, 1600, 1700, 1800, 1850, 1900, 1940, 1970};
        java.lang.System.out.print(String.format("%-12s", ""));
        for (int year : years) {
            java.lang.System.out.print(String.format("%1$6d", year));
        }
        java.lang.System.out.println();
        for (int i = 0; i < names.length; i++) {
            StringBuilder row = new StringBuilder(String.format("%-12s", names[i]));
            for (int year : years) {
                StringBuilder marks = new StringBuilder();
                for (Channel c : NewsChannels.inUse(SettlementRank.CITY, true, pts[i][0],
                        pts[i][1], year)) {
                    marks.append(switch (c) {
                        case CRIER -> "C"; case NEWSLETTER -> "N"; case NEWSPAPER -> "P";
                        case WIRE -> "W"; case WIRELESS -> "R"; case TELEVISION -> "T";
                        case INSCRIPTION -> "S";
                    });
                }
                row.append(String.format("%1$6s", marks.isEmpty() ? "-" : marks));
            }
            java.lang.System.out.println(row);
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
'''


def method(src, signature):
    """The text of one method, from its signature line to its closing brace at the same indent."""
    lines = src.split("\n")
    i = next(n for n, l in enumerate(lines) if signature in l)
    indent = len(lines[i]) - len(lines[i].lstrip())
    j = i
    while True:
        j += 1
        if lines[j].strip() == "}" and (len(lines[j]) - len(lines[j].lstrip())) == indent:
            break
    return "\n".join(lines[i:j + 1])


def main():
    dst = sys.argv[1]
    src = open(SRC, encoding="utf-8").read()
    body = method(src, "static String dateLine(double lat, double lon, int date) {")
    years = method(src, "public static String yearText(double lat, double lon, int y) {")
    assert "KnowledgeDate." in body, "expected the masthead to use KnowledgeDate"
    body = body.replace("KnowledgeDate.", "KD.").replace("dateLine(date)",
                                                         "gregorianFallback(date)")
    years = years.replace("KnowledgeDate.", "KD.").replace("yearText(y)", "String.valueOf(y)")
    # the no-place fallbacks, so the lifted method compiles on its own
    fallback = '''
    /** The old Gregorian line, for a date the local calendar cannot be worked out for. */
    static String gregorianFallback(int date) {
        return KD.day(date) + " " + Calendars.MONTHS_GREGORIAN[KD.month(date) - 1] + " "
                + KD.year(date);
    }
'''
    open(dst, "w", encoding="utf-8").write(HEAD + body + "\n\n" + years + "\n" + fallback + TAIL_START)
    print("lifted the masthead into " + dst)


if __name__ == "__main__":
    main()
