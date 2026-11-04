/* Step 56 part 5: the chain, end to end. Each class passed its own probe; only the chain proves the
   game. The chain: a universe cracks open (step 54) -> a traveller crosses and comes home along her
   own ticket (H7) -> a fixed point is forced and the counter rises -> it is rebuilt and the counter
   falls (H8) -> the campaign walks the same ground as a story whose pressure is a gauge and whose
   player is never erased (F6). */
import com.eternalengine.chrononexus.Campaign;
import com.eternalengine.chrononexus.Campaign.State;
import com.eternalengine.chrononexus.Campaign.Told;
import com.eternalengine.player.Permissions.Decision;
import com.eternalengine.terrabridge.LandSpec;
import com.eternalengine.terrabridge.LandSpec.Mirror;
import com.eternalengine.timeline.BeforeChange;
import com.eternalengine.timeline.BranchSave;
import com.eternalengine.timeline.FixedPoints;
import com.eternalengine.timeline.Passage;
import com.eternalengine.timeline.Passage.Way;
import com.eternalengine.timeline.Repairs;
import com.eternalengine.timeline.Repairs.Repaired;
import com.eternalengine.timeline.RuptureEngine;
import com.eternalengine.timeline.RuptureEngine.Verdict;
import com.eternalengine.timeline.Ruptures;
import com.eternalengine.timeline.Stress;

import java.util.List;
import java.util.Map;

public class Step56ChainProbe {
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
        // ------------------------------------------------ 1. A UNIVERSE CRACKS OPEN
        Ruptures worlds = Ruptures.empty();
        worlds.declare("earth", null, LandSpec.earth(), -3000, "the land as Terra++ makes it");
        BeforeChange copies = BeforeChange.empty();
        LandSpec.Made other = LandSpec.make(120, -2032, 2032, true, Mirror.EAST_WEST, "the rupture of 2026");
        Verdict made = RuptureEngine.rupture("the year 2026", "u-high-sea-2026", "earth", other.spec(),
                null, 2026, "the seas rose and the land flipped", copies,
                BranchSave.Snapshot.of(Map.of("state.world", "2026"), 2026, "main"), worlds, null);
        copies = made.copiesAfter();
        ok(made.ok(), "the universe exists: " + made.decision().why());
        ok(made.backupId() != null, "its copy was taken first: " + made.backupId());

        // ------------------------------------------------ 2. A CROSSING OUT AND HOME (H7)
        Passage book = Passage.over(worlds);
        Passage.Travelled out = book.travel("Maya", "earth", "u-high-sea-2026", 2100, Way.PORTAL,
                "the drowned streets");
        ok(out.ok(), "Maya crosses to the new universe: " + out.ticket().line());
        eq(book.whereIs("Maya"), "u-high-sea-2026", "and stands there");
        eq(book.outstanding().size(), 1, "away, with the way home booked");
        Passage.Returned home = book.back("Maya", out.ticket().id());
        ok(home.ok(), "and comes home along her own ticket");
        eq(book.whereIs("Maya"), "earth", "back on earth");
        eq(book.outstanding().size(), 0, "and nobody is stranded");

        // ------------------------------------------------ 3. FORCE, THEN REBUILD (H8)
        FixedPoints pts = FixedPoints.empty();
        pts.declare(new FixedPoints.Point("fall-of-cuzco", 1576, "the fall of Cuzco",
                "the record holds it", 5));
        Stress stress = Stress.empty();
        Decision resisted = pts.restore("nobody", "fall-of-cuzco", "x"); // unbroken: the safe words
        ok(!resisted.allowed() && resisted.why().contains("nothing to rebuild"),
                "an unbroken point needs no repair: " + resisted.why());
        ok(pts.force("the year 2026", "fall-of-cuzco", "the campaign's chapter").ok(),
                "the campaign forces the point");
        stress.add(Stress.Source.EVENT, "the year 2026", 2026, "forced fall-of-cuzco", 5,
                "the point's weight");
        eq(stress.total(), 5, "and the counter rises");
        System.out.println("     " + Campaign.pressure(stress));
        Repaired fixed = Repairs.repair(pts, stress, "Maya", "fall-of-cuzco", 2100, "the city rebuilt");
        ok(fixed.ok(), "Maya rebuilds it: " + fixed.line());
        eq(fixed.before(), 5, "the counter was 5");
        eq(fixed.after(), 0, "and falls to 0");
        ok(fixed.line().contains("lowered the stress from 5 to 0"), "in one line: " + fixed.line());
        System.out.println("     " + Campaign.pressure(stress));

        // ------------------------------------------------ 4. THE CAMPAIGN WALKS THE SAME GROUND (F6)
        State s = new State(List.of(), List.of(), "");
        s = Campaign.tell(s, 5, true).state();     // the rupture, just done
        s = Campaign.tell(s, 2, true).state();     // the crossing, just done
        s = Campaign.tell(s, 4, true).state();     // the repair, just done
        Told skip = Campaign.tell(s, 3, false);    // the paradox chapter: continued, never failed
        ok(skip.ok(), "and a chapter not kept is continued");
        eq(skip.state().continued(), List.of(3), "never failed");
        List<String> page = Campaign.page(skip.state());
        for (String line : page) System.out.println("     " + line);
        ok(page.get(4).contains("[kept]") && page.get(1).contains("[kept]"),
                "the page marks what was kept");
        Told closed = Campaign.close(skip.state(), "");
        ok(closed.ok(), "and the story closes in words: " + closed.state().ending());
        ok(closed.state().ending().contains("nobody was erased"), "with the erasure refusal in the "
                + "ending itself");

        // ------------------------------------------------ 5. THE RULES
        System.out.println("     " + Passage.ruleLine());
        System.out.println("     " + Repairs.ruleLine());
        System.out.println("     " + Campaign.ruleLine());
        ok(Passage.ruleLine().contains("both legs"), "the travel rule stands");
        ok(Repairs.ruleLine().contains("clamps at zero"), "the repair rule stands");
        ok(Campaign.ruleLine().contains("never erased"), "and the campaign rule stands");

        System.out.println("\nStep 56 part 5: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
