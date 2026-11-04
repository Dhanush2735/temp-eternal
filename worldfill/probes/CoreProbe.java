import com.eternalengine.clock.SimulationClockManager;
import com.eternalengine.core.SystemRunner;
import com.eternalengine.terrabridge.TerraTimeBridge;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * Step 14: the pure parts of the core changes, outside the game.
 *  1. Speed votes: a speed wins with more than half of the VIP players online; others' votes do not count.
 *  2. Terra++ time: the first day of a year at a scale lands in that year (the old rounding missed some).
 *  3. The safety net: a failing system costs only its own run; the next system still runs; failures are
 *     counted with the latest error; errors the JVM cannot recover from still stop the server.
 * Run with worldfill/probe_core.sh. Prints PASS/FAIL lines and a summary; exit code 1 on any failure.
 */
public class CoreProbe {
    static int pass, fail;

    static void check(boolean ok, String what) {
        if (ok) { pass++; System.out.println("PASS " + what); }
        else { fail++; System.out.println("FAIL " + what); }
    }

    public static void main(String[] args) {
        UUID a = UUID.randomUUID(), b = UUID.randomUUID(), c = UUID.randomUUID(), outsider = UUID.randomUUID();
        Map<UUID, Integer> votes = new HashMap<>();
        votes.put(a, 25);
        var o1 = SimulationClockManager.tally(votes, Set.of(a, b, c));
        check(o1.winner() == null && o1.needed() == 2 && o1.eligible() == 3, "1 of 3 VIPs for 25x: no winner yet, 2 needed");
        votes.put(b, 25);
        var o2 = SimulationClockManager.tally(votes, Set.of(a, b, c));
        check(Integer.valueOf(25).equals(o2.winner()), "2 of 3 VIPs for 25x: 25x wins");
        votes.put(b, 10);
        votes.put(outsider, 10);
        votes.put(c, 50);
        var o3 = SimulationClockManager.tally(votes, Set.of(a, b, c));
        check(o3.winner() == null && o3.tally().getOrDefault(10, 0) == 1,
            "25x/10x/50x split: no winner; the vote of a player who is not an online VIP is not counted");
        var o4 = SimulationClockManager.tally(Map.of(a, 5), Set.of(a));
        check(Integer.valueOf(5).equals(o4.winner()), "the only VIP online decides alone");
        var o5 = SimulationClockManager.tally(Map.of(a, 10, b, 25), Set.of(a, b));
        check(o5.winner() == null, "1:1 between two VIPs: no winner (a speed needs more than half)");

        int[] scales = {1, 10, 25, 50};
        int bad = 0, oldBad = 0, n = 0;
        for (int scale : scales) {
            for (int year = -3000; year <= 2100; year++) {
                long day = TerraTimeBridge.dayForYear(year, -3000, 365, scale);
                int got = (int) (-3000 + (day * scale) / 365);
                long dayBefore = day - 1;
                int prev = dayBefore < 0 ? Integer.MIN_VALUE : (int) (-3000 + (dayBefore * scale) / 365);
                if (got != year || prev == year) bad++;   // must be in the year, and the first day of it
                long oldDay = ((long) (year + 3000) * 365) / scale;   // the rounding before step 14
                if ((int) (-3000 + (oldDay * scale) / 365) != year) oldBad++;
                n++;
            }
        }
        check(bad == 0, "Terra++ time: the day for each of " + n + " year/scale pairs is the first day of that year ("
            + bad + " wrong; the old rounding put " + oldBad + " of them in the year before)");
        check(TerraTimeBridge.dayForYear(-3001, -3000, 365, 10) < 0, "Terra++ time: a year before -3000 has no day");

        SystemRunner runner = new SystemRunner();
        int[] ran = {0};
        boolean first = runner.run("broken", () -> { throw new IllegalStateException("boom 1"); });
        boolean next = runner.run("fine", () -> ran[0]++);
        runner.run("broken", () -> { throw new IllegalStateException("boom 2"); });
        var failures = runner.failures();
        check(!first && next && ran[0] == 1, "a system that throws returns false, and the next system still runs");
        check(failures.containsKey("broken") && failures.get("broken").count() == 2
                && failures.get("broken").lastError().contains("boom 2") && !failures.containsKey("fine"),
            "failures are counted per system with the latest error; a healthy system has none");
        boolean vmErrorPassed;
        try {
            runner.run("oom", () -> { throw new OutOfMemoryError("probe"); });
            vmErrorPassed = false;
        } catch (OutOfMemoryError expected) {
            vmErrorPassed = true;
        }
        check(vmErrorPassed, "an out-of-memory error is not swallowed (it must still stop the server)");
        runner.clear();
        check(runner.failures().isEmpty() && runner.totalFailures() == 0, "a new world starts with no failures");

        System.out.println("SUMMARY pass=" + pass + " fail=" + fail);
        System.exit(fail == 0 ? 0 : 1);
    }
}
