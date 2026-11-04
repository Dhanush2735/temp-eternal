/* Step 49 part 5 (D12): rulers decide.
   The claim: a ruler's decision can be explained rather than rolled - three numbers, three decisions, and
   every one of them carrying the sentence a player can argue with. */
import com.eternalengine.timeline.ChangeRecord;
import com.eternalengine.timeline.Provenance;
import com.eternalengine.timeline.Rulers;

import java.util.List;

public class Step49RulersProbe {
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
        // ------------------------------------------------ 1. THREE DECISIONS AND THREE NUMBERS
        eq(Rulers.Decision.values().length, 3, "a ruler is asked for three kinds of decision");
        Rulers.Ruler unknown = Rulers.Ruler.unknown();
        ok(unknown.name().contains("nobody named"),
                "and an unknown ruler is named as unknown rather than given a name: " + unknown.name());
        eq(Rulers.Ruler.unknown().treasure(), 0L, "with no treasure");
        // The numbers are clamped, because a caller with a bug should not produce a ruler at 400%.
        Rulers.Ruler overdrawn = new Rulers.Ruler("a king", 4.0, -50, 9.0);
        eq(overdrawn.security(), 1.0, "security is clamped to certainty");
        eq(overdrawn.treasure(), 0L, "and a negative treasury is an empty one");
        eq(overdrawn.armyStrength(), 1.0, "and strength to its ceiling");

        // ------------------------------------------------ 2. THE THRONE COMES FIRST, EVERY TIME
        Rulers.Ruler worried = new Rulers.Ruler("a worried king", 0.10, 500, 0.9);
        Rulers.Choice worriedTax = Rulers.decide(worried, Rulers.Question.tax(1750, "Berlin", 0.15, 0.25));
        ok(!worriedTax.yes(), "a worried ruler does not raise a tax, however rich");
        ok(worriedTax.why().contains("rising"), "and the reason is the rising: " + worriedTax.why());
        Rulers.Choice worriedWar = Rulers.decide(worried, Rulers.Question.war(1750, "Berlin", "Austria", 0.9));
        ok(!worriedWar.yes(), "and does not go to war even with a 90% chance of winning");
        ok(worriedWar.why().contains("leaves the country"),
                "because a worried ruler who leaves comes back to a different country: " + worriedWar.why());
        Rulers.Choice worriedHeir = Rulers.decide(worried, Rulers.Question.heir(1750, "Berlin"));
        ok(worriedHeir.yes(), "but does name an heir, which is the one steadying thing they can do");
        ok(worriedHeir.why().contains("alternative"), "and the reason says why: " + worriedHeir.why());

        // ------------------------------------------------ 3. A TAX HAS A CEILING AND A REASON
        Rulers.Ruler secure = new Rulers.Ruler("a secure king", 0.85, 50, 0.5);
        Rulers.Choice raising = Rulers.decide(secure, Rulers.Question.tax(1750, "Berlin", 0.15, 0.25));
        ok(raising.yes(), "a secure ruler with a thin treasury raises the tax: " + raising.line());
        Rulers.Choice tooMuch = Rulers.decide(secure, Rulers.Question.tax(1750, "Berlin", 0.15, 0.49));
        ok(!tooMuch.yes(), "but not above the ceiling");
        ok(tooMuch.why().contains("costs"), "and the reason is that it collects less than it costs: "
                + tooMuch.why());
        Rulers.Ruler rich = new Rulers.Ruler("a rich king", 0.85, 900, 0.5);
        Rulers.Choice richTax = Rulers.decide(rich, Rulers.Question.tax(1750, "Berlin", 0.15, 0.25));
        ok(!richTax.yes(), "and a rich ruler does not raise one at all");
        ok(richTax.why().contains("enough"), "because the treasury is enough: " + richTax.why());
        eq(Rulers.TAX_CEILING, 0.35, "the ceiling is one number in one place");

        // ------------------------------------------------ 4. A WAR NEEDS TREASURE AND A CHANCE
        Rulers.Choice poorWar = Rulers.decide(new Rulers.Ruler("a poor king", 0.9, 20, 0.9),
                Rulers.Question.war(1750, "Berlin", "Austria", 0.9));
        ok(!poorWar.yes(), "an army that is not paid is somewhere else, whatever the odds");
        ok(poorWar.why().contains("not paid"), "and the sentence says exactly that: " + poorWar.why());
        Rulers.Choice goodWar = Rulers.decide(new Rulers.Ruler("a king", 0.9, 400, 0.5),
                Rulers.Question.war(1757, "Berlin", "Austria", 0.6));
        ok(goodWar.yes(), "a secure ruler with money takes a war they expect to win: " + goodWar.line());
        Rulers.Choice coinToss = Rulers.decide(new Rulers.Ruler("a king", 0.9, 400, 0.5),
                Rulers.Question.war(1757, "Berlin", "Austria", 0.5));
        ok(!coinToss.yes(), "and refuses a coin toss");
        ok(coinToss.why().contains("other people's lives"),
                "with the reason a player will remember: " + coinToss.why());
        Rulers.Choice strongArmy = Rulers.decide(new Rulers.Ruler("a soldier king", 0.9, 400, 0.9),
                Rulers.Question.war(1757, "Berlin", "Austria", 0.47));
        ok(strongArmy.yes(), "a strong army makes its own odds as the war goes on: " + strongArmy.line());
        ok(strongArmy.confidence() < goodWar.confidence(),
                "and the engine is less sure of that answer than of the first: "
                        + strongArmy.confidence() + " against " + goodWar.confidence());

        // ------------------------------------------------ 5. NAMING AN HEIR IS A BALANCE
        Rulers.Choice settle = Rulers.decide(new Rulers.Ruler("a king", 0.6, 100, 0.5),
                Rulers.Question.heir(1750, "Berlin"));
        ok(settle.yes(), "a middling ruler settles the succession while it is still their choice");
        Rulers.Choice notYet = Rulers.decide(new Rulers.Ruler("a secure king", 0.95, 100, 0.5),
                Rulers.Question.heir(1750, "Berlin"));
        ok(!notYet.yes(), "a very secure one does not, and the reason is the opposite one");
        ok(notYet.why().contains("focus"), "because naming one early makes a focus: " + notYet.why());

        // ------------------------------------------------ 6. THE SAME RULER ALWAYS DECIDES THE SAME WAY
        // This is the property the old engine does not have, and it is checked by repetition rather than
        // by reading the code: a decision that cannot be repeated cannot be argued with.
        // A ruler who has the treasure to fight at all: the first run of this used a ruler with 50 in hand
        // and got 200 refusals, which was the money rule working and the test asking about the wrong king.
        Rulers.Ruler tested = new Rulers.Ruler("a king", 0.85, 400, 0.5);
        int agree = 0;
        for (int i = 0; i < 200; i++) {
            if (Rulers.decide(tested, Rulers.Question.war(1757, "Berlin", "Austria", 0.60)).yes()) agree++;
        }
        eq(agree, 200, "two hundred identical questions give two hundred identical answers, with no roll");
        eq(Rulers.decide(tested, Rulers.Question.war(1757, "Berlin", "Austria", 0.60)).why(),
                Rulers.decide(tested, Rulers.Question.war(1757, "Berlin", "Austria", 0.60)).why(),
                "and the same sentence every time, so a player can point at it");
        // And the poor ruler agrees with itself too, in the other direction.
        int always = 0;
        for (int i = 0; i < 50; i++) {
            if (!Rulers.decide(secure, Rulers.Question.war(1757, "Berlin", "Austria", 0.60)).yes()) always++;
        }
        eq(always, 50, "and a ruler with a treasury of 50 says no fifty times running, because the money "
                + "rule comes before the odds: " +
                Rulers.decide(secure, Rulers.Question.war(1757, "Berlin", "Austria", 0.60)).why());

        // ------------------------------------------------ 7. AND A RULER REACTS TO WHAT A PLAYER DID
        ChangeRecord.Act kill = new ChangeRecord.Act(1757, ChangeRecord.What.PERSON,
                ChangeRecord.How.REMOVE, "a duke", "Saxony", 1, Provenance.AUTHORED, "a player");
        Rulers.Choice reacts = Rulers.reactTo(secure, kill, 0.9);
        ok(reacts.yes(), "a big change to a person is answered by a secure ruler");
        Rulers.Choice ignores = Rulers.reactTo(secure, kill, 0.1);
        ok(!ignores.yes(), "and a small one is not");
        ok(ignores.why().contains("most rulers do about most things"),
                "with the honest reason: " + ignores.why());
        Rulers.Choice cannot = Rulers.reactTo(worried, kill, 0.9);
        ok(!cannot.yes(), "and a ruler who cannot afford a fight does not pick one");
        eq(Rulers.reactTo(secure, null, 0.5).words(), "nothing happened",
                "and no act at all is no reaction");
        // A change to a thing and not a person is not a threat to a throne.
        ChangeRecord.Act road = new ChangeRecord.Act(1757, ChangeRecord.What.PLACE,
                ChangeRecord.How.ADD, "a town", "Saxony", 40, Provenance.AUTHORED, "a player");
        ok(!Rulers.reactTo(secure, road, 0.9).yes(),
                "a town founded is not a threat to a throne, however big the town");

        // ------------------------------------------------ 8. THE CARD A PLAYER READS
        List<String> card = Rulers.card(new Rulers.Ruler("Frederick", 0.7, 300, 0.8), 1757, "Berlin", 0.6,
                "Austria");
        eq(card.size(), 4, "the card is four lines: who, and the three decisions");
        for (String l : card) System.out.println("     " + l);
        ok(card.get(0).contains("security 70%"), "and the first line carries the numbers: " + card.get(0));
        ok(card.get(1).contains("tax"), "and each decision is on its own line");

        // ------------------------------------------------ 9. THE TWO DEFECTS IN THE OLD ENGINE, STATED
        List<String> defects = Rulers.defects();
        eq(defects.size(), 2, "two defects are recorded rather than quietly worked around");
        ok(defects.get(0).contains("heirs.get(0)"),
                "the first is the list order pretending to be a law: " + defects.get(0));
        ok(defects.get(1).contains("Math.random"),
                "and the second is the roll: " + defects.get(1));
        ok(defects.get(1).contains("reload"),
                "which the sentence explains in terms of a player's experience: " + defects.get(1));

        System.out.println("  " + Rulers.ruleLine());
        System.out.println("  " + Rulers.summary(secure, 1757, "Berlin"));
        System.out.println(failed == 0
                ? "Step49RulersProbe: " + checks + " checks, 0 failed"
                : "Step49RulersProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
