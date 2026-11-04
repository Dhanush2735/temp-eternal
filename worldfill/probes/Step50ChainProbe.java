/* Step 50 part 6: the chain, end to end. Parts 2 to 5 each proved their own class; step 49 taught that a probe
   per class proves the class and only a probe per chain proves the game.
   The chain: the packs -> a story about a place in a year -> the surface the record says is there -> the object a
   player reads -> a branch's own claim cut into it -> a card that can hold two answers. And the AD 3000 rule at
   the end of the chain, where a plan could be mistaken for history. */
import com.eternalengine.civilization.SettlementRank;
import com.eternalengine.civilization.Signs;
import com.eternalengine.knowledge.BranchKnowledge;
import com.eternalengine.knowledge.KnowledgeCard;
import com.eternalengine.knowledge.VoicedCard;
import com.eternalengine.knowledge.WrittenThing;
import com.eternalengine.story.BranchStory;
import com.eternalengine.story.PlaceRecord;
import com.eternalengine.timeline.Provenance;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.zip.GZIPInputStream;

public class Step50ChainProbe {
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

    static final double DELHI_LAT = 28.61, DELHI_LON = 77.21;
    static final String HISTORY = "/data/eternalengine/eternal/history/";

    static InputStream gz(String n) throws Exception {
        return new GZIPInputStream(Step50ChainProbe.class.getResourceAsStream(HISTORY + n));
    }

    static Signs.Sign signWith(Signs.Here here, String id) {
        for (Signs.Sign s : here.signs()) if (s.id().equals(id)) return s;
        return null;
    }

    public static void main(String[] args) throws Exception {
        PlaceRecord rec = PlaceRecord.load(gz("towns.json.gz"), gz("buildings_famous.json.gz"),
                gz("ways_works.json.gz"));
        Signs signs = Signs.get();

        PlaceRecord.Town delhi = rec.nearest(DELHI_LAT, DELHI_LON);
        Signs.Here here = signs.hereAt(DELHI_LAT, DELHI_LON, 1900, SettlementRank.CITY);
        System.out.println("     " + delhi.nameNow() + " (" + delhi.qid() + "), " + here.line().split("\\.")[0]);

        // ------------------------------------------------ 1. THE CHAIN, IN ONE PIECE
        BranchStory.Story story = rec.story(delhi.qid(), 1900, BranchStory.Voice.TAX_ROLL, 25, 40);
        ok(!story.empty(), "the packs give a story for this place in 1900");
        ok(story.name().equals(delhi.nameIn(1900)), "told in the name the pack gives it for 1900: " + story.name());
        Signs.Sign wall = signWith(here, "temple_inscription");
        ok(wall != null, "and the record has a temple inscription standing there");
        WrittenThing object = WrittenThing.carve(wall, here, story,
                "the temple, which kept the account of what it cost");
        ok(!object.read().isEmpty(), "so there is an object to read");
        eq(object.script(), here.script(), "in the script the record gives for that place and year");
        eq(object.year(), 1900, "and it is dated 1900, the year it was carved");
        eq(object.voice(), BranchStory.Voice.TAX_ROLL, "in the voice the story was told in");
        System.out.println("     " + object.read().get(0));
        System.out.println("     " + object.read().get(object.read().size() - 1));

        // Every line between the opening and the closing is a line of the record, with its mark.
        boolean everyBodyLineFromTheRecord = true;
        for (int i = 1; i < object.lines().size() - 1; i++) {
            String body = object.lines().get(i);
            // A body line is "<year>: <text>" plus, where it applies, "  (mark)".
            if (!body.matches("^-?\\d+: .*")) everyBodyLineFromTheRecord = false;
        }
        ok(everyBodyLineFromTheRecord, "every body line carries the year of the row it came from");

        // Pagination, from the same object a player would hold.
        List<String> all = object.wrapped(19);
        List<String> back = new ArrayList<>();
        for (List<String> p : object.pages(19, 5)) back.addAll(p);
        eq(back, all, "the pages hold every wrapped line, in order");
        ok(!all.isEmpty(), "and there is something to wrap");

        // ------------------------------------------------ 2. A BRANCH'S CLAIM, CUT INTO IT
        BranchKnowledge mine = BranchKnowledge.of("branch-that-built-it")
                .claim(1901, "harbour", "The new works are mine and the record will not say so.", "Asha",
                        BranchStory.Voice.TAX_ROLL)
                .hearsay(1901, "harbour", "the new works", BranchStory.Voice.TRAVELLER);
        List<KnowledgeCard.Question> qs = new ArrayList<>();
        qs.add(new KnowledgeCard.Question("harbour", "What is the harbour like?", 1, List.of(
                new KnowledgeCard.Answer(1800, KnowledgeCard.OPEN, "The harbour is shallow and busy.", null))));
        KnowledgeCard card = new KnowledgeCard("delhi", delhi.nameNow(), null, "Place", 1, 1700,
                delhi.lat(), delhi.lon(), qs, List.of(), List.of(), List.of(), false);
        VoicedCard voiced = mine.attach(VoicedCard.of(card)).card();
        eq(voiced.accounts("harbour", 1905).size(), 2, "the branch's card holds two accounts of one question");
        String cardText = voiced.asText("harbour", 1905);
        ok(cardText.contains("(authored)") && cardText.contains("(modelled)"), "both marked");
        BranchKnowledge theirs = BranchKnowledge.of("branch-that-did-not");
        ok(theirs.attach(VoicedCard.of(card)).card().accounts("harbour", 1905).size() == 1,
                "and a different branch of the same year holds only its own one answer");

        // The same claim does not appear on the stone, because the stone is the record's voice and not the
        // branch's. That is the whole distinction: a card is where a claim can live, a surface is where it cannot.
        String stone = object.asText();
        ok(!stone.contains("are mine and the record will not say so"), "a branch's claim is not on the stone");
        ok(cardText.contains("are mine and the record will not say so"), "it is on the card");

        // ------------------------------------------------ 3. THE END OF THE RECORD
        int held = rec.futureRowCount();
        // 17 and not 16: two buildings and fifteen works, one of them a station that is in the pack twice. The first
        // count of this in python used "> 2027" and missed the 2027 row, which is the same mistake as reading a
        // threshold as "after" instead of "later than".
        eq(held, 17, "seventeen rows in the packs are dated after the record ends");
        System.out.println("     " + rec.future());
        BranchStory.Story far = rec.story(delhi.qid(), 2900, BranchStory.Voice.COURT, 500, 4000);
        ok(!far.empty(), "a story can still be told in AD 2900");
        int latest = Integer.MIN_VALUE;
        boolean anyAfterTheRecord = false;
        for (BranchStory.Sentence s : far.sentences()) {
            latest = Math.max(latest, s.year());
            if (s.year() > PlaceRecord.LAST_RECORDED) anyAfterTheRecord = true;
        }
        ok(!anyAfterTheRecord, "and not one of its sentences is dated after " + PlaceRecord.LAST_RECORDED
                + "; the latest is " + latest);
        ok(latest <= PlaceRecord.LAST_RECORDED && latest > 1900,
                "the story reaches the present and stops there: " + latest);
        // A planned railway must not be handed to a player in 2900 as something that happened.
        boolean anyPlanned = false;
        for (BranchStory.Sentence s : far.sentences()) {
            if (s.text().contains("Mutiara")) anyPlanned = true;
        }
        ok(!anyPlanned, "a 2031 line that was still a drawing is not on the wall in 2900");

        // ------------------------------------------------ 4. NOTHING IS INVENTED, ANYWHERE IN THE CHAIN
        boolean everySentenceSourced = true;
        boolean everySentenceMarked = true;
        for (BranchStory.Sentence s : far.sentences()) {
            if (s.record().isEmpty()) everySentenceSourced = false;
            if (s.provenance() == null) everySentenceMarked = false;
            if (s.provenance() == Provenance.AUTHORED) everySentenceSourced = false;   // no player wrote this one
        }
        ok(everySentenceSourced, "every sentence of a story with nobody in it comes from a pack");
        ok(everySentenceMarked, "and says what it rests on");

        int markedSomewhere = 0;
        for (BranchStory.Sentence s : far.sentences()) {
            if (s.provenance() != Provenance.OBSERVED) markedSomewhere++;
        }
        ok(markedSomewhere > 0, "and some of them are marked, because a wide story reaches estimated rows: "
                + markedSomewhere + " of " + far.sentences().size());
        ok(far.asMarkedText().contains("(modelled)") || far.asMarkedText().contains("(structural)"),
                "which the reader is shown");

        // ------------------------------------------------ 5. AND THE SURFACE STILL REFUSES THE IMPOSSIBLE
        Signs.Here cuzco1500 = signs.hereAt(-13.53, -71.97, 1500, SettlementRank.CITY);
        BranchStory.Story cuzco = rec.story(rec.nearest(-13.53, -71.97).qid(), 1500,
                BranchStory.Voice.TEMPLE, 25, 10);
        final Signs.Sign any = wall;
        checks++;
        try {
            WrittenThing.carve(any, cuzco1500, cuzco, "the parish");
            failed++;
            System.out.println("  FAIL a place with no writing refused the object");
        } catch (IllegalStateException e) {
            if (!e.getMessage().contains("Nothing is written")) {
                failed++;
                System.out.println("  FAIL wrong refusal at Cuzco: " + e.getMessage());
            }
        }

        System.out.println("\nStep 50 part 6: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
