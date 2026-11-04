/* Step 53 part 4 (H2): one paradox counter, shared with Terra++. The claim: one number, named parts, every
   addition explained, repair brings it down, and with no Terra++ the building part is reported as NOT COUNTED
   rather than as zero - a timeline with no bridge must never look like a timeline with no broken buildings. */
import com.eternalengine.timeline.Paradox;
import com.eternalengine.timeline.Stress;
import com.eternalengine.timeline.Stress.Bridge;
import com.eternalengine.timeline.Stress.Source;

import java.util.Map;

public class Step53StressProbe {
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

    static void refused(Stress.Changed c, String words, String what) {
        checks++;
        if (c.ok()) {
            failed++;
            System.out.println("  FAIL " + what + "  (it was booked)");
            return;
        }
        if (c.refused().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no reason says \"" + words + "\"; got " + c.refused());
    }

    public static void main(String[] args) {
        Stress stress = Stress.empty();

        // ------------------------------------------------ 1. ADDITIONS, EXPLAINED
        ok(stress.add(Source.EVENT, "Sam", 1857, "the mutiny of 1857", 3, "the event was touched").ok(),
                "an event adds to the counter");
        ok(stress.add(Source.PERSON, "Sam", 1857, "Fatima", 5, "her life was ended early").ok(),
                "a person adds");
        ok(stress.add(Source.THING, "Mira", 1576, "the compass", 2, "given before its origin").ok(),
                "and a thing adds");
        eq(stress.total(), 10, "the counter is one number");
        eq(stress.ownTotal(), 10, "of this mod's own so far");
        refused(stress.add(Source.EVENT, "Sam", 1857, "x", 0, "why"), "adds nothing",
                "adding nothing is refused");
        refused(stress.add(Source.EVENT, "Sam", 1857, "x", -3, "why"), "adds nothing",
                "and so is adding less than nothing");
        refused(stress.add(Source.EVENT, "Sam", 1857, "x", 3, ""), "must say why",
                "an unexplained rise is refused");
        refused(stress.add(null, "Sam", 1857, "x", 3, "why"), "no source",
                "and one with no source");
        eq(stress.total(), 10, "and every refusal leaves the counter alone");

        // ------------------------------------------------ 2. PARADOX ENTRIES NAME THEIR SOURCE
        ok(stress.add(Paradox.givenBeforeOrigin("Ninlil", "paper", -2960, -300).found()).ok(),
                "a paradox goes on the books");
        Map<Source, Integer> parts = stress.bySource();
        eq(parts.get(Source.THING), 4, "a causal loop is a thing's problem: 2 booked + 2 more");
        eq(parts.get(Source.PERSON), 5, "a person's problem stays a person's");
        eq(parts.get(Source.EVENT), 3, "and an event's an event's");
        eq(parts.get(Source.BUILDING), 0, "with no buildings so far");
        eq(stress.total(), 12, "one number, whatever its parts");

        // ------------------------------------------------ 3. THE SEAM, AND THE ABSENT BRIDGE
        eq(stress.buildingStress(), 0, "with no Terra++, buildings add nothing");
        ok(stress.bridgeLine().contains("Terra++ is not connected"),
                "and the report says the bridge is missing, not that buildings are fine: "
                        + stress.bridgeLine());
        Bridge fake = new Bridge() {
            @Override
            public int buildingStress() {
                return 7;
            }

            @Override
            public String describe() {
                return "a recorder, standing in for Terra++";
            }
        };
        stress.connect(fake);
        eq(stress.buildingStress(), 7, "a connected bridge adds its broken buildings");
        eq(stress.total(), 19, "and the one number includes them");
        eq(stress.ownTotal(), 12, "while the mod's own total still says what it said");
        ok(stress.report().toString().contains("7 from buildings"), "and the report splits them out");
        stress.connect(Stress.absent());
        eq(stress.total(), 12, "and disconnecting takes them back out");

        // ------------------------------------------------ 4. REPAIR BRINGS IT DOWN, AND SAYS SO
        refused(stress.repair("Ada", 1860, "the fort", 2, ""), "must say what was rebuilt",
                "a repair with no words is refused");
        refused(stress.repair("Ada", 1860, "the fort", 0, "rebuilt"), "repairs nothing",
                "and repairing nothing is refused");
        Stress.Changed small = stress.repair("Ada", 1860, "the fort", 4, "the stones went back");
        ok(small.ok(), "a repair is booked: " + small.entry().line());
        eq(stress.total(), 8, "and the counter falls");
        eq(stress.repaired(), 4, "by what was repaired");
        Stress.Changed big = stress.repair("Ada", 1861, "the whole city", 100, "rebuilt it all");
        ok(big.ok(), "an over-large repair is booked");
        eq(stress.total(), 0, "and the counter lands at zero, not below");
        ok(big.entry().why().contains("92 of the repair was unused"),
                "and the entry says how much was unused: " + big.entry().why());
        ok(big.entry().why().contains("the counter was at 8"), "and what it was at");

        // ------------------------------------------------ 5. THE BOOKS AND THE REPORT
        Stress fresh = Stress.empty();
        fresh.add(Source.EVENT, "Sam", 1857, "the mutiny of 1857", 3, "the event was touched");
        fresh.add(Source.PERSON, "Sam", 2026, "Fatima", 5, "her life was ended early");
        fresh.connect(fake);
        for (String line : fresh.report()) System.out.println("     " + line);
        ok(fresh.report().get(0).startsWith("stress 15"), "the report opens with the one number: "
                + fresh.report().get(0));
        ok(fresh.report().toString().contains("standing in for Terra++"), "and names the bridge");
        for (String line : fresh.lines()) System.out.println("     " + line);
        ok(fresh.lines().get(0).contains("add · 3 · event"), "the books show each row");
        ok(fresh.lines().get(1).contains("person"), "with its source");
        eq(fresh.books().size(), 2, "and every row is kept");

        System.out.println("     " + Stress.ruleLine());
        ok(Stress.ruleLine().contains("no threshold decides anything"), "the rule line refuses to decide");
        ok(Stress.ruleLine().contains("not as zero"), "and keeps the absent-bridge rule");

        System.out.println("\nStep 53 part 4: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
