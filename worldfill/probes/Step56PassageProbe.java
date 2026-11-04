/* Step 56 part 2 (H7): travel between universes. The claim: one crossing books BOTH legs - the way back
   is booked before the way out. A return is only along your own ticket, nobody is in two universes at
   once, and nobody stands in a universe before it ruptured. */
import com.eternalengine.terrabridge.LandSpec;
import com.eternalengine.timeline.Passage;
import com.eternalengine.timeline.Passage.Way;
import com.eternalengine.timeline.Ruptures;

public class Step56PassageProbe {
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

    static void refused(Passage.Travelled t, String words, String what) {
        checks++;
        if (t.ok()) {
            failed++;
            System.out.println("  FAIL " + what + "  (the crossing happened)");
            return;
        }
        if (t.refused().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no refusal says \"" + words + "\"; got " + t.refused());
    }

    static void refused(Passage.Returned r, String words, String what) {
        checks++;
        if (r.ok()) {
            failed++;
            System.out.println("  FAIL " + what + "  (the return happened)");
            return;
        }
        if (r.refused().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no refusal says \"" + words + "\"; got " + r.refused());
    }

    public static void main(String[] args) {
        Ruptures worlds = Ruptures.empty();
        worlds.declare("earth", null, LandSpec.earth(), -3000, "the land as Terra++ makes it");
        worlds.declare("u-cuzco-1576", "earth", LandSpec.earth(), 1576, "the fall of Cuzco");
        worlds.declare("u-deep-2100", "earth", LandSpec.earth(), 2100, "the sea is gone");
        Passage book = Passage.over(worlds);

        // ------------------------------------------------ 1. A CROSSING BOOKS BOTH LEGS AT ONCE
        Passage.Travelled out = book.travel("Sam", "earth", "u-cuzco-1576", 1600, Way.PORTAL,
                "the year of the fall");
        ok(out.ok(), "the crossing happens: " + (out.ok() ? out.ticket().line() : out.refused()));
        eq(book.openTicket("Sam").to(), "u-cuzco-1576", "Sam is away");
        eq(book.whereIs("Sam"), "u-cuzco-1576", "and knows where he stands");
        ok(out.ticket().open(), "and the ticket is open");
        ok(out.ticket().line().contains("with the way home booked"), "in words: " + out.ticket().line());
        eq(book.outstanding().size(), 1, "outstanding lists exactly who is away");
        ok(book.outstanding().get(0).traveller().equals("Sam"), "with the way home each holds");

        // ------------------------------------------------ 2. THE WAY BACK, ONLY YOUR OWN
        Passage.Returned home = book.back("Sam", out.ticket().id());
        ok(home.ok(), "the return happens: " + (home.ok() ? home.ticket().line() : home.refused()));
        eq(book.whereIs("Sam"), "earth", "Sam is home");
        eq(book.openTicket("Sam"), null, "and holds no open ticket");
        refused(book.back("Sam", out.ticket().id()), "already home", "a second return is refused");
        refused(book.back("Maya", out.ticket().id()), "only along your own ticket",
                "and nobody comes home on someone else's ticket");

        // ------------------------------------------------ 3. THE FOUR REFUSALS
        refused(book.travel("", "earth", "u-cuzco-1576", 1600, Way.PORTAL, "x"), "nobody on it",
                "a crossing with no traveller is refused");
        refused(book.travel("Sam", "earth", "u-nowhere", 1600, Way.PORTAL, "x"), "no universe called",
                "a crossing to a universe that does not exist is refused");
        refused(book.travel("Sam", "u-nowhere", "earth", 1600, Way.PORTAL, "x"), "no universe called",
                "and from one that does not exist too");
        refused(book.travel("Sam", "earth", "u-deep-2100", 2000, Way.PORTAL, "x"),
                "before it ruptured", "nobody stands in a universe before it was born");
        refused(book.travel("Sam", "earth", "earth", 1600, Way.PORTAL, "x"), "already in",
                "and a crossing that goes nowhere is refused");
        refused(book.travel("Sam", "earth", "u-cuzco-1576", 1600, null, "x"), "a portal or a rift",
                "and the way must be named");

        // ------------------------------------------------ 4. NOBODY IS IN TWO UNIVERSES AT ONCE
        Passage.Travelled away = book.travel("Sam", "earth", "u-cuzco-1576", 1600, Way.PORTAL, "the fall");
        ok(away.ok(), "Sam crosses again");
        refused(book.travel("Sam", "u-cuzco-1576", "u-deep-2100", 2200, Way.RIFT, "x"),
                "nobody is in two universes at once", "and cannot cross again while away");
        ok(book.travel("Maya", "earth", "u-deep-2100", 2200, Way.PORTAL, "the high ground").ok(),
                "while Maya's own crossing to 2100 is lawful in 2200");

        // ------------------------------------------------ 5. A RIFT'S TICKET SAYS IT IS UNSTABLE
        Passage.Travelled rift = book.travel("Kai", "earth", "u-deep-2100", 2200, Way.RIFT,
                "through the shimmer");
        ok(rift.ok(), "a rift crossing happens too: " + rift.ticket().line());
        ok(Way.RIFT.ticketNote().contains("unstable"), "and a rift's ticket says it is unstable");
        ok(!Way.PORTAL.ticketNote().contains("unstable"), "while a portal's says the way home is clear");
        eq(book.outstanding().size(), 3, "three travellers are away, all with tickets home");
        for (String line : book.lines()) System.out.println("     " + line);
        Passage.Returned riftHome = book.back("Kai", rift.ticket().id());
        ok(riftHome.ok(), "and a rift's way home works too");
        eq(book.whereIs("Kai"), "earth", "Kai is home");

        // ------------------------------------------------ 6. THE RULE
        System.out.println("     " + Passage.ruleLine());
        ok(Passage.ruleLine().contains("both legs"), "the rule keeps both legs");
        ok(Passage.ruleLine().contains("own ticket"), "and your own ticket");
        ok(Passage.ruleLine().contains("before it ruptured"), "and the universe's birth year");

        System.out.println("\nStep 56 part 2: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
