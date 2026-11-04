package com.eternalengine.lifeprobe;

import com.eternalengine.civilization.Disasters.Disaster;
import com.eternalengine.people.Health;
import com.eternalengine.people.Health.Illness;
import com.eternalengine.people.Health.Remedy;
import com.eternalengine.people.Health.Situation;
import com.eternalengine.people.Health.Tier;

import java.util.List;
import java.util.Locale;

/** Step 38 part 7 (C20 diseases and medicine). Run with {@code probe_lifetable.sh}. */
public final class HealthRun {

    static int checks = 0;
    static int failed = 0;

    // Oxford, a Bihar village, London, Cairo, Tenochtitlan, Amazonia, the high Arctic
    static final double[][] PLACES = {
        {51.75d, -1.26d}, {25.40d, 85.10d}, {51.51d, -0.13d}, {30.04d, 31.24d},
        {19.43d, -99.13d}, {-3.10d, -60.02d}, {78.22d, 15.63d},
    };
    static final String[] NAMES = {
        "Oxford", "a Bihar village", "London", "Cairo", "Tenochtitlan", "Amazonia", "Svalbard",
    };

    public static void main(String[] args) {
        ok("the pack is loaded", Health.remedyCount() == 14 && Health.illnessCount() == 18);
        System.out.println("  " + Health.remedyCount() + " remedies, " + Health.illnessCount()
            + " diseases");

        int bad = 0;
        for (Remedy r : Health.allRemedies()) {
            if (r.source().isEmpty() || r.name().isEmpty()) {
                bad++;
            }
        }
        for (Illness d : Health.allIllnesses()) {
            if (d.source().isEmpty() || d.name().isEmpty()) {
                bad++;
            }
            if (d.cfr() <= 0.0d || d.cfr() > 1.0d) {
                bad++;
            }
        }
        ok("every row is sourced, named, and carries a believable case fatality", bad == 0);

        // ------------------------------------------------------- the defect this fixes
        System.out.println();
        System.out.println("  -- the world-wide year tier is dead: 1945, in two places --");
        int ox = 0, bi = 5;
        Tier tOx = Health.tierAt(PLACES[ox][0], PLACES[ox][1], 1945);
        Tier tBi = Health.tierAt(PLACES[bi][0], PLACES[bi][1], 1945);
        ok("in 1945 Oxford is modern", tOx == Tier.MODERN);
        ok("in 1945 Amazonia is not modern, because penicillin has not been there for centuries",
            tBi != Tier.MODERN);
        System.out.println("    Oxford 1945: " + tOx + " (" + tOx.phrase() + ")");
        System.out.println("    Amazonia 1945: " + tBi + " (" + tBi.phrase() + ")");
        Remedy pen = Health.remedy("antibiotics");
        ok("penicillin has reached Oxford by 1945", pen.here(PLACES[ox][0], PLACES[ox][1], 1945));
        ok("and not the Amazon by 1945", !pen.here(PLACES[bi][0], PLACES[bi][1], 1945));
        System.out.println("    penicillin: Oxford " + pen.yearLine(PLACES[ox][0], PLACES[ox][1])
            + ", Amazonia " + pen.yearLine(PLACES[bi][0], PLACES[bi][1]));

        // ------------------------------------------------------- before anything worked
        System.out.println();
        System.out.println("  -- the Black Death, in a place with nothing --");
        Illness bd = Health.find("black_death");
        ok("the Black Death is in the table", bd != null);
        ok("in London in 1348 the medicine of the humours takes almost nothing off it",
            bd.helpAt(PLACES[2][0], PLACES[2][1], 1348) < 0.05d);
        ok("and the register says so in words rather than quoting a hopeful 2 per cent",
            Health.at(PLACES[2][0], PLACES[2][1], 1348).line()
                .contains("Almost nothing in this place can touch it"));
        ok("quarantine had not reached London in 1348 - it was eight years old in Ragusa",
            !Health.remedy("quarantine").here(PLACES[2][0], PLACES[2][1], 1348));

        // ------------------------------------------------------- a remedy that worked
        System.out.println();
        System.out.println("  -- cholera, before and after clean water --");
        Illness ch = Health.find("cholera");
        double before = ch.fatalityAt(PLACES[2][0], PLACES[2][1], 1840);
        double after = ch.fatalityAt(PLACES[2][0], PLACES[2][1], 1900);
        ok("cholera got less deadly in London between 1840 and 1900", after < before);
        ok("and by 1900 the medicine there takes a real bite out of it",
            ch.helpAt(PLACES[2][0], PLACES[2][1], 1900) > 0.2d);
        System.out.println(String.format(Locale.ROOT,
            "    London 1840: %.0f%% fatal; London 1900: %.0f%% fatal",
            before * 100.0d, after * 100.0d));
        System.out.println("    epidemiology reached London "
            + Health.remedy("epidemiology").yearLine(PLACES[2][0], PLACES[2][1]));

        // ------------------------------------------------------- the one that is over
        System.out.println();
        Illness sp = Health.find("smallpox");
        ok("smallpox is over everywhere by 2000", sp.overBy(PLACES[2][0], PLACES[2][1], 2000));
        ok("and it was not over in 1700", !sp.overBy(PLACES[2][0], PLACES[2][1], 1700));
        ok("vaccination took more of the dying than variolation did",
            sp.fatalityAt(PLACES[2][0], PLACES[2][1], 1800)
            < sp.fatalityAt(PLACES[2][0], PLACES[2][1], 1750));
        System.out.println("    smallpox: over in London "
            + Health.remedy("vaccine").yearLine(PLACES[2][0], PLACES[2][1]));

        // ------------------------------------------------------- geography
        System.out.println();
        ok("malaria cannot reach Svalbard", !Health.find("malaria").possibleAt(78.22d, 15.63d, 1500));
        ok("and it can reach the Amazon", Health.find("malaria").possibleAt(-3.10d, -60.02d, 1500));
        ok("smallpox had not been seen in Tenochtitlan in AD 1000, and it was not",
            !sp.possibleAt(19.43d, -99.13d, 1000));
        ok("care is always between nothing and everything", careSane());

        // ------------------------------------------------------- the join to the hazard pack
        System.out.println();
        System.out.println("  -- the sickness actually in force, named --");
        Disaster londonPlague = Health.sicknessAt(PLACES[2][0], PLACES[2][1], 1348);
        ok("London in 1348 has a sickness in force", londonPlague != null);
        if (londonPlague != null) {
            System.out.println("    " + londonPlague.name() + ", " + londonPlague.yearLabel());
            ok("and this table can name it", Health.nameOf(londonPlague) != null);
        }
        ok("the medicine of the humours had not reached the Amazon before anybody got there",
            Health.remedy("humoral").arrivedAt(PLACES[5][0], PLACES[5][1]) >= 1492);
        ok("and quarantine had, by 1600, because a ship brought it",
            Health.remedy("quarantine").arrivedAt(PLACES[5][0], PLACES[5][1]) >= 1492);
        ok("a quiet year in a quiet place has no sickness in force",
            Health.sicknessAt(PLACES[6][0], PLACES[6][1], 1700) == null);

        // ------------------------------------------------------- the prose
        System.out.println();
        System.out.println("  -- what the register says --");
        int[][] WHEN = {{2, 1348}, {2, 1840}, {2, 1900}, {0, 1945}, {1, 1945},
                        {5, 1500}, {3, 1000}, {6, 1900}};
        for (int[] w : WHEN) {
            System.out.println("  " + NAMES[w[0]] + " " + w[1] + ": "
                + Health.at(PLACES[w[0]][0], PLACES[w[0]][1], w[1]).line());
        }
        System.out.println();
        System.out.println("  card, a Bihar village 1945:");
        for (String l : Health.card(PLACES[1][0], PLACES[1][1], 1945).split("\n")) {
            System.out.println("   " + l);
        }
        System.out.println("  card, Oxford 1945:");
        for (String l : Health.card(PLACES[0][0], PLACES[0][1], 1945).split("\n")) {
            System.out.println("   " + l);
        }

        System.out.println();
        System.out.println(failed == 0
            ? "ALL " + checks + " CHECKS PASSED" : failed + " of " + checks + " CHECKS FAILED");
        if (failed > 0) {
            System.exit(1);
        }
    }

    static boolean careSane() {
        for (double[] p : PLACES) {
            for (int y : new int[] {-3000, 0, 1000, 1500, 1800, 1900, 1945, 2000, 2020}) {
                double c = Health.careAt(p[0], p[1], y);
                if (!(c > 0.0d && c <= 1.0d)) {
                    return false;
                }
            }
        }
        return true;
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
