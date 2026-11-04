/* Step 52 part 5 (A10): the saves nobody kept: people, purses and notes, per universe AND per timeline. The
   claim: a pocket is saved as the difference from its parent pocket like the world's flags are; a purse cannot
   go below zero (refused, not clamped); a note is written once; and a chain with a missing parent or a loop
   restores nothing and says why. */
import com.eternalengine.player.PocketSave;
import com.eternalengine.player.PocketSave.Delta;
import com.eternalengine.player.PocketSave.Key;
import com.eternalengine.player.PocketSave.Pocket;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class Step52PocketProbe {
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

    static void refused(String actual, String words, String what) {
        checks++;
        if (actual == null || actual.isEmpty()) {
            failed++;
            System.out.println("  FAIL " + what + "  (it was not refused)");
            return;
        }
        if (actual.contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no reason says \"" + words + "\"; got " + actual);
    }

    static Map<String, List<String>> notes(String who, String... lines) {
        Map<String, List<String>> n = new LinkedHashMap<>();
        n.put(who, new ArrayList<>(List.of(lines)));
        return n;
    }

    public static void main(String[] args) {
        Key main = new Key("delhi", "main");
        Key b1 = new Key("delhi", "b1");

        // ------------------------------------------------ 1. THE THREE PAYLOADS AND THEIR THREE RULES
        Pocket dayOne = Pocket.of(
                Map.of("Nana", "in Delhi, a merchant", "Ravi", "in Delhi, a scribe"),
                Map.of("Sam", 12, "Mira", 3),
                notes("Sam", "arrived in 1857"));
        eq(dayOne.people().size(), 2, "the pocket holds what the world knows of two people");
        eq(dayOne.coinsOf("Sam"), 12, "and what Sam carries");
        eq(dayOne.notesOf("Sam").size(), 1, "and one note");

        // purses: refused at zero, never clamped
        Pocket earned = dayOne.earn("Sam", 5);
        eq(earned.coinsOf("Sam"), 17, "earn adds");
        eq(dayOne.coinsOf("Sam"), 12, "and the pocket it came from is unchanged: pockets are copies");
        PocketSave.Spent ok = earned.spend("Sam", 2);
        ok(ok.ok(), "spending what you have is allowed");
        eq(ok.pocket().coinsOf("Sam"), 15, "and leaves the rest");
        PocketSave.Spent tooMuch = ok.pocket().spend("Sam", 999);
        refused(tooMuch.refused(), "has 15 and cannot spend 999", "a purse cannot go below zero");
        eq(tooMuch.pocket().coinsOf("Sam"), 15, "and the refused spend changed nothing");
        PocketSave.Spent miraShort = ok.pocket().spend("Mira", 4);
        refused(miraShort.refused(), "has 3 and cannot spend 4", "the refusal says the numbers");
        PocketSave.Spent emptyIt = ok.pocket().spend("Sam", 15);
        ok(emptyIt.ok(), "spending everything is allowed");
        eq(emptyIt.pocket().coinsOf("Sam"), 0, "and leaves an empty purse");
        PocketSave.Spent odd = ok.pocket().spend("Sam", -5);
        refused(odd.refused(), "is not spending", "spending less than nothing is refused");

        // notes: written once
        Pocket wrote = dayOne.writeNote("Sam", "the bazaar is loud");
        eq(wrote.notesOf("Sam").size(), 2, "a note is appended");
        eq(wrote.notesOf("Sam").get(0), "arrived in 1857", "and what was written before is untouched");
        eq(dayOne.notesOf("Sam").size(), 1, "the earlier pocket still holds one note");
        refused(wrote.editNote("Sam", 0, "the bazaar is quiet").why(), "written once",
                "changing what a note says is refused, always");
        ok(wrote.editNote("Sam", 0, "x").why().contains("cannot be rewritten"),
                "and the refusal shows what was wanted: " + wrote.editNote("Sam", 0, "x").why());

        // people: recorded, removed, read
        Pocket moved = wrote.putPerson("Ravi", "in Delhi, a printer");
        eq(moved.personLine("Ravi"), "Ravi · in Delhi, a printer", "the world may re-record what a person does");
        ok(moved.personLine("ravi") != null, "and reads names whatever their case");
        Pocket gone = moved.removePerson("Ravi");
        eq(gone.personLine("Ravi"), null, "a branch may carry the end of a person");
        eq(gone.people().size(), 1, "and the pocket holds one less");

        // ------------------------------------------------ 2. THE SAVE: ROOT WHOLE, A CHILD AS A DIFFERENCE
        PocketSave save = PocketSave.empty().root(main, dayOne, "the real history");
        PocketSave.Restored restored = save.chain(main);
        ok(restored.ok(), "the root restores");
        eq(restored.pocket().people(), dayOne.people(), "exactly as saved");
        eq(restored.applied(), List.of(main), "from one save");

        Pocket onBranch = gone.writeNote("Mira", "took the northern road").earn("Mira", 27);
        save.branch(main, b1, onBranch, "the road was taken");
        Delta d = save.get(b1);
        eq(d.parent(), main, "the branch hangs off the real history");
        eq(d.peopleGone(), java.util.Set.of("Ravi"), "its delta holds the one it removed");
        ok(d.peopleChanged().isEmpty(), "and only what it changed: " + d.peopleChanged());
        eq(d.purseChanged().get("Mira"), 30, "Mira's purse on this branch is 30");
        System.out.println("     delta touches: " + d.touched());

        PocketSave.Restored onB1 = save.chain(b1);
        ok(onB1.ok(), "the chain to the branch restores");
        eq(onB1.applied(), List.of(main, b1), "root-down");
        eq(onB1.pocket().personLine("Ravi"), null, "Ravi is gone on this branch");
        eq(onB1.pocket().personLine("Nana").contains("merchant") ? "kept" : "lost", "kept",
                "and Nana still stands");
        eq(onB1.pocket().coinsOf("Mira"), 30, "Mira has 30 here");
        eq(onB1.pocket().coinsOf("Sam"), 12, "and Sam is as the root left him");
        eq(onB1.pocket().notesOf("Sam").get(0), "arrived in 1857", "Sam's root note survives the branch, "
                + "first");
        eq(onB1.pocket().notesOf("Sam").size(), 2, "with only the branch's new one after it");
        eq(onB1.pocket().notesOf("Mira").size(), 1, "and the branch's note is Mira's");

        // The real history is untouched by its branch.
        eq(save.chain(main).pocket().personLine("Ravi").contains("scribe") ? "kept" : "lost", "kept",
                "Ravi still stands on the real history");
        eq(save.chain(main).pocket().coinsOf("Mira"), 3, "and Mira there has 3");

        // A lone branch saves nothing (the root is stored whole once): the saving is in the fan, as step 51
        // measured for the world's flags. Four more branches, each changing one purse.
        for (int i = 2; i <= 5; i++) {
            Pocket p = dayOne.earn("Sam", i * 10);
            save.branch(main, new Key("delhi", "b" + i), p, "branch " + i);
        }
        System.out.println("     " + save.cost());
        ok(save.cost().contains("% of the cost"), "and the cost of the difference is measured");
        String cost = save.cost();
        int pct = Integer.parseInt(cost.replaceAll(".*: (\\d+)%.*", "$1"));
        ok(pct < 100, "five branches cost less than saving every pocket whole (" + pct + "%)");
        ok(pct < 80, "and clearly less (" + pct + "%)");

        // ------------------------------------------------ 3. THE CHEAP COPY CHECKED AGAINST A FULL ONE
        eq(save.diff(b1, onB1.pocket()).size(), 0, "the cheap save agrees with a full save of the branch");
        Pocket wrong = Pocket.of(onB1.pocket().people(), Map.of("Mira", 29, "Sam", 12),
                onB1.pocket().notes());
        List<PocketSave.Difference> diffs = save.diff(b1, wrong);
        eq(diffs.size(), 1, "one wrong purse is found");
        eq(diffs.get(0).name(), "Mira", "and named");
        eq(diffs.get(0).section(), "purse", "in its section");
        eq(diffs.get(0).key(), b1, "and the branch's own delta is to blame: " + diffs.get(0).line());
        Pocket missingPerson = Pocket.of(
                Map.of("Nana", "in Delhi, a merchant", "Late", "arrived after the branch"),
                onB1.pocket().purses(), onB1.pocket().notes());
        List<PocketSave.Difference> missing = save.diff(b1, missingPerson);
        eq(missing.size(), 1, "a person the full save has and the chain does not is found");
        eq(missing.get(0).name(), "Late", "and named: " + missing.get(0).line());

        // ------------------------------------------------ 4. TWO UNIVERSES, ONE BRANCH NAME, TWO WORLDS
        Key red = new Key("u-red", "main");
        Key blue = new Key("u-blue", "main");
        PocketSave multiverse = PocketSave.empty()
                .root(red, Pocket.of(Map.of("Nana", "alive in u-red"), Map.of(), notes("Nana", "here")), "red")
                .root(blue, Pocket.of(Map.of("Nana", "never came to u-blue"), Map.of(), Map.of()), "blue");
        eq(multiverse.keys().size(), 2, "one branch name, two universes, two saves");
        eq(multiverse.chain(red).pocket().personLine("Nana"), "Nana · alive in u-red",
                "the red world's Nana");
        eq(multiverse.chain(blue).pocket().personLine("Nana"), "Nana · never came to u-blue",
                "and the blue world's are not the same save");
        eq(multiverse.chain(blue).pocket().notesOf("Nana").size(), 0,
                "only the red one has the note");

        // ------------------------------------------------ 5. A BROKEN FILE RESTORES NOTHING
        PocketSave.Delta orphan = new PocketSave.Delta(b1, main, Map.of(), Set.of(), Map.of(), Set.of(),
                Map.of(), Set.of(), "read from disk");
        PocketSave fromDisk = PocketSave.of(orphan);
        PocketSave.Restored broken = fromDisk.chain(b1);
        ok(!broken.ok(), "a child whose parent is missing restores nothing");
        refused(String.join(" | ", broken.refused()), "there is no save for delhi/main",
                "and says which save is missing: " + broken.refused());

        PocketSave.Delta toA = new PocketSave.Delta(new Key("u", "a"), new Key("u", "b"), Map.of(),
                Set.of(), Map.of(), Set.of(), Map.of(), Set.of(), "");
        PocketSave.Delta toB = new PocketSave.Delta(new Key("u", "b"), new Key("u", "a"), Map.of(),
                Set.of(), Map.of(), Set.of(), Map.of(), Set.of(), "");
        PocketSave loop = PocketSave.of(toA, toB);
        PocketSave.Restored looped = loop.chain(new Key("u", "a"));
        ok(!looped.ok(), "a looping chain restores nothing");
        refused(String.join(" | ", looped.refused()), "loops", "and says the word loops");

        // ------------------------------------------------ 6. THE BUILDER REFUSES WHAT IT CANNOT MEAN
        checks++;
        try {
            save.branch(new Key("delhi", "nobody"), new Key("delhi", "b6"), dayOne, "");
            failed++;
            System.out.println("  FAIL a child with no parent was saved");
        } catch (IllegalArgumentException e) {
            ok(e.getMessage().contains("broken chain"), "and says why: " + e.getMessage());
            checks--;
        }
        checks++;
        try {
            save.root(main, dayOne, "again");
            failed++;
            System.out.println("  FAIL one pocket was saved twice");
        } catch (IllegalArgumentException e) {
            ok(e.getMessage().contains("already saved"), "a pocket saved twice is refused: " + e.getMessage());
            checks--;
        }
        checks++;
        try {
            save.branch(main, main, dayOne, "");
            failed++;
            System.out.println("  FAIL a pocket was made its own parent");
        } catch (IllegalArgumentException e) {
            ok(e.getMessage().contains("own parent"), "and a pocket cannot be its own parent");
            checks--;
        }

        // ------------------------------------------------ 7. THE RULE LINE
        System.out.println("     " + PocketSave.ruleLine());
        ok(PocketSave.ruleLine().contains("below zero"), "the rule line names the purse rule");
        ok(PocketSave.ruleLine().contains("written once"), "and the note rule");
        ok(PocketSave.ruleLine().contains("restores nothing"), "and the broken-chain rule");

        System.out.println("\nStep 52 part 5: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
