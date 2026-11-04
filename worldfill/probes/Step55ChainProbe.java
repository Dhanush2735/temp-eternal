/* Step 55 part 5: the chain, end to end. Each class passed its own probe; only the chain proves the game.
   The chain: a universe cracks open (step 54's one call) -> its rule set is made (H4) -> its own history
   and people are written (H6) -> its papers and book are printed -> every surface is read through the
   rules, naming every rule applied -> the guardrail refuses by name -> the scan proves what it can and
   says silence about the rest proves nothing. */
import com.eternalengine.player.Permissions.Decision;
import com.eternalengine.story.UniverseBook;
import com.eternalengine.story.UniverseBook.Printed;
import com.eternalengine.story.UniverseBook.Reading;
import com.eternalengine.story.UniverseStory;
import com.eternalengine.terrabridge.BrokenPhysics;
import com.eternalengine.terrabridge.LandSpec;
import com.eternalengine.terrabridge.LandSpec.Mirror;
import com.eternalengine.timeline.BeforeChange;
import com.eternalengine.timeline.BrokenLogic;
import com.eternalengine.timeline.BrokenLogic.Entry;
import com.eternalengine.timeline.BrokenLogic.Kind;
import com.eternalengine.timeline.BranchSave;
import com.eternalengine.timeline.RuptureEngine;
import com.eternalengine.timeline.RuptureEngine.Verdict;
import com.eternalengine.timeline.Ruptures;
import com.eternalengine.timeline.Provenance;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Step55ChainProbe {
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
        // ------------------------------------------------ 1. A UNIVERSE CRACKS OPEN (STEP 54)
        Ruptures worlds = Ruptures.empty();
        worlds.declare("earth", null, LandSpec.earth(), -3000, "the land as Terra++ makes it");
        BeforeChange copies = BeforeChange.empty();
        LandSpec.Made other = LandSpec.make(120, -2032, 2032, true, Mirror.EAST_WEST, "the rupture of 2526");
        Verdict made = RuptureEngine.rupture("the year 2526", "u-reversed-2526", "earth", other.spec(),
                null, 2526, "the world cracked and its logic with it", copies,
                BranchSave.Snapshot.of(Map.of("state.world", "2526"), 2526, "main"), worlds, null);
        copies = made.copiesAfter();
        ok(made.ok(), "the universe exists: " + made.decision().why());
        ok(made.line().contains("could not be checked"), "and its land is honestly unchecked");
        eq(worlds.find("u-reversed-2526").land().seaLevel(), 120, "with the land it asked for");

        // ------------------------------------------------ 2. ITS RULE SET (H4)
        BrokenLogic.Made rules = BrokenLogic.make(List.of(
                Kind.TIME_BACKWARDS, Kind.SCRAMBLED_LANGUAGES, Kind.MONEY_UPSIDE_DOWN,
                Kind.ERAS_MIXED, Kind.OUT_OF_ORDER, Kind.DOUBLES, Kind.EFFECTS_BEFORE_CAUSES),
                "the rupture of 2526");
        ok(rules.ok(), "and its logic is broken in all seven ways: " + rules.spec().describe());
        eq(BrokenLogic.changesFromEarth(rules.spec()).size(), 7, "seven broken kinds, each naming what "
                + "it bends");
        BrokenLogic.Reported said = new BrokenLogic.Reported(
                java.util.EnumSet.allOf(Kind.class), "u-reversed-2526");
        eq(BrokenLogic.diff(rules.spec(), said).size(), 0, "the universe reports what was asked");
        BrokenLogic.Reported wrong = new BrokenLogic.Reported(
                java.util.EnumSet.of(Kind.TIME_BACKWARDS), "u-reversed-2526");
        eq(BrokenLogic.diff(rules.spec(), wrong).size(), 6, "and a universe that under-reports is named "
                + "six times");

        // ------------------------------------------------ 3. ITS OWN HISTORY AND PEOPLE (H6)
        UniverseStory story = UniverseStory.of("u-reversed-2526");
        ok(story.add(1576, "Cuzco", "the fall is recorded in the book", Provenance.OBSERVED, "").ok(),
                "its history runs from 1576");
        ok(story.add(1857, "Delhi", "the mutiny year is recorded in the book", Provenance.OBSERVED, "")
                .ok(), "through 1857");
        ok(story.add(2026, "Hyderabad", "the city is recorded as it is", Provenance.OBSERVED, "").ok(),
                "to the end of the record in 2026");
        ok(story.add(2200, "Hyderabad", "the sea is still high", Provenance.MODELLED, "").ok(),
                "and one projection continuing a state");
        UniverseStory.LineWritten guard = story.add(2200, "Hyderabad", "the king rules the drowned "
                + "streets", Provenance.MODELLED, "");
        ok(!guard.ok(), "but a projection naming a ruler is refused");
        ok(guard.refused().get(0).contains("says \"king\""), "by name: " + guard.refused());
        ok(story.name("The Traveller", 2100, null, "traveller", Provenance.AUTHORED, "Sam").ok(),
                "a player may author a person the record does not hold");
        UniverseStory.PersonNamed projected = story.name("The Heir", 2100, null, "heir",
                Provenance.MODELLED, "");
        ok(!projected.ok() && projected.refused().get(0).contains("never projected"),
                "but nobody is ever projected");

        // ------------------------------------------------ 4. ITS PAPERS AND BOOK, READ THROUGH THE RULES
        Printed paper = UniverseBook.paper("u-reversed-2526", "Hyderabad", 2200,
                List.of("the sea is still high", "the war goes on"));
        eq(paper.sheet().stories(), List.of("the sea is still high"),
                "the paper of 2200 prints only the lawful story");
        ok(paper.refused().get(0).contains("says \"war\""), "and names the one it dropped");
        List<String> page = UniverseBook.book("u-reversed-2526", "Hyderabad", 2200,
                List.of("sea level 63 -> 120", "mirrored east-west"), story);
        ok(page.get(0).contains("[projected]"), "the book of 2200 is marked projected: " + page.get(0));
        ok(page.get(page.size() - 1).contains("projection"), "and carries the projection note");
        ok(page.get(1).contains("broke off from its parent"), "and what changed here: " + page.get(1));

        Reading read = Reading.through(rules.spec());
        eq(read.history(List.of("the fall", "the mutiny", "the city")),
                List.of("the city", "the mutiny", "the fall"), "history reads newest first");
        eq(read.words("Hyderabad"), "Hydirebed", "the words are scrambled one vowel along (e->i, a->e)");
        eq(read.money("4"), "4 (read upside down: 0.25)", "and the money is upside down");
        eq(read.applied().size(), 7, "and the reading names all seven rules, every time");
        for (String line : read.applied()) System.out.println("     " + line);
        System.out.println("     " + read.line());

        // ------------------------------------------------ 5. THE SCAN PROVES THREE AND SAYS NOTHING ABOUT FOUR
        BrokenLogic.Scan scan = BrokenLogic.scan(List.of(
                new Entry("e1", 2200, "the flood", List.of("e2")),
                new Entry("e2", 2100, "the drought", List.of("e1")),
                new Entry("e1", 2200, "the flood", List.of("e2"))));
        eq(scan.proved().size(), 3, "the bent entries prove the three provable kinds");
        ok(scan.line().contains("cause each other"), "including the cause loop");
        eq(scan.notProvable().size(), 4, "and the four declared kinds are named as not provable");
        for (String line : List.of(scan.line())) System.out.println("     scan: " + line);
        for (String line : UniverseBook.book("u-reversed-2526", "Delhi", 1857, null, story)) {
            System.out.println("     " + line);
        }

        System.out.println("     " + BrokenLogic.ruleLine());
        System.out.println("     " + UniverseStory.ruleLine());
        System.out.println("     " + UniverseBook.ruleLine());

        System.out.println("\nStep 55 part 5: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
