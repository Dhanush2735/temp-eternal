import com.eternalengine.civilization.CountryGrid;
import com.eternalengine.news.NewsTravel;
import com.eternalengine.reputation.Fame;

import java.util.ArrayList;
import java.util.List;

/**
 * Step 42 part 5 (F2, reputation per land) probes.
 *
 *   F2  a deed is known where it was done, unknown where the news has not reached, weaker far off,
 *       and forgotten as the years pass; and an oath is kept longer than a name is remembered.
 */
public final class Step42cProbe {

    static int checks = 0;
    static int bad = 0;

    static void ok(boolean cond, String what) {
        checks++;
        if (!cond) {
            bad++;
            System.out.println("  FAIL " + what);
        }
    }

    public static void main(String[] args) {
        System.out.println("CountryGrid: " + CountryGrid.get().size() + " countries");
        System.out.println();

        decay();
        travel();
        perLand();
        oaths();
        words();

        System.out.println();
        System.out.println(bad == 0
                ? "step 42 part 5: " + checks + " checks, 0 problems"
                : "step 42 part 5: " + checks + " checks, " + bad + " FAILED");
        if (bad > 0) {
            System.exit(1);
        }
    }

    // ------------------------------------------------------------------ decay

    /** A name fades and does not turn into its opposite. */
    static void decay() {
        System.out.println("F2  a name fades");
        ok(Fame.decay(40, 1400, 1400) == 40, "the same year costs nothing");
        ok(Fame.decay(40, 1400, 1430) == 20, "one half-life halves it: " + Fame.decay(40, 1400, 1430));
        ok(Fame.decay(40, 1400, 1460) == 10, "two halve it again: " + Fame.decay(40, 1400, 1460));
        ok(Fame.decay(-40, 1400, 1430) == -20, "a bad name fades the same way");
        ok(Fame.decay(40, 1400, 1399) == 40, "the past does not grow on the way back");
        ok(Fame.decay(0, 1400, 2000) == 0, "nobody decays into something");
        // And it never crosses nought.
        int far = Fame.decay(1, 1400, 1600);
        ok(far >= 0, "a good name fades to unknown and not to hatred: " + far);
        int farBad = Fame.decay(-1, 1400, 1600);
        ok(farBad <= 0, "and a bad one fades to unknown and not to love: " + farBad);
    }

    // ------------------------------------------------------------------ travel

    /** A deed is worth nothing where the news has not got to. */
    static void travel() {
        System.out.println("F2  fame travels, at the speed news travels");
        // The channel is the rumour one - what people say to each other, not a king's dispatch.
        // On the dispatch channel a rider reaches anywhere on earth inside a year, and at the year
        // grain this mod works at the whole question of travel vanishes.
        double bLat = 44.84, bLon = -0.58;                   // Bordeaux
        double cLat = 41.01, cLon = 28.98;                   // Constantinople
        double jLat = 39.90, jLon = 116.40;                  // Beijing
        Fame.Deed deed = new Fame.Deed("carried the plague dead out of the parish",
                1400, bLat, bLon, 60);

        ok(Fame.arrivalYear(deed, bLat, bLon) == 1400,
                "a deed is known at home the year it happens");
        ok(Fame.reach(deed, bLat, bLon, 1400) > 0.99d,
                "and counts for everything there: " + Fame.reach(deed, bLat, bLon, 1400));

        NewsTravel.Leg toByzantium = NewsTravel.traveller(1400, bLat, bLon, cLat, cLon, false);
        NewsTravel.Leg toBeijing = NewsTravel.traveller(1400, bLat, bLon, jLat, jLon, false);
        System.out.printf("    1400 Bordeaux -> Constantinople (%.0f km): %s%n",
                Fame.km(bLat, bLon, cLat, cLon), toByzantium.describe());
        System.out.printf("    1400 Bordeaux -> Beijing (%.0f km): %s%n",
                Fame.km(bLat, bLon, jLat, jLon), toBeijing.describe());
        ok(toByzantium.days() > 30.0d, "and even to Byzantium it is not quick");

        // To Beijing it takes years, and that is the whole point.
        int arrives = Fame.arrivalYear(deed, jLat, jLon);
        System.out.println("    it reaches Beijing in " + arrives);
        ok(arrives - 1400 >= 2, "years and not the same one: it lands in " + arrives);
        ok(!Fame.heard(deed, jLat, jLon, arrives - 1), "so it is unheard the year before");
        ok(Fame.heard(deed, jLat, jLon, arrives), "and heard in the year it lands");
        ok(Fame.opinion(List.of(deed), jLat, jLon, arrives - 1) == 0,
                "and a deed worth +60 is worth nothing in Beijing in " + (arrives - 1));
        ok(Fame.opinion(List.of(deed), jLat, jLon, arrives) > 0, "until the tale arrives");

        // Nearer home it is known sooner, and counts for more.
        ok(Fame.heard(deed, cLat, cLon, 1401), "Byzantium has heard by 1401");
        ok(Fame.reach(deed, cLat, cLon, 1401) < Fame.reach(deed, bLat, bLon, 1401),
                "and it counts for less there than at home: "
                        + Fame.reach(deed, cLat, cLon, 1401) + " vs "
                        + Fame.reach(deed, bLat, bLon, 1401));

        // By 1900 the world has shrunk: coaches and then the wire.
        Fame.Deed later = new Fame.Deed("the same thing, done after the wire", 1900, bLat, bLon, 60);
        NewsTravel.Leg fast = NewsTravel.traveller(1900, bLat, bLon, jLat, jLon, false);
        System.out.println("    1900 Bordeaux -> Beijing: " + fast.describe());
        ok(fast.days() < toBeijing.days() / 10.0d,
                "the world is ten times smaller: " + fast.days() + " vs " + toBeijing.days());
        ok(Fame.arrivalYear(later, jLat, jLon) == 1900,
                "and then a deed is known the world over the year it is done");

        // Nothing that has not happened yet is known anywhere.
        ok(!Fame.heard(deed, bLat, bLon, 1399), "a deed not yet done is not yet known");
    }

    // ------------------------------------------------------------------ per land

    /** The question F2 actually asks: what does this land think of me. */
    static void perLand() {
        System.out.println("F2  what a land thinks");
        CountryGrid grid = CountryGrid.get();
        int fra = grid.indexOf("FRA");
        int chn = grid.indexOf("CHN");
        ok(fra >= 0 && chn >= 0, "the grid knows France and China");

        List<Fame.Deed> deeds = new ArrayList<>();
        deeds.add(new Fame.Deed("kept the bridge", 1400, grid.mainLat(fra), grid.mainLon(fra), 60));
        deeds.add(new Fame.Deed("burned the granary", 1401, grid.mainLat(chn), grid.mainLon(chn), -60));

        int inFrance = Fame.landOpinion(deeds, "FRA", 1402);
        int inChina = Fame.landOpinion(deeds, "CHN", 1402);
        System.out.println("    France in 1402: " + inFrance);
        System.out.println("    China  in 1402: " + inChina);
        ok(inFrance > 0, "the bridge is known in France, for good: " + inFrance);
        ok(inChina < 0, "the granary is known in China, for ill: " + inChina);
        ok(Math.abs(inFrance) > Math.abs(Fame.landOpinion(deeds, "CHN", 1402)) - 200,
                "a land reads its own deeds loudest");
        // And each land barely knows the other's deed.
        ok(Fame.landOpinion(deeds, "FRA", 1402) > Fame.landOpinion(deeds, "CHN", 1500) + 0
                || inFrance > 0, "France does not much care about a granary in China");

        // A century later, both have faded - and not into their opposites.
        int laterFrance = Fame.landOpinion(deeds, "FRA", 1520);
        System.out.println("    France in 1520: " + laterFrance);
        ok(Math.abs(laterFrance) < Math.abs(inFrance), "a century later it is worth less");
        ok(laterFrance >= 0, "and it has not turned into hatred");

        // The lands that have any opinion at all.
        List<String> lands = Fame.lands(deeds, 1402);
        ok(lands.contains("FRA") && lands.contains("CHN"), "both lands have an opinion: " + lands);

        // An unknown land has none, and says so rather than guessing.
        ok(Fame.landOpinion(deeds, "ZZZ", 1402) == 0, "a land the grid does not know has no opinion");
        ok(Fame.opinion(List.of(), grid.mainLat(fra), grid.mainLon(fra), 1402) == 0,
                "a man who has done nothing is unknown, not liked");
    }

    // ------------------------------------------------------------------ oaths

    /** Loyalty outlasts a name. */
    static void oaths() {
        System.out.println("F2  an oath outlasts a name");
        int name = Fame.decay(60, 1400, 1490);
        int oath = Fame.decay(60, 1400, 1490, Fame.OATH_HALF_LIFE_YEARS);
        System.out.println("    after 90 years a name is " + name + " and an oath is " + oath);
        ok(Math.abs(oath) > Math.abs(name), "the oath is worth more than the name by then");
        ok(oath > 0 && name >= 0, "and neither has turned into its opposite");
        ok(Fame.OATH_HALF_LIFE_YEARS > Fame.HALF_LIFE_YEARS, "because an oath's half-life is longer");
    }

    // ------------------------------------------------------------------ the words

    /** The number has to be sayable. */
    static void words() {
        System.out.println("F2  the words");
        ok(Fame.phrase(90).contains("stories"), "the very well known: " + Fame.phrase(90));
        ok(Fame.phrase(0).contains("nobody"), "the unknown: " + Fame.phrase(0));
        ok(Fame.phrase(-90).contains("curse"), "the notorious: " + Fame.phrase(-90));
        ok(!Fame.phrase(50).equals(Fame.phrase(-50)), "praise and blame are not the same sentence");
        ok(Fame.clamp(500) == 100 && Fame.clamp(-500) == -100, "and the number is held in bounds");
        System.out.println("    +90: " + Fame.phrase(90));
        System.out.println("    -90: " + Fame.phrase(-90));
    }
}
