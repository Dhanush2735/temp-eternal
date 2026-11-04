/* Step 50 part 3 (G10 as a card): one question, one day, more than one answer, each with a name on it.
   The claim: a card can hold two accounts where it used to hold one, a card with no accounts reads exactly
   as it did before and says out loud that nobody is named, and the base card's unreachable answers can be
   reported instead of being quietly lost. */
import com.eternalengine.knowledge.KnowledgeCard;
import com.eternalengine.knowledge.VoicedCard;
import com.eternalengine.story.BranchStory;
import com.eternalengine.timeline.Provenance;

import java.util.ArrayList;
import java.util.List;

public class Step50VoiceProbe {
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

    static void throwsUp(Runnable r, String what) {
        checks++;
        try {
            r.run();
            failed++;
            System.out.println("  FAIL " + what + "  expected an exception and got none");
        } catch (IllegalArgumentException e) {
            // what we wanted
        }
    }

    /** A card as the packs build them today: dated answers, and nobody's name on any of them. */
    static KnowledgeCard mumbai(boolean withTheShadowedOne) {
        List<KnowledgeCard.Question> qs = new ArrayList<>();
        qs.add(new KnowledgeCard.Question("docks", "Who built the docks?", 1, List.of(
                new KnowledgeCard.Answer(1872, KnowledgeCard.OPEN, "The docks were opened in 1872.", null))));
        qs.add(new KnowledgeCard.Question("court", "Who governs here?", 2, List.of(
                new KnowledgeCard.Answer(1890, KnowledgeCard.OPEN,
                        "A municipal corporation governs the city from 1890.", null))));
        qs.add(new KnowledgeCard.Question("harbour", "What is the harbour like?", 1, List.of(
                new KnowledgeCard.Answer(1800, KnowledgeCard.OPEN, "The harbour is shallow and busy.", null))));
        if (withTheShadowedOne) {
            // Two answers on one day: one of them can never be heard, and nothing in the pack says which.
            List<KnowledgeCard.Answer> twice = new ArrayList<>();
            twice.add(new KnowledgeCard.Answer(1872, KnowledgeCard.OPEN, "The old account of 1872.", null));
            twice.add(new KnowledgeCard.Answer(1872, KnowledgeCard.OPEN, "The later account of 1872.", null));
            qs.add(new KnowledgeCard.Question("twice", "What happened in 1872?", 1, twice));
        }
        return new KnowledgeCard("mumbai", "Bombay", null, "Place", 1, 1700, 19.07, 72.87, qs,
                List.of(), List.of("Mumbai"), List.of(), false);
    }

    public static void main(String[] args) {
        KnowledgeCard base = mumbai(true);
        VoicedCard plain = VoicedCard.of(base);

        // ------------------------------------------------ 1. THE CARD AS IT IS: ANONYMOUS, AND SAYS SO
        eq(plain.accounts("docks", 1900).size(), 1, "one answer on the docks question");
        ok(plain.accounts("docks", 1900).get(0).anonymous(), "and nobody is named as giving it");
        eq(plain.accounts("docks", 1900).get(0).text(), "The docks were opened in 1872.", "the words are the card's own");
        ok(plain.accounts("docks", 1900).get(0).line().startsWith("nobody in particular: "),
                "and the reader is told that in the line itself");
        String plainRead = plain.asText("docks", 1900);
        System.out.println("     " + plainRead.replace("\n", "\n     "));
        ok(plainRead.contains("does not say who tells you this"), "the reading says so out loud rather than guessing a name");
        eq(plain.anonymousAnswers(1900), 4, "every question of an untouched card is anonymous");
        ok(plain.disputed(1900).isEmpty(), "and nothing is disputed, because a card with one answer per question cannot disagree");

        // ------------------------------------------------ 2. ONE VOICE ON IT
        VoicedCard court = plain.with(VoicedCard.recorded("docks", 1872, KnowledgeCard.OPEN,
                BranchStory.Voice.COURT, "The docks were opened by the throne's order, in good time.", "ways_works"));
        List<VoicedCard.Spoken> one = court.accounts("docks", 1900);
        eq(one.size(), 1, "one account once a voice is added");
        ok(!one.get(0).anonymous(), "and it is no longer anonymous");
        eq(one.get(0).voice(), BranchStory.Voice.COURT, "the voice is the court's");
        eq(one.get(0).provenance(), Provenance.OBSERVED, "a reading of a row is observed and needs no warning mark");
        ok(!one.get(0).line().contains("(observed)"), "so no mark is printed on it");
        String courtRead = court.asText("docks", 1900);
        System.out.println("     " + courtRead.replace("\n", "\n     "));
        ok(courtRead.contains("One account, from a chronicler at court"), "the reading names the single voice");
        eq(court.anonymousAnswers(1900), 3, "and one fewer question is anonymous: " + court.anonymousAnswers(1900));

        // ------------------------------------------------ 3. TWO ON ONE DAY, WHICH IS G10
        VoicedCard two = court.with(VoicedCard.recorded("docks", 1872, KnowledgeCard.OPEN,
                BranchStory.Voice.TRAVELLER, "They laid the docks where the boats already went, and call it new.",
                "ways_works"));
        List<VoicedCard.Spoken> both = two.accounts("docks", 1900);
        eq(both.size(), 2, "two live accounts of one question on one day");
        eq(both.get(0).voice(), BranchStory.Voice.COURT, "the court is read first, because the order is fixed and not the caller's");
        eq(both.get(1).voice(), BranchStory.Voice.TRAVELLER, "and the traveller second");
        ok(two.severalAccounts("docks", 1900), "the card now disagrees with itself, on purpose");
        ok(two.disputed(1900).contains("docks"), "and the disagreement can be found without reading the text");
        String twoRead = two.asText("docks", 1900);
        System.out.println("     " + twoRead.replace("\n", "\n     "));
        ok(twoRead.contains("2 live accounts on one day"), "the reading says how many it is showing");
        ok(twoRead.contains("could hold only one of them"), "and says what a one-answer card would have done");
        ok(twoRead.contains("readings of the same rows and not two sources"),
                "and does not pretend two voices are two sources");
        ok(twoRead.contains("a chronicler at court") && twoRead.contains("a traveller"), "both names are on the page");

        // Order is fixed, not insertion order.
        VoicedCard backwards = plain
                .with(VoicedCard.recorded("docks", 1872, KnowledgeCard.OPEN, BranchStory.Voice.TRAVELLER, "t", "ways_works"))
                .with(VoicedCard.recorded("docks", 1872, KnowledgeCard.OPEN, BranchStory.Voice.COURT, "c", "ways_works"));
        eq(backwards.accounts("docks", 1900).get(0).voice(), BranchStory.Voice.COURT,
                "adding the traveller first does not put the traveller first");

        // ------------------------------------------------ 4. A VOICE HOLDS ITS CLAIM FOR ITS OWN YEARS
        VoicedCard windowed = two.with(VoicedCard.recorded("docks", 1872, 1890, BranchStory.Voice.TEMPLE,
                "The tank beside the docks was dug for the god, and the docks came after.", "ways_works"));
        eq(windowed.accounts("docks", 1880).size(), 3, "three voices while the temple holds its account");
        eq(windowed.accounts("docks", 1890).size(), 3, "still three on the last day of it");
        eq(windowed.accounts("docks", 1891).size(), 2, "and two when the temple stops saying it");
        ok(windowed.accounts("docks", 1840).isEmpty(), "before any of them started, the card itself has nothing either");

        // ------------------------------------------------ 5. NOTHING LIVE IS NOT NOTHING HAPPENED
        String nothing = windowed.asText("docks", 1840);
        System.out.println("     " + nothing.replace("\n", "\n     "));
        ok(nothing.contains("Nothing on this is live on 1840"), "the reader is told there is nothing on this day");
        ok(nothing.contains("not the same as saying nothing happened"), "and is not left to conclude that nothing happened");

        // ------------------------------------------------ 6. CALLER MISTAKES FAIL LOUDLY
        throwsUp(() -> plain.with(VoicedCard.recorded("no-such-question", 1872, KnowledgeCard.OPEN,
                BranchStory.Voice.COURT, "x", "ways_works")), "an answer to a question the card does not ask is refused");
        throwsUp(() -> plain.accounts("no-such-question", 1900), "asking for a question the card does not ask is refused");
        throwsUp(() -> plain.read("no-such-question", 1900), "and so is reading one");
        throwsUp(() -> VoicedCard.fromSentence("docks", KnowledgeCard.OPEN, null), "a spoken answer needs a sentence");
        throwsUp(() -> VoicedCard.of(null), "a voiced card needs a card");

        // ------------------------------------------------ 7. G5: A BRANCH'S OWN KNOWLEDGE, WRITTEN ONCE
        BranchStory.Sentence claim = BranchStory.authored(1901, "The new mill works, and it is mine.", "Asha",
                BranchStory.Voice.TEMPLE);
        VoicedCard.Spoken mine = VoicedCard.authored("harbour", KnowledgeCard.OPEN, claim);
        eq(mine.text(), claim.text(), "the words are BranchStory's and are not written a second time here");
        eq(mine.provenance(), Provenance.AUTHORED, "a player's claim is authored and marked as such");
        ok(mine.text().contains("Asha's account of it and not the record's"), "and it names whose account it is");
        ok(mine.line().contains("(authored)"), "the mark is printed on the line: " + mine.line());
        eq(mine.from(), 1901, "it starts in the year it was claimed");

        BranchStory.Sentence hearsay = BranchStory.rumour(1901, "the mill", BranchStory.Voice.COURT);
        VoicedCard.Spoken rumoured = VoicedCard.rumour("harbour", KnowledgeCard.OPEN, hearsay);
        eq(rumoured.provenance(), Provenance.MODELLED, "a rumour is modelled, because nobody has checked it");
        ok(rumoured.text().contains("Nobody has looked."), "and says exactly that");
        ok(rumoured.line().contains("(modelled)"), "the mark is printed: " + rumoured.line());

        VoicedCard branch = plain.with(mine).with(rumoured);
        eq(branch.accounts("harbour", 1905).size(), 2, "the claimed mill and the rumour beside it are both live");
        ok(branch.severalAccounts("harbour", 1905), "so the branch's knowledge makes the card disagree with itself");
        String branchRead = branch.asText("harbour", 1905);
        System.out.println("     " + branchRead.replace("\n", "\n     "));
        ok(branchRead.contains("(authored)") && branchRead.contains("(modelled)"),
                "and the reader can tell the claim from the rumour without being told what to think");
        // The note under a set of accounts has to know what it is looking at. Two voices over one row is a
        // reading of the same material; a claim and a rumour is not, and the first version of this note said
        // "readings of the same rows" about both, which was a worse lie than staying quiet.
        ok(!branchRead.contains("readings of the same rows"),
                "a claim and a rumour are not called readings of the same rows");
        ok(branchRead.contains("Not all of these are in the record"),
                "the reader is told that some of this is not the record's word");
        ok(twoRead.contains("readings of the same rows"), "and two voices over one row still are called that");

        // ------------------------------------------------ 8. THE BASE CARD'S LOST ANSWERS ARE REPORTED
        List<String> sh = plain.shadowed();
        eq(sh.size(), 1, "one unreachable answer in the fixture: " + sh.size());
        ok(sh.get(0).contains("twice"), "and it is named by its question: " + sh.get(0));
        ok(VoicedCard.of(mumbai(false)).shadowed().isEmpty(), "a clean card reports nothing");

        // ------------------------------------------------ 9. WHO CAN BE ASKED WHAT
        ok(VoicedCard.speaksTo(BranchStory.Voice.TRAVELLER, 1), "a traveller can be asked what the street knows");
        ok(!VoicedCard.speaksTo(BranchStory.Voice.TRAVELLER, 2), "and cannot be asked what the court decided");
        ok(VoicedCard.speaksTo(BranchStory.Voice.TAX_ROLL, 2), "the tax roll can, because the roll is the court's own book");
        ok(!VoicedCard.speaksTo(null, 1), "an unnamed answer is not a voice");
        eq(VoicedCard.voicesFor(1).size(), 4, "four voices for a street question");
        eq(VoicedCard.voicesFor(2).size(), 3, "three for a court question");
        ok(!VoicedCard.voicesFor(2).contains(BranchStory.Voice.TRAVELLER), "and the traveller is not one of them");
        for (BranchStory.Voice v : BranchStory.Voice.values()) {
            ok(VoicedCard.voicesFor(1).contains(v), "every voice can be asked a street question: " + v.who());
        }

        // ------------------------------------------------ 10. THE SCREEN LINES
        ok(VoicedCard.ruleLine().contains("who gives it"), "the rule line says what a card can now do");
        ok(VoicedCard.ruleLine().contains("nobody is named"), "and what it says when it cannot");
        eq(two.asText("docks", 1900), String.join("\n", two.read("docks", 1900)), "asText is read, joined");

        System.out.println("\nStep 50 part 3: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
