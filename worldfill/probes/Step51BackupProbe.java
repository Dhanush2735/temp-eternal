/* Step 51 part 4 (A17): a copy of the world taken before a big change, and not by the clock.
   The claim: the copy before a jump, a split or a rupture is taken by the code doing the damage, it is open
   until that change is answered, a second copy of the same kind is refused while one is open, and a timed copy
   is not a substitute. */
import com.eternalengine.timeline.BeforeChange;
import com.eternalengine.timeline.BranchSave;

import java.util.Map;
import java.util.TreeMap;

public class Step51BackupProbe {
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

    static BranchSave.Snapshot state(int year, String branch, String... kv) {
        Map<String, String> f = new TreeMap<>();
        for (int i = 0; i < kv.length; i += 2) f.put(kv[i], kv[i + 1]);
        return BranchSave.Snapshot.of(f, year, branch);
    }

    public static void main(String[] args) {
        BranchSave.Snapshot before = state(1857, "main",
                "event.triggered.sepoy_mutiny", "1857", "tech.flag_rail", "1853", "climate.flag_year", "cold");
        BeforeChange list = BeforeChange.empty();

        // ------------------------------------------------ 1. THE COPY BEFORE THE CHANGE
        BeforeChange.Taken t = list.take(BeforeChange.ChangeKind.TIME_JUMP, before, "the player asked to jump to 1947");
        ok(t.ok(), "a copy is taken before a time jump: " + t.line());
        list = t.list();
        eq(list.size(), 1, "one copy kept");
        BeforeChange.Backup b1 = t.made();
        ok(b1.open(), "and it is open until the change is answered");
        eq(b1.year(), 1857, "it remembers the year it was taken in");
        eq(b1.branch(), "main", "and the branch");
        ok(b1.line().contains("STILL OPEN"), "and says so on its own line: " + b1.line());
        eq(list.undo(b1.id()).flags(), before.flags(), "undoing it puts the world back exactly");
        eq(list.undo(b1.id()).year(), 1857, "year and all");
        System.out.println("     " + b1.line());

        // ------------------------------------------------ 2. THE SECOND COPY OF THE SAME KIND IS REFUSED
        BeforeChange.Taken again = list.take(BeforeChange.ChangeKind.TIME_JUMP, before, "another jump");
        ok(!again.ok(), "a second copy is refused while the first is open");
        ok(again.refused().why().contains(b1.id()), "and the refusal names the open one: " + again.refused().why());
        eq(again.list().size(), 1, "nothing was added");
        System.out.println("     " + again.line());

        // A different kind is not blocked by it: a rupture while a jump is open is a different change.
        BeforeChange.Taken rupture = list.take(BeforeChange.ChangeKind.RUPTURE, before, "physics broke");
        ok(rupture.ok(), "a copy for a different kind of change is still taken");
        list = rupture.list();
        eq(list.size(), 2, "so two copies now");
        eq(list.openIds().size(), 2, "both open");
        eq(list.latest().kind(), BeforeChange.ChangeKind.RUPTURE, "and the newest is the rupture");
        eq(list.latestFor(BeforeChange.ChangeKind.TIME_JUMP).id(), b1.id(), "the jump's copy is still findable by kind");

        // ------------------------------------------------ 3. THE CHANGE IS ANSWERED
        list = list.complete(b1.id());
        ok(!list.get(b1.id()).open(), "the copy stops being open when the change is done");
        eq(list.openIds().size(), 1, "one still open");
        BeforeChange.Taken second = list.take(BeforeChange.ChangeKind.TIME_JUMP, before, "the player jumps again");
        ok(second.ok(), "so a new jump can take a new copy");
        list = second.list();
        eq(list.size(), 3, "three copies");
        eq(list.latestFor(BeforeChange.ChangeKind.TIME_JUMP).id(), second.made().id(), "and the newest of the "
                + "jumps' copies is the new one");

        // ------------------------------------------------ 4. A TIMED COPY IS NOT A SUBSTITUTE
        ok(list.whyTimedCopiesDoNotCount().contains("every half hour"), "the class says what the timed copies are");
        ok(list.whyTimedCopiesDoNotCount().contains("predates it"), "and why none of them is the one you need");
        eq(BeforeChange.empty().latestFor(BeforeChange.ChangeKind.RUPTURE), null,
                "a world whose only copies are the timed ones has no before-change backup for a rupture");

        // ------------------------------------------------ 5. NOT EVERY CHANGE DESERVES ONE
        BeforeChange.Taken flag = list.take(BeforeChange.ChangeKind.FLAG, before, "the climate engine set a flag");
        ok(!flag.ok(), "an engine's flag does not take a copy");
        ok(flag.refused().why().contains("does not take a backup"), "and the refusal says why: " + flag.refused().why());
        ok(BeforeChange.ChangeKind.TIME_JUMP.needsBackup(), "a jump does");
        ok(BeforeChange.ChangeKind.TIMELINE_SPLIT.needsBackup(), "so does a split");
        ok(BeforeChange.ChangeKind.RUPTURE.needsBackup(), "and a rupture");
        ok(!BeforeChange.ChangeKind.FLAG.needsBackup(), "and a flag does not");

        // ------------------------------------------------ 6. ROTATION KEEPS THE OPEN ONE
        BeforeChange small = BeforeChange.empty(3);
        BranchSave.Snapshot s1900 = state(1900, "main", "a", "1");
        BeforeChange.Taken a1 = small.take(BeforeChange.ChangeKind.RUPTURE, s1900, "first");
        small = a1.list().complete(a1.made().id());
        BeforeChange.Taken a2 = small.take(BeforeChange.ChangeKind.RUPTURE, s1900, "second");
        small = a2.list().complete(a2.made().id());
        BeforeChange.Taken a3 = small.take(BeforeChange.ChangeKind.TIME_JUMP, s1900, "third");
        small = a3.list();   // left open on purpose
        eq(small.size(), 3, "three kept, which is the limit");
        BeforeChange.Taken a4 = small.take(BeforeChange.ChangeKind.TIMELINE_SPLIT, s1900, "fourth");
        ok(a4.ok(), "a fourth is still taken");
        small = a4.list();
        eq(small.size(), 3, "and the list stays at three");
        ok(small.get(a3.made().id()) != null, "the OPEN copy was not rotated out: " + a3.made().id());
        eq(small.lost(), 1, "one closed copy was rotated out instead");
        System.out.println("     " + small.ruleLine());
        ok(small.ruleLine().contains("rotated out"), "and the class says a copy was lost rather than hiding it");

        // The one that rotation must never take: an open copy older than everything else.
        eq(small.openIds().size(), 2, "two open copies, one for the jump and one for the split");
        ok(small.lost() >= 1, "and the oldest closed copy is the one that went");

        // ------------------------------------------------ 7. WHAT CANNOT BE ASKED FOR
        checks++;
        try {
            list.undo("backup-99");
            failed++;
            System.out.println("  FAIL undoing a backup that does not exist was allowed");
        } catch (IllegalArgumentException e) {
            // what we wanted
        }
        checks++;
        try {
            list.complete("backup-99");
            failed++;
            System.out.println("  FAIL completing a backup that does not exist was allowed");
        } catch (IllegalArgumentException e) {
            // what we wanted
        }
        BeforeChange.Taken noKind = list.take(null, before, "nothing named");
        ok(!noKind.ok(), "taking a copy without naming the change is refused");
        BeforeChange.Taken noState = list.take(BeforeChange.ChangeKind.RUPTURE, null, "no state");
        ok(!noState.ok(), "and so is a copy of nothing");
        eq(list.forget(b1.id()).size(), list.size() - 1, "a copy can be forgotten");
        eq(list.forget("nothing"), list, "forgetting one that is not there changes nothing");

        // ------------------------------------------------ 8. THE SCREEN LINE
        ok(BeforeChange.empty().ruleLine().contains("No copies taken"), "an empty list says so");
        ok(list.ruleLine().contains("open"), "the rule line counts what is still open: " + list.ruleLine());

        // ------------------------------------------------ 9. A COPY DOES NOT CHANGE AFTER IT IS TAKEN
        eq(list.undo(b1.id()).flagCount(), before.flagCount(), "the copy holds what was there when it was taken");

        System.out.println("\nStep 51 part 4: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
