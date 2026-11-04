/* Step 52 part 4 (A11): time for several players, at once. The claim: one world has one date and one timeline;
   different years at once means different universes, lawfully, with nobody moving anybody else; a shared date
   moves everyone in it and takes their vote or an operator; and a private year in a shared world is refused,
   always, and the refusal explains the two ways that do work. */
import com.eternalengine.clock.Clocks;
import com.eternalengine.clock.Clocks.Standing;
import com.eternalengine.player.Permissions.Action;
import com.eternalengine.player.Permissions.Actor;
import com.eternalengine.player.Permissions.Decision;
import com.eternalengine.player.Permissions.Vote;

import java.util.List;

public class Step52ClockProbe {
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

    static void refused(Decision d, String words, String what) {
        checks++;
        if (d.allowed()) {
            failed++;
            System.out.println("  FAIL " + what + "  (it was allowed)");
            return;
        }
        if (d.why().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no reason says \"" + words + "\"; got " + d.why());
    }

    static void allowed(Decision d, String what) {
        checks++;
        if (!d.allowed()) {
            failed++;
            System.out.println("  FAIL " + what + "  (" + d.why() + ")");
        }
    }

    public static void main(String[] args) {
        Actor sam = Actor.of("Sam", false);
        Actor ada = Actor.of("Ada", true);
        Actor mira = Actor.of("Mira", false);

        // ------------------------------------------------ 1. FOUR WORLDS, FOUR ERAS, AT ONCE
        Clocks clocks = Clocks.empty();
        allowed(clocks.openWorld("ur", -2960, "main"), "a world opens in 2960 BC");
        allowed(clocks.openWorld("cuzco", 1576, "main"), "one in 1576");
        allowed(clocks.openWorld("delhi", 1900, "main"), "one in 1900");
        allowed(clocks.openWorld("shore", 2200, "b1"), "and one in 2200, already on a branch");
        refused(clocks.openWorld("ur", -2900, "main"), "already exists", "two worlds with one name are refused");
        refused(clocks.openWorld("nowhere", 1900, ""), "which timeline", "a world must say its timeline");
        refused(clocks.openWorld("before", -3001, "main"), "before it", "nothing before 3000 BC");
        refused(clocks.openWorld("after", 3001, "main"), "after it", "and nothing after AD 3000");
        allowed(clocks.openWorld("first", -3000, "main"), "3000 BC itself is in");
        allowed(clocks.openWorld("last", 3000, "main"), "and so is AD 3000");

        // ------------------------------------------------ 2. WHO STANDS WHERE
        allowed(clocks.join("Sam", "delhi"), "Sam enters Delhi");
        allowed(clocks.join("Mira", "delhi"), "Mira enters Delhi");
        allowed(clocks.join("Rafi", "delhi"), "Rafi enters Delhi");
        allowed(clocks.join("Ninlil", "ur"), "and Ninlil is in Ur, 2960 BC, at the same time");
        allowed(clocks.join("Mira", "cuzco"), "Mira moves to Cuzco");
        Standing miraStands = clocks.standingOf("Mira");
        eq(miraStands.universe(), "cuzco", "Mira stands in Cuzco now");
        eq(miraStands.year(), 1576, "in 1576");
        eq(clocks.peopleIn("delhi"), 2, "and Delhi holds 2 people now");
        eq(clocks.standingOf("nobody"), null, "a stranger stands nowhere");
        refused(clocks.join("Sam", "atlantis"), "no universe called atlantis", "entering nowhere is refused");
        refused(clocks.join("  ", "delhi"), "nobody cannot enter", "and nobody cannot enter anywhere");
        refused(clocks.join("Sam", "delhi"), "already in", "entering where you stand is refused");

        // Three players, three years, at once - the question A11 asks.
        for (Standing s : clocks.standings()) System.out.println("     " + s.line());
        eq(clocks.standings().size(), 4, "four people stand in four places");
        eq(clocks.yearOf("ur"), -2960, "Ur is in 2960 BC");
        eq(clocks.yearOf("cuzco"), 1576, "Cuzco in 1576");
        eq(clocks.yearOf("delhi"), 1900, "Delhi in 1900");
        eq(clocks.branchOf("shore"), "b1", "and the shore is on branch b1 while the rest are on main");

        // ------------------------------------------------ 3. A SHARED DATE MOVES EVERYONE IN IT
        // Sam is alone in Delhi's date question? No: Delhi holds Sam and Rafi. It takes their vote.
        refused(clocks.moveDate(sam, "delhi", 1947, null, "the world changes"), "takes their vote",
                "a player alone cannot move a date two people share");
        // Sam does not stand in Cuzco, so Sam cannot move it however empty it looks.
        refused(clocks.moveDate(sam, "cuzco", 1577, null, "a year passes"), "does not stand in",
                "a player may not move a world they are not in");
        // Ninlil is alone in Ur: moving its date moves nobody else.
        allowed(clocks.moveDate(Actor.of("Ninlil", false), "ur", -2959, null, "a year passes"),
                "alone in the world, moving its date moves only you");
        eq(clocks.yearOf("ur"), -2959, "Ur is in 2959 BC now");
        eq(clocks.yearOf("cuzco"), 1576, "and Cuzco has not moved: nobody in Ur can move it");
        eq(clocks.standingOf("Ninlil").year(), -2959, "and Ninlil moved with her world");
        // An operator moves anything, anywhere.
        allowed(clocks.moveDate(ada, "delhi", 1947, null, "independence"), "an operator moves Delhi for everyone");
        eq(clocks.yearOf("delhi"), 1947, "Delhi is in 1947");
        eq(clocks.standingOf("Sam").year(), 1947, "Sam moved with it");
        eq(clocks.standingOf("Rafi").year(), 1947, "and so did Rafi");
        eq(clocks.yearOf("cuzco"), 1576, "Cuzco still did not move");

        // ------------------------------------------------ 4. THE VOTE PATH
        Vote.Opened asked = Vote.open(Action.MOVE_WORLD_TIME, "delhi", sam, List.of("Sam", "Rafi"));
        ok(asked.ok(), "a vote opens about Delhi's date: " + (asked.ok() ? "" : asked.refused()));
        Vote vote = asked.vote();
        allowed(vote.cast(sam, true), "Sam votes");
        allowed(vote.cast(Actor.of("Rafi", false), true), "Rafi votes");
        allowed(vote.close(sam), "and the vote closes");
        ok(vote.passed(), "and passes: both people it moves said yes");
        allowed(clocks.moveDate(sam, "delhi", 2026, vote, "the present"), "with the vote, Sam may move Delhi");
        eq(clocks.yearOf("delhi"), 2026, "Delhi is in 2026");

        // A vote about the wrong thing is refused here, not stretched.
        Vote.Opened wrongAct = Vote.open(Action.SPLIT_TIMELINE, "delhi", sam, List.of("Sam", "Rafi"));
        ok(wrongAct.ok(), "a split vote opens");
        Vote wv = wrongAct.vote();
        wv.cast(sam, true);
        wv.cast(Actor.of("Rafi", false), true);
        wv.close(sam);
        refused(clocks.moveDate(sam, "delhi", 2027, wv, "wrong act"), "not move the shared date",
                "a vote about splitting is not a vote about the date");
        Vote.Opened wrongWorld = Vote.open(Action.MOVE_WORLD_TIME, "ur", sam, List.of("Sam", "Rafi"));
        Vote ww = wrongWorld.vote();
        ww.cast(sam, true);
        ww.cast(Actor.of("Rafi", false), true);
        ww.close(sam);
        refused(clocks.moveDate(sam, "delhi", 2027, ww, "wrong world"), "not delhi",
                "a vote about another world is refused here");
        Vote.Opened notYet = Vote.open(Action.MOVE_WORLD_TIME, "delhi", sam, List.of("Sam", "Rafi"));
        refused(clocks.moveDate(sam, "delhi", 2027, notYet.vote(), "not closed"), "has not passed",
                "an open vote is not authority");

        // ------------------------------------------------ 5. A PRIVATE YEAR IS ALWAYS REFUSED
        refused(clocks.jumpSelf(sam, "Sam", 1857), "one world has one date",
                "no player gets a private year in a shared world");
        refused(clocks.jumpSelf(sam, "Sam", 1857), "another universe",
                "and the refusal names the ways that do work");
        refused(clocks.jumpSelf(sam, "Sam", 1857), "move the shared date", "both of them");
        eq(clocks.standingOf("Sam").year(), 2026, "and Sam is still where the world is");

        // ------------------------------------------------ 6. THE TIMELINE MOVES THE SAME WAY
        refused(clocks.moveBranch(sam, "delhi", "b1", null, "a branch"), "takes their vote",
                "switching the shared timeline is the same kind of act");
        refused(clocks.moveBranch(sam, "cuzco", "b1", null, "a branch"), "does not stand in",
                "and the same membership rule holds");
        allowed(clocks.moveBranch(ada, "delhi", "b1", null, "the split lands"), "an operator switches it");
        eq(clocks.branchOf("delhi"), "b1", "Delhi is on b1 now");
        eq(clocks.branchOf("ur"), "main", "Ur is not: a branch is per world");
        refused(clocks.moveBranch(ada, "delhi", "b1", null, "again"), "already on", "not twice");
        refused(clocks.moveBranch(ada, "delhi", "  ", null, "blank"), "switch to what timeline",
                "and not to nowhere");

        // ------------------------------------------------ 7. THE TABLE
        for (String line : clocks.table()) System.out.println("     " + line);
        ok(clocks.table().get(0).contains("person"), "the table counts the people of each world: "
                + clocks.table().get(0));
        eq(clocks.universes().size(), 6, "and every world that opened is on it (the two beyond the "
                + "project's years were refused and do not exist)");
        refused(clocks.moveDate(sam, "delhi", 2027, null, "same"), "takes their vote",
                "Sam still needs a vote for Delhi");
        refused(clocks.moveDate(sam, "atlantis", 1900, null, "x"), "no universe called atlantis",
                "moving nowhere is refused");
        refused(clocks.moveDate(sam, "delhi", 2027, wv, "bounds"), "not move the shared date",
                "the wrong vote is still refused");
        allowed(clocks.moveDate(ada, "first", -2999, null, "the edges move too"), "the edges of the timeline "
                + "move like anywhere else");
        eq(clocks.yearOf("first"), -2999, "3000 BC's world is in 2999 BC");

        System.out.println("\nStep 52 part 4: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
