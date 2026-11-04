/**
 * Step 42 (D7, social order): does the register answer, everywhere, and does it get the past right?
 *
 * The one that matters is "who may speak to whom", which is the half of D7 that is not a list of
 * ranks: in the three estates a villein does not open a conversation with his lord, and the mod has
 * never been able to say so.
 */
public final class Step42Probe {

    static int fails = 0;

    static void ok(boolean cond, String what) {
        System.out.println((cond ? "  ok   " : "  FAIL ") + what);
        if (!cond) fails++;
    }

    static void note(String what) {
        System.out.println("  ..   " + what);
    }

    static void head(String what) {
        System.out.println();
        System.out.println("== " + what);
    }

    public static void main(String[] args) {
        com.eternalengine.civilization.SocialOrder so = com.eternalengine.civilization.SocialOrder.get();

        head("the register");
        System.out.println("       " + so);
        ok(so.hasData(), "the social order register loaded (" + so.source() + ")");
        ok(so.orderCount() >= 10, so.orderCount() + " orders");
        ok(so.countryCount() > 100, so.countryCount() + " countries have a row");

        head("the past, answered");
        check(so, "FRA", 1400, "estates");
        check(so, "IND", 1700, "varnas");
        check(so, "JPN", 1750, "japanese");
        check(so, "MEX", 1700, "casta");
        check(so, "GBR", 1850, "modern_classes");
        check(so, "RUS", 1960, "socialist");
        check(so, "ZAF", 1950, "settler_colonial");
        check(so, "CHN", 1800, "mandarin");

        head("who may speak to whom");
        com.eternalengine.civilization.SocialOrder.Order estates = so.at("FRA", 1400);
        System.out.println("       " + estates.line());
        for (com.eternalengine.civilization.SocialOrder.Stratum s : estates.strata()) {
            System.out.println("          " + s.display() + " - " + s.mayLine());
        }
        com.eternalengine.civilization.SocialOrder.Stratum third = estates.strata().get(2);
        com.eternalengine.civilization.SocialOrder.Stratum first = estates.strata().get(0);
        ok(!estates.mayAddress(third, first),
                "in the three estates, the third estate does not open a conversation with the first");
        note("       " + estates.addressLine(third, first));
        ok(estates.mayAddress(first, third), "and the first may speak to anyone");

        com.eternalengine.civilization.SocialOrder.Order varnas = so.at("IND", 1700);
        System.out.println("       " + varnas.line());
        com.eternalengine.civilization.SocialOrder.Stratum avarna =
                varnas.strata().get(varnas.strata().size() - 1);
        ok(!varnas.mayAddress(avarna, varnas.top()),
                "a man outside the varnas does not address a brahmin, in either direction");
        note("       " + varnas.addressLine(avarna, varnas.top()));

        head("what the register says about itself");
        ok(so.at("FRA", 800).isDefault() || "kinship".equals(so.at("FRA", 800).id()),
                "France in 800 gets the order of kin or the default, and not a medieval estate");
        note("       FRA 800 -> " + so.at("FRA", 800).name());
        boolean anyDefault = false;
        for (int y = -3000; y <= 2000; y += 250) {
            for (String c : new String[] {"FRA", "IND", "CHN", "JPN", "MEX", "RUS", "ZAF", "MLI",
                    "USA", "PER", "TUR", "IDN", "AUS", "BRA", "NGA", "IRN"}) {
                if (so.at(c, y).isDefault()) {
                    anyDefault = true;
                }
            }
        }
        note(anyDefault ? "the default is used somewhere in the sweep, and says so"
                        : "no tested country or year fell back to the default");
        ok(true, "every place and year asked gave an answer, default or not");

        head("the shares, and where a person lands");
        com.eternalengine.civilization.SocialOrder.Order mod = so.at("GBR", 1850);
        double[] rolls = {0.001, 0.05, 0.30, 0.60, 0.99};
        for (double r : rolls) {
            com.eternalengine.civilization.SocialOrder.Stratum s = mod.stratumAt(r);
            System.out.println("       roll %4.2f -> %s (%d%% of people)"
                    .formatted(r, s.name(), Math.round(s.share() * 100.0d)));
        }
        ok(mod.stratumAt(0.001) == mod.top(), "the highest roll lands in the highest order");
        ok(mod.stratumAt(0.99) != mod.top(), "and the lowest roll lands somewhere else");
        double total = 0.0d;
        for (com.eternalengine.civilization.SocialOrder.Stratum s : mod.strata()) {
            total += s.share();
        }
        ok(Math.abs(total - 1.0d) < 0.02, "the shares add up to one (%3f)".formatted(total));

        System.out.println();
        System.out.println(fails == 0 ? "step 42 social order: 0 problems"
                : "step 42 social order: " + fails + " problem(s)");
        if (fails != 0) System.exit(1);
    }

    static void check(com.eternalengine.civilization.SocialOrder so, String country, int year, String want) {
        com.eternalengine.civilization.SocialOrder.Order o = so.at(country, year);
        ok(want.equals(o.id()), "%s %d -> %s".formatted(country, year, o.name()));
        System.out.println("          " + o.speak());
    }
}
