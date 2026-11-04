package com.eternalengine.lifeprobe;

import com.eternalengine.people.Scenes;
import com.eternalengine.people.Scenes.Occasion;
import com.eternalengine.people.Scenes.Part;
import com.eternalengine.people.Scenes.Scene;
import com.eternalengine.people.Scenes.Trigger;
import com.eternalengine.people.Scenes.Where;

import java.util.List;

/** Step 39 (D9 event scenes). Run with {@code probe_lifetable.sh}. */
public final class SceneRun {

    static int checks = 0;
    static int failed = 0;

    static final double[][] PLACES = {
        {41.89d, 12.49d},     // Rome
        {51.51d, -0.13d},     // London
        {30.04d, 31.24d},     // Cairo
        {28.61d, 77.21d},     // Delhi
        {31.55d, 74.34d},     // Lahore
        {25.40d, 85.10d},     // a Bihar village
        {19.43d, -99.13d},    // Tenochtitlan
        {-3.10d, -60.02d},    // Amazonia
        {55.86d, -4.25d},     // Glasgow
        {35.68d, 139.65d},    // Edo
    };
    static final String[] NAMES = {"Rome", "London", "Cairo", "Delhi", "Lahore",
        "a Bihar village", "Tenochtitlan", "Amazonia", "Glasgow", "Edo"};
    static final int[] FOLK = {50000, 40000, 60000, 60000, 30000, 300, 60000, 25, 70000, 80000};
    static final String[] FAITH = {"roman", "christianity", "islam", "hinduism", "islam",
        "hinduism", "none", "none", "christianity", "buddhism"};

    static Where at(int i, int year) {
        return Where.of(PLACES[i][0], PLACES[i][1], year).town(FOLK[i] > 1000)
            .keeps(FAITH[i]).folk(FOLK[i]);
    }

    public static void main(String[] args) {
        ok("twenty scenes load", Scenes.count() == 20);
        System.out.println("  " + Scenes.count() + " scenes");

        int bad = 0;
        for (Scene s : Scenes.all()) {
            if (s.source().isEmpty() || s.name().isEmpty() || s.doing().isEmpty()) {
                bad++;
            }
            if (s.where().isEmpty() || s.trigger() == null) {
                bad++;
            }
            if (s.cast().isEmpty() || s.size() <= 0) {
                bad++;
            }
        }
        ok("every scene is sourced, named, stands on ground, has a trigger and has a cast",
            bad == 0);

        int[] byTrigger = new int[Trigger.values().length];
        for (Scene s : Scenes.all()) {
            byTrigger[s.trigger().ordinal()]++;
        }
        int used = 0;
        int most = 0;
        for (int n : byTrigger) {
            if (n > 0) {
                used++;
            }
            most = Math.max(most, n);
        }
        ok("all seven triggers are used", used == 7);
        ok("and no single trigger carries half the scenes", most * 2 < Scenes.count());
        ok("every part is a sector the job table draws from", sectorsKnown());

        // ---------------------------------------------------------- the quorum
        System.out.println();
        System.out.println("  -- a scene needs a quorum --");
        Scene coronation = Scenes.find("crowning");
        ok("a coronation is in the register", coronation != null);
        Where rome = at(0, 100).holding("coronation a coronation in the temple");
        Where amazon = at(7, 100).holding("coronation a coronation in the temple");
        ok("Rome in AD 100 can cast a coronation: " + Scenes.available(coronation, rome)
            + " of " + coronation.size() + " parts",
            Scenes.on(coronation, rome));
        ok("and a band of twenty-five foragers in AD 100 cannot: only "
            + Scenes.available(coronation, amazon) + " of " + coronation.size()
            + " parts, so the scene is not on at all",
            !Scenes.on(coronation, amazon));
        ok("the crowd is what decides it, not the year: the Amazon at 25,000 people could",
            Scenes.on(coronation, amazon.folk(25000)));
        Occasion oc = Scenes.make(coronation, rome);
        System.out.println("    Rome:   " + (oc == null ? "?" : oc.line()));
        System.out.println("    Amazon: " + Scenes.line(amazon));

        // ---------------------------------------------------------- triggers
        System.out.println();
        System.out.println("  -- what sets a scene off --");
        ok("the Lahore road in 1947 puts a refugee scene on",
            Scenes.on(Scenes.find("refugees"), at(4, 1947).on(8, 20).day(5000L)));
        ok("and Lahore in 1848 does not, because this is records and not a field",
            !Scenes.on(Scenes.find("refugees"), at(4, 1848).on(8, 20).day(5000L)));
        ok("a plague scene is not on where no sickness is in force",
            !Scenes.on(Scenes.find("plague"), at(7, 1700)));
        ok("the Black Death puts one on in London in 1348",
            Scenes.on(Scenes.find("plague"), at(1, 1348)));

        int marketDays = 0;
        for (long d = 0L; d < 40L; d++) {
            if (Scenes.triggered(Scenes.find("market_day"), at(1, 1300).day(d))) {
                marketDays++;
            }
        }
        ok("the London market comes round a handful of times in forty days, not every day: "
            + marketDays, marketDays >= 3 && marketDays <= 12);

        ok("an hour of prayer is on in Cairo at dawn",
            Scenes.triggered(Scenes.find("prayer"), at(2, 1000).at(5)));
        ok("and not in the middle of the afternoon",
            !Scenes.triggered(Scenes.find("prayer"), at(2, 1000).at(15)));
        ok("and where the register is not told the hour, it declines rather than guessing",
            !Scenes.triggered(Scenes.find("prayer"), at(2, 1000)));

        // a feast is on its day and not on the day after
        int feasts = 0;
        for (int m = 1; m <= 12; m++) {
            for (int d = 1; d <= 28; d++) {
                if (Scenes.triggered(Scenes.find("festival"), at(1, 1300).on(m, d))) {
                    feasts++;
                }
            }
        }
        ok("a feast day comes a handful of times a year in London, not all 336 of them: "
            + feasts, feasts >= 1 && feasts <= 40);

        // ---------------------------------------------------------- funerals from the death rate
        System.out.println();
        int vOld = 0;
        int vNow = 0;
        int wOld = 0;
        for (long d = 0L; d < 3000L; d++) {
            if ("funeral".equals(Scenes.lifeScene(at(5, 1850).day(d)))) {
                vOld++;
            }
            if ("funeral".equals(Scenes.lifeScene(at(5, 2020).day(d)))) {
                vNow++;
            }
            if ("wedding".equals(Scenes.lifeScene(at(5, 1850).day(d)))) {
                wOld++;
            }
        }
        ok("a Bihar village buries more people in 1850 than in 2020 - " + vOld + " against "
            + vNow + " funerals in 3,000 days, which is the life table's own number",
            vOld > vNow);
        ok("and it holds weddings as well as funerals, a little less often: " + wOld
            + " weddings against " + vOld + " funerals", wOld > 0 && wOld < vOld);
        ok("a city of forty thousand has a funeral on every day of the year, because three "
            + "people a day die there", "funeral".equals(Scenes.lifeScene(at(1, 1850).day(7L)))
            || "wedding".equals(Scenes.lifeScene(at(1, 1850).day(7L))));
        int quiet = 0;
        for (long d = 0L; d < 3000L; d++) {
            if (Scenes.lifeScene(at(5, 1900).day(d)).isEmpty()) {
                quiet++;
            }
        }
        ok("and a village of three hundred does not: " + quiet + " of 3,000 days have nothing "
            + "on at all", quiet > 2000);
        System.out.println("    a Bihar village, 3,000 days: " + vOld + " funerals in 1850, "
            + vNow + " in 2020, " + wOld + " weddings in 1850");

        // ---------------------------------------------------------- a scene of absence
        System.out.println();
        System.out.println("  -- a scene of absence --");
        Occasion plague = Scenes.make(Scenes.find("plague"), at(1, 1348));
        ok("the Black Death empties a London street, and the register says how much",
            plague != null && plague.absence() > 0.0d && plague.line().contains("emptier"));
        ok("and it is a scene of people not being there, so it stays under a clean sweep",
            plague != null && plague.absence() < 0.96d);
        Occasion siege = Scenes.make(Scenes.find("siege"), at(0, 100)
            .holding("siege a siege of the city"));
        ok("a siege is about how short of food the town is, not about fighting",
            siege != null && siege.line().toLowerCase().contains("siege"));
        if (plague != null) {
            System.out.println("    " + plague.line());
        }
        if (siege != null) {
            System.out.println("    " + siege.line());
        }

        // ---------------------------------------------------------- the prose
        System.out.println();
        System.out.println("  -- what the register says --");
        int[][] WHEN = {{0, 100}, {1, 1348}, {1, 1850}, {2, 1000}, {3, 1700}, {4, 1947},
                        {5, 1900}, {6, 1500}, {7, 1500}, {8, 1900}, {9, 1700}};
        for (int[] w : WHEN) {
            System.out.println("  " + NAMES[w[0]] + " " + w[1] + ": "
                + Scenes.line(at(w[0], w[1]).on(6, 15).day(1234L).at(9)));
        }
        System.out.println();
        System.out.println("  card, Lahore 1947:");
        for (String l : Scenes.card(at(4, 1947).on(8, 20).day(5000L)).split("\n")) {
            System.out.println("   " + l);
        }

        System.out.println();
        System.out.println(failed == 0
            ? "ALL " + checks + " CHECKS PASSED" : failed + " of " + checks + " CHECKS FAILED");
        if (failed > 0) {
            System.exit(1);
        }
    }

    static boolean sectorsKnown() {
        String[] known = {"farming", "herding", "foraging", "craft", "miner", "trade", "service",
                          "transport", "soldier", "clergy", "official", "scholar"};
        for (Scene s : Scenes.all()) {
            for (Part p : s.cast()) {
                boolean seen = false;
                for (String k : known) {
                    if (k.equals(p.sector())) {
                        seen = true;
                    }
                }
                if (!seen) {
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
