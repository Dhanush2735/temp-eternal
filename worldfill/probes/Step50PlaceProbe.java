/* Step 50 part 4 (the join, and G5): a story read out of the real packs, and knowledge a branch has that the
   record does not.
   The claim: nothing in part 2 or 3 could read a pack, and now something does. Every fact carries the pack it
   came from and how sure the pack is of it, an estimated year is never promoted to an observed one, and a
   branch's own knowledge stays in that branch. */
import com.eternalengine.knowledge.BranchKnowledge;
import com.eternalengine.knowledge.KnowledgeCard;
import com.eternalengine.knowledge.VoicedCard;
import com.eternalengine.story.BranchStory;
import com.eternalengine.story.PlaceRecord;
import com.eternalengine.timeline.Provenance;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.zip.GZIPInputStream;

public class Step50PlaceProbe {
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

    static final String HISTORY = "/data/eternalengine/eternal/history/";

    static JsonObject pack(String name) {
        try (InputStream in = new GZIPInputStream(Step50PlaceProbe.class.getResourceAsStream(HISTORY + name));
             InputStreamReader r = new InputStreamReader(in, StandardCharsets.UTF_8)) {
            return JsonParser.parseReader(r).getAsJsonObject();
        } catch (Exception e) {
            throw new IllegalStateException("cannot read " + name, e);
        }
    }

    static boolean near(double lat1, double lon1, double lat2, double lon2, double radius) {
        return PlaceRecord.km(lat1, lon1, lat2, lon2) <= radius;
    }

    /** The fixture card: two questions, one dated answer each, nobody's name on either. */
    static KnowledgeCard card() {
        List<KnowledgeCard.Question> qs = new ArrayList<>();
        qs.add(new KnowledgeCard.Question("docks", "Who built the docks?", 1, List.of(
                new KnowledgeCard.Answer(1872, KnowledgeCard.OPEN, "The docks were opened in 1872.", null))));
        qs.add(new KnowledgeCard.Question("harbour", "What is the harbour like?", 1, List.of(
                new KnowledgeCard.Answer(1800, KnowledgeCard.OPEN, "The harbour is shallow and busy.", null))));
        return new KnowledgeCard("mumbai", "Bombay", null, "Place", 1, 1700, 19.07, 72.87, qs,
                List.of(), List.of(), List.of(), false);
    }

    public static void main(String[] args) throws Exception {
        PlaceRecord rec = PlaceRecord.load(
                new GZIPInputStream(Step50PlaceProbe.class.getResourceAsStream(HISTORY + "towns.json.gz")),
                new GZIPInputStream(Step50PlaceProbe.class.getResourceAsStream(HISTORY + "buildings_famous.json.gz")),
                new GZIPInputStream(Step50PlaceProbe.class.getResourceAsStream(HISTORY + "ways_works.json.gz")));

        // ------------------------------------------------ 1. THE PACKS THROUGH THE JOIN
        eq(rec.townCount(), 30151, "every town is read");
        eq(rec.buildingCount(), 23535, "every famous building is read");
        eq(rec.workCount(), 110447, "every work is read");
        // Two different numbers, and the notes had them confused: 3,892 towns carry names, and 2,582 of those
        // have a name the pack actually dates. An undated name cannot be a sentence with a year on it.
        eq(rec.townsWithNames(), 3892, "3,892 towns carry names at all");
        eq(rec.townsWithDatedNames(), 2582, "and 2,582 of them have a dated name, which is what a story is told in");
        System.out.println("     undated: " + rec.undated());

        // ------------------------------------------------ 2. THE NAME THE PLACE HAD THAT YEAR
        PlaceRecord.Town mumbai = rec.town("Q1156");
        ok(mumbai != null, "Mumbai is in the pack");
        eq(mumbai.nameIn(1850), "Bombay", "Bombay in 1850");
        eq(mumbai.nameIn(1700), "Bombay", "Bombay in 1700, before the first dated stretch too");
        eq(mumbai.nameIn(1995), "Mumbai", "Mumbai in 1995, the year the change takes effect");
        eq(mumbai.nameIn(2020), "Mumbai", "and still Mumbai");
        eq(mumbai.nowNameCameIn(), 1995, "the pack dates the change to 1995");
        eq(rec.namingLine("Q1156", 1850),
                "It is Bombay in 1850, and Mumbai is what it is called now: the record dates the change to 1995.",
                "the naming line comes out of the pack and not out of a table in the probe");
        System.out.println("     " + rec.namingLine("Q1156", 1850));

        // ------------------------------------------------ 3. FACTS CARRY THEIR PACK AND THEIR CERTAINTY
        List<BranchStory.Fact> f1900 = rec.facts(mumbai, 25, 1900);
        ok(f1900.size() > 5, "Mumbai has a story's worth of dated rows by 1900: " + f1900.size());
        boolean allDated = true, allSourced = true, noneFromTheFuture = true, allMarked = true;
        for (BranchStory.Fact f : f1900) {
            if (f.name().isEmpty()) allDated = false;
            if (f.record().isEmpty()) allSourced = false;
            if (f.year() > 1900) noneFromTheFuture = false;
            if (f.provenance() == null) allMarked = false;
        }
        ok(allDated, "every fact has a name");
        ok(allSourced, "every fact names the pack it came from");
        ok(noneFromTheFuture, "and none of them is in the story's own future");
        ok(allMarked, "every fact says what it rests on");
        boolean sawWorks = false, sawBuildings = false;
        for (BranchStory.Fact f : f1900) {
            if (f.record().equals("ways_works")) sawWorks = true;
            if (f.record().equals("buildings_famous")) sawBuildings = true;
        }
        ok(sawWorks, "the works pack reaches the story");
        ok(sawBuildings, "and so does the buildings pack");

        // ------------------------------------------------ 4. AN ESTIMATE IS NEVER PROMOTED
        // Recomputed here from the raw pack, so the join is checked against something that is not itself.
        JsonObject works = pack("ways_works.json.gz");
        int estNear = 0;
        for (JsonElement e : works.getAsJsonArray("works")) {
            JsonArray r = e.getAsJsonArray();
            Integer year = r.get(3).isJsonNull() ? null : r.get(3).getAsInt();
            if (year == null || year > 2000) continue;
            if (!near(mumbai.lat(), mumbai.lon(), r.get(0).getAsDouble(), r.get(1).getAsDouble(), 200)) continue;
            if (r.get(7).getAsInt() == 1) estNear++;
        }
        List<BranchStory.Fact> wide = rec.facts(mumbai, 200, 2000);
        int modelledWorks = 0;
        for (BranchStory.Fact f : wide) {
            if (f.record().equals("ways_works") && f.provenance() == Provenance.MODELLED) modelledWorks++;
        }
        eq(modelledWorks, estNear, "every estimated work year within 200 km is marked modelled and no other is");
        ok(estNear > 0, "and there are some, so the check is not vacuous: " + estNear);

        JsonObject builds = pack("buildings_famous.json.gz");
        int gazetteerNear = 0;
        int recordedBuildingsNear = 0;
        for (JsonElement e : builds.getAsJsonArray("buildings")) {
            JsonArray r = e.getAsJsonArray();
            Integer year = r.get(4).isJsonNull() ? null : r.get(4).getAsInt();
            if (year == null || year > 2000) continue;
            if (!near(mumbai.lat(), mumbai.lon(), r.get(1).getAsDouble() / 1000.0, r.get(2).getAsDouble() / 1000.0, 200)) continue;
            if ("gazetteer".equals(r.get(7).getAsString())) gazetteerNear++;
            else recordedBuildingsNear++;
        }
        int modelledBuildings = 0;
        for (BranchStory.Fact f : wide) {
            if (f.record().equals("buildings_famous") && f.provenance() == Provenance.MODELLED) modelledBuildings++;
        }
        eq(modelledBuildings, gazetteerNear, "a building dated from the gazetteer's window is modelled, and the count matches");

        // And the other half of the same rule: what the pack records is observed. Across the whole pack the
        // record dominates, 82,304 works with a year from Wikidata against 28,143 estimated ones.
        int recordedWorks = 0;
        int observedNear = 0;
        for (JsonElement e : works.getAsJsonArray("works")) {
            JsonArray r = e.getAsJsonArray();
            if (r.get(7).getAsInt() == 0) recordedWorks++;
            Integer year = r.get(3).isJsonNull() ? null : r.get(3).getAsInt();
            if (year == null || year > 2000) continue;
            if (near(mumbai.lat(), mumbai.lon(), r.get(0).getAsDouble(), r.get(1).getAsDouble(), 200)
                    && r.get(7).getAsInt() == 0) {
                observedNear++;
            }
        }
        eq(recordedWorks, 82304, "82,304 works carry a year that Wikidata records");
        // THE FINDING, and it is not the one this probe expected: across the pack the record dominates, and
        // where the works are dense it does not. Within 200 km of Mumbai only 58 works of 260 carry a recorded
        // year; the other 202 take theirs from the technology atlas. A story told there is mostly marked, and
        // the mark is the honest part of it.
        ok(estNear > observedNear, "but near Mumbai the estimated years outnumber the recorded ones, "
                + estNear + " to " + observedNear);
        int observed = 0;
        for (BranchStory.Fact f : wide) {
            if (f.provenance() == Provenance.OBSERVED) observed++;
        }
        eq(observed, observedNear + recordedBuildingsNear,
                "and every fact the join calls observed is one the pack records: " + observedNear + " works and "
                        + recordedBuildingsNear + " buildings");

        // ------------------------------------------------ 5. A RADIUS IS A RADIUS
        ok(rec.facts(mumbai, 5, 1900).size() <= f1900.size(), "a smaller radius holds no more");
        ok(rec.facts(mumbai, 500, 1900).size() >= f1900.size(), "a larger radius holds no less");

        // ------------------------------------------------ 6. THE STORY OUT OF THE PACKS
        BranchStory.Story story = rec.story("Q1156", 1900, BranchStory.Voice.COURT, 25, 30);
        ok(!story.empty(), "1900 has a story: " + story.sentences().size() + " sentences");
        boolean ordered = true, sourced = true, inPast = true, marked = true;
        for (int i = 0; i < story.sentences().size(); i++) {
            BranchStory.Sentence s = story.sentences().get(i);
            if (i > 0 && s.year() < story.sentences().get(i - 1).year()) ordered = false;
            if (s.record().isEmpty()) sourced = false;
            if (s.year() > 1900) inPast = false;
            if (s.provenance() == null) marked = false;
            ok(s.text().length() > 20, "sentence " + i + " is a sentence");
        }
        ok(ordered, "in order");
        ok(sourced, "every sentence carries the row behind it");
        ok(inPast, "and nothing from after the year it is told in");
        ok(marked, "every sentence says what it rests on");
        eq(story.name(), "Bombay", "told in the name the place had in 1900");
        System.out.println("     " + story.asMarkedText().split("\n")[0]);
        System.out.println("     " + story.markedLines().size() + " lines, of which "
                + (story.markedLines().size() - 1 - story.sentences().size()) + " are extra");
        eq(story.markedLines().size(), story.sentences().size() + 1, "a header and one line a sentence");
        Boolean anyMarked = null;
        for (BranchStory.Sentence s : story.sentences()) {
            if (s.provenance() != Provenance.OBSERVED) anyMarked = true;
        }
        // A long story over a wide radius has to show at least one mark, because a third of the works pack does
        // not carry a recorded year and near Mumbai it is most of it.
        BranchStory.Story wideStory = rec.story("Q1156", 2000, BranchStory.Voice.TAX_ROLL, 200, 400);
        ok(wideStory.asMarkedText().contains("(modelled)") || wideStory.asMarkedText().contains("(structural)"),
                "a wide story in 2000 shows the marks a reader needs");
        if (anyMarked != null) {
            ok(story.asMarkedText().contains("(structural)") || story.asMarkedText().contains("(modelled)"),
                    "an estimated sentence is marked in the text a reader gets");
        } else {
            ok(true, "nothing in this story is estimated, so there is nothing to mark");
        }

        // Nothing dated before the story's year is not a claim that nothing happened.
        BranchStory.Story ancient = rec.story("Q1156", -3000, BranchStory.Voice.COURT, 25, 30);
        if (ancient.empty()) {
            ok(ancient.refused().contains("not a claim that nothing happened"),
                    "an empty story says what it is not: " + ancient.refused());
        } else {
            ok(true, "there is something dated at 3000 BC here, and it is told");
        }

        // ------------------------------------------------ 7. CALLER MISTAKES FAIL LOUDLY
        throwsUp(() -> rec.story("Q0-nothing", 1900, BranchStory.Voice.COURT, 25, 30), "a town that is not in the pack is refused");
        throwsUp(() -> rec.namingLine("Q0-nothing", 1900), "and so is a naming line for one");

        // ------------------------------------------------ 8. G5: WHAT ONE BRANCH KNOWS
        BranchKnowledge a = BranchKnowledge.of("branch-a");
        ok(a.empty(), "a new branch knows nothing the record does not");
        ok(a.ruleLine().contains("nothing has come to it"), "and says so: " + a.ruleLine());

        a = a.claim(1901, "docks", "The new dock works, and it works because I built it.", "Asha",
                BranchStory.Voice.TEMPLE);
        eq(a.claims().size(), 1, "one claim");
        ok(a.knows("docks"), "the branch knows something about the docks");
        ok(!a.knows("harbour"), "and nothing about the harbour");
        eq(a.claims().get(0).sentence().provenance(), Provenance.AUTHORED, "a claim is authored");
        ok(!a.claims().get(0).inTheRecord(), "and is never the record's");
        ok(a.claims().get(0).line().contains("Asha"), "the line names the author: " + a.claims().get(0).line());
        eq(a.by("Asha").size(), 1, "and can be found by author");
        eq(a.by("Somebody Else").size(), 0, "and not by somebody who said nothing");
        eq(a.unverified(), 0, "an authored claim is not unverified, it is merely somebody's");

        a = a.hearsay(1901, "docks", "the dock works", BranchStory.Voice.TRAVELLER);
        eq(a.claims().size(), 2, "a rumour is a second claim");
        ok(a.claims().get(1).isRumour(), "and is marked as a rumour");
        eq(a.unverified(), 1, "one claim is unverified");
        ok(a.ruleLine().contains("branch-a"), "the rule line says which timeline this belongs to: " + a.ruleLine());
        thumb(a, 2);

        // ------------------------------------------------ 9. AND NO OTHER BRANCH KNOWS IT
        BranchKnowledge b = BranchKnowledge.of("branch-b");
        ok(b.empty(), "the other branch of the same year knows nothing of it");
        eq(b.claims().size(), 0, "not one claim crosses over");
        ok(!b.knows("docks"), "the other branch cannot answer the question at all");

        // ------------------------------------------------ 10. ATTACHING IT TO A CARD
        BranchKnowledge.Attached at = a.attach(VoicedCard.of(card()));
        eq(at.unattached().size(), 0, "both claims find their question");
        List<VoicedCard.Spoken> on = at.card().accounts("docks", 1905);
        eq(on.size(), 2, "the card holds the claim and the rumour beside its own anonymous answer");
        ok(at.card().severalAccounts("docks", 1905), "so the branch's card disagrees with itself");
        String read = at.card().asText("docks", 1905);
        System.out.println("     " + read.replace("\n", "\n     "));
        ok(read.contains("(authored)") && read.contains("(modelled)"), "with both marks on the page");
        ok(!read.contains("readings of the same rows"), "and no claim that this is all from the record");

        BranchKnowledge.Attached elsewhere = b.attach(VoicedCard.of(card()));
        eq(elsewhere.unattached().size(), 0, "the other branch attaches nothing and loses nothing");
        eq(elsewhere.card().accounts("docks", 1905).size(), 1, "its card has only its own answer");
        ok(!elsewhere.card().asText("docks", 1905).contains("(authored)"), "and no authored line on it");

        BranchKnowledge stray = BranchKnowledge.of("branch-c")
                .claim(1901, "no-such-question", "A thing about nothing in particular.", "Asha",
                        BranchStory.Voice.COURT);
        BranchKnowledge.Attached lost = stray.attach(VoicedCard.of(card()));
        eq(lost.unattached().size(), 1, "a claim on a question the card does not ask is reported, not dropped");
        ok(lost.unattached().get(0).contains("no-such-question"), "and it says which: " + lost.unattached().get(0));
        eq(lost.card().spoken().size(), 0, "so the card is unchanged");

        // ------------------------------------------------ 11. MISTAKES IN THE CALLER
        throwsUp(() -> BranchKnowledge.of(""), "a branch with no id is refused");
        throwsUp(() -> BranchKnowledge.of("x").claim(1901, "docks", "text", "", BranchStory.Voice.COURT),
                "an authored claim with no author is refused");
        throwsUp(() -> BranchKnowledge.of("x").claim(1901, "", "text", "Asha", BranchStory.Voice.COURT),
                "a claim answering no question is refused");
        BranchKnowledge forNull = a;
        throwsUp(() -> forNull.attach(null), "nothing to attach to is refused");

        List<String> trail = a.trail();
        eq(trail.size(), 2, "the trail has both lines");
        System.out.println("     trail: " + String.join(" | ", trail));

        System.out.println("\nStep 50 part 4: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }

    /** Small helper so a check on the whole rule line does not have to be written twice. */
    static void thumb(BranchKnowledge a, int n) {
        eq(a.claims().size(), n, "still " + n + " claims after the last addition");
    }
}
