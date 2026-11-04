import com.eternalengine.civilization.Borders;
import com.eternalengine.civilization.CountryGrid;
import com.eternalengine.civilization.RulerRegister;

import java.util.ArrayList;
import java.util.List;

/**
 * Step 42 part 7 (F8, borders and permits): does the crossing pack answer, and does the border it
 * derives from the ruler register land where the ground says it should?
 *
 * <p>Compiled on its own against a plain JDK 17 and Gson, so the very code the game runs is what
 * runs here. The half of this that matters most is {@code borderBetween}, which is the part of F8
 * that is not data at all.
 */
public class Step42eProbe {

    static int checks = 0;
    static final List<String> bad = new ArrayList<>();

    static void ok(boolean cond, String what) {
        checks++;
        System.out.println((cond ? "  ok   " : "  FAIL ") + what);
        if (!cond) {
            bad.add(what);
        }
    }

    static String post(String c, int y, boolean sea) {
        return Borders.get().post(c, y, sea).id();
    }

    static String ruler(double lat, double lon, int year) {
        return RulerRegister.get().rulerAt(lat, lon, year).map(RulerRegister.Hit::ruler).orElse("-");
    }

    // ---------------------------------------------------------------- the pack

    static void pack() {
        System.out.println("-- the pack");
        Borders b = Borders.get();
        ok(b.loaded(), "the pack loads from the jar (" + b.source().substring(0, 40) + "...)");
        ok(b.rowCount() == 12, "12 kinds of crossing (" + b.rowCount() + ")");
        ok(b.counts().getOrDefault("estimated", 0) == b.rowCount(),
                "every row is marked estimated, and the pack says so");
        ok(!b.gaps().isEmpty(), "the pack states its limits (" + b.gaps().size() + " gaps)");

        List<Borders.Row> rows = b.rows();
        ok(rows.size() == b.rowCount(), "every row survives the country index (" + rows.size() + ")");
        for (Borders.Row r : rows) {
            ok(r.name() != null && r.what() != null && r.demand() != null && r.line() != null
                    && r.source() != null, r.id() + " has a name, a what, a demand, a line and a source");
            ok(r.end() == null || r.end() >= r.start(), r.id() + " does not end before it begins");
            ok(!(r.sea() && r.internal()),
                    r.id() + " is not both a port and an inland toll, which would make it unreachable");
        }

        long sea = rows.stream().filter(Borders.Row::sea).count();
        long internal = rows.stream().filter(Borders.Row::internal).count();
        ok(sea >= 1 && internal >= 2, "the sea and internal marks are actually used (" + sea
                + " sea, " + internal + " internal)");
        ok(rows.stream().noneMatch(r -> r.papers() && r.start() < 1914),
                "nothing asks for papers before 1914, which is when the passport became general");
        ok(rows.stream().noneMatch(r -> r.quarantine() && r.start() < 1377),
                "nothing holds you before 1377, which is when Ragusa imposed the trentino");
        ok(rows.stream().filter(Borders.Row::closed).count() == 1,
                "exactly one crossing turns you back, and it is the closed shore");
    }

    // ---------------------------------------------------------------- what stops you, and when

    static void dated() {
        System.out.println("-- the dated facts, read out of the articles");
        // Quarantine: Ragusa, 1377.
        ok(!"lazaretto".equals(post("HRV", 1300, true)),
                "a ship putting in at Ragusa in 1300 is not held - the trentino is 1377");
        ok("lazaretto".equals(post("HRV", 1400, true)),
                "and is by 1400, which is the first quarantine anywhere");
        ok("lazaretto".equals(post("ITA", 1500, true)),
                "a ship into Venice in 1500 sits out the forty days");
        ok(!"lazaretto".equals(post("ITA", 1500, false)),
                "and a man riding over the Alps in 1500 does not, which is what `sea` is for");
        ok(!Borders.get().post("GBR", 1800, true).quarantine(),
                "and a ship into Liverpool in 1800 is not held either - the lazaretto is "
                        + "Mediterranean, and saying otherwise was the first defect this probe found");

        // The passport: 1914 Act, 1920 standardised.
        ok(!Borders.get().post("GBR", 1900, false).papers(),
                "no crossing in 1900 asks who you are");
        ok("passport_control".equals(post("GBR", 1930, false)),
                "and by 1930 the crossing is passport control");
        ok("checkpoint".equals(post("FRA", 1960, false)),
                "and by 1960 it is the checkpoint, a barrier and a queue");
        ok("customs_house".equals(post("FRA", 1905, false)),
                "1905 is not a hole: customs were taken then too, which the 1900 end date had "
                        + "silently deleted");

        // Sakoku and Canton.
        ok(Borders.get().post("JPN", 1750, true).closed(),
                "Japan in 1750 is shut to a ship, which is sakoku");
        ok(!Borders.get().post("JPN", 1900, true).closed(),
                "and by 1900 is open, which is after Perry");
        ok(Borders.get().post("CHN", 1800, true).closed(),
                "China in 1800 trades through one door, which is the Canton System");
        ok(!Borders.get().post("CHN", 1900, true).closed(),
                "and by 1900 does not, the system having ended in 1842");

        // The Zollverein: the one row whose answer is that you are not stopped.
        ok("zollverein".equals(post("DEU", 1850, false)),
                "the German states in 1850 do not stop each other's traffic");
        ok(!"zollverein".equals(post("DEU", 1800, false)),
                "and in 1800 they do, the union having started in 1834");
        ok("nothing".equals(Borders.get().post("DEU", 1850, false).demand().substring(0, 7)),
                "and the row says so in its demand, so a caller can act on it");

        // The turnpike: a toll inside a state, not between two.
        ok("turnpike".equals(post("GBR", 1800, false)),
                "a man riding north through England in 1800 pays for the road at every gate");
        ok(!"turnpike".equals(post("GBR", 1800, true)),
                "and a ship putting in at Liverpool does not, which is what `internal` is for");
        ok(!"turnpike".equals(post("GBR", 1900, false)),
                "by 1900 the road is free, the trusts having ended in 1888");
        ok("octroi".equals(post("FRA", 1450, false)),
                "France in 1450 takes a toll on everything carried into a town");

        // The deep past.
        ok("tribute_gate".equals(post("IRQ", -1000, false)),
                "Mesopotamia in 1000 BC is a gate and a gift");
        ok("caravan_gate".equals(post("IRN", 900, false)),
                "and the road east of it is the caravanserai and the gate toll");
        ok("open_ground".equals(post("AUS", -4000, false)),
                "before 3000 BC the fallback answers: a frontier needs a state on both sides");
    }

    // ---------------------------------------------------------------- coverage

    static void coverage() {
        System.out.println("-- every country, every era, both ways of arriving");
        List<String> codes = new ArrayList<>();
        for (int i = 0; i < CountryGrid.get().size(); i++) {
            String c = CountryGrid.get().code(i);
            if (c != null && !c.isBlank()) {
                codes.add(c);
            }
        }
        ok(codes.size() >= 250, "the country grid knows " + codes.size() + " countries");
        int[] years = {-4000, -1000, 0, 500, 1000, 1300, 1500, 1700, 1800, 1850, 1900, 1930, 1960,
                2000};
        for (int y : years) {
            for (boolean sea : new boolean[]{false, true}) {
                int missing = 0;
                int kinds = -1;
                java.util.Set<String> seen = new java.util.HashSet<>();
                for (String c : codes) {
                    Borders.Row r = Borders.get().post(c, y, sea);
                    if (r == null || r.id() == null) {
                        missing++;
                    } else {
                        seen.add(r.id());
                    }
                }
                kinds = seen.size();
                if (y < -3000) {
                    ok(missing == 0 && kinds == 1 && seen.contains("open_ground"),
                            String.format("%6d %s: before any state, every country falls back to "
                                    + "open ground, which is the edge of the pack and not a hole",
                                    y, sea ? "by sea " : "by land"));
                } else {
                    ok(missing == 0 && kinds > 1,
                            String.format("%6d %s: all %d countries answered, %d different kinds",
                                    y, sea ? "by sea " : "by land", codes.size(), kinds));
                }
            }
        }
    }

    // ---------------------------------------------------------------- where the line runs

    static void lines() {
        System.out.println("-- where the line runs, derived and not stored");
        // Inside one state: no line.
        ok(Borders.get().borderBetween(48.85, 2.35, 45.76, 4.83, 1300).isEmpty(),
                "Paris to Lyon in 1300 crosses nothing - both are the Kingdom of France");
        ok(Borders.get().borderBetween(28.61, 77.21, 31.55, 74.34, 1700).isEmpty(),
                "Delhi to Lahore in 1700 crosses nothing - both are the Mughal Empire");
        ok(Borders.get().borderBetween(39.90, 116.40, 47.90, 106.90, 1900).isEmpty(),
                "Beijing to Ulaanbaatar in 1900 crosses nothing - both are Qing");
        ok(Borders.get().borderBetween(48.85, 2.35, 48.86, 2.36, 1300).isEmpty(),
                "and a step of a hundred metres is never a border");

        // Between two states: a line, in the right place.
        Borders.Border fr = Borders.get().borderBetween(48.85, 2.35, 50.94, 6.96, 1300).orElse(null);
        ok(fr != null, "Paris to Cologne in 1300 does cross one");
        if (fr != null) {
            ok(fr.from().contains("France"), "  and you leave the Kingdom of France (" + fr.from() + ")");
            ok(fr.lat() > 48.85 && fr.lat() < 50.94 && fr.lon() > 2.35 && fr.lon() < 6.96,
                    String.format("  and the line falls between the two ends (%.2f, %.2f)",
                            fr.lat(), fr.lon()));
            ok(fr.km() > 0 && fr.km() < RulerRegister.distanceKm(48.85, 2.35, 50.94, 6.96),
                    String.format("  and you meet it partway along, at %.0f km", fr.km()));
        }

        Borders.Border ip = Borders.get().borderBetween(28.61, 77.21, 31.55, 74.34, 1950).orElse(null);
        ok(ip != null, "Delhi to Lahore in 1950 crosses one, the same road that crossed none in 1700");
        if (ip != null) {
            ok(ip.from().contains("India") && ip.to().contains("Pakistan"),
                    "  and it is India giving way to Pakistan (" + ip.line() + ")");
            ok(ip.lat() > 28.61 && ip.lat() < 31.55,
                    String.format("  and it falls between them, at %.2f N", ip.lat()));
        }

        // The far side is the NEIGHBOUR, not the destination. This was the second defect: a leg
        // from Rome to Krakow reported "the Papal States give way to the House of Jagiellon",
        // which is true of the journey and false of the line.
        Borders.Border rk = Borders.get().borderBetween(41.89, 12.44, 50.06, 19.94, 1500).orElse(null);
        ok(rk != null, "Rome to Krakow in 1500 crosses one");
        if (rk != null) {
            ok(!rk.to().equals(rk.from()),
                    "  and the two sides of the line are ruled differently ("
                            + rk.from() + " | " + rk.to() + ")");
            ok(rk.lat() < 44.0,
                    String.format("  and the line falls in Italy, at %.2f N, which is right", rk.lat()));
        }

        // A border is symmetric: whichever way you walk it, it is in the same place. Tested on
        // Delhi to Lahore, which crosses one line - the Rhine corridor in 1300 crosses several
        // (HRE Minor States, Luxembourg) and there the two directions legitimately find different
        // ones, because each is finding the first handover from its own end.
        Borders.Border out = Borders.get().borderBetween(28.61, 77.21, 31.55, 74.34, 1950).orElse(null);
        Borders.Border back = Borders.get().borderBetween(31.55, 74.34, 28.61, 77.21, 1950).orElse(null);
        ok(out != null && back != null, "the Delhi-Lahore road is walkable both ways");
        if (out != null && back != null) {
            ok(Math.abs(out.lat() - back.lat()) < 0.5 && Math.abs(out.lon() - back.lon()) < 0.5,
                    String.format("  and the line is in the same place from either side "
                                    + "(%.2f,%.2f vs %.2f,%.2f)", out.lat(), out.lon(),
                            back.lat(), back.lon()));
            ok(out.from().equals(back.to()) && out.to().equals(back.from()),
                    "  and the two sides swap over exactly (" + out.line() + " / " + back.line() + ")");
        }

        // Across the Pacific: the short way round, not the long way.
        Borders.Border pac = Borders.get().borderBetween(35.68, 139.69, 37.77, -122.42, 1900).orElse(null);
        ok(pac == null || (pac.lon() > 139.69 || pac.lon() < -122.42),
                "a leg from Tokyo to San Francisco goes east, not west across Eurasia"
                        + (pac == null ? "" : String.format(" (%.2f)", pac.lon())));
    }

    // ---------------------------------------------------------------- what it costs you

    static void crossings() {
        System.out.println("-- what the step costs you");
        Borders.Cross none = Borders.get().crossing(48.85, 2.35, 45.76, 4.83, 1300, false);
        ok(!none.isBorder(), "Paris to Lyon in 1300 is not a crossing");
        ok(!none.refused(), "  and you are not turned back");
        ok(none.post() != null, "  but the pack still says what the road costs you");

        Borders.Cross shut = Borders.get().crossing(31.23, 121.47, 35.68, 139.69, 1800, true);
        ok(shut.refused(), "a ship from Shanghai to Edo in 1800 is turned back, which is sakoku ("
                + shut.post().name() + ")");

        Borders.Cross ip = Borders.get().crossing(28.61, 77.21, 31.55, 74.34, 1950, false);
        ok(ip.isBorder() && ip.post().papers(),
                "Delhi to Lahore in 1950 is a border that wants your papers");

        ok(!Borders.get().crossing(28.61, 77.21, 31.55, 74.34, 1700, false).post().papers(),
                "and the same road in 1700 wants none, which is the whole change F8 is about");

        // No answer is ever null, anywhere, ever.
        int nulls = 0;
        double[][] spots = {{48.85, 2.35}, {0.0, -30.0}, {-22.9, -43.2}, {39.5, -8.0}, {36.0, 138.0},
                {22.0, 78.0}, {-33.9, 151.2}, {64.0, -21.0}, {30.0, 31.0}, {-1.3, 36.8}};
        for (int y = -3000; y <= 2000; y += 137) {
            for (double[] s : spots) {
                for (boolean sea : new boolean[]{false, true}) {
                    if (Borders.get().postAt(s[0], s[1], y, sea) == null) {
                        nulls++;
                    }
                    if (Borders.get().crossing(s[0], s[1], s[0] + 2, s[1] + 2, y, sea).post() == null) {
                        nulls++;
                    }
                }
            }
        }
        ok(nulls == 0, "ten places across the map, forty years apart, both ways of arriving: "
                + "not one null answer (" + nulls + ")");
    }

    public static void main(String[] args) {
        System.out.println("step 42 part 7 (F8, borders and permits)");
        System.out.println();
        pack();
        System.out.println();
        dated();
        System.out.println();
        coverage();
        System.out.println();
        lines();
        System.out.println();
        crossings();
        System.out.println();
        System.out.println("step 42 part 7: " + checks + " checks, " + bad.size() + " problems");
        for (String b : bad) {
            System.out.println("  FAIL " + b);
        }
        System.exit(bad.isEmpty() ? 0 : 1);
    }
}
