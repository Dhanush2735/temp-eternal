/* Step 51 part 2 (G8): a branch saved as its differences from its parent.
   The claim: the root is saved whole once, every branch after it saves only what it changed, restoring walks the
   chain from the root down, a chain that does not reach a root or loops is refused rather than guessed, and the
   cheap copy can be checked key by key against the expensive one. */
import com.eternalengine.timeline.BranchSave;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

public class Step51SaveProbe {
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

    static void refuses(Runnable r, String contains, String what) {
        checks++;
        try {
            r.run();
            failed++;
            System.out.println("  FAIL " + what + "  expected a refusal and got none");
        } catch (IllegalStateException | IllegalArgumentException e) {
            if (contains != null && !e.getMessage().contains(contains)) {
                failed++;
                System.out.println("  FAIL " + what + "  wrong refusal: " + e.getMessage());
            }
        }
    }

    /** A world of flags under the real prefixes, so the size measurement is not a toy. */
    static Map<String, String> world() {
        Map<String, String> f = new LinkedHashMap<>();
        String[] prefixes = {"event.", "dynasty.", "climate.", "economy.", "tech.", "religion.", "population.",
                "disease.", "trade.", "player.", "civ.", "diplomacy.", "famine.", "food.", "urban.", "timeline.",
                "quarantine.", "vip.", "holy_war.", "branch."};
        for (String p : prefixes) {
            for (int i = 0; i < 10; i++) {
                f.put(p + "flag_" + i, "value_" + (i * 7 % 13));
            }
        }
        return f;
    }

    /** The flags b1 holds, for the two snapshots above that differ only in their year. */
    static Map<String, String> basedOnB1() {
        Map<String, String> f = new TreeMap<>(world());
        f.put("event.triggered.sepoy_mutiny", "1857");
        f.put("dynasty.ruler.mughal", "Bahadur Shah II");
        f.put("timeline.diverged", "true");
        return f;
    }

    public static void main(String[] args) {
        Map<String, String> base = world();
        BranchSave.Snapshot main = BranchSave.Snapshot.of(base, 1857, "main");
        System.out.println("     a world of " + main.flagCount() + " flags, " + main.bytes() + " bytes, in 1857");

        BranchSave save = BranchSave.root(main, "the real history");
        eq(save.size(), 1, "one save to start");
        ok(save.get("main").isRoot(), "and it is the root");
        eq(save.get("main").changed().size(), main.flagCount(), "the root saves every flag, once");
        eq(save.restore("main").flagCount(), main.flagCount(), "and restores to the same world");

        // ------------------------------------------------ 1. A BRANCH SAVES ONLY WHAT IT CHANGED
        Map<String, String> b1flags = new TreeMap<>(base);
        b1flags.put("event.triggered.sepoy_mutiny", "1857");
        b1flags.put("dynasty.ruler.mughal", "Bahadur Shah II");
        b1flags.put("timeline.diverged", "true");
        BranchSave.Snapshot b1 = BranchSave.Snapshot.of(b1flags, 1857, "b1");
        save = save.branch(main, b1, 1857, List.of("pin_sepoy_mutiny", "pin_sibling_1"), "the mutiny did not happen");
        BranchSave.Delta d1 = save.get("b1");
        eq(d1.changed().size(), 3, "the branch changed three flags and saves three");
        eq(d1.removed().size(), 0, "and removed none");
        eq(d1.suppressedPins().size(), 2, "it names the two pins that stopped happening");
        eq(d1.touched(), 3, "so it owns three flags, not two hundred");
        ok(d1.bytes() * 10 < main.bytes(), "and its save is far smaller than the world: " + d1.bytes()
                + " bytes against " + main.bytes());
        ok(!d1.changed().containsKey("tech.flag_0"), "a flag it did not change is not in its save");
        System.out.println("     " + save.restore("b1").flagCount() + " flags restored for b1");

        // ------------------------------------------------ 2. RESTORING IS EXACTLY THE FULL STATE
        eq(save.restore("b1").flags(), b1.flags(), "restoring the branch gives the whole state back, flag for flag");
        eq(save.restore("b1").year(), 1857, "and the year");
        eq(save.restore("b1").activeBranch(), "b1", "and which branch the world was showing");
        eq(save.diff("b1", b1).size(), 0, "and the cheap copy says the same thing as a full save of it");

        // ------------------------------------------------ 3. THREE DEEP, EACH FROM ITS OWN PARENT
        Map<String, String> b2flags = new TreeMap<>(b1flags);
        b2flags.put("tech.flag_0", "telegraph");
        b2flags.remove("famine.flag_3");
        BranchSave.Snapshot b2 = BranchSave.Snapshot.of(b2flags, 1861, "b2");
        save = save.branch(b1, b2, 1861, List.of("pin_famine_1861"), "the famine did not come");
        BranchSave.Delta d2 = save.get("b2");
        eq(d2.parentId(), "b1", "the second branch's parent is the first branch and not the root");
        eq(d2.changed().size(), 1, "it changed one flag");
        eq(d2.removed().size(), 1, "and removed one");
        ok(d2.removed().contains("famine.flag_3"), "and it says which: " + d2.removed());
        eq(d2.changed().size() + d2.removed().size(), 2, "two differences from its parent, not from the root");

        Map<String, String> b3flags = new TreeMap<>(b2flags);
        b3flags.put("population.flag_2", "1901");
        BranchSave.Snapshot b3 = BranchSave.Snapshot.of(b3flags, 1901, "b3");
        save = save.branch(b2, b3, 1901, List.of(), "the century turned differently");
        eq(save.get("b3").changed().size(), 1, "three deep, still one flag saved");

        BranchSave.Restored r3 = save.chain("b3");
        ok(r3.complete(), "the chain restores: " + r3.line());
        eq(r3.applied(), List.of("main", "b1", "b2", "b3"), "and it walks the chain from the root down");
        eq(r3.snapshot().flags(), b3.flags(), "and lands on the right world");
        eq(save.diff("b3", b3).size(), 0, "three deep, the deltas still say exactly what a full save says");

        // The famine flag: removed at b2, so it must stay gone three deep. A delta save that loses a removal is
        // the classic way a save system goes quietly wrong, so it gets its own check.
        ok(!save.restore("b3").flags().containsKey("famine.flag_3"), "a flag removed at b2 is still gone at b3");
        ok(save.restore("b1").flags().containsKey("famine.flag_3"), "and is still there at b1, where it was removed later");

        // ------------------------------------------------ 4. A SIBLING IS NOT AFFECTED
        Map<String, String> b1bflags = new TreeMap<>(base);
        b1bflags.put("event.triggered.other_thing", "1858");
        BranchSave.Snapshot b1b = BranchSave.Snapshot.of(b1bflags, 1858, "b1b");
        save = save.branch(main, b1b, 1858, List.of(), "a different fork from the same year");
        eq(save.childrenOf("main").size(), 2, "the root has two children");
        eq(save.childrenOf("b1"), List.of("b2"), "and b1 has one");
        eq(save.childrenOf("b2"), List.of("b3"), "and b2 has one");
        ok(!save.restore("b1b").flags().containsKey("event.triggered.sepoy_mutiny"),
                "the sibling's flags do not leak into this branch");
        eq(save.restore("b1").flags().get("event.triggered.sepoy_mutiny"), "1857", "and this branch keeps its own");
        eq(save.diff("b1b", b1b).size(), 0, "the sibling restores exactly too");
        ok(!save.restore("b1").activeBranch().equals(save.restore("b1b").activeBranch()), "two branches, two states");

        // ------------------------------------------------ 5. A BROKEN CHAIN IS REFUSED, NOT GUESSED
        // A file that arrived from disk with a parent that is not in it. The builder refuses to write this; the
        // reader has to survive it, so it is built here the way a file would.
        BranchSave orphans = BranchSave.of(new BranchSave.Delta("lonely", "nowhere", 1900, Map.of("a", "b"),
                Set.of(), List.of(), ""));
        BranchSave.Restored rl = orphans.chain("lonely");
        ok(!rl.complete(), "a branch whose parent is not saved cannot be restored");
        ok(rl.snapshot() == null, "and no state is produced at all");
        ok(String.join(" ", rl.refused()).contains("no save for nowhere"), "and it says what is missing: " + rl.refused());

        ok(orphans.restore("nothing") == null, "restoring a branch that was never saved gives nothing");
        eq(orphans.diff("nothing", main).size(), 1, "and the diff reports it as a refusal, not as a difference");

        // ------------------------------------------------ 6. A LOOPING SAVE IS REFUSED
        Map<String, String> loopFlags = new TreeMap<>();
        loopFlags.put("loop", "true");
        BranchSave.Delta l1 = new BranchSave.Delta("l1", "l2", 1900, loopFlags, Set.of(), List.of(), "");
        BranchSave.Delta l2 = new BranchSave.Delta("l2", "l1", 1901, loopFlags, Set.of(), List.of(), "");
        BranchSave.Restored rloop = BranchSave.of(l1, l2).chain("l1");
        ok(!rloop.complete(), "a parent pointer that loops cannot be restored");
        ok(String.join(" ", rloop.refused()).contains("loops"), "and the refusal says so: " + rloop.refused());

        // ------------------------------------------------ 7. A WRONG DELTA IS FOUND AND BLAMED
        Map<String, String> wrongFlags = new TreeMap<>(b2flags);
        wrongFlags.put("tech.flag_0", "telegraph");        // as b2 says
        wrongFlags.put("climate.flag_4", "a different value");
        BranchSave.Snapshot wrongFull = BranchSave.Snapshot.of(wrongFlags, 1861, "b2");
        List<BranchSave.Difference> diffs = save.diff("b2", wrongFull);
        eq(diffs.size(), 1, "one flag where the cheap copy and the full save disagree: " + diffs.size());
        ok(diffs.get(0).key().equals("climate.flag_4"), "and it is the right flag: " + diffs.get(0).key());
        ok(diffs.get(0).line().contains("saved a different value"), "the line says both values: " + diffs.get(0).line());

        // A delta that sets a flag to its parent's value is a delta that lied about changing it; the diff has to
        // catch that even though nothing about it looks wrong.
        BranchSave.Snapshot lyingFull = BranchSave.Snapshot.of(base, 1857, "b1");
        List<BranchSave.Difference> lieDiffs = save.diff("b1", lyingFull);
        ok(lieDiffs.size() >= 3, "a branch saved as changing three flags, restored onto the unchanged world, shows "
                + "three disagreements: " + lieDiffs.size());
        boolean blamed = false;
        for (BranchSave.Difference d : lieDiffs) {
            if (d.introducedBy() != null && d.introducedBy().equals("b1")) blamed = true;
        }
        ok(blamed, "and the blame names the branch whose delta introduced it");

        // ------------------------------------------------ 8. THE SIZE, WHICH IS THE POINT
        String cost = save.cost(main);
        System.out.println("     " + cost);
        ok(cost.contains("branches"), "the cost line reports what the cheap copy costs");
        ok(save.deltaBytes() * 4 < main.bytes() * save.size(), "and the branches cost less than saving them whole");
        ok(save.ruleLine().contains("cannot be restored without"), "the rule line says the condition: " + save.ruleLine());

        // ------------------------------------------------ 9. A BRANCH THAT CHANGED NOTHING
        // A branch at rest is a branch at the moment it split, so a full save of it from a LATER year has the same
        // flags and a later clock. That is not a disagreement about the branch, and the first version of diff()
        // called it one. A full save from BEFORE the split is a disagreement, because no state of a branch can be
        // older than the split that made it.
        BranchSave.Snapshot later = BranchSave.Snapshot.of(basedOnB1(), 1901, "b1");
        eq(save.diff("b1", later).size(), 0, "a full save of the branch from a later year agrees with the cheap one");
        BranchSave.Snapshot tooEarly = BranchSave.Snapshot.of(basedOnB1(), 1800, "b1");
        eq(save.diff("b1", tooEarly).size(), 1, "a full save from before the branch split does not");

        BranchSave.Snapshot same = BranchSave.Snapshot.of(base, 1857, "quiet");
        BranchSave quietSave = BranchSave.root(main, "the real history").branch(main, same, 1857, List.of(),
                "a fork with no consequences");
        eq(quietSave.get("quiet").touched(), 0, "a branch that changed nothing saves nothing");
        eq(quietSave.restore("quiet").flags(), main.flags(), "and restores to its parent's world exactly");
        eq(quietSave.diff("quiet", same).size(), 0, "the diff agrees");

        // ------------------------------------------------ 10. THE SNAPSHOT CANNOT BE CHANGED BEHIND YOUR BACK
        Map<String, String> mutable = new TreeMap<>(base);
        BranchSave.Snapshot held = BranchSave.Snapshot.of(mutable, 1900, "held");
        mutable.put("event.injected", "after the save");
        ok(!held.flags().containsKey("event.injected"), "a snapshot does not see changes made after it was taken");
        checks++;
        try {
            held.flags().put("x", "y");
            failed++;
            System.out.println("  FAIL a snapshot's flags can be written to");
        } catch (UnsupportedOperationException e) {
            // what we wanted
        }
        eq(new BranchSave.Snapshot(null, 1900, null).activeBranch(), "main", "a snapshot with no branch is the main one");

        // ------------------------------------------------ 11. REFUSALS
        BranchSave s0 = save;
        refuses(() -> s0.branch(main, main, 1857, List.of(), ""), "its own parent",
                "a branch cannot be its own parent");
        refuses(() -> s0.branch(null, b1, 1857, List.of(), ""), "needs the parent's state",
                "a branch with no parent state is refused");
        final BranchSave empty = BranchSave.empty();
        BranchSave.Snapshot lonelyView = BranchSave.Snapshot.of(base, 1857, "unseen");
        refuses(() -> empty.branch(lonelyView, b1, 1857, List.of(), ""), "never saved",
                "a branch whose parent was never saved is refused");
        checks++;
        try {
            new BranchSave.Delta("", null, 1, Map.of(), Set.of(), List.of(), "");
            failed++;
            System.out.println("  FAIL a saved branch with no id was allowed");
        } catch (IllegalArgumentException e) {
            // what we wanted
        }

        System.out.println("\nStep 51 part 2: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }

}
