package com.eternalengine.calprobe;

import com.eternalengine.knowledge.Beliefs;
import com.eternalengine.knowledge.Beliefs.Belief;
import com.eternalengine.knowledge.Beliefs.Who;

import java.util.ArrayList;
import java.util.List;

/**
 * Step 37 (C29): run the beliefs register against the record. Every check here can fail — and the
 * ones worth having are the negative ones: a belief must not reach a place it never reached, and
 * must stop being held when it stopped being held.
 */
public final class BeliefsRun {

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

    private static final double HYD_LA = 17.39d, HYD_LO = 78.49d;
    private static final double PARIS_LA = 48.86d, PARIS_LO = 2.35d;
    private static final double LONDON_LA = 51.5d, LONDON_LO = -0.13d;
    private static final double BAGHDAD_LA = 33.3d, BAGHDAD_LO = 44.4d;
    private static final double CAIRO_LA = 30.0d, CAIRO_LO = 31.2d;
    private static final double CHANGAN_LA = 34.3d, CHANGAN_LO = 108.9d;
    private static final double DELHI_LA = 28.61d, DELHI_LO = 77.21d;
    private static final double CUSCO_LA = -13.5d, CUSCO_LO = -72.0d;
    private static final double TOMBOUCTOU_LA = 16.8d, TOMBOUCTOU_LO = -3.0d;

    public static void main(String[] args) {
        Beliefs b = Beliefs.get();
        java.lang.System.out.println("source: " + b.source());
        java.lang.System.out.println("beliefs: " + b.count());
        java.lang.System.out.println();

        // --------------------------------------------------------------- the pack itself
        ok(b.count() >= 29, "the pack should carry its table, got " + b.count());
        int unsourced = 0;
        for (Belief f : b.all()) {
            if (f.source() == null || f.source().isEmpty()) {
                unsourced++;
            }
        }
        eq(0, unsourced, "beliefs with no source article");

        // --------------------------------------------------------------- the inclusions
        ok(b.held("three_doshas", HYD_LA, HYD_LO, 1348).isPresent(),
                "Hyderabad in 1348 has the three doshas");
        ok(b.held("miasma", HYD_LA, HYD_LO, 1348).isPresent(), "and bad air");
        ok(b.held("miasma", PARIS_LA, PARIS_LO, 1348).isPresent(), "Paris in 1348 has bad air");
        ok(b.held("four_humours", PARIS_LA, PARIS_LO, 1348).isPresent(), "and the four humours");
        ok(b.held("geocentrism", PARIS_LA, PARIS_LO, 1348).isPresent(), "and a still earth");
        ok(b.held("four_humours", BAGHDAD_LA, BAGHDAD_LO, 900).isPresent(),
                "Baghdad in 900 has the four humours");
        ok(b.held("alchemy", BAGHDAD_LA, BAGHDAD_LO, 900).isPresent(), "and alchemy");
        ok(b.held("jinn", CAIRO_LA, CAIRO_LO, 1900).isPresent(), "Cairo in 1900 has the jinn");
        ok(b.held("germ_theory", CAIRO_LA, CAIRO_LO, 1900).isPresent(), "and also germ theory");
        ok(b.held("mandate_of_heaven", CHANGAN_LA, CHANGAN_LO, 800).isPresent(),
                "Chang'an in 800 has the mandate of heaven");
        ok(b.held("young_earth", LONDON_LA, LONDON_LO, 1650).isPresent(),
                "London in 1650 has Ussher's chronology");
        ok(b.held("witchcraft_europe", LONDON_LA, LONDON_LO, 1700).isPresent(),
                "London in 1700 has the witch trials");
        ok(b.held("aether", LONDON_LA, LONDON_LO, 1900).isPresent(),
                "London in 1900 has the aether");
        ok(b.held("plate_tectonics", LONDON_LA, LONDON_LO, 1970).isPresent(),
                "London in 1970 has plate tectonics");
        ok(b.held("ulcer_stress", LONDON_LA, LONDON_LO, 1970).isPresent(),
                "and still believes ulcers come from worry");
        ok(b.held("rotating_earth_india", DELHI_LA, DELHI_LO, 500).isPresent(),
                "Delhi in 500 has Aryabhata's turning earth, against its own consensus");

        // --------------------------------------------------------------- the exclusions
        ok(b.held("five_elements_india", CHANGAN_LA, CHANGAN_LO, 800).isEmpty(),
                "the five elements of India must not reach China");
        ok(b.held("phlogiston", LONDON_LA, LONDON_LO, 1900).isEmpty(),
                "phlogiston must be over by 1900");
        ok(b.held("witchcraft_europe", LONDON_LA, LONDON_LO, 1900).isEmpty(),
                "the witch trials must be over by 1900");
        ok(b.held("germ_theory", PARIS_LA, PARIS_LO, 1348).isEmpty(),
                "germ theory must not be in Paris in 1348");
        ok(b.held("miasma", LONDON_LA, LONDON_LO, 1970).isEmpty(),
                "bad air must be over in London by 1970");
        ok(b.held("geocentrism", LONDON_LA, LONDON_LO, 1750).isEmpty(),
                "a still earth must be over in London by 1750");
        ok(b.held("mandate_of_heaven", PARIS_LA, PARIS_LO, 800).isEmpty(),
                "the mandate of heaven must not reach Paris");
        ok(b.held("young_earth", LONDON_LA, LONDON_LO, 1900).isEmpty(),
                "Ussher's chronology must be over by 1900");

        // --------------------------------------------------------------- who held it
        eq(Who.EVERYONE, b.held("miasma", PARIS_LA, PARIS_LO, 1348).get().who(),
                "bad air was everybody's belief");
        eq(Who.EDUCATED, b.held("four_humours", PARIS_LA, PARIS_LO, 1348).get().who(),
                "the humours were the physicians'");
        eq(Who.SCHOLARS, b.held("rotating_earth_india", DELHI_LA, DELHI_LO, 500).get().who(),
                "Aryabhata's earth was a minority view");
        ok(b.at(PARIS_LA, PARIS_LO, 1348, Who.SCHOLARS).isEmpty(),
                "and Paris in 1348 has no such minority on record");

        // --------------------------------------------------------------- everywhere, every era
        double[][] spots = {{PARIS_LA, PARIS_LO}, {BAGHDAD_LA, BAGHDAD_LO}, {DELHI_LA, DELHI_LO},
                {CHANGAN_LA, CHANGAN_LO}, {TOMBOUCTOU_LA, TOMBOUCTOU_LO}, {CUSCO_LA, CUSCO_LO},
                {CAIRO_LA, CAIRO_LO}, {35.0d, 135.8d}};
        String[] names = {"Paris", "Baghdad", "Delhi", "Chang'an", "Timbuktu", "Cusco", "Cairo",
                "Kyoto"};
        int[] years = {-500, 1, 500, 1000, 1500, 1700, 1900, 2000};
        for (int i = 0; i < spots.length; i++) {
            for (int year : years) {
                ok(!b.at(spots[i][0], spots[i][1], year).isEmpty(),
                        names[i] + " should have something believed in " + year);
            }
        }

        // --------------------------------------------------------------- what is said
        String farmer = b.says("farmer", PARIS_LA, PARIS_LO, 1348, 0L);
        String clerk = b.says("scribe", PARIS_LA, PARIS_LO, 1348, 0L);
        ok(!farmer.isEmpty(), "a farmer in Paris in 1348 has something to say");
        ok(!clerk.isEmpty(), "and so does the court clerk");
        ok(!farmer.equals(clerk), "and they do not say the same thing: " + farmer + " / " + clerk);
        ok(farmer.startsWith("Everyone here says") || farmer.startsWith("The learned")
                        || farmer.startsWith("A few"),
                "a farmer speaks for the street: " + farmer);
        ok(clerk.startsWith("It is held that"), "the clerk quotes the consensus: " + clerk);
        // a European argument is not put in a mouth that never made it
        ok(b.held("fixed_continents", -13.5d, -71.9d, 1200).isEmpty(),
                "Cusco: no continental question");
        ok(b.held("alchemy", 19.4d, -99.1d, 1200).isEmpty(),
                "Tenochtitlan: no transmutation of metals");
        // and East Asia has its own five phases, not the Greek four nor the Indian five
        ok(b.held("wuxing", 34.3d, 108.9d, 800).isPresent(), "Chang'an: wu xing");
        ok(b.held("four_elements", 34.3d, 108.9d, 800).isEmpty(),
                "Chang'an: not the Greek four");

        // a belief recorded for the whole world reaches mid-ocean: the register says where a
        // belief was held, not where people were, and callers ask about settlements
        ok(!b.says("farmer", 0.0d, -140.0d, 1900, 0L).isEmpty(),
                "a world belief reaches the open Pacific, where nobody held it");

        String card = b.card(PARIS_LA, PARIS_LO, 1348);
        ok(!card.isEmpty(), "the card for Paris in 1348 says something");
        ok(card.contains("You would say"), "and puts the present beside it");

        // --------------------------------------------------------------- the read-out
        java.lang.System.out.println("what people believed:");
        for (String[] place : new String[][]{{"Paris", "1348"}, {"Baghdad", "900"},
                {"Delhi", "1500"}, {"Chang'an", "800"}, {"Timbuktu", "1400"}, {"Cusco", "1400"},
                {"London", "1650"}, {"London", "1900"}, {"Hyderabad", "1348"},
                {"Hyderabad", "1948"}}) {
            int year = Integer.parseInt(place[1]);
            double[] q = null;
            String n = place[0];
            if (n.equals("Paris")) { q = new double[]{PARIS_LA, PARIS_LO}; }
            if (n.equals("Baghdad")) { q = new double[]{BAGHDAD_LA, BAGHDAD_LO}; }
            if (n.equals("Delhi")) { q = new double[]{DELHI_LA, DELHI_LO}; }
            if (n.equals("Chang'an")) { q = new double[]{CHANGAN_LA, CHANGAN_LO}; }
            if (n.equals("Timbuktu")) { q = new double[]{TOMBOUCTOU_LA, TOMBOUCTOU_LO}; }
            if (n.equals("Cusco")) { q = new double[]{CUSCO_LA, CUSCO_LO}; }
            if (n.equals("London")) { q = new double[]{LONDON_LA, LONDON_LO}; }
            if (n.equals("Hyderabad")) { q = new double[]{HYD_LA, HYD_LO}; }
            java.lang.System.out.println("  " + n + ", " + year + ":");
            for (Belief f : b.at(q[0], q[1], year)) {
                java.lang.System.out.println("      [" + f.who().name().toLowerCase()
                        + "] " + f.said() + "   " + f.youWouldSay());
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
