/* Step 54 part 3 (H3, the act and the check): a rupture makes a new universe with other land. The claim: a
   rupture needs its copy taken first (step 51's rule), must change the land to count, is named once; and
   what the generator made is checked key by key, with no generator the check says it cannot check and passes
   nothing. */
import com.eternalengine.terrabridge.LandSpec;
import com.eternalengine.terrabridge.LandSpec.Mirror;
import com.eternalengine.terrabridge.LandSpec.Spec;
import com.eternalengine.timeline.BeforeChange;
import com.eternalengine.timeline.BranchSave;
import com.eternalengine.timeline.Ruptures;

import java.util.List;
import java.util.Map;

public class Step54RuptureProbe {
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

    static void refused(Ruptures.Ruptured r, String words, String what) {
        checks++;
        if (r.ok()) {
            failed++;
            System.out.println("  FAIL " + what + "  (a universe was made)");
            return;
        }
        if (r.refused().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no reason says \"" + words + "\"; got " + r.refused());
    }

    static void refused(Ruptures.Checked c, String words, String what) {
        checks++;
        if (c.diffs().isEmpty() && c.refused().isEmpty()) {
            failed++;
            System.out.println("  FAIL " + what + "  (clean)");
            return;
        }
        String all = c.line();
        if (all.contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no reason says \"" + words + "\"; got " + all);
    }

    public static void main(String[] args) {
        Spec earthLand = LandSpec.earth();
        LandSpec.Made other = LandSpec.make(120, -2032, 2032, true, Mirror.EAST_WEST, "the rupture of 2026");
        Spec otherLand = other.spec();

        // ------------------------------------------------ 1. THE UNBROKEN ONE, AND WHO BREAKS OFF FROM IT
        Ruptures worlds = Ruptures.empty();
        Ruptures.Ruptured base = worlds.declare("earth", null, earthLand, -3000, "the land as Terra++ makes it");
        ok(base.ok(), "the unbroken universe is declared: " + (base.ok() ? "" : base.refused()));
        refused(worlds.declare("earth", null, earthLand, -3000, "again"), "already a universe called earth",
                "two worlds with one name are refused");
        refused(worlds.declare("", null, earthLand, -3000, ""), "no name is nowhere",
                "a nameless universe is refused");
        refused(worlds.declare("x", null, null, -3000, ""), "what its land is",
                "a universe with no land is refused");
        refused(worlds.declare("x", "nowhere", earthLand, -3000, ""), "no universe called nowhere",
                "a child of nowhere is refused");

        // ------------------------------------------------ 2. A RUPTURE NEEDS ITS COPY TAKEN FIRST
        BeforeChange copies = BeforeChange.empty();
        BranchSave.Snapshot now = BranchSave.Snapshot.of(Map.of("state.world", "2026"), 2026, "main");
        refused(worlds.rupture("Sam", "u-high-sea", "earth", otherLand, 2026, "the sea rose", null),
                "needs its copy taken first", "a rupture with no copy is refused");
        BeforeChange jump = BeforeChange.empty();
        BeforeChange.Taken jumpCopy = jump.take(BeforeChange.ChangeKind.TIME_JUMP, now, "a jump in time");
        ok(jumpCopy.ok(), "a copy of the wrong kind can be taken (it guards a jump)");
        refused(worlds.rupture("Sam", "u-high-sea", "earth", otherLand, 2026, "the sea rose", jumpCopy),
                "needs a copy of", "and does not guard a rupture");

        BeforeChange.Taken guard = copies.take(BeforeChange.ChangeKind.RUPTURE, now, "the world is about to "
                + "break");
        ok(guard.ok(), "a rupture copy is taken before the damage: " + guard.line());
        refused(worlds.rupture("Sam", "u-high-sea", "earth", earthLand, 2026, "nothing changes", guard),
                "changes nothing is not a rupture", "a rupture that changes no land is refused");
        refused(worlds.rupture("Sam", "u-high-sea", "nowhere", otherLand, 2026, "x", guard),
                "no universe called nowhere", "and one off nowhere is refused");

        Ruptures.Ruptured broke = worlds.rupture("Sam", "u-high-sea", "earth", otherLand, 2026,
                "the sea rose and the land flipped", guard);
        ok(broke.ok(), "the rupture happens: " + (broke.ok() ? "" : broke.refused()));
        eq(broke.made().parent(), "earth", "and it broke off from the unbroken one");
        eq(broke.made().changes().size(), 3, "with exactly what it changed, computed not declared");
        ok(broke.made().line().contains("broke off from earth"), "the line says where it came from");
        ok(broke.made().line().contains("height profile is inverted"), "and what is different about its land");
        eq(worlds.childrenOf("earth").size(), 1, "earth has one child");
        refused(worlds.rupture("Sam", "u-high-sea", "earth", otherLand, 2026, "again", guard),
                "already a universe called", "the name is taken once");

        // ------------------------------------------------ 3. CHECK IT: KEY BY KEY, OR SAY IT CANNOT
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
        Ruptures.Checked clean = worlds.check("u-high-sea", honest);
        ok(clean.clean(), "a generator that made what was asked checks clean: " + clean.line());
        Ruptures.Port wrong = new Ruptures.Port() {
            @Override
            public LandSpec.Reported report(String universeId) {
                return new LandSpec.Reported(63, -2032, 2032, false, Mirror.NONE, "a liar");
            }

            @Override
            public String describe() {
                return "a recorder telling another story";
            }
        };
        Ruptures.Checked dirty = worlds.check("u-high-sea", wrong);
        ok(!dirty.clean(), "a generator that made ordinary land is not a pass");
        eq(dirty.diffs().size(), 3, "and every disagreement is named");
        ok(dirty.line().contains("sea level: asked for 120, made 63"), "the sea: " + dirty.line());
        ok(dirty.line().contains("orientation"), "the orientation");
        ok(dirty.line().contains("the mirror"), "and the mirror");
        refused(worlds.check("u-high-sea", null), "Terra++ is not connected",
                "with no generator the check says it cannot check");
        refused(worlds.check("u-high-sea", Ruptures.absent()), "no land can be checked",
                "in the words of the absent bridge");
        refused(worlds.check("no-such", honest), "no universe called no-such",
                "checking nowhere is refused");
        eq(worlds.check("earth", honest).diffs().size(), 3, "and the unbroken land is checked the same way "
                + "(the recorder reports the ruptured land for every id)");

        // ------------------------------------------------ 4. THE PAGE AND THE RULE
        for (String line : worlds.lines()) System.out.println("     " + line);
        ok(worlds.lines().get(0).startsWith("2 universes"), "the page counts what it holds");
        ok(String.join("\n", worlds.lines()).contains("sea level 63"), "with each land in one line");
        eq(worlds.all().size(), 2, "every universe is on the page");
        System.out.println("     " + Ruptures.ruleLine());
        ok(Ruptures.ruleLine().contains("copy taken first"), "the rule line keeps step 51's rule");
        ok(Ruptures.ruleLine().contains("passes nothing"), "and the absent-check rule");

        System.out.println("\nStep 54 part 3: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
