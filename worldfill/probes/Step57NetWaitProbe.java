/* Step 57 part 6 (I7, I8): packet budgets and the rebuild wait. The claim: a packet over Minecraft's
   limit is refused by name and by how much (it is not slow, it never arrives); a window over the rate
   budgets is named in words. The wait is a state, not a stall: it names what is queued, what is rebuilt
   and what is left; a second wait while one runs is refused; more rebuilt than queued invents chunks
   and is refused; and when the queue drains the wait says it is over. */
import com.eternalengine.network.PacketBudget;
import com.eternalengine.network.PacketBudget.Sent;
import com.eternalengine.network.PacketBudget.Window;
import com.eternalengine.terrabridge.RebuildWait;
import com.eternalengine.terrabridge.RebuildWait.Started;
import com.eternalengine.terrabridge.RebuildWait.Wait;

public class Step57NetWaitProbe {
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

    static void refused(Sent s, String words, String what) {
        checks++;
        if (s.ok()) {
            failed++;
            System.out.println("  FAIL " + what + "  (the packet was sent)");
            return;
        }
        if (s.refused().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no refusal says \"" + words + "\"; got " + s.refused());
    }

    static void refused(Started s, String words, String what) {
        checks++;
        if (s.ok()) {
            failed++;
            System.out.println("  FAIL " + what + "  (it happened: " + s.state().line() + ")");
            return;
        }
        if (s.refused().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no refusal says \"" + words + "\"; got " + s.refused());
    }

    public static void main(String[] args) {
        // ------------------------------------------------ 1. THE PACKET BUDGETS (I7)
        eq(PacketBudget.MAX_BYTES, 32767, "Minecraft's own limit is the size budget");
        eq(PacketBudget.MAX_PER_SECOND, 20, "one packet a tick");
        eq(PacketBudget.MAX_BYTES_PER_SECOND, 200000L, "and 200,000 bytes a second");

        Sent ok = PacketBudget.send("the paper page", 4000);
        ok(ok.ok(), "a packet inside the limit is sent: " + (ok.ok() ? ok.packet().what() : ok.refused()));
        refused(PacketBudget.send("", 100), "no name", "a packet with no name is refused");
        refused(PacketBudget.send("the page", 0), "carries nothing", "and a packet of nothing");
        refused(PacketBudget.send("the book", 40000), "never arrives",
                "a packet over Minecraft's limit is refused, by name and by how much");
        refused(PacketBudget.send("the book", 40000), "32767", "naming the limit");
        refused(PacketBudget.send("the book", 40000), "7233 over", "and how much over");

        Window clean = PacketBudget.window("Sam", 1.0, 10, 50000);
        ok(clean.clean(), "a quiet window is clean: " + clean.line());
        Window busy = PacketBudget.window("Sam", 1.0, 40, 100000);
        ok(!busy.clean(), "a busy one is named");
        ok(busy.line().contains("inside every rate") || busy.over().get(0).contains("40 packets a second"),
                "in words: " + busy.line());
        ok(busy.line().contains("40 packets a second against 20"), "the rate is named: " + busy.line());
        Window heavy = PacketBudget.window("Sam", 1.0, 5, 500000);
        ok(heavy.line().contains("bytes a second against 200000"), "and the byte rate: " + heavy.line());
        Window noTime = PacketBudget.window("Sam", 0, 5, 100);
        ok(noTime.line().contains("no window"), "and a window of no time is refused, not guessed: "
                + noTime.line());
        System.out.println("     " + PacketBudget.ruleLine());

        // ------------------------------------------------ 2. THE REBUILD WAIT (I8)
        RebuildWait waits = RebuildWait.empty();
        ok(!waits.running(), "nothing is waiting");
        Started begun = waits.begin(120, "the time jump of 2026");
        ok(begun.ok(), "the wait begins: " + begun.state().line());
        ok(begun.state().words().contains("0 of 120 chunks rebuilt, 120 left"),
                "and says where it stands: " + begun.state().words());
        ok(waits.running(), "and the world knows it is waiting");

        refused(waits.begin(50, "another jump"), "already running",
                "a second wait while one runs is refused");
        refused(waits.begin(50, "another jump"), "worlds corrupt", "and says why");

        Started part = waits.progress(begun.state().id(), 40);
        ok(part.ok(), "the rebuild drains: " + part.state().words());
        ok(part.state().words().contains("40 of 120"), "and the words keep count");
        ok(part.state().words().contains("80 left"), "and what is left");
        refused(waits.progress(begun.state().id(), 200), "invent chunks",
                "more rebuilt than queued is refused");
        refused(waits.progress(begun.state().id(), -1), "below none", "and below none");
        refused(waits.progress("no-such-wait", 1), "no wait called", "an unknown wait is refused");

        Started done = waits.progress(begun.state().id(), 120);
        ok(done.ok(), "and the queue drains: " + done.state().words());
        ok(done.state().words().contains("the wait is over: 120 chunks rebuilt"),
                "in words: " + done.state().words());
        ok(!waits.running(), "and nothing is waiting");
        refused(waits.progress(begun.state().id(), 120), "already over", "an over wait is over");
        // check order matters: the already-running refusal fires first, so the empty queue is tried
        // only now, with nothing running.
        refused(waits.begin(0, ""), "nothing is queued", "a wait for nothing is a stall");

        Wait found = waits.find(begun.state().id());
        ok(found != null && found.left() == 0, "the book keeps the record");
        eq(waits.lines().size(), 1, "one wait on the books");
        for (String line : waits.lines()) System.out.println("     " + line);
        System.out.println("     " + RebuildWait.ruleLine());
        ok(RebuildWait.ruleLine().contains("not a stall"), "the rule keeps the state rule");
        ok(RebuildWait.ruleLine().contains("invents"), "and the no-inventing rule");

        System.out.println("\nStep 57 part 6: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
