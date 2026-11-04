/* Step 55 part 2 (H4): broken logic within a universe. The claim: a rule set of seven kinds, and every
   kind names what it BENDS. Three kinds can be proved from dated entries and four can only be declared;
   a scan that finds none proves nothing about the four. */
import com.eternalengine.timeline.BrokenLogic;
import com.eternalengine.timeline.BrokenLogic.Entry;
import com.eternalengine.timeline.BrokenLogic.Kind;
import com.eternalengine.timeline.BrokenLogic.Spec;

import java.util.EnumSet;
import java.util.List;

public class Step55LogicProbe {
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

    static void refused(BrokenLogic.Made m, String words, String what) {
        checks++;
        if (m.ok()) {
            failed++;
            System.out.println("  FAIL " + what + "  (a rule set was made)");
            return;
        }
        for (String why : m.refused()) {
            if (why.contains(words)) return;
        }
        failed++;
        System.out.println("  FAIL " + what + "  no refusal says \"" + words + "\"; got " + m.refused());
    }

    static boolean in(List<String> lines, String words) {
        for (String l : lines) {
            if (l.contains(words)) return true;
        }
        return false;
    }

    public static void main(String[] args) {
        // ------------------------------------------------ 1. THE UNBROKEN WORLD
        Spec earth = BrokenLogic.earth();
        eq(earth.kinds().size(), 0, "Earth's logic breaks nothing");
        ok(earth.describe().contains("unbroken"), "in words: " + earth.describe());
        eq(BrokenLogic.changesFromEarth(earth).size(), 0, "and nothing about it is broken");

        // ------------------------------------------------ 2. THE SEVEN KINDS, EACH NAMING WHAT IT BENDS
        eq(Kind.values().length, 7, "H4 names seven kinds");
        eq(BrokenLogic.Kind.TIME_BACKWARDS.bends(), "the reading order of the record",
                "time backwards bends the reading order");
        eq(BrokenLogic.Kind.MONEY_UPSIDE_DOWN.bends(), "the money service's values",
                "money upside down bends the values");
        eq(BrokenLogic.Kind.SCRAMBLED_LANGUAGES.bends(), "the words themselves",
                "scrambled languages bends the words");
        int provable = 0;
        for (Kind k : Kind.values()) {
            ok(k.line().contains("bends"), "every kind's line names what it bends: " + k.line());
            if (k.provable()) {
                provable++;
                ok(k.line().contains("provable from dated entries"), "and the provable say so: " + k.line());
            } else {
                ok(k.line().contains("proves nothing"), "and the declared-only say silence is not "
                        + "evidence: " + k.line());
            }
        }
        eq(provable, 3, "exactly three kinds are provable");
        ok(BrokenLogic.Kind.OUT_OF_ORDER.provable() && BrokenLogic.Kind.EFFECTS_BEFORE_CAUSES.provable()
                        && BrokenLogic.Kind.DOUBLES.provable(),
                "they are out of order, effects before causes, and doubles");
        ok(!BrokenLogic.Kind.ERAS_MIXED.provable() && !BrokenLogic.Kind.TIME_BACKWARDS.provable()
                        && !BrokenLogic.Kind.MONEY_UPSIDE_DOWN.provable()
                        && !BrokenLogic.Kind.SCRAMBLED_LANGUAGES.provable(),
                "and eras, backwards time, money and languages are declared only");

        // ------------------------------------------------ 3. A RULE SET, AND ONE THAT CANNOT MEAN ANYTHING
        BrokenLogic.Made made = BrokenLogic.make(
                List.of(BrokenLogic.Kind.TIME_BACKWARDS, BrokenLogic.Kind.DOUBLES), "the rupture of 2026");
        ok(made.ok(), "a rule set is made: " + (made.ok() ? "" : made.refused()));
        List<String> changes = BrokenLogic.changesFromEarth(made.spec());
        eq(changes.size(), 2, "two kinds are broken");
        ok(changes.get(0).contains("bends the reading order"), "and each names what it bends: "
                + changes);
        ok(made.spec().describe().contains("bends the person register"), "the describe does too");
        refused(BrokenLogic.make(List.of(), "the rupture"), "breaks nothing",
                "a rule set that breaks nothing is refused");
        refused(BrokenLogic.make(List.of(BrokenLogic.Kind.DOUBLES, BrokenLogic.Kind.DOUBLES), "x"),
                "named twice", "one rule named twice is refused");
        refused(BrokenLogic.make(java.util.Collections.<BrokenLogic.Kind>singletonList(null), "x"),
                "not one of the seven", "a rule that is not a kind is refused");
        refused(BrokenLogic.make(List.of(BrokenLogic.Kind.DOUBLES), "  "), "without a why",
                "and a rule set without a why is refused");

        // changes between rule sets
        BrokenLogic.Made other = BrokenLogic.make(
                List.of(BrokenLogic.Kind.DOUBLES, BrokenLogic.Kind.ERAS_MIXED), "the rupture of 2027");
        List<String> moved = BrokenLogic.changes(made.spec(), other.spec());
        eq(moved.size(), 2, "one rule added and one put straight");
        ok(in(moved, "added eras mixed"), "in words: " + moved);
        ok(in(moved, "put time runs backwards straight"), "and: " + moved);

        // ------------------------------------------------ 4. THE CHECK: ASKED AGAINST REPORTED
        BrokenLogic.Reported same = new BrokenLogic.Reported(
                EnumSet.of(BrokenLogic.Kind.TIME_BACKWARDS, BrokenLogic.Kind.DOUBLES), "the universe");
        eq(BrokenLogic.diff(made.spec(), same).size(), 0, "a universe that is what was asked checks clean");
        BrokenLogic.Reported wrong = new BrokenLogic.Reported(
                EnumSet.of(BrokenLogic.Kind.TIME_BACKWARDS), "the universe");
        List<BrokenLogic.Difference> diffs = BrokenLogic.diff(made.spec(), wrong);
        eq(diffs.size(), 1, "one wrong rule is one disagreement");
        eq(diffs.get(0).what(), "doubles of famous people", "and named");
        ok(diffs.get(0).line().contains("asked for on, made off"), "in plain words: " + diffs.get(0).line());
        eq(BrokenLogic.diff(made.spec(), null).get(0).made(), "nothing was reported",
                "a universe that reports nothing is not a pass");
        eq(BrokenLogic.diff(null, same).get(0).what(), "(the rule set)", "and no rule set is refused");

        // ------------------------------------------------ 5. THE SCAN: PROVED, NOT PROVED, NOT PROVABLE
        List<Entry> clean = List.of(
                new Entry("a", 100, "the coronation", List.of()),
                new Entry("b", 200, "the war", List.of("a")));
        BrokenLogic.Scan s1 = BrokenLogic.scan(clean);
        eq(s1.proved().size(), 0, "a straight record proves nothing");
        eq(s1.foundNone(), List.of(BrokenLogic.Kind.OUT_OF_ORDER, BrokenLogic.Kind.EFFECTS_BEFORE_CAUSES,
                BrokenLogic.Kind.DOUBLES), "and says so for exactly the three provable kinds");
        eq(s1.notProvable().size(), 4, "while naming the four it can never prove");
        ok(s1.line().contains("declared only"), "in words: " + s1.line());

        List<Entry> bent = List.of(
                new Entry("a", 300, "the coronation", List.of()),
                new Entry("b", 100, "the war", List.of("a")),
                new Entry("b", 100, "the war", List.of("a")),
                new Entry("c", 150, "the peace", List.of()),
                new Entry("d", 150, "the peace", List.of("c")),
                new Entry("e", 160, "the flood", List.of("f")),
                new Entry("f", 170, "the drought", List.of("e")));
        BrokenLogic.Scan s2 = BrokenLogic.scan(bent);
        eq(s2.proved().size(), 3, "a bent record proves all three provable kinds");
        ok(s2.line().contains("the book's order and the years disagree"), "out of order is proved: "
                + s2.line());
        ok(s2.line().contains("appears twice: the record loops"), "and the loop is proved");
        ok(s2.line().contains("has not happened yet"), "effects before causes is proved");
        ok(s2.line().contains("cause each other: the cause graph loops"), "the cause loop too");
        ok(s2.line().contains("two entries named the peace"), "and the double is proved");
        eq(s2.notProvable().size(), 4, "but the declared four are still named as not provable");

        // The scan never speaks about the declared four, even when entries look odd.
        BrokenLogic.Scan s3 = BrokenLogic.scan(List.of(new Entry("a", -500, "$%#*", List.of())));
        eq(s3.proved().size(), 0, "a scrambled name dated in the deep past proves nothing");
        ok(s3.notProvable().contains(BrokenLogic.Kind.SCRAMBLED_LANGUAGES),
                "and languages stay in the not-provable list");
        eq(BrokenLogic.scan(null).line(), "no entries to scan", "and no entries is no scan");

        // ------------------------------------------------ 6. THE RULE
        System.out.println("     " + BrokenLogic.ruleLine());
        ok(BrokenLogic.ruleLine().contains("seven kinds"), "the rule line keeps the seven");
        ok(BrokenLogic.ruleLine().contains("four can only be declared"), "and the proved-or-declared rule");

        System.out.println("\nStep 55 part 2: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }

}
