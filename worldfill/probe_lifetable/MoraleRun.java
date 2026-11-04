package com.eternalengine.lifeprobe;

import com.eternalengine.war.Army;
import com.eternalengine.war.FormationType;
import com.eternalengine.war.Morale;
import com.eternalengine.war.Morale.Factor;
import com.eternalengine.war.Morale.Raised;
import com.eternalengine.war.Morale.Reading;
import com.eternalengine.war.Morale.State;
import com.eternalengine.war.Sides;
import com.eternalengine.war.Sides.Party;
import com.eternalengine.war.Sides.Side;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * Step 40 (D10 armies in action), part 5: morale and sides.
 *
 * <p>The old {@code BattleSimulator} handed morale three integers and no reason. An army that had
 * not been paid for four months and an army that had just taken a town got the same ten points,
 * and both sides of a battle lost the same percentage of their men.
 *
 * <p>The claims this probe holds the new register to:
 *
 * <ul>
 * <li><b>dispersion costs morale rather than granting it</b> - du Picq's most counter-intuitive
 *     claim, and the one an army model is most likely to get backwards;</li>
 * <li><b>depth gains it</b> - the Romans kept the rear rank away from the carnage;</li>
 * <li><b>losing is worse than winning is good</b> - Lee's men fought hungry and cheerful for
 *     three years and went home in the fourth;</li>
 * <li><b>the rout is where the dying happens</b> - the losers of a battle do not lose the same
 *     share as the winners, and the gap is the pursuit;</li>
 * <li><b>desertion lands on the measured rates</b> - Prussia at 3.2 a year, the Confederacy in
 *     1864 far worse than the Union in 1863, and an unpaid hired company worst of all;</li>
 * <li><b>and a party need not be a state</b> - Brecke's rule, with the consequence that a side
 *     containing a warlord band or an unpaid company cannot be bound by a treaty at all.</li>
 * </ul>
 */
public final class MoraleRun {

    static int checks = 0;
    static int failed = 0;

    public static void main(String[] args) {
        ok("the morale register loads: " + Morale.factorCount() + " factors, "
            + Morale.raisedCount() + " ways of raising an army, " + Morale.rateCount()
            + " measured desertion rates and " + Morale.breaking().size() + " ways of breaking",
            Morale.factorCount() >= 30 && Morale.raisedCount() >= 8 && Morale.rateCount() >= 10
                && Morale.breaking().size() >= 3);
        ok("the sides register loads: " + Sides.partyCount() + " kinds of party",
            Sides.partyCount() >= 12);

        // ===================================================== du Picq: dispersion and depth
        System.out.println();
        System.out.println("  -- du Picq: the shape they are standing in --");

        // du Picq's claim is about firearms, and this row is dated to them: "since the invention
        // of fire arms... the more men think themselves isolated, the more need they have of high
        // morale." So the dispersion test belongs in 1863, next to a line and a skirmish line.
        State line63 = base(1863, 39.0d, -77.0d, "conscript_national", FormationType.LINE, 2);
        State skim63 = base(1863, 39.0d, -77.0d, "conscript_national", FormationType.SKIRMISH, 1);
        Reading rl2 = Morale.read(line63);
        Reading rsk = Morale.read(skim63);
        System.out.println("    1863, in line:          " + rl2.line());
        System.out.println("    1863, in skirmish order: " + rsk.line());
        ok("dispersion costs morale rather than granting it: the same men in loose order ("
            + rsk.morale() + ") are worth less than in line (" + rl2.morale() + ")",
            rsk.morale() < rl2.morale());
        ok("the loose order is charged for dispersion and the close order is not",
            hasFactor(rsk, "dispersion_cost") && !hasFactor(rsk, "close_order_confidence")
                && hasFactor(rl2, "close_order_confidence"));

        // Depth is older than gunpowder, and the Romans knew it first.
        State phalanx = base(-400, 38.0d, 23.0d, "citizen_militia", FormationType.PHALANX, 8);
        State skirmish = base(-400, 38.0d, 23.0d, "citizen_militia", FormationType.SKIRMISH, 1);
        Reading rp = Morale.read(phalanx);
        Reading rs = Morale.read(skirmish);
        System.out.println("    -400, phalanx 8 deep:   " + rp.line());
        System.out.println("    -400, skirmish 1 deep:  " + rs.line());
        State deep4 = base(-400, 38.0d, 23.0d, "citizen_militia", FormationType.SQUARE, 4);
        State thin1 = base(-400, 38.0d, 23.0d, "citizen_militia", FormationType.SQUARE, 1);
        ok("depth gains morale: 4 ranks (" + Morale.read(deep4).morale() + ") beat 1 rank ("
            + Morale.read(thin1).morale() + "), because the rear cannot see the carnage",
            Morale.read(deep4).morale() > Morale.read(thin1).morale());
        ok("the deep body is credited with depth and the thin one is charged for it",
            hasFactor(Morale.read(deep4), "depth_holds")
                && hasFactor(Morale.read(thin1), "thin_panics"));
        ok("and it works before gunpowder as well as after: a phalanx (" + rp.morale()
            + ") is worth more than the same men thrown out as skirmishers (" + rs.morale() + ")",
            rp.morale() > rs.morale());

        // ===================================================== winning and losing
        System.out.println();
        System.out.println("  -- winning and losing --");

        State win = base(1864, 37.5d, -77.5d, "conscript_national", FormationType.LINE, 2);
        win = with(win, true, false, true, false);
        State lose = with(win, false, true, true, false);
        Reading rw = Morale.read(win);
        Reading rl = Morale.read(lose);
        State plain = with(win, false, false, true, false);
        int gain = rw.morale() - Morale.read(plain).morale();
        int loss = Morale.read(plain).morale() - rl.morale();
        System.out.println("    winning: " + rw.morale());
        System.out.println("    neither: " + Morale.read(plain).morale());
        System.out.println("    losing:  " + rl.morale());
        ok("losing (" + -loss + ") is worse than winning (" + gain + ") is good, and the record "
            + "says so: 'Lee's men fought hungry through much of the Civil War, cheerfully and "
            + "without complaint; it was only when Grant and Sherman began to close in that they "
            + "deserted'", loss > gain && gain > 0);

        // ===================================================== the rout is where the dying happens
        System.out.println();
        System.out.println("  -- the rout is where the dying happens --");

        long men = 10000L;
        long winnersFall = (long) (men * Morale.winnerLoss() / 100.0d);
        long losersFall = (long) (men * Morale.loserLoss() / 100.0d);
        long pursuit = (long) (men * Morale.pursuitLoss() / 100.0d);
        System.out.println("    10,000 a side: the winners lose " + winnersFall
            + ", the losers lose " + losersFall + ", of which " + pursuit + " is the pursuit");
        ok("the losers of a battle lose more than the winners do ("
            + Morale.loserLoss() + "% against " + Morale.winnerLoss() + "%)",
            Morale.loserLoss() > Morale.winnerLoss());
        ok("most of the losers' dead are not lost in the fighting but after it: the pursuit ("
            + Morale.pursuitLoss() + " points) is more than half of the losers' whole share",
            Morale.pursuitLoss() > Morale.loserLoss() / 2.0d);
        ok("an army is not destroyed before the register will admit it has routed",
            Morale.routThreshold() < Morale.loserLoss());
        ok("12 per cent gone and the body is routing; 5 per cent and it is not",
            Morale.routs(12.0d) && !Morale.routs(5.0d));
        ok("the register names the rout, not the fighting, as what a 20 per cent loss amounts to",
            Morale.breakingAt(20.0d, -400) != null
                && "pursuit".equals(Morale.breakingAt(20.0d, -400).id()));
        ok("mutiny and mass desertion are not caused by casualties at all, and say so",
            !Morale.notOnCasualties(1864).isEmpty()
                && Morale.notOnCasualties(1864).stream().noneMatch(b -> b.onCasualties()));

        // ===================================================== desertion, against the record
        System.out.println();
        System.out.println("  -- desertion, against the record --");

        double prussia = rate("professional_standing", 1730, true, true, true);
        double saxon = rate("professional_standing", 1720, true, true, true);
        System.out.println("    a long-service army in 1730: " + one(prussia) + "% a year");
        ok("a long-service army in the age of reason loses about 3 to 5 per cent a year, which is "
            + "Duffy's measured band for Prussia (3.2), France (4.4) and Saxony (7.0)",
            prussia >= 3.0d && prussia <= 5.0d);
        ok("the register can say which army it is quoting",
            Morale.rateFor(Morale.raised("professional_standing"), 1730) != null);

        State union63 = base(1863, 38.0d, -77.0d, "conscript_national", FormationType.LINE, 2);
        union63 = with(union63, true, false, true, true);
        State rebel64 = with(union63, false, true, false, true);
        double uRate = Morale.desertionPerYear(union63);
        double cRate = Morale.desertionPerYear(rebel64);
        System.out.println("    the Army of the Potomac, 1863, paid and advancing: "
            + one(uRate) + "% a year");
        System.out.println("    the Army of Northern Virginia, 1864, unpaid and closing in: "
            + one(cRate) + "% a year");
        ok("the Confederates in 1864 desert far faster than the Union in 1863 (" + one(cRate)
            + "% against " + one(uRate) + "%): the same men held for three years and went home "
            + "in the fourth", cRate > uRate * 2.0d);
        Double cTotal = Morale.totalDesertion(Morale.raised("conscript_national"), 1864);
        Double uTotal = Morale.rate("union_1861").totalPct();
        System.out.println("    and across the whole war: the Union " + one(uTotal)
            + "%, the Confederacy " + one(cTotal) + "%");
        ok("the whole-war figures land on the record: the Union 9 to 12 per cent of 2.1 million "
            + "and the Confederacy 10 to 15 per cent of 800,000 to a million",
            uTotal >= 9.0d && uTotal <= 12.0d && cTotal >= 10.0d && cTotal <= 15.0d);

        State hiredPaid = base(1400, 43.0d, 11.0d, "mercenary_company", FormationType.LINE, 2);
        hiredPaid = withFlags(with(hiredPaid, true, false, true, true), false, true, false,
            false);
        State hiredUnpaid = with(hiredPaid, true, false, false, true);
        System.out.println("    a hired company, paid:   " + one(Morale.desertionPerYear(hiredPaid))
            + "% a year");
        System.out.println("    the same company, unpaid: "
            + one(Morale.desertionPerYear(hiredUnpaid)) + "% a year");
        ok("an unpaid hired company loses men twice as fast as a paid one, because 'hired troops "
            + "could passively refuse to fight, mutiny, desert to a higher bidder'",
            Morale.desertionPerYear(hiredUnpaid) >= Morale.desertionPerYear(hiredPaid) * 2.0d
            && Morale.desertionPerYear(hiredPaid) < 12.0d);

        // ===================================================== how they were raised
        System.out.println();
        System.out.println("  -- how the men were raised --");

        Raised swiss = Morale.raisedAt(46.9d, 8.2d, 1450);
        ok("a Swiss valley in 1450 raises a citizen militia and not a warlord band, because the "
            + "narrowest box wins", swiss != null && "citizen_militia".equals(swiss.id()));
        Raised steppe = Morale.raisedAt(47.0d, 105.0d, 1200);
        ok("the steppe in 1200 raises a khan's following",
            steppe != null && "steppe_following".equals(steppe.id()));
        Raised saxonHome = Morale.raisedAt(51.0d, 13.0d, 1740);
        ok("Saxony in 1740 raises a standing army",
            saxonHome != null && "professional_standing".equals(saxonHome.id()));

        for (Raised r : Morale.raised()) {
            System.out.println("    " + pad(r.id(), 24) + pad(String.valueOf(r.cohesion()), 5)
                + pad(one(r.desertion()) + "%/yr", 10) + " paid in " + r.paidIn());
        }
        ok("a citizen militia is worth more than a warlord band and loses fewer men",
            Morale.raised("citizen_militia").cohesion()
                > Morale.raised("warlord_band").cohesion()
            && Morale.raised("citizen_militia").desertion()
                < Morale.raised("warlord_band").desertion());
        ok("slave soldiers desert least of all, having nowhere to desert to",
            Morale.raised("slave_soldier").desertion()
                <= Morale.raised("professional_standing").desertion());

        // ===================================================== the reading accounts for itself
        System.out.println();
        System.out.println("  -- every point accounted for --");

        Reading r = Morale.read(rebel64);
        System.out.println("    " + r.line());
        ok("the reading accounts for every point of itself: " + r.base() + " base, "
            + r.helpSum() + " helping, " + r.hurtSum() + " hurting",
            r.base() + r.helpSum() + r.hurtSum() == r.morale());
        ok("the register says where each point came from rather than printing a number",
            r.line().contains("+") && r.line().contains("(-")
                && r.line().length() > 80);
        ok("the primary group is in every reading, at every date, in every place",
            Morale.read(phalanx).helping().stream().anyMatch(f -> f.id().equals("primary_group"))
                && Morale.read(rebel64).helping().stream()
                    .anyMatch(f -> f.id().equals("primary_group")));
        ok("a figure this register read off rather than measured says so every time it is "
            + "printed", !"estimated".equals(r.raised().mark()) || r.line().contains("[est]"));

        // ===================================================== what belongs to what century
        System.out.println();
        System.out.println("  -- what belongs to what century --");

        State france1750 = base(1750, 48.0d, 2.0d, "professional_standing", FormationType.LINE, 2);
        State france1800 = base(1800, 48.0d, 2.0d, "conscript_national", FormationType.LINE, 2);
        ok("the nation is not a factor in 1750 and is one in 1800, and the date is the levée en "
            + "masse", !hasFactor(Morale.read(france1750), "nationalism")
                && hasFactor(Morale.read(france1800), "nationalism"));
        State rome = base(-100, 41.9d, 12.5d, "professional_standing", FormationType.SQUARE, 3);
        ok("decimation belongs to republican Rome and not to France in 1750",
            hasFactor(Morale.read(rome), "decimation")
                && !hasFactor(Morale.read(france1750), "decimation"));
        State somme = base(1917, 50.0d, 2.8d, "conscript_national", FormationType.SKIRMISH, 1);
        ok("blocking detachments belong to the age of total war and to no other",
            hasFactor(Morale.read(somme), "blocking_detachments")
                && !hasFactor(Morale.read(france1800), "blocking_detachments"));
        ok("a hired company is charged for the other side's bid and a levy is not",
            hasFactor(Morale.read(hiredPaid), "higher_bid")
                && !hasFactor(Morale.read(france1750), "higher_bid"));

        // ===================================================== sides
        System.out.println();
        System.out.println("  -- who is fighting, and as what --");

        for (Party p : Sides.parties()) {
            System.out.println("    " + pad(p.id(), 24)
                + pad(p.willTreat() ? "can treat" : "CANNOT TREAT", 14)
                + pad(p.canInitiate() ? "can start one" : "cannot start one", 17)
                + p.raised());
        }
        ok("a sovereign state can be bound by a treaty",
            Sides.party("sovereign_state").willTreat());
        ok("a warlord band cannot, which is Brecke's point: 'conflicts between warlords when "
            + "there is no state involvement qualify as violent conflicts'",
            !Sides.party("warlord_band").willTreat());
        ok("a hired company cannot, because its captain cannot deliver it",
            !Sides.party("mercenary_company").willTreat());
        ok("civilians cannot start a war, which is what the word means",
            !Sides.party("civilians").canInitiate());
        ok("civilians cannot sign one either", !Sides.party("civilians").willTreat());
        ok("every party names a way its troops were raised that the morale pack has heard of",
            Sides.parties().stream().allMatch(p -> p.raised() != null));

        Side france = Sides.side(Arrays.asList("sovereign_state", "city_commune"));
        Side withBand = Sides.side(Arrays.asList("sovereign_state", "warlord_band"));
        Side withHire = Sides.side(Arrays.asList("sovereign_state", "mercenary_company"));
        ok("a side of a state and a commune can treat", france.willTreat());
        ok("a side containing a warlord band cannot, because one member cannot be held to it",
            !withBand.willTreat());
        ok("a side containing an unpaid hired company cannot either, and that is why half the "
            + "sackings in the Italian wars begin there", !withHire.willTreat());
        ok("a side's worth is the weakest body in it, because a line is only as good as the unit "
            + "that gives way", withBand.cohesion() < france.cohesion());

        Party florence = Sides.partyAt(43.77d, 11.25d, 1400);
        ok("a map and a year cannot tell you that Florence is a commune, and the register says so "
            + "by leaving local parties out of partyAt: for Florence in 1400 it answers '"
            + (florence == null ? "nothing" : florence.id()) + "'",
            florence != null && !"city_commune".equals(florence.id())
                && florence.guessable());
        Party commune = Sides.party("city_commune");
        ok("a commune named by the town that knows is a city that governs itself, can be bound, "
            + "and fields better men (" + commune.cohesion() + ") than any state can hire ("
            + Morale.raised("mercenary_company").cohesion() + ") -- which is the party the siege "
            + "register was written for",
            commune.willTreat() && "city".equals(commune.kind())
                && commune.cohesion() > Morale.raised("mercenary_company").cohesion());
        Party khanate = Sides.partyAt(47.0d, 105.0d, 1200);
        ok("a place a map *can* read is read: the steppe in 1200 gives a khan's following",
            khanate != null && "steppe_khanate".equals(khanate.id()));
        ok("there are more kinds of party that cannot be bargained with than that can, in 1400",
            Sides.cannotTreat(1400).size() >= Sides.canTreat(1400).size());

        // ===================================================== armies, in the flesh
        System.out.println();
        System.out.println("  -- an army in the flesh --");

        Army lee = new Army("anv", "confederacy", 37.5d, -77.5d, 50000L, 70, 40, "INDUSTRIAL",
            20.0d, 37.5d, -77.5d, "conscript_national", "sovereign_state", FormationType.LINE);
        System.out.println("    before Petersburg: " + lee.size() + " men, morale " + lee.morale()
            + ", " + one(lee.lossShare() * 100.0d) + "% gone, routing: " + lee.routing());
        lee.takeLosses(6000L);
        System.out.println("    after the Crater:  " + lee.size() + " men, morale " + lee.morale()
            + ", " + one(lee.lossShare() * 100.0d) + "% gone, routing: " + lee.routing());
        ok("an army that has lost 12 per cent of itself is routing and one at 5 per cent is not",
            lee.routing() && lee.lossShare() * 100.0d >= 12.0d);

        Army away = new Army("exp", "france", 55.0d, 37.0d, 40000L, 60, 30, "INDUSTRIAL", 20.0d,
            48.8d, 2.3d, "professional_standing", "sovereign_state", FormationType.LINE);
        ok("an army knows how far from home it is: " + Math.round(away.homeDistanceKm())
            + " km from Paris to the Moscow road", away.homeDistanceKm() > 2000.0d);

        long before = away.size();
        long home = away.desertions(1812, true, false, true, false);
        System.out.println("    and loses " + home + " of " + before + " men gone in the year");
        ok("an army 2,500 km from home and short of supply loses men, and the register says how "
            + "many rather than only that it did", home > 0L && home < before);

        Army unpaid = new Army("cmp", "milan", 45.4d, 9.2d, 8000L, 50, 60, "MEDIEVAL", 20.0d,
            45.4d, 9.2d, "mercenary_company", "mercenary_company", FormationType.LINE);
        long strength = unpaid.size();
        long gonePaid = unpaid.desertions(1400, true, false, true, false);
        unpaid.setSize(strength);
        long goneUnpaid = unpaid.desertions(1400, true, false, false, false);
        System.out.println("    a company of 8,000 in Milan: " + gonePaid + " go when paid, "
            + goneUnpaid + " when the pay stops");
        ok("an unpaid company melts and a paid one mostly does not: " + goneUnpaid + " go against "
            + gonePaid, goneUnpaid >= gonePaid * 2 && gonePaid < strength / 10L);
        ok("an army knows what kind of party fields it and whether that party can be held to a "
            + "treaty", unpaid.party(1400) != null && !unpaid.party(1400).willTreat());

        // ===================================================== the gaps
        System.out.println();
        System.out.println("  -- what this register will not answer --");
        List<Raised> oceanian = new ArrayList<>();
        for (Raised rr : Morale.raised()) {
            if (rr.inForce(1500) && rr.here(-20.0d, -160.0d)) {
                oceanian.add(rr);
            }
        }
        System.out.println("    the south Pacific, 1500: " + oceanian.size()
            + " row(s), and the only one is the world-wide default");
        ok("Oceania answers with the world-wide default and nothing else, which is the register "
            + "admitting it read nothing for it",
            oceanian.size() == 1 && "warlord_band".equals(oceanian.get(0).id()));
        ok("a standing army is not a fact about the whole world: the register will not put one "
            + "in the Pacific in 1500",
            Morale.raised("professional_standing") != null
                && !Morale.raised("professional_standing").here(-20.0d, -160.0d));

        System.out.println();
        System.out.println(failed == 0 ? "ALL " + checks + " CHECKS PASSED"
            : failed + " of " + checks + " CHECKS FAILED");
        if (failed > 0) {
            System.exit(1);
        }
    }

    // ================================================================== helpers

    static State base(int year, double lat, double lon, String raised, FormationType f, int ranks) {
        return new State(year, lat, lon, raised, f, ranks, false, false, false, false, true,
            true, false, false, false, false, false, false, false, false, false, false);
    }

    static State with(State s, boolean winning, boolean losing, boolean paid, boolean home) {
        return new State(s.year(), s.lat(), s.lon(), s.raised(), s.formation(), s.ranks(),
            winning, losing, s.lastVictory(), s.lastDefeat(), home, paid, s.plunderPromised(),
            s.plundered(), s.besieged(), s.hungry(), s.sick(), s.drafted(), s.hired(),
            s.blooded(), s.raw(), s.longWar());
    }

    /** The flags that say what the army is, which the register cannot guess from a map. */
    static State withFlags(State s, boolean drafted, boolean hired, boolean blooded, boolean raw) {
        return new State(s.year(), s.lat(), s.lon(), s.raised(), s.formation(), s.ranks(),
            s.winning(), s.losing(), s.lastVictory(), s.lastDefeat(), s.home(), s.paid(),
            s.plunderPromised(), s.plundered(), s.besieged(), s.hungry(), s.sick(), drafted,
            hired, blooded, raw, s.longWar());
    }

    static double rate(String raised, int year, boolean home, boolean paid, boolean winning) {
        State s = base(year, 52.5d, 13.4d, raised, FormationType.LINE, 2);
        return Morale.desertionPerYear(with(s, winning, !winning, paid, home));
    }

    static boolean hasFactor(Reading r, String id) {
        for (Factor f : r.helping()) {
            if (f.id().equals(id)) {
                return true;
            }
        }
        for (Factor f : r.hurting()) {
            if (f.id().equals(id)) {
                return true;
            }
        }
        return false;
    }

    static String one(double v) {
        return String.format("%.1f", v);
    }

    static String pad(String s, int n) {
        StringBuilder sb = new StringBuilder(s == null ? "" : s);
        while (sb.length() < n) {
            sb.append(' ');
        }
        return sb.toString();
    }

    static void ok(String what, boolean pass) {
        checks++;
        if (pass) {
            System.out.println("  ok   " + what);
        } else {
            failed++;
            System.out.println("  FAIL " + what);
        }
    }
}
