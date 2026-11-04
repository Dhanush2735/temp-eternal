/* Step 54 part 6: the chain, end to end. Each class passed its own probe; only the chain proves the game.
   The chain: the unbroken land declared -> a rupture in one era, its copy taken first -> the generator's
   work checked clean -> a second rupture in another era with broken physics -> a third whose generator lies,
   named -> and one with no generator at all, reported as unchecked. Refused ruptures leave closed copies and
   nothing else. */
import com.eternalengine.terrabridge.BrokenPhysics;
import com.eternalengine.terrabridge.LandSpec;
import com.eternalengine.terrabridge.LandSpec.Mirror;
import com.eternalengine.timeline.BeforeChange;
import com.eternalengine.timeline.BranchSave;
import com.eternalengine.timeline.RuptureEngine;
import com.eternalengine.timeline.RuptureEngine.Verdict;
import com.eternalengine.timeline.Ruptures;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Step54ChainProbe {
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

    public static void main(String[] args) {
        BeforeChange copies = BeforeChange.empty();
        Ruptures worlds = Ruptures.empty();
        worlds.declare("earth", null, LandSpec.earth(), -3000, "the land as Terra++ makes it");

        Ruptures.Port terra = new Ruptures.Port() {
            @Override
            public LandSpec.Reported report(String universeId) {
                if (universeId.equals("u-cuzco-1576")) {
                    return new LandSpec.Reported(63, -64, 320, false, Mirror.NONE, "Terra++");
                }
                if (universeId.equals("u-delhi-1857")) {
                    return new LandSpec.Reported(120, -2032, 2032, true, Mirror.EAST_WEST, "Terra++");
                }
                return new LandSpec.Reported(63, -2032, 2032, false, Mirror.NONE, "Terra++");
            }

            @Override
            public String describe() {
                return "a recorder, standing in for Terra++";
            }
        };

        // ------------------------------------------------ 1. THE FIRST RUPTURE, IN 1576
        LandSpec.Made shallow = LandSpec.make(63, -64, 320, false, Mirror.NONE, "the fall of Cuzco");
        BranchSave.Snapshot then = BranchSave.Snapshot.of(Map.of("state.world", "1576"), 1576, "main");
        Verdict cuzco = RuptureEngine.rupture("the fall of Cuzco", "u-cuzco-1576", "earth", shallow.spec(),
                null, 1576, "the world cracked at Cuzco", copies, then, worlds, terra);
        copies = cuzco.copiesAfter();
        ok(cuzco.ok(), "a universe cracks open in 1576: " + cuzco.decision().why());
        ok(cuzco.landCheck().clean(), "and the generator's land checks clean");
        eq(cuzco.physicsChanges().get(0), "the physics of the unbroken world",
                "with the physics of the unbroken world");
        eq(cuzco.made().changes().size(), 1, "the land changed in one way only: "
                + cuzco.made().changes());

        // ------------------------------------------------ 2. THE SECOND, IN 1857, WITH BROKEN PHYSICS
        LandSpec.Made flipped = LandSpec.make(120, -2032, 2032, true, Mirror.EAST_WEST,
                "the mutiny's year");
        BrokenPhysics.Made broke = BrokenPhysics.make(0.3, 6000L, 1.0, 0.4, true, true, true, true, true,
                "the mutiny's year");
        BranchSave.Snapshot later = BranchSave.Snapshot.of(Map.of("state.world", "1857"), 1857, "main");
        Verdict delhi = RuptureEngine.rupture("the mutiny of 1857", "u-delhi-1857", "earth", flipped.spec(),
                broke.spec(), 1857, "the world cracked at Delhi", copies, later, worlds, terra);
        copies = delhi.copiesAfter();
        ok(delhi.ok(), "a second universe cracks open in 1857");
        ok(delhi.landCheck().clean(), "and its land checks clean too");
        eq(delhi.physicsChanges().size(), 8, "with eight broken physics facts");
        ok(delhi.line().contains("bed_works"), "each naming its mechanism: beds say bed_works");
        ok(delhi.line().contains("mod-side rules"), "and the mod-side ones say mod-side");

        // ------------------------------------------------ 3. A GENERATOR THAT LIES IS NAMED
        LandSpec.Made highSea = LandSpec.make(200, -2032, 2032, false, Mirror.NONE, "the seas rose");
        Verdict liar = RuptureEngine.rupture("2026", "u-liar-2026", "earth", highSea.spec(), null, 2026,
                "the seas rose", copies, BranchSave.Snapshot.of(Map.of("state.world", "2026"), 2026, "main"),
                worlds, terra);
        copies = liar.copiesAfter();
        ok(liar.ok(), "a third cracks open in 2026");
        ok(!liar.landCheck().clean(), "and the generator did not make it");
        ok(liar.line().contains("asked for 200, made 63"), "and the verdict names the sea's disagreement: "
                + liar.line());

        // ------------------------------------------------ 4. ONE WITH NO GENERATOR SAYS IT WAS UNCHECKED
        Verdict nowhere = RuptureEngine.rupture("2100", "u-deep-2100", "earth",
                LandSpec.make(-1950, -2032, -1900, false, Mirror.NONE, "the sea is gone").spec(),
                BrokenPhysics.make(0.0, null, 0.1, 1.0, false, true, true, true, true, "2100").spec(),
                2100, "a traveller's year", copies,
                BranchSave.Snapshot.of(Map.of("state.world", "2100"), 2100, "main"), worlds, null);
        copies = nowhere.copiesAfter();
        ok(nowhere.ok(), "a fourth opens with no generator connected");
        ok(nowhere.line().contains("could not be checked"), "and it says its land was unchecked: "
                + nowhere.line());
        ok(nowhere.physicsChanges().toString().contains("0.0"), "its gravity is none");
        ok(nowhere.physicsChanges().toString().contains("no vanilla flag exists at all")
                        || nowhere.line().contains("mod-side rules"),
                "and floating blocks would be mod-side");

        // ------------------------------------------------ 5. REFUSALS LEAVE CLOSED COPIES AND NOTHING ELSE
        Verdict noop = RuptureEngine.rupture("2026", "u-noop", "earth", LandSpec.earth(), null, 2026,
                "nothing", copies, BranchSave.Snapshot.of(Map.of("state.world", "2026"), 2026, "main"),
                worlds, terra);
        copies = noop.copiesAfter();
        ok(!noop.ok(), "a rupture that changes no land is refused");
        eq(copies.openOf(BeforeChange.ChangeKind.RUPTURE), null, "and its copy is closed again");
        eq(worlds.find("u-noop"), null, "with no universe left behind");
        eq(copies.lost(), 0, "and no copy lost");

        // A copy already open blocks the next rupture by name.
        BeforeChange.Taken open = copies.take(BeforeChange.ChangeKind.RUPTURE,
                BranchSave.Snapshot.of(Map.of("state.world", "2100"), 2100, "main"), "a rupture underway");
        copies = open.list();
        Verdict blocked = RuptureEngine.rupture("2100", "u-blocked", "earth", highSea.spec(), null, 2100,
                "x", copies, BranchSave.Snapshot.of(Map.of("state.world", "2100"), 2100, "main"), worlds,
                terra);
        ok(!blocked.ok(), "and nothing cracks open while a copy is open");
        ok(blocked.decision().why().contains("a rupture"), "naming it: " + blocked.decision().why());
        copies = copies.complete(open.made().id());

        // ------------------------------------------------ 6. THE PAGE
        List<Verdict> all = new ArrayList<>(List.of(cuzco, delhi, liar, nowhere, noop, blocked));
        for (String line : RuptureEngine.page(all)) System.out.println("     " + line);
        eq(worlds.all().size(), 5, "four universes exist (earth and four ruptured)");
        eq(RuptureEngine.page(all).size(), 6, "and every verdict has its line");
        ok(RuptureEngine.page(all).get(0).startsWith("u-cuzco-1576"), "in the order they happened");
        ok(RuptureEngine.page(all).get(4).startsWith("REFUSED"), "with the refusals marked");
        for (String line : worlds.lines()) System.out.println("     " + line);
        System.out.println("     " + LandSpec.ruleLine());
        System.out.println("     " + BrokenPhysics.ruleLine());
        System.out.println("     " + Ruptures.ruleLine());
        System.out.println("     " + RuptureEngine.ruleLine());

        System.out.println("\nStep 54 part 6: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
