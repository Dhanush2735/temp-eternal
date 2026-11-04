/* Step 51 part 5 (G6 and A12): does the world follow the timeline.
   The claim: what stands on a branch is computed here from the record and the branch's own statements; what is
   DRAWN is Terra++'s job and goes through one narrow seam; a statement that cannot be placed is reported, not
   dropped; two things with one name are refused rather than guessed; and a world with no Terra++ says so instead
   of pretending to have obeyed. */
import com.eternalengine.story.BranchStory;
import com.eternalengine.story.PlaceRecord;
import com.eternalengine.terrabridge.BranchWorld;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.zip.GZIPInputStream;

public class Step51WorldProbe {
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
        return new GZIPInputStream(Step51WorldProbe.class.getResourceAsStream(
                "/data/eternalengine/eternal/history/" + n));
    }

    /** A port that remembers what it was told, which is what a probe can have instead of Terra++. */
    static final class Recorder implements BranchWorld.Port {
        final List<String> removed = new ArrayList<>();
        final List<String> added = new ArrayList<>();
        final java.util.Set<String> refuse = new java.util.HashSet<>();

        @Override
        public boolean remove(BranchWorld.Decision d) {
            if (refuse.contains(d.name())) return false;
            removed.add(d.name());
            return true;
        }

        @Override
        public boolean add(BranchWorld.Decision d) {
            if (refuse.contains(d.name())) return false;
            added.add(d.name());
            return true;
        }

        @Override
        public String describe() {
            return "a recorder, standing in for Terra++";
        }
    }

    public static void main(String[] args) throws Exception {
        PlaceRecord rec = PlaceRecord.load(gz("towns.json.gz"), gz("buildings_famous.json.gz"),
                gz("ways_works.json.gz"));
        double lat = 28.61, lon = 77.21;                 // Delhi
        PlaceRecord.Town delhi = rec.nearest(lat, lon);
        List<BranchStory.Fact> facts = rec.facts(delhi, 25, 1900);
        ok(facts.size() > 3, "the record has rows near Delhi by 1900: " + facts.size());

        // ------------------------------------------------ 1. A BRANCH THAT SAYS NOTHING CHANGES NOTHING
        BranchWorld.Plan quiet = BranchWorld.plan("main", 1900, facts, List.of());
        // NOT "everything stands": the record ends some of its own rows before 1900, and those do not stand on
        // any branch. The first version of this probe asserted that nothing was gone, which is a claim about the
        // data that the data disagrees with.
        ok(quiet.gone().size() > 0, "the record ends some of its own rows before 1900: " + quiet.gone().size());
        for (BranchWorld.Decision d : quiet.gone()) {
            ok(d.why().contains("the record itself ends it"),
                    "and every one of those is the record's doing and not a branch's: " + d.name());
        }
        eq(quiet.gone().size() + quiet.standing().size(), quiet.decisions().size(), "every row is decided one way or "
                + "the other");
        eq(quiet.unplaced().size(), 0, "and with no statements, nothing is unplaced");
        System.out.println("     " + quiet.line());

        // ------------------------------------------------ 2. A BRANCH TAKES SOMETHING AWAY
        BranchStory.Fact first = facts.get(0);
        BranchWorld.Statement gone = new BranchWorld.Statement(first.name(), first.kind(), first.year(), false,
                "the branch stopped it");
        BranchWorld.Plan one = BranchWorld.plan("b1", 1900, facts, List.of(gone));
        eq(one.gone().size(), quiet.gone().size() + 1, "one more thing does not stand on this branch than on the "
                + "real history");
        boolean named = false;
        for (BranchWorld.Decision d : one.gone()) {
            if (d.name().equals(first.name())) named = true;
        }
        ok(named, "and it is the one the branch named: " + first.name());
        eq(one.standing().size(), quiet.standing().size() - 1, "the rest still stand, less the one");
        ok(one.gone().get(0).why().contains("the branch stopped it"), "and the reason is the branch's own");
        System.out.println("     " + one.gone().get(0).line());

        // ------------------------------------------------ 3. A STATEMENT THE RECORD CANNOT PLACE
        BranchWorld.Statement invented = new BranchWorld.Statement("a bridge that never was", "bridge", 1850, false,
                "the branch's own invention");
        BranchWorld.Plan withInvented = BranchWorld.plan("b1", 1900, facts, List.of(gone, invented));
        eq(withInvented.unplaced().size(), 1, "a statement with no row behind it is reported");
        ok(withInvented.unplaced().get(0).name().equals("a bridge that never was"), "and named");
        ok(withInvented.unplaced().get(0).why().contains("no row by that name"), "with the reason: "
                + withInvented.unplaced().get(0).line());
        eq(withInvented.gone().size(), one.gone().size(), "and it does not silently take something else's place");

        // ------------------------------------------------ 4. TWO THINGS WITH ONE NAME ARE A QUESTION
        List<BranchStory.Fact> twins = new ArrayList<>();
        twins.add(new BranchStory.Fact(1860, null, "the station", "station", "ways_works"));
        twins.add(new BranchStory.Fact(1870, null, "the station", "station", "ways_works"));
        twins.add(new BranchStory.Fact(1880, null, "the mill", "mill", "ways_works"));
        BranchWorld.Plan ambiguous = BranchWorld.plan("b1", 1900, twins,
                List.of(new BranchWorld.Statement("the station", "station", 1860, false, "closed early")));
        eq(ambiguous.unplaced().size(), 1, "a name the record has twice is refused, not guessed");
        ok(ambiguous.unplaced().get(0).why().contains("holds 2 things"), "and the refusal says how many: "
                + ambiguous.unplaced().get(0).why());
        eq(ambiguous.gone().size(), 0, "nothing is taken away on a guess");
        eq(ambiguous.standing().size(), 3, "and everything stands, waiting for an answer");

        // ------------------------------------------------ 5. THE RECORD'S OWN END YEAR NEEDS NO STATEMENT
        List<BranchStory.Fact> ended = List.of(new BranchStory.Fact(1700, 1800, "the old fort", "fort",
                "buildings_famous"));
        BranchWorld.Plan past = BranchWorld.plan("main", 1900, ended, List.of());
        eq(past.gone().size(), 1, "a thing the record itself ends before this year does not stand");
        ok(past.gone().get(0).why().contains("the record itself ends it"), "and the record gets the credit: "
                + past.gone().get(0).why());

        // A row from the future of the story is not in the plan at all.
        List<BranchStory.Fact> future = List.of(new BranchStory.Fact(1950, null, "a tower", "tower", "ways_works"));
        eq(BranchWorld.plan("main", 1900, future, List.of()).decisions().size(), 0, "a row after the year does not stand");

        // ------------------------------------------------ 6. HANDING IT TO THE WORLD
        Recorder port = new Recorder();
        BranchWorld.Applied applied = BranchWorld.apply(one, port);
        ok(applied.clean(), "the port accepts what it is given");
        eq(applied.removed(), one.gone().size(), "every thing the branch does not have is taken away");
        eq(applied.added(), one.standing().size(), "and every thing it does have is put in place");
        ok(port.removed.contains(first.name()), "and the port was actually told");
        System.out.println("     " + applied.line() + " (" + port.describe() + ")");

        Recorder stubborn = new Recorder();
        stubborn.refuse.add(first.name());
        BranchWorld.Applied refused = BranchWorld.apply(one, stubborn);
        ok(!refused.clean(), "a refusal is not clean");
        eq(refused.refused(), 1, "one refusal counted");
        ok(refused.log().get(0).contains("refused to take away"), "and logged in words: " + refused.log().get(0));

        // ------------------------------------------------ 7. NO TERRAPLUSPLUS MEANS NO PRETENDING
        BranchWorld.Applied noWorld = BranchWorld.apply(one, BranchWorld.absent());
        ok(!noWorld.clean(), "with no Terra++, nothing is clean");
        eq(noWorld.removed(), 0, "nothing is taken away");
        eq(noWorld.refused(), one.decisions().size(), "and every single decision is reported as refused");
        ok(BranchWorld.absent().describe().contains("Terra++ is not connected"),
                "and the port says why: " + BranchWorld.absent().describe());

        checks++;
        try {
            BranchWorld.apply(null, port);
            failed++;
            System.out.println("  FAIL a plan of null was applied");
        } catch (IllegalArgumentException e) {
            // what we wanted
        }
        checks++;
        try {
            BranchWorld.apply(one, null);
            failed++;
            System.out.println("  FAIL a port of null was applied to");
        } catch (IllegalArgumentException e) {
            // what we wanted
        }

        // ------------------------------------------------ 8. THE SCREEN LINES
        System.out.println("     " + BranchWorld.ruleLine());
        ok(BranchWorld.ruleLine().contains("Terra++ draws it"), "the rule line says who draws what");
        ok(one.line().contains("could not be placed"), "the plan's own line reports what it could not place: "
                + one.line());
        ok(BranchWorld.byKind(one).containsKey(first.kind()), "the plan can be counted by kind");
        eq(BranchWorld.byKind(one).get(first.kind()), 1, "one thing of that kind gone");

        // ------------------------------------------------ 9. LOWER CASE, TRIMMED, AND NOTHING ELSE
        List<BranchStory.Fact> casing = List.of(new BranchStory.Fact(1860, null, "The Mill", "mill", "ways_works"));
        BranchWorld.Plan caseInsensitive = BranchWorld.plan("b1", 1900, casing,
                List.of(new BranchWorld.Statement("  the mill  ", "mill", 1860, false, "")));
        eq(caseInsensitive.gone().size(), 1, "a name matches whatever its case, once trimmed");
        BranchWorld.Plan substring = BranchWorld.plan("b1", 1900, casing,
                List.of(new BranchWorld.Statement("the", "mill", 1860, false, "")));
        eq(substring.unplaced().size(), 1, "but a fragment of a name matches nothing");
        eq(substring.gone().size(), 0, "and takes nothing away");

        System.out.println("\nStep 51 part 5: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
