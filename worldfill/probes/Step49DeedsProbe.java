/* Step 49 part 2: the plumbing step 48 promised.
   The claim: five registers already count the five things a role is made of, one class joins them, and the
   chronicler built in step 47e finally gets a caller. */
import com.eternalengine.timeline.Agency;
import com.eternalengine.timeline.Chronicler;
import com.eternalengine.timeline.ChangeRecord;
import com.eternalengine.timeline.DeedLedger;
import com.eternalengine.timeline.PlayerRoles;
import com.eternalengine.timeline.Provenance;

import java.util.List;

public class Step49DeedsProbe {
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

        // ------------------------------------------------ 1. NOBODY HAS DONE ANYTHING
        eq(ledger.players(), 0, "an empty ledger knows nobody");
        eq(ledger.roleOf("Meera", 1300), PlayerRoles.Role.NONE, "and a stranger is nothing");
        ok(ledger.lines("main").isEmpty(), "and the chronicle is empty");

        // ------------------------------------------------ 2. SALES MAKE A MERCHANT, FROM THE LEDGER
        for (int k = 0; k < PlayerRoles.SALES_FOR_MERCHANT - 1; k++) ledger.sale("Meera", "Deccan", 1300);
        eq(ledger.roleOf("Meera", 1300), PlayerRoles.Role.NONE, "nine sales is not a merchant");
        ledger.sale("Meera", "Deccan", 1300);
        eq(ledger.roleOf("Meera", 1300), PlayerRoles.Role.MERCHANT, "ten is, and the ledger is the reason");
        eq(ledger.deedsOf("Meera").sales(), 10, "and the count is exact");
        eq(ledger.roleOf("meera", 1300), PlayerRoles.Role.MERCHANT,
                "a player is the same player whatever case their name arrives in");

        // The purse that comes with it is part 4's rule and it arrives here for free.
        Agency.Situation s = ledger.situationOf("Meera", 1300, "Deccan", 5000);
        ok(s.purse() > 0, "and the situation carries the merchant's purse: " + s.purse());
        ok(ledger.waysOf("Meera", 1300, "Deccan", 5000)
                .contains(ChangeRecord.Way.TRADE_OR_SABOTAGE_GOODS),
                "so the way that needs a purse is open: " + ledger.waysOf("Meera", 1300, "Deccan", 5000));

        // ------------------------------------------------ 3. FIGHTS, COURT DAYS, CARDS, AN OFFICE
        for (int k = 0; k < PlayerRoles.FIGHTS_FOR_SOLDIER; k++) ledger.fight("Arjun", "Konkan", 1400);
        eq(ledger.roleOf("Arjun", 1400), PlayerRoles.Role.SOLDIER, "three fights is a soldier");
        for (int k = 0; k < PlayerRoles.COURT_FOR_COURTIER; k++) ledger.courtDay("Tara", "Vijayanagara", 1450);
        eq(ledger.roleOf("Tara", 1450), PlayerRoles.Role.COURTIER, "twenty court days is a courtier");
        for (int k = 0; k < PlayerRoles.CARDS_FOR_SCHOLAR; k++) ledger.learned("Kabir", "Bidar", 1500);
        eq(ledger.roleOf("Kabir", 1500), PlayerRoles.Role.SCHOLAR, "ten cards is a scholar");
        ok(ledger.waysOf("Kabir", 1500, "Bidar", 20000)
                .contains(ChangeRecord.Way.BRING_AN_INVENTION_EARLY),
                "and a scholar's study opens the invention: " + ledger.waysOf("Kabir", 1500, "Bidar", 20000));

        // ------------------------------------------------ 4. TAKING AN OFFICE IS A CHRONICLE LINE
        ok(ledger.lines("main").isEmpty(), "no office yet, no line");
        Chronicler.Line office = ledger.office("Ravi", "Bijapur", 1550, true, "main");
        ok(office != null, "taking an office is a line in the chronicle");
        eq(office.provenance(), Provenance.AUTHORED, "and it is marked as something a person did");
        ok(office.title().contains("Bijapur"), "and it says where: " + office.title());
        eq(ledger.roleOf("Ravi", 1550), PlayerRoles.Role.RULER, "and the player is a ruler");
        eq(ledger.lines("main").size(), 1, "exactly one line for it, not one per tick");
        // Giving it up is not a line. Losing an office is not an event, it is an absence.
        ok(ledger.office("Ravi", "Bijapur", 1560, false, "main") == null, "and giving it up is not a line");
        eq(ledger.roleOf("Ravi", 1560), PlayerRoles.Role.NONE, "though the role goes with it");

        // ------------------------------------------------ 5. AN INTERVENTION IS HISTORY, AND IS COUNTED
        int linesBefore = ledger.lines("main").size();
        Chronicler.Line won = ledger.intervention("main", "Arjun", 1402, "the siege of the fort", "Konkan", 6);
        ok(won != null, "stopping a battle with force 6 is history");
        eq(ledger.lines("main").size(), linesBefore + 1, "and it is one line");
        eq(won.provenance(), Provenance.AUTHORED, "marked as the player's, not the record's");
        eq(ledger.deedsOf("Arjun").fights(), 4,
                "and the fight is counted as a fight, because intervening is being in it");
        // Force 0 is not enough for the recorder's threshold, and nothing is written.
        Chronicler.Line nothing = ledger.intervention("main", "Arjun", 1403, "a scuffle", "Konkan", 0);
        eq(nothing, null, "a scuffle with no force behind it is not a line, which is the recorder judging");
        ok(won.title().contains("War") || won.title().toLowerCase().contains("war"),
                "and the line reads as a war: " + won.title());

        // ------------------------------------------------ 6. A BRANCH HAS ITS OWN CHRONICLE
        ledger.office("Meera", "Deccan", 1410, true, "branch-north");
        eq(ledger.lines("branch-north").size(), 1, "a second branch has its own chronicle");
        ok(ledger.lines("main").size() > 1, "and the first is untouched: " + ledger.lines("main").size());
        ok(ledger.chroniclerFor(null) == ledger.chroniclerFor("main"),
                "no branch named means the main one, and it is the same object");

        // ------------------------------------------------ 7. ROLES ARE BORROWED FROM A LEDGER, NOT A CLOCK
        // A merchant who traded in 1300 and a merchant who stopped, and the difference is one year.
        for (int k = 0; k < PlayerRoles.SALES_FOR_MERCHANT; k++) ledger.sale("Lakshmi", "Deccan", 1300);
        eq(ledger.roleOf("Lakshmi", 1300), PlayerRoles.Role.MERCHANT, "the ledger says what she was");
        eq(ledger.roleOf("Lakshmi", 1300 + PlayerRoles.LAPSE_YEARS), PlayerRoles.Role.MERCHANT,
                "and she is still one at the edge of the window");
        eq(ledger.roleOf("Lakshmi", 1300 + PlayerRoles.LAPSE_YEARS + 1), PlayerRoles.Role.NONE,
                "and nothing one year past it");
        eq(ledger.deedsOf("Lakshmi").sales(), PlayerRoles.SALES_FOR_MERCHANT,
                "while the count stays, so a return is one more sale");

        // The bug this part found: an office taken in 1410 does not make anybody a ruler in 1400.
        eq(ledger.roleOf("Meera", 1400), PlayerRoles.Role.NONE,
                "and an office taken in 1410 does not reach back into 1400");

        // ------------------------------------------------ 8. WHAT A PLAYER READS
        String line = ledger.lineFor("Arjun", 1402, "Konkan", 500);
        System.out.println("  " + line);
        ok(line.contains("soldier"), "the line names what they are: " + line);
        ok(line.contains("Konkan"), "and where they are");
        // Everybody who is something, in one call. This is what a scoreboard would show.
        List<String> who = ledger.whoIsWhat(1402);
        System.out.println("  who is what in 1402: " + who);
        ok(who.size() >= 3, "the ledger can say who is what: " + who);
        // A player who lapsed is not on the list, because they are not anything any more.
        boolean lakshmiListed = false;
        for (String w : who) if (w.startsWith("lakshmi")) lakshmiListed = true;
        ok(!lakshmiListed, "and a lapsed player is not on it: " + who);

        // ------------------------------------------------ 9. IT CAN BE CLEARED, WHICH A RELOAD NEEDS
        ledger.clear();
        eq(ledger.players(), 0, "clearing forgets every player");
        ok(ledger.lines("main").isEmpty(), "and every line");
        eq(ledger.roleOf("Arjun", 1402), PlayerRoles.Role.NONE, "including the roles that came from it");

        System.out.println(failed == 0
                ? "Step49DeedsProbe: " + checks + " checks, 0 failed"
                : "Step49DeedsProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
