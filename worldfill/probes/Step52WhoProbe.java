/* Step 51 part 2 (F10): the card a player starts with. The claim: who you are is decided once, checked once
   (a parent born after their child is refused, not repaired), and answers the one question the grandfather
   paradox will ask: was this person alive in that year, and are they mine? */
import com.eternalengine.player.WhoYouAre;

import java.util.ArrayList;
import java.util.List;

public class Step52WhoProbe {
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

    static void refused(WhoYouAre.Result r, String words, String what) {
        checks++;
        if (r.ok()) {
            failed++;
            System.out.println("  FAIL " + what + "  (a card was made)");
            return;
        }
        for (String why : r.refused()) {
            if (why.contains(words)) return;
        }
        failed++;
        System.out.println("  FAIL " + what + "  no refusal says \"" + words + "\"; got " + r.refused());
    }

    static WhoYouAre.Entry e(String n, String rel, int depth, int born, Integer died) {
        return new WhoYouAre.Entry(n, rel, depth, born, died);
    }

    public static void main(String[] args) {
        // ------------------------------------------------ 1. THREE PLAYERS, THREE ERAS, THREE PLACES
        WhoYouAre.Result urLocal = WhoYouAre.make("Ninlil", WhoYouAre.Kind.LOCAL, -2980, -2960, "Ur",
                List.of(e("Nanna", "mother", 1, -2995, -2940), e("Enheduana", "grandmother", 2, -3040, -2935)),
                List.of(new WhoYouAre.Item("barley", 3), new WhoYouAre.Item("wool", 1)));
        ok(urLocal.ok(), "a local of Ur, born 2980 BC: " + (urLocal.ok() ? "" : urLocal.refused()));
        WhoYouAre ninlil = urLocal.who();

        WhoYouAre.Result delhiLocal = WhoYouAre.make("Ashraf", WhoYouAre.Kind.LOCAL, 1830, 1857, "Delhi",
                List.of(e("Fatima", "mother", 1, 1805, 1870), e("Daulat", "grandfather", 2, 1778, 1840)),
                List.of(new WhoYouAre.Item("a spade", 1)));
        ok(delhiLocal.ok(), "a local of Delhi standing in 1857");
        WhoYouAre ashraf = delhiLocal.who();

        WhoYouAre.Result traveller = WhoYouAre.make("Mira", WhoYouAre.Kind.TRAVELLER, 2100, 1576, "Cuzco",
                List.of(), List.of(new WhoYouAre.Item("a notebook", 1), new WhoYouAre.Item("bread", 2)));
        ok(traveller.ok(), "a traveller born in 2100, beginning in 1576 Cuzco: "
                + (traveller.ok() ? "" : traveller.refused()));
        WhoYouAre mira = traveller.who();

        // ------------------------------------------------ 2. THE CARD, AS A PLAYER READS IT
        for (String line : ninlil.card()) System.out.println("     " + line);
        ok(ninlil.card().get(0).contains("begins in -2960 at Ur"), "the card names the year and the place");
        ok(ninlil.card().get(0).contains("a local"), "and which kind of person you are");
        eq(ninlil.line().size(), 2, "and the line it was given");
        ok(ninlil.card().toString().contains("barley"), "and the kit");
        ok(ninlil.lineOrigin().contains("the record holds this line"), "a local's line is the record's: "
                + ninlil.lineOrigin());
        ok(mira.lineOrigin().contains("carried with you"), "a traveller's line is carried: " + mira.lineOrigin());
        for (String line : mira.card()) System.out.println("     " + line);

        // ------------------------------------------------ 3. THE QUESTIONS STEP 53 WILL ASK
        ok(ninlil.aliveAt(-2970), "the player is alive in the year they stand in");
        ok(!ninlil.aliveAt(-3000), "and not before they were born");
        ok(mira.aliveAt(1576), "a traveller stands in any year they travel to");
        eq(ninlil.ancestorsAliveAt(-2970).size(), 2, "in 2970 BC both of Ninlil's line are alive");
        eq(ninlil.ancestorsAliveAt(-3000).size(), 1, "in 3000 BC only the grandmother is: "
                + ninlil.ancestorsAliveAt(-3000).get(0).name());
        eq(ninlil.ancestorsAliveAt(-2930).size(), 0, "and by 2930 BC both are dead");
        ok(ashraf.isAncestor("Daulat"), "Daulat is Ashraf's ancestor");
        ok(!ashraf.isAncestor("Ninlil"), "and Ninlil is not");
        eq(ashraf.depthOf("Fatima"), 1, "a parent is one step up");
        eq(ashraf.depthOf("Daulat"), 2, "a grandparent two");
        eq(ashraf.depthOf("nobody"), 0, "and a stranger is none");
        List<WhoYouAre.Entry> chain = ashraf.chainToYou("Daulat");
        eq(chain.size(), 2, "the chain from the grandfather down holds both people of the line");
        eq(chain.get(0).name(), "Daulat", "the ancestor first");
        eq(chain.get(1).name(), "Fatima", "and the nearer one last, next to you");
        eq(ashraf.chainToYou("Ninlil").size(), 0, "a chain from somebody else's line is empty");

        // ------------------------------------------------ 4. A LOCAL CANNOT BEGIN BEFORE THEY ARE BORN
        refused(WhoYouAre.make("Late", WhoYouAre.Kind.LOCAL, 1900, 1850, "Delhi", List.of(), List.of()),
                "before they were born", "a local cannot begin before they are born");
        ok(WhoYouAre.make("Early", WhoYouAre.Kind.TRAVELLER, 2100, 1850, "Delhi", List.of(), List.of()).ok(),
                "a traveller can: that is what travelling is");

        // ------------------------------------------------ 5. A LINE THAT CANNOT HAVE HAPPENED IS REFUSED
        refused(WhoYouAre.make("Backwards", WhoYouAre.Kind.LOCAL, 1900, 1900, "Delhi",
                List.of(e("Ramesh", "grandfather", 2, 1880, 1950), e("Sita", "mother", 1, 1860, 1930)), List.of()),
                "cannot be", "a grandfather born after his own child is refused");
        refused(WhoYouAre.make("DiesEarly", WhoYouAre.Kind.LOCAL, 1900, 1900, "Delhi",
                List.of(e("Gone", "mother", 1, 1860, 1850)), List.of()),
                "before they were born", "a death before a birth is refused");
        refused(WhoYouAre.make("Twins", WhoYouAre.Kind.LOCAL, 1900, 1900, "Delhi",
                List.of(e("Mary", "mother", 1, 1840, null), e("Aisha", "aunt", 1, 1810, null)),
                List.of()), "two people in the line share depth", "two relatives at one step of the line are refused");
        refused(WhoYouAre.make("SameName", WhoYouAre.Kind.LOCAL, 1900, 1900, "Delhi",
                List.of(e("Mary", "mother", 1, 1860, null), e("Mary", "grandmother", 2, 1830, null)),
                List.of()), "holds 2 people by the name", "two relatives with one name are a question, not a family");
        refused(WhoYouAre.make("TooLate", WhoYouAre.Kind.LOCAL, 1900, 1900, "Delhi",
                List.of(e("Young", "mother", 1, 1905, null)), List.of()),
                "not before you were born", "a parent born after you is refused");

        // ------------------------------------------------ 6. THE KIT
        refused(WhoYouAre.make("NoKitName", WhoYouAre.Kind.LOCAL, 1900, 1900, "Delhi", List.of(),
                List.of(new WhoYouAre.Item("  ", 1))),
                "no name", "a kit thing with no name is refused");
        refused(WhoYouAre.make("NoKitCount", WhoYouAre.Kind.LOCAL, 1900, 1900, "Delhi", List.of(),
                List.of(new WhoYouAre.Item("bread", 0))),
                "which is none", "a kit of none is refused");
        refused(WhoYouAre.make("TwoBreads", WhoYouAre.Kind.LOCAL, 1900, 1900, "Delhi", List.of(),
                List.of(new WhoYouAre.Item("bread", 1), new WhoYouAre.Item("Bread", 2))),
                "names Bread twice", "the same thing named twice in a kit is refused, not merged");
        eq(mira.kit().size(), 2, "and a traveller's kit is what it is");

        // ------------------------------------------------ 7. BLANKS, AND THE EMPTY LINE
        refused(WhoYouAre.make("  ", WhoYouAre.Kind.LOCAL, 1900, 1900, "Delhi", List.of(), List.of()),
                "no name is nobody's", "a blank name is refused");
        refused(WhoYouAre.make("Nowhere", WhoYouAre.Kind.LOCAL, 1900, 1900, "  ", List.of(), List.of()),
                "begins nowhere", "a blank start place is refused");
        refused(WhoYouAre.make("Unkind", null, 1900, 1900, "Delhi", List.of(), List.of()),
                "local or a traveller", "a card that does not say which kind of person you are is refused");
        eq(mira.line().size(), 0, "a traveller with no line has an empty line");
        ok(mira.card().toString().contains("nobody is recorded"), "and the card says so in words");
        ok(mira.card().toString().contains("carried with you"), "and says where a line would come from");

        // ------------------------------------------------ 8. NO EDITS AFTER THE CARD IS MADE
        List<WhoYouAre.Entry> mutable = new ArrayList<>();
        mutable.add(e("Fatima", "mother", 1, 1805, 1870));
        WhoYouAre.Result made = WhoYouAre.make("Kept", WhoYouAre.Kind.LOCAL, 1830, 1857, "Delhi", mutable,
                List.of());
        mutable.add(e("Late", "grandfather", 2, 1900, null));
        eq(made.who().line().size(), 1, "changing the list afterwards does not change the card: the line is "
                + "recorded once");
        eq(made.who().line().get(0).name(), "Fatima", "and what was checked is what stands");

        // ------------------------------------------------ 9. THE RULE LINE
        System.out.println("     " + WhoYouAre.ruleLine());
        ok(WhoYouAre.ruleLine().contains("never edited"), "the rule line says the card is made once");
        ok(WhoYouAre.ruleLine().contains("traveller carries theirs"), "and how a traveller's line differs");

        System.out.println("\nStep 52 part 2: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
