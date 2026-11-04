/* Step 53 part 2 (G9): fixed points. The claim: a fixed point resists by REFUSING the in-place change and
   naming the safe way out (a branch), and only forcing breaks it - on the record, with a hand and a reason,
   costing stress that rebuilding can give back. No dice, no hidden roll, anywhere. */
import com.eternalengine.player.Permissions.Decision;
import com.eternalengine.timeline.FixedPoints;
import com.eternalengine.timeline.FixedPoints.Point;

import java.util.List;

public class Step53FixedProbe {
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

    static void refused(Decision d, String words, String what) {
        checks++;
        if (d.allowed()) {
            failed++;
            System.out.println("  FAIL " + what + "  (it was allowed)");
            return;
        }
        if (d.why().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no reason says \"" + words + "\"; got " + d.why());
    }

    static void refused(FixedPoints.Forced f, String words, String what) {
        checks++;
        if (f.ok()) {
            failed++;
            System.out.println("  FAIL " + what + "  (it was forced)");
            return;
        }
        if (f.refused().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no reason says \"" + words + "\"; got " + f.refused());
    }

    public static void main(String[] args) {
        // ------------------------------------------------ 1. THE REGISTER, ACROSS ERAS AND PLACES
        FixedPoints pts = FixedPoints.empty();
        ok(pts.declare(new Point("mutiny-1857", 1857, "the mutiny of 1857 in Delhi",
                "the century hangs off it", 5)).allowed(), "a fixed point in 1857");
        ok(pts.declare(new Point("cuzco-1576", 1576, "the fall of Cuzco",
                "the Andes after it are built on it", 4)).allowed(), "one in 1576");
        ok(pts.declare(new Point("ur-2960", -2960, "the first city walls of Ur",
                "Sumer is what came of it", 3)).allowed(), "one in 2960 BC");
        ok(pts.declare(new Point("farming-first", -9500, "farming's first year",
                "every later year of the record grows out of it", 6)).allowed(),
                "and one in 9500 BC, from the technology atlas's own first year");
        ok(pts.declare(new Point("independence-1947", 1947, "the independence of India",
                "the map after it is this event", 5)).allowed(), "and one in 1947");
        refused(pts.declare(new Point("mutiny-1857", 1857, "another thing", "", 1)),
                "one name", "two events with one name are refused");
        checks++;
        try {
            pts.declare(new Point("cheap", 1900, "a point that costs nothing", "", 0));
            failed++;
            System.out.println("  FAIL a fixed point that resists nothing was declared");
        } catch (IllegalArgumentException e) {
            ok(e.getMessage().contains("not fixed"), "and a point that costs nothing to force is refused: "
                    + e.getMessage());
            checks--;
        }
        checks++;
        try {
            new Point("", 1900, "nameless", "", 1);
            failed++;
            System.out.println("  FAIL a nameless point was made");
        } catch (IllegalArgumentException e) {
            ok(e.getMessage().contains("needs a name"), "a nameless point cannot exist");
            checks--;
        }

        // ------------------------------------------------ 2. IT RESISTS: REFUSED, AND THE WAY OUT NAMED
        Decision tried = pts.attempt("mutiny-1857", "stop the mutiny in place");
        refused(tried, "resists", "the attempt is refused");
        refused(tried, "take the change to a timeline branch", "and the safe way out comes first");
        refused(tried, "force it and carry the paradox", "with the dangerous way named after");
        refused(pts.attempt("no-such", "anything"), "no fixed point called no-such", "an unknown point "
                + "is no point");
        eq(pts.broken().size(), 0, "and nothing is broken by an attempt");

        // ------------------------------------------------ 3. FORCING BREAKS IT, ON THE RECORD
        refused(pts.force("", "mutiny-1857", "I want to"), "no hand on it", "a forcing with no hand is "
                + "refused");
        refused(pts.force("Sam", "mutiny-1857", ""), "must say why", "and one with no reason");
        refused(pts.force("Sam", "no-such", "because"), "no fixed point called no-such", "an unknown point "
                + "cannot be forced");
        FixedPoints.Forced forced = pts.force("Sam", "mutiny-1857", "the player stopped the mutiny");
        ok(forced.ok(), "an operator's hand forces it: " + (forced.ok() ? "" : forced.refused()));
        eq(forced.point().weight(), 5, "and the cost is the point's own weight");
        ok(pts.broken("mutiny-1857"), "the point is broken");
        eq(pts.brokenBy("mutiny-1857"), "Sam", "and the record says whose hand did it");
        refused(pts.force("Ada", "mutiny-1857", "again"), "already broken", "not twice");
        refused(pts.attempt("mutiny-1857", "anything"), "already forced by Sam",
                "and a broken point resists nothing: it is already gone");
        eq(pts.weightOf("mutiny-1857"), 5, "and its weight is still on the books");

        // ------------------------------------------------ 4. REBUILDING GIVES IT BACK (H8's arithmetic)
        refused(pts.restore("Ada", "cuzco-1576", ""), "nothing to rebuild", "a point that stands is not "
                + "rebuilt");
        refused(pts.restore("", "mutiny-1857", ""), "no hand on it", "and a rebuilding needs a hand too");
        Decision rebuilt = pts.restore("Ada", "mutiny-1857", "the stones went back");
        ok(rebuilt.allowed(), "a rebuild is allowed: " + rebuilt.why());
        ok(rebuilt.why().contains("5 of stress can be given back"), "and says what it gives back: "
                + rebuilt.why());
        ok(!pts.broken("mutiny-1857"), "the point stands again");
        refused(pts.restore("Ada", "mutiny-1857", "again"), "unbroken", "not twice");

        // ------------------------------------------------ 5. THE PAGE AND THE LOG
        pts.force("Sam", "cuzco-1576", "the player took Cuzco early");
        for (String line : pts.lines()) System.out.println("     " + line);
        ok(pts.lines().get(0).contains("5 fixed points"), "the page counts what it holds");
        ok(pts.lines().get(0).contains("1 broken"), "and what is broken");
        ok(String.join("\n", pts.lines()).contains("BROKEN cuzco-1576"), "and names it in capitals");
        ok(String.join("\n", pts.lines()).contains("forced by Sam"), "with the hand that broke it");
        eq(pts.all().size(), 5, "every point is on the page");
        eq(pts.broken().size(), 1, "exactly one stands broken");
        ok(pts.log().get(0).startsWith("declared"), "the log keeps declaring");
        ok(pts.log().toString().contains("FORCED cuzco-1576 by Sam"), "and forcing, in capitals");
        ok(pts.log().toString().contains("rebuilt mutiny-1857 by Ada"), "and rebuilding");

        System.out.println("     " + FixedPoints.ruleLine());
        ok(FixedPoints.ruleLine().contains("to a branch"), "the rule line names the safe way");
        ok(FixedPoints.ruleLine().contains("stress falls"), "and the way stress falls");

        System.out.println("\nStep 53 part 2: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
