/* Step 54 part 5: the one call that makes a rupture happen. The claim: five things in order - the copy
   first, the universe, its land, its physics, and the generator's work checked. A refused rupture leaves
   nothing behind but a closed copy; an unchecked one says it was unchecked. */
import com.eternalengine.player.Permissions.Decision;
import com.eternalengine.terrabridge.BrokenPhysics;
import com.eternalengine.terrabridge.LandSpec;
import com.eternalengine.terrabridge.LandSpec.Mirror;
import com.eternalengine.terrabridge.LandSpec.Spec;
import com.eternalengine.timeline.BeforeChange;
import com.eternalengine.timeline.BranchSave;
import com.eternalengine.timeline.RuptureEngine;
import com.eternalengine.timeline.RuptureEngine.Verdict;
import com.eternalengine.timeline.Ruptures;

import java.util.List;
import java.util.Map;

public class Step54EngineProbe {
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
            System.out.println("  FAIL " + what + "  (it happened: " + v.line() + ")");
            return;
        }
        if (v.decision().why().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no reason says \"" + words + "\"; got " + v.decision().why());
    }

    public static void main(String[] args) {
        Spec earthLand = LandSpec.earth();
        LandSpec.Made other = LandSpec.make(120, -2032, 2032, true, Mirror.EAST_WEST, "the rupture of 2026");
        BrokenPhysics.Made otherPhysics = BrokenPhysics.make(0.3, 6000L, 1.0, 0.4, true, true, true, true,
                true, "the rupture of 2026");

        Ruptures worlds = Ruptures.empty();
        worlds.declare("earth", null, earthLand, -3000, "the land as Terra++ makes it");
        BeforeChange copies = BeforeChange.empty();
        BranchSave.Snapshot now = BranchSave.Snapshot.of(Map.of("state.world", "2026"), 2026, "main");

        Ruptures.Port honest = new Ruptures.Port() {
            @Override
            public LandSpec.Reported report(String universeId) {
                return new LandSpec.Reported(120, -2032, 2032, true, Mirror.EAST_WEST, "a recorder");
            }

            @Override
            public String describe() {
                return "a recorder, standing in for Terra++";
            }
        };

        // ------------------------------------------------ 1. THE WHOLE CALL, IN ORDER
        // BeforeChange is immutable-style (step 51): the call returns the new copy book in the verdict, and
        // the caller threads it. The first version of this probe read the OLD book and its "the copy closed"
        // check would have passed on a book that never held the copy at all.
        Verdict made = RuptureEngine.rupture("Sam", "u-high-sea", "earth", other.spec(),
                otherPhysics.spec(), 2026, "the sea rose and the land flipped", copies, now, worlds, honest);
        ok(made.ok(), "the rupture happens: " + (made.ok() ? made.line() : made.decision().why()));
        ok(made.backupId() != null, "and its copy is named: " + made.backupId());
        copies = made.copiesAfter();
        eq(copies.openOf(BeforeChange.ChangeKind.RUPTURE), null,
                "the copy closed once the change was answered");
        eq(made.made().parent(), "earth", "the universe knows its parent");
        eq(made.landCheck().clean(), true, "and the generator's land checks clean");
        ok(made.line().contains("matches what was asked"), "in words: the check says so");
        eq(made.physicsChanges().size(), 8, "the physics carries its eight broken facts");
        ok(made.line().contains("forge:entity_gravity") || made.line().contains("Forge entity gravity"),
                "and the line names the Forge attribute");
        for (String line : RuptureEngine.page(List.of(made))) System.out.println("     " + line);

        // ------------------------------------------------ 2. A REFUSED RUPTURE LEAVES A CLOSED COPY AND NOTHING ELSE
        Verdict refused = RuptureEngine.rupture("Sam", "u-same", "earth", earthLand, otherPhysics.spec(),
                2026, "nothing changes", copies, now, worlds, honest);
        ok(!refused.ok(), "a rupture that changes no land is refused");
        ok(refused.decision().why().contains("not a rupture"), "and says why");
        ok(refused.backupId() != null, "its copy was taken and is named: " + refused.backupId());
        copies = refused.copiesAfter();
        eq(copies.openOf(BeforeChange.ChangeKind.RUPTURE), null,
                "and closed again: a copy guarding nothing must not block the next change");
        eq(worlds.find("u-same"), null, "and no universe exists");
        eq(copies.lost(), 0, "nothing was lost from the copies");

        // ------------------------------------------------ 3. THE COPY FIRST, ALWAYS
        refused(RuptureEngine.rupture("Sam", "u-x", "earth", other.spec(), null, 2026, "x", null, now,
                worlds, honest), "keeper of copies", "with no keeper of copies, nothing happens");
        refused(RuptureEngine.rupture("Sam", "u-x", "earth", other.spec(), null, 2026, "x", copies, null,
                worlds, honest), "copy of nothing", "and a copy of nothing is refused");
        // A rupture copy already open blocks the next one, by name.
        BeforeChange.Taken open = copies.take(BeforeChange.ChangeKind.RUPTURE, now, "a rupture already "
                + "underway");
        ok(open.ok(), "a copy is open");
        copies = open.list();
        Verdict blocked = RuptureEngine.rupture("Sam", "u-blocked", "earth", other.spec(), null, 2026, "x",
                copies, now, worlds, honest);
        ok(!blocked.ok(), "and the next rupture is refused while it is open");
        ok(blocked.decision().why().contains("a rupture"), "naming the kind of the open copy: "
                + blocked.decision().why());
        eq(worlds.find("u-blocked"), null, "and nothing exists");
        copies = copies.complete(open.made().id());

        // ------------------------------------------------ 4. AN UNCHECKED ONE SAYS IT WAS UNCHECKED
        Verdict unchecked = RuptureEngine.rupture("Sam", "u-deep", "earth",
                LandSpec.make(30, -2032, 2032, false, Mirror.NONE, "the sea fell").spec(), null, 2027,
                "the sea fell", copies, now, worlds, null);
        copies = unchecked.copiesAfter();
        ok(unchecked.ok(), "a rupture with no generator still happens: " + unchecked.line());
        ok(!unchecked.landCheck().clean(), "and its land is not checked");
        ok(unchecked.line().contains("could not be checked"), "in words: " + unchecked.line());
        ok(unchecked.line().contains("Terra++ is not connected"), "naming the missing bridge");
        eq(unchecked.physicsChanges().get(0), "the physics of the unbroken world",
                "and no physics spec means the unbroken world");

        // ------------------------------------------------ 5. A GENERATOR THAT LIED IS NAMED, NOT PARDONED
        Ruptures.Port liar = new Ruptures.Port() {
            @Override
            public LandSpec.Reported report(String universeId) {
                return new LandSpec.Reported(63, -2032, 2032, false, Mirror.NONE, "a liar");
            }

            @Override
            public String describe() {
                return "a recorder telling another story";
            }
        };
        Verdict dirty = RuptureEngine.rupture("Sam", "u-liar", "earth",
                LandSpec.make(90, -2032, 2032, true, Mirror.NONE, "a high sea").spec(), null, 2028,
                "the sea rose", copies, now, worlds, liar);
        copies = dirty.copiesAfter();
        ok(dirty.ok(), "the rupture happens");
        ok(!dirty.landCheck().clean(), "and the check is not clean");
        ok(dirty.line().contains("disagrees"), "and the verdict says the generator disagrees: "
                + dirty.line());
        ok(dirty.line().contains("asked for 90, made 63"), "naming the sea's disagreement");

        // ------------------------------------------------ 6. THE RULE
        System.out.println("     " + RuptureEngine.ruleLine());
        ok(RuptureEngine.ruleLine().contains("copy first"), "the rule line keeps the order");
        ok(RuptureEngine.ruleLine().contains("closed copy"), "and the refused-rupture rule");
        ok(RuptureEngine.ruleLine().contains("unchecked"), "and the unchecked rule");

        System.out.println("\nStep 54 part 5: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
