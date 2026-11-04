/* Step 57 part 4 (I3): heavy work off the game thread. The claim: work is a CLASS, not a place -
   loading, planning, path searches, saves and the network run off the game thread; ticking and world
   writes run on it. A job on the wrong side is refused by name; a result that touches the world comes
   back first. The load numbers behind the rule are the walk's own measurements. */
import com.eternalengine.core.OffThread;
import com.eternalengine.core.OffThread.Job;
import com.eternalengine.core.OffThread.Side;
import com.eternalengine.core.OffThread.Started;
import com.eternalengine.core.OffThread.Work;

public class Step57OffThreadProbe {
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

    static void refused(Started s, String words, String what) {
        checks++;
        if (s.ok()) {
            failed++;
            System.out.println("  FAIL " + what + "  (the job started)");
            return;
        }
        if (s.refused().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no refusal says \"" + words + "\"; got " + s.refused());
    }

    public static void main(String[] args) {
        // ------------------------------------------------ 1. THE TABLE OF CLASSES
        eq(Work.values().length, 7, "seven classes of work");
        eq(Work.LOADING.side(), Side.OFF_THREAD, "loading runs off the game thread");
        eq(Work.PLANNING.side(), Side.OFF_THREAD, "so does planning");
        eq(Work.PATH_SEARCH.side(), Side.OFF_THREAD, "and path searches");
        eq(Work.SAVE.side(), Side.OFF_THREAD, "and saves");
        eq(Work.NETWORK.side(), Side.OFF_THREAD, "and the network");
        eq(Work.TICK.side(), Side.GAME_THREAD, "while ticking runs on it");
        eq(Work.WORLD_WRITE.side(), Side.GAME_THREAD, "and so does anything that writes the world");
        ok(Work.LOADING.why().contains("1,201 to 1,388 ms"), "the load rule carries the walk's "
                + "measurement: " + Work.LOADING.why());
        for (Work w : Work.values()) ok(w.line().contains("runs"), "every line names its side: " + w.line());

        // ------------------------------------------------ 2. A JOB ON THE WRONG SIDE IS REFUSED BY NAME
        Started load = OffThread.start("the gazetteer loads", Work.LOADING, Side.OFF_THREAD);
        ok(load.ok(), "loading off-thread starts: " + (load.ok() ? load.job().line() : load.refused()));
        eq(load.job().side(), Side.OFF_THREAD, "and runs there");
        refused(OffThread.start("the gazetteer loads", Work.LOADING, Side.GAME_THREAD),
                "runs off the game thread", "loading on the game thread is refused");
        refused(OffThread.start("the tick", Work.TICK, Side.OFF_THREAD),
                "runs on the game thread", "and ticking off it is refused");
        refused(OffThread.start("", Work.SAVE, Side.OFF_THREAD), "nobody can account for",
                "work with no name is refused");
        refused(OffThread.start("a job", null, Side.OFF_THREAD), "names no class",
                "a job with no class is refused");
        refused(OffThread.start("a job", Work.SAVE, null), "say where it runs",
                "and a job with no side is refused");

        // ------------------------------------------------ 3. COMING BACK
        refused(OffThread.touchWorld("the plan's answer", Work.PLANNING, Side.OFF_THREAD),
                "hand it back first", "an off-thread result may not touch the world");
        ok(OffThread.touchWorld("the tick's change", Work.WORLD_WRITE, Side.GAME_THREAD).ok(),
                "and the game thread writes the world");
        ok(OffThread.touchWorld("the tick's change", Work.TICK, Side.GAME_THREAD).ok(),
                "as it ticks");

        // ------------------------------------------------ 4. THE PAGE AND THE RULE
        eq(OffThread.lines().size(), 7, "the page carries every class");
        for (String line : OffThread.lines()) System.out.println("     " + line);
        System.out.println("     " + OffThread.ruleLine());
        ok(OffThread.ruleLine().contains("class, not a place"), "the rule keeps the shape");
        ok(OffThread.ruleLine().contains("hand") || OffThread.ruleLine().contains("comes back"),
                "and the hand-back rule");

        System.out.println("\nStep 57 part 4: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
