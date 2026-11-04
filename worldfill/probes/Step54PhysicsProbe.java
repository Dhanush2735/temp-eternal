/* Step 54 part 4 (H5): broken physics within Minecraft. The claim: nine facts, and every one names WHO
   enforces it - a Minecraft attribute, a dimension-type flag, or a mod-side rule. Four of the nine are
   mod-side or half so, and no screen may say Minecraft applied those. */
import com.eternalengine.terrabridge.BrokenPhysics;
import com.eternalengine.terrabridge.BrokenPhysics.Mechanism;
import com.eternalengine.terrabridge.BrokenPhysics.Spec;

import java.util.List;

public class Step54PhysicsProbe {
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

    static void refused(BrokenPhysics.Made m, String words, String what) {
        checks++;
        if (m.ok()) {
            failed++;
            System.out.println("  FAIL " + what + "  (a spec was made)");
            return;
        }
        for (String why : m.refused()) {
            if (why.contains(words)) return;
        }
        failed++;
        System.out.println("  FAIL " + what + "  no refusal says \"" + words + "\"; got " + m.refused());
    }

    public static void main(String[] args) {
        // ------------------------------------------------ 1. THE UNBROKEN WORLD
        Spec earth = BrokenPhysics.earth();
        eq(earth.gravity(), 1.0, "Earth's gravity is 1.0");
        eq(earth.fixedSunTime(), null, "its sun moves");
        eq(earth.dayLengthScale(), 1.0, "its day is Earth's");
        eq(BrokenPhysics.changesFromEarth(earth).size(), 0, "and nothing about it is broken");
        ok(earth.describe().contains("unbroken"), "in words: " + earth.describe());

        // ------------------------------------------------ 2. A BROKEN WORLD, EACH FACT NAMING WHO ENFORCES IT
        BrokenPhysics.Made made = BrokenPhysics.make(0.3, 6000L, 1.0, 0.4, true, true, true, true, true,
                "the rupture of 2026");
        ok(made.ok(), "a broken world is a spec: " + (made.ok() ? "" : made.refused()));
        Spec broken = made.spec();
        List<String> changes = BrokenPhysics.changesFromEarth(broken);
        eq(changes.size(), 8, "eight of the nine are broken (the day means nothing under a fixed sun)");
        ok(changes.toString().contains("forge:entity_gravity") || changes.toString().contains("Forge entity "
                + "gravity"), "gravity names the Forge attribute");
        ok(changes.toString().contains("fixed_time"), "the fixed sun names the dimension-type flag");
        ok(changes.toString().contains("ultrawarm"), "the boiling water names its flag");
        ok(changes.toString().contains("bed_works"), "and the beds theirs");
        for (String c : changes) System.out.println("     " + c);
        // The three with no Minecraft flag say so.
        for (String c : changes) {
            if (c.startsWith("extreme weather") || c.startsWith("floating blocks")) {
                ok(c.contains("mod-side rules"), "and a mod-side fact says mod-side: " + c);
            }
        }
        ok(changes.toString().contains("part Minecraft, part mod-side"), "strange mobs say both");

        // ------------------------------------------------ 3. THE TABLE OF NINE
        eq(BrokenPhysics.fields().size(), 9, "the table has the nine rows of H5");
        eq(BrokenPhysics.appliedBy("gravity"), Mechanism.MINECRAFT_ATTRIBUTE,
                "gravity is Minecraft's, via the Forge attribute");
        eq(BrokenPhysics.appliedBy("a fixed sun"), Mechanism.DIMENSION_TYPE, "a fixed sun is the dimension type");
        eq(BrokenPhysics.appliedBy("a racing sun"), Mechanism.MOD_SIDE, "a racing sun is mod-side");
        eq(BrokenPhysics.appliedBy("water boils away"), Mechanism.DIMENSION_TYPE, "ultrawarm is the dimension type");
        eq(BrokenPhysics.appliedBy("extreme weather"), Mechanism.MOD_SIDE, "extreme weather is mod-side");
        eq(BrokenPhysics.appliedBy("floating blocks"), Mechanism.MOD_SIDE,
                "floating blocks have no vanilla flag at all");
        eq(BrokenPhysics.appliedBy("strange mobs"), Mechanism.PART_BOTH, "strange mobs are part both");
        eq(BrokenPhysics.appliedBy("no such fact"), null, "and there is no other fact");
        int modSide = 0;
        for (BrokenPhysics.Field f : BrokenPhysics.fields()) {
            if (f.by() == Mechanism.MOD_SIDE || f.by() == Mechanism.PART_BOTH) {
                modSide++;
            }
        }
        eq(modSide, 4, "exactly four of the nine are mod-side or half so");
        for (BrokenPhysics.Field f : BrokenPhysics.fields()) System.out.println("     " + f.line());

        // ------------------------------------------------ 4. A SPEC THAT CANNOT MEAN ANYTHING IS REFUSED
        refused(BrokenPhysics.make(-1.0, null, 1.0, 0.0, false, false, false, false, false, ""),
                "below no gravity at all", "negative gravity is refused");
        refused(BrokenPhysics.make(1.0, 24000L, 1.0, 0.0, false, false, false, false, false, ""),
                "not a time of Minecraft's day", "a fixed sun at midnight tomorrow is refused");
        refused(BrokenPhysics.make(1.0, 6000L, 0.5, 0.0, false, false, false, false, false, ""),
                "fixed and racing", "a sun that is both fixed and racing is refused, not guessed");
        refused(BrokenPhysics.make(1.0, null, 0.0, 0.0, false, false, false, false, false, ""),
                "lasts nothing", "a day that lasts nothing is refused");
        refused(BrokenPhysics.make(1.0, null, 1.0, 1.5, false, false, false, false, false, ""),
                "not a share of full light", "and light beyond full is refused");

        // A racing sun is fine on its own.
        BrokenPhysics.Made racing = BrokenPhysics.make(1.0, null, 0.1, 0.0, false, false, false, false,
                false, "the sun runs");
        ok(racing.ok(), "a racing sun alone is a spec");
        ok(BrokenPhysics.changesFromEarth(racing.spec()).get(0).contains("mod-side rules"),
                "and names who would enforce it: " + BrokenPhysics.changesFromEarth(racing.spec()).get(0));

        // ------------------------------------------------ 5. THE CHECK: ASKED AGAINST REPORTED
        BrokenPhysics.Reported same = new BrokenPhysics.Reported(0.3, 6000L, 1.0, 0.4, true, true, true,
                true, true, "the world");
        eq(BrokenPhysics.diff(broken, same).size(), 0, "a world that is what was asked checks clean");
        BrokenPhysics.Reported wrong = new BrokenPhysics.Reported(1.0, 6000L, 1.0, 0.4, true, true, true,
                true, true, "the world");
        List<BrokenPhysics.Difference> diffs = BrokenPhysics.diff(broken, wrong);
        eq(diffs.size(), 1, "one wrong fact is one disagreement");
        eq(diffs.get(0).what(), "gravity", "and named");
        ok(diffs.get(0).line().contains("Forge entity gravity"), "with its mechanism: " + diffs.get(0).line());
        eq(BrokenPhysics.diff(broken, null).get(0).made(), "nothing was reported",
                "a world that reports nothing is not a pass");
        eq(BrokenPhysics.diff(null, same).get(0).what(), "(the spec)", "and a spec of nothing is refused");

        // ------------------------------------------------ 6. THE RULE
        System.out.println("     " + BrokenPhysics.ruleLine());
        ok(BrokenPhysics.ruleLine().contains("mod-side"), "the rule line keeps the mod-side count");
        ok(BrokenPhysics.ruleLine().contains("Four of the nine"), "and says how many");

        System.out.println("\nStep 54 part 4: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
