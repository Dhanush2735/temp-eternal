import com.eternalengine.civilization.WaysOfLife;
import com.eternalengine.money.ProductAtlas;

import java.util.ArrayList;
import java.util.List;

/**
 * Product atlas, part B: the world product list and the "is it here?" answers, with the mod's real code and data (the
 * ways-of-life survey too), no server. Run by worldfill/probe_atlas.sh. Exit code 1 if a check fails.
 */
public final class AtlasProbe {
    private static int pass;
    private static int fail;

    public static void main(String[] args) {
        ProductAtlas atlas = ProductAtlas.get();
        System.out.println("1. The atlas");
        check("the atlas loads with no problems (" + atlas.summary() + ")", atlas.problems().isEmpty()
                && atlas.products().size() >= 120 && atlas.areas().size() == 17, String.join("; ", atlas.problems()));
        check("the survey has its 146 regions, each in a known area", WaysOfLife.get().regionList().size() == 146
                && WaysOfLife.get().regionList().stream().allMatch(r -> atlas.areaOfWorld(r.world()) != null), "");
        long t0 = System.nanoTime();
        String order = atlas.checkOrder();
        check("the data is in order; nothing is here before its first year (" + ms(t0) + ")", order == null, order);
        t0 = System.nanoTime();
        String inputs = atlas.checkInputs();
        check("every input is made or brought where and when it is used (" + atlas.inputLinks() + " links, " + ms(t0)
                + ")", inputs == null, inputs);
        t0 = System.nanoTime();
        String staples = atlas.checkStaples();
        check("food, cloth, fuel and light in all regions in all check years (" + ProductAtlas.stapleChecks()
                + " places, " + ms(t0) + ")", staples == null, staples);
        t0 = System.nanoTime();
        String self = atlas.selfTest();
        check("the plan's examples: Harappa 2500 BCE, Rome 100, London 1850, Hyderabad 1948 (" + ms(t0) + ")",
                self == null, self);

        System.out.println("\n2. More places");
        is(atlas, "Tenochtitlan", 19.43, -99.13, 1500, ProductAtlas.Status.MADE_HERE, "maize cacao chillies cotton");
        is(atlas, "Tenochtitlan", 19.43, -99.13, 1500, ProductAtlas.Status.NOT_YET, "wheat iron horses coins carts");
        is(atlas, "Mexico City", 19.43, -99.13, 1600, ProductAtlas.Status.MADE_HERE, "wheat horses iron coins books");
        is(atlas, "Sydney", -33.87, 151.21, 1500, ProductAtlas.Status.MADE_HERE, "wild_food fish hides_furs firewood");
        is(atlas, "Sydney", -33.87, 151.21, 1500, ProductAtlas.Status.NOT_YET, "wheat iron bows cattle");
        is(atlas, "Sydney", -33.87, 151.21, 1850, ProductAtlas.Status.MADE_HERE, "wheat sheep_goats wool iron");
        is(atlas, "Sydney", -33.87, 151.21, 1850, ProductAtlas.Status.BROUGHT, "tea");
        is(atlas, "Anyang", 36.1, 114.35, -1200, ProductAtlas.Status.MADE_HERE, "millet bronze silk");
        is(atlas, "Anyang", 36.1, 114.35, -1200, ProductAtlas.Status.NOT_YET, "iron paper coins");
        is(atlas, "Timbuktu", 16.77, -3.0, 1350, ProductAtlas.Status.MADE_HERE, "rice millet iron");
        is(atlas, "Timbuktu", 16.77, -3.0, 1350, ProductAtlas.Status.BROUGHT, "paper");
        is(atlas, "Tahiti", -17.6, -149.5, 1700, ProductAtlas.Status.MADE_HERE, "roots fish bark_cloth");
        is(atlas, "Tahiti", -17.6, -149.5, 1700, ProductAtlas.Status.NOT_YET, "iron firearms paper");
        is(atlas, "Hyderabad", 17.3616, 78.4747, 1700, ProductAtlas.Status.MADE_HERE,
                "rice millet cotton iron coins paper chillies tobacco gunpowder");
        is(atlas, "Hyderabad", 17.3616, 78.4747, 1700, ProductAtlas.Status.BROUGHT, "tea");
        is(atlas, "Hyderabad", 17.3616, 78.4747, 1700, ProductAtlas.Status.NOT_YET, "kerosene railway newspaper");
        is(atlas, "Hyderabad", 17.3616, 78.4747, 1948, ProductAtlas.Status.MADE_HERE,
                "railway electricity telephone newspaper mill_cloth cement");
        is(atlas, "Hyderabad", 17.3616, 78.4747, 1948, ProductAtlas.Status.GONE, "stone_tools palm_leaf armour");
        ProductAtlas.Place bombay = atlas.place(18.94, 72.83, 1948);
        check("Bombay, on the coast, is in a survey region of Southern Asia (" + bombay.region() + ")",
                "SAS".equals(bombay.area()) && !bombay.region().isBlank(), bombay.toString());
        ProductAtlas.Place sea = atlas.place(0.0, -30.0, 1600);
        check("the middle of the Atlantic is in no region and takes a box (" + sea.area() + ")",
                sea.region().isBlank() && sea.reading() == null, sea.toString());
        is(atlas, "Siberia (foragers)", 62.0, 100.0, -3000, ProductAtlas.Status.NOT_YET, "wheat bread");
        is(atlas, "Siberia (foragers)", 62.0, 100.0, -3000, ProductAtlas.Status.MADE_HERE, "wild_food hides_furs");

        System.out.println("\n3. The places, in one line each");
        Object[][] places = {
                {"Harappa", 30.63, 72.86, -2500}, {"Rome", 41.89, 12.49, 100}, {"London", 51.51, -0.13, 1850},
                {"Hyderabad", 17.3616, 78.4747, 1948}, {"Kothapalle", 18.87, 79.43, 1948},
                {"Hyderabad", 17.3616, 78.4747, 1700}, {"Tenochtitlan", 19.43, -99.13, 1500},
                {"Sydney", -33.87, 151.21, 1500}, {"Timbuktu", 16.77, -3.0, 1350}, {"Tahiti", -17.6, -149.5, 1700},
                {"Mid-Atlantic", 30.0, -40.0, 1600}, {"Siberia", 62.0, 100.0, -3000}};
        for (Object[] p : places) {
            ProductAtlas.Place at = atlas.place((Double) p[1], (Double) p[2], (Integer) p[3]);
            System.out.println("   " + p[0] + ": " + atlas.summaryAt(at));
            System.out.println("      " + atlas.staplesAt(at));
        }

        System.out.println("\n4. Merchants");
        List<ProductAtlas.Answer> hyd = atlas.forSale("merchant", 17.3616, 78.4747, 1948);
        List<String> ids = new ArrayList<>();
        for (ProductAtlas.Answer a : hyd) {
            ids.add(a.product().id() + (a.status() == ProductAtlas.Status.BROUGHT ? " (brought)" : ""));
        }
        System.out.println("   Hyderabad 1948 may sell: " + String.join(", ", ids));
        check("in Hyderabad in 1948 a lantern is a kerosene lamp and paper is paper (not palm leaves); no flint",
                ids.contains("kerosene_lamp") && !ids.contains("oil_lamp") && ids.contains("paper")
                        && !ids.contains("palm_leaf") && !ids.contains("stone_tools") && ids.contains("cacao (brought)"),
                String.join(", ", ids));
        List<ProductAtlas.Answer> a1 = ProductAtlas.carried(hyd, 12345L, ProductAtlas.MERCHANT_MAX);
        List<ProductAtlas.Answer> a2 = ProductAtlas.carried(hyd, 12345L, ProductAtlas.MERCHANT_MAX);
        List<ProductAtlas.Answer> b = ProductAtlas.carried(hyd, 99L, ProductAtlas.MERCHANT_MAX);
        check("a merchant carries at most " + ProductAtlas.MERCHANT_MAX + " kinds, always the same; another merchant"
                + " others", a1.size() == ProductAtlas.MERCHANT_MAX && a1.equals(a2) && !a1.equals(b), a1.size() + " / "
                + b.size());
        List<ProductAtlas.Answer> rome = atlas.forSale("merchant", 41.89, 12.49, 100);
        List<String> rids = new ArrayList<>();
        for (ProductAtlas.Answer a : rome) {
            rids.add(a.product().id() + (a.status() == ProductAtlas.Status.BROUGHT ? " (brought)" : ""));
        }
        System.out.println("   Rome 100 may sell: " + String.join(", ", rids));
        check("in Rome in 100 there is no paper, sugar or kerosene lamp for sale, and there are oil lamps",
                !rids.contains("paper") && !rids.contains("sugar") && !rids.contains("kerosene_lamp")
                        && rids.contains("oil_lamp"), String.join(", ", rids));

        System.out.println("\nRESULT: " + pass + " passed, " + fail + " failed");
        System.exit(fail == 0 ? 0 : 1);
    }

    static String ms(long t0) {
        return (System.nanoTime() - t0) / 1_000_000L + " ms";
    }

    static void is(ProductAtlas atlas, String name, double lat, double lon, int year, ProductAtlas.Status want, String ids) {
        ProductAtlas.Place at = atlas.place(lat, lon, year);
        List<String> bad = new ArrayList<>();
        for (String id : ids.split(" ")) {
            ProductAtlas.Product p = atlas.product(id);
            if (p == null) {
                bad.add("no product " + id);
                continue;
            }
            ProductAtlas.Answer a = atlas.status(p, at);
            if (a.status() != want) {
                bad.add(id + " is " + a.status().words + (a.why().isBlank() ? "" : " (" + a.why() + ")"));
            }
        }
        check(name + " " + ProductAtlas.yearText(year) + " [" + at.area() + (at.region().isBlank() ? "" : ", "
                + at.region()) + "]: " + want.words + ": " + ids.replace(' ', ','), bad.isEmpty(), String.join("; ", bad));
    }

    static void check(String what, boolean ok, String detail) {
        if (ok) {
            pass++;
            System.out.println("  PASS " + what);
        } else {
            fail++;
            System.out.println("  FAIL " + what + (detail == null || detail.isBlank() ? "" : "\n       " + detail));
        }
    }
}
