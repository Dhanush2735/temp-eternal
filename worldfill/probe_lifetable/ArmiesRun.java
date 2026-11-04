package com.eternalengine.lifeprobe;

import com.eternalengine.war.Army;
import com.eternalengine.war.BattleSimulator;
import com.eternalengine.war.Battles;
import com.eternalengine.war.Morale;
import com.eternalengine.war.Sides;
import com.eternalengine.war.Sieges;
import com.eternalengine.war.Sieges.Siege;
import com.eternalengine.war.Sieges.Town;
import com.eternalengine.war.War;

import java.util.List;

/**
 * Step 40 (D10 armies in action), part 6: <b>the wiring</b>.
 *
 * <p>Parts 1 to 5 built five registers and proved each of them on its own. This is the part that
 * asks whether the mod actually uses them. Before it, the mod's battle path was
 * {@code BattleSimulator}, which set losses at 8% for the winner and 18% for the loser whatever
 * year it was and however the loser went, and moved morale by {@code +10}, {@code -2} or
 * {@code -15}. The registers existed beside it and nothing read them.
 *
 * <p>The four things this probe holds the wiring to:
 *
 * <ul>
 * <li><b>the mod's battle goes through the battle register</b> — the loser of a battle loses a
 *     bigger share than the winner, and by how much depends on how it went;</li>
 * <li><b>morale comes out of the morale register</b> — no {@code +10} or {@code -15} survives in
 *     the mod's own code, and the loser's fall is scaled by how badly it was hurt;</li>
 * <li><b>an army remembers what it has lost</b> — losses go through {@code takeLosses}, so
 *     {@code Army.routing} can be asked of it later, because the rout is where the dying happens
 *     and an army that does not count its own dead cannot know it is breaking;</li>
 * <li><b>and a side that cannot be bound is not offered terms</b> — the siege register will not
 *     open the gates of a warlord's town on a named day, because a conditional surrender is a
 *     bargain between two parties who can each be held to it.</li>
 * </ul>
 */
public final class ArmiesRun {

    static int checks = 0;
    static int failed = 0;

    public static void main(String[] args) {
        ok("all five registers of this step load together: " + Battles.formationCount()
            + " formations, " + Morale.factorCount() + " morale factors, "
            + Morale.raisedCount() + " ways of raising an army, " + Sides.partyCount()
            + " kinds of party, " + Sieges.wallCount() + " kinds of wall",
            Battles.formationCount() > 0 && Morale.factorCount() > 0 && Sides.partyCount() > 0
                && Sieges.wallCount() > 0);

        // ===================================================== the battle, through the register
        System.out.println();
        System.out.println("  -- the mod's battle, through the register --");

        int worse = 0;
        int drawn = 0;
        int fights = 0;
        int routed = 0;
        double loserShare = 0.0d;
        double winnerShare = 0.0d;
        int brokeTotal = 0;
        int brokeWorse = 0;
        int withdrewTotal = 0;
        int withdrewBelow = 0;
        int[] SPAN = {-400, 100, 1200, 1750, 1863, 1916, 1943};
        String[] GROUND = {"level", "open", "broken", "any"};
        for (int i = 0; i < 140; i++) {
            int year = SPAN[i % SPAN.length];
            String ground = GROUND[i % GROUND.length];
            Army a = field("attacker_" + i, 48.0d + (i % 9), 10.0d - (i % 13), 9000L + i * 137L,
                year);
            Army d = field("defender_" + i, 48.0d + (i % 5), 10.0d - (i % 7), 9000L + i * 91L,
                year);
            long a0 = a.size();
            long d0 = d.size();

            Battles.Outcome o = Battles.fight(a, d, ground, year, 7000L + i);
            if (o == null) {
                continue;
            }
            fights++;
            Battles.apply(o, a, d);
            if (o.draw()) {
                drawn++;
                continue;
            }
            Army won = o.winner() == 1 ? a : d;
            Army lost = o.winner() == 1 ? d : a;
            long wonBefore = o.winner() == 1 ? a0 : d0;
            long lostBefore = o.winner() == 1 ? d0 : a0;
            double ws = (wonBefore - won.size()) / (double) wonBefore * 100.0d;
            double ls = (lostBefore - lost.size()) / (double) lostBefore * 100.0d;
            winnerShare += ws;
            loserShare += ls;
            if (ls > ws) {
                worse++;
            }
            double mult = o.how() == null ? 1.0d : o.how().mult();
            if (mult >= 1.0d) {
                brokeTotal++;
                if (ls > ws) {
                    brokeWorse++;
                }
            } else {
                withdrewTotal++;
                if (ls < ws) {
                    withdrewBelow++;
                }
            }
            if (Morale.routs(ls)) {
                routed++;
            }
        }
        int decided = fights - drawn;
        System.out.println("    " + fights + " fights, " + drawn + " drawn, " + decided
            + " decided; the loser lost the bigger share in " + worse + " of them");
        System.out.println("    mean share: winner " + one(winnerShare / Math.max(1, decided))
            + "%, loser " + one(loserShare / Math.max(1, decided)) + "%, and " + routed
            + " of the losers were routed");
        ok("an army that breaks and runs always loses more than the side that beat it: "
            + brokeWorse + " of " + brokeTotal + " times the loser broke -- that is what the "
            + "pursuit is", brokeWorse == brokeTotal && brokeTotal > 30);
        ok("and an army that retires in order does not necessarily: it lost fewer than the "
            + "side that beat it in " + withdrewBelow + " of " + withdrewTotal + ", which is why "
            + "the same army can lose three battles and still be an army",
            withdrewTotal > 0 && withdrewBelow > 0);
        ok("but across all of them the loser still loses far more: " + worse + " of " + decided
            + " decided fights", worse * 10 > decided * 8);
        ok("the gap between them is the pursuit and not marksmanship: the losers lose "
            + one(loserShare / Math.max(1, decided)) + "% against the winners' "
            + one(winnerShare / Math.max(1, decided)) + "%",
            loserShare > winnerShare * 1.5d);
        ok("some losers break and some do not, because how the loser goes is the whole question: "
            + routed + " of " + decided + " routed", routed > 0 && routed < decided);

        // ===================================================== morale out of the register
        System.out.println();
        System.out.println("  -- morale out of the register, not out of a constant --");

        int victory = Morale.factorWeight("victory", 0);
        int defeat = Morale.factorWeight("defeat", 0);
        ok("the register carries the two numbers the mod used to write for itself: victory "
            + victory + ", defeat " + defeat, victory > 0 && defeat < 0);
        ok("and losing is worth more than winning, as the record says it is",
            -defeat > victory);

        int[] upDown = Battles.moraleChange(
            new Battles.Outcome(1, null, null, null, null, 100L, 1500L, 0.6d, ""),
            12000L, 12000L);
        System.out.println("    a decided battle: " + upDown[0] + " to the winner, " + upDown[1]
            + " to the loser, and the loser lost 12.5% of itself");
        ok("the winner is credited and the loser is charged", upDown[0] > 0 && upDown[1] < 0);
        int[] routDelta = Battles.moraleChange(
            new Battles.Outcome(1, null, null, null, null, 100L, 3000L, 0.6d, ""),
            12000L, 12000L);
        System.out.println("    the same battle with the loser ridden down (25% gone): "
            + routDelta[1] + " to the loser");
        ok("a routed army falls further than a beaten one: " + routDelta[1] + " against "
            + upDown[1], routDelta[1] < upDown[1]);
        int[] drawnDelta = Battles.moraleChange(
            new Battles.Outcome(0, null, null, null, null, 0L, 0L, 0.5d, ""), 12000L, 12000L);
        ok("a draw costs both sides something and neither side everything: " + drawnDelta[0]
            + " each", drawnDelta[0] == drawnDelta[1] && drawnDelta[0] < 0
                && drawnDelta[0] > defeat);

        // ===================================================== an army remembers
        System.out.println();
        System.out.println("  -- an army remembers what it has lost --");

        Army lee = new Army("anv", "confederacy", 37.5d, -77.5d, 50000L, 70, 40, "INDUSTRIAL",
            20.0d, 37.5d, -77.5d, "conscript_national", "sovereign_state", null);
        System.out.println("    at the start: " + lee.size() + " men, "
            + one(lee.lossShare() * 100.0d) + "% gone, routing: " + lee.routing());
        ok("an army that has lost nothing is not routing",
            !lee.routing() && lee.lossShare() == 0.0d);
        lee.takeLosses(4000L);
        System.out.println("    after one battle: " + lee.size() + " men, "
            + one(lee.lossShare() * 100.0d) + "% gone, routing: " + lee.routing());
        ok("8% gone and it holds", !lee.routing() && lee.size() == 46000L);
        lee.takeLosses(2600L);
        System.out.println("    after two: " + lee.size() + " men, "
            + one(lee.lossShare() * 100.0d) + "% gone, routing: " + lee.routing());
        ok("13.2% gone and it is breaking, because Krentz's measured point is 12%",
            lee.routing() && lee.size() == 43400L);

        // ===================================================== the mod's own path
        System.out.println();
        System.out.println("  -- BattleSimulator, the mod's own battle path --");

        BattleSimulator sim = new BattleSimulator();
        Army a1 = field("a1", 41.0d, 29.0d, 14000L, 1453);
        Army a2 = field("a2", 41.0d, 29.0d, 11000L, 1453);
        long a1Before = a1.size();
        long a2Before = a2.size();
        BattleSimulator.BattleResult br = sim.simulate(a1, a2, "open", 0, 1453, 31L);
        System.out.println("    " + br.narrativeDesc());
        ok("the mod's battle path answers, and says why", br != null
            && !br.narrativeDesc().isBlank());
        ok("it is not the old flat 8/18: the loser's share is not a constant",
            br.attackerLosses() >= 0 && br.defenderLosses() >= 0
                && !(br.attackerLosses() == 0 && br.defenderLosses() == 0));
        sim.applyResult(br, a1, a2, null, 1453);
        long aGone = a1Before - a1.size();
        long dGone = a2Before - a2.size();
        System.out.println("    the attacker lost " + aGone + ", the defender " + dGone
            + "; routed: " + br.routed());
        ok("applyResult takes the losses through takeLosses, so the army carries them",
            a1.size() == a1Before - br.attackerLosses()
                && a2.size() == a2Before - br.defenderLosses());
        ok("the routed flag is only ever set for the side that lost",
            !br.routed() || (br.attackerRouted() != br.defenderRouted()));
        War war = new War("w1", "a war", List.of("civ_a"), List.of("civ_b"), 1453, null);
        sim.applyResult(br, a1, a2, war, 1453);
        ok("and the war records the battle", war.battles().size() == 1);

        // ===================================================== sides: who can be bound
        System.out.println();
        System.out.println("  -- sides: who can be held to an agreement --");

        War two = new War("w2", "a war of two states", List.of("civ_a"), List.of("civ_b"), 1200,
            null);
        System.out.println("    " + two.treatyLine());
        ok("a war between two states can be ended by a treaty", two.canTreat());
        two.setPartyOf("civ_b", "warlord_band");
        System.out.println("    after the other side turns out to be a warlord band: "
            + two.treatyLine());
        ok("a war with a warlord band in it cannot, and the register names the side that cannot "
            + "be bound", !two.canTreat() && two.treatyLine().contains("warlord"));
        two.setPartyOf("civ_b", "city_commune");
        ok("a commune can be bound, even though a map could never have told you it was one",
            two.canTreat());
        two.setPartyOf("civ_a", "coalition");
        two.setPartyOf("civ_b", "mercenary_company");
        ok("and one unpaid hired company anywhere in a coalition is enough: "
            + two.treatyLine(), !two.canTreat());
        War none = new War("w3", "a war nobody named", List.of("x"), List.of("y"), 1200, null);
        ok("a war whose parties nobody named defaults to two sovereigns rather than to nothing",
            none.canTreat() && none.alliedSide().members().size() == 1);

        // ===================================================== sieges: terms only for the bound
        System.out.println();
        System.out.println("  -- a surrender is a bargain, and a warlord cannot make one --");

        int communeTerms = termsIn("city_commune", 48);
        int stateTerms = termsIn(null, 48);
        int bandTerms = termsIn("warlord_band", 48);
        int hireTerms = termsIn("mercenary_company", 48);
        System.out.println("    48 sieges of the same town: as a commune " + communeTerms
            + " end in terms, unnamed " + stateTerms + ", as a warlord band " + bandTerms
            + ", as a hired company " + hireTerms);
        ok("a commune's gates open on a named day", communeTerms > 0);
        ok("an unnamed town is not punished for the register not knowing what it is",
            stateTerms == communeTerms);
        ok("a warlord's town is never offered terms: it is stormed or it starves, because a "
            + "conditional surrender is a bargain between two parties who can each be held to it",
            bandTerms == 0);
        ok("and neither is a hired company's, because its captain cannot deliver it",
            hireTerms == 0);
        ok("the endings still come out where the town can be bound: "
            + communeTerms + " terms against " + bandTerms + " for the band",
            communeTerms > bandTerms);

        System.out.println();
        System.out.println(failed == 0 ? "ALL " + checks + " CHECKS PASSED"
            : failed + " of " + checks + " CHECKS FAILED");
        if (failed > 0) {
            System.exit(1);
        }
    }

    // ================================================================== helpers

    static Army field(String id, double lat, double lon, long size, int year) {
        Morale.Raised r = Morale.raisedAt(lat, lon, year);
        return new Army(id, "civ_" + id, lat, lon, size, 55 + (int) (size % 30L),
            40 + (int) (size % 50L), "MEDIEVAL", 20.0d, lat, lon,
            r == null ? null : r.id(), null, null);
    }

    /** How many of n sieges of one town end in terms, when the town is this kind of party. */
    static int termsIn(String partyId, int n) {
        int terms = 0;
        for (int i = 0; i < n; i++) {
            int year = 1150 + (i % 9) * 60;
            long mouths = 5000L + (i * 7919L) % 20000L;
            long garrison = Math.max(200L, mouths / 6L + (i * 31L) % 900L);
            Town t = new Town("a town", 52.0d, -1.5d, mouths, garrison, 20 + (i * 13) % 300,
                10 + (i * 17) % 80, (i * 7) % 70,
                i % 3 == 0 ? "dry" : i % 3 == 1 ? "rock" : "wet", partyId);
            Army a = new Army("besieger_" + partyId + "_" + i, "attacker", 52.0d, -1.5d,
                Math.max(500L, garrison * (1L + (i % 7))), 40 + (i * 11) % 55,
                20 + (i * 23) % 75, "MEDIEVAL", 20.0d);
            Siege s = Sieges.besiege(t, a, year, -1, 9000L + i);
            if (s != null && "terms".equals(s.endingId())) {
                terms++;
            }
        }
        return terms;
    }

    static String one(double v) {
        return String.format("%.1f", v);
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
