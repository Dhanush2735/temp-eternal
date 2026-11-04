/* Step 53 part 3 (H1): the five paradox kinds. The claim: ordinary play makes no paradox, and each of the
   five named mistakes has one test that answers either with the paradox or with the words that clear it -
   never silence. The grandfather test reads the frozen card; the causal-loop test reads the technology
   atlas's own origin years. */
import com.eternalengine.timeline.FixedPoints;
import com.eternalengine.timeline.Paradox;
import com.eternalengine.timeline.Paradox.Check;
import com.eternalengine.player.WhoYouAre;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.zip.GZIPInputStream;

public class Step53ParadoxProbe {
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

    static void paradox(Check c, String words, String what) {
        checks++;
        if (!c.paradox()) {
            failed++;
            System.out.println("  FAIL " + what + "  (cleared: " + c.clear() + ")");
            return;
        }
        if (c.found().why().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no reason says \"" + words + "\"; got " + c.found().why());
    }

    static void cleared(Check c, String words, String what) {
        checks++;
        if (c.paradox()) {
            failed++;
            System.out.println("  FAIL " + what + "  (paradox: " + c.found().line() + ")");
            return;
        }
        if (c.clear().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no clearance says \"" + words + "\"; got " + c.clear());
    }

    static Map<String, Integer> origins() throws Exception {
        try (InputStream in = new GZIPInputStream(Step53ParadoxProbe.class.getResourceAsStream(
                "/data/eternalengine/eternal/history/technology_atlas.json.gz"))) {
            JsonObject root = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8))
                    .getAsJsonObject();
            JsonArray techs = root.getAsJsonArray("techs");
            Map<String, Integer> out = new HashMap<>();
            for (int i = 0; i < techs.size(); i++) {
                JsonObject t = techs.get(i).getAsJsonObject();
                out.put(t.get("id").getAsString(), t.get("first").getAsInt());
            }
            return out;
        }
    }

    public static void main(String[] args) throws Exception {
        // ------------------------------------------------ 0. THE ORIGIN YEARS ARE THE PACK'S OWN
        Map<String, Integer> origin = origins();
        eq(origin.size(), 130, "the technology atlas ships 130 techs, each with a first year");
        eq(origin.get("farming"), -9500, "farming's own first year");
        eq(origin.get("paper"), -300, "paper's");
        eq(origin.get("compass"), 1088, "the compass's");
        eq(origin.get("printing_press"), 1440, "and printed books'");

        // ------------------------------------------------ 1. THE FROZEN CARDS (step 52)
        WhoYouAre ashraf = WhoYouAre.make("Ashraf", WhoYouAre.Kind.LOCAL, 1830, 1857, "Delhi",
                List.of(new WhoYouAre.Entry("Fatima", "mother", 1, 1805, 1870),
                        new WhoYouAre.Entry("Daulat", "grandfather", 2, 1778, 1840)),
                List.of()).who();
        WhoYouAre mira = WhoYouAre.make("Mira", WhoYouAre.Kind.TRAVELLER, 2100, 1576, "Cuzco",
                List.of(), List.of()).who();

        // ------------------------------------------------ 2. GRANDFATHER: THE CHAIN, TESTED YEAR BY YEAR
        paradox(Paradox.undoAncestor(ashraf, "Daulat", 1795), "cause of their own arrival",
                "ending Daulat in 1795, before Fatima is born, undoes the line");
        eq(Paradox.undoAncestor(ashraf, "Daulat", 1795).found().kind(), Paradox.Kind.GRANDFATHER,
                "and it is grandfather kind");
        eq(Paradox.undoAncestor(ashraf, "Daulat", 1795).found().weight(), 5, "at the kind's weight");
        ok(Paradox.undoAncestor(ashraf, "Daulat", 1795).found().why().contains("Fatima"),
                "and the reason names the next of the line");
        cleared(Paradox.undoAncestor(ashraf, "Daulat", 1810), "a death and not a paradox",
                "ending Daulat in 1810 is after Fatima was born: a death, not a paradox");
        cleared(Paradox.undoAncestor(ashraf, "Daulat", 1850), "died in 1840",
                "ending him after he died is nobody to end");
        cleared(Paradox.undoAncestor(ashraf, "Daulat", 1770), "not born until 1778",
                "and before he was born there is nobody either");
        paradox(Paradox.undoAncestor(ashraf, "Fatima", 1820), "before Ashraf was born",
                "ending Fatima in 1820, before Ashraf was born, undoes the line");
        cleared(Paradox.undoAncestor(ashraf, "Fatima", 1835), "a death and not a paradox",
                "ending her after 1830 does not");
        cleared(Paradox.undoAncestor(ashraf, "Ninlil", 1857), "is not in Ashraf's line",
                "somebody else's ancestor is nobody of yours");
        cleared(Paradox.undoAncestor(null, "Daulat", 1800), "there is nobody", "no card, no line");
        cleared(Paradox.undoAncestor(ashraf, "  ", 1800), "no name was given", "and no name, no check");

        // ------------------------------------------------ 3. GRANDFATHER: A TRAVELLER'S NAMED CAUSE
        paradox(Paradox.undoArrival(mira, "the machine under the hill", 1576), "own arrival",
                "undoing what brought the traveller undoes their arrival");
        cleared(Paradox.undoArrival(mira, "", 1576), "no cause of arrival was named",
                "with no cause named there is nothing to undo");
        cleared(Paradox.undoArrival(null, "the machine", 1576), "nobody who could have arrived",
                "and nobody, no arrival");

        // ------------------------------------------------ 4. GRANDFATHER: A DESTROYED FIXED POINT
        FixedPoints pts = FixedPoints.empty();
        pts.declare(new FixedPoints.Point("cuzco-1576", 1576, "the fall of Cuzco",
                "the Andes after it are built on it", 4));
        FixedPoints.Forced broke = pts.force("Sam", "cuzco-1576", "the player took Cuzco early");
        Check fromFixed = Paradox.destroyedFixedPoint(broke);
        paradox(fromFixed, "a dated fixed point destroyed is grandfather kind",
                "forcing a fixed point is grandfather kind");
        eq(fromFixed.found().weight(), 4, "and carries the point's own weight, not the kind's default");
        cleared(Paradox.destroyedFixedPoint(pts.force("Ada", "no-such", "x")), "nothing was forced",
                "a refused force destroys nothing");
        cleared(Paradox.destroyedFixedPoint(null), "nothing was forced", "and neither does nothing");

        // ------------------------------------------------ 5. CAUSAL LOOP: THE ATLAS AGAINST THE GIFT
        cleared(Paradox.givenBeforeOrigin("Ninlil", "farming", -2960, origin.get("farming")),
                "is not before that", "farming in 2960 BC is nine thousand years late, which is fine");
        paradox(Paradox.givenBeforeOrigin("Ninlil", "paper", -2960, origin.get("paper")),
                "before its own origin", "paper in 2960 BC comes from nowhere");
        paradox(Paradox.givenBeforeOrigin("Sam", "the compass", 1000, origin.get("compass")),
                "it came from nowhere", "the compass in 1000 AD, a century early");
        cleared(Paradox.givenBeforeOrigin("Sam", "the compass", 1576, origin.get("compass")),
                "is not before that", "the compass in 1576 is fine");
        paradox(Paradox.givenBeforeOrigin("Mira", "printed books", 1000, origin.get("printing_press")),
                "before its own origin", "printed books in 1000 AD");
        paradox(Paradox.givenBeforeOrigin("Mira", "a device with no name in any book", 1576, null),
                "no origin year anywhere in the record", "a thing the record dates nowhere is a loop itself");
        eq(Paradox.givenBeforeOrigin("Mira", "paper", -2960, origin.get("paper")).found().kind(),
                Paradox.Kind.CAUSAL_LOOP, "and it is causal-loop kind");
        cleared(Paradox.givenBeforeOrigin("Mira", "", 1576, 1), "no thing was given", "nothing given, "
                + "no loop");

        // ------------------------------------------------ 6. PREDESTINATION
        paradox(Paradox.attemptCaused("Sam", "tried to stop the mutiny", "the mutiny of 1857", 1857),
                "is what caused it", "an attempt that causes its own event is predestination");
        eq(Paradox.attemptCaused("Sam", "x", "the mutiny", 1857).found().kind(),
                Paradox.Kind.PREDESTINATION, "and it is named so");
        cleared(Paradox.attemptCaused("Sam", "", "the mutiny", 1857), "unnamed",
                "an unnamed attempt is no paradox");
        cleared(Paradox.attemptCaused("Sam", "tried", "", 1857), "unnamed", "and an unnamed event neither");

        // ------------------------------------------------ 7. MEETING YOURSELF
        cleared(Paradox.metSelf("Mira", "Cuzco", 1576, 1), "nobody meets themselves",
                "one stamp is standing somewhere");
        paradox(Paradox.metSelf("Mira", "Cuzco", 1576, 2), "there are two of them to meet",
                "two stamps of one person at one place-year");
        eq(Paradox.metSelf("Mira", "Cuzco", 1576, 2).found().kind(), Paradox.Kind.MEETING_SELF,
                "and it is meeting-yourself kind");

        // ------------------------------------------------ 8. TELLING THE FUTURE
        paradox(Paradox.toldFuture("Sam", "the internet", 1990, 1857), "the record does not know it until 1990",
                "telling Delhi in 1857 about the internet");
        cleared(Paradox.toldFuture("Sam", "the internet", 1990, 2026), "is not before that",
                "telling it in 2026 is just talking");
        cleared(Paradox.toldFuture("Sam", "", 1990, 1857), "nothing was told", "nothing told, no future");
        eq(Paradox.toldFuture("Sam", "the internet", 1990, 1857).found().weight(), 1,
                "and gossip about the future counts the least");

        // ------------------------------------------------ 9. THE PAGE AND THE RULE
        List<Check> pile = new ArrayList<>();
        pile.add(Paradox.undoAncestor(ashraf, "Daulat", 1795));
        pile.add(Paradox.undoAncestor(ashraf, "Daulat", 1810));
        pile.add(Paradox.givenBeforeOrigin("Ninlil", "paper", -2960, origin.get("paper")));
        pile.add(Paradox.metSelf("Mira", "Cuzco", 1576, 2));
        pile.add(Paradox.toldFuture("Sam", "the internet", 1990, 2026));
        for (String line : Paradox.page(pile)) System.out.println("     " + line);
        ok(Paradox.page(pile).get(0).contains("3 paradoxes"), "the page counts the paradoxes");
        ok(Paradox.page(pile).get(0).contains("2 cleared"), "and the clears");
        ok(Paradox.page(pile).get(0).contains("10 stress"), "and the stress they add to the counter");
        ok(Paradox.page(pile).get(1).startsWith("  grandfather"), "grandfather comes first in the page");
        System.out.println("     " + Paradox.ruleLine());
        ok(Paradox.ruleLine().contains("no paradox"), "the rule line says ordinary play is clean");
        ok(Paradox.ruleLine().contains("five specific acts"), "and that the kinds are specific acts");

        System.out.println("\nStep 53 part 3: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
