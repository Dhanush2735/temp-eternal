/* Step 48 part 5 (F9): how a player reaches another year.
   The claim: there is one date for the world, the clock runs forward by itself, and going back is an
   operator's command that forks the world rather than undoing it. */
import com.eternalengine.clock.TimeTravel;
import com.eternalengine.clock.Timeline;

import java.util.List;

public class Step48TravelProbe {
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
        // ------------------------------------------------ 1. ONE SPAN, AND THE EDGES OF IT
        eq(Timeline.FIRST_YEAR, -3000, "the world starts at 3000 BC");
        eq(Timeline.LAST_YEAR, 3000, "and ends at AD 3000");
        eq(Timeline.RECORDED_UNTIL, 2026, "with records to 2026 and projection after");

        // ------------------------------------------------ 2. A PLAYER MAY NOT MOVE THE CLOCK AT ALL
        TimeTravel.Verdict playerForward = TimeTravel.judge(1200, 1201, TimeTravel.Who.PLAYER);
        ok(!playerForward.allowed(), "a player cannot move the clock even one year forward");
        ok(playerForward.because().contains("every player"),
                "and the reason is the shared date, not the permission: " + playerForward.because());
        ok(!TimeTravel.judge(1200, 1100, TimeTravel.Who.PLAYER).allowed(),
                "and certainly not backward");

        // ------------------------------------------------ 3. THE CLOCK ITSELF ONLY RUNS FORWARD
        ok(TimeTravel.judge(1200, 1201, TimeTravel.Who.CLOCK).allowed(),
                "the clock moves forward on its own");
        ok(!TimeTravel.judge(1200, 1199, TimeTravel.Who.CLOCK).allowed(),
                "and never backward, even by a year");
        ok(TimeTravel.judge(1200, 1199, TimeTravel.Who.CLOCK).because().contains("second author"),
                "because a clock that turned back would be a second author of history: "
                        + TimeTravel.judge(1200, 1199, TimeTravel.Who.CLOCK).because());

        // ------------------------------------------------ 4. THE OPERATOR'S DOOR, BOTH WAYS
        TimeTravel.Verdict opForward = TimeTravel.judge(1200, 1300, TimeTravel.Who.OPERATOR);
        ok(opForward.allowed(), "an operator may move the clock forward");
        eq(opForward.effect(), TimeTravel.Effect.FORWARD_RECORDED, "and still be inside the records");
        ok(!opForward.forks(), "with no fork, because nothing was changed");
        ok(opForward.because().contains("100 years"), "and the line says how far: " + opForward.because());

        TimeTravel.Verdict opBack = TimeTravel.judge(1300, 1200, TimeTravel.Who.OPERATOR);
        ok(opBack.allowed(), "an operator may also move it back");
        eq(opBack.effect(), TimeTravel.Effect.BACK_INTO_RECORD, "into recorded years");
        ok(opBack.forks(), "and that forking is the whole of what going back means");
        ok(opBack.because().contains("forks"), "said plainly: " + opBack.because());
        ok(opBack.because().contains("undone"),
                "and it says nothing seen is undone: " + opBack.because());

        // ------------------------------------------------ 5. THE SEAM, BOTH WAYS
        TimeTravel.Verdict past = TimeTravel.judge(2000, 2400, TimeTravel.Who.OPERATOR);
        eq(past.effect(), TimeTravel.Effect.FORWARD_UNWRITTEN, "crossing 2026 forward is a change of "
                + "authority and not of scenery");
        ok(past.crossesSeam(), "and it is a seam crossing");
        ok(past.because().contains("writes its own history"),
                "the line says so: " + past.because());
        ok(!past.forks(), "no fork is needed, because there is no record there to fork");
        TimeTravel.Verdict back = TimeTravel.judge(2400, 2000, TimeTravel.Who.OPERATOR);
        eq(back.effect(), TimeTravel.Effect.BACK_INTO_RECORD, "and crossing it back resumes the record");
        ok(back.crossesSeam(), "also a seam crossing");
        ok(back.because().contains("The packs answer again"), "said plainly: " + back.because());
        ok(back.forks(), "and it forks, because it lands in a year the packs own");

        // Backward but staying past the seam: the years were this world's own, so nothing forks.
        TimeTravel.Verdict backOwn = TimeTravel.judge(2400, 2300, TimeTravel.Who.OPERATOR);
        eq(backOwn.effect(), TimeTravel.Effect.BACK_UNWRITTEN,
                "going back inside the unwritten years is its own case, which the first run of this "
                        + "probe found missing from the enum");
        ok(!backOwn.crossesSeam(), "it does not cross the seam");
        ok(!backOwn.forks(), "and it does not fork, because there is no record to fork: "
                + backOwn.because());

        // Exactly at the seam, on both sides: 2026 is recorded, 2027 is not.
        eq(TimeTravel.effectOf(2026, 2027), TimeTravel.Effect.FORWARD_UNWRITTEN,
                "2026 is the last recorded year and 2027 the first unwritten one");
        eq(TimeTravel.effectOf(2027, 2026), TimeTravel.Effect.BACK_INTO_RECORD, "in either direction");
        eq(TimeTravel.effectOf(2026, 2025), TimeTravel.Effect.BACK_INTO_RECORD,
                "and inside the record a backward step is a fork");

        // ------------------------------------------------ 6. THE EDGES REFUSE, AND SAY WHY
        TimeTravel.Verdict beyond = TimeTravel.judge(2900, 3500, TimeTravel.Who.OPERATOR);
        ok(!beyond.allowed(), "AD 3500 is outside the world");
        ok(beyond.because().contains("3000"), "and the refusal names the span: " + beyond.because());
        ok(beyond.because().contains("empty room"),
                "with the reason that matters: " + beyond.because());
        ok(!TimeTravel.judge(1200, -4000, TimeTravel.Who.OPERATOR).allowed(),
                "and 4000 BC is outside it too");
        ok(TimeTravel.judge(1200, -3000, TimeTravel.Who.OPERATOR).allowed(),
                "while 3000 BC, the first year, is inside");
        ok(TimeTravel.judge(2999, 3000, TimeTravel.Who.OPERATOR).allowed(),
                "and so is AD 3000, the last");

        // Staying put is allowed for everybody, including a player.
        TimeTravel.Verdict stays = TimeTravel.judge(1200, 1200, TimeTravel.Who.PLAYER);
        ok(stays.allowed(), "a player asking to stay where they are is not refused");
        eq(stays.effect(), TimeTravel.Effect.STAYS, "nothing happens");
        ok(!stays.forks(), "and nothing forks");

        // ------------------------------------------------ 7. WHAT A JUMP LEAVES BEHIND
        ok(TimeTravel.leavesGap(TimeTravel.Effect.FORWARD_UNWRITTEN),
                "a jump past the seam leaves years nobody lived through");
        ok(TimeTravel.leavesGap(TimeTravel.Effect.BACK_INTO_RECORD), "in either direction");
        ok(!TimeTravel.leavesGap(TimeTravel.Effect.BACK_UNWRITTEN),
                "while going back inside this world's own history leaves no gap at all");
        ok(!TimeTravel.leavesGap(TimeTravel.Effect.FORWARD_RECORDED),
                "a jump inside the records leaves no gap, because the packs fill it");
        ok(TimeTravel.chronicleNote(TimeTravel.Effect.FORWARD_UNWRITTEN) == null,
                "and none of it is written into the chronicle: the clock is not the world, and a line "
                        + "about the clock would be a line about the reader");

        // ------------------------------------------------ 8. THE DOORWAYS, IN THE RIGHT ORDER
        List<String> doors = TimeTravel.doorways();
        eq(doors.size(), 4, "there are four ways to be in another year");
        ok(doors.get(0).startsWith("let the clock run"),
                "and the slow one comes first, because that is the way the game is played: " + doors.get(0));
        ok(doors.get(3).contains("/ee date"), "the command is last and named as an operator's");
        ok(doors.get(1).contains("travel"),
                "and travel is in the list, because it is most of what people mean: " + doors.get(1));

        // ------------------------------------------------ 9. THE REFUSALS SOMEBODY WILL ASK FOR
        for (TimeTravel.Refused r : TimeTravel.Refused.values()) {
            ok(r.why().length() > 40, r + " is refused in a sentence rather than a shrug");
        }
        ok(TimeTravel.Refused.A_CLOCK_PER_PLAYER.why().contains("two different villages"),
                "the per-player clock is refused for the pack's reason: "
                        + TimeTravel.Refused.A_CLOCK_PER_PLAYER.why());
        ok(TimeTravel.Refused.A_FREE_MACHINE.why().contains("prop"),
                "and the time machine item is named as what it is: "
                        + TimeTravel.Refused.A_FREE_MACHINE.why());

        System.out.println("  " + TimeTravel.ruleLine(1200));
        System.out.println("  " + opBack.words());
        System.out.println("  " + past.words());
        System.out.println(failed == 0
                ? "Step48TravelProbe: " + checks + " checks, 0 failed"
                : "Step48TravelProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
