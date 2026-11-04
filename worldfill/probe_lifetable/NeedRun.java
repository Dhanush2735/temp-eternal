package com.eternalengine.lifeprobe;

import com.eternalengine.civilization.Disasters;
import com.eternalengine.civilization.Disasters.Disaster;
import com.eternalengine.people.Households;
import com.eternalengine.people.Jobs;
import com.eternalengine.people.Needs;
import com.eternalengine.people.Needs.Need;
import com.eternalengine.people.Needs.Situation;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Checks the needs register with no Minecraft and no Gradle. The register invents almost nothing —
 * every number is read off a register that already exists — so what this probe is really testing
 * is the composition: that a famine hits the grower harder than the buyer, that a plague and an
 * earthquake are different kinds of fear, and that faith rises where the day stops to pray.
 */
public final class NeedRun {

    private static int checks;
    private static final List<String> failures = new ArrayList<>();

    private static void ok(boolean pass, String what) {
        checks++;
        if (!pass) {
            failures.add(what);
            System.out.println("FAIL  " + what);
        }
    }

    private static void eq(String what, int got, int want) {
        checks++;
        if (got != want) {
            failures.add(what + ": got " + got + ", want " + want);
            System.out.println("FAIL  " + what + ": got " + got + ", want " + want);
        }
    }

    private static final int[] YEARS = {-10000, -3000, -1000, -1, 1, 500, 1000, 1348, 1500, 1700,
            1800, 1850, 1900, 1950, 2000, 2026};

    static int run() {
        Needs t = Needs.get();
        Disasters dz = Disasters.get();
        System.out.println();
        System.out.println("=== needs and mind, over " + dz.count() + " dated hazards ===");
        ok(dz.count() > 0, "the hazard pack loaded nothing");

        // -------------------------------------------------- every place, every year, whole numbers
        int holes = 0;
        int bad = 0;
        for (String[] s : HomeRun.SPOTS) {
            double lat = Double.parseDouble(s[1]);
            double lon = Double.parseDouble(s[2]);
            for (int y : YEARS) {
                Situation sit = t.at(lat, lon, y, false, "farming", "christianity");
                if (sit == null || sit.needs().isEmpty()) {
                    holes++;
                    continue;
                }
                for (Need n : sit.needs()) {
                    if (!(n.level() >= 0.0d && n.level() <= 1.0d)) {
                        bad++;
                        System.out.println("FAIL  " + s[0] + " " + y + " " + n.id() + " = "
                                + n.level());
                    }
                }
            }
        }
        ok(holes == 0, holes + " place-years with no situation at all");
        ok(bad == 0, bad + " need levels outside nought to one");
        eq("five needs", t.at(51.51, -0.13, 1700, false, "farming", "christianity")
                .needs().size(), 5);

        // -------------------------------------------------- the claim the register is built on
        System.out.println();
        System.out.println("--- the same failed harvest, on two people ---");
        Disaster famine = firstOf(dz, "FAMINE");
        Disaster plague = firstOf(dz, "PLAGUE", "EPIDEMIC", "PANDEMIC");
        Disaster quake = firstOf(dz, "EARTHQUAKE");
        for (Disaster d : new Disaster[]{famine, plague, quake}) {
            if (d == null) {
                System.out.println("  (no disaster of this kind in the pack)");
                continue;
            }
            System.out.printf(Locale.ROOT, "  %s, %s, severity %.2f, reach %.0f km%n",
                    d.name(), d.yearLabel(), d.severity(), d.radiusKm());
        }
        if (famine != null) {
            int y = mid(famine);
            Situation grower = t.at(famine.lat(), famine.lon(), y, false, "farming", "christianity");
            Situation buyer = t.at(famine.lat(), famine.lon(), y, false, "trade", "christianity");
            double gf = grower.need("food").level();
            double bf = buyer.need("food").level();
            System.out.printf(Locale.ROOT, "    the grower's food %.2f, the buyer's %.2f%n", gf, bf);
            ok(gf < bf, "a famine should hit the grower harder than the buyer: " + gf + " vs " + bf);
            ok(gf < 0.95d, "a famine should move the needle at all: " + gf);
            ok(bf > 0.0d && bf <= 1.0d, "the buyer's food should still be a real number: " + bf);
        }

        // -------------------------------------------------- plague and earthquake are not the same
        System.out.println();
        System.out.println("--- two kinds of fear ---");
        if (plague != null && quake != null) {
            Situation p = t.at(plague.lat(), plague.lon(), mid(plague), false, "farming",
                    "christianity");
            Situation q = t.at(quake.lat(), quake.lon(), mid(quake), false, "farming",
                    "christianity");
            System.out.println("    after the sickness: " + p.need("safety").describe());
            System.out.println("    after the quake:    " + q.need("safety").describe());
            ok(p.need("safety").why().contains("nobody left to mend")
                    != q.need("safety").why().contains("nobody left to mend"),
                    "a plague and an earthquake should say different things");
            // faith rises where the sickness is
            Situation calm = t.at(plague.lat(), plague.lon(), mid(plague), false, "farming", "none");
            ok(p.need("faith").level() > calm.need("faith").level(),
                    "faith should be higher where the day stops to pray");
        }

        // -------------------------------------------------- a quiet place
        System.out.println();
        System.out.println("--- somewhere nothing is happening ---");
        int quiet = quietYear(dz, 51.51, -0.13);
        Situation calm = t.at(51.51, -0.13, quiet, false, "farming", "christianity");
        System.out.println("    London " + quiet + ": "
                + t.card(51.51, -0.13, quiet, false, "farming", "christianity").trim()
                        .replace("\n", " | "));
        ok(calm.pressing() == null, "a quiet year should have nothing pressing at London");
        ok(calm.need("food").level() > 0.95d, "food should be whole in a quiet year");
        ok(calm.need("safety").level() > 0.95d, "safety should be whole in a quiet year");

        // -------------------------------------------------- money is built from what can be seen
        System.out.println();
        System.out.println("--- money, which no register can source ---");
        Situation rich = t.at(51.51, -0.13, 2020, false, "scholar", "christianity");
        Situation poor = t.at(-3.10, -60.02, -9000, false, "foraging", "none");
        System.out.printf(Locale.ROOT, "    London 2020, a scholar: %.2f — %s%n",
                rich.need("money").level(), rich.need("money").why());
        System.out.printf(Locale.ROOT, "    Amazonia -9000, a forager: %.2f — %s%n",
                poor.need("money").level(), poor.need("money").why());
        ok(rich.need("money").level() > poor.need("money").level(),
                "a modern scholar should be better off than a Palaeolithic forager");

        // -------------------------------------------------- the five needs, worst first
        System.out.println();
        System.out.println("--- six people, as the game would show them ---");
        Object[][] people = {{"a farmer in London, 1348", 51.51, -0.13, 1348, false, "farming",
                "christianity"},
                {"a weaver in London, 1850", 51.51, -0.13, 1850, true, "craft", "christianity"},
                {"a ryot near Delhi, 1890", 28.61, 77.21, 1890, false, "farming", "hinduism"},
                {"a clerk in Hyderabad now", 17.39, 78.49, 2020, false, "official", "islam"},
                {"a herder near Timbuktu, 1400", 16.77, -3.01, 1400, false, "herding", "islam"},
                {"a hunter in Amazonia, -9000", -3.10, -60.02, -9000, false, "foraging", "none"}};
        for (Object[] p : people) {
            System.out.println("  " + p[0] + ":");
            System.out.println("    " + t.personLine((Double) p[1], (Double) p[2], (Integer) p[3],
                    (Boolean) p[4], (String) p[5], (String) p[6]));
        }

        // -------------------------------------------------- the town-situation reader
        System.out.println();
        System.out.println("--- the town-situation reader ---");
        Object[][] towns = {{"London", 51.51, -0.13, 1348, false, "farming", "christianity"},
                {"Cairo", 30.04, 31.24, 1000, false, "farming", "islam"},
                {"Beijing", 39.90, 116.41, 1700, false, "farming", "buddhism"},
                {"Lagos", 6.52, 3.38, 2020, false, "trade", "islam"}};
        for (Object[] w : towns) {
            System.out.println("  " + w[0] + " " + w[3] + ": " + t.line((Double) w[1],
                    (Double) w[2], (Integer) w[3], (Boolean) w[4], (String) w[5], (String) w[6]));
        }

        // -------------------------------------------------- the pressing disaster is real
        int checked = 0;
        for (Disaster d : dz.all()) {
            Disaster got = t.pressing(d.lat(), d.lon(), d.year());
            if (got != null) {
                checked++;
                if (!got.inForceIn(d.year()) || !got.reaches(d.lat(), d.lon())) {
                    failures.add("pressing disaster does not reach or is not in force");
                    System.out.println("FAIL  pressing disaster is not in force");
                    break;
                }
            }
        }
        ok(checked > 100, "only " + checked + " disasters were found pressing at their own place");

        System.out.println();
        System.out.println(failures.isEmpty() ? "ALL " + checks + " CHECKS PASSED"
                : failures.size() + " of " + checks + " CHECKS FAILED");
        for (String f : failures) {
            System.out.println("  - " + f);
        }
        return failures.isEmpty() ? 0 : 1;
    }

    private static Disaster firstOf(Disasters dz, String... kinds) {
        Disaster best = null;
        for (Disaster d : dz.all()) {
            for (String k : kinds) {
                if (d.kind().name().equals(k)) {
                    if (best == null || d.severity() > best.severity()) {
                        best = d;
                    }
                }
            }
        }
        return best;
    }

    private static int mid(Disaster d) {
        int end = d.endYear() == Disasters.NO_END ? d.year() : d.endYear();
        return d.year() + Math.max(0, (end - d.year()) / 2);
    }

    private static int quietYear(Disasters dz, double lat, double lon) {
        for (int y = 1700; y < 1900; y++) {
            boolean quiet = true;
            for (Disaster d : dz.all()) {
                if (d.inForceIn(y) && d.reaches(lat, lon)) {
                    quiet = false;
                    break;
                }
            }
            if (quiet) {
                return y;
            }
        }
        return 1750;
    }

    public static void main(String[] args) {
        System.exit(run());
    }
}
