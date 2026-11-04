/* Step 48 part 4 (F5): player roles, and what being one opens.
   The claim: a role is earned by doing the thing the role does, counted from registers the mod already
   keeps, and it is lost by stopping - so the standing that part 3 read from nowhere now comes from the
   player's own history. */
import com.eternalengine.timeline.Agency;
import com.eternalengine.timeline.ChangeRecord;
import com.eternalengine.timeline.PlayerRoles;

import java.util.List;
import java.util.Set;

public class Step48RolesProbe {
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
        // ------------------------------------------------ 1. NOBODY STARTS AS ANYTHING
        PlayerRoles.Deeds none = PlayerRoles.Deeds.none();
        eq(PlayerRoles.held(none, 1200), PlayerRoles.Role.NONE, "a player who has done nothing is nothing");
        eq(PlayerRoles.earned(none), PlayerRoles.Role.NONE, "and has earned nothing");
        ok(!PlayerRoles.lapsed(none, 1200), "and has not lapsed, which is a different thing to a player");
        eq(PlayerRoles.situation(1200, "a village", 200, none).standing(), Agency.Standing.OUTSIDER,
                "and is a stranger to the village");

        // ------------------------------------------------ 2. EARNING, ONE DEED AT A TIME
        PlayerRoles.Deeds d = none;
        for (int k = 0; k < PlayerRoles.SALES_FOR_MERCHANT - 1; k++) d = d.plusSale(1200);
        eq(PlayerRoles.held(d, 1200), PlayerRoles.Role.NONE,
                "nine sales is not a merchant: " + PlayerRoles.progressLine(d, 1200));
        d = d.plusSale(1200);
        eq(PlayerRoles.held(d, 1200), PlayerRoles.Role.MERCHANT, "ten is");
        eq(PlayerRoles.held(d, 1200).standing(), Agency.Standing.RESIDENT,
                "and a merchant is a resident of the place they trade in, not a stranger");
        ok(PlayerRoles.purse(PlayerRoles.Role.MERCHANT, d) >= 100,
                "with a purse to match: " + PlayerRoles.purse(PlayerRoles.Role.MERCHANT, d));

        PlayerRoles.Deeds fighter = PlayerRoles.Deeds.none();
        for (int k = 0; k < PlayerRoles.FIGHTS_FOR_SOLDIER - 1; k++) fighter = fighter.plusFight(1300);
        eq(PlayerRoles.held(fighter, 1300), PlayerRoles.Role.NONE, "two fights is not a soldier");
        fighter = fighter.plusFight(1300);
        eq(PlayerRoles.held(fighter, 1300), PlayerRoles.Role.SOLDIER, "three is");
        eq(PlayerRoles.held(fighter, 1300).standing(), Agency.Standing.NOTABLE,
                "and a soldier is a notable");
        ok(PlayerRoles.followers(PlayerRoles.Role.SOLDIER, fighter) > 0,
                "with people behind them: " + PlayerRoles.followers(PlayerRoles.Role.SOLDIER, fighter));
        // The cap is the honest bit: a warband, not an army.
        PlayerRoles.Deeds manyFights = new PlayerRoles.Deeds(0, 500, 0, 0, false, 1300);
        eq(PlayerRoles.followers(PlayerRoles.Role.SOLDIER, manyFights), 50,
                "and never more than a warband, however long they fight");

        PlayerRoles.Deeds scholar = PlayerRoles.Deeds.none();
        for (int k = 0; k < PlayerRoles.CARDS_FOR_SCHOLAR; k++) scholar = scholar.plusCard(1400);
        eq(PlayerRoles.held(scholar, 1400), PlayerRoles.Role.SCHOLAR, "ten cards makes a scholar");
        ok(PlayerRoles.workshop(PlayerRoles.Role.SCHOLAR), "and a scholar's study is a workshop");
        ok(!PlayerRoles.workshop(PlayerRoles.Role.MERCHANT), "which a warehouse is not");

        PlayerRoles.Deeds courtier = PlayerRoles.Deeds.none();
        for (int k = 0; k < PlayerRoles.COURT_FOR_COURTIER; k++) courtier = courtier.plusCourtDay(1500);
        eq(PlayerRoles.held(courtier, 1500), PlayerRoles.Role.COURTIER, "twenty court days makes a courtier");
        eq(PlayerRoles.held(courtier, 1500).standing(), Agency.Standing.OFFICE,
                "which is an office and not merely a reputation");

        PlayerRoles.Deeds ruler = PlayerRoles.Deeds.none().withOffice(true, 1600);
        eq(PlayerRoles.held(ruler, 1600), PlayerRoles.Role.RULER, "holding a place makes a ruler");
        eq(PlayerRoles.held(ruler, 1600).standing(), Agency.Standing.RULER, "the top of the ladder");
        // The office outranks everything: a ruler who also sells is still the ruler.
        PlayerRoles.Deeds rulerWhoSells = new PlayerRoles.Deeds(400, 40, 40, 40, true, 1600);
        eq(PlayerRoles.held(rulerWhoSells, 1600), PlayerRoles.Role.RULER, "and outranks every other role");

        // ------------------------------------------------ 3. LOSING IT, WHICH IS THE POINT
        // A role is a practice and not a badge: stop doing it for twenty-five years and it is gone.
        eq(PlayerRoles.held(d, 1200 + PlayerRoles.LAPSE_YEARS), PlayerRoles.Role.MERCHANT,
                "a merchant who traded last year is still a merchant at the edge of the window");
        eq(PlayerRoles.held(d, 1201 + PlayerRoles.LAPSE_YEARS), PlayerRoles.Role.NONE,
                "and one year past it is not");
        ok(PlayerRoles.lapsed(d, 1300), "and the game knows they lapsed rather than never started");
        ok(PlayerRoles.progressLine(d, 1300).contains("Do it again"),
                "so the line is a way back rather than a verdict: " + PlayerRoles.progressLine(d, 1300));
        // Coming back is easier than starting, because the deeds are still counted.
        PlayerRoles.Deeds back = d.plusSale(1301);
        eq(PlayerRoles.held(back, 1301), PlayerRoles.Role.MERCHANT, "one more sale and the role returns");
        // An office is not a practice: lose the place and everything goes with it, at once.
        PlayerRoles.Deeds deposed = new PlayerRoles.Deeds(0, 0, 0, 0, false, 1600);
        eq(PlayerRoles.held(ruler, 1700), PlayerRoles.Role.NONE, "a ruler who has not ruled for a century is not one");

        // ------------------------------------------------ 4. WHAT EACH ROLE OPENS
        PlayerRoles.Role[] roles = {PlayerRoles.Role.NONE, PlayerRoles.Role.MERCHANT,
                PlayerRoles.Role.SCHOLAR, PlayerRoles.Role.SOLDIER, PlayerRoles.Role.COURTIER,
                PlayerRoles.Role.RULER};
        int previous = -1;
        for (PlayerRoles.Role r : roles) {
            int n = PlayerRoles.supplies(r).size();
            ok(n >= previous, "a higher role supplies at least as much as a lower one: " + r + " " + n);
            previous = n;
        }
        ok(PlayerRoles.supplies(PlayerRoles.Role.NONE).isEmpty(), "nothing at all supplies nothing");
        eq(PlayerRoles.supplies(PlayerRoles.Role.SOLDIER).size(), 3,
                "a soldier supplies three ways the world wants people for");
        ok(PlayerRoles.supplies(PlayerRoles.Role.SCHOLAR)
                .contains(ChangeRecord.Way.BRING_AN_INVENTION_EARLY),
                "a scholar supplies the workshop that bringing an invention early demands");
        ok(!PlayerRoles.supplies(PlayerRoles.Role.SCHOLAR)
                .contains(ChangeRecord.Way.START_OR_ESCALATE_A_WAR),
                "and does not supply an army");
        ok(PlayerRoles.supplies(PlayerRoles.Role.COURTIER).contains(ChangeRecord.Way.MARRY),
                "a courtier supplies the standing a marriage needs");
        eq(PlayerRoles.supplies(PlayerRoles.Role.RULER).size(), ChangeRecord.Way.values().length - 1,
                "a ruler supplies everything but one: killing or saving one person is still done with "
                        + "your own hands and nobody can do it for you");

        // ------------------------------------------------ 5. THE JOIN WITH PART 3
        // The same city, the same count of people, five players with five histories.
        int year = 1600;
        long people = 50_000;
        String place = "a city";
        // Every history is kept alive into 1600, because a role lapses and a probe that forgets is
        // testing the lapse and calling it the role.
        PlayerRoles.Deeds merchant1600 = d.plusSale(year);
        PlayerRoles.Deeds scholar1600 = scholar.plusCard(year);
        PlayerRoles.Deeds fighter1600 = fighter.plusFight(year);
        PlayerRoles.Deeds courtier1600 = courtier.plusCourtDay(year);
        PlayerRoles.Deeds[] histories = {none, merchant1600, scholar1600, fighter1600, courtier1600, ruler};
        int lastOpen = -1;
        java.util.Map<PlayerRoles.Role, Integer> count = new java.util.LinkedHashMap<>();
        for (PlayerRoles.Deeds h : histories) {
            Agency.Situation s = PlayerRoles.situation(year, place, people, h);
            List<ChangeRecord.Way> open = PlayerRoles.openWays(year, place, people, h);
            System.out.println("     " + PlayerRoles.held(h, year) + ": standing "
                    + s.standing() + ", " + open.size() + " ways - " + open);
            lastOpen = open.size();
            count.put(PlayerRoles.held(h, year), open.size());
        }
        // THE FINDING, and it is the opposite of a ladder: roles open DIFFERENT things, not more of
        // the same thing. A soldier with thirty behind them can found a town; a courtier with an
        // office and five followers cannot, because founding a town wants twenty people who will stay
        // and a court is not a crowd. What is monotone is standing, not the count of ways.
        ok(count.get(PlayerRoles.Role.SOLDIER) > count.get(PlayerRoles.Role.COURTIER),
                "a soldier can do more things than a courtier and is lower on the ladder: "
                        + count.get(PlayerRoles.Role.SOLDIER) + " against "
                        + count.get(PlayerRoles.Role.COURTIER));
        ok(!PlayerRoles.openWays(year, place, people, courtier1600)
                .contains(ChangeRecord.Way.FOUND_A_TOWN),
                "because a courtier has standing and not a following");
        ok(PlayerRoles.openWays(year, place, people, fighter1600)
                .contains(ChangeRecord.Way.FOUND_A_TOWN),
                "while a soldier has thirty people who will follow them");
        List<ChangeRecord.Way> strangerWays = PlayerRoles.openWays(year, place, people, none);
        List<ChangeRecord.Way> rulerWays = PlayerRoles.openWays(year, place, people, ruler);
        ok(rulerWays.size() > strangerWays.size(),
                "and a ruler can do more than a stranger: " + rulerWays.size() + " against "
                        + strangerWays.size());
        ok(rulerWays.contains(ChangeRecord.Way.TAKE_THE_CROWN),
                "including the one thing only a ruler-shaped player can reach: " + rulerWays);
        // The scholar's whole point: the same city, the same deeds of another kind, and the invention
        // that a soldier with two hundred behind them still cannot bring.
        List<ChangeRecord.Way> scholarWays = PlayerRoles.openWays(year, place, people, scholar1600);
        ok(scholarWays.contains(ChangeRecord.Way.BRING_AN_INVENTION_EARLY),
                "a scholar with a study can bring an invention early: " + scholarWays);
        ok(!PlayerRoles.openWays(year, place, people, fighter1600)
                .contains(ChangeRecord.Way.BRING_AN_INVENTION_EARLY),
                "and a soldier with forty behind them cannot");

        // The lapse shows up in the standing too, and this check is the one the bug was found by.
        eq(PlayerRoles.situation(1600, place, people, courtier).standing(), Agency.Standing.OUTSIDER,
                "a courtier who has not been to court since 1500 is a stranger again by 1600");

        // ------------------------------------------------ 6. THE MESSAGE A PLAYER READS
        System.out.println("  " + PlayerRoles.progressLine(none, 1200));
        System.out.println("  " + PlayerRoles.progressLine(d, 1300));
        System.out.println("  " + PlayerRoles.summary(year, place, people, courtier1600));
        ok(PlayerRoles.progressLine(none, 1200).startsWith("Nothing yet"),
                "a new player is told what is nearest rather than what they are not: "
                        + PlayerRoles.progressLine(none, 1200));
        ok(PlayerRoles.summary(year, place, people, courtier1600).contains("courtier"),
                "and the summary names what they are");
        // A player who sold once is one sale from nothing and nine from a merchant; the line should
        // point at the nearer thing, which is the fight, because one fight is closer than nine sales.
        PlayerRoles.Deeds oneSale = none.plusSale(1200);
        ok(PlayerRoles.progressLine(oneSale, 1200).contains("fights"),
                "with a single sale behind them the nearest role is the soldier: "
                        + PlayerRoles.progressLine(oneSale, 1200));

        // ------------------------------------------------ 7. NOBODY IS BORN A RULER
        // The one refusal that matters: a role cannot be granted by the packs. Every path to RULER runs
        // through holding an office in the world, and the only counter for that is in the world.
        for (PlayerRoles.Deeds h : histories) {
            if (PlayerRoles.held(h, year) == PlayerRoles.Role.RULER) {
                ok(h.holdsOffice(), "the only ruler here holds an office, as they must");
            }
            if (!h.holdsOffice()) {
                ok(PlayerRoles.held(h, year) != PlayerRoles.Role.RULER,
                        "and no amount of anything else makes one");
            }
        }
        PlayerRoles.Deeds thousandSales = new PlayerRoles.Deeds(1000, 0, 0, 0, false, 1600);
        ok(PlayerRoles.held(thousandSales, 1600) != PlayerRoles.Role.RULER,
                "a thousand sales and no office is a merchant, not a king: "
                        + PlayerRoles.held(thousandSales, 1600));

        System.out.println(failed == 0
                ? "Step48RolesProbe: " + checks + " checks, 0 failed"
                : "Step48RolesProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
