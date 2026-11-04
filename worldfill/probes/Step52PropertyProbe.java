/* Step 52 part 6 (F4): property per timeline. The claim: a deed belongs to ONE timeline; one place has one
   owner; what is yours you may sell, give up or reshape; what is another's needs an operator and the book
   records the confiscation; and the same coordinates on another branch are somebody else's, lawfully. */
import com.eternalengine.player.Permissions.Actor;
import com.eternalengine.player.Permissions.Decision;
import com.eternalengine.player.Property;
import com.eternalengine.player.Property.Claim;
import com.eternalengine.player.Property.Kind;

import java.util.List;

public class Step52PropertyProbe {
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

    static void refused(Property.Result r, String words, String what) {
        checks++;
        if (r.ok()) {
            failed++;
            System.out.println("  FAIL " + what + "  (a deed was made)");
            return;
        }
        if (r.refused().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no reason says \"" + words + "\"; got " + r.refused());
    }

    static void refused(Decision d, String words, String what) {
        checks++;
        if (d.allowed()) {
            failed++;
            System.out.println("  FAIL " + what + "  (it was allowed)");
            return;
        }
        if (d.why().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no reason says \"" + words + "\"; got " + d.why());
    }

    static void allowed(Decision d, String what) {
        checks++;
        if (!d.allowed()) {
            failed++;
            System.out.println("  FAIL " + what + "  (" + d.why() + ")");
        }
    }

    public static void main(String[] args) {
        Actor sam = Actor.of("Sam", false);
        Actor ada = Actor.of("Ada", true);
        Actor mira = Actor.of("Mira", false);

        // ------------------------------------------------ 1. ONE TIMELINE, ONE DEED PER PLACE
        Property main = new Property("delhi", "main");
        eq(main.where(), "delhi/main", "the book answers for exactly one timeline");
        Property.Result home = main.claim("home-1857", Kind.HOUSE, "Sam", 100, 64, 200, 104, 70, 204,
                1857, "raised in the year of the mutiny");
        ok(home.ok(), "Sam claims a house in 1857: " + (home.ok() ? "" : home.refused()));
        eq(home.claim().blocks(), 5 * 7 * 5, "the box counts its blocks");
        eq(main.at(102, 67, 202).id(), "home-1857", "and covers what it says");
        eq(main.at(105, 67, 202), null, "and nothing beyond its edges");
        eq(main.ownedBy("sam").size(), 1, "what Sam owns here, whatever the case of his name");
        eq(main.ownedBy("Sam").get(0).id(), "home-1857", "is this deed");

        // The same name, or the same blocks, twice: refused.
        refused(main.claim("home-1857", Kind.SHOP, "Mira", 0, 64, 0, 2, 64, 2, 1857, ""),
                "two deeds with one name", "one name, one deed");
        refused(main.claim("shed", Kind.HOUSE, "Mira", 102, 64, 202, 110, 70, 210, 1857, ""),
                "already Sam's", "and one place, one owner");
        refused(main.claim("shed", Kind.HOUSE, "Mira", -1000, 64, -1000, -500, 70, -500, 1857, ""),
                "nobody can check", "a claim the size of a province is refused");
        refused(main.claim("", Kind.HOUSE, "Mira", 0, 64, 0, 1, 64, 1, 1857, ""),
                "no deed", "a nameless deed is refused");
        refused(main.claim("x", Kind.HOUSE, "", 0, 64, 0, 1, 64, 1, 1857, ""),
                "whose it is", "a deed with no owner is refused");
        refused(main.claim("x", null, "Mira", 0, 64, 0, 1, 64, 1, 1857, ""),
                "house, land or a shop", "a deed that says what it is not is refused");

        // Corners typed the wrong way round are the same box.
        Property.Result reversed = main.claim("well", Kind.LAND, "Mira", 300, 63, 300, 290, 60, 290,
                1858, "");
        ok(reversed.ok(), "a box typed back to front is still a box");
        eq(reversed.claim().x1(), 290, "and is stored sorted");
        eq(reversed.claim().blocks(), 11 * 4 * 11, "with its true size");

        // ------------------------------------------------ 2. PER TIMELINE: THE SAME BLOCKS, ANOTHER BRANCH
        Property b1 = new Property("delhi", "b1");
        Property.Result onBranch = b1.claim("home-1857", Kind.HOUSE, "Mira", 100, 64, 200, 104, 70, 204,
                1861, "the branch's own house");
        ok(onBranch.ok(), "the same name AND the same blocks on another branch are a different deed");
        eq(b1.at(102, 67, 202).owner(), "Mira", "on b1 the house is Mira's");
        eq(main.at(102, 67, 202).owner(), "Sam", "and on the real history it is still Sam's");
        eq(b1.where(), "delhi/b1", "and each book says which timeline it answers for");
        eq(main.ownedBy("Mira").get(0).id(), "well", "on the real history Mira owns the well and not the "
                + "house");

        // ------------------------------------------------ 3. GIVING, SELLING, AND THE BOOK'S MEMORY
        refused(main.transfer(mira, "home-1857", "Mira", 1859, ""), "Sam's, and Mira is",
                "a stranger cannot sell another's house");
        refused(main.transfer(sam, "home-1857", "Sam", 1859, ""), "already owns",
                "and nobody sells to themselves");
        refused(main.transfer(sam, "home-1857", "  ", 1859, ""), "to nobody",
                "nor to nobody at all");
        allowed(main.transfer(sam, "home-1857", "Mira", 1859, "sold for 40 coins"),
                "the owner sells to whoever they like");
        eq(main.at(102, 67, 202).owner(), "Mira", "the house is Mira's now");
        eq(main.historyOf("home-1857").size(), 2, "and the book kept both rows");
        eq(main.historyOf("home-1857").get(0).from(), "nobody", "claimed from nobody");
        eq(main.historyOf("home-1857").get(1).why(), "sold for 40 coins", "and why it changed hands");
        for (Property.Hand h : main.historyOf("home-1857")) System.out.println("     " + h.line());
        allowed(main.release(mira, "home-1857", 1860, "left the city"), "the owner gives it up");
        eq(main.at(102, 67, 202), null, "and the blocks are nobody's again");
        eq(main.historyOf("home-1857").size(), 3, "with the release in the book");
        refused(main.release(sam, "well", 1860, ""), "Mira's", "a stranger cannot release another's deed");
        refused(main.release(sam, "no-such", 1860, ""), "no deed called no-such", "nor one that does not "
                + "exist");

        // ------------------------------------------------ 4. CONFISCATION IS AN OPERATOR'S ACT
        refused(main.take(sam, "well", 1860, "I want it"), "operators only",
                "a player cannot take another's deed");
        refused(main.take(sam, "well", 1860, "I want it"), "not Sam's to take",
                "and the refusal says whose it is");
        allowed(main.take(ada, "well", 1860, "the city needs the well"), "an operator can");
        eq(main.at(295, 61, 295).owner(), "Ada", "and the deed is the operator's now");
        eq(main.historyOf("well").get(1).why(), "the city needs the well", "with the reason in the book");

        // ------------------------------------------------ 5. RESHAPING WHAT IS YOURS
        refused(main.reshape(sam, "well", 0, 64, 0, 1, 64, 1, 1860), "Ada's",
                "a stranger cannot reshape another's deed");
        // The house is released (above), so a neighbour claims a yard where it stood.
        ok(main.claim("yard", Kind.LAND, "Mira", 200, 64, 200, 220, 66, 220, 1861, "").ok(),
                "Mira claims a yard where the old house stood");
        refused(main.reshape(ada, "well", 200, 64, 200, 204, 70, 204, 1861), "already Mira's",
                "and a reshape cannot swallow another's blocks");
        refused(main.reshape(ada, "well", 0, 64, 0, 2000, 64, 2000, 1860), "nobody can check",
                "nor grow past what a player can walk");
        allowed(main.reshape(ada, "well", 290, 60, 290, 300, 63, 300, 1860), "the owner reshapes their own");
        eq(main.find("well").blocks(), 11 * 4 * 11, "and the box is what it now says");
        eq(main.at(305, 61, 305), null, "and nothing outside it");

        // ------------------------------------------------ 6. EVERY PLACE HAS ITS BOOK
        Property cuzco = new Property("cuzco", "main");
        Property ur = new Property("ur", "main");
        ok(cuzco.claim("tambo-1576", Kind.SHOP, "Mira", 0, 64, 0, 9, 68, 9, 1576, "an inn").ok(),
                "a shop in Cuzco, 1576");
        ok(ur.claim("field-2960", Kind.LAND, "Ninlil", -50, 62, -50, -1, 62, -1, -2960, "barley").ok(),
                "a field in Ur, 2960 BC");
        eq(cuzco.ownedBy("Ninlil").size(), 0, "a field in Ur is not a shop in Cuzco");
        eq(cuzco.at(5, 66, 5).id(), "tambo-1576", "each book answers for its own place and time");
        eq(ur.at(-25, 62, -25).id(), "field-2960", "including the very old ones");

        // ------------------------------------------------ 7. THE PAGE AND THE RULE
        for (String line : main.lines()) System.out.println("     " + line);
        ok(main.lines().get(0).startsWith("delhi/main"), "the page names the timeline first: "
                + main.lines().get(0));
        System.out.println("     " + Property.ruleLine());
        ok(Property.ruleLine().contains("per timeline"), "the rule line says deeds are per timeline");
        checks++;
        try {
            new Property("delhi", " ");
            failed++;
            System.out.println("  FAIL a book with no timeline was opened");
        } catch (IllegalArgumentException e) {
            ok(e.getMessage().contains("per timeline"), "and a book with no timeline cannot exist");
            checks--;
        }

        System.out.println("\nStep 52 part 6: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
