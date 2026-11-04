/* Step 57 part 2 (I1): budgets as data. The claim: every budget names where its number comes from - a
   game default, a measurement, or Minecraft's own limit. A blown budget is named in words and never
   hidden; no report is not a pardon. */
import com.eternalengine.core.PerfBudget;
import com.eternalengine.core.PerfBudget.Budget;
import com.eternalengine.core.PerfBudget.Report;
import com.eternalengine.core.PerfBudget.Sample;
import com.eternalengine.core.PerfBudget.Source;

import java.util.List;

public class Step57BudgetProbe {
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
        // ------------------------------------------------ 1. THE BUDGETS AND THEIR SOURCES
        eq(PerfBudget.budgets().size(), 4, "four budgets are held");
        eq(PerfBudget.TICK_TOTAL.source(), Source.GAME_DEFAULT, "the tick budget is a game default");
        eq(PerfBudget.PACKET_BYTES.source(), Source.VANILLA_LIMIT, "the packet limit is Minecraft's own");
        ok(PerfBudget.CACHE_BYTES.line().contains("a game default"), "and every line names its source: "
                + PerfBudget.CACHE_BYTES.line());
        ok(PerfBudget.TICK_TOTAL.line().contains("maxTickBudgetMs"), "in words: "
                + PerfBudget.TICK_TOTAL.line());
        eq(PerfBudget.TICK_TOTAL.limit(), 10.0, "the tick is 10 ms");
        eq(PerfBudget.ONE_QUERY.limit(), 2.0, "a lookup is 2 ms");
        eq(PerfBudget.PACKET_BYTES.limit(), 32767.0, "and a packet is 32,767 bytes");

        // ------------------------------------------------ 2. SAMPLES
        Sample clean = new Sample("ruler-register", 1000, 100.0, 0.5);
        eq(String.format("%.4f", clean.avgMs()), "0.1000", "the average is computed");
        ok(clean.line().contains("1000 calls"), "in words: " + clean.line());

        // ------------------------------------------------ 3. A BLOWN BUDGET IS NAMED IN WORDS
        eq(PerfBudget.over(clean, PerfBudget.ONE_QUERY), null, "a clean lookup blows nothing");
        eq(PerfBudget.over(clean, PerfBudget.TICK_TOTAL), null, "and no single call blows the tick");
        Sample slow = new Sample("scene-register", 100, 900.0, 4.5);
        String blow = PerfBudget.over(slow, PerfBudget.ONE_QUERY);
        checks++;
        if (blow == null || !blow.contains("scene-register blew one lookup answering a player")
                || !blow.contains("7.0 over") || !blow.contains("a game default")) {
            failed++;
            System.out.println("  FAIL the blow names system, budget, over, and source; got " + blow);
        } else {
            System.out.println("     " + blow);
        }
        String tickBlow = PerfBudget.over(new Sample("map", 10, 50.0, 12.0), PerfBudget.TICK_TOTAL);
        ok(tickBlow != null && tickBlow.contains("worst call 12.0 ms against 10.0"),
                "and a single call over the tick is named too: " + tickBlow);

        // ------------------------------------------------ 4. THE CHECK
        Report cleanWalk = new Report(List.of(clean, new Sample("law-register", 500, 50.0, 0.4)),
                PerfBudget.budgets(), 1200, 3);
        eq(PerfBudget.check(cleanWalk).size(), 0, "a clean walk checks clean");
        Report dirtyWalk = new Report(List.of(clean, slow, new Sample("soundscape", 50, 400.0, 9.0)),
                PerfBudget.budgets(), 2400, 3);
        List<String> blows = PerfBudget.check(dirtyWalk);
        eq(blows.size(), 2, "two systems blew the lookup budget");
        ok(blows.get(0).contains("scene-register") && blows.get(1).contains("soundscape"),
                "in walk order: " + blows);
        ok(PerfBudget.check(null).get(0).contains("nothing is pardoned"),
                "and no report is not a pardon: " + PerfBudget.check(null));
        eq(dirtyWalk.worst().system(), "soundscape", "the worst call is named");

        // ------------------------------------------------ 5. THE PAGE AND THE RULE
        List<String> page = PerfBudget.page(dirtyWalk);
        ok(page.get(0).contains("3 iterations in 2400 ms"), "the page opens with the run: " + page.get(0));
        ok(page.get(1).contains("budget the whole tick"), "and every budget with its source");
        ok(page.get(page.size() - 1).startsWith("OVER:"), "and the blows at the end: "
                + page.get(page.size() - 1));
        for (String line : page) System.out.println("     " + line);
        System.out.println("     " + PerfBudget.ruleLine());
        ok(PerfBudget.ruleLine().contains("where its number comes from"), "the rule keeps the sources");
        ok(PerfBudget.ruleLine().contains("never hidden"), "and the naming rule");

        System.out.println("\nStep 57 part 2: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
