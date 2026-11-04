/* Step 57 part 7: the chain, end to end, and CacheLimits (I11). The claim: a cache has bytes and counts
   every drop (oldest first; an entry bigger than the whole cache refused); a chunk keeps twelve rebuilt
   years and the save's line says which copies go. The chain: one time jump in 2026 walked through the
   whole step - budgets named with their sources, an over-budget system named in words, the crowd far
   away becoming numbers, a packet sent and an oversized one refused, the rebuild waited out, and the
   save's growth counted. */
import com.eternalengine.core.CacheLimits;
import com.eternalengine.core.CacheLimits.Added;
import com.eternalengine.core.CacheLimits.Cache;
import com.eternalengine.core.Distances;
import com.eternalengine.core.Distances.Detail;
import com.eternalengine.core.Distances.Sim;
import com.eternalengine.core.OffThread;
import com.eternalengine.core.OffThread.Side;
import com.eternalengine.core.OffThread.Work;
import com.eternalengine.core.PerfBudget;
import com.eternalengine.core.PerfBudget.Report;
import com.eternalengine.core.PerfBudget.Sample;
import com.eternalengine.network.PacketBudget;
import com.eternalengine.terrabridge.RebuildWait;
import com.eternalengine.terrabridge.RebuildWait.Started;

import java.util.List;

public class Step57ChainProbe {
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
        // ------------------------------------------------ 1. CACHELIMITS (I11)
        Cache cache = new Cache("chunk years", 1000);
        ok(cache.put("1576", 300).ok(), "a year goes in");
        ok(cache.put("1857", 300).ok(), "and another");
        Added crowded = cache.put("2026", 300);
        ok(crowded.ok() && crowded.droppedNow() == 0, "and a third fits: " + cache.report());
        Added dropped = cache.put("2100", 300);
        ok(dropped.ok() && dropped.droppedNow() == 1, "the fourth drops the oldest");
        eq(dropped.droppedBytes(), 300L, "and counts its bytes");
        ok(cache.report().contains("1 entries dropped (300 bytes) to stay inside"),
                "in words, never silent: " + cache.report());
        eq(cache.size(), 3, "three entries held");
        eq(cache.used(), 900L, "900 of 1000 bytes");
        Added tooBig = cache.put("the whole world", 5000);
        ok(!tooBig.ok() && tooBig.refused().contains("bigger than the whole cache"),
                "an entry bigger than the cache is refused: " + tooBig.refused());
        ok(!cache.put("", 10).ok() && !cache.put("x", 0).ok(), "and nameless or empty entries too");
        ok(CacheLimits.saveLine(12).contains("inside 12"), "twelve years is inside: "
                + CacheLimits.saveLine(12));
        ok(CacheLimits.saveLine(15).contains("the oldest 3 year(s) of copies go, oldest first"),
                "and past that the words say what goes: " + CacheLimits.saveLine(15));
        ok(CacheLimits.saveLine(-1).contains("below none"), "below none is refused: "
                + CacheLimits.saveLine(-1));

        // ------------------------------------------------ 2. THE CHAIN: ONE TIME JUMP, WALKED
        // (a) the budgets, each naming its source
        for (PerfBudget.Budget b : PerfBudget.budgets()) {
            ok(b.line().contains("a game default") || b.line().contains("Minecraft"),
                    "every budget names its source: " + b.line());
        }
        // (b) an over-budget system is named in words
        Report report = new Report(List.of(new Sample("gazetteer", 100, 400.0, 0.5),
                new Sample("soundscape", 1, 12.0, 12.0)), PerfBudget.budgets(), 100, 1);
        List<String> blows = PerfBudget.check(report);
        ok(blows.size() >= 1 && blows.get(0).contains("blew"), "the walk's naming works: " + blows);
        // (c) the crowd far away is numbers, and hidden
        eq(Distances.at(300, 256).sim(), Sim.NUMBERS, "far away: numbers only");
        eq(Distances.at(300, 256).draw(), Detail.HIDDEN, "and hidden");
        // (d) the packet goes, and the oversized one never arrives
        ok(PacketBudget.send("the wait page", 4000).ok(), "the packet goes");
        ok(!PacketBudget.send("the whole save", 40000).ok(), "and the oversized one is refused");
        // (e) the rebuild is waited out, off the game thread
        ok(OffThread.start("the world rebuilds", Work.LOADING, Side.OFF_THREAD).ok(),
                "the rebuild runs off the game thread");
        RebuildWait waits = RebuildWait.empty();
        Started begun = waits.begin(60, "the time jump of 2026");
        ok(begun.ok(), "the wait begins");
        Started done = waits.progress(begun.state().id(), 60);
        ok(done.state().words().contains("the wait is over"), "and ends in words: "
                + done.state().words());
        // (f) and the save's growth is counted
        ok(CacheLimits.saveLine(13).contains("oldest 1"), "the save line counts the years");

        // ------------------------------------------------ 3. THE RULES
        System.out.println("     " + CacheLimits.ruleLine());
        System.out.println("     " + PerfBudget.ruleLine());
        System.out.println("     " + OffThread.ruleLine());
        System.out.println("     " + Distances.ruleLine());
        System.out.println("     " + PacketBudget.ruleLine());
        System.out.println("     " + RebuildWait.ruleLine());
        ok(CacheLimits.ruleLine().contains("oldest goes first"), "the cache rule stands");
        ok(CacheLimits.ruleLine().contains("game default"), "and names its source");

        System.out.println("\nStep 57 part 7: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
