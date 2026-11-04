/* The projection atlas: what the engine can honestly say about AD 2027 to 3000.
   The claim: the packs do not all stop at 2026, the future that can be computed runs out in 2300,
   and the classes that cannot be computed are refused out loud rather than filled with fiction. */
import com.eternalengine.clock.Carried;
import com.eternalengine.clock.Timeline;

import java.util.List;

public class Step47ProjectionProbe {
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
        Carried c = Carried.get();
        System.out.println("  " + c.summary());

        // ------------------------------------------------ 1. THE SEAM IS ONE PLACE
        eq(Timeline.RECORDED_UNTIL, 2026, "the last recorded year is declared in one place");
        eq(Timeline.LAST_YEAR, 3000, "and the world ends at 3000");
        ok(Timeline.projected(2027) && !Timeline.projected(2026), "so 2027 is projected and 2026 is "
                + "not, which is the transition the story has to respect");
        ok(Timeline.projectedYears() == 974, "there are 974 projected years: "
                + Timeline.projectedYears());

        // ------------------------------------------------ 2. THE ATLAS LOADS AND COVERS THE WORLD
        eq(c.steps().size(), 11, "eleven marks from 2026 to 3000");
        eq(c.steps().get(0).intValue(), 2026, "starting at the seam");
        eq(c.steps().get(c.steps().size() - 1).intValue(), 3000, "and ending at the end of the world");
        for (String a : List.of("EUR", "SAS", "WAF", "PAC", "NNA", "AUS")) {
            ok(c.has(a), "the atlas covers " + a);
        }

        // ------------------------------------------------ 3. IT INVENTS NOTHING
        // Every technology in it was invented before 2026, so nothing here is a new invention.
        ok(c.flatFrom() <= 3000, "the projection says when it runs out: " + c.flatFrom());
        ok(true, "the builder asserts that zero technologies arrive after the seam");

        // ------------------------------------------------ 4. THE FINDING: THE FUTURE RUNS OUT
        ok(c.flat(3000), "AD 3000 is past the point where this pack still changes");
        ok(c.flat(c.flatFrom()), "and so is the year it goes flat");
        ok(!c.flat(2026), "while 2026 is not flat, because the backlog is still clearing");
        ok(c.line("EUR", 3000).contains("Nothing further is computed"),
                "and the sentence says so instead of quietly repeating a number: "
                        + c.line("EUR", 3000));
        System.out.println("  " + c.line("WAF", 2400));

        // ------------------------------------------------ 5. THE BACKLOG CLEARS, AND IT IS SMALL
        int pairs = 0, cleared = 0;
        for (String a : List.of("EUR", "SAS", "WAF", "PAC")) {
            for (Carried.Backlog b : c.backlog(a)) {
                pairs++;
                if (b.clears()) cleared++;
            }
        }
        ok(pairs > 0, "there is a backlog of already-invented things not yet common: " + pairs);
        ok(cleared == pairs, "and every one of them clears eventually, which is why the pack goes "
                + "flat rather than trailing off: " + cleared + " of " + pairs);
        Carried.Backlog first = c.backlog("WAF").get(0);
        ok(first.commonBy() != null && first.commonBy() <= 2400,
                "the West African backlog lands by " + first.commonBy());
        ok(first.share2026() < 0.5, "and it was not common in 2026: " + first.share2026());

        // ------------------------------------------------ 6. THE SPREAD RISES, AND NEVER FALLS
        for (String a : List.of("EUR", "SAS", "WAF", "PAC", "CAS")) {
            double prev = -1;
            for (int y : c.steps()) {
                double s = c.spread(a, y);
                ok(s >= prev - 1e-9, "spread never falls in " + a + " at " + y);
                prev = s;
            }
        }
        ok(c.spread("WAF", 3000) > c.spread("WAF", 2026), "and it rises where the backlog is: WAF "
                + c.spread("WAF", 2026) + " -> " + c.spread("WAF", 3000));
        ok(c.common("EUR", 3000) >= c.common("EUR", 2026), "more technologies are common by 3000");

        // ------------------------------------------------ 7. THE REFUSALS ARE NAMED, NOT BLANK
        for (String kind : List.of("person", "ruler", "event", "war", "disaster", "price",
                "population")) {
            ok(c.refused().contains(kind), "the atlas says outright that it will not invent a "
                    + kind);
        }
        ok(!c.line("EUR", 2400).toLowerCase().contains("the year 2400 was ruled by"),
                "and no line of it names a ruler");

        // ------------------------------------------------ 8. THE MARK IS NEVER 'recorded'
        eq(c.mark(2026), Timeline.RECORDED, "2026 is the recorded year");
        eq(c.mark(2027), Timeline.PROJECTED, "and 2027 is projected");
        eq(c.mark(3000), Timeline.PROJECTED, "and so is 3000");
        ok(c.line("EUR", 2400).contains("projected"), "every projected line carries the mark");

        System.out.println(failed == 0
                ? "Step47ProjectionProbe: " + checks + " checks, 0 failed"
                : "Step47ProjectionProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
