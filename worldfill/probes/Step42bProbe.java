import com.eternalengine.civilization.CountryGrid;
import com.eternalengine.civilization.LawRegister;
import com.eternalengine.civilization.Reactions;
import com.eternalengine.civilization.RulerRegister;
import com.eternalengine.civilization.SocialOrder;
import com.eternalengine.technology.TechnologyAtlas;

/**
 * Step 42 parts 4 (D13 reactions + D18 friendship and greetings) probes.
 *
 *   D13  what a person here says to the player, about the law, and about a thing out of its time
 *   D18  the greeting: remembered by name, shaped by standing, and shaped by D7's address rule
 */
public final class Step42bProbe {

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
        System.out.println("LawRegister:    " + LawRegister.get());
        System.out.println("TechnologyAtlas: " + TechnologyAtlas.get().summary());
        System.out.println();

        d18Greeting();
        d13ToPlayer();
        d13ToLaw();
        d13OutOfTime();

        System.out.println();
        System.out.println(bad == 0
                ? "step 42 part 4: " + checks + " checks, 0 problems"
                : "step 42 part 4: " + checks + " checks, " + bad + " FAILED");
        if (bad > 0) {
            System.exit(1);
        }
    }

    // ------------------------------------------------------------------ D18

    /** A stranger, someone known, someone loved, someone hated — in a place with an order. */
    static void d18Greeting() {
        System.out.println("D18  the greeting");
        double france = 47.0, lon = 2.0;                   // France
        ok(Reactions.greet(0, "Miriam", france, lon, 1400).contains("not from here"),
                "a stranger in France in 1400 is not recognised");

        String warm = Reactions.greet(70, "Miriam", france, lon, 1400);
        ok(warm.contains("Miriam"), "a friend is greeted by name: " + warm);
        ok(Reactions.greet(-70, "Miriam", france, lon, 1400).contains("Miriam"),
                "even a hated name is spoken");

        // D7's rule: a third-estate man does not open a conversation with a first-estate one.
        SocialOrder.Order estates = SocialOrder.get().at("FRA", 1400);
        SocialOrder.Stratum third = null;
        for (SocialOrder.Stratum s : estates.strata()) {
            if (s.name().contains("third estate")) {
                third = s;
            }
        }
        ok(third != null, "France in 1400 has a third estate");
        if (third != null) {
            String deferent = Reactions.greet(0, "Miriam", third, estates.top(), france, lon, 1400);
            ok(deferent.contains("waits to be spoken to"),
                    "a villein does not open: " + deferent);
            ok(deferent.contains(estates.addressLine(third, estates.top())),
                    "the greeting says why, in the order's own words");
            // The same villein among his own kind needs no leave.
            String own = Reactions.greet(0, "Miriam", third, third, france, lon, 1400);
            ok(!own.contains("waits to be spoken to"),
                    "a villein speaks freely to a villein: " + own);
            // And he is not blocked by a rank nobody has assigned you.
            ok(!Reactions.greet(0, "Miriam", third, null, france, lon, 1400)
                            .contains("waits to be spoken to"),
                    "an unknown rank is not taken for a slight");
        }
        // The top of the same order may open freely.
        if (estates.top() != null) {
            String topLine = Reactions.greet(0, "Miriam", estates.top(), third, france, lon, 1400);
            ok(!topLine.contains("waits to be spoken to"),
                    "the first estate needs no leave: " + topLine);
        }
        System.out.println("    1400 France, a villein to a lord:  "
                + Reactions.greet(0, "Miriam", third, estates.top(), france, lon, 1400));
        System.out.println("    1400 France, a villein to his own: "
                + Reactions.greet(0, "Miriam", third, third, france, lon, 1400));
        System.out.println("    1400 France, a lord to a villein:  "
                + Reactions.greet(0, "Miriam", estates.top(), third, france, lon, 1400));
        System.out.println("    1400 France, a friend:  " + Reactions.greet(70, "Miriam", france, lon, 1400));
    }

    // ------------------------------------------------------------------ D13 (1)

    /** The words change with the standing, and they belong to the place. */
    static void d13ToPlayer() {
        System.out.println("D13  to the player");
        double lat = 47.0, lon = 2.0;
        String hostile = Reactions.toPlayer(-90, lat, lon, 1400);
        String delighted = Reactions.toPlayer(90, lat, lon, 1400);
        ok(hostile.contains("shut their doors"), "hostility shuts doors: " + hostile);
        ok(delighted.contains("come out to meet"), "delight comes out: " + delighted);
        ok(!hostile.equals(delighted), "standing changes the words");

        // The same standing in a different place gives a different sentence.
        String india = Reactions.toPlayer(0, 22.0, 78.0, 1700);
        String france = Reactions.toPlayer(0, lat, lon, 1400);
        ok(!india.equals(france), "place changes the words");
        ok(india.contains(SocialOrder.get().at("IND", 1700).speak()),
                "the reaction speaks in the voice of the order here");
        System.out.println("    1700 India, unknown:  " + india);
        System.out.println("    1400 France, unknown: " + france);

        ok(Reactions.warmth(-90) == Reactions.HOSTILE, "warmth is hostile below -60");
        ok(Reactions.warmth(90) == Reactions.DELIGHTED, "warmth is delighted above 60");
        ok(Reactions.warmth(0) == Reactions.NEUTRAL, "warmth is neutral at 0");
    }

    // ------------------------------------------------------------------ D13 (2)

    /** The law: a place whose law just changed talks about it; a quiet place says so. */
    static void d13ToLaw() {
        System.out.println("D13  to the law");
        ok(LawRegister.get().hasData(), "the law pack loaded");
        ok(LawRegister.get().rowCount() > 300, "the law pack has its rows: " + LawRegister.get().rowCount());

        // Brazil abolished slavery in 1888; ask just after, and just before.
        String qid = LawRegister.get().findPolity("Brazil");
        ok(qid != null, "the register knows a Brazil: " + qid + " ("
                + LawRegister.get().polityName(qid) + ")");
        if (qid != null) {
            LawRegister.Change c = LawRegister.get().latest(qid, 1888);
            ok(c != null && c.text().toLowerCase().contains("slav"),
                    "Brazil's latest change by 1888 is the abolition: " + c);
            ok(LawRegister.get().next(qid, 1880) != null
                            && LawRegister.get().next(qid, 1880).year() > 1880,
                    "in 1880 it is still to come: " + LawRegister.get().next(qid, 1880));
        }

        // Through the map: a point in the Empire of Brazil in 1888, and one far away.
        System.out.println("    1888 Brazil:  " + Reactions.toLaw(-22.9, -43.2, 1888));
        System.out.println("    1880 Brazil:  " + Reactions.toLaw(-22.9, -43.2, 1880));
        System.out.println("    1400 France:  " + Reactions.toLaw(47.0, 2.0, 1400));
        ok(!Reactions.toLaw(-22.9, -43.2, 1888).equals(Reactions.toLaw(-22.9, -43.2, 1880)),
                "the same place speaks differently before and after the change");
    }

    // ------------------------------------------------------------------ D13 (3)

    /** A thing from the future is out of its time before it arrives, and not after. */
    static void d13OutOfTime() {
        System.out.println("D13  things out of their time");
        TechnologyAtlas atlas = TechnologyAtlas.get();
        ok(atlas.size() > 0, "the technology atlas loaded: " + atlas.size() + " technologies");

        String id = null;
        for (TechnologyAtlas.Tech t : atlas.all()) {
            if (t != null && (t.id.contains("telephone") || t.id.contains("radio")
                    || t.id.contains("computer") || t.id.contains("electric"))) {
                id = t.id;
                break;
            }
        }
        ok(id != null, "the atlas has a modern thing to carry");
        System.out.println("    carrying: " + id);

        if (id != null) {
            ok(Reactions.outOfTime(id, 47.0, 2.0, 1400), "a modern thing is out of time in 1400 France");
            ok(!Reactions.outOfTime(id, 47.0, 2.0, 2020), "the same thing is ordinary in 2020 France");

            String before = Reactions.toStrange(id, 47.0, 2.0, 1400, "the box in your hands");
            String after = Reactions.toStrange(id, 47.0, 2.0, 2020, "the box in your hands");
            ok(after.contains("second look"), "in 2020 nobody looks twice: " + after);
            ok(before.length() > 40, "in 1400 they have something to say: " + before);
            System.out.println("    1400 France: " + before);

            // A different order reads the same thing differently.
            String japan = Reactions.toStrange(id, 36.0, 138.0, 1750, "the box in your hands");
            ok(!japan.equals(before), "a samurai and a Breton peasant do not say the same thing");
            System.out.println("    1750 Japan:  " + japan);
        }
        ok(!Reactions.outOfTime("not_a_technology", 47.0, 2.0, 1400), "an unknown id is not out of time");
    }
}
