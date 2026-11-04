/* Step 54 part 2 (H3, the land half): a universe's land in five plain facts. The claim: the mod states what
   the land IS and checks what was generated; it does no projection math and generates nothing. Every word
   means one thing: upside down inverts the height profile, mirrored names its axis. */
import com.eternalengine.terrabridge.LandSpec;
import com.eternalengine.terrabridge.LandSpec.Mirror;
import com.eternalengine.terrabridge.LandSpec.Spec;

import java.util.List;

public class Step54LandProbe {
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

    static void refused(LandSpec.Made m, String words, String what) {
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
        // ------------------------------------------------ 1. THE UNBROKEN LAND IS TERRA++'S OWN NUMBERS
        Spec earth = LandSpec.earth();
        eq(earth.seaLevel(), 63, "Earth's sea is Terra++'s fallback: 63");
        eq(earth.minY(), -2032, "its floor is -2032");
        eq(earth.maxY(), 2032, "its ceiling 2032");
        eq(earth.upsideDown(), false, "it is not upside down");
        eq(earth.mirror(), Mirror.NONE, "and not mirrored");
        eq(earth.height(), 4065, "which makes it 4065 tall");
        System.out.println("     " + earth.describe());

        // ------------------------------------------------ 2. A RUPTURED LAND
        LandSpec.Made highSea = LandSpec.make(120, -2032, 2032, true, Mirror.EAST_WEST,
                "the rupture of 2026");
        ok(highSea.ok(), "a high-sea, upside-down, east-west mirrored land is a land: "
                + (highSea.ok() ? "" : highSea.refused()));
        Spec other = highSea.spec();
        eq(other.height(), 4065, "with Earth's own height");
        eq(other.mirror(), Mirror.EAST_WEST, "and one named axis of mirroring");
        List<String> changes = LandSpec.changesFromEarth(other);
        eq(changes.size(), 3, "it differs from Earth in exactly three ways");
        ok(changes.contains("sea level 63 -> 120"), "the sea");
        ok(changes.toString().contains("height profile is inverted"), "the inversion");
        ok(changes.toString().contains("mirrored east-west"), "and the mirror");
        for (String c : changes) System.out.println("     " + c);
        eq(LandSpec.changesFromEarth(earth).size(), 0, "the unbroken land differs from itself in nothing");

        // A rupture of height only.
        LandSpec.Made shallow = LandSpec.make(63, -64, 320, false, Mirror.NONE, "a gentle rupture");
        ok(shallow.ok(), "a shallow world is a land: " + (shallow.ok() ? "" : shallow.refused()));
        eq(LandSpec.changesFromEarth(shallow.spec()).size(), 1, "and differs in the height alone");
        ok(LandSpec.changesFromEarth(shallow.spec()).get(0).contains("-2032..2032 -> -64..320"),
                "saying which: " + LandSpec.changesFromEarth(shallow.spec()).get(0));

        // ------------------------------------------------ 3. A LAND THAT CANNOT BE GENERATED IS REFUSED
        refused(LandSpec.make(63, 100, 50, false, Mirror.NONE, ""), "floor",
                "a floor above the ceiling is refused");
        refused(LandSpec.make(63, -3000, 3000, false, Mirror.NONE, ""), "4096",
                "a world taller than Minecraft can build is refused");
        refused(LandSpec.make(63, 0, 8, false, Mirror.NONE, ""), "not a world",
                "and one shorter than sixteen blocks is refused too");
        refused(LandSpec.make(400, -64, 320, false, Mirror.NONE, ""), "outside the world",
                "a sea outside the world is refused");
        refused(LandSpec.make(63, -64, 320, false, null, ""), "which way it is mirrored",
                "and a mirror with no direction is refused, not guessed");

        // ------------------------------------------------ 4. THE CHECK: ASKED AGAINST MADE
        LandSpec.Reported made = new LandSpec.Reported(63, -2032, 2032, false, Mirror.NONE, "Terra++");
        eq(LandSpec.diff(earth, made).size(), 0, "a generator that made what was asked agrees, key by key");
        LandSpec.Reported wrong = new LandSpec.Reported(62, -2032, 2032, false, Mirror.NONE, "Terra++");
        List<LandSpec.Difference> diffs = LandSpec.diff(earth, wrong);
        eq(diffs.size(), 1, "one wrong fact is one disagreement");
        eq(diffs.get(0).what(), "sea level", "and named");
        eq(diffs.get(0).asked(), "63", "with what was asked");
        eq(diffs.get(0).made(), "62", "and what was made");
        for (LandSpec.Difference d : diffs) System.out.println("     " + d.line());
        LandSpec.Reported allWrong = new LandSpec.Reported(0, 0, 4095, true, Mirror.NORTH_SOUTH, "Terra++");
        eq(LandSpec.diff(earth, allWrong).size(), 5, "a generator that made a different world disagrees in "
                + "every fact");
        eq(LandSpec.diff(other, new LandSpec.Reported(120, -2032, 2032, true, Mirror.EAST_WEST, "Terra++"))
                .size(), 0, "and the ruptured land is checkable like any other");
        eq(LandSpec.diff(earth, null).get(0).what(), "(the report)", "a generator that reports nothing is "
                + "not a pass");
        ok(LandSpec.diff(earth, null).get(0).made().contains("nothing was reported"), "and says so");
        eq(LandSpec.diff(null, made).get(0).what(), "(the spec)", "and neither is a spec of nothing");

        // ------------------------------------------------ 5. THE WORDS KEEP THEIR MEANINGS
        ok(Mirror.EAST_WEST.words().contains("east"), "the mirror says which way");
        ok(Mirror.NONE.words().contains("not mirrored"), "and none says none");
        ok(earth.describe().contains("sea level 63"), "the description carries the facts");
        ok(other.describe().contains("height profile is inverted"), "and what the words mean");
        System.out.println("     " + LandSpec.ruleLine());
        ok(LandSpec.ruleLine().contains("no projection math"), "the rule line keeps TerraBridge's rule");
        ok(LandSpec.ruleLine().contains("Terra++ generates"), "and says who generates");

        System.out.println("\nStep 54 part 2: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
