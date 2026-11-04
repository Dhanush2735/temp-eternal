// Step 44 part D (E5, chains and workplaces): what each product is made from, and who makes it.
//
// The checks are about the shape of the economy, not about whether a file loaded: that a chain
// has no cycle, that nothing is dated before anything it is made from, and that the mod can now
// name a maker where before it named none.
import com.eternalengine.money.ProductAtlas;
import com.eternalengine.money.ProductAtlas.Maker;
import com.eternalengine.money.ProductAtlas.Product;
import com.eternalengine.money.ProductAtlas.Status;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public final class Step44ChainsProbe {

    static int checks = 0;
    static int fails = 0;

    static void ok(boolean cond, String what) {
        checks++;
        if (!cond) {
            fails++;
            System.out.println("  FAIL  " + what);
        }
    }

    public static void main(String[] args) {
        ProductAtlas a = ProductAtlas.get();
        List<Product> all = a.products();
        System.out.println(a.summary());

        // ------------------------------------------------------------------ every product has a maker
        ok(a.problems().isEmpty(), "the atlas loads with no problems: " + a.problems());
        long withWork = all.stream().filter(p -> p.work() != null && !p.work().isBlank()).count();
        long withPlace = all.stream().filter(p -> p.workplaceName() != null && !p.workplaceName().isBlank()).count();
        ok(withWork == all.size(), "every product names the work that makes it (" + withWork + " of " + all.size() + ")");
        ok(withPlace == all.size(), "every product names a workplace (" + withPlace + " of " + all.size() + ")");

        // ------------------------------------------------------------------ the chain graph is sound
        Set<String> ids = new HashSet<>();
        for (Product p : all) {
            ids.add(p.id());
        }
        int dangling = 0;
        for (Product p : all) {
            for (List<String> g : p.inputs()) {
                for (String i : g) {
                    if (!ids.contains(i)) {
                        dangling++;
                        if (dangling < 6) {
                            System.out.println("        " + p.id() + " names a missing input " + i);
                        }
                    }
                }
            }
        }
        ok(dangling == 0, "no product names an input that is not in the atlas (" + dangling + " dangling)");

        int withInputs = (int) all.stream().filter(p -> !p.inputs().isEmpty()).count();
        ok(withInputs > 300, "the chains are filled in: " + withInputs + " products have inputs (was 38)");

        // no cycles
        Set<String> black = new HashSet<>();
        List<String> cycles = new ArrayList<>();
        for (Product p : all) {
            Set<String> grey = new HashSet<>();
            walk(a, p.id(), grey, black, cycles);
        }
        ok(cycles.isEmpty(), "the chain has no cycles: " + cycles);

        // ------------------------------------------------------------------ nothing before its inputs
        // The Python builder already pushes years forward; this checks the Java sees the same thing.
        int early = 0;
        for (Product p : all) {
            for (String area : a.areas()) {
                if (p.madeIn(area) == ProductAtlas.NEVER) {
                    continue;
                }
                for (List<String> g : p.inputs()) {
                    boolean any = false;
                    for (String i : g) {
                        Product in = a.product(i);
                        if (in != null && (in.madeIn(area) <= p.madeIn(area)
                                || in.broughtIn(area) <= p.madeIn(area))) {
                            any = true;
                        }
                    }
                    if (!any) {
                        early++;
                        if (early < 4) {
                            System.out.println("        " + p.id() + " made in " + area + " in "
                                    + p.madeIn(area) + " with none of " + g + " there");
                        }
                    }
                }
            }
        }
        ok(early == 0, "nothing is made before its inputs are there (" + early + " contradictions)");

        // ------------------------------------------------------------------ the chain in words
        Product flour = a.product("flour");
        Product wheat = a.product("wheat");
        ok(flour != null && !flour.inputs().isEmpty(), "flour has inputs");
        if (flour != null) {
            ok(flour.inputs().get(0).contains("wheat"), "flour is made from wheat");
            ok(!a.chain(flour).isBlank(), "the chain reads: " + a.chain(flour));
        }
        ok(wheat != null && wheat.inputs().isEmpty(), "wheat is the raw material, made from nothing");

        Product pottery = a.product("pottery");
        ok(pottery != null && "craft".equals(pottery.work()), "pottery is craft work");
        ok(pottery != null && pottery.workplace().equals("kiln"), "pottery is made in a kiln");
        if (pottery != null) {
            ok(pottery.workWord().equals("craftsman"), "a potter is a craftsman: " + pottery.workWord());
            ok(!pottery.madeBy().isBlank(), "it says who makes it: " + pottery.madeBy());
        }
        ok(wheat != null && "farming".equals(wheat.work()), "wheat is farming");
        ok(wheat != null && wheat.workplace().equals("farm"), "wheat is grown on a farm");
        Product iron = a.product("iron");
        ok(iron != null && iron.workplace().equals("forge"), "iron is made in a forge");

        // ------------------------------------------------------------------ makers, from the jobs register
        // A medieval town has smiths. A band of foragers does not, and the mod must say so rather
        // than inventing one: two in the hundred of twenty-five people is nobody.
        ProductAtlas.Place london = a.place(51.51, -0.13, 1350);
        Maker londonPotter = a.maker(pottery, 51.51, -0.13, 1350, london, 1000);
        ok(londonPotter.share() > 0, "in London in 1350 some share of people are craftsmen ("
                + londonPotter.share() + " in the hundred)");
        ok(!londonPotter.none(), "so there are potters in London in 1350: about " + londonPotter.people());
        ok(!londonPotter.sentence().isBlank(), londonPotter.sentence());

        // twenty-five foragers: craft is 4 in the hundred, which is one person, rounded
        Maker band = a.maker(pottery, 60.0, 100.0, -5000, false, 25);
        ok(band.people() >= 1 && band.people() <= 3, "in a band of twenty-five a few people craft ("
                + band.people() + ")");
        // The jobs hang off the subsistence map, not off a list: this is Siberia five thousand
        // years before anyone farmed it, so it has no farmers however many the era's row gives.
        ProductAtlas.Place sib = a.place(60.0, 100.0, -5000);
        Maker sibFarmer = a.maker(wheat, 60.0, 100.0, -5000, sib, 300);
        Maker sibFarmerRaw = a.maker(wheat, 60.0, 100.0, -5000, false, 300);
        ok(sibFarmer.people() < sibFarmerRaw.people() || sibFarmerRaw.people() == 0,
                "the subsistence map cuts the farmers in Siberia in 5000 BCE from "
                        + sibFarmerRaw.people() + " to " + sibFarmer.people());
        Maker sibHunter = a.maker(a.product("meat"), 60.0, 100.0, -5000, sib, 300);
        ok(sibHunter.people() > 0, "but it still has hunters: " + sibHunter.people());
        Maker nobody = a.maker(pottery, 60.0, 100.0, -5000, false, 10);
        ok(nobody.none(), "in a band of ten there is nobody: " + nobody.sentence());
        ok(nobody.share() > 0, "even though the era does give the band a share of "
                + nobody.share() + " in the hundred");

        // ------------------------------------------------------------------ the whole chain
        if (flour != null) {
            Set<String> deep = a.allInputs(flour);
            ok(deep.contains("wheat"), "walking flour's chain back reaches wheat: " + deep);
        }
        Product paper = a.product("paper");
        if (paper != null) {
            ok(!a.allInputs(paper).isEmpty(), "paper's chain: " + a.allInputs(paper));
        }

        // ------------------------------------------------------------------ status still works
        ProductAtlas.Place hyderabad = a.place(17.3616, 78.4747, 1700);
        if (flour != null) {
            ProductAtlas.Answer ans = a.status(flour, hyderabad);
            ok(ans.status() == Status.MADE_HERE, "flour is made in Hyderabad in 1700: " + ans.status()
                    + " " + ans.why());
        }
        // a place with no wheat must not have flour
        ProductAtlas.Place siberia = a.place(60.0, 100.0, -3000);
        if (flour != null) {
            ProductAtlas.Answer ans = a.status(flour, siberia);
            ok(ans.status() != Status.MADE_HERE, "flour is not made in Siberia in 3000 BCE: "
                    + ans.status() + " " + ans.why());
        }

        // ------------------------------------------------------------------ read this, do not just count it
        System.out.println("\n5. Chains, in words");
        for (String id : new String[]{"bread", "flour", "pottery", "paper", "books", "steel",
                "gunpowder", "cloth", "beer", "cheese", "glass", "soap", "sugar", "identity_cards"}) {
            Product p = a.product(id);
            if (p != null) {
                System.out.println("   " + a.chain(p));
                System.out.println("     -> " + p.madeBy());
            }
        }

        System.out.println("\n6. Who makes it, where");
        int[][] pts = {{51, -0, 1350, 1}, {17, 78, 1700, 1}, {41, 12, -100, 1},
                {30, 31, -2500, 1}, {60, 100, -5000, 0}, {-13, -72, 1200, 0}};
        String[] names = {"London 1350", "Hyderabad 1700", "Rome 100 BCE",
                "Nile -2500", "Siberia -5000", "Andes 1200"};
        for (int k = 0; k < pts.length; k++) {
            double lat = pts[k][0], lon = pts[k][1];
            int yr = pts[k][2];
            boolean urban = pts[k][3] == 1;
            ProductAtlas.Place pl = a.place(lat, lon, yr);
            System.out.println("  " + names[k] + " (" + pl.area() + "):");
            for (String id : new String[]{"pottery", "iron", "wheat", "bread", "paper"}) {
                Product p = a.product(id);
                if (p == null) {
                    continue;
                }
                ProductAtlas.Answer ans = a.status(p, pl);
                Maker m = a.maker(p, lat, lon, yr, pl, 300);
                System.out.println("     " + id + ": " + ans.status()
                        + " | " + (m.none() ? "no one here makes it" : m.people() + " " + m.word() + "(s)"));
            }
        }

        System.out.printf("%nchains probe: %d checks, %d failed%n", checks, fails);
        if (fails > 0) {
            System.exit(1);
        }
    }

    /** Depth-first, marking a cycle if we meet a node still on the stack. */
    static void walk(ProductAtlas a, String id, Set<String> grey, Set<String> black, List<String> cycles) {
        if (black.contains(id) || grey.contains(id)) {
            if (grey.contains(id)) {
                cycles.add(id);
            }
            return;
        }
        grey.add(id);
        Product p = a.product(id);
        if (p != null) {
            for (List<String> g : p.inputs()) {
                for (String m : g) {
                    walk(a, m, grey, black, cycles);
                }
            }
        }
        grey.remove(id);
        black.add(id);
    }
}
