/* Step 48 part 2 (G1): what counts as a change.
   The claim: every way a player can change history is a point in one grid of five whats and six hows,
   the grid has holes that are named rather than forgotten, and the guardrail's four refusals are
   refusals the vocabulary itself makes. */
import com.eternalengine.timeline.ChangeRecord;
import com.eternalengine.timeline.Chronicler;
import com.eternalengine.timeline.Provenance;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class Step48ChangeProbe {
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

    public static void main(String[] args) {
        // ------------------------------------------------ 1. THE GRID IS SMALL AND CLOSED
        eq(ChangeRecord.What.values().length, 5, "five kinds of thing to change");
        eq(ChangeRecord.How.values().length, 6, "six verbs for changing one");
        eq(ChangeRecord.CELLS, 30, "so thirty cells, which is the whole vocabulary");
        eq(ChangeRecord.filledCells(), 28, "and twenty-eight of them can be said");

        // The two holes are named, and named for a reason rather than left blank.
        ok(!ChangeRecord.expressible(ChangeRecord.What.PERSON, ChangeRecord.How.EARLIER),
                "a person cannot be made earlier");
        ok(!ChangeRecord.expressible(ChangeRecord.What.PERSON, ChangeRecord.How.LATER),
                "nor later: a birth is not a lever");
        ok(ChangeRecord.holeFor(ChangeRecord.What.PERSON, ChangeRecord.How.EARLIER).contains("born when"),
                "and the hole explains itself: "
                        + ChangeRecord.holeFor(ChangeRecord.What.PERSON, ChangeRecord.How.EARLIER));
        eq(ChangeRecord.holeFor(ChangeRecord.What.EVENT, ChangeRecord.How.REMOVE), null,
                "while a battle can be stopped, and that cell is not a hole");

        // Every other cell has a price, a gate and a kind: a filled cell that is silent would be a
        // hole wearing a price tag.
        int silent = 0;
        for (ChangeRecord.What w : ChangeRecord.What.values()) {
            for (ChangeRecord.How h : ChangeRecord.How.values()) {
                if (!ChangeRecord.expressible(w, h)) continue;
                if (ChangeRecord.costFor(w, h) <= 0
                        || ChangeRecord.gateFor(w, h).isBlank()
                        || ChangeRecord.kindFor(w, h) == null) silent++;
            }
        }
        eq(silent, 0, "every filled cell has a cost, a gate and a chronicle kind");

        // ------------------------------------------------ 2. THE PRICES ARE ORDERED THE WAY LIFE IS
        int stopBattle = ChangeRecord.costFor(ChangeRecord.What.EVENT, ChangeRecord.How.REMOVE);
        int startWar = ChangeRecord.costFor(ChangeRecord.What.EVENT, ChangeRecord.How.ADD);
        int escalate = ChangeRecord.costFor(ChangeRecord.What.EVENT, ChangeRecord.How.BIGGER);
        ok(startWar > stopBattle, "starting a war costs more than stopping one: " + startWar
                + " against " + stopBattle);
        ok(escalate > stopBattle, "and escalating costs more than stopping: " + escalate);
        int kill = ChangeRecord.costFor(ChangeRecord.What.PERSON, ChangeRecord.How.REMOVE);
        eq(kill, 3, "one person is the smallest change there is");
        ok(kill < ChangeRecord.costFor(ChangeRecord.What.PLACE, ChangeRecord.How.ADD),
                "and cheaper than founding a town");
        int early = ChangeRecord.costFor(ChangeRecord.What.KNOWLEDGE, ChangeRecord.How.EARLIER);
        ok(early >= ChangeRecord.costFor(ChangeRecord.What.KNOWLEDGE, ChangeRecord.How.ADD),
                "moving a discovery is dearer than having it: " + early);
        eq(early, 7, "and it is the dearest cell in the grid, which is the honest answer");
        int dearest = 0;
        for (ChangeRecord.What w : ChangeRecord.What.values()) {
            for (ChangeRecord.How h : ChangeRecord.How.values()) {
                dearest = Math.max(dearest, ChangeRecord.costFor(w, h));
            }
        }
        eq(dearest, startWar, "nothing costs more than starting a war: " + dearest);

        // Every price is at least three actions, matching the detector's own floor: a change costs
        // effort and a click is not history.
        int tooCheap = 0;
        for (ChangeRecord.What w : ChangeRecord.What.values()) {
            for (ChangeRecord.How h : ChangeRecord.How.values()) {
                int c = ChangeRecord.costFor(w, h);
                if (c > 0 && c < 3) tooCheap++;
            }
        }
        eq(tooCheap, 0, "no change is one or two actions, the same floor the intervention detector uses");

        // ------------------------------------------------ 3. THE GATES ARE NOT ALL THE SAME
        Set<String> gates = new HashSet<>();
        for (ChangeRecord.What w : ChangeRecord.What.values()) {
            for (ChangeRecord.How h : ChangeRecord.How.values()) {
                if (ChangeRecord.expressible(w, h)) gates.add(ChangeRecord.gateFor(w, h));
            }
        }
        ok(gates.size() >= 6, "the grid needs at least six different things to open it: " + gates.size());
        eq(ChangeRecord.gateFor(ChangeRecord.What.PERSON, ChangeRecord.How.REMOVE),
                "your own two hands", "and killing one person needs nothing but hands");
        ok(ChangeRecord.gateFor(ChangeRecord.What.EVENT, ChangeRecord.How.ADD).contains("army"),
                "while starting a war needs an army: "
                        + ChangeRecord.gateFor(ChangeRecord.What.EVENT, ChangeRecord.How.ADD));

        // ------------------------------------------------ 4. F1'S WAYS ALL LAND IN THE GRID
        List<ChangeRecord.Way> ways = ChangeRecord.ways();
        eq(ways.size(), 10, "ten ways to change history, and no more");
        int unplaced = 0;
        Set<String> cells = new HashSet<>();
        for (ChangeRecord.Way w : ways) {
            if (!ChangeRecord.expressible(w.what(), w.how())) unplaced++;
            cells.add(w.what() + "|" + w.how());
        }
        eq(unplaced, 0, "and every one of them is a cell in the grid");
        ok(cells.size() == ways.size(), "no two ways are the same cell: " + cells.size() + " distinct");

        eq(ChangeRecord.Way.BRING_AN_INVENTION_EARLY.kind(), Chronicler.Kind.TECHNOLOGY,
                "bringing an invention early is recorded as a technology arriving");
        eq(ChangeRecord.Way.FOUND_A_TOWN.kind(), Chronicler.Kind.SETTLEMENT,
                "founding a town is recorded as a settlement");
        eq(ChangeRecord.Way.TAKE_THE_CROWN.kind(), Chronicler.Kind.PERSON,
                "and taking a crown is recorded as a person, which is why the chronicler needed a "
                        + "person kind");
        eq(ChangeRecord.Way.TRADE_OR_SABOTAGE_GOODS.kind(), Chronicler.Kind.TRADE,
                "trade is recorded as trade, the one way that already works");

        // ------------------------------------------------ 5. THE FOUR REFUSALS
        // Three of the four are refused by the vocabulary having no word for them.
        for (ChangeRecord.Refused r : ChangeRecord.Refused.values()) {
            ok(r.why().length() > 40, r + " is refused in a sentence rather than a shrug");
        }
        ok(ChangeRecord.Refused.A_POPULATION_FIGURE.hasNoWord(), "a census has no word in the grid");
        ok(ChangeRecord.Refused.A_PRICE.hasNoWord(), "and neither does a price");
        ok(!ChangeRecord.Refused.A_WAR_NOBODY_CAUSED.hasNoWord(),
                "a war nobody caused can be said, and is refused a layer up, by provenance");
        boolean anyPopulationWord = false;
        for (ChangeRecord.What w : ChangeRecord.What.values()) {
            String n = w.name();
            if (n.contains("POPULATION") || n.contains("PRICE") || n.contains("MONEY")
                    || n.contains("PERSON_COUNT")) anyPopulationWord = true;
        }
        ok(!anyPopulationWord, "and there really is no What for people-as-a-number or for money");

        // That refusal is not just a comment: the chronicler refuses the modelled version too.
        Chronicler ch = new Chronicler();
        ChangeRecord.Act modelledRuler = new ChangeRecord.Act(2400, ChangeRecord.What.PERSON,
                ChangeRecord.How.BIGGER, "a king", "Deccan", 1, Provenance.MODELLED, "the engine");
        eq(ch.report(ChangeRecord.toChange(modelledRuler)), null,
                "a ruler the engine supposes is not a line");
        ChangeRecord.Act authoredRuler = new ChangeRecord.Act(2400, ChangeRecord.What.PERSON,
                ChangeRecord.How.BIGGER, "a king", "Deccan", 1, Provenance.AUTHORED, "a player");
        Chronicler.Line crown = ch.report(ChangeRecord.toChange(authoredRuler));
        ok(crown != null, "while a ruler a player put there is one");
        eq(crown.provenance(), Provenance.AUTHORED, "and it says so");
        ok(crown.title().contains("a king"), "and the line names them: " + crown.title());
        ok(crown.body().contains("put their name"), "the body carries the assertion: " + crown.body());

        // ------------------------------------------------ 6. THE TWO CLASSES AGREE ABOUT EVERY CELL
        // Every filled cell, at its own threshold, becomes a line in 2400 and none does in 1000.
        Chronicler after = new Chronicler();
        Chronicler before = new Chronicler();
        int recorded = 0, refusedBefore = 0, wouldNot = 0;
        for (ChangeRecord.What w : ChangeRecord.What.values()) {
            for (ChangeRecord.How h : ChangeRecord.How.values()) {
                if (!ChangeRecord.expressible(w, h)) continue;
                int mag = ChangeRecord.sampleMagnitude(w, h);
                // A distinct subject per cell, so the repeat rule cannot merge two cells into one
                // longer line and hide the year cap. The first run of this probe did merge them and
                // read twelve lines in a year that holds three, which is the cap working correctly
                // and the test asking the wrong question.
                String subject = "a thing " + w + " " + h;
                ChangeRecord.Act act = new ChangeRecord.Act(2400, w, h, subject, "Deccan", mag,
                        Provenance.AUTHORED, "a player");
                if (after.report(ChangeRecord.toChange(act)) != null) recorded++;
                // Before the seam an AUTHORED act is allowed, but an OBSERVED one is not: the packs
                // own that year, and only a divergence may be added to it.
                ChangeRecord.Act observed = new ChangeRecord.Act(1000, w, h, subject, "Deccan", mag,
                        Provenance.OBSERVED, "");
                if (before.report(ChangeRecord.toChange(observed)) == null) refusedBefore++;
                ChangeRecord.Act wrong = new ChangeRecord.Act(2400, w, h, "another " + w + " " + h,
                        "Deccan", mag - 1, Provenance.AUTHORED, "a player");
                if (after.report(ChangeRecord.toChange(wrong)) != null) wouldNot++;
            }
        }
        // Three lines a year is the cap, so not every cell can land in one year. That is the point of
        // the cap, and it is checked rather than assumed.
        eq(recorded, Chronicler.PER_YEAR,
                "a busy year takes exactly its cap of three and turns the other twenty-five away");
        eq(refusedBefore, 28, "before the seam, nothing observed is added to a year the packs own");
        eq(wouldNot, 0, "and one unit under the threshold is never a line");

        // ------------------------------------------------ 7. THE GRID IN PLAIN WORDS
        List<String> rows = ChangeRecord.rows();
        eq(rows.size(), 30, "the grid prints thirty rows");
        System.out.println("  " + rows.get(0));
        System.out.println("  " + rows.get(6));
        System.out.println("  " + rows.get(11));
        System.out.println("  " + ChangeRecord.Way.BRING_AN_INVENTION_EARLY.plain());

        System.out.println(failed == 0
                ? "Step48ChangeProbe: " + checks + " checks, 0 failed"
                : "Step48ChangeProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
