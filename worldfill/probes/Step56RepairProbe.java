/* Step 56 part 3 (H8): repair. The claim: rebuilding a fixed point lowers the stress by the point's own
   weight, in ONE call that cannot do half the work. An unbroken point has nothing to rebuild; the
   counter clamps at zero and says how much of the repair was unused. */
import com.eternalengine.timeline.FixedPoints;
import com.eternalengine.timeline.Repairs;
import com.eternalengine.timeline.Repairs.Repaired;
import com.eternalengine.timeline.Stress;

public class Step56RepairProbe {
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

    static void refused(Repaired r, String words, String what) {
        checks++;
        if (r.ok()) {
            failed++;
            System.out.println("  FAIL " + what + "  (the repair happened: " + r.line() + ")");
            return;
        }
        if (r.refused().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no refusal says \"" + words + "\"; got " + r.refused());
    }

    public static void main(String[] args) {
        // ------------------------------------------------ 1. FORCE, THEN REBUILD: THE FALL IN ONE LINE
        FixedPoints pts = FixedPoints.empty();
        pts.declare(new FixedPoints.Point("fall-of-cuzco", 1576, "the fall of Cuzco",
                "the record holds it", 5));
        Stress stress = Stress.empty();
        ok(pts.force("the year 2526", "fall-of-cuzco", "forced for the test").ok(), "a point is forced");
        stress.add(Stress.Source.EVENT, "the year 2526", 2526, "forced fall-of-cuzco", 5,
                "the weight of the point");
        eq(stress.total(), 5, "and the counter holds its weight");

        Repaired fixed = Repairs.repair(pts, stress, "Sam", "fall-of-cuzco", 2600, "the walls rebuilt");
        ok(fixed.ok(), "the repair happens: " + fixed.line());
        eq(fixed.before(), 5, "the counter was at 5");
        eq(fixed.after(), 0, "and is at 0");
        eq(fixed.given(), 5, "the point's own weight was given back");
        ok(fixed.line().contains("lowered the stress from 5 to 0"),
                "in one line: " + fixed.line());
        ok(!pts.broken("fall-of-cuzco"), "and the point stands again");
        eq(stress.repaired(), 5, "the books record the repair");

        // ------------------------------------------------ 2. THE REFUSALS CARRY THROUGH
        // Check order matters: the no-hand refusal must be tested on a BROKEN point, or the unbroken
        // refusal fires first and the words never appear.
        refused(Repairs.repair(pts, stress, "Sam", "no-such-point", 2600, "x"),
                "no fixed point called", "no such point is refused in FixedPoints' own words");
        refused(Repairs.repair(pts, stress, "Sam", "fall-of-cuzco", 2600, "x"),
                "nothing to rebuild", "an unbroken point has nothing to rebuild");
        ok(pts.force("the year 2526", "fall-of-cuzco", "forced again for the test").ok(),
                "the point is broken again");
        refused(Repairs.repair(pts, stress, "", "fall-of-cuzco", 2600, "x"),
                "no hand on it", "and a rebuilding with no hand is nobody's");
        ok(Repairs.repair(pts, stress, "Sam", "fall-of-cuzco", 2600, "and now rebuilt").ok(),
                "then it is rebuilt for real");
        refused(Repairs.repair(null, stress, "Sam", "x", 2600, "x"), "no register",
                "and no register is refused");
        refused(Repairs.repair(pts, null, "Sam", "x", 2600, "x"), "no counter",
                "and no counter is refused");

        // ------------------------------------------------ 3. THE CLAMP IS REPORTED, NOT SWALLOWED
        // A point forced while the counter never took its weight: rebuilding gives nothing back, and
        // the line says the counter was already at zero rather than swallowing the clamp.
        pts.declare(new FixedPoints.Point("the-empty-year", 2100, "a quiet year",
                "a test of the clamp", 2));
        ok(pts.force("the year 2526", "the-empty-year", "forced for the test").ok(),
                "a point is forced and the counter is NOT booked");
        eq(stress.total(), 0, "so the counter stays at zero");
        Repaired clamped = Repairs.repair(pts, stress, "Sam", "the-empty-year", 2600, "rebuilt");
        ok(clamped.ok(), "and rebuilding it succeeds");
        eq(clamped.given(), 0, "with nothing given back");
        eq(clamped.before(), 0, "the counter was already at zero");
        ok(clamped.line().contains("gave nothing back"), "and the line says so: " + clamped.line());

        // A repair bigger than the books clamps at zero and says how much was unused (Stress's words).
        pts.declare(new FixedPoints.Point("the-mutiny-year", 1857, "the mutiny of Delhi",
                "the record holds it", 9));
        ok(pts.force("the year 2526", "the-mutiny-year", "forced for the test").ok(), "a heavy point "
                + "is forced");
        stress.add(Stress.Source.THING, "the year 2526", 2526, "forced the-mutiny-year", 3,
                "only 3 of its 9 booked");
        Repaired big = Repairs.repair(pts, stress, "Maya", "the-mutiny-year", 2700, "rebuilt");
        ok(big.ok(), "the repair happens");
        eq(big.before(), 3, "the counter held 3");
        eq(big.after(), 0, "and falls to zero");
        eq(big.given(), 3, "with 3 given back, not 9");
        ok(big.line().contains("from 3 to 0"), "in the line: " + big.line());
        ok(stress.report().toString().contains("unused") || stress.books().get(stress.books().size() - 1)
                        .why().contains("unused"),
                "and the unused part is on the books: "
                        + stress.books().get(stress.books().size() - 1).why());

        // ------------------------------------------------ 4. THE SCREEN AND THE RULE
        System.out.println("     " + Repairs.screen(java.util.List.of(fixed, clamped, big)));
        ok(Repairs.screen(null).contains("nothing has been rebuilt"), "an empty screen says so");
        System.out.println("     " + Repairs.ruleLine());
        ok(Repairs.ruleLine().contains("own weight"), "the rule keeps the weight");
        ok(Repairs.ruleLine().contains("clamps at zero"), "and the clamp");

        System.out.println("\nStep 56 part 3: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
