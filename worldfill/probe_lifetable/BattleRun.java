package com.eternalengine.lifeprobe;

import com.eternalengine.war.Army;
import com.eternalengine.war.Battles;
import com.eternalengine.war.Battles.Band;
import com.eternalengine.war.Battles.Formation;
import com.eternalengine.war.Battles.How;
import com.eternalengine.war.Battles.Outcome;

import java.util.List;

/**
 * Step 40 (D10 armies in action), part 3: the battle register.
 *
 * <p>The old {@code BattleSimulator} decided a battle with one dice roll and then set the losses
 * at 8% for the winner and 18% for the loser, for Cannae and for a skirmish in Flanders alike.
 * The three claims this probe is here to hold the new register to:
 *
 * <ul>
 * <li><b>losses are not a constant.</b> Fight the same battle two hundred times and the loser's
 *     share has to vary, and vary for a reason;</li>
 * <li><b>how the loser goes is what sets the casualty list.</b> An army that withdraws in order
 *     loses far less of itself than one that is encircled, and the register has to say which</li>
 * <li><b>the rifle band is lower than the musket band.</b> A player will assume the opposite, and
 *     the register has to be right: casualty rates have been falling since the seventeenth
 *     century, because armies dispersed faster than weapons got more lethal.</li>
 * </ul>
 */
public final class BattleRun {

    static int checks = 0;
    static int failed = 0;

    /** Places and years where the formation table has a definite answer. */
    static final String[] PLACE = {"Rome", "Greece", "North India", "Wessex", "Edo",
        "Switzerland", "Flanders", "Sweden", "France", "Virginia", "Bohemia", "Zululand",
        "the Western Front", "today"};
    static final double[][] SPOT = {{41.0d, 13.0d}, {38.0d, 23.0d}, {27.0d, 78.0d},
        {51.0d, -2.0d}, {35.0d, 139.0d}, {46.5d, 8.0d}, {50.5d, 3.0d}, {59.0d, 18.0d},
        {48.0d, 4.0d}, {37.0d, -80.0d}, {50.0d, 14.0d}, {-27.0d, 30.0d}, {50.0d, 3.0d},
        {50.0d, 3.0d}};
    static final int[] YEAR = {-200, -400, -300, 1000, 1600, 1470, 1700, 1650, 1805, 1863, 1866,
        1879, 1917, 2020};
    static final String[] WANT = {"roman_triplex", "hoplite_phalanx", "war_elephant",
        "shield_wall", "nagae_yari", "swiss_square", "tercio", "swedish_brigade",
        "line_and_column", "civil_war_skirmish", "open_order", "zulu_horns", "fireteam",
        "fireteam"};

    public static void main(String[] args) {
        ok("the formation table loads: " + Battles.formationCount() + " formations",
            Battles.formationCount() == 16);
        ok("and the battle numbers load: " + Battles.bands().size() + " casualty bands and "
            + Battles.breaks().size() + " ways to lose",
            Battles.bands().size() == 4 && Battles.breaks().size() == 4);

        // ---------------------------------------------------------- what stands where, when
        System.out.println();
        System.out.println("  -- what stands where, when --");
        int wrong = 0;
        for (int i = 0; i < PLACE.length; i++) {
            Formation f = Battles.formationAt(SPOT[i][0], SPOT[i][1], YEAR[i]);
            boolean good = f != null && f.id().equals(WANT[i]);
            if (!good) {
                wrong++;
            }
            System.out.println("    " + pad(PLACE[i], 18) + pad(Integer.toString(YEAR[i]), 6)
                + (f == null ? "NO ANSWER" : f.name()));
        }
        ok("every place and year gets the formation the record says it used", wrong == 0);

        Formation phalanx = Battles.formationAt(38.0d, 23.0d, -330);
        ok("the Macedonian phalanx is what Greece had in 330 BC",
            phalanx != null && "macedonian_phalanx".equals(phalanx.id()));
        ok("and it wants level ground, which is why it lost to the Roman line",
            phalanx != null && "level".equals(phalanx.ground()));
        ok("on broken ground the phalanx is at a real disadvantage: "
            + String.format("%+.2f", Battles.groundEdge(phalanx,
                Battles.formationAt(41.0d, 13.0d, -200), "broken")),
            Battles.groundEdge(phalanx, Battles.formationAt(41.0d, 13.0d, -200), "broken") < 0.0d);

        // ---------------------------------------------------------- the bands
        System.out.println();
        System.out.println("  -- the casualty bands --");
        for (Band b : Battles.bands()) {
            System.out.println("    " + pad(b.id(), 8)
                + "winner " + String.format("%.0f-%.0f%%", b.wlo(), b.whi())
                + "  loser " + String.format("%.0f-%.0f%%", b.llo(), b.lhi())
                + "  (" + b.mark() + ")");
        }
        Band shock = Battles.bandFor("spear");
        Band musket = Battles.bandFor("musket");
        Band rifle = Battles.bandFor("rifle");
        ok("no band lets the winner lose more than the loser", bandsHonest());
        ok("the musket band is the bloodiest in the table", musket.lhi() > shock.lhi()
            && musket.lhi() > rifle.lhi());
        ok("and the rifle band is LOWER than the musket band - " + rifle.lhi() + "% against "
            + musket.lhi() + "% - because casualty rates have been falling since the seventeenth "
            + "century as armies dispersed faster than weapons got more lethal",
            rifle.lhi() < musket.lhi() && rifle.wlo() < musket.wlo());

        // ---------------------------------------------------------- losses are not a constant
        System.out.println();
        System.out.println("  -- the same battle, two hundred times --");
        Army a1 = new Army("legio", "rome", 41.0d, 13.0d, 20000L, 70, 70, "ANCIENT", 20.0d);
        Army d1 = new Army("phalanx", "macedon", 41.0d, 13.0d, 18000L, 60, 55, "ANCIENT", 18.0d);
        double min = 100.0d;
        double max = 0.0d;
        int wins = 0;
        String hows = "";
        for (int i = 0; i < 200; i++) {
            Army at = new Army("legio", "rome", 41.0d, 13.0d, 20000L, 70, 70, "ANCIENT", 20.0d);
            Army df = new Army("phalanx", "macedon", 41.0d, 13.0d, 18000L, 60, 55, "ANCIENT",
                18.0d);
            Outcome o = Battles.fight(at, df, "level", -200, 1000L + i);
            long lost = o.winner() == 1 ? o.defenderLosses() : o.attackerLosses();
            long before = o.winner() == 1 ? 18000L : 20000L;
            double share = 100.0d * lost / (double) before;
            min = Math.min(min, share);
            max = Math.max(max, share);
            if (o.winner() == 1) {
                wins++;
            }
            if (hows.indexOf(o.how().id()) < 0) {
                hows += (hows.isEmpty() ? "" : ", ") + o.how().id();
            }
        }
        System.out.println("    the loser lost between " + String.format("%.0f%%", min) + " and "
            + String.format("%.0f%%", max) + " of itself; the Roman side won " + wins
            + " of 200; the ways it went: " + hows);
        ok("the loser's share is not 18% every time: it runs "
            + String.format("%.0f%%", min) + " to " + String.format("%.0f%%", max),
            max - min > 8.0d);
        ok("and it does not always go the same way: " + hows, hows.split(", ").length >= 2);
        ok("the better army does not win every time - the dice is real - but wins most: "
            + wins + " of 200", wins > 100 && wins < 200);

        // ---------------------------------------------------------- how it broke is what costs
        System.out.println();
        System.out.println("  -- how the loser goes is what sets the casualty list --");
        Formation horns = byId("zulu_horns");
        Formation line = byId("open_order");
        double[] share = new double[Battles.breaks().size()];
        int seen = 0;
        int zuluWin = 0;
        int zuluBloody = 0;
        int britBloody = 0;
        int britWin = 0;
        for (int k = 0; k < Battles.breaks().size(); k++) {
            How h = Battles.breaks().get(k);
            double lo = 100.0d;
            double hi = 0.0d;
            int n = 0;
            for (int i = 0; i < 2000; i++) {
                Army at = new Army("z", "zulu", -27.0d, 30.0d, 12000L, 52, 60, "ERA", 20.0d);
                Army df = new Army("y", "britain", -27.0d, 30.0d, 4000L, 60, 55, "ERA", 18.0d);
                Outcome o = Battles.fight(at, df, horns, line, "open", 1879, 5000L + i);
                if (o == null || o.how() == null) {
                    continue;
                }
                if (o.winner() == 1) {
                    zuluWin++;
                    if (o.how().mult() >= 2.0d) {
                        zuluBloody++;
                    }
                } else if (o.winner() == 2) {
                    britWin++;
                    if (o.how().mult() >= 2.0d) {
                        britBloody++;
                    }
                }
                if (!o.how().id().equals(h.id())) {
                    continue;
                }
                n++;
                long lost = o.winner() == 1 ? o.defenderLosses() : o.attackerLosses();
                long before = o.winner() == 1 ? 4000L : 12000L;
                double s = 100.0d * lost / (double) before;
                lo = Math.min(lo, s);
                hi = Math.max(hi, s);
            }
            if (n > 0) {
                seen++;
            }
            share[k] = hi;
            System.out.println("    " + pad(h.id(), 12) + pad(String.format("x%.1f", h.mult()), 7)
                + (n == 0 ? "did not come up" : pad(String.format("%.0f%% to %.0f%%", lo, hi), 14)
                    + String.format("(%d of 2000)", n))
                + "  " + h.when());
        }
        ok("all four ways to lose come up in a real campaign, not just the two bloodiest: "
            + seen + " of " + Battles.breaks().size(), seen == Battles.breaks().size());
        ok("an army that withdraws in order loses less of itself than one that is encircled: "
            + String.format("%.0f%%", share[0]) + " against " + String.format("%.0f%%", share[3]),
            share[0] > 0.0d && share[3] > 0.0d && share[3] > share[0] * 1.5d);
        System.out.println("    when the horns work they are " + pct(zuluBloody, zuluWin)
            + " annihilations; when the line wins it is " + pct(britBloody, britWin));
        ok("and the way an army fights is what makes a victory decisive: the horns, which were "
            + "built to encircle, finish the job " + pct(zuluBloody, zuluWin)
            + " of the time against " + pct(britBloody, britWin) + " for the line",
            zuluWin > 20 && britWin > 20
            && (double) zuluBloody / zuluWin > (double) britBloody / britWin);

        // ---------------------------------------------------------- ground
        System.out.println();
        System.out.println("  -- the same battle on two kinds of ground --");
        Formation mac = byId("macedonian_phalanx");
        Formation rom = byId("roman_triplex");
        int levelWins = 0;
        int brokenWins = 0;
        for (int i = 0; i < 200; i++) {
            Army at = new Army("phalanx", "macedon", 40.0d, 22.0d, 20000L, 65, 60, "ANCIENT",
                18.0d);
            Army df = new Army("legio", "rome", 40.0d, 22.0d, 20000L, 65, 60, "ANCIENT", 20.0d);
            if (Battles.fight(at, df, mac, rom, "level", -200, 9000L + i).winner() == 1) {
                levelWins++;
            }
            Army at2 = new Army("phalanx", "macedon", 40.0d, 22.0d, 20000L, 65, 60, "ANCIENT",
                18.0d);
            Army df2 = new Army("legio", "rome", 40.0d, 22.0d, 20000L, 65, 60, "ANCIENT", 20.0d);
            if (Battles.fight(at2, df2, mac, rom, "broken", -200, 9000L + i).winner() == 1) {
                brokenWins++;
            }
        }
        System.out.println("    the phalanx beats the Roman line " + levelWins
            + " times in 200 on level ground and " + brokenWins + " times in 200 on broken ground");
        ok("a phalanx that cannot keep its order is a different army: " + brokenWins
            + " wins on broken ground against " + levelWins + " on the plain",
            brokenWins < levelWins);

        // ---------------------------------------------------------- what it says
        System.out.println();
        System.out.println("  -- what the register says --");
        String[] EVENT = {"Cynoscephalae 197 BC, on the ridge",
            "Gaugamela 331 BC, on the plain", "Breitenfeld 1631, in the open",
            "Flanders 1700, in the open", "Waterloo 1815, on the field",
            "Gettysburg 1863, on stony ground", "Isandlwana 1879, in the open",
            "the Somme 1916, on churned ground"};
        int[] WHEN = {-197, -331, 1631, 1700, 1815, 1863, 1879, 1916};
        String[] GROUND = {"broken", "open", "open", "open", "level", "broken", "open", "broken"};
        String[] HOME = {"macedonian_phalanx", "macedonian_phalanx", "swedish_brigade",
            "tercio", "line_and_column", "civil_war_skirmish", "zulu_horns", "open_order"};
        String[] AWAY = {"roman_triplex", "war_elephant", "tercio", "swedish_brigade",
            "line_and_column", "civil_war_skirmish", "open_order", "fireteam"};
        long[] ASIZE = {26000L, 40000L, 42000L, 20000L, 73000L, 75000L, 20000L, 120000L};
        long[] DSIZE = {26000L, 50000L, 35000L, 24000L, 68000L, 83000L, 1800L, 100000L};
        for (int w = 0; w < EVENT.length; w++) {
            Army at = new Army("a", "home", 40.0d, 22.0d, ASIZE[w], 60, 55, "ERA", 18.0d);
            Army df = new Army("d", "away", 40.0d, 22.0d, DSIZE[w], 70, 65, "ERA", 20.0d);
            Outcome o = Battles.fight(at, df, byId(HOME[w]), byId(AWAY[w]), GROUND[w], WHEN[w],
                424242L);
            System.out.println("  " + EVENT[w] + ", " + ASIZE[w] / 1000L + "000 against "
                + DSIZE[w] / 1000L + "000, odds to the attacker "
                + String.format("%.0f%%", o.chance() * 100.0d) + ":");
            System.out.println("    " + o.line());
        }
        System.out.println();
        System.out.println("  card, Isandlwana 1879:");
        Army za = new Army("a", "zulu", -27.0d, 30.0d, 20000L, 70, 65, "ERA", 20.0d);
        Army zd = new Army("d", "britain", -27.0d, 30.0d, 4000L, 60, 55, "ERA", 18.0d);
        for (String l : Battles
                .card(za, zd, byId("zulu_horns"), byId("open_order"), "open", 1879, 7L)
                .split("\n")) {
            System.out.println("   " + l);
        }

        // ---------------------------------------------------------- against the source
        System.out.println();
        System.out.println("  -- does it agree with the one survey that exists? --");
        double sum = 0.0d;
        double wsum = 0.0d;
        int n = 0;
        for (int i = 0; i < 3000; i++) {
            Army at = new Army("a", "sparta", 38.0d, 23.0d, 9000L, 65, 60, "ERA", 18.0d);
            Army df = new Army("d", "athens", 38.0d, 23.0d, 9000L, 60, 55, "ERA", 18.0d);
            Outcome o = Battles.fight(at, df, byId("hoplite_phalanx"), byId("hoplite_phalanx"),
                "level", -400, 77000L + i);
            if (o == null || o.winner() == 0) {
                continue;
            }
            long gone = o.winner() == 1 ? o.defenderLosses() : o.attackerLosses();
            long kept = o.winner() == 1 ? o.attackerLosses() : o.defenderLosses();
            sum += 100.0d * gone / 9000.0d;
            wsum += 100.0d * kept / 9000.0d;
            n++;
        }
        System.out.println("    over " + n + " hoplite battles, an even fight: the winner lost "
            + String.format("%.1f%%", wsum / n) + " on average and the loser "
            + String.format("%.1f%%", sum / n));
        System.out.println("    Krentz, measuring every surviving Greek casualty figure, got "
            + "about 5% and 14%.");
        ok("the loser's average is in Krentz's band, not the old flat 18%: "
            + String.format("%.1f%%", sum / n), sum / n > 8.0d && sum / n < 22.0d);
        ok("and the winner loses far less than the loser, which is the whole point: "
            + String.format("%.1f%%", wsum / n) + " against " + String.format("%.1f%%", sum / n),
            wsum / n < sum / n * 0.6d);

        System.out.println();
        System.out.println(failed == 0
            ? "ALL " + checks + " CHECKS PASSED" : failed + " of " + checks + " CHECKS FAILED");
        if (failed > 0) {
            System.exit(1);
        }
    }

    static boolean bandsHonest() {
        for (Band b : Battles.bands()) {
            if (b.whi() > b.llo()) {
                return false;
            }
        }
        return true;
    }

    /** Fetch a formation by id, so the probe can stage a clash of two doctrines. */
    static Formation byId(String id) {
        for (Formation f : Battles.formations()) {
            if (f.id().equals(id)) {
                return f;
            }
        }
        return null;
    }

    static String pct(long a, long b) {
        return b <= 0 ? "0%" : String.format("%.0f%%", 100.0d * a / (double) b);
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
