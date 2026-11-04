/* Step 53 part 5: the one surface game code would call. The claim: one call per risky act gives the decision,
   every paradox found, and every row booked - in that order, once, so no caller has to know the three classes
   underneath or the order to ask them in. */
import com.eternalengine.player.Permissions.Actor;
import com.eternalengine.timeline.FixedPoints;
import com.eternalengine.timeline.Paradox;
import com.eternalengine.timeline.ParadoxEngine;
import com.eternalengine.timeline.ParadoxEngine.Verdict;
import com.eternalengine.timeline.Stress;
import com.eternalengine.player.WhoYouAre;

import java.util.List;

public class Step53EngineProbe {
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

    static void refused(Verdict v, String words, String what) {
        checks++;
        if (v.ok()) {
            failed++;
            System.out.println("  FAIL " + what + "  (it was allowed: " + v.line() + ")");
            return;
        }
        if (v.decision().why().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no reason says \"" + words + "\"; got " + v.decision().why());
    }

    public static void main(String[] args) {
        Actor sam = Actor.of("Sam", false);
        Actor ada = Actor.of("Ada", true);

        WhoYouAre ashraf = WhoYouAre.make("Ashraf", WhoYouAre.Kind.LOCAL, 1830, 1857, "Delhi",
                List.of(new WhoYouAre.Entry("Fatima", "mother", 1, 1805, 1870),
                        new WhoYouAre.Entry("Daulat", "grandfather", 2, 1778, 1840)),
                List.of()).who();

        FixedPoints pts = FixedPoints.empty();
        pts.declare(new FixedPoints.Point("mutiny-1857", 1857, "the mutiny of 1857 in Delhi",
                "the century hangs off it", 5));
        Stress stress = Stress.empty();

        // ------------------------------------------------ 1. A FIXED POINT: THE SAFE ANSWER FIRST
        Verdict tried = ParadoxEngine.attemptFixed(pts, stress, "mutiny-1857", "stop it in place");
        refused(tried, "take the change to a timeline branch", "the attempt is refused with the safe way");
        eq(stress.total(), 0, "and nothing is booked for a refused attempt");

        // ------------------------------------------------ 2. FORCING: AN OPERATOR'S HAND OR NOTHING
        Verdict stranger = ParadoxEngine.forceFixed(sam, pts, stress, "mutiny-1857", "I want to", 1857);
        refused(stranger, "rewrites what is recorded", "a player cannot force a fixed point");
        eq(stress.total(), 0, "and nothing is booked for a refused force");
        eq(pts.broken().size(), 0, "and nothing is broken");

        Verdict forced = ParadoxEngine.forceFixed(ada, pts, stress, "mutiny-1857", "the player stopped it",
                1857);
        ok(forced.ok(), "an operator forces it: " + forced.line());
        eq(forced.found().size(), 1, "one paradox found");
        eq(forced.found().get(0).kind(), Paradox.Kind.GRANDFATHER, "grandfather kind");
        eq(forced.booked().size(), 1, "one row booked");
        eq(stress.total(), 5, "and the counter carries the point's own weight");
        ok(pts.broken("mutiny-1857"), "the point is broken");
        refused(ParadoxEngine.forceFixed(ada, pts, stress, "mutiny-1857", "again", 1857), "already broken",
                "not twice");
        refused(ParadoxEngine.forceFixed(ada, pts, stress, "no-such", "why", 1857), "no fixed point",
                "and an unknown point cannot be forced");

        // ------------------------------------------------ 3. EVERY OTHER ACT STANDS WITH ITS PARADOX
        Verdict killed = ParadoxEngine.endAncestor(ashraf, stress, "Sam", "Daulat", 1795);
        ok(killed.ok(), "ending Daulat in 1795 stands: " + killed.line());
        eq(killed.found().get(0).kind(), Paradox.Kind.GRANDFATHER, "and is grandfather kind");
        eq(stress.total(), 10, "the counter carries it");
        Verdict killedLater = ParadoxEngine.endAncestor(ashraf, stress, "Sam", "Daulat", 1810);
        ok(killedLater.ok(), "ending him in 1810 also stands");
        eq(killedLater.found().size(), 0, "but finds no paradox");
        eq(killedLater.booked().size(), 0, "and books nothing");
        ok(killedLater.decision().why().contains("clears"), "and says it clears: "
                + killedLater.decision().why());
        eq(stress.total(), 10, "the counter is unmoved by a clearance");

        Verdict brought = ParadoxEngine.handOver(stress, "Mira", "Ninlil", "paper", -2960, -300);
        ok(brought.ok(), "handing paper to 2960 BC stands");
        eq(brought.found().get(0).kind(), Paradox.Kind.CAUSAL_LOOP, "as a causal loop");
        eq(stress.total(), 12, "on the counter");

        Verdict caused = ParadoxEngine.attemptCaused(stress, "Sam", "Sam", "tried to stop the mutiny",
                "the mutiny of 1857", 1857);
        eq(caused.found().get(0).kind(), Paradox.Kind.PREDESTINATION, "predestination is named");
        eq(stress.total(), 14, "and booked");

        Verdict stamped = ParadoxEngine.stamp(stress, "Mira", "Mira", "Cuzco", 1576, 2);
        eq(stamped.found().get(0).kind(), Paradox.Kind.MEETING_SELF, "meeting yourself is named");
        eq(stress.total(), 17, "and booked");

        Verdict told = ParadoxEngine.tell(stress, "Sam", "Sam", "the internet", 1990, 1857);
        eq(told.found().get(0).kind(), Paradox.Kind.TELLING_FUTURE, "telling the future is named");
        eq(stress.total(), 18, "and booked: five kinds, five rows");
        eq(stress.books().size(), 6, "every booked row is on the books (five kinds plus the forced fixed "
                + "point, which is grandfather kind too)");

        // ------------------------------------------------ 4. REBUILDING BRINGS IT BACK
        Verdict rebuilt = ParadoxEngine.rebuild(ada, pts, stress, "mutiny-1857", "the stones went back");
        ok(rebuilt.ok(), "an operator rebuilds it: " + rebuilt.line());
        ok(!pts.broken("mutiny-1857"), "the point stands again");
        eq(rebuilt.booked().size(), 1, "and a repair row is booked");
        eq(stress.total(), 13, "the counter falls by the point's weight");
        eq(stress.repaired(), 5, "and the repair is on the books");
        refused(ParadoxEngine.rebuild(ada, pts, stress, "mutiny-1857", "again"), "unbroken",
                "a point that stands is not rebuilt");
        refused(ParadoxEngine.rebuild(ada, pts, stress, "no-such", "why"), "no fixed point",
                "and an unknown one neither");

        // ------------------------------------------------ 5. THE PAGE AND THE RULE
        for (String line : ParadoxEngine.page(List.of(killed, brought, caused, stamped, told))) {
            System.out.println("     " + line);
        }
        ok(ParadoxEngine.page(List.of(killed, brought, caused, stamped, told)).get(0).contains("5 paradoxes"),
                "the page counts every verdict's findings");
        System.out.println("     " + ParadoxEngine.ruleLine());
        ok(ParadoxEngine.ruleLine().contains("on the books"), "the rule line says acts stand with their "
                + "paradox booked");
        ok(ParadoxEngine.ruleLine().contains("operator's hand"), "and who forces");
        refused(ParadoxEngine.forceFixed(sam, pts, stress, "no-such", "why", 1857),
                "rewrites what is recorded", "a player's force is refused before the point is even looked at");

        System.out.println("\nStep 53 part 5: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
