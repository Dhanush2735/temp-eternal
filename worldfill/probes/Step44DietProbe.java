import com.eternalengine.money.Diet;
import com.eternalengine.money.Diet.Meal;
import com.eternalengine.money.Diet.Serving;
import com.eternalengine.money.ProductAtlas;

import java.util.ArrayList;
import java.util.List;

/** Step 44 part 6 (E6): what a place eats. Checks are printed, so a wrong number is visible. */
public final class Step44DietProbe {

    private static final String[] AREAS = {"NNA", "MNA", "CAC", "SAM", "EUR", "EEU", "WAS", "NAF",
            "WAF", "MSA", "EAF", "CAS", "SAS", "EAS", "SEA", "AUS", "PAC"};

    private static int checks = 0;
    private static int failed = 0;

    /**
     * The ordering a seat must obey.
     *
     * <p>The rule is not "grown before gathered" on its own. A food already named at an earlier
     * seat is demoted below everything else, deliberately: honey is the sweet of a boreal forest
     * even though dates are the cultivated crop, because dates have already been named as the
     * fruit. So the invariant only binds between two foods that are equally already-named.
     */
    private static void checkOrder(List<Serving> ss, String label) {
        for (int i = 0; i < ss.size(); i++) {
            for (int j = i + 1; j < ss.size(); j++) {
                Serving a = ss.get(i), b = ss.get(j);
                if (a.used() == b.used() && b.tilled() && !a.tilled()) {
                    ok(false, label + ": " + b.name() + " is grown but named after the gathered "
                            + a.name());
                }
                if (a.used() == b.used() && a.tilled() == b.tilled() && b.madeHere() && !a.madeHere()) {
                    ok(false, label + ": " + b.name() + " is made here but named after the brought "
                            + a.name());
                }
            }
        }
    }

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

    private static final double[][] PLACES = {
        {17.39, 78.49, -1500},   // Hyderabad, deep prehistory
        {17.39, 78.49, 1600},    // Hyderabad, Mughal Deccan
        {17.39, 78.49, 1900},    // Hyderabad, after the Columbian exchange
        {31.55, 74.34, 1600},    // Lahore, the Punjab
        {41.88, 12.50, 100},     // Rome, imperial
        {41.88, 12.50, 1550},    // Rome, after the tomato
        {19.43, -99.13, 1500},   // Tenochtitlan, before the Spanish
        {-13.53, -71.97, 1400},  // Cusco, Inca
        {6.52, 3.38, 1700},      // Lagos
        {22.32, 114.17, 1200},   // Guangzhou, Song
        {55.75, 37.62, 1450},    // Moscow
        {-33.87, 151.21, 1788},  // Sydney, first fleet
        {-17.65, -149.45, 1300}, // Tahiti, the sweet potato
        {30.04, 31.24, -2000},   // Cairo, Old Kingdom
    };

    public static void main(String[] args) {
        ProductAtlas atlas = ProductAtlas.get();
        System.out.println("atlas: " + atlas.summary());
        if (atlas.problem() != null) {
            System.out.println("  atlas problem: " + atlas.problem());
        }

        Diet diet = Diet.get();
        System.out.println("diet: " + diet.summary());
        ok(diet.loaded(), "the seat pack loads");
        eq(diet.problem(), null, "no problem reading the seat pack");
        ok(diet.foods() >= 80, "at least 80 foods hold a seat (have " + diet.foods() + ")");
        eq(diet.seats().size(), 11, "eleven seats at the table");
        ok(diet.seats().contains("staple"), "the grain has a seat");
        ok(diet.seatWord("staple").equals("the grain"), "the grain is called 'the grain'");
        ok(diet.seatWord("fat").startsWith("the fat"), "the fat is called 'the fat ...'");

        // ---------------------------------------------------------------- every seat has food in it
        for (String seat : diet.seats()) {
            ok(diet.table().containsKey(seat), "seat '" + seat + "' has something that can fill it");
        }

        // ---------------------------------------------------------------- the meals
        System.out.println();
        System.out.println("what a place eats:");
        for (double[] pl : PLACES) {
            double lat = pl[0], lon = pl[1];
            int year = (int) pl[2];
            Meal meal = diet.at(lat, lon, year);
            System.out.printf("  %-14s %-6d %-6s %s%n",
                    name(lat, lon), year, meal.place().area(),
                    Diet.sentence(meal));
            // what is named must actually be here
            for (Serving s : meal.all()) {
                ProductAtlas.Product p = atlas.product(s.id());
                ok(p != null, s.id() + " is a real product");
                if (p != null) {
                    ok(atlas.status(p, meal.place()).status().present(),
                            s.id() + " is really at " + name(lat, lon) + " in " + year);
                }
            }
            for (String seat : meal.seats().keySet()) {
                ok(diet.seats().contains(seat), "'" + seat + "' is a real seat");
            }
        }

        // ---------------------------------------------------------------- the world changes
        System.out.println();
        System.out.println("the same place, before and after:");
        for (double[] pl : new double[][]{{41.88, 12.50, 1500, 1600}, {17.39, 78.49, 1490, 1650},
                {-17.65, -149.45, 1100, 1300}}) {
            Meal before = diet.at(pl[0], pl[1], (int) pl[2]);
            Meal after = diet.at(pl[0], pl[1], (int) pl[3]);
            System.out.printf("  %-14s %-6d %s%n", name(pl[0], pl[1]), (int) pl[2], Diet.sentence(before));
            System.out.printf("  %-14s %-6d %s%n", name(pl[0], pl[1]), (int) pl[3], Diet.sentence(after));
            ok(!before.all().isEmpty() || before.thin(), "a thin place says so rather than printing nothing");
            System.out.println();
        }

        // ---------------------------------------------------------------- made here before brought
        System.out.println("what is made here, against what is brought:");
        Meal punjab = diet.at(31.55, 74.34, 1600);
        for (String seat : punjab.seats().keySet()) {
            checkOrder(punjab.at(seat), seat);
        }
        for (String seat : punjab.seats().keySet()) {
            System.out.printf("   %-11s %s%n", seat, join(punjab.at(seat)));
        }

        // ---------------------------------------------------------------- nothing, somewhere
        // The mid Atlantic and Tahiti both fall outside the survey's 146 regions -- the first
        // because it is water, the second because it is a small island. Only one of them should
        // be silent, and it is not the one with the sweet potato.
        Meal sea = diet.at(0.0, -30.0, -4000);
        Meal tahiti = diet.at(-17.65, -149.45, 1300);
        System.out.println();
        System.out.println("mid Atlantic: " + Diet.sentence(sea) + "   [mapped=" + sea.mapped() + "]");
        System.out.println("Tahiti 1300 : " + Diet.sentence(tahiti) + "   [mapped=" + tahiti.mapped() + "]");
        ok(!sea.mapped(), "the mid Atlantic is outside the survey's regions");
        ok(!tahiti.mapped(), "Tahiti is outside the survey's regions, and is still answered");
        ok(!tahiti.seats().isEmpty(), "Tahiti has a meal, mapped or not");
        ok(tahiti.seats().containsKey("staple"), "Tahiti has a grain");
        boolean sp = false;
        for (Serving v : tahiti.at("staple")) {
            if (v.id().equals("sweet_potato")) {
                sp = true;
            }
        }
        ok(sp, "Tahiti in 1300 eats sweet potatoes, which reached Polynesia about 1210");

        // ---------------------------------------------------------------- coverage: everywhere, everywhen
        // The step is not done for one place in one century. Every inhabited latitude and every
        // thousand years from the start of the game to now has to produce an answer that is true.
        System.out.println();
        System.out.println("coverage sweep:");
        int meals = 0, withGrain = 0, withAll = 0, bare = 0;
        int[] perArea = new int[20];
        for (double lat = -58.0; lat <= 70.0; lat += 8.0) {
            for (double lon = -178.0; lon <= 178.0; lon += 16.0) {
                for (int year = -4000; year <= 1900; year += 400) {
                    Meal m = diet.at(lat, lon, year);
                    meals++;
                    if (m.seats().isEmpty()) {
                        bare++;
                        continue;
                    }
                    if (m.seats().containsKey("staple")) {
                        withGrain++;
                    }
                    if (m.seats().size() == diet.seats().size()) {
                        withAll++;
                    }
                    int k = java.util.Arrays.asList(AREAS).indexOf(m.place().area());
                    if (k >= 0 && k < perArea.length) {
                        perArea[k]++;
                    }
                    // whatever is named must really be there, and must not be named twice
                    List<String> seen = new ArrayList<>();
                    for (Serving v : m.all()) {
                        ProductAtlas.Product p = atlas.product(v.id());
                        ok(p != null, v.id() + " is a real product");
                        if (p != null) {
                            ok(atlas.status(p, m.place()).status().present(),
                                    v.id() + " is at " + lat + "," + lon + " in " + year);
                        }
                        ok(!seen.contains(v.name()), v.name() + " is named twice at one meal");
                        seen.add(v.name());
                    }
                    for (String seat : m.seats().keySet()) {
                        checkOrder(m.at(seat), "at " + lat + "," + lon + " in " + year);
                    }
                }
            }
        }
        System.out.printf("  %,d meals: %,d with a grain, %,d with every seat filled, %,d with nothing.%n",
                meals, withGrain, withAll, bare);
        System.out.println("  meals per area:");
        for (int i = 0; i < AREAS.length; i++) {
            System.out.printf("     %-4s %,6d%n", AREAS[i], perArea[i]);
        }
        ok(withGrain > 0, "some place, somewhere, has a grain");
        ok(bare < meals / 2, "most of the world has something to eat");

        System.out.println();
        System.out.println("diet: " + checks + " checks, " + failed + " failed");
        if (failed > 0) {
            System.exit(1);
        }
    }

    private static String join(List<Serving> ss) {
        StringBuilder b = new StringBuilder();
        for (Serving s : ss) {
            if (b.length() > 0) {
                b.append(", ");
            }
            b.append(s.name()).append(s.madeHere() ? " (made here)" : " (brought)");
        }
        return b.toString();
    }

    private static String name(double lat, double lon) {
        if (Math.abs(lat - 17.39) < 0.5) return "Hyderabad";
        if (Math.abs(lat - 31.55) < 0.5) return "Lahore";
        if (Math.abs(lat - 41.88) < 0.5) return "Rome";
        if (Math.abs(lat - 19.43) < 0.5) return "Tenochtitlan";
        if (Math.abs(lat + 13.53) < 0.5) return "Cusco";
        if (Math.abs(lat - 6.52) < 0.5) return "Lagos";
        if (Math.abs(lat - 22.32) < 0.5) return "Guangzhou";
        if (Math.abs(lat - 55.75) < 0.5) return "Moscow";
        if (Math.abs(lat + 33.87) < 0.5) return "Sydney";
        if (Math.abs(lat + 17.65) < 0.5) return "Tahiti";
        if (Math.abs(lat - 30.04) < 0.5) return "Cairo";
        return lat + "," + lon;
    }
}
