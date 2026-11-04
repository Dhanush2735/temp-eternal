/* Step 51 part 3 (G7): the timeline tree in the book, and travel between timelines.
   The claim: the tree can be walked both ways, a branch cannot be entered before it split, a branch with no save
   cannot be entered at all, and the book draws what is there rather than what would look tidy. */
import com.eternalengine.timeline.BranchSave;
import com.eternalengine.timeline.BranchTree;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

public class Step51TreeProbe {
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

    static Map<String, String> flags(String... kv) {
        Map<String, String> f = new TreeMap<>();
        for (int i = 0; i < kv.length; i += 2) f.put(kv[i], kv[i + 1]);
        return f;
    }

    public static void main(String[] args) {
        // A world: the real history plus three branches, one of them two deep.
        BranchSave.Snapshot main = BranchSave.Snapshot.of(flags(
                "event.triggered.sepoy_mutiny", "1857", "dynasty.ruler.mughal", "Bahadur Shah II",
                "tech.flag_rail", "1853", "climate.flag_year", "cold"), 1700, "main");
        BranchSave save = BranchSave.root(main, "the history that happened");

        BranchSave.Snapshot b1 = BranchSave.Snapshot.of(flags(
                "event.triggered.sepoy_mutiny", "1857", "dynasty.ruler.mughal", "no one",
                "tech.flag_rail", "1853", "climate.flag_year", "cold", "timeline.mutiny", "stopped"), 1857, "b1");
        save = save.branch(main, b1, 1857, List.of("pin_sepoy_mutiny"), "the mutiny was stopped");

        BranchSave.Snapshot b2 = BranchSave.Snapshot.of(flags(
                "event.triggered.sepoy_mutiny", "1857", "dynasty.ruler.mughal", "no one",
                "tech.flag_rail", "1861", "climate.flag_year", "cold", "timeline.mutiny", "stopped"), 1861, "b2");
        save = save.branch(b1, b2, 1861, List.of(), "the railway came late instead");

        BranchSave.Snapshot b1b = BranchSave.Snapshot.of(flags(
                "event.triggered.sepoy_mutiny", "1857", "dynasty.ruler.mughal", "Bahadur Shah II",
                "tech.flag_rail", "1853", "climate.flag_year", "cold", "timeline.other", "true"), 1858, "b1b");
        save = save.branch(main, b1b, 1858, List.of(), "a different fork from the same history");

        BranchTree tree = BranchTree.from(save);
        List<String> drawn = tree.lines();
        for (String l : drawn) System.out.println("     " + l);

        // ------------------------------------------------ 1. THE TREE WALKS BOTH WAYS
        eq(tree.size(), 4, "four branches, the root included");
        eq(tree.roots(), List.of("main"), "one root");
        eq(tree.childrenOf("main").size(), 2, "the root has two children: " + tree.childrenOf("main"));
        eq(tree.childrenOf("b1"), List.of("b2"), "b1 has one");
        eq(tree.childrenOf("b2").size(), 0, "and b2 has none");
        eq(tree.path("b2"), List.of("main", "b1", "b2"), "the path to the deepest branch is root first");
        eq(tree.depth("main"), 0, "the root is depth 0");
        eq(tree.depth("b1"), 1, "a branch off the root is depth 1");
        eq(tree.depth("b2"), 2, "and one off that is 2");
        ok(!tree.broken("b2"), "the deepest branch is connected");
        eq(tree.orphans().size(), 0, "and nothing is orphaned");

        // ------------------------------------------------ 2. THE BOOK'S PAGES
        eq(drawn.size(), 4, "four lines for four branches");
        ok(drawn.get(0).startsWith("main"), "the root is drawn first");
        ok(drawn.get(1).startsWith("  - b1") || drawn.get(1).startsWith("  - b1b"), "then the children, indented: "
                + drawn.get(1));
        ok(drawn.get(2).startsWith("    - b2"), "and the grandchild is indented twice: " + drawn.get(2));
        ok(drawn.get(0).contains("1700"), "every line carries its year");
        List<List<String>> pages = tree.pages(3);
        eq(pages.size(), 2, "four lines over three to a page is two pages");
        List<String> flat = new ArrayList<>();
        for (List<String> p : pages) flat.addAll(p);
        eq(flat, drawn, "and every line lands on a page, in order");
        eq(tree.pages(100).size(), 1, "a page big enough holds it all");

        // ------------------------------------------------ 3. WHERE YOU ARE
        String mainPos = tree.position("main");
        ok(mainPos.contains("the history that happened"), "the root says what it is: " + mainPos);
        String bPos = tree.position("b2");
        System.out.println("     " + bPos);
        ok(bPos.contains("split from b1"), "a branch names its parent");
        ok(bPos.contains("1861"), "and the year it split");
        ok(bPos.contains("because the railway came late"), "and why, in the words of the log");
        ok(bPos.contains("2 splits from the real history"), "and how far from the real history it is");
        ok(tree.position("nothing").contains("no branch this book knows"), "an unknown branch is said to be unknown");

        // ------------------------------------------------ 4. THE RULE: NOT BEFORE IT SPLIT
        BranchTree.Trip in1850 = tree.plan(save, "main", "b1", 1850);
        ok(in1850.possible(), "a trip to b1 in 1850 is possible");
        ok(in1850.redirected(), "but not to b1: the mutiny was stopped in 1857");
        eq(in1850.standOn(), "main", "so in 1850 you stand on the real history");
        System.out.println("     " + in1850.line());
        ok(in1850.why().contains("splits in 1857"), "and the trip says why: " + in1850.why());

        BranchTree.Trip in1858 = tree.plan(save, "main", "b1", 1858);
        eq(in1858.standOn(), "b1", "after the split you stand on the branch");
        ok(!in1858.redirected(), "and you get the branch you asked for");
        ok(in1858.line().contains("by way of main -> b1"), "by way of the chain: " + in1858.line());

        BranchTree.Trip deep1850 = tree.plan(save, "main", "b2", 1850);
        eq(deep1850.standOn(), "main", "asking for a grandchild in 1850 puts you on the root");
        BranchTree.Trip deep1858 = tree.plan(save, "main", "b2", 1858);
        eq(deep1858.standOn(), "b1", "in 1858 on its parent, because b2 did not split until 1861");
        BranchTree.Trip deep1862 = tree.plan(save, "main", "b2", 1862);
        eq(deep1862.standOn(), "b2", "and in 1862 on b2 itself");

        // ------------------------------------------------ 5. TRAVEL PUTS THE WORLD BACK
        String[] why = new String[1];
        BranchSave.Snapshot went = tree.travel(save, "main", "b2", 1862, why);
        ok(went != null, "the trip happens: " + why[0]);
        eq(went.activeBranch(), "b2", "the world is on b2");
        eq(went.year(), 1862, "in the year asked for");
        eq(went.flags().get("tech.flag_rail"), "1861", "and the railway is the branch's railway, not the real one");
        eq(went.flags().get("dynasty.ruler.mughal"), "no one", "and the dynasty is the branch's too");
        ok(went.flags().containsKey("timeline.mutiny"), "and the branch's own flag came with it");

        BranchSave.Snapshot back = tree.travel(save, "b2", "main", 1862, why);
        eq(back.activeBranch(), "main", "and coming back lands on the real history");
        eq(back.flags().get("tech.flag_rail"), "1853", "with the real railway");
        eq(back.flags().get("dynasty.ruler.mughal"), "Bahadur Shah II", "and the real ruler");
        ok(!back.flags().containsKey("timeline.mutiny"), "and the branch's own flag is gone, because it is the "
                + "branch's and not the world's");

        // A trip to a branch with no save is refused.
        BranchSave noB1b = BranchSave.root(main, "the history that happened");
        BranchTree.Trip noSave = tree.plan(noB1b, "main", "b1b", 1900);
        ok(!noSave.possible(), "a branch with no save cannot be entered");
        ok(noSave.why().contains("no save for b1b"), "and the trip says which save is missing: " + noSave.why());
        String[] why2 = new String[1];
        ok(tree.travel(noB1b, "main", "b1b", 1900, why2) == null, "and nothing is restored");

        // And a branch that does not exist is refused.
        BranchTree.Trip nowhere = tree.plan(save, "main", "atlantis", 1900);
        ok(!nowhere.possible(), "a branch that does not exist cannot be asked for");
        ok(nowhere.why().contains("no branch atlantis"), "and it says so: " + nowhere.why());

        // ------------------------------------------------ 6. A BROKEN TREE IS DRAWN AS BROKEN
        BranchTree holed = BranchTree.of(List.of(
                new BranchTree.Node("main", null, 1700, "", "", List.of()),
                new BranchTree.Node("lost", "ghost", 1800, "", "its parent is not here", List.of())));
        eq(holed.orphans().size(), 1, "a branch whose parent is missing is reported");
        ok(holed.lines().get(holed.lines().size() - 1).startsWith("?"), "and drawn with a question mark rather "
                + "than left out: " + holed.lines());
        ok(holed.broken("lost"), "it cannot be walked to a root");
        eq(holed.depth("lost"), -1, "so its depth is not a number");
        BranchTree.Trip toLost = holed.plan(BranchSave.root(main, ""), "main", "lost", 1900);
        ok(!toLost.possible(), "and a trip to it is refused");

        BranchTree looped = BranchTree.of(List.of(
                new BranchTree.Node("a", "b", 1800, "", "", List.of()),
                new BranchTree.Node("b", "a", 1801, "", "", List.of())));
        eq(looped.roots().size(), 0, "a tree that loops has no root");
        ok(looped.broken("a"), "and neither branch can be walked");
        // The first version of BranchTree.lines() drew NOTHING for a looping tree, because it started from the
        // roots and there were none. A broken save that looks like an empty one is worse than one that looks
        // broken, so the probe demands a line for each and the words that say why.
        eq(looped.lines().size(), 2, "and both are drawn even though no root reaches them: " + looped.lines());
        ok(looped.lines().get(0).startsWith("?"), "with a question mark: " + looped.lines().get(0));
        ok(looped.lines().get(0).contains("loops"), "and the reason: " + looped.lines().get(0));

        checks++;
        try {
            BranchTree.of(List.of(new BranchTree.Node("x", null, 1, "", "", List.of()),
                    new BranchTree.Node("x", null, 2, "", "", List.of())));
            failed++;
            System.out.println("  FAIL two branches with one id were allowed");
        } catch (IllegalArgumentException e) {
            // what we wanted
        }
        checks++;
        try {
            new BranchTree.Node("", null, 1, "", "", List.of());
            failed++;
            System.out.println("  FAIL a branch with no id was allowed");
        } catch (IllegalArgumentException e) {
            // what we wanted
        }

        // ------------------------------------------------ 7. THE SCREEN LINES
        System.out.println("     " + tree.ruleLine());
        ok(tree.ruleLine().contains("3 of them forks"), "the rule line counts forks and not branches");
        ok(tree.ruleLine().contains("only from a year after it split"), "and states the rule a trip obeys");
        ok(BranchTree.of(List.of()).ruleLine().contains("No branches"), "an empty tree says so");
        ok(tree.get("b1").line().contains("1 pins stopped"), "a branch's line says how many pins it stopped");
        ok(tree.get("b1").line().contains("1857"), "and when it split");

        System.out.println("\nStep 51 part 3: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
