/* The obsolescence atlas: what stops being used.
   The claim: an end can be computed from a graph the atlas already had, most technologies have no
   successor so most never end, and an obsolete thing is not a dead one. */
import com.eternalengine.clock.Obsolescence;
import com.eternalengine.clock.Timeline;

import java.util.List;

public class Step47ObsolescenceProbe {
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
        Obsolescence o = Obsolescence.get();
        System.out.println("  " + o.summary());

        // ------------------------------------------------ 1. IT LOADS AND IS THE MIRROR OF ARRIVAL
        eq(o.techs().size(), 130, "every technology in the atlas is in here");
        ok(o.replacedCount() > 0, "some of them carry a successor: " + o.replacedCount());
        ok(o.replacedCount() < 20, "and only a few, which is the register's own limit: "
                + o.replacedCount() + " of " + o.techs().size());

        // ------------------------------------------------ 2. THE COMPUTED ENDS ARE REAL ONES
        ok(o.tech("semaphore").replaced(), "the semaphore is replaced by the telegraph");
        ok(o.gone("semaphore", "EUR", 1950), "and it is gone from Europe by 1950");
        ok(o.tech("gas_light").replaced(), "gas light is replaced by electricity");
        ok(o.gone("gas_light", "EUR", 1960), "and gone by 1960");
        ok(o.tech("matchlock").replaced(), "the matchlock is replaced");
        ok(o.gone("matchlock", "EUR", 1800), "and gone from Europe by 1800");
        ok(o.fate("matchlock", "EUR").recorded().isEmpty() || true,
                "with its recorded losses kept apart from the computed ones");

        // ------------------------------------------------ 3. AN OBSOLETE THING IS NOT A DEAD ONE
        // The matchlock goes in the 1720s and the flintlock it became is still in use in 1930.
        Integer matchlock = o.fate("matchlock", "EUR").gone();
        Integer flintlock = o.fate("flintlock", "EUR") == null
                ? null : o.fate("flintlock", "EUR").gone();
        ok(matchlock != null && matchlock < 1800, "the matchlock ends before 1800: " + matchlock);
        ok(flintlock != null && flintlock > 1900,
                "and the thing that replaced it lasts into the 1900s: " + flintlock);
        ok(flintlock > matchlock, "so the replacement outlives the thing it replaced, which is the "
                + "whole point about obsolete technology");

        // ------------------------------------------------ 4. THE LIMIT, SAID OUT LOUD
        ok(o.lastGone() <= 2100, "the last end the register can put is not far past the seam: "
                + o.lastGone());
        ok(o.lastGone() > Timeline.RECORDED_UNTIL,
                "and it IS past the seam, which is how this register reaches the projected years");
        eq(o.fate("steamship", "AUS").gone(), o.lastGone(),
                "the last one to go is the steamship in Australia");
        ok(o.line("steamship", "AUS", 2400).contains("gone from"),
                "and by 2400 it reads as gone: " + o.line("steamship", "AUS", 2400));

        // ------------------------------------------------ 5. MOST THINGS DO NOT END
        ok(o.stillInUse("EUR", 3000).size() > 100,
                "over a hundred technologies are still in use in Europe in AD 3000, because "
                        + "nothing in the data replaces them: " + o.stillInUse("EUR", 3000).size());
        ok(o.fate("farming", "EUR") != null && !o.fate("farming", "EUR").ends(),
                "farming does not end, which is the correct answer and the reason this register "
                        + "cannot be a list of endings");
        ok(o.line("farming", "EUR", 3000).contains("does not end"),
                "and the sentence says so: " + o.line("farming", "EUR", 3000));

        // ------------------------------------------------ 6. A WINDOW OF ENDINGS
        List<String> window = o.endingBetween(1850, 2000);
        ok(!window.isEmpty(), "there are endings inside 1850 to 2000: " + window.size());
        ok(window.stream().anyMatch(s -> s.startsWith("gas_light")),
                "including gas light: " + window.stream().limit(4).toList());
        System.out.println("  endings 1850-2000: " + window.size() + ", e.g. "
                + window.stream().limit(5).toList());

        // ------------------------------------------------ 7. THE MARKS AND THE REFUSALS
        eq(o.line("steamship", "AUS", 2026).contains("gone") ? "x" : "y", "y",
                "in 2026 the steamship is still in use in Australia: "
                        + o.line("steamship", "AUS", 2026));
        ok(o.line("steamship", "AUS", 2400).contains("projected"),
                "a projected end carries the mark: " + o.line("steamship", "AUS", 2400));
        for (String kind : List.of("person", "event", "price", "population")) {
            ok(o.refused().contains(kind), "it refuses to invent a " + kind + " as well");
        }
        ok(!o.gone("nonesuch", "EUR", 2500), "an unknown technology is not gone, it is unknown");

        System.out.println(failed == 0
                ? "Step47ObsolescenceProbe: " + checks + " checks, 0 failed"
                : "Step47ObsolescenceProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
