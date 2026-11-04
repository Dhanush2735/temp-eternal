package com.eternalengine.calprobe;

import com.eternalengine.news.NewsTravel;
import com.eternalengine.news.NewsTravel.Leg;
import com.eternalengine.news.NewsTravel.Mode;

import java.util.ArrayList;
import java.util.List;

/**
 * Step 37 (C24 the speed of news, E20 post and messages): run the travel register against the
 * record. Every check here can fail, and several of them are checked against what actually
 * happened — the month a ship took from Rome to Antioch, the three days the post took from
 * London to Edinburgh in the 1690s, and the day the wire put London and Calcutta in touch.
 */
public final class TravelRun {

    private static int passed;
    private static final List<String> failures = new ArrayList<>();

    static void ok(boolean b, String what) {
        if (b) {
            passed++;
        } else {
            failures.add(what);
        }
    }

    static void between(double want, double got, double spread, String what) {
        if (got >= want - spread && got <= want + spread) {
            passed++;
        } else {
            failures.add(what + ": wanted about " + want + " (+/- " + spread + "), got " + got);
        }
    }

    static void eq(Object want, Object got, String what) {
        if (want == null ? got == null : want.equals(got)) {
            passed++;
        } else {
            failures.add(what + ": wanted " + want + ", got " + got);
        }
    }

    // a few places, as latitude and longitude
    private static final double ROME_LA = 41.9d, ROME_LO = 12.5d;
    private static final double ANTIOCH_LA = 36.2d, ANTIOCH_LO = 36.16d;
    private static final double LONDON_LA = 51.5d, LONDON_LO = -0.13d;
    private static final double EDINBURGH_LA = 55.95d, EDINBURGH_LO = -3.19d;
    private static final double CALCUTTA_LA = 22.57d, CALCUTTA_LO = 88.36d;
    private static final double DELHI_LA = 28.61d, DELHI_LO = 77.21d;
    private static final double PARIS_LA = 48.86d, PARIS_LO = 2.35d;

    public static void main(String[] args) {
        // ------------------------------------------------------- Rome to Antioch, AD 100
        Leg sea = NewsTravel.fastest(100, ROME_LA, ROME_LO, ANTIOCH_LA, ANTIOCH_LO, true);
        ok(sea != null, "Rome to Antioch by sea has an answer in AD 100");
        eq(Mode.SAIL, sea.mode(), "Rome to Antioch by sea, AD 100, went by ship");
        between(31.0d, sea.days(), 12.0d, "Rome to Antioch by sea, AD 100 (about a month)");

        Leg land = NewsTravel.fastest(100, ROME_LA, ROME_LO, ANTIOCH_LA, ANTIOCH_LO, false);
        eq(Mode.RIDER, land.mode(), "Rome to Antioch overland, AD 100, went by rider");
        between(34.0d, land.days(), 12.0d, "Rome to Antioch overland, AD 100");

        // ------------------------------------------------------- London to Edinburgh
        Leg ed1350 = NewsTravel.fastest(1350, LONDON_LA, LONDON_LO, EDINBURGH_LA, EDINBURGH_LO,
                false);
        eq(Mode.RIDER, ed1350.mode(), "London to Edinburgh in 1350 went by rider");
        between(9.0d, ed1350.days(), 3.0d, "London to Edinburgh in 1350");
        ok(!NewsTravel.available(Mode.POST, LONDON_LA, LONDON_LO, 1350),
                "there was no public post in 1350");

        Leg ed1700 = NewsTravel.fastest(1700, LONDON_LA, LONDON_LO, EDINBURGH_LA, EDINBURGH_LO,
                false);
        eq(Mode.POST, ed1700.mode(), "London to Edinburgh in 1700 went by post");
        between(4.0d, ed1700.days(), 2.0d, "London to Edinburgh in 1700 (the post took three)");

        Leg ed1850 = NewsTravel.fastest(1850, LONDON_LA, LONDON_LO, EDINBURGH_LA, EDINBURGH_LO,
                false);
        eq(Mode.RAILWAY, ed1850.mode(), "London to Edinburgh in 1850 went by railway");
        between(1.0d, ed1850.days(), 1.0d, "London to Edinburgh in 1850");

        // ------------------------------------------------------- London to Calcutta: the wire
        ok(!NewsTravel.available(Mode.WIRE, LONDON_LA, LONDON_LO, 1830),
                "there was no telegraph in 1830");
        ok(NewsTravel.available(Mode.WIRE, LONDON_LA, LONDON_LO, 1850),
                "the telegraph had reached London by 1850");

        Leg cal1750 = NewsTravel.fastest(1750, LONDON_LA, LONDON_LO, CALCUTTA_LA, CALCUTTA_LO,
                true);
        eq(Mode.SAIL, cal1750.mode(), "London to Calcutta in 1750 went by sea");
        between(120.0d, cal1750.days(), 40.0d, "London to Calcutta in 1750");

        Leg cal1870 = NewsTravel.fastest(1870, LONDON_LA, LONDON_LO, CALCUTTA_LA, CALCUTTA_LO,
                true);
        eq(Mode.WIRE, cal1870.mode(), "London to Calcutta in 1870 went down the wire");
        eq(1.0d, cal1870.days(), "the wire is a day, whatever the distance");

        Leg delhi1940 = NewsTravel.fastest(1940, LONDON_LA, LONDON_LO, DELHI_LA, DELHI_LO, true);
        eq(Mode.AIRWAVE, delhi1940.mode(), "London to Delhi in 1940 went over the air");
        eq(0.0d, delhi1940.days(), "the air is the same day");

        // ------------------------------------------------------- the next village
        // ten kilometres down the road: the question the plan asks
        Leg village = NewsTravel.fastest(1000, 30.0d, 10.0d, 30.0d, 10.1d, false);
        ok(village != null && village.days() < 1.0d,
                "news reaches the next village inside a day, got "
                        + (village == null ? "nothing" : village.describe()));

        // ------------------------------------------------------- the incidental channel is slowest
        Leg traveller = NewsTravel.traveller(1500, ROME_LA, ROME_LO, ANTIOCH_LA, ANTIOCH_LO, true);
        Leg best1500 = NewsTravel.fastest(1500, ROME_LA, ROME_LO, ANTIOCH_LA, ANTIOCH_LO, true);
        ok(traveller != null && best1500 != null && traveller.days() > best1500.days(),
                "news nobody carries on purpose is slower than news somebody carries");

        // ------------------------------------------------------- ships only on water, riders only on land
        ok(NewsTravel.leg(Mode.SAIL, 1500, ROME_LA, ROME_LO, ANTIOCH_LA, ANTIOCH_LO, false)
                .isEmpty(), "a ship does not sail overland");
        ok(NewsTravel.leg(Mode.RIDER, 1500, ROME_LA, ROME_LO, ANTIOCH_LA, ANTIOCH_LO, true)
                .isEmpty(), "a rider does not ride the sea");
        ok(NewsTravel.leg(Mode.TRAVELLER, 1500, ROME_LA, ROME_LO, ANTIOCH_LA, ANTIOCH_LO, true)
                .isPresent(), "a traveller goes either way");

        // ------------------------------------------------------- the list is sorted and complete
        List<Leg> all = NewsTravel.all(1750, LONDON_LA, LONDON_LO, PARIS_LA, PARIS_LO, false);
        ok(!all.isEmpty(), "there is always at least one way");
        boolean sorted = true;
        for (int i = 1; i < all.size(); i++) {
            if (all.get(i).days() < all.get(i - 1).days()) {
                sorted = false;
            }
        }
        ok(sorted, "the list comes back quickest first");

        // ------------------------------------------------------- the words
        eq("the same day", NewsTravel.phrase(0.0d), "phrase for no time at all");
        eq("the next day", NewsTravel.phrase(1.0d), "phrase for a day");
        eq("in about 9 days", NewsTravel.phrase(9.0d), "phrase for nine days");
        eq("in about 4 weeks", NewsTravel.phrase(30.0d), "phrase for a month");
        eq("in about 6 months", NewsTravel.phrase(180.0d), "phrase for half a year");

        // ------------------------------------------------------- what it says
        java.lang.System.out.println("how long the news took:");
        String[][] routes = {
                {"Rome", "Antioch", "sea"}, {"Rome", "Antioch", "land"},
                {"London", "Edinburgh", "land"}, {"London", "Calcutta", "sea"},
                {"London", "Delhi", "land"}, {"Beijing", "Rome", "land"},
                {"Cusco", "Cusco's next valley", "land"},
        };
        double[][] points = {
                {ROME_LA, ROME_LO, ANTIOCH_LA, ANTIOCH_LO},
                {ROME_LA, ROME_LO, ANTIOCH_LA, ANTIOCH_LO},
                {LONDON_LA, LONDON_LO, EDINBURGH_LA, EDINBURGH_LO},
                {LONDON_LA, LONDON_LO, CALCUTTA_LA, CALCUTTA_LO},
                {LONDON_LA, LONDON_LO, DELHI_LA, DELHI_LO},
                {39.9d, 116.4d, ROME_LA, ROME_LO},
                {-13.5d, -72.0d, -13.5d, -71.9d},
        };
        int[] years = {-200, 100, 500, 1000, 1350, 1500, 1600, 1700, 1780, 1830, 1850, 1870,
                1900, 1940, 1970};
        java.lang.System.out.print("              ");
        for (int year : years) {
            java.lang.System.out.print(String.format("%1$6d", year));
        }
        // ------------------------------------------------------- what the data says
        // the register is only as good as the atlas it reads; show the years it is reading
        java.lang.System.out.println();
        java.lang.System.out.println("the year each road reached each place (blank = never):");
        String[] towns = {"London", "Edinburgh", "Rome", "Antioch", "Calcutta", "Delhi",
                "Beijing", "Cusco"};
        double[][] at = {{LONDON_LA, LONDON_LO}, {EDINBURGH_LA, EDINBURGH_LO},
                {ROME_LA, ROME_LO}, {ANTIOCH_LA, ANTIOCH_LO}, {CALCUTTA_LA, CALCUTTA_LO},
                {DELHI_LA, DELHI_LO}, {39.9d, 116.4d}, {-13.5d, -72.0d}};
        Mode[] roads = {Mode.POST, Mode.STEAMSHIP, Mode.RAILWAY, Mode.MOTOR, Mode.WIRE,
                Mode.AIRWAVE};
        java.lang.System.out.print(String.format("%-12s", ""));
        for (String t : towns) {
            java.lang.System.out.print(String.format("%1$10s", t));
        }
        java.lang.System.out.println();
        for (Mode m : roads) {
            java.lang.System.out.print(String.format("%-12s", m.name().toLowerCase()));
            for (double[] q : at) {
                int y = NewsTravel.arrivalOf(m, q[0], q[1]);
                java.lang.System.out.print(String.format("%1$10s",
                        y == Integer.MIN_VALUE ? "always"
                                : y == Integer.MAX_VALUE ? "-" : String.valueOf(y)));
            }
            java.lang.System.out.println();
        }

        java.lang.System.out.println();
        for (int r = 0; r < routes.length; r++) {
            boolean bySea = routes[r][2].equals("sea");
            StringBuilder row = new StringBuilder();
            row.append(String.format("%-14s", (routes[r][0] + "-" + routes[r][1]).length() > 13
                    ? (routes[r][0] + "-" + routes[r][1]).substring(0, 13)
                    : routes[r][0] + "-" + routes[r][1]));
            for (int year : years) {
                Leg l = NewsTravel.fastest(year, points[r][0], points[r][1], points[r][2],
                        points[r][3], bySea);
                row.append(String.format("%1$6s", l == null ? "-" : (int) Math.round(l.days())));
            }
            java.lang.System.out.println(row + "   (" + routes[r][2] + ", in days)");
        }
        java.lang.System.out.println();
        for (int r = 0; r < routes.length; r++) {
            boolean bySea = routes[r][2].equals("sea");
            for (int year : new int[] {100, 1500, 1850, 1940}) {
                Leg l = NewsTravel.fastest(year, points[r][0], points[r][1], points[r][2],
                        points[r][3], bySea);
                if (l != null) {
                    java.lang.System.out.println("  " + year + "  " + routes[r][0] + " to "
                            + routes[r][1] + ": " + l.describe());
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
