/* Step 53 part 6: the chain, end to end. Each class passed its own probe; only the chain proves the game.
   The chain: a dated thing out of the record -> an attempt that is refused and sent to a branch -> the branch
   taken, cleanly -> a force that breaks it and books its paradox -> the five kinds tested against real years
   -> Terra++'s buildings on the same counter -> and a rebuild that brings it down. */
import com.eternalengine.player.Permissions.Actor;
import com.eternalengine.player.WhoYouAre;
import com.eternalengine.story.BranchStory;
import com.eternalengine.story.PlaceRecord;
import com.eternalengine.timeline.BranchSave;
import com.eternalengine.timeline.FixedPoints;
import com.eternalengine.timeline.Paradox;
import com.eternalengine.timeline.ParadoxEngine;
import com.eternalengine.timeline.ParadoxEngine.Verdict;
import com.eternalengine.timeline.Stress;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.zip.GZIPInputStream;

public class Step53ChainProbe {
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
        return new GZIPInputStream(Step53ChainProbe.class.getResourceAsStream(
                "/data/eternalengine/eternal/history/" + n));
    }

    public static void main(String[] args) throws Exception {
        Actor ada = Actor.of("Ada", true);

        // ------------------------------------------------ 1. THE RECORD, IN ITS OWN PLACE AND YEAR
        PlaceRecord rec = PlaceRecord.load(gz("towns.json.gz"), gz("buildings_famous.json.gz"),
                gz("ways_works.json.gz"));
        PlaceRecord.Town delhi = rec.nearest(28.61, 77.21);
        List<BranchStory.Fact> facts = rec.facts(delhi, 25, 1857);
        String fortName = null;
        int fortYear = 0;
        for (BranchStory.Fact f : facts) {
            if (f.name().toLowerCase(java.util.Locale.ROOT).contains("red fort")) {
                fortName = f.name();
                fortYear = f.year();
            }
        }
        ok(fortName != null, "the record holds the Red Fort for Delhi by 1857");
        ok(fortYear > 1500 && fortYear < 1700, "dated in its own century: " + fortYear);

        try (InputStream in = gz("technology_atlas.json.gz")) {
            JsonObject root = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8))
                    .getAsJsonObject();
            int techs = root.getAsJsonArray("techs").size();
            eq(techs, 130, "and the technology atlas holds its 130 origin years");
        }

        // ------------------------------------------------ 2. THE REGISTER, DRAWN FROM THE RECORD
        FixedPoints pts = FixedPoints.empty();
        ok(pts.declare(new FixedPoints.Point("red-fort", fortYear, fortName + " of Delhi",
                "the city's centuries lean on it", 5)).allowed(),
                "a fixed point declared from a real dated row");
        Stress stress = Stress.empty();

        // ------------------------------------------------ 3. THE ATTEMPT IS REFUSED AND SENT TO A BRANCH
        Verdict tried = ParadoxEngine.attemptFixed(pts, stress, "red-fort", "tear it down in place");
        ok(!tried.ok(), "tearing it down in place is refused");
        ok(tried.decision().why().contains("take the change to a timeline branch"),
                "and the safe way out is named first");
        eq(stress.total(), 0, "a refused attempt costs nothing");

        // The branch path, with step 51's own save machinery: the real history survives what-if.
        Map<String, String> world = new TreeMap<>();
        world.put("place.delhi.red_fort", "stands");
        world.put("place.delhi.chandni_chowk", "stands");
        BranchSave save = BranchSave.root(BranchSave.Snapshot.of(world, 1857, "main"),
                "the history that happened");
        Map<String, String> branchWorld = new TreeMap<>(world);
        branchWorld.put("place.delhi.red_fort", "never built");
        save = save.branch(BranchSave.Snapshot.of(world, 1857, "main"),
                BranchSave.Snapshot.of(branchWorld, 1861, "b1"), 1857, List.of(), "the fort never rose");
        ok(save.diff("b1", BranchSave.Snapshot.of(branchWorld, 1861, "b1")).isEmpty(),
                "and the branch is clean: no paradox, no stress, no broken point");
        eq(stress.total(), 0, "the counter does not move for a what-if");

        // ------------------------------------------------ 4. THE FORCE BREAKS IT AND BOOKS ITS PARADOX
        Verdict strangerForce = ParadoxEngine.forceFixed(Actor.of("Sam", false), pts, stress, "red-fort",
                "I want it gone", 1857);
        ok(!strangerForce.ok(), "a player cannot force it");
        Verdict forced = ParadoxEngine.forceFixed(ada, pts, stress, "red-fort", "the player tore it down",
                1857);
        ok(forced.ok(), "an operator forces it");
        eq(forced.found().get(0).kind(), Paradox.Kind.GRANDFATHER, "and the paradox is grandfather kind");
        ok(forced.found().get(0).what().contains(fortName), "naming the record's own thing: "
                + forced.found().get(0).what());
        eq(stress.total(), 5, "the counter carries the point's weight");

        // ------------------------------------------------ 5. THE OTHER KINDS, ACROSS ERAS
        WhoYouAre ashraf = WhoYouAre.make("Ashraf", WhoYouAre.Kind.LOCAL, 1830, 1857, "Delhi",
                List.of(new WhoYouAre.Entry("Fatima", "mother", 1, 1805, 1870),
                        new WhoYouAre.Entry("Daulat", "grandfather", 2, 1778, 1840)), List.of()).who();
        Verdict killed = ParadoxEngine.endAncestor(ashraf, stress, "Sam", "Daulat", 1795);
        ok(killed.ok() && killed.found().size() == 1, "ending the grandfather too early is booked");
        Verdict killedOk = ParadoxEngine.endAncestor(ashraf, stress, "Sam", "Daulat", 1810);
        ok(killedOk.ok() && killedOk.found().isEmpty(), "and ending him later is a death, cleared");
        Verdict paper = ParadoxEngine.handOver(stress, "Mira", "Ninlil", "paper", -2960, -300);
        ok(paper.found().get(0).kind() == Paradox.Kind.CAUSAL_LOOP, "paper in 2960 BC is a loop");
        Verdict farming = ParadoxEngine.handOver(stress, "Mira", "Ninlil", "farming", -2960, -9500);
        ok(farming.found().isEmpty(), "farming in 2960 BC is nine thousand years late, which is fine");
        Verdict caused = ParadoxEngine.attemptCaused(stress, "Sam", "Sam", "tried to stop the mutiny",
                "the mutiny of 1857", 1857);
        ok(caused.found().get(0).kind() == Paradox.Kind.PREDESTINATION, "the attempt that caused its event");
        Verdict stamped = ParadoxEngine.stamp(stress, "Mira", "Mira", "Cuzco", 1576, 2);
        ok(stamped.found().get(0).kind() == Paradox.Kind.MEETING_SELF, "two stamps in 1576 Cuzco");
        Verdict told = ParadoxEngine.tell(stress, "Sam", "Sam", "the internet", 1990, 1857);
        ok(told.found().get(0).kind() == Paradox.Kind.TELLING_FUTURE, "the internet in 1857");
        eq(stress.total(), 5 + 5 + 2 + 2 + 3 + 1, "five kinds and the force: one counter");

        // ------------------------------------------------ 6. TERRA++'S BUILDINGS ON THE SAME COUNTER
        Stress.Bridge buildings = new Stress.Bridge() {
            @Override
            public int buildingStress() {
                return 7;
            }

            @Override
            public String describe() {
                return "a recorder, standing in for Terra++: 7 broken dated buildings";
            }
        };
        stress.connect(buildings);
        eq(stress.total(), 25, "the one counter includes Terra++'s buildings");
        stress.connect(Stress.absent());
        eq(stress.total(), 18, "and without the bridge it says they are not counted, not that they are fine");
        ok(stress.bridgeLine().contains("not connected"), "in words: " + stress.bridgeLine());

        // ------------------------------------------------ 7. REBUILDING BRINGS IT DOWN (H8's arithmetic)
        Verdict rebuilt = ParadoxEngine.rebuild(ada, pts, stress, "red-fort", "the stones went back");
        ok(rebuilt.ok(), "the point is rebuilt: " + rebuilt.line());
        eq(stress.total(), 13, "and the counter falls by exactly the point's weight");
        ok(!pts.broken("red-fort"), "and the point stands again");

        // ------------------------------------------------ 8. THE PAGE, AND WHAT IS NOT ON IT
        List<Verdict> all = new ArrayList<>(List.of(forced, killed, killedOk, paper, farming, caused,
                stamped, told, rebuilt));
        for (String line : ParadoxEngine.page(all)) System.out.println("     " + line);
        ok(ParadoxEngine.page(all).get(0).contains("6 paradoxes"), "the page counts every finding (the "
                + "force and the five kinds)");
        for (String line : stress.report()) System.out.println("     " + line);
        ok(stress.report().get(0).contains("stress 13"), "and the counter's report agrees with the page's "
                + "maths");
        ok(!String.join("\n", stress.report()).toLowerCase(java.util.Locale.ROOT).contains("erasure"),
                "nothing here decides a consequence: no erasure, no threshold");
        System.out.println("     " + Paradox.ruleLine());
        System.out.println("     " + Stress.ruleLine());

        System.out.println("\nStep 53 part 6: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
