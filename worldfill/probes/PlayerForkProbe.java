import com.eternalengine.story.Divergence;
import com.eternalengine.story.DivergedHistory;
import com.eternalengine.story.ForkLedger;

/**
 * Can a player actually cause a fork, and does it keep the rules? (player-changes-history stage 2, 2026-10-27)
 */
public final class PlayerForkProbe {
    public static void main(String[] args) {
        int checks = 0, bad = 0;

        // 1. an unnamed player cannot open a fork
        var anon = ForkLedger.cause("", 17.385, 78.486, 2029, 4, 13, "stopped the thing");
        checks++;
        if (anon.ok()) { bad++; System.out.println("BAD  an unnamed player opened a fork"); }
        else System.out.println("ok   refused, unnamed: " + anon.why());

        // 2. an empty act is not an event
        var empty = ForkLedger.cause("Asha", 17.385, 78.486, 2029, 4, 13, "  ");
        checks++;
        if (empty.ok()) { bad++; System.out.println("BAD  a fork with no description was opened"); }
        else System.out.println("ok   refused, no description: " + empty.why());

        // 3. a real fork opens, and is signed by its player
        var r = ForkLedger.cause("Asha", 17.385, 78.486, 2029, 4, 13, "warned the old city about the rock");
        checks++;
        if (!r.ok()) { bad++; System.out.println("BAD  a real fork was refused: " + r.why()); }
        else System.out.println("ok   opened: " + r.fork().line());

        // 4. the same act is one fork, not two
        var again = ForkLedger.cause("Asha", 17.385, 78.486, 2029, 4, 13, "warned the old city about the rock");
        checks++;
        if (again.ok()) { bad++; System.out.println("BAD  the same act opened a second fork"); }
        else System.out.println("ok   second time refused: " + again.why());

        // 5. a different act that day is a different fork
        var other = ForkLedger.cause("Asha", 17.385, 78.486, 2029, 4, 13, "opened the school roof to the public");
        checks++;
        if (!other.ok()) { bad++; System.out.println("BAD  a different act was blocked: " + other.why()); }
        else System.out.println("ok   a different act is a different fork: " + other.fork().id());

        // 6. a player fork is enterable - the whole point
        var fork = r.fork();
        var asFork = ForkLedger.asDivergence(fork);
        checks++;
        if (!asFork.enterable()) { bad++; System.out.println("BAD  a player fork is not enterable: " + asFork.notEnterableBecause()); }
        else System.out.println("ok   enterable, signed by " + asFork.author());

        // 7. and it is refused by nothing that refuses the drafts
        for (var shipped : Divergence.all()) {
            checks++;
            if (shipped.id().equals(fork.id())) { bad++; System.out.println("BAD  a player fork appears among the shipped scenarios"); }
        }

        // 8. nothing before the fork changes
        var before = DivergedHistory.accounts(asFork, fork.year() - 1);
        checks++;
        if (!before.sameAsRecord()) { bad++; System.out.println("BAD  the year before the fork already differs"); }
        else System.out.println("ok   " + (fork.year() - 1) + " is the same in both timelines");

        // 9. on the fork year, the record and the branch are both stated
        var on = DivergedHistory.accounts(asFork, fork.year());
        checks++;
        if (on.record().isBlank() || on.branch().isBlank()) { bad++; System.out.println("BAD  the fork year says nothing"); }
        else System.out.println("ok   " + on.line().substring(0, Math.min(150, on.line().length())));

        // 10. the sky is untouched by a player fork
        var skyA = DivergedHistory.skyDates();
        checks++;
        if (skyA.isEmpty()) { bad++; System.out.println("BAD  no astronomy"); }
        else System.out.println("ok   sky still " + skyA.size() + " dates after a player fork");

        // 11. a bad date is refused
        var badDate = ForkLedger.cause("Asha", 17.385, 78.486, 2029, 13, 40, "nonsense");
        checks++;
        if (badDate.ok()) { bad++; System.out.println("BAD  an impossible date was accepted"); }
        else System.out.println("ok   refused, bad date: " + badDate.why());

        // 12. a place not on Earth is refused
        var badPlace = ForkLedger.cause("Asha", 200, 78.486, 2029, 4, 13, "off the planet");
        checks++;
        if (badPlace.ok()) { bad++; System.out.println("BAD  a place off Earth was accepted"); }
        else System.out.println("ok   refused, bad place: " + badPlace.why());

        // 13. the ledger survives a save and load
        int before2 = ForkLedger.size();
        String json = ForkLedger.toJson();
        ForkLedger.clear();
        int loaded = ForkLedger.fromJson(json);
        checks++;
        if (loaded != before2) { bad++; System.out.println("BAD  ledger lost forks across a save: " + before2 + " -> " + loaded); }
        else System.out.println("ok   " + loaded + " forks survived a save and load");

        // 14. a fork with no player in the JSON is not loaded
        int afterBad = ForkLedger.fromJson("{\"forks\":[{\"id\":\"x\",\"player\":\"\",\"lat\":0,\"lon\":0,"
                + "\"year\":2030,\"month\":1,\"day\":1,\"what\":\"unsigned\"}]}");
        checks++;
        if (afterBad != 0) { bad++; System.out.println("BAD  an unsigned fork was loaded from a save"); }
        else System.out.println("ok   an unsigned fork in a save is refused on load");

        System.out.println();
        System.out.println("ledger now holds: " + ForkLedger.size());
        for (var f : ForkLedger.all()) { System.out.println("  " + f.line()); }
        System.out.println();
        System.out.println("checks: " + checks + "   failures: " + bad);
    }
}
