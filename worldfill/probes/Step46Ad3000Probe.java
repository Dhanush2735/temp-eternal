/* Step 46 part 7: AD 3000, and the third mark.
   The guardrail the project chose: a projected value must never be indistinguishable from a
   recorded one. Timeline stated the rule in step 41 and NOT ONE shipped pack contains the word;
   Projector is where it gets applied. This asserts the rule holds in both directions: what is
   carried past the record says it is projected, and the four things that are never invented are
   refused rather than guessed. */
import com.eternalengine.clock.Projector;
import com.eternalengine.clock.Timeline;

import java.util.List;

public class Step46Ad3000Probe {
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
        // ---------------------------------------------------------------- 1. THE SPAN
        eq(Timeline.FIRST_YEAR, -3000, "the world begins in 3000 BC");
        eq(Timeline.LAST_YEAR, 3000, "and ends in AD 3000");
        eq(Timeline.RECORDED_UNTIL, 2026, "the record ends in AD 2026");
        ok(Timeline.inSpan(-3000), "3000 BC is answerable");
        ok(Timeline.inSpan(3000), "and so is AD 3000");
        ok(!Timeline.inSpan(-3001), "but not 3001 BC");
        ok(!Timeline.inSpan(3001), "and not AD 3001");
        ok(Projector.outOfSpanWhy(-3500).contains("before the world begins"),
                "and the reason is in words a player can read");
        ok(Projector.outOfSpanWhy(3500).contains("past the end of the world"),
                "both ways");

        // ---------------------------------------------------------------- 2. THE LINE
        ok(!Timeline.projected(2026), "AD 2026 is inside the record");
        ok(Timeline.projected(2027), "AD 2027 is not");
        ok(Timeline.projected(3000), "and AD 3000 is a projection");
        eq(Timeline.markFor(2026), "recorded", "the mark before the line is recorded");
        eq(Timeline.markFor(2027), "projected", "and after it is projected");
        eq(Timeline.readAt(2600), 2026, "a projected year is read at the last recorded one");
        eq(Timeline.readAt(1400), 1400, "and a recorded year is read as itself");

        // ---------------------------------------------------------------- 3. WHAT IS CARRIED
        // A technology that arrived stays.
        Projector.Stated tech = Projector.carry("the printing press", Projector.Carry.CONTINUATION,
                2600, "the press");
        eq(tech.mark(), "projected", "a carried technology is marked projected");
        ok(tech.phrase().contains("PROJECTED"), "and says so in capitals in the sentence");
        ok(tech.phrase().contains("2026"), "and names the last recorded year: " + tech.phrase());
        ok(tech.phrase().contains("stays"), "and gives the reason: " + tech.phrase());
        System.out.println("  " + tech.phrase());

        // The SAME value inside the record is NOT projected. This is the whole point of putting the
        // mark on the answer rather than the row.
        Projector.Stated tech1400 = Projector.carry("the printing press",
                Projector.Carry.CONTINUATION, 1400, "the press");
        eq(tech1400.mark(), "recorded", "the same value in AD 1400 is not projected");
        ok(!tech1400.phrase().contains("PROJECTED"), "and does not claim to be");

        // The sky is computed, not projected, and says which.
        Projector.Stated sky = Projector.carry("an eclipse", Projector.Carry.COMPUTATION, 2900,
                "the eclipse");
        ok(sky.phrase().contains("calculated"), "the sky is carried as calculated: " + sky.phrase());

        // A persisting state.
        Projector.Stated polity = Projector.carry("a polity", Projector.Carry.PERSISTENCE, 2400,
                "the ruling power");
        ok(polity.phrase().contains("last recorded day"),
                "a polity is carried as the state of the last recorded day");

        // Nothing recorded means nothing invented, even for a carryable kind.
        Projector.Stated empty = Projector.carry(null, Projector.Carry.PERSISTENCE, 2600,
                "ruling power");
        ok(!empty.present(), "with nothing recorded there is nothing carried");
        eq(empty.mark(), "projected", "but the answer is still marked");

        // ---------------------------------------------------------------- 4. WHAT IS REFUSED
        // THE GUARDRAIL. Four kinds are never invented, for any year after the record.
        Projector.Kind[] never = {Projector.Kind.PERSON, Projector.Kind.EVENT,
                Projector.Kind.PRICE, Projector.Kind.POPULATION};
        for (Projector.Kind k : never) {
            ok(Projector.refusal(k, 2600) != null, k + " is refused for AD 2600");
            ok(Projector.refusal(k, 2600).contains("2026"),
                    "and the refusal names the last recorded year");
            eq(Projector.refusal(k, 1400), null,
                    "but " + k + " is answered normally inside the record");
            ok(!Projector.mayCarry(k), k + " may not be carried past the record");
        }
        for (Projector.Kind k : never) {
            ok(Projector.refusal(k, 3000) != null, k + " is still refused at the far end");
        }
        System.out.println("  " + Projector.refusal(Projector.Kind.PERSON, 2600));
        ok(Projector.refusal(Projector.Kind.PERSON, 2600).contains("no ruler"),
                "and the refusal is about rulers");

        // ---------------------------------------------------------------- 5. THE POLICY IS ONE LIST
        List<String> policy = Projector.policy();
        ok(policy.size() >= 4, policy.size() + " lines of policy");
        String all = String.join(" ", policy);
        for (String need : new String[]{"3000", "carried", "never", "ANSWER"}) {
            ok(all.contains(need), "the policy mentions " + need);
        }
        ok(Projector.carried().contains("stays"), "continuations say why they are carried");
        ok(Projector.refused().contains("person") && Projector.refused().contains("population"),
                "and the refused list is four kinds: " + Projector.refused());

        // ---------------------------------------------------------------- 6. THE MARK IS A THIRD ONE
        // recorded, estimated, projected: three, and a reader can tell them apart.
        ok(!Timeline.PROJECTED.equals(Timeline.RECORDED), "projected is not recorded");
        ok(!Timeline.PROJECTED.equals(Timeline.ESTIMATED), "and not estimated");
        ok(Timeline.PROJECTED.equals("projected"), "and it is spelled the way the reader shows it");

        // ---------------------------------------------------------------- 7. THE FAR END ANSWERS
        ok(Projector.answerable(3000), "the mod answers for AD 3000");
        ok(!Projector.answerable(3001), "and refuses AD 3001 rather than guessing");
        ok(Projector.summary(2600).contains("projected"), "and says what AD 2600 is: "
                + Projector.summary(2600));
        ok(Projector.summary(1400).contains("inside the record"), "and what AD 1400 is");
        System.out.println("  " + Projector.summary(2600));

        System.out.println("== step 46 AD 3000: " + checks + " checks, " + failed + " failed ==");
        if (failed > 0) System.exit(1);
    }
}
