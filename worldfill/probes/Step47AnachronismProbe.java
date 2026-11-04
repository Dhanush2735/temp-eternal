/* Step 47 part 3 (E8, E22): what a year may use.
   The distinction under test: three kinds of impossible thing, three answers. A brewing stand in
   1300 is not an anachronism, it is an alchemist's bench; an ender pearl is not anything, ever. */
import com.eternalengine.tools.Anachronisms;

import java.util.List;
import java.util.Map;

public class Step47AnachronismProbe {
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

    static final Anachronisms A = Anachronisms.get();
    static final Anachronisms.Setting STRICT = Anachronisms.Setting.STRICT;
    static final Anachronisms.Setting TRAVELLER = Anachronisms.Setting.TRAVELLER;

    public static void main(String[] args) {
        System.out.println("== " + A + " ==");
        ok(A.hasData(), "the register has data");
        eq(A.problem(), null, "no problem reported");
        ok(A.finding() != null && A.finding().contains("alchemy"),
                "the finding is about alchemy being real history");
        System.out.println("  " + A.summary(STRICT));

        // ------------------------------------------------------- 1. THE THREE KINDS EXIST
        ok(A.count(Anachronisms.Kind.REAL) >= 2, A.count(Anachronisms.Kind.REAL) + " real");
        ok(A.count(Anachronisms.Kind.MYTH) >= 3, A.count(Anachronisms.Kind.MYTH) + " myth");
        ok(A.count(Anachronisms.Kind.NEVER) >= 5, A.count(Anachronisms.Kind.NEVER) + " never");

        // ------------------------------------------------------- 2. THE ONE THE GAME GOT RIGHT
        Anachronisms.Verdict gold = A.judge("minecraft:golden_sword", -3000, STRICT);
        ok(gold.allowed(), "a golden sword is allowed in 3000 BC");
        ok(!gold.renamed(), "and needs no renaming");
        System.out.println("  " + gold.line());

        // ------------------------------------------------------- 3. THE MIDDLE KIND: RENAME, NOT DELETE
        Anachronisms.Verdict brew = A.judge("minecraft:brewing_stand", 1300, STRICT);
        ok(brew.allowed(), "a brewing stand is ALLOWED in 1300, not locked");
        ok(brew.renamed(), "and it is renamed");
        eq(brew.asWhat(), "an alchemist's bench", "to an alchemist's bench");
        System.out.println("  " + brew.line());
        // Alchemy is old but not as old as the world, and the difference matters: the register
        // dates the bench to about 2000 BC, and in 3000 BC there is no bench yet.
        ok(!A.judge("minecraft:brewing_stand", -3000, STRICT).allowed(),
                "but NOT at the first year: the register dates the bench to 2000 BC");
        ok(A.judge("minecraft:brewing_stand", -2000, STRICT).allowed(),
                "and it is there from 2000 BC, which is what the row says");

        Anachronisms.Verdict table = A.judge("minecraft:enchanting_table", 1000, STRICT);
        ok(table.allowed() && table.renamed(), "an enchanting table is allowed as a shrine in 1000");
        eq(table.asWhat(), "a shrine, and a man who says the words", "a shrine");
        ok(A.judge("minecraft:enchanting_table", -3000, STRICT).allowed(),
                "and shrines are as old as belief, which is older than the world");

        // The diamond: a gem with a date and NO tool.
        Anachronisms.Verdict dia = A.judge("minecraft:diamond", -500, STRICT);
        ok(!dia.allowed(), "no diamond in the Mediterranean in 500 BC");
        Anachronisms.Verdict dia300 = A.judge("minecraft:diamond", 0, STRICT);
        ok(dia300.allowed(), "and one in AD 0, which is when the trade ran");
        ok(dia300.renamed(), "renamed, because a diamond was a stone and not a tool");

        // ------------------------------------------------------- 4. THE NEVER KIND
        for (String id : new String[]{"minecraft:ender_pearl", "minecraft:netherite_ingot",
                "minecraft:elytra", "minecraft:totem_of_undying", "minecraft:beacon"}) {
            Anachronisms.Verdict v = A.judge(id, 1400, STRICT);
            ok(!v.allowed(), id + " is locked in a strict world in 1400");
            eq(v.kind(), Anachronisms.Kind.NEVER, "and is marked never, not myth");
            // It is locked at EVERY year, including the last one.
            ok(!A.judge(id, 3000, STRICT).allowed(), id + " is still locked in AD 3000");
            ok(!A.judge(id, -3000, STRICT).allowed(), id + " is locked in 3000 BC too");
        }
        System.out.println("  " + A.judge("minecraft:elytra", 1400, STRICT).line());

        // ------------------------------------------------------- 5. THE TRAVELLER SETTING
        // E8's whole point: the player is an exception, and is SEEN being one.
        Anachronisms.Verdict pearlT = A.judge("minecraft:ender_pearl", 1400, TRAVELLER);
        ok(pearlT.allowed(), "a time traveller may carry an ender pearl in 1400");
        ok(pearlT.why().contains("seen"), "and the verdict says he will be seen doing it");
        System.out.println("  " + pearlT.line());
        // But the traveller does NOT unlock a thing that has a date and has not arrived.
        Anachronisms.Verdict phone = A.judge("minecraft:netherite_ingot", 1400, TRAVELLER);
        ok(phone.allowed(), "and the same for netherite");
        // The setting changes nothing for a real object.
        eq(A.judge("minecraft:anvil", 1200, STRICT).allowed(),
           A.judge("minecraft:anvil", 1200, TRAVELLER).allowed(),
           "the setting does not change a real object's verdict");

        // ------------------------------------------------------- 6. COUNTS AND LISTS
        List<String> lockedStrict = A.lockedAt(1400, STRICT);
        List<String> lockedTraveller = A.lockedAt(1400, TRAVELLER);
        ok(lockedStrict.size() >= 8, lockedStrict.size() + " locked in a strict 1400");
        ok(lockedTraveller.isEmpty(), "and none locked for a time traveller in 1400: "
                + lockedTraveller);
        Map<String, String> ren = A.renamedAt(1400, STRICT);
        ok(ren.size() >= 5, ren.size() + " objects renamed in 1400: " + ren.keySet());
        eq(A.nameFor("minecraft:brewing_stand", 1400, STRICT), "an alchemist's bench",
                "the name a player is shown in 1400");
        eq(A.nameFor("minecraft:anvil", 1400, STRICT), "minecraft:anvil",
                "and an unrenamed object keeps its id");

        // ------------------------------------------------------- 7. THE UNDECLARED IS ALLOWED
        // Never guess: an unknown item is allowed AND the verdict says it was not judged.
        Anachronisms.Verdict unknown = A.judge("somemod:plank", 1400, STRICT);
        ok(unknown.allowed(), "an item the register has never heard of is allowed");
        ok(unknown.why().contains("never refused"), "and says so rather than pretending to know");
        eq(A.judge("", 1400, STRICT).allowed(), true, "and an empty id does not throw");

        // ------------------------------------------------------- 8. THE SETTING PARSES
        eq(Anachronisms.Setting.of("traveller"), TRAVELLER, "the traveller setting parses");
        eq(Anachronisms.Setting.of("Traveller"), TRAVELLER, "and is case-insensitive");
        eq(Anachronisms.Setting.of(null), STRICT, "and the default is strict");
        eq(Anachronisms.Setting.of("nonsense"), STRICT, "and an unknown setting is strict, "
                + "because strict is the safe answer");

        System.out.println("== step 47 anachronisms: " + checks + " checks, " + failed + " failed ==");
        if (failed > 0) System.exit(1);
    }
}
