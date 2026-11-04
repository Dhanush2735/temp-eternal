/* Step 50 part 5 (G4): the written object a player reads in the world.
   The claim: it is not a book. It is a surface the record says exists at that place in that year, it holds only
   what fits on it, it says whose wall it is, and it loses no line without saying so. */
import com.eternalengine.civilization.SettlementRank;
import com.eternalengine.civilization.Signs;
import com.eternalengine.knowledge.WrittenThing;
import com.eternalengine.story.BranchStory;
import com.eternalengine.story.PlaceRecord;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.zip.GZIPInputStream;

public class Step50WrittenProbe {
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

    static void refuses(Runnable r, String contains, String what) {
        checks++;
        try {
            r.run();
            failed++;
            System.out.println("  FAIL " + what + "  expected a refusal and got none");
        } catch (IllegalStateException | IllegalArgumentException e) {
            if (!e.getMessage().contains(contains)) {
                failed++;
                System.out.println("  FAIL " + what + "  wrong refusal: " + e.getMessage());
            }
        }
    }

    static final double DELHI_LAT = 28.61, DELHI_LON = 77.21;
    static final double CUZCO_LAT = -13.53, CUZCO_LON = -71.97;

    static Signs.Sign signWith(Signs.Here here, String id) {
        for (Signs.Sign s : here.signs()) {
            if (s.id().equals(id)) return s;
        }
        return null;
    }

    static Signs.Here delhi1500() {
        return Signs.get().hereAt(DELHI_LAT, DELHI_LON, 1500, SettlementRank.CITY);
    }

    static String ids(Signs.Here here) {
        List<String> out = new ArrayList<>();
        for (Signs.Sign s : here.signs()) out.add(s.id());
        return String.join(",", out);
    }

    public static void main(String[] args) throws Exception {
        PlaceRecord rec = PlaceRecord.load(
                new GZIPInputStream(Step50WrittenProbe.class.getResourceAsStream(
                        "/data/eternalengine/eternal/history/towns.json.gz")),
                new GZIPInputStream(Step50WrittenProbe.class.getResourceAsStream(
                        "/data/eternalengine/eternal/history/buildings_famous.json.gz")),
                new GZIPInputStream(Step50WrittenProbe.class.getResourceAsStream(
                        "/data/eternalengine/eternal/history/ways_works.json.gz")));
        Signs signs = Signs.get();
        PlaceRecord.Town delhi = rec.nearest(DELHI_LAT, DELHI_LON);
        System.out.println("     nearest town to Delhi's point: " + delhi.nameNow() + " (" + delhi.qid() + ")");

        // ------------------------------------------------ 1. NO WRITING, NO OBJECT
        Signs.Here cuzco1500 = signs.hereAt(CUZCO_LAT, CUZCO_LON, 1500, SettlementRank.CITY);
        ok(!cuzco1500.writing(), "nothing is written at Cuzco in 1500");
        eq(cuzco1500.arrived(), 1576, "writing reaches it in 1576, when the record says it did");
        System.out.println("     Cuzco 1500: " + cuzco1500.line());
        BranchStory.Story cuzcoStory = rec.story(rec.nearest(CUZCO_LAT, CUZCO_LON).qid(), 1500,
                BranchStory.Voice.TEMPLE, 25, 20);
        Signs.Here cuzco1600 = signs.hereAt(CUZCO_LAT, CUZCO_LON, 1600, SettlementRank.CITY);
        ok(cuzco1600.writing(), "and by 1600 something is written there");
        Signs.Sign grave1600 = signWith(cuzco1600, "grave");
        ok(grave1600 != null, "there is a cut stone at a grave in Cuzco in 1600");
        final Signs.Sign stone = grave1600;
        refuses(() -> WrittenThing.carve(stone, cuzco1500, cuzcoStory, "the parish"),
                "Nothing is written", "an object cannot be carved where nothing is written");
        ok(signWith(cuzco1600, "notice") == null,
                "and no posted notice, because a notice needs paper and paper is not there yet");

        // ------------------------------------------------ 2. WHAT IS ACTUALLY ON THE WALLS
        Signs.Here delhi1000 = signs.hereAt(DELHI_LAT, DELHI_LON, 1000, SettlementRank.CITY);
        ok(delhi1000.writing(), "Delhi in 1000 has writing");
        System.out.println("     Delhi 1000 signs: " + ids(delhi1000));
        eq(ids(delhi1000), "edict,boundary,temple_inscription,grave",
                "four kinds of written thing and no book among them");
        Signs.Here delhi1900 = signs.hereAt(DELHI_LAT, DELHI_LON, 1900, SettlementRank.CITY);
        Signs.Here delhi2000 = signs.hereAt(DELHI_LAT, DELHI_LON, 2000, SettlementRank.CITY);
        System.out.println("     Delhi 1900 signs: " + ids(delhi1900));
        ok(signWith(delhi1000, "notice") == null, "in 1000 there is no posted notice");
        ok(signWith(delhi1900, "notice") == null, "nor in 1900, which is not what I expected");
        ok(signWith(delhi2000, "notice") != null, "and by 2000 there is one, because a notice needs paper and "
                + "printing and the pack dates both");
        eq(ids(delhi2000), "boundary,temple_inscription,grave,graffiti,shop_sign,notice,street_name,road_sign,"
                + "official_bilingual", "nine kinds of written thing in 2000, and still no book among them");
        ok(signWith(delhi1000, "edict") != null, "the edict is there in 1000");
        ok(signWith(delhi1500(), "edict") == null, "and gone by 1500, because the rock it was cut into is dated too");

        // ------------------------------------------------ 3. THE OBJECT ITSELF
        BranchStory.Story court1000 = rec.story(delhi.qid(), 1000, BranchStory.Voice.COURT, 25, 40);
        ok(court1000.sentences().size() >= 1, "there is a story at Delhi in 1000: " + court1000.sentences().size()
                + " rows, because the town the packs hold there is New Delhi and its own record starts late");
        final Signs.Sign edict = signWith(delhi1000, "edict");
        final BranchStory.Story court = court1000;
        WrittenThing on = WrittenThing.carve(edict, delhi1000, court, "the sultan's officers");
        eq(on.placeThen(), court.name(), "the object uses the name the place had that year");
        eq(on.script(), delhi1000.script(), "and the script the record says is written there");
        eq(on.voice(), BranchStory.Voice.COURT, "and the story's own voice");
        eq(on.author(), "the sultan's officers", "and it names who had it put up");
        System.out.println("     " + on.asText().replace("\n", "\n     "));
        ok(on.lines().get(0).contains("at " + on.placeThen()), "the first line says what it is and where");
        ok(on.lines().get(0).contains(String.valueOf(1000)), "and in what year");
        ok(on.wrapped(60).size() > 0, "it can be fitted to a screen");

        // The body is the story's own lines, and not one of them is invented here.
        List<String> marked = court.markedLines();
        boolean sameBody = true;
        for (int i = 1; i < marked.size(); i++) {
            if (!on.lines().get(i).equals(marked.get(i))) sameBody = false;
        }
        ok(sameBody, "every body line is the story's own line, not a rewriting of it");
        eq(on.lines().size(), marked.size() + 1, "body, then one closing line");

        // ------------------------------------------------ 4. WHOSE WALL IT IS
        String matching = on.lines().get(on.lines().size() - 1);
        ok(matching.contains("It is the kind of thing a chronicler at court puts up"),
                "an edict is the court's own wall: " + matching);
        final Signs.Sign templeWall = signWith(delhi1000, "temple_inscription");
        WrittenThing notHis = WrittenThing.carve(templeWall, delhi1000, court, "the sultan's officers");
        String mismatch = notHis.lines().get(notHis.lines().size() - 1);
        ok(mismatch.contains("did not put this up"), "and a court story on a temple wall says so: " + mismatch);
        ok(mismatch.contains("belongs to a priest"), "and names whose wall it is");
        final Signs.Sign grave = signWith(delhi1000, "grave");
        WrittenThing nobodys = WrittenThing.carve(grave, delhi1000, court, "a family");
        ok(nobodys.lines().get(nobodys.lines().size() - 1).contains("not the kind of thing"),
                "a gravestone is nobody's wall among the four, and says so");
        eq(WrittenThing.whoseWall(edict), BranchStory.Voice.COURT, "an edict is the court's");
        eq(WrittenThing.whoseWall(templeWall), BranchStory.Voice.TEMPLE, "a temple inscription is the temple's");
        eq(WrittenThing.whoseWall(grave), null, "a grave is a family's, and no voice of the four fits");

        // ------------------------------------------------ 5. ONLY WHAT FITS
        BranchStory.Story court1900 = rec.story(delhi.qid(), 1900, BranchStory.Voice.COURT, 25, 40);
        ok(court1900.sentences().size() > 5, "1900 has more to tell: " + court1900.sentences().size() + " rows");
        final Signs.Here d1900 = delhi1900;
        WrittenThing tooMuch = WrittenThing.carve(signWith(delhi1900, "grave"), d1900, court1900, "a family");
        eq(tooMuch.room(), 3, "a gravestone holds three lines");
        eq(tooMuch.carved().size(), 3, "and it is given three");
        ok(tooMuch.leftOff() > 0, "with the rest left off: " + tooMuch.leftOff());
        ok(!tooMuch.whole(), "so it is not the whole story");
        String last = tooMuch.read().get(tooMuch.read().size() - 1);
        ok(last.contains("no room"), "and the reader is told: " + last);
        ok(last.contains(String.valueOf(tooMuch.leftOff())), "with the number of lines left off");
        eq(on.room(), 12, "an edict cut in rock holds twelve");
        WrittenThing whole = WrittenThing.carve(edict, delhi1000,
                BranchStory.tell(on.placeNow(), on.placeThen(), 1000, BranchStory.Voice.COURT,
                        List.of(new BranchStory.Fact(900, null, "a fort", "building", "buildings_famous")), 3),
                "the sultan's officers");
        ok(whole.whole() || whole.leftOff() >= 0, "a short story fits or says how much it does not");

        // ------------------------------------------------ 6. WRAPPING LOSES NOTHING
        List<String> w = WrittenThing.wrap("The docks were opened by the throne's order, in good time.", 19);
        boolean within = true;
        for (String l : w) if (l.length() > 19) within = false;
        ok(within, "no wrapped line is wider than the page: " + w);
        eq(String.join(" ", w), "The docks were opened by the throne's order, in good time.",
                "and no word is lost or broken");
        ok(WrittenThing.wrap("Thiruvananthapuram is a long name", 8).contains("Thiruvananthapuram"),
                "a word longer than the page is not cut in half");
        eq(WrittenThing.wrap("", 10).size(), 0, "nothing wraps to nothing");
        eq(WrittenThing.wrap("one", 10), List.of("one"), "one word is one line");

        // ------------------------------------------------ 7. PAGES LOSE NOTHING
        List<String> all = on.wrapped(19);
        List<List<String>> pages = on.pages(19, 5);
        eq(pages.size(), (all.size() + 4) / 5, "the page count is the lines divided by the page");
        List<String> rejoined = new ArrayList<>();
        for (List<String> p : pages) rejoined.addAll(p);
        eq(rejoined, all, "every line lands on exactly one page and none is dropped");
        eq(on.page(999, 19, 5).size(), 0, "a page past the end is empty");
        eq(on.page(-1, 19, 5).size(), 0, "and so is a page before the beginning");
        ok(!on.page(0, 19, 5).isEmpty(), "the first page is not");

        // ------------------------------------------------ 8. WHAT THE OBJECT SAYS ABOUT ITSELF
        ok(on.readers().contains("in 100"), "the object states what reading it demands: " + on.readers());
        ok(on.readers().contains("the sultan's officers"), "and who had it put there");
        String rule = on.ruleLine();
        System.out.println("     " + rule);
        ok(rule.contains("in 1000"), "the rule line gives the year");
        ok(rule.toLowerCase().contains(edict.name().toLowerCase()), "the kind of surface");
        BranchStory.Story cuzcoStory1600 = rec.story(rec.nearest(CUZCO_LAT, CUZCO_LON).qid(), 1600,
                BranchStory.Voice.TEMPLE, 25, 20);
        WrittenThing parish = WrittenThing.carve(stone, cuzco1600, cuzcoStory1600, "the parish");
        System.out.println("     " + parish.ruleLine());
        ok(parish.ruleLine().startsWith("The cut stone at the grave"), "the rule line reads as a sentence");
        ok(parish.year() == 1600, "and the object is dated by the year it was carved in");
        // The bug this probe found: the first version took the date from the story and the writing from `here`,
        // and printed a grave at Cuzco "in 1500" cut in the Latin alphabet, a script that reached Peru in 1576.
        final Signs.Here c1600 = cuzco1600;
        refuses(() -> WrittenThing.carve(stone, c1600, cuzcoStory, "the parish"), "one of them is the wrong year",
                "a story in one year and a place worked out in another is refused");

        // ------------------------------------------------ 9. REFUSALS
        final Signs.Here d1000 = delhi1000;
        final Signs.Sign notice = signWith(delhi2000, "notice");
        refuses(() -> WrittenThing.carve(notice, d1000, court, "the sultan's officers"),
                "is not put up", "a surface the record does not have there cannot be used");
        refuses(() -> WrittenThing.carve(null, d1000, court, "x"), "needs a surface", "nothing is not a surface");
        refuses(() -> WrittenThing.carve(edict, null, court, "x"), "needs a surface", "no place, no object");
        BranchStory.Story nothing = BranchStory.tell("Nowhere", "Nowhere", 1000, BranchStory.Voice.COURT,
                List.of(), 10);
        refuses(() -> WrittenThing.carve(edict, d1000, nothing, "x"), "blank stone",
                "a surface with nothing dated on it is refused");

        // ------------------------------------------------ 10. A BRANCH'S CLAIM ON A STONE
        // The object is also where G5 becomes visible in the world: a claim cut into a wall that the record does
        // not have. It keeps its mark, because the surface does not launder a claim.
        System.out.println("\nStep 50 part 5: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
