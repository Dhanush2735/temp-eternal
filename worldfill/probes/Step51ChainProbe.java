/* Step 51 part 6: the chain, end to end. Each class passed its own probe; step 49 and step 50 both taught
   that a probe per class proves the class and only a probe per chain proves the game.
   The chain: a copy taken BEFORE the split -> the split -> the branch saved as a difference -> the branch in the
   tree -> travel into it and back -> the world on it -> the book's pages -> and the copy that undoes the lot. */
import com.eternalengine.story.BranchStory;
import com.eternalengine.story.PlaceRecord;
import com.eternalengine.terrabridge.BranchWorld;
import com.eternalengine.timeline.BeforeChange;
import com.eternalengine.timeline.BranchSave;
import com.eternalengine.timeline.BranchTree;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.zip.GZIPInputStream;

public class Step51ChainProbe {
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

    static InputStream gz(String n) throws Exception {
        return new GZIPInputStream(Step51ChainProbe.class.getResourceAsStream(
                "/data/eternalengine/eternal/history/" + n));
    }

    static Map<String, String> world(String ruler, String rail, boolean mutiny) {
        Map<String, String> f = new TreeMap<>();
        for (int i = 0; i < 40; i++) f.put("tech.flag_" + i, "old");
        for (int i = 0; i < 20; i++) f.put("event.flag_" + i, "done");
        f.put("dynasty.ruler.mughal", ruler);
        f.put("tech.railway", rail);
        if (mutiny) f.put("event.triggered.sepoy_mutiny", "1857");
        return f;
    }

    public static void main(String[] args) throws Exception {
        // ------------------------------------------------ 1. THE WORLD AS IT WAS
        BranchSave.Snapshot before1857 = BranchSave.Snapshot.of(world("Bahadur Shah II", "1853", true), 1856, "main");
        BranchSave save = BranchSave.root(before1857, "the history that happened");
        BeforeChange copies = BeforeChange.empty();

        // ------------------------------------------------ 2. THE COPY BEFORE THE SPLIT (A17)
        BeforeChange.Taken copy = copies.take(BeforeChange.ChangeKind.TIMELINE_SPLIT, before1857,
                "the player is about to stop the mutiny");
        ok(copy.ok(), "a copy is taken before the split: " + copy.line());
        copies = copy.list();
        ok(copies.openOf(BeforeChange.ChangeKind.TIMELINE_SPLIT) != null, "and it is open while the split happens");

        // ------------------------------------------------ 3. THE SPLIT, SAVED AS A DIFFERENCE (G8)
        BranchSave.Snapshot onBranch = BranchSave.Snapshot.of(world("no one", "1861", false), 1861, "b1");
        save = save.branch(before1857, onBranch, 1857, List.of("pin_sepoy_mutiny"), "the mutiny was stopped");
        // Two flags changed value (the ruler and the railway) and one flag the root had is gone from the branch
        // (the mutiny, which never happened). Three differences against a world of sixty-two flags, not sixty-two.
        eq(save.get("b1").changed().size(), 2, "the branch saves the two flags it changed: "
                + save.get("b1").changed());
        eq(save.get("b1").removed(), java.util.Set.of("event.triggered.sepoy_mutiny"), "and the one it removed");
        ok(save.diff("b1", onBranch).isEmpty(), "and the cheap copy says the same as a full save of the branch");
        copies = copies.complete(copy.made().id());
        ok(copies.openOf(BeforeChange.ChangeKind.TIMELINE_SPLIT) == null, "the copy closes when the split is done");

        // ------------------------------------------------ 4. THE BRANCH IN THE TREE (G7)
        BranchTree tree = BranchTree.from(save);
        eq(tree.size(), 2, "the tree has the world and the branch");
        eq(tree.path("b1"), List.of("main", "b1"), "and the branch hangs off the real history");
        ok(tree.position("b1").contains("1 split from the real history"), "the book can say how far out you are: "
                + tree.position("b1"));
        eq(tree.pages(10).size(), 1, "and the tree fits a page");
        System.out.println("     " + tree.lines().get(1));

        // ------------------------------------------------ 5. TRAVEL, AND THE YEAR RULE
        String[] why = new String[1];
        BranchSave.Snapshot stayed = tree.travel(save, "b1", "b1", 1850, why);
        ok(stayed != null, "travelling to the branch in 1850 is possible");
        eq(stayed.activeBranch(), "main", "but in 1850 you are on the real history, because the branch is 1857's");
        ok(why[0].contains("splits in 1857"), "and the trip says so: " + why[0]);

        BranchSave.Snapshot went = tree.travel(save, "main", "b1", 1861, why);
        ok(went != null, "in 1861 the trip lands on the branch");
        eq(went.activeBranch(), "b1", "the world is on b1");
        eq(went.flags().get("dynasty.ruler.mughal"), "no one", "and the ruler is the branch's");
        ok(!went.flags().containsKey("event.triggered.sepoy_mutiny"), "and the mutiny never happened there");
        eq(went.flags().get("tech.railway"), "1861", "and the railway came late");

        BranchSave.Snapshot back = tree.travel(save, "b1", "main", 1861, why);
        eq(back.flags().get("dynasty.ruler.mughal"), "Bahadur Shah II", "and coming back restores the real ruler");
        ok(back.flags().containsKey("event.triggered.sepoy_mutiny"), "and the mutiny, which is in the record");

        // ------------------------------------------------ 6. THE WORLD ON THAT BRANCH (G6)
        PlaceRecord rec = PlaceRecord.load(gz("towns.json.gz"), gz("buildings_famous.json.gz"),
                gz("ways_works.json.gz"));
        PlaceRecord.Town delhi = rec.nearest(28.61, 77.21);
        List<BranchStory.Fact> facts = rec.facts(delhi, 25, 1861);
        BranchWorld.Plan plan = BranchWorld.plan("b1", 1861, facts, List.of(
                new BranchWorld.Statement("Red Fort", "fort", 1648, false, "the branch tore it down")));
        ok(plan.gone().size() >= 1, "the branch takes something out of the world: " + plan.gone().size());
        BranchWorld.Applied absent = BranchWorld.apply(plan, BranchWorld.absent());
        ok(!absent.clean(), "with no Terra++ not one thing reaches the ground");
        eq(absent.refused(), plan.decisions().size(), "and every decision is reported, not silently dropped");
        System.out.println("     " + plan.line());
        System.out.println("     " + absent.line());

        // ------------------------------------------------ 7. THE BOOK, AS A PLAYER SEES IT
        List<String> page = tree.pages(10).get(0);
        ok(page.size() == 2, "the book shows both branches");
        ok(copies.latestFor(BeforeChange.ChangeKind.TIMELINE_SPLIT) != null, "and the copy before the split is "
                + "still there to undo it");
        System.out.println("     " + copies.ruleLine());

        // ------------------------------------------------ 8. UNDOING THE SPLIT
        BeforeChange.Backup undoMe = copies.latestFor(BeforeChange.ChangeKind.TIMELINE_SPLIT);
        BranchSave.Snapshot undone = copies.undo(undoMe.id());
        eq(undone.flags(), before1857.flags(), "undoing the split gives back the world exactly as it was");
        eq(undone.year(), 1856, "in the year it was taken");
        eq(undone.activeBranch(), "main", "on the branch it was taken");

        // ------------------------------------------------ 9. THE THREE RULES, TOGETHER
        // A branch cannot be entered without a save, a copy cannot be taken twice for one change, and a timed copy
        // is not a before-change copy. In one chain, each depends on the others holding.
        BranchSave bare = BranchSave.root(before1857, "the history that happened");
        BranchTree bareTree = BranchTree.of(List.of(
                new BranchTree.Node("main", null, 1700, "", "the history that happened", List.of()),
                new BranchTree.Node("b1", "main", 1857, "", "the mutiny was stopped", List.of("pin_sepoy_mutiny"))));
        String[] why2 = new String[1];
        ok(bareTree.travel(bare, "main", "b1", 1900, why2) == null,
                "a branch in the tree but not in the save cannot be entered");
        ok(why2[0].contains("no save for b1"), "and the refusal says which save: " + why2[0]);
        ok(BeforeChange.empty().latestFor(BeforeChange.ChangeKind.TIMELINE_SPLIT) == null,
                "a world whose only copies are the timed ones cannot undo a split");

        // ------------------------------------------------ 10. NOTHING WAS INVENTED
        boolean everyDecisionFromTheRecord = true;
        for (BranchWorld.Decision d : plan.decisions()) {
            if (d.record() == null || d.record().isEmpty()) everyDecisionFromTheRecord = false;
        }
        ok(everyDecisionFromTheRecord, "every thing the world is told about comes from a row of the record");
        for (BranchWorld.Unplaced u : plan.unplaced()) {
            ok(u.why().contains("no row") || u.why().contains("holds 2"), "an unplaced statement says why: "
                    + u.line());
        }

        System.out.println("\nStep 51 part 6: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
