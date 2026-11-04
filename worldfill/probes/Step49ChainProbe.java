import com.eternalengine.timeline.Agency;
import com.eternalengine.timeline.ChangeRecord;
import com.eternalengine.timeline.Chronicler;
import com.eternalengine.timeline.DeedLedger;
import com.eternalengine.timeline.Depends;
import com.eternalengine.timeline.PlayerRoles;
import com.eternalengine.timeline.Provenance;
import com.eternalengine.timeline.Rulers;
import com.eternalengine.timeline.WhatIf;

import java.util.ArrayList;
import java.util.List;

/**
 * Step 49 part 6: the whole chain, end to end.
 *
 * <p>Every class in steps 48 and 49 has a probe of its own. This one exists because each of those probes
 * passed while the chain was broken: the parts have to be joined to find out that a merchant can found a
 * town, that a change to a war reaches a border, and that a ruler reacts to what the player did. Nothing
 * here tests a rule that is not tested elsewhere. It tests that the rules <b>meet</b>.
 */
public class Step49ChainProbe {
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
        DeedLedger ledger = new DeedLedger();
        int year = 1757;
        String place = "Saxony";
        long people = 40_000;

        // ------------------------------------------------ 1. A PLAYER STARTS AS NOTHING
        eq(ledger.roleOf("Asha", year), PlayerRoles.Role.NONE, "the player starts as nothing");
        List<ChangeRecord.Way> atStart = ledger.waysOf("Asha", year, place, people);
        System.out.println("     at the start: " + atStart);
        eq(atStart.size(), 2, "and can do exactly two things: touch a person and tell the future");

        // ------------------------------------------------ 2. WORKING MAKES THEM SOMETHING
        // Twenty sales, not ten: ten makes a merchant, and a merchant's following grows one head per sale,
        // so ten sales is a merchant who cannot yet found a town and twenty is one who can. That is the
        // join this probe exists to check, and it took a failing test to see the shape of it.
        for (int k = 0; k < 20; k++) ledger.sale("Asha", place, year);
        eq(ledger.roleOf("Asha", year), PlayerRoles.Role.MERCHANT, "ten sales makes them a merchant");
        List<ChangeRecord.Way> asMerchant = ledger.waysOf("Asha", year, place, people);
        System.out.println("     as a merchant: " + asMerchant);
        ok(asMerchant.size() > atStart.size(), "and opens more of the world: " + asMerchant.size()
                + " against " + atStart.size());
        ok(asMerchant.contains(ChangeRecord.Way.TRADE_OR_SABOTAGE_GOODS), "including trade");
        // THE BUG THIS PROBE WAS BUILT TO FIND, in three directions at once:
        // (a) founding a town wants twenty people who will stay, and a merchant had no following at all, so
        //     the one way a merchant's money is FOR was closed to every merchant alive. Part 4 now gives a
        //     merchant a following of their own custom, and the following is the one thing about a merchant
        //     that is rented rather than owned; (b) the merchant's purse was fine, so money was never the
        //     obstacle; (c) the ruler's own following was 100 court days' worth, so a ruler with an office'
        //     and no court behind them could not found a town either. Both are fixed in PlayerRoles.
        ok(asMerchant.contains(ChangeRecord.Way.FOUND_A_TOWN),
                "and founding a town, once twenty sales have brought twenty heads of custom: " + asMerchant);

        // ------------------------------------------------ 3. A WAY BECOMES AN ACT, AND AN ACT IS JUDGED
        ChangeRecord.Act town = new ChangeRecord.Act(year, ChangeRecord.What.PLACE, ChangeRecord.How.ADD,
                "New Ashabad", place, 40, Provenance.AUTHORED, "Asha");
        ok(ChangeRecord.expressible(town.what(), town.how()), "the act is a cell in the grid");
        eq(ChangeRecord.costFor(town.what(), town.how()), 5, "and it costs what the grid says, five actions");
        ok(ledger.waysOf("Asha", year, place, people).contains(ChangeRecord.Way.FOUND_A_TOWN),
                "and the player can pay for it, which is the join that matters");

        // ------------------------------------------------ 4. THE ACT BECOMES HISTORY
        Chronicler.Kind kind = ChangeRecord.kindFor(town.what(), town.how());
        eq(kind, Chronicler.Kind.SETTLEMENT, "the act is recorded as a settlement, by the grid and not by hand");
        Chronicler.Change change = ChangeRecord.toChange(town);
        ok(change != null, "and it converts to the recorder's own record");
        Chronicler.Line line = ledger.record("main", change);
        ok(line != null, "which becomes a line in this branch's chronicle: "
                + (line == null ? "null" : line.title()));
        eq(line.provenance(), Provenance.AUTHORED, "marked as the player's");
        eq(ledger.lines("main").size(), 1, "and exactly one line");

        // ------------------------------------------------ 5. A DEPENDENCY SAYS WHAT THE TOWN SITS INSIDE
        Depends.Node war = new Depends.Node(1756, 1763, "the Seven Years War", "war", 51.0, 13.0, 500);
        Depends.Node townNode = new Depends.Node(year, year, "New Ashabad", "political", 51.2, 11.6, 20);
        ok(townNode.inside(war), "the new town falls inside a recorded war");
        List<Depends.Edge> into = Depends.edgesInto(townNode, List.of(war), null);
        eq(into.size(), 1, "so the dependency graph finds one parent for it");
        ok(into.get(0).usable(), "and the edge is usable, being unambiguous");

        // ------------------------------------------------ 6. THE WHAT-IF FOLLOWS IT INTO THE REGISTERS
        WhatIf.World world = WhatIf.World.quiet(year, place, 51.2, 11.6)
                .withWar("Prussia", "Austria", place, 0.45)
                .withInvention("the steam engine", 1712)
                .withFaith("Protestantism", 0.40)
                .withSuccession("the king", List.of(
                        new WhatIf.Heir("the elder daughter", 0.55, 70, 1735),
                        new WhatIf.Heir("the younger son", 0.30, 40, 1740)),
                        WhatIf.SuccessionLaw.PRIMOGENITURE);
        double strength = WhatIf.strengthOf(town);
        ok(strength > 0, "the act has a strength: " + strength);
        WhatIf.Result aftermath = WhatIf.apply(town, world);
        ok(aftermath.changed(), "a town founded changes what follows in the world it is founded in");
        // A town is a place, and a place does not decide a succession: the heir must be untouched.
        WhatIf.Effect heir = aftermath.first(WhatIf.Field.HEIR);
        eq(heir, null, "and it does not touch the succession, because a town is not a person");
        // But the faith share moves, because a new town has people in it.
        WhatIf.Effect faith = aftermath.first(WhatIf.Field.FAITH);
        ok(faith != null && !faith.absorbed(), "while the faith share moves: "
                + (faith == null ? "null" : faith.line()));
        eq(aftermath.refused().size(), 2, "and the two refusals come back as they always do");

        // ------------------------------------------------ 7. A RULER REACTS, AND THE ANSWER IS EXPLAINED
        Rulers.Ruler king = new Rulers.Ruler("the king", 0.7, 300, 0.6);
        Rulers.Choice reaction = Rulers.reactTo(king, town, strength);
        System.out.println("     " + reaction.line());
        ok(!reaction.yes(), "a town founded is not a threat to a throne, so the king does nothing");
        ok(reaction.why().length() > 30, "and the reason is a sentence, not a shrug: " + reaction.why());

        // ------------------------------------------------ 8. THE WHOLE CHAIN ON ONE THING A PLAYER DID
        // A player intervenes in the war: the act, the fight it counts as, the line it writes, the war it
        // moves and the ruler who answers it.
        Chronicler.Line intervention = ledger.intervention("main", "Asha", year,
                "the battle at Rossbach", place, 6);
        ok(intervention != null, "an intervention with force is history");
        eq(ledger.deedsOf("Asha").fights(), 1, "and counts as one fight");
        WhatIf.Result warMove = WhatIf.apply(new ChangeRecord.Act(year, ChangeRecord.What.EVENT,
                ChangeRecord.How.BIGGER, "the battle at Rossbach", place, 6, Provenance.AUTHORED, "Asha"),
                world);
        WhatIf.Effect w = warMove.first(WhatIf.Field.WAR);
        ok(w != null, "and moves the war the player was in");
        Rulers.Choice answered = Rulers.reactTo(king, town, 0.9);
        ok(!answered.yes(), "and the king still does not answer a town");
        Rulers.Choice toPerson = Rulers.reactTo(king, new ChangeRecord.Act(year, ChangeRecord.What.PERSON,
                ChangeRecord.How.REMOVE, "a duke", place, 1, Provenance.AUTHORED, "Asha"), 0.9);
        ok(toPerson.yes(), "while he answers a duke: " + toPerson.why());

        // ------------------------------------------------ 9. NOTHING IN THE CHAIN INVENTED A NUMBER
        // The two refusals survive the whole chain, which is the property that matters most: no matter how
        // many parts a change is passed through, it never produces a population figure or a price.
        for (WhatIf.Field f : WhatIf.Field.values()) {
            if (!f.refused()) continue;
            WhatIf.Effect e = aftermath.first(f);
            ok(e != null, f + " is in the answer as a refusal");
            eq(e.after(), "not computed", f + " is never computed, whatever the change was");
        }
        ok(!aftermath.summary().toLowerCase().contains("people: "), "and no summary prints a headcount");
        ok(!aftermath.summary().toLowerCase().contains("costs a"), "and none prints a price");

        // ------------------------------------------------ 10. AND THE LINE A PLAYER ENDS UP WITH
        String line1 = ledger.lineFor("Asha", year, place, people);
        System.out.println("     " + line1);
        ok(line1.contains("merchant"), "the player is what their deeds made them: " + line1);
        ok(line1.contains(place), "and knows where they are");
        System.out.println("     chronicle: " + ledger.lines("main").size() + " lines");
        for (Chronicler.Line l : ledger.lines("main")) System.out.println("       " + l.title());

        System.out.println(failed == 0
                ? "Step49ChainProbe: " + checks + " checks, 0 failed"
                : "Step49ChainProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
