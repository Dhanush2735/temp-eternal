/* Step 47 part 4 (E12, E21): the period wardrobe.
   The bug under test: every garment in SkinPoolDatabase's modern wardrobe arrives in 1873 or later,
   so before that year every person in the world was dressed in nothing. This asserts that history
   now has clothes, and that the dates are the history of tailoring. */
import com.eternalengine.skin.Wardrobe;

import java.util.List;

public class Step47WardrobeProbe {
    static int checks = 0, failed = 0;

    static void ok(boolean c, String what) {
        checks++;
        if (!c) { failed++; System.out.println("  FAIL " + what); }
    }
    static void eq(Object a, Object b, String what) {
        checks++;
        if (a == null ? b != null : !a.equals(b)) {
            failed++; System.out.println("  FAIL " + what + "  expected=" + b + " actual=" + a);
        }
    }

    static final Wardrobe W = Wardrobe.get();

    public static void main(String[] args) {
        System.out.println("== " + W + " ==");
        ok(W.hasData(), "the period wardrobe has data");
        eq(W.problem(), null, "no problem reported");
        ok(W.finding() != null && W.finding().contains("tailor"), "the finding names the tailor");
        System.out.println("  " + W.summary());

        // ------------------------------------------------ 1. THE BUG: HISTORY WAS NAKED
        // Every culture pool must be able to dress somebody BEFORE the modern wardrobe starts.
        String[] cultures = {"deccan", "indic", "maurya", "persianate", "mesopotamian",
                "mediterranean", "rome", "north_african", "african", "east_asian", "americas"};
        for (String c : cultures) {
            ok(W.covers(c, 1400, false) || W.covers(c, 1400, true),
                    "the " + c + " pool can dress somebody in 1400");
        }
        // And at the world's first year, which is the harder test.
        ok(W.covers("mesopotamian", -3000, false), "Mesopotamia is dressed in 3000 BC");
        ok(W.covers("east_asian", -1000, false), "China is dressed in 1000 BC");
        ok(!W.covers("americas", 1400, false) || W.covers("americas", 1400, true),
                "and the Americas are dressed in 1400 for at least one sex");

        // ------------------------------------------------ 2. THE OUTFIT IS NOT EMPTY
        List<String> deccan = W.outfitFor("deccan", 1400, false, "artisan");
        ok(!deccan.isEmpty(), "a Deccan artisan in 1400 wears " + deccan);
        ok(deccan.contains("kurta"), "including the kurta");
        ok(!deccan.contains("crew_tee"), "and NOT a crew-neck T-shirt");
        ok(!deccan.contains("sherwani"), "and not a 19th-century court coat");
        System.out.println("  Deccan 1400 artisan: " + deccan);

        List<String> rome = W.outfitFor("rome", 100, false, "citizen");
        ok(rome.contains("tunic"), "a Roman citizen wears a tunic: " + rome);
        ok(rome.contains("toga"), "and a toga, which is a citizenship and not a garment");
        System.out.println("  Rome AD 100 citizen: " + rome);

        List<String> han = W.outfitFor("east_asian", 800, false, "scholar");
        ok(han.contains("hanfu"), "a Chinese scholar wears a hanfu in AD 800: " + han);
        // The east_asian pool is China AND Japan in one list, so a Heian woman may be drawn in
        // either. That is a limit of the pool and not of this register, and the probe says so.
        List<String> heian = W.outfitFor("east_asian", 900, true, "citizen");
        ok(!heian.isEmpty(), "and an east Asian woman in 900 wears something: " + heian);
        ok(W.forPart("east_asian", 900, true, "dress", "citizen").contains("kimono") ||
           W.forPart("east_asian", 900, true, "dress", "citizen").contains("kimono_f"),
           "with the kimono available from 794: "
                   + W.forPart("east_asian", 900, true, "dress", "citizen"));

        // ------------------------------------------------ 3. NOTHING BEFORE ITS TIME
        // The trap this register exists to prevent.
        List<String> mughal = W.outfitFor("deccan", 1600, false, "advisor");
        ok(!mughal.contains("sherwani"),
                "a Mughal nobleman in 1600 does NOT wear a sherwani: " + mughal);
        // AVAILABLE, not CHOSEN: outfitFor takes the first garment the trade is known for, and a
        // Deccan advisor in 1900 may equally be in the kaftan he has worn all along.
        ok(W.forPart("deccan", 1900, false, "outer", "advisor").contains("sherwani"),
                "and one in 1900 MAY wear a sherwani: "
                        + W.forPart("deccan", 1900, false, "outer", "advisor"));
        ok(!W.forPart("deccan", 1600, false, "outer", "advisor").contains("sherwani"),
                "while in 1600 it is not available at all");
        // A doublet before the 1340s is the same error.
        ok(!W.forPart("mediterranean", 1200, false, "top", "merchant").contains("doublet"),
                "no doublet in 1200: the cut has not been invented");
        ok(W.forPart("mediterranean", 1400, false, "top", "merchant").contains("doublet"),
                "and one in 1400");

        // ------------------------------------------------ 4. THE RECTANGLE AND THE SEAM
        // Everything before the tailor is a rectangle, and the register must say which is which.
        Wardrobe.Garment tunic = find("tunic");
        ok(tunic.arrival() <= -3000, "the tunic is as old as the world: " + tunic.arrival());
        Wardrobe.Garment doublet = find("doublet");
        eq(doublet.arrival(), 1340, "the doublet is 1340");
        ok(doublet.note().contains("curved seam") || doublet.note().contains("cut and sewn"),
                "and it is the first European garment cut to a body");
        // The 1340s date is the finding, so it must be in the pack's own words.
        ok(W.finding().contains("1340"), "the finding gives the decade");

        // ------------------------------------------------ 5. THE ROLE PREFERENCE
        // A trade's own garment comes first, which is what stops a market being a uniform.
        List<String> merc = W.forPart("mediterranean", 1400, false, "outer", "merchant");
        ok(merc.contains("cloak"),
                "and the cloak is Europe's coat before there is tailoring: " + merc);
        List<String> none = W.forPart("mediterranean", 1400, false, "outer", "nobody");
        ok(!merc.isEmpty(), "a merchant has a period outer garment: " + merc);
        ok(merc.size() <= Math.max(1, none.size()), "and the role narrows the choice");

        // ------------------------------------------------ 6. THE PARTS AND THE SEXES
        for (boolean female : new boolean[]{false, true}) {
            List<Wardrobe.Garment> got = W.at("mediterranean", 1400, female);
            ok(!got.isEmpty(), "the Mediterranean dresses female=" + female + " in 1400: "
                    + got.size() + " garments");
        }
        // A woman's garment is not offered to a man, which is the pool's own rule.
        List<String> maleRome = W.outfitFor("rome", 100, false, null);
        List<String> femaleRome = W.outfitFor("rome", 100, true, null);
        ok(maleRome.contains("tunic") && !maleRome.contains("tunic_f"),
                "a Roman man gets the male tunic");
        ok(femaleRome.contains("tunic_f") || femaleRome.contains("chiton_f"),
                "and a Roman woman the female one: " + femaleRome);

        // ------------------------------------------------ 7. THE EDGES
        eq(W.earliestFor("mesopotamian", false), -3000, "the earliest garment is 3000 BC");
        ok(W.outfitFor("african", -2000, false, "farmer").isEmpty(),
                "and before a culture has anything, the answer is empty, not wrong");
        ok(W.outfitFor("african", 1200, false, "farmer").contains("wrapper_top"),
                "and an African farmer in 1200 has the wrapped cloth");
        // The modern wardrobe is untouched: this class starts where the other one stops.
        eq(W.MODERN_WARDROBE_FROM, 1873, "the modern wardrobe starts in 1873");
        for (Wardrobe.Garment g : W.garments()) {
            ok(g.arrival() < W.MODERN_WARDROBE_FROM,
                    g.name() + " is before the modern wardrobe: " + g.arrival());
        }

        System.out.println("== step 47 wardrobe: " + checks + " checks, " + failed + " failed ==");
        if (failed > 0) System.exit(1);
    }

    static Wardrobe.Garment find(String name) {
        for (Wardrobe.Garment g : W.garments()) if (g.name().equals(name)) return g;
        throw new IllegalStateException("no garment " + name);
    }
}
