/* Step 52 part 3 (A16): who may move time, change history or use the admin commands when several people play.
   The claim: the server axis has three kinds of act, not one blunt operator test; an act that moves several
   people takes THEIR vote (not a show of hands among bystanders) or an operator; and an act that rewrites what
   is recorded is refused to everyone else however alone they are. */
import com.eternalengine.player.Permissions;
import com.eternalengine.player.Permissions.Action;
import com.eternalengine.player.Permissions.Actor;
import com.eternalengine.player.Permissions.Decision;
import com.eternalengine.player.Permissions.Rank;
import com.eternalengine.player.Permissions.Vote;

import java.util.List;

public class Step52PermissionProbe {
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

    static void noVote(Vote.Opened o, String words, String what) {
        checks++;
        if (o.ok()) {
            failed++;
            System.out.println("  FAIL " + what + "  (a vote was opened)");
            return;
        }
        if (o.refused().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no reason says \"" + words + "\"; got " + o.refused());
    }

    public static void main(String[] args) {
        Actor sam = Actor.of("Sam", false);
        Actor ada = Actor.of("Ada", true);          // an operator
        Actor mira = Actor.of("Mira", false);

        // ------------------------------------------------ 1. MOVES ONLY YOU: ANYONE, ANY TIME
        for (Action a : List.of(Action.ENTER_UNIVERSE, Action.CLAIM_PROPERTY, Action.TAKE_BACKUP, Action.VOTE)) {
            ok(Permissions.mayAlone(sam, a, 100).allowed(), "anybody may " + a.words() + ", however many "
                    + "people are about");
        }
        ok(Permissions.mayAlone(sam, Action.TAKE_BACKUP, 5).why().contains("nobody else"),
                "and the reason says why it needs nobody: "
                        + Permissions.mayAlone(sam, Action.TAKE_BACKUP, 5).why());

        // ------------------------------------------------ 2. MOVES THE SHARED WORLD: ALONE YES, SEVERAL NEEDS MORE
        ok(Permissions.mayAlone(sam, Action.MOVE_WORLD_TIME, 1).allowed(),
                "alone, moving the shared date moves only you");
        refused(Permissions.mayAlone(sam, Action.MOVE_WORLD_TIME, 4), "takes their vote",
                "with four people moved it takes their vote or an operator");
        refused(Permissions.mayAlone(sam, Action.SPLIT_TIMELINE, 2), "or an operator",
                "splitting the shared timeline is the same kind of act");
        ok(Permissions.mayAlone(ada, Action.MOVE_WORLD_TIME, 4).allowed(),
                "an operator may move it for everyone without asking");
        ok(Permissions.mayAlone(ada, Action.MOVE_WORLD_TIME, 4).why().contains("without asking"),
                "and the reason says so: " + Permissions.mayAlone(ada, Action.MOVE_WORLD_TIME, 4).why());

        // ------------------------------------------------ 3. REWRITES: OPERATORS ONLY, ALONE OR NOT
        for (Action a : List.of(Action.RESTORE_BACKUP, Action.USE_ADMIN, Action.CHANGE_HISTORY,
                Action.EDIT_ANY_PROPERTY)) {
            refused(Permissions.mayAlone(sam, a, 1), "operators only",
                    "alone, a player still may not " + a.words());
            ok(Permissions.mayAlone(ada, a, 1).allowed(), "but an operator may " + a.words());
        }
        refused(Permissions.mayAlone(sam, Action.RESTORE_BACKUP, 1), "rewrites what is already recorded",
                "and the refusal says what is special about it");

        // ------------------------------------------------ 4. A VOTE IS OF THE PEOPLE IT MOVES
        Vote.Opened asked = Vote.open(Action.MOVE_WORLD_TIME, "Delhi, 1857", sam,
                List.of("Sam", "Mira", "Ada"));
        ok(asked.ok(), "a vote opens when several people are moved: " + (asked.ok() ? "" : asked.refused()));
        Vote vote = asked.vote();
        for (String line : vote.log()) System.out.println("     " + line);

        ok(vote.cast(sam, true).allowed(), "a person the act moves may vote");
        refused(vote.cast(sam, true), "already voted", "but only once");
        refused(vote.cast(Actor.of("Rafi", false), true), "is not moved by this act",
                "and a bystander may not vote at all");
        ok(vote.cast(Actor.of("Rafi", false), true).why().contains("Sam, Mira, Ada"),
                "and the refusal names who may: " + vote.cast(Actor.of("Rafi", false), true).why());

        refused(vote.close(sam), "have not spoken", "the vote cannot close while somebody moved is silent");
        ok(vote.cast(mira, false).allowed(), "an operator's word counts like anybody's");
        ok(vote.cast(ada, false).allowed(), "and so does another's");
        Decision closed = vote.close(sam);
        // 1 yes of 3 is not more than half of 3. (2 of 3 WOULD be: the first version of this probe said it
        // would not, and the arithmetic was the probe's, not the class's.)
        ok(!closed.allowed(), "1 yes of 3 is not more than half of 3: " + closed.why());
        ok(closed.why().contains("not more than half"), "and the count is said in words");
        ok(vote.isClosed() && !vote.passed(), "the vote is closed and did not pass");
        refused(vote.cast(sam, true), "closed", "and nobody votes after it closes");

        // ------------------------------------------------ 5. PASSES ONLY ON A MAJORITY OF THE MOVED
        Vote.Opened asked2 = Vote.open(Action.MOVE_WORLD_TIME, "Cuzco, 1576", sam,
                List.of("Sam", "Mira", "Ada", "Rafi"));
        ok(asked2.ok(), "a second vote opens");
        Vote v2 = asked2.vote();
        v2.cast(sam, true);
        v2.cast(mira, true);
        v2.cast(ada, true);
        v2.cast(Actor.of("Rafi", false), false);
        Decision c2 = v2.close(sam);
        ok(c2.allowed(), "3 yes of 4 is more than half of 4: " + c2.why());
        ok(v2.passed(), "and it passed");
        for (String line : v2.log()) System.out.println("     " + line);

        // ------------------------------------------------ 6. OPERATORS DO NOT NEED VOTES, AND SAY WHY WHEN THEY ACT
        noVote(Vote.open(Action.MOVE_WORLD_TIME, "Ur, -2960", ada, List.of("Ada", "Sam")),
                "without a vote", "an operator's act needs no vote");
        noVote(Vote.open(Action.MOVE_WORLD_TIME, "Ur, -2960", sam, List.of("Sam")),
                "nobody but Sam", "an act that moves only the proposer needs no vote");
        noVote(Vote.open(Action.RESTORE_BACKUP, "Delhi, 1857", sam, List.of("Sam", "Mira")),
                "operators only", "a vote cannot hand out what rank withholds");
        noVote(Vote.open(Action.TAKE_BACKUP, "Delhi, 1857", sam, List.of("Sam", "Mira")),
                "nothing to vote about", "an act that moves nobody is not voted on");
        noVote(Vote.open(Action.MOVE_WORLD_TIME, "Delhi, 1857", sam, List.of()),
                "decides nothing", "a vote of nobody is refused");
        noVote(Vote.open(Action.MOVE_WORLD_TIME, "Delhi, 1857", sam, List.of("Sam", "sam")),
                "listed twice", "and one name listed twice is a question");

        // An operator closing early, and a non-operator trying the same.
        Vote.Opened asked3 = Vote.open(Action.SPLIT_TIMELINE, "Delhi, 1857", sam,
                List.of("Sam", "Mira", "Ada", "Rafi"));
        Vote v3 = asked3.vote();
        v3.cast(sam, true);
        refused(v3.close(mira), "have not spoken", "only an operator closes a vote early");
        Decision byHand = v3.close(ada);
        ok(byHand.allowed(), "an operator may: " + byHand.why());
        ok(byHand.why().contains("closed it early"), "and the record says it was closed early");
        ok(v3.passed(), "and the act stands");

        Vote.Opened asked4 = Vote.open(Action.MOVE_WORLD_TIME, "Delhi, 2026", sam,
                List.of("Sam", "Mira", "Ada"));
        Vote v4 = asked4.vote();
        refused(v4.override(sam, "I want to"), "cannot close a vote by hand", "a player cannot override");
        ok(v4.override(ada, "the server is empty tonight").allowed(),
                "an operator can, and gives a reason");
        ok(v4.log().get(v4.log().size() - 1).contains("the server is empty tonight"),
                "and the reason is kept in the vote's log");
        refused(v4.override(ada, "again"), "already closed", "not twice");

        // ------------------------------------------------ 7. THE TABLE AND THE RULE LINE
        for (String line : Permissions.table()) System.out.println("     " + line);
        eq(Permissions.table().size(), 14, "the table lists every act in its kind (3 headings + 11 acts)");
        ok(Permissions.table().get(0).contains("moves only you"), "and says which kind is which");
        System.out.println("     " + Permissions.ruleLine());
        ok(Permissions.ruleLine().contains("operators only"), "the rule line names the third kind");
        refused(Permissions.mayAlone(null, Action.USE_ADMIN, 1), "nobody asking", "no actor, no answer");
        refused(Permissions.mayAlone(sam, null, 1), "no act named", "no act, no answer");

        System.out.println("\nStep 52 part 3: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
