import com.eternalengine.money.Diet;
import com.eternalengine.money.ProductAtlas;
import com.eternalengine.money.ProductAtlas.Place;
import com.eternalengine.money.ProductAtlas.Product;
import com.eternalengine.money.Shortages;
import com.eternalengine.money.Workshop;
import com.eternalengine.money.Workshop.Output;

import java.util.List;
import java.util.Locale;

/** Step 44 part 7 (D16): does any workplace turn an input into an output? Checks are printed. */
public final class Step44WorkshopProbe {

    private static int checks = 0;
    private static int failed = 0;

    private static void ok(boolean cond, String what) {
        checks++;
        if (!cond) {
            failed++;
            System.out.println("  FAIL  " + what);
        }
    }

    private static void eq(Object got, Object want, String what) {
        checks++;
        if (got == null ? want != null : !got.equals(want)) {
            failed++;
            System.out.println("  FAIL  " + what + ": got " + got + ", want " + want);
        }
    }

    /** Places chosen to be unlike each other: a town and a camp, a famine and a good year. */
    private static final double[][] PLACES = {
        {17.39, 78.49, 1600, 800},    // Hyderabad, a city
        {17.39, 78.49, 1630, 800},    // Hyderabad in the Deccan famine
        {31.55, 74.34, 1600, 300},    // Lahore
        {41.88, 12.50, 100, 5000},    // Rome, imperial
        {19.43, -99.13, 1500, 3000},  // Tenochtitlan
        {55.75, 37.62, 1450, 400},    // Moscow
        {6.52, 3.38, 1700, 600},      // Lagos
    };

    private static final String[] TRY = {"bread", "pottery", "iron_tools", "cheese", "glass",
            "paper", "cloth", "beer", "sugar", "leather", "soap", "sword"};

    public static void main(String[] args) {
        ProductAtlas atlas = ProductAtlas.get();
        System.out.println("atlas: " + atlas.summary());
        System.out.println("rates: " + Workshop.summary());

        // ---------------------------------------------------------------- the rates themselves
        ok(Workshop.rates().containsKey("craft"), "craft has a measured rate (15 products)");
        ok(!Workshop.rates().containsKey("miner"), "the miner has no measured rate, and says so");
        ok(Workshop.daysOf(atlas.product("saddle")) == 2.0d,
                "a saddle is two days of work, measured");
        ok(Workshop.rateOf(atlas.product("saddle")) == 0.5d, "half a saddle a day");
        ok(Workshop.daysOf(atlas.product("wheat")) > 0,
                "wheat takes its rate from farming, which has three measurements");
        eq(Workshop.daysOf(atlas.product("sword")), Workshop.UNMEASURED,
                "a sword is unrated rather than guessed");

        // every product either carries a measured rate or says it does not
        int rated = 0, unrated = 0;
        for (Product p : atlas.products()) {
            if (Workshop.rateOf(p) > 0) {
                rated++;
            } else {
                unrated++;
            }
        }
        System.out.println("  rated " + rated + ", unrated " + unrated + " of " + atlas.products().size());
        ok(rated > 300, "most products carry a rate (have " + rated + ")");
        ok(unrated > 0, "some are honestly unrated rather than guessed (have " + unrated + ")");
        ok(rated + unrated == atlas.products().size(), "every product is one or the other");

        // ---------------------------------------------------------------- the workshops
        System.out.println();
        System.out.println("what a workshop turns out in a day:");
        for (double[] pl : PLACES) {
            Place at = atlas.place(pl[0], pl[1], (int) pl[2]);
            System.out.println("  " + name(pl) + " (" + at.area() + ", " + (int) pl[3] + " people)");
            for (String id : TRY) {
                Product p = atlas.product(id);
                if (p == null) {
                    continue;
                }
                Output o = Workshop.at(p, pl[0], pl[1], (int) pl[2], at, (int) pl[3]);
                if (o == null) {
                    continue;
                }
                String n = String.format(Locale.ROOT, "%.2f", o.perHead());
                System.out.printf("     %-12s %-8s hands=%-4d scarce=%-10s %s%n",
                        id, o.rated() ? n : "—", o.hands(), o.scarce(), o.sentence());
                // per head cannot exceed the rate, and the ceiling is hands times the rate
                if (o.rated() && o.hands() > 0) {
                    ok(o.perHead() <= Workshop.rateOf(p) + 1e-9,
                            id + ": one person makes more than the rate allows");
                    ok(o.ceiling() <= o.hands() * Workshop.rateOf(p) + 1e-9,
                            id + ": the ceiling is more than every hand at full rate");
                    ok(o.rivals() >= 1, id + ": a workshop with no rivals at all");
                }
                ok(o.hands() >= 0, id + ": a negative number of hands");
                ok(o.scarce() != null, id + ": names what is binding");
            }
            System.out.println();
        }

        // ---------------------------------------------------------------- a famine has to bite
        System.out.println("the same workshop before and during a famine:");
        for (String id : new String[]{"bread", "beer", "cloth"}) {
            Product p = atlas.product(id);
            if (p == null) {
                continue;
            }
            Output good = Workshop.at(p, 17.39, 78.49, 1600, 800);
            Output bad = Workshop.at(p, 17.39, 78.49, 1630, 800);
            System.out.printf("   %-8s 1600 %-7.2f   1630 %-7.2f   (%s)%n", id,
                    good.perHead(), bad.perHead(), bad.why());
            ok(bad.perHead() <= good.perHead() + 1e-9,
                    id + ": a famine makes more than a good year");
        }

        // ---------------------------------------------------------------- an empty camp makes nothing
        Output nobody = Workshop.at(atlas.product("pottery"), 17.39, 78.49, 1600, 0);
        System.out.println();
        System.out.println("nobody: " + (nobody == null ? "null" : nobody.sentence()));
        ok(nobody != null && nobody.hands() == 0 && nobody.idle(), "an empty camp makes nothing");

        // ---------------------------------------------------------------- what is short, across the world
        System.out.println();
        System.out.println("what is holding workshops back (worst first):");
        for (double[] pl : new double[][]{{17.39, 78.49, 1630}, {31.55, 74.34, 1600},
                {41.88, 12.50, 100}}) {
            List<Output> shortfalls = Workshop.shortfalls(pl[0], pl[1], (int) pl[2], 800);
            System.out.printf("  %-14s %d workshops held back%n", name(pl), shortfalls.size());
            for (Output o : shortfalls.subList(0, Math.min(5, shortfalls.size()))) {
                System.out.printf("     %-16s %-10s %s%n", o.product().id(), o.scarce(), o.why());
            }
            for (Output o : shortfalls) {
                ok(!o.full(), o.product().id() + " is in the short list but is at full output");
                ok(!o.idle(), o.product().id() + " is in the short list but makes nothing");
            }
        }

        // ---------------------------------------------------------------- coverage
        System.out.println();
        int made = 0, idle = 0, hands0 = 0, material0 = 0, world0 = 0, full = 0;
        for (double lat = -50.0; lat <= 66.0; lat += 14.0) {
            for (double lon = -170.0; lon <= 170.0; lon += 20.0) {
                for (int year = -3000; year <= 1900; year += 500) {
                    Place at = atlas.place(lat, lon, year);
                    for (String id : new String[]{"bread", "pottery", "cheese", "cloth"}) {
                        Product p = atlas.product(id);
                        if (p == null) {
                            continue;
                        }
                        Output o = Workshop.at(p, lat, lon, year, at, 400);
                        if (o == null) {
                            continue;
                        }
                        if (o.idle()) {
                            idle++;
                        } else {
                            made++;
                        }
                        switch (o.scarce()) {
                            case "hands" -> hands0++;
                            case "material" -> material0++;
                            case "the world" -> world0++;
                            default -> full++;
                        }
                        ok(o.hands() <= 400, id + ": more workers than people");
                        if (o.rated()) {
                            ok(o.perHead() >= 0, id + ": a negative output");
                        }
                    }
                }
            }
        }
        System.out.printf("  %d workshop-days: %d producing, %d idle%n", made + idle, made, idle);
        System.out.printf("  held back by: hands %d, material %d, the world %d, nothing %d%n",
                hands0, material0, world0, full);
        ok(made > 0, "somewhere, something is made");
        ok(material0 + world0 > 0, "something, somewhere, is held back by more than hands");

        System.out.println();
        System.out.println("workshop: " + checks + " checks, " + failed + " failed");
        if (failed > 0) {
            System.exit(1);
        }
    }

    private static String name(double[] pl) {
        if (Math.abs(pl[0] - 17.39) < 0.5) return "Hyderabad";
        if (Math.abs(pl[0] - 31.55) < 0.5) return "Lahore";
        if (Math.abs(pl[0] - 41.88) < 0.5) return "Rome";
        if (Math.abs(pl[0] - 19.43) < 0.5) return "Tenochtitlan";
        if (Math.abs(pl[0] - 55.75) < 0.5) return "Moscow";
        if (Math.abs(pl[0] - 6.52) < 0.5) return "Lagos";
        return pl[0] + "," + pl[1];
    }
}
