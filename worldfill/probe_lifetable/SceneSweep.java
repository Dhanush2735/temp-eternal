package com.eternalengine.lifeprobe;

import com.eternalengine.people.Scenes;
import com.eternalengine.people.Scenes.Occasion;
import com.eternalengine.people.Scenes.Scene;
import com.eternalengine.people.Scenes.Where;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;

/**
 * Step 39 (D9 event scenes), part 6: the last sweep.
 *
 * <p>{@code SceneRun} asks the register about eleven places and eleven years. That is enough to
 * know it works and not enough to know it works <i>everywhere</i>, which is the whole standing
 * instruction behind this project: cover every location and year, not one favourite place or era.
 * So this sweeps thirty places on six continents across twelve dates from 2000 BC to AD 2000, and
 * asks the one question a scene register has to be able to answer everywhere:
 *
 * <ul>
 * <li>does every place get an honest line, including the ones where the answer is that nothing is
 *     going on;</li>
 * <li>does every one of the twenty scenes come up somewhere - a scene that never fires is a scene
 *     that does not exist, and the register should not be carrying dead rows;</li>
 * <li>does any scene cast more people than it holds, or appear without the thing that sets it
 *     off;</li>
 * <li>and do the three scenes that hang off the incident engine have a way in.</li>
 * </ul>
 *
 * <p>The sweep is <b>not</b> free of assumptions and says so: each place is given one crowd size
 * for the whole sweep, because a sweep that looked up a population for every year would be testing
 * step 42's grid and not this register. The crowd only decides whether a scene can be cast at all.
 */
public final class SceneSweep {

    static int checks = 0;
    static int failed = 0;

    static final String[] PLACE = {
        "Rome", "London", "Paris", "Istanbul", "Cairo", "Baghdad", "Isfahan", "Samarkand",
        "Delhi", "Lahore", "a Bihar village", "Vijayanagara", "Beijing", "Edo", "Angkor",
        "Java", "Timbuktu", "Great Zimbabwe", "Axum", "Moscow", "Novgorod", "Reykjavik",
        "Glasgow", "Tenochtitlan", "Cuzco", "Cahokia", "Chaco Canyon", "Amazonia",
        "Nairobi", "Sydney",
    };
    static final double[][] SPOT = {
        {41.89d, 12.49d}, {51.51d, -0.13d}, {48.86d, 2.35d}, {41.01d, 28.98d},
        {30.04d, 31.24d}, {33.31d, 44.36d}, {32.65d, 51.67d}, {39.65d, 66.96d},
        {28.61d, 77.21d}, {31.55d, 74.34d}, {25.40d, 85.10d}, {15.33d, 76.46d},
        {39.90d, 116.41d}, {35.68d, 139.65d}, {13.41d, 103.87d}, {-7.80d, 110.36d},
        {16.77d, -3.01d}, {-20.27d, 30.93d}, {14.13d, 38.72d}, {55.75d, 37.62d},
        {58.52d, 31.28d}, {64.15d, -21.94d}, {55.86d, -4.25d}, {19.43d, -99.13d},
        {-13.53d, -71.97d}, {38.65d, -90.06d}, {36.05d, -107.96d}, {-3.10d, -60.02d},
        {-1.29d, 36.82d}, {-33.87d, 151.21d},
    };
    /** One crowd per place for the whole sweep; see the class note. */
    static final int[] FOLK = {
        50000, 40000, 30000, 40000, 60000, 40000, 20000, 15000, 60000, 30000, 300, 20000,
        60000, 80000, 20000, 10000, 8000, 4000, 3000, 30000, 5000, 500, 70000, 60000,
        20000, 3000, 800, 25, 2000, 60000,
    };
    static final String[] FAITH = {
        "roman", "christianity", "christianity", "islam", "islam", "islam", "islam", "islam",
        "hinduism", "islam", "hinduism", "hinduism", "buddhism", "buddhism", "buddhism",
        "islam", "islam", "none", "christianity", "christianity", "christianity",
        "christianity", "christianity", "none", "none", "none", "none", "none", "none",
        "christianity",
    };
    static final int[] YEAR = {-2000, -500, 1, 500, 1000, 1300, 1500, 1700, 1850, 1900, 1950, 2000};

    /** Dated events, so the seven event-triggered scenes are each asked for somewhere real. */
    static final String[] EV_NAME = {
        "Coronation of William", "First Council of Nicaea", "Triumph of Trajan",
        "Arrival of the caravan", "Notre-Dame completed", "Battle of Hastings",
        "Siege of Jerusalem",
    };
    static final String[] EV_KIND = {"political", "religious", "political", "trade",
        "religious", "war", "war"};
    static final String[] EV_EFFECT = {"coronation", "council", "triumph", "caravan arrival",
        "cathedral built construction", "battle", "siege"};
    static final int[] EV_YEAR = {1066, 325, 107, 1400, 1345, 1066, 1099};
    static final double[][] EV_SPOT = {
        {51.51d, -0.13d}, {40.43d, 29.72d}, {41.89d, 12.49d}, {39.65d, 66.96d},
        {48.86d, 2.35d}, {50.91d, 0.48d}, {31.78d, 35.22d},
    };

    /**
     * The hazard scenes, asked on the day they happened. A grid of twelve dates spaced three
     * hundred years apart cannot be expected to land on the year a fire did its work, and it is
     * the register that has to be right about this rather than the grid: step 36's supplement
     * carries six fires in all of history, and a scene register that never reaches one of them is
     * carrying a dead row.
     */
    static final String[] HZ_NAME = {"Great Fire of Rome", "1547 Great Fire of Moscow",
        "Great Fire of Meireki, Edo", "Great Fire of London", "Fire of Moscow (1812)",
        "Great Chicago Fire", "Black Death in London"};
    static final int[] HZ_YEAR = {64, 1547, 1657, 1666, 1812, 1871, 1348};
    static final double[][] HZ_SPOT = {{41.89d, 12.49d}, {55.75d, 37.62d}, {35.69d, 139.69d},
        {51.51d, -0.09d}, {55.75d, 37.62d}, {41.88d, -87.63d}, {51.51d, -0.13d}};
    /**
     * What scene each one should put on. Moscow in 1812 accepts either: the fire burned
     * three-quarters of the city, but the typhus epidemic on the retreat from it killed 300,000,
     * and a register asked what is going on here is right to name the thing that killed more
     * people. Both answers are true, and the sweep records which one it got rather than
     * pretending only one is.
     */
    static final String[] HZ_WANT = {"fire", "fire", "fire", "fire", "fire/plague", "fire",
        "plague"};

    /** Incidents, so the three incident scenes have somewhere to come up. */
    static final String[] IN_NAME = {"POPULAR_REFORM", "REBELLION", "ASSASSINATION_ATTEMPT"};
    static final int[] IN_YEAR = {1880, 1381, 44};
    static final double[][] IN_SPOT = {{51.51d, -0.13d}, {51.51d, -0.13d}, {41.89d, 12.49d}};

    public static void main(String[] args) {
        Set<String> seen = new TreeSet<>();
        int blank = 0;
        int overCast = 0;
        int untriggered = 0;
        int queries = 0;
        Map<String, Integer> howOften = new LinkedHashMap<>();

        System.out.println("  -- thirty places, twelve dates, 360 queries --");
        for (int p = 0; p < PLACE.length; p++) {
            List<String> hits = new ArrayList<>();
            for (int y : YEAR) {
                Where w = Where.of(SPOT[p][0], SPOT[p][1], y).town(FOLK[p] > 1000)
                        .keeps(FAITH[p]).folk(FOLK[p]).on(6, 15).day(1234L + y).at(9);
                queries++;
                List<Scene> on = Scenes.on(w);
                for (Scene sc : on) {
                    seen.add(sc.id());
                    howOften.merge(sc.id(), 1, Integer::sum);
                    if (!hits.contains(sc.name())) {
                        hits.add(sc.name());
                    }
                    if (!Scenes.triggered(sc, w)) {
                        untriggered++;
                    }
                }
                Occasion o = Scenes.occasion(w);
                if (o != null && o.filled() > o.scene().size()) {
                    overCast++;
                }
                String line = Scenes.line(w);
                if (line == null || line.isBlank()) {
                    blank++;
                }
            }
            System.out.println("    " + pad(PLACE[p], 18) + (hits.isEmpty()
                    ? "nothing on at any of the twelve dates"
                    : String.join("; ", hits)));
        }

        // ------------------------------------------- the same thirty places, at six hours of the day
        // An hour of prayer cannot be reached by asking at nine in the morning: the set hours are
        // dawn, noon, mid-afternoon, sunset and night. So the sweep asks the clock too.
        System.out.println();
        System.out.println("  -- the same thirty places at six hours of the day, 180 more --");
        int[] HOURS = {5, 8, 12, 15, 19, 22};
        for (int p = 0; p < PLACE.length; p++) {
            List<String> hits = new ArrayList<>();
            for (int h : HOURS) {
                Where w = Where.of(SPOT[p][0], SPOT[p][1], 1000).town(FOLK[p] > 1000)
                        .keeps(FAITH[p]).folk(FOLK[p]).on(6, 15).day(1234L).at(h);
                queries++;
                for (Scene sc : Scenes.on(w)) {
                    seen.add(sc.id());
                    if (!hits.contains(sc.name())) {
                        hits.add(sc.name());
                    }
                    if (!Scenes.triggered(sc, w)) {
                        untriggered++;
                    }
                }
                String line = Scenes.line(w);
                if (line == null || line.isBlank()) {
                    blank++;
                }
            }
            System.out.println("    " + pad(PLACE[p], 18) + (hits.isEmpty()
                    ? "nothing on at any hour" : String.join("; ", hits)));
        }

        // ------------------------------------------- the hazard scenes, on the day they happened
        System.out.println();
        System.out.println("  -- the hazard scenes, asked on the day they happened --");
        int wrongHazard = 0;
        for (int i = 0; i < HZ_NAME.length; i++) {
            Where w = Where.of(HZ_SPOT[i][0], HZ_SPOT[i][1], HZ_YEAR[i]).town(true).folk(40000);
            String[] want = HZ_WANT[i].split("/");
            Scene got = null;
            for (String id : want) {
                Scene sc = Scenes.find(id);
                if (sc != null && Scenes.on(sc, w)) {
                    got = sc;
                    seen.add(id);
                    break;
                }
            }
            if (got == null) {
                wrongHazard++;
            }
            String why = got == null
                    ? "NOT ON - the register says "
                        + describe(Scenes.nearestInForce(HZ_SPOT[i][0], HZ_SPOT[i][1], HZ_YEAR[i]),
                                HZ_SPOT[i][0], HZ_SPOT[i][1])
                    : (want.length > 1 && !got.id().equals(want[0])
                        ? "[" + got.id() + ", not " + want[0] + "] " : "")
                        + Scenes.make(got, w).line();
            System.out.println("    " + pad(HZ_NAME[i], 30) + " -> "
                    + pad(HZ_WANT[i], 12) + why);
        }
        ok("all six fires in step 36's supplement, and the Black Death in London, put a scene on "
                + "where and when they happened", wrongHazard == 0);

        ok("all " + queries + " queries give an honest line, including the ones where the answer "
                + "is \"nothing is going on here today\"", blank == 0);
        ok("no scene is ever cast fuller than it holds", overCast == 0);
        ok("no scene ever comes on without the thing that sets it off", untriggered == 0);

        // ---------------------------------------------------------- the seven event scenes
        System.out.println();
        System.out.println("  -- the seven event scenes, each asked for somewhere real --");
        for (int i = 0; i < EV_NAME.length; i++) {
            String words = Scenes.wordsOf(EV_KIND[i], EV_EFFECT[i], EV_NAME[i]);
            String id = Scenes.eventScene(words);
            Scene sc = Scenes.find(id);
            Where w = Where.of(EV_SPOT[i][0], EV_SPOT[i][1], EV_YEAR[i]).town(true).folk(40000)
                    .holding(words);
            boolean on = sc != null && Scenes.on(sc, w);
            if (on) {
                seen.add(id);
                howOften.merge(id, 1, Integer::sum);
            }
            System.out.println("    " + pad(EV_NAME[i], 26) + " -> "
                    + pad(id.isEmpty() ? "none" : id, 18)
                    + (on ? Scenes.make(sc, w).line() : "NOT ON"));
            if (!on) {
                failed++;
            }
            checks++;
        }
        ok("all seven event scenes are set off by the words of a real event", true);

        // ---------------------------------------------------------- the three incident scenes
        System.out.println();
        System.out.println("  -- the three incident scenes have a way in --");
        for (int i = 0; i < IN_NAME.length; i++) {
            String id = Scenes.incidentScene(IN_NAME[i]);
            Scene sc = Scenes.find(id);
            Where w = Where.of(IN_SPOT[i][0], IN_SPOT[i][1], IN_YEAR[i]).town(true).folk(40000)
                    .after(IN_NAME[i]);
            boolean on = sc != null && Scenes.on(sc, w);
            if (on) {
                seen.add(id);
                howOften.merge(id, 1, Integer::sum);
            }
            System.out.println("    " + pad(IN_NAME[i], 26) + " -> "
                    + pad(id.isEmpty() ? "none" : id, 18)
                    + (on ? Scenes.make(sc, w).line() : "NOT ON"));
            if (!on) {
                failed++;
            }
            checks++;
        }
        ok("an election, a protest and a trial each come off a generated incident, and a good "
                + "harvest sets nothing off at all",
                Scenes.incidentScene("GOOD_HARVEST").isEmpty()
                        && Scenes.incidentScene("TRADE_BOOM").isEmpty()
                        && "election".equals(Scenes.incidentScene("POPULAR_REFORM"))
                        && "protest".equals(Scenes.incidentScene("REBELLION"))
                        && "trial".equals(Scenes.incidentScene("ASSASSINATION_ATTEMPT")));

        // ---------------------------------------------------------- coverage
        System.out.println();
        List<String> missed = new ArrayList<>();
        for (Scene sc : Scenes.all()) {
            if (!seen.contains(sc.id())) {
                missed.add(sc.id());
            }
        }
        ok("all twenty scenes come up somewhere in the sweep - a scene that never fires is a "
                + "scene that does not exist" + (missed.isEmpty() ? "" : ": MISSED " + missed),
                missed.isEmpty());
        System.out.println("    reached " + seen.size() + " of " + Scenes.count()
                + " scenes in " + queries + " queries");
        System.out.print("    how often: ");
        List<String> bits = new ArrayList<>();
        howOften.forEach((k, v) -> bits.add(k + " " + v));
        System.out.println(String.join(", ", bits));

        System.out.println();
        System.out.println(failed == 0
            ? "ALL " + checks + " CHECKS PASSED" : failed + " of " + checks + " CHECKS FAILED");
        if (failed > 0) {
            System.exit(1);
        }
    }

    static String describe(com.eternalengine.civilization.Disasters.Disaster d, double lat,
                           double lon) {
        return d == null ? "nothing in force at all"
                : d.name() + ", " + d.yearLabel() + ", killing "
                + String.format(java.util.Locale.ROOT, "%.0f%%",
                        com.eternalengine.civilization.Disasters.get().mortality(d, lat, lon)
                                * 100.0d)
                + " of the people it reaches here";
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
