/* Step 55 part 4 (H6 second half + the H4 tie): the papers and book of one universe, read through its
   rule set. The claim: every surface read through rules names EVERY rule applied; four kinds bend what a
   reader sees and three are what the scan proves - and the reading names those too, never staying
   silent. The guardrail travels with the words. */
import com.eternalengine.story.UniverseBook;
import com.eternalengine.story.UniverseBook.Printed;
import com.eternalengine.story.UniverseBook.Reading;
import com.eternalengine.story.UniverseStory;
import com.eternalengine.timeline.BrokenLogic;
import com.eternalengine.timeline.Provenance;

import java.util.List;

public class Step55BookProbe {
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
        // ------------------------------------------------ 1. THE PAPER
        Printed p = UniverseBook.paper("u-cuzco-1576", "Cuzco", 1576,
                List.of("the walls are rebuilt", "the market meets again"));
        ok(p.ok(), "a paper prints: " + (p.ok() ? "" : p.refused()));
        eq(p.sheet().stories().size(), 2, "with its two stories");
        ok(p.sheet().page().get(0).contains("[recorded]"), "and a computed mark: "
                + p.sheet().page().get(0));
        ok(p.sheet().page().get(0).contains("in u-cuzco-1576"), "naming its universe");

        // The guardrail travels with the words: a guarded story is refused BY NAME and the rest prints.
        Printed future = UniverseBook.paper("u-cuzco-1576", "Cuzco", 2200,
                List.of("the sea is still high", "the war goes on"));
        ok(future.ok(), "the paper still prints");
        eq(future.sheet().stories(), List.of("the sea is still high"), "without the guarded story");
        ok(future.refused().get(0).contains("says \"war\""), "and says why: " + future.refused());
        eq(future.sheet().mark(), "projected", "marked projected");

        Printed noU = UniverseBook.paper("", "Cuzco", 1576, List.of("x"));
        ok(!noU.ok(), "a paper with no universe is refused");
        ok(noU.refused().get(0).contains("name the universe"), "in words: " + noU.refused());

        // ------------------------------------------------ 2. THE BOOK
        UniverseStory story = UniverseStory.of("u-cuzco-1576");
        story.add(1576, "Cuzco", "the fall is recorded in the book", Provenance.OBSERVED, "");
        story.name("Huayna Capac", 1464, 1527, "ruler", Provenance.OBSERVED, "");
        List<String> page = UniverseBook.book("u-cuzco-1576", "Cuzco", 1576,
                List.of("sea level 63 -> 120"), story);
        eq(page.size(), 4, "the book page has header, change, history, person (and no projection note inside the record)");
        ok(page.get(0).contains("the book of Cuzco, 1576, in u-cuzco-1576 [recorded]"),
                "its header: " + page.get(0));
        ok(page.get(1).contains("broke off from its parent: sea level 63 -> 120"),
                "its change: " + page.get(1));
        ok(page.get(3).contains("Huayna Capac"), "and its people: " + page.get(3));
        List<String> futurePage = UniverseBook.book("u-cuzco-1576", "Cuzco", 2200, List.of(), story);
        ok(futurePage.get(futurePage.size() - 1).contains("projection"),
                "a projected page carries the projection note: " + futurePage.get(futurePage.size() - 1));
        List<String> empty = UniverseBook.book("u-nowhere", "Lhasa", 1000, null, story);
        ok(empty.contains("  nothing is recorded here yet"), "and an empty book says so, never fills "
                + "itself: " + empty);

        // ------------------------------------------------ 3. READING THROUGH THE RULES
        Reading clean = Reading.through(BrokenLogic.earth());
        eq(clean.applied().size(), 0, "the unbroken world reads straight");
        eq(clean.history(List.of("first", "second")), List.of("first", "second"),
                "and changes no order");
        eq(clean.words("cat"), "cat", "and no words");
        ok(clean.line().contains("unbroken world"), "in words: " + clean.line());

        BrokenLogic.Made bent = BrokenLogic.make(List.of(
                BrokenLogic.Kind.TIME_BACKWARDS, BrokenLogic.Kind.SCRAMBLED_LANGUAGES,
                BrokenLogic.Kind.MONEY_UPSIDE_DOWN, BrokenLogic.Kind.ERAS_MIXED,
                BrokenLogic.Kind.OUT_OF_ORDER, BrokenLogic.Kind.DOUBLES,
                BrokenLogic.Kind.EFFECTS_BEFORE_CAUSES), "the rupture of 2026");
        Reading read = Reading.through(bent.spec());
        eq(read.applied().size(), 7, "every rule is named, all seven");
        eq(read.history(List.of("the fall", "the rebuilding")),
                List.of("the rebuilding", "the fall"), "backwards time reads newest first");
        eq(read.words("Cuzco"), "Cazcu", "scrambled languages shifts vowels one along (u->a, o->u)");
        eq(read.money("4"), "4 (read upside down: 0.25)", "money upside down reads the value inverted");
        eq(read.era("the knight rides"), "from another age: the knight rides",
                "eras mixed marks the line");
        ok(read.line().contains("bends the reading order") && read.line().contains("bends the words")
                        && read.line().contains("bends the cause graph")
                        && read.line().contains("bends the person register"),
                "and the reading names ALL of them, even the three a reader cannot see: " + read.line());
        for (String a : read.applied()) System.out.println("     " + a);
        System.out.println("     " + read.line());

        // A reading through no rules never lies about what it did.
        eq(Reading.through(null).applied().size(), 0, "and no rule set reads straight too");

        // ------------------------------------------------ 4. THE RULE
        System.out.println("     " + UniverseBook.ruleLine());
        ok(UniverseBook.ruleLine().contains("names every rule applied"), "the rule keeps the naming");
        ok(UniverseBook.ruleLine().contains("staying silent"), "and the no-silence rule");

        System.out.println("\nStep 55 part 4: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
