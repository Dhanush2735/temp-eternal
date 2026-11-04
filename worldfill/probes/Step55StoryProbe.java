/* Step 55 part 3 (H6 first half): the history and people of one ruptured universe. The claim: every line
   says where and when and who wrote it; the mark (recorded or projected) is COMPUTED from the year and
   never declared; past 2026 a line may continue a state but never names a new ruler, person, war, event,
   disaster, price or population; and a person is never projected at all. */
import com.eternalengine.clock.Timeline;
import com.eternalengine.story.UniverseStory;
import com.eternalengine.timeline.Provenance;

public class Step55StoryProbe {
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

    static void refused(UniverseStory.LineWritten w, String words, String what) {
        checks++;
        if (w.ok()) {
            failed++;
            System.out.println("  FAIL " + what + "  (a line was written)");
            return;
        }
        for (String why : w.refused()) {
            if (why.contains(words)) return;
        }
        failed++;
        System.out.println("  FAIL " + what + "  no refusal says \"" + words + "\"; got " + w.refused());
    }

    static void refused(UniverseStory.PersonNamed p, String words, String what) {
        checks++;
        if (p.ok()) {
            failed++;
            System.out.println("  FAIL " + what + "  (a person was named)");
            return;
        }
        for (String why : p.refused()) {
            if (why.contains(words)) return;
        }
        failed++;
        System.out.println("  FAIL " + what + "  no refusal says \"" + words + "\"; got " + p.refused());
    }

    public static void main(String[] args) {
        UniverseStory story = UniverseStory.of("u-cuzco-1576");

        // ------------------------------------------------ 1. A LINE, AND ITS COMPUTED MARK
        UniverseStory.LineWritten w = story.add(1576, "Cuzco", "the fall is recorded in the book",
                Provenance.OBSERVED, "");
        ok(w.ok(), "a recorded line is written: " + (w.ok() ? "" : w.refused()));
        eq(w.line().mark(), "recorded", "and its mark is computed from the year");
        ok(w.line().line().startsWith("u-cuzco-1576 · Cuzco · 1576 [recorded, observed]"),
                "in words: " + w.line().line());
        UniverseStory.LineWritten w2 = story.add(2100, "Cuzco", "the sea is still high",
                Provenance.MODELLED, "");
        ok(w2.ok(), "a projected line that continues a state is written");
        eq(w2.line().mark(), "projected", "and it is marked projected");
        ok(UniverseStory.guardFor(2100) != null, "the guardrail note speaks for 2100");
        eq(UniverseStory.guardFor(1576), null, "and is silent inside the record");

        // ------------------------------------------------ 2. THE GUARDRAIL REFUSES, BY NAME
        refused(story.add(2100, "Cuzco", "the king still rules the highlands", Provenance.MODELLED, ""),
                "says \"king\"", "a projection naming a ruler is refused");
        refused(story.add(2200, "Cuzco", "the war goes on", Provenance.MODELLED, ""),
                "says \"war\"", "a projection naming a war is refused");
        refused(story.add(2300, "Cuzco", "the population is 5,000", Provenance.MODELLED, ""),
                "says \"population\"", "a projection naming a population is refused");
        refused(story.add(2400, "Cuzco", "the price of maize is 4", Provenance.MODELLED, ""),
                "says \"price\"", "a projection naming a price is refused");
        ok(story.add(1576, "Cuzco", "the king fell with the city", Provenance.OBSERVED, "").ok(),
                "inside the record, kings are history and are written");
        eq(story.history().size(), 3, "and only the lawful lines exist (the fall, the sea, and the king who fell in 1576)");

        // ------------------------------------------------ 3. WHO WROTE IT
        refused(story.add(1600, "Cuzco", "the rebuilt walls stand", Provenance.AUTHORED, ""),
                "signs its name", "an authored line with no author is refused");
        refused(story.add(1600, "Cuzco", "", Provenance.OBSERVED, ""),
                "blank line", "a blank line is refused");
        refused(story.add(1600, " ", "the walls stand", Provenance.OBSERVED, ""),
                "says where", "a line with no place is refused");
        refused(story.add(1600, "Cuzco", "the walls stand", null, ""),
                "who wrote it", "a line with no provenance is refused");
        ok(story.add(1600, "Cuzco", "the rebuilt walls stand", Provenance.AUTHORED, "Sam").ok(),
                "an authored line with its author is written");
        refused(UniverseStory.of("  ").add(1576, "Cuzco", "x", Provenance.OBSERVED, ""),
                "which universe", "and a universe with no name keeps no history");

        // ------------------------------------------------ 4. PEOPLE: NEVER PROJECTED
        UniverseStory.PersonNamed p = story.name("Huayna Capac", 1464, 1527, "ruler", Provenance.OBSERVED, "");
        ok(p.ok(), "a person of the record is named: " + (p.ok() ? "" : p.refused()));
        ok(p.person().line().contains("1464-1527"), "in words: " + p.person().line());
        refused(story.name("", 1, 2, "", Provenance.OBSERVED, ""), "no name is nobody",
                "a person with no name is refused");
        refused(story.name("Timeless", 1500, 1400, "", Provenance.OBSERVED, ""), "before 1500",
                "a death before a birth is refused");
        refused(story.name("The Child", 2100, null, "", Provenance.MODELLED, ""), "never projected",
                "a projected person is refused");
        refused(story.name("The Child", 2100, null, "", Provenance.AUTHORED, ""),
                "signs its name", "an authored person with no author is refused");
        ok(story.name("The Traveller", 2100, null, "traveller", Provenance.AUTHORED, "Sam").ok(),
                "but a player may author someone the record does not hold");
        eq(story.people().size(), 2, "and only the lawful people exist");
        ok(story.peoplePage().get(0).contains("u-cuzco-1576"), "the people page says which universe: "
                + story.peoplePage().get(0));

        // ------------------------------------------------ 5. THE PAGES AND THE RULE
        eq(story.page().size(), 4, "the history page carries its four lines");
        ok(story.page().get(1).contains("[projected, modelled]"),
                "each with its computed mark: " + story.page().get(1));
        System.out.println("     " + UniverseStory.ruleLine());
        ok(UniverseStory.ruleLine().contains("never declared"), "the rule keeps the computed mark");
        ok(UniverseStory.ruleLine().contains("never projected at all"), "and the person rule");
        ok(UniverseStory.ruleLine().contains("population"), "and the guardrail's subjects");

        System.out.println("\nStep 55 part 3: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
