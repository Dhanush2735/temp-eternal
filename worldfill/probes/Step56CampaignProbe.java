/* Step 56 part 4 (F6): the story campaign, decision 7. The claim: a player is never erased; no countdown
   deletes anybody; a chapter not kept is CONTINUED, never failed; and the pressure is a gauge that
   fires nothing. The six stations walk the whole timeline, not one favourite place or year. */
import com.eternalengine.chrononexus.Campaign;
import com.eternalengine.chrononexus.Campaign.Chapter;
import com.eternalengine.chrononexus.Campaign.State;
import com.eternalengine.chrononexus.Campaign.Told;
import com.eternalengine.timeline.Stress;

import java.util.List;

public class Step56CampaignProbe {
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

    static void refused(Told t, String words, String what) {
        checks++;
        if (t.ok()) {
            failed++;
            System.out.println("  FAIL " + what + "  (it happened)");
            return;
        }
        if (t.refused().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no refusal says \"" + words + "\"; got " + t.refused());
    }

    public static void main(String[] args) {
        // ------------------------------------------------ 1. THE SIX STATIONS
        List<Chapter> chapters = Campaign.chapters();
        eq(chapters.size(), 6, "the story has six stations");
        eq(chapters.get(0).place(), "Ur", "and walks the whole timeline: Ur in -2900");
        eq(chapters.get(1).place(), "Cuzco", "Cuzco in 1576");
        eq(chapters.get(2).year(), 1857, "Delhi in 1857");
        eq(chapters.get(4).year(), 2026, "Hyderabad in 2026");
        eq(chapters.get(5).year(), 2100, "and the far shore in 2100");
        for (Chapter c : chapters) System.out.println("     " + c.line());

        // ------------------------------------------------ 2. A CHAPTER NOT KEPT IS CONTINUED
        State s = new State(List.of(), List.of(), "");
        Told told = Campaign.tell(s, 1, true);
        ok(told.ok(), "the first chapter is told");
        eq(told.state().kept(), List.of(1), "and kept");
        Told gone = Campaign.tell(told.state(), 2, false);
        ok(gone.ok(), "a chapter not kept is still told");
        eq(gone.state().continued(), List.of(2), "and continued, never failed");
        ok(gone.state().line().contains("the story goes on"), "in words: " + gone.state().line());
        refused(Campaign.tell(gone.state(), 2, true), "already told",
                "a story tells its chapters once");
        refused(Campaign.tell(gone.state(), 9, true), "no chapter 9",
                "and there is no chapter that is not there");

        // ------------------------------------------------ 3. NO RAIL, NO SCRIPT, NO TIMER
        Told outOfOrder = Campaign.tell(gone.state(), 5, true);
        ok(outOfOrder.ok(), "chapters may be walked in any order: 5 before 3 and 4");
        eq(outOfOrder.state().kept(), List.of(1, 5), "the story is not a rail");
        // and nothing in this class knows about time passing
        for (String line : Campaign.page(outOfOrder.state())) System.out.println("     " + line);

        // ------------------------------------------------ 4. THE PRESSURE IS A GAUGE
        Stress stress = Stress.empty();
        stress.add(Stress.Source.EVENT, "the year 2526", 2526, "forced a fixed point", 5, "the weight");
        String gauge = Campaign.pressure(stress);
        ok(gauge.contains("pressure: 5"), "the gauge reads the counter: " + gauge);
        ok(gauge.contains("It rises and it falls"), "and says what it is");
        ok(gauge.contains("Nothing here erases you"), "and what it is not: " + gauge);
        ok(Campaign.pressure(null).contains("pressure: 0"), "and a missing counter reads zero, not "
                + "erasure");

        // ------------------------------------------------ 5. THE ENDINGS ARE WORDS
        refused(Campaign.close(new State(List.of(), List.of(), ""), "the end"), "unopened",
                "a story with nothing told is unopened, not ended");
        Told closed = Campaign.close(outOfOrder.state(), "");
        ok(closed.ok(), "the story closes in words");
        ok(closed.state().ending().contains("differently") && closed.state().ending().contains(
                "nobody was erased"), "and the ending says it: " + closed.state().ending());
        Told closedAll = Campaign.close(new State(List.of(1, 2, 3), List.of(), ""), "");
        ok(closedAll.state().ending().contains("world intact"), "a fully kept story ends whole: "
                + closedAll.state().ending());
        refused(Campaign.close(closed.state(), ""), "already closed", "and it closes once");
        ok(Campaign.close(closed.state(), "").refused().contains("went on, differently"),
                "carrying its own ending: " + Campaign.close(closed.state(), "").refused());

        // ------------------------------------------------ 6. THE RULE
        System.out.println("     " + Campaign.pressure(stress));
        System.out.println("     " + Campaign.ruleLine());
        ok(Campaign.ruleLine().contains("never erased"), "the rule keeps the erasure refusal");
        ok(Campaign.ruleLine().contains("never failed"), "and the no-failure rule");
        ok(Campaign.ruleLine().contains("fires nothing"), "and the gauge rule");

        System.out.println("\nStep 56 part 4: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
