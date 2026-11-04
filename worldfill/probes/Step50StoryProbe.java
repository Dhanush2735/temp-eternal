/* Step 50 part 2 (G4 and G10): a story about a place, told by somebody, out of what the record holds.
   The claim: a story invents nothing, uses the name the place had that year, and says who is telling it -
   which is the thing a knowledge card with one answer per question cannot do. */
import com.eternalengine.story.BranchStory;
import com.eternalengine.timeline.Provenance;

import java.util.ArrayList;
import java.util.List;

public class Step50StoryProbe {
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

    static List<BranchStory.Fact> mumbai() {
        List<BranchStory.Fact> f = new ArrayList<>();
        f.add(new BranchStory.Fact(1737, 1737, "the dockyard rebuilt", "works", "ways_works"));
        f.add(new BranchStory.Fact(1847, 1847, "the first cotton mill", "works", "ways_works"));
        f.add(new BranchStory.Fact(1853, 1853, "the first railway in India", "line", "ways_works"));
        f.add(new BranchStory.Fact(1872, 1872, "the docks opened", "port", "ways_works"));
        f.add(new BranchStory.Fact(1890, 1890, "the municipal corporation", "building", "towns"));
        f.add(new BranchStory.Fact(1995, null, "the name change", "political", "towns"));
        return f;
    }

    public static void main(String[] args) {
        // ------------------------------------------------ 1. FOUR VOICES, EACH WITH A BIAS
        eq(BranchStory.Voice.values().length, 4, "four kinds of narrator");
        for (String v : BranchStory.voices()) System.out.println("     " + v);
        for (BranchStory.Voice v : BranchStory.Voice.values()) {
            ok(!v.serves().isEmpty(), v.who() + " serves something, which is why it is worth listening to "
                    + "and worth doubting");
            ok(!v.overstates().isEmpty(), "and overstates something: " + v.overstates());
        }
        ok(BranchStory.Voice.TAX_ROLL.isRecord(), "a tax roll is a record and not a story");
        ok(!BranchStory.Voice.COURT.isRecord(), "and a court chronicle is a story");

        // ------------------------------------------------ 2. NOTHING IN ITS OWN FUTURE
        BranchStory.Story s1850 = BranchStory.tell("Mumbai", "Bombay", 1850, BranchStory.Voice.COURT,
                mumbai(), 20);
        ok(!s1850.empty(), "there is a story in 1850");
        for (BranchStory.Sentence s : s1850.sentences()) {
            ok(s.year() <= 1850, "and no sentence is from the future: " + s.line());
        }
        // Two of the six fixture rows are dated by 1850: 1737 and 1847. The first version of this probe said
        // three, counting the 1853 railway, which is three years in the future of the story and correctly
        // left out. The engine was right and the arithmetic in the test was wrong.
        eq(s1850.sentences().size(), 2, "two rows are dated by 1850: " + s1850.sentences().size());
        // Ordered, which is what makes it a story rather than a list.
        for (int i = 1; i < s1850.sentences().size(); i++) {
            ok(s1850.sentences().get(i).year() >= s1850.sentences().get(i - 1).year(),
                    "and the sentences are in order");
        }

        // ------------------------------------------------ 3. EVERY SENTENCE CARRIES ITS ROW
        for (BranchStory.Sentence s : s1850.sentences()) {
            ok(!s.record().isEmpty(), "a sentence names the pack it came from: " + s.record());
            eq(s.provenance(), Provenance.OBSERVED, "and is marked as recorded and not as a story told by us");
        }

        // ------------------------------------------------ 4. THE NAME THE PLACE HAD THAT YEAR
        eq(BranchStory.namingLine("Mumbai", "Bombay", 1850, 1995),
                "It is Bombay in 1850, and Mumbai is what it is called now: the record dates the change to 1995.",
                "the name a place had that year is used, and the change is dated");
        eq(BranchStory.namingLine("Mumbai", "Mumbai", 2000, 1995), "Mumbai is called Mumbai in 2000.",
                "and after the change it is called by the new name");
        eq(BranchStory.namingLine("Tokyo", "Edo", 1700, null),
                "It is Edo in 1700, which is the name this record gives it for that year.",
                "and with no dated change in the pack, the year's own name is used without inventing a date");
        ok(!s1850.lines().get(0).contains("Mumbai in 1850"),
                "the story's own header uses the year's name: " + s1850.lines().get(0));

        // ------------------------------------------------ 5. THE SAME ROW IN TWO VOICES IS TWO SENTENCES
        BranchStory.Fact railway = new BranchStory.Fact(1853, 1853, "the first railway in India", "line",
                "ways_works");
        List<String> two = BranchStory.twoAccounts(railway, BranchStory.Voice.COURT,
                BranchStory.Voice.TRAVELLER);
        eq(two.size(), 3, "two accounts and a note about what they are");
        System.out.println("     " + two.get(0));
        System.out.println("     " + two.get(1));
        ok(two.get(0).startsWith("a chronicler at court"), "the first says who is talking");
        ok(two.get(1).startsWith("a traveller"), "and the second says who is talking");
        ok(!two.get(0).substring(two.get(0).indexOf(':')).equals(two.get(1).substring(two.get(1).indexOf(':'))),
                "and they do not say the same thing");
        ok(two.get(2).contains("one row"), "the note says they are about one row: " + two.get(2));
        ok(two.get(2).contains("not a second source"),
                "and is honest that a second voice over one account is a reading and not a source: "
                        + two.get(2));
        // Both keep the row's own words, so a reader can check the fact under the voice.
        ok(two.get(0).contains("the first railway in India") && two.get(1).contains("the first railway in India"),
                "and both carry the row's own name, so the fact can be checked under the voice");

        // The tax roll is the one that changes least, and says so.
        String roll = BranchStory.twoAccounts(railway, BranchStory.Voice.TAX_ROLL,
                BranchStory.Voice.TEMPLE).get(0);
        ok(roll.contains("without a word about whether it was just or cruel"),
                "a tax roll states the fact and refuses to judge it: " + roll);

        // ------------------------------------------------ 6. A THING THAT STOOD IS TOLD BY HOW LONG IT STOOD
        BranchStory.Fact fort = new BranchStory.Fact(1650, 1800, "the old fort", "fortification",
                "buildings_famous");
        BranchStory.Story s1700 = BranchStory.tell("Mumbai", "Bombay", 1700, BranchStory.Voice.COURT,
                List.of(fort), 10);
        eq(s1700.sentences().size(), 1, "a standing thing is one sentence");
        ok(s1700.sentences().get(0).text().contains("50 years"),
                "and it says how long it has stood, which a date alone does not: "
                        + s1700.sentences().get(0).text());
        // After it ended, the story says it stood, because the row says it ended and the story is of a year
        // after the end: it stands in the record and the sentence still reports the fact.
        BranchStory.Story s1900 = BranchStory.tell("Mumbai", "Bombay", 1900, BranchStory.Voice.COURT,
                List.of(fort), 10);
        ok(!s1900.empty(), "and after it is gone the row is still dated and still readable");

        // ------------------------------------------------ 7. WHAT A BRANCH KNOWS THAT THE RECORD DOES NOT
        BranchStory.Sentence authored = BranchStory.authored(1850, "A steam engine was built at the mill.",
                "Asha", BranchStory.Voice.TRAVELLER);
        eq(authored.provenance(), Provenance.AUTHORED, "a player's knowledge is AUTHORED and not recorded");
        ok(authored.text().contains("Asha"), "and names the player: " + authored.text());
        ok(authored.text().contains("not the record's"), "and says it is not the record's: " + authored.text());
        eq(authored.provenance() == Provenance.OBSERVED, false, "it is never passed off as recorded");
        BranchStory.Sentence rumour = BranchStory.rumour(1850, "the steam engine", BranchStory.Voice.COURT);
        eq(rumour.provenance(), Provenance.MODELLED, "and a rumour is MODELLED, which is the third mark");
        ok(rumour.text().contains("Nobody has looked"),
                "and says nobody has checked it: " + rumour.text());
        ok(!rumour.record().startsWith("ways"), "a rumour has no row behind it and does not pretend to");

        // ------------------------------------------------ 8. NOTHING INVENTED WHEN THERE IS NOTHING THERE
        BranchStory.Story none = BranchStory.tell("a valley", "a valley", 1200, BranchStory.Voice.COURT,
                List.of(), 10);
        ok(none.empty(), "no rows, no story");
        ok(none.refused().contains("not a claim that nothing happened"),
                "and the refusal is careful about what it means: " + none.refused());
        // Facts in the future are not used, and the story says there is nothing.
        BranchStory.Story future = BranchStory.tell("Mumbai", "Bombay", 1700, BranchStory.Voice.COURT,
                mumbai(), 10);
        ok(future.empty(), "all six rows are after 1700, so there is nothing to tell");

        // ------------------------------------------------ 9. THE LIMIT IS A LIMIT
        BranchStory.Story longStory = BranchStory.tell("Mumbai", "Bombay", 2000, BranchStory.Voice.TRAVELLER,
                mumbai(), 3);
        eq(longStory.sentences().size(), 3, "a story of three sentences is three sentences");
        eq(longStory.sentences().get(2).year(), 1853, "and it takes the earliest three, in order: "
                + longStory.sentences().get(2).line());

        // ------------------------------------------------ 10. WHAT A READER GETS
        BranchStory.Story all = BranchStory.tell("Mumbai", "Bombay", 2000, BranchStory.Voice.TRAVELLER,
                mumbai(), 20);
        List<String> lines = all.lines();
        eq(lines.size(), all.sentences().size() + 1, "the story is a header and a line per sentence");
        for (String l : lines) System.out.println("     " + l);
        ok(lines.get(0).contains("as a traveller would have it"),
                "and the header says who is telling it: " + lines.get(0));
        ok(all.asText().split("\n").length == lines.size(), "and the text form is the same thing");

        System.out.println("  " + BranchStory.ruleLine());
        System.out.println(failed == 0
                ? "Step50StoryProbe: " + checks + " checks, 0 failed"
                : "Step50StoryProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
