/* Step 49 part 4 (G3): the what-if engine.
   The claim: a change can be followed into five registers this world already keeps, and the two that cannot
   be computed are refused by name rather than quietly left out. */
import com.eternalengine.timeline.ChangeRecord;
import com.eternalengine.timeline.Provenance;
import com.eternalengine.timeline.WhatIf;

import java.util.List;

public class Step49WhatIfProbe {
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

    static ChangeRecord.Act act(ChangeRecord.What what, ChangeRecord.How how, int mag, String subject,
                                String place) {
        return new ChangeRecord.Act(1757, what, how, subject, place, mag, Provenance.AUTHORED, "a player");
    }

    /** The world this whole probe uses: a battle in 1757 whose probability the battle model already gave. */
    static WhatIf.World rossbach() {
        return WhatIf.World.quiet(1757, "Rossbach", 51.2, 11.6)
                .withWar("Prussia", "France", "Saxony", 0.45)
                .withInvention("the steam engine", 1712)
                .withFaith("Protestantism", 0.40);
    }

    public static void main(String[] args) {
        // ------------------------------------------------ 1. SEVEN FIELDS, FIVE COMPUTED, TWO REFUSED
        eq(WhatIf.Field.values().length, 7, "G3 names seven things a change can touch");
        int computed = 0, refused = 0;
        for (WhatIf.Field f : WhatIf.Field.values()) {
            if (f.refused()) refused++; else computed++;
        }
        eq(computed, 5, "five of them are computed");
        eq(refused, 2, "and two are refused: this corrects the survey, which said one");
        ok(WhatIf.Field.POPULATION.refused(), "the people are refused");
        ok(WhatIf.Field.MONEY.refused(), "and so is the money, which the survey had not counted");
        for (String row : WhatIf.fields()) System.out.println("     " + row);

        // ------------------------------------------------ 2. NOTHING CHANGED, NOTHING FOLLOWS
        WhatIf.Result none = WhatIf.apply(null, rossbach());
        ok(!none.changed(), "no change, no consequence");
        ok(none.effects().isEmpty(), "and not one effect");
        eq(none.refused().size(), 2, "though the two refusals are still reported");

        // ------------------------------------------------ 3. A WAR PROBABILITY, MOVED
        // The world comes in at 45%. A change of the biggest size adds half of the remaining room.
        ChangeRecord.Act win = act(ChangeRecord.What.EVENT, ChangeRecord.How.BIGGER, 10, "the battle",
                "Rossbach");
        WhatIf.Result r = WhatIf.apply(win, rossbach());
        WhatIf.Effect war = r.first(WhatIf.Field.WAR);
        ok(war != null, "the war is computed");
        ok(!war.absorbed(), "and it is not absorbed, because there is no trend to resist it");
        eq(war.before(), "45%", "the probability before is the one the battle model gave");
        eq(war.after(), "95%", "and after the change it is arithmetic on that number, not a new model");
        // The border moves with it, because 45% to 95% crosses the halfway mark.
        WhatIf.Effect border = r.first(WhatIf.Field.BORDER);
        ok(border != null, "and the border is computed");
        eq(border.after(), "Prussia", "the border moves to the side that now wins: " + border.why());
        ok(border.why().contains("loses"), "and the sentence says who loses what: " + border.why());

        // A change the other way pushes the other way.
        ChangeRecord.Act lose = act(ChangeRecord.What.EVENT, ChangeRecord.How.SMALLER, 10, "the battle",
                "Rossbach");
        WhatIf.Effect down = WhatIf.apply(lose, rossbach()).first(WhatIf.Field.WAR);
        ok(down != null && down.after().equals("0%"), "a change against the war pushes it down: "
                + (down == null ? "null" : down.after()));

        // ------------------------------------------------ 4. A BORDER HOLDS UNLESS THE MARK IS CROSSED
        WhatIf.World safe = WhatIf.World.quiet(1757, "Rossbach", 51.2, 11.6)
                .withWar("Prussia", "France", "Saxony", 0.20);
        WhatIf.Result small = WhatIf.apply(act(ChangeRecord.What.EVENT, ChangeRecord.How.BIGGER, 1,
                "a skirmish", "Rossbach"), safe);
        WhatIf.Effect held = small.first(WhatIf.Field.BORDER);
        ok(held != null, "a small change still computes the border");
        eq(held.before(), "France", "France held it before");
        eq(held.after(), "France", "and holds it after, because 20% plus a little is not a crossing");
        ok(held.why().contains("does not move"), "and the sentence says it holds: " + held.why());

        // ------------------------------------------------ 5. THE TREND SWALLOWS WHAT IS SMALLER THAN IT
        WhatIf.World trend = rossbach().withTrend(0.6);
        WhatIf.Result swallowed = WhatIf.apply(act(ChangeRecord.What.EVENT, ChangeRecord.How.BIGGER, 2,
                "a gesture", "Rossbach"), trend);
        WhatIf.Effect absorbedWar = swallowed.first(WhatIf.Field.WAR);
        ok(absorbedWar != null && absorbedWar.absorbed(),
                "a change smaller than the trend is absorbed rather than reported");
        ok(absorbedWar.why().contains("swallowed"), "and says so in plain words: " + absorbedWar.why());
        ok(!swallowed.changed(), "so the world does not change");
        // And a change bigger than the trend is not absorbed. The trend here is smaller than the push, so
        // it cannot swallow it: the first run of this probe used a trend of 0.6 against a push of 0.5 and
        // asserted the opposite, which was the test being wrong rather than the engine.
        WhatIf.Result strong = WhatIf.apply(win, rossbach().withTrend(0.3));
        WhatIf.Effect strongWar = strong.first(WhatIf.Field.WAR);
        ok(strongWar != null && !strongWar.absorbed(), "while a big change gets through a big trend");
        ok(strongWar.confidence() < 0.8, "and is less sure of itself than against no trend: "
                + strongWar.confidence());
        ok(strongWar.confidence() <= WhatIf.MOST_SURE,
                "and never more sure than " + WhatIf.MOST_SURE + ", because nothing un-happened is "
                        + "certain: " + strongWar.confidence());
        ok(!strongWar.line().contains("100% sure"),
                "so no line ever claims certainty: " + strongWar.line());

        // ------------------------------------------------ 6. CONFIDENCE FALLS WITH THE TREND
        double sure = WhatIf.confidence(0.0, 0.5, 0, 0);
        double doubtful = WhatIf.confidence(0.6, 0.5, 0, 0);
        ok(sure > doubtful, "the same change against a big trend is less sure: " + sure + " against "
                + doubtful);
        ok(sure <= 1.0 && doubtful >= 0.0, "and both stay between nothing and certainty");
        ok(WhatIf.confidence(0.0, 0.0, 0, 0) < sure, "a tiny change is less sure than a big one");
        eq(WhatIf.confidence(0.0, 1.0, 0, 0), WhatIf.MOST_SURE, "and the ceiling holds at the top end");
        ok(!Double.isNaN(sure) && !Double.isInfinite(sure), "and the number is a number");

        // ------------------------------------------------ 7. FOUR SUCCESSION LAWS, FOUR ANSWERS
        List<WhatIf.Heir> heirs = List.of(
                new WhatIf.Heir("the younger son", 0.30, 40, 1740),
                new WhatIf.Heir("the elder daughter", 0.55, 70, 1735),
                new WhatIf.Heir("the cousin", 0.70, 30, 1720),
                new WhatIf.Heir("", 0.99, 99, 1700));      // no name: nobody at all
        eq(WhatIf.successor(heirs, WhatIf.SuccessionLaw.PRIMOGENITURE).name(), "the cousin",
                "primogeniture takes the eldest, which is 1720 and not the first row");
        eq(WhatIf.successor(heirs, WhatIf.SuccessionLaw.SENIORITY).name(), "the cousin",
                "seniority takes the same elder here");
        eq(WhatIf.successor(heirs, WhatIf.SuccessionLaw.ELECTIVE_SENATE).name(), "the cousin",
                "the senate elects the strongest claim, 0.70");
        // The coup weighs legitimacy heavily, so it can disagree with the senate: here the elder daughter
        // has the weaker claim and the far stronger legitimacy, and force plus legitimacy is what a coup is.
        eq(WhatIf.successor(heirs, WhatIf.SuccessionLaw.USURPATION_COUP).name(), "the elder daughter",
                "and a coup weighs legitimacy with force, so it need not agree with the senate");
        ok(!WhatIf.successor(heirs, WhatIf.SuccessionLaw.USURPATION_COUP).name()
                .equals(WhatIf.successor(heirs, WhatIf.SuccessionLaw.ELECTIVE_SENATE).name()),
                "which is the point of having four laws: they give different answers");
        // A tie in claim is broken by legitimacy, and the empty name never wins.
        List<WhatIf.Heir> tie = List.of(new WhatIf.Heir("a", 0.5, 10, 1700),
                new WhatIf.Heir("b", 0.5, 90, 1760));
        eq(WhatIf.successor(tie, WhatIf.SuccessionLaw.ELECTIVE_SENATE).name(), "b",
                "a tie in claim goes to legitimacy");
        eq(WhatIf.successor(tie, WhatIf.SuccessionLaw.PRIMOGENITURE).name(), "a",
                "and primogeniture ignores both and takes the elder");
        eq(WhatIf.successor(List.of(), WhatIf.SuccessionLaw.PRIMOGENITURE), null,
                "no heirs is no successor, and the engine says nobody rather than inventing a name");
        eq(WhatIf.successor(List.of(new WhatIf.Heir("", 1.0, 99, 1700)),
                WhatIf.SuccessionLaw.ELECTIVE_SENATE), null, "and a nameless heir is nobody");

        // A ruler removed is a succession, and the law decides it.
        WhatIf.World court = WhatIf.World.quiet(1757, "Berlin", 52.5, 13.4)
                .withSuccession("the king", heirs, WhatIf.SuccessionLaw.PRIMOGENITURE);
        WhatIf.Result dead = WhatIf.apply(act(ChangeRecord.What.PERSON, ChangeRecord.How.REMOVE, 1,
                "the king", "Berlin"), court);
        WhatIf.Effect heir = dead.first(WhatIf.Field.HEIR);
        ok(heir != null, "killing a ruler is a succession");
        eq(heir.before(), "the king", "and the line says who before");
        eq(heir.after(), "the cousin", "and who after, by the law the caller gave");
        ok(heir.why().contains("eldest"), "with the rule named: " + heir.why());

        // A court with no heirs has an open succession, which is the dangerous answer.
        WhatIf.World noHeirs = WhatIf.World.quiet(1757, "Berlin", 52.5, 13.4)
                .withSuccession("the king", List.of(), WhatIf.SuccessionLaw.PRIMOGENITURE);
        WhatIf.Effect open = WhatIf.apply(act(ChangeRecord.What.PERSON, ChangeRecord.How.REMOVE, 1,
                "the king", "Berlin"), noHeirs).first(WhatIf.Field.HEIR);
        ok(open != null && open.after().contains("nobody"), "no heir means the succession is open: "
                + (open == null ? "null" : open.after()));
        ok(open.why().contains("most dangerous"), "and the engine says why that matters: " + open.why());

        // ------------------------------------------------ 8. AN INVENTION MOVES IN TIME, AND SPREADS
        WhatIf.Result early = WhatIf.apply(act(ChangeRecord.What.KNOWLEDGE, ChangeRecord.How.EARLIER, 10,
                "the steam engine", "Rossbach"), rossbach());
        WhatIf.Effect tech = early.first(WhatIf.Field.TECHNOLOGY);
        ok(tech != null, "the invention is computed");
        eq(tech.before(), "arrives 1712", "the atlas dates it 1712");
        eq(tech.after(), "arrives 1692", "and a change of the biggest size moves it twenty years, not a "
                + "century");
        ok(tech.why().contains("years later"), "and the spread is stated in years: " + tech.why());
        ok(WhatIf.yearsToSpread(20) == 10, "a twenty-year shift reaches other places in about ten");

        // ------------------------------------------------ 9. AND A FAITH SHARE IS A FRACTION OF PEOPLE
        WhatIf.Effect faith = WhatIf.apply(act(ChangeRecord.What.PERSON, ChangeRecord.How.BIGGER, 10,
                "a preacher", "Rossbach"), rossbach()).first(WhatIf.Field.FAITH);
        ok(faith != null, "the faith is computed");
        eq(faith.before(), "40%", "from the share the caller gave");
        ok(!faith.after().equals("40%"), "to a different share: " + faith.after());
        ok(faith.confidence() > 0 && faith.confidence() <= 1, "with a confidence between nothing and "
                + "certainty");

        // ------------------------------------------------ 10. THE TWO REFUSALS, IN EVERY ANSWER
        WhatIf.Result any = WhatIf.apply(win, rossbach());
        WhatIf.Effect people = any.first(WhatIf.Field.POPULATION);
        WhatIf.Effect money = any.first(WhatIf.Field.MONEY);
        ok(people != null && people.after().equals("not computed"), "the population is present and refused");
        ok(people.why().contains("never to how many"), "with the reason: " + people.why());
        ok(money != null && money.after().equals("not computed"), "and so is the money");
        ok(people.line().contains("refused. "), "a refusal reads as a refusal and not as a change: "
                + people.line());
        ok(money.why().contains("price"), "for the price's own reason: " + money.why());
        eq(any.refused().size(), 2, "and the result names exactly two refusals");
        ok(any.summary().contains("Two things are refused"), "the summary says it every time: "
                + any.summary());

        // ------------------------------------------------ 11. NOTHING IS INVENTED WHEN THERE IS NOTHING THERE
        WhatIf.Result quiet = WhatIf.apply(win, WhatIf.World.quiet(1757, "a valley", 10, 10));
        ok(!quiet.changed(), "in a valley with no war, no ruler, no invention and no faith, nothing follows");
        eq(quiet.effects().size(), 2, "and the only effects are the two refusals");
        ok(quiet.summary().contains("Nothing follows"), "said plainly: " + quiet.summary());

        System.out.println("  " + WhatIf.ruleLine());
        System.out.println("  " + any.summary());
        for (WhatIf.Effect e : any.effects()) System.out.println("     " + e.line());
        System.out.println(failed == 0
                ? "Step49WhatIfProbe: " + checks + " checks, 0 failed"
                : "Step49WhatIfProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
