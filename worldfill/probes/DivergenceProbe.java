import com.eternalengine.story.Divergence;
import com.eternalengine.story.DivergedHistory;

/**
 * Can a player's fork be addressed, and does it keep the two rules? (player-changes-history, 2026-10-27)
 *
 * <p>Rule 1: nothing before the fork changes. Rule 2: the sky is identical in every timeline.
 */
public final class DivergenceProbe {
    public static void main(String[] args) {
        var forks = Divergence.all();
        System.out.println("forks found: " + forks.size());
        for (var f : forks) {
            System.out.println("  " + f);
        }
        System.out.println();

        int checks = 0, bad = 0;
        for (var f : forks) {
            System.out.println("=== " + f.id() + " (fork at " + f.triggerYear() + ") ===");
            // rule 1: the year before the fork is identical in both timelines
            var before = DivergedHistory.accounts(f, f.triggerYear() - 1);
            checks++;
            if (!before.sameAsRecord()) {
                bad++;
                System.out.println("  BAD  the year before the fork already differs: " + before.line());
            } else {
                System.out.println("  ok   " + before.year() + " is the same in both timelines");
            }
            // every changed year must say what the record had and what the branch has
            for (int y : DivergedHistory.changedYears(f)) {
                var two = DivergedHistory.accounts(f, y);
                checks++;
                boolean ok = !two.record().isBlank() && !two.branch().isBlank();
                if (!ok) {
                    bad++;
                }
                System.out.println("  " + (ok ? "ok  " : "BAD ") + " " + two.line());
            }
            System.out.println("  sky, from inside this fork: " + DivergedHistory.skyDates(f).size() + " dates");
        }

        // rule 2: the sky is the same list for every fork
        var first = forks.isEmpty() ? java.util.List.<String>of() : DivergedHistory.skyDates(forks.get(0));
        for (var f : forks) {
            checks++;
            if (!DivergedHistory.skyDates(f).equals(first)) {
                bad++;
                System.out.println("BAD  " + f.id() + " has a different sky");
            }
        }
        System.out.println();
        System.out.println("sky dates, identical in every fork: " + first.size());
        if (!first.isEmpty()) {
            System.out.println("  first: " + first.get(0) + "   last: " + first.get(first.size() - 1));
        }
        System.out.println();
        System.out.println("checks: " + checks + "   failures: " + bad);
        System.out.println();
        System.out.println("enterable by a player today: "
                + forks.stream().filter(Divergence::enterable).count() + " of " + forks.size());
        for (var f : forks) {
            if (!f.enterable()) {
                System.out.println("  blocked: " + f.id() + " - " + f.notEnterableBecause());
            }
        }
    }
}
