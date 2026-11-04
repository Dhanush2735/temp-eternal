package com.eternalengine.lifeprobe;

import com.eternalengine.war.Army;
import com.eternalengine.war.Sieges;
import com.eternalengine.war.Sieges.Ending;
import com.eternalengine.war.Sieges.Method;
import com.eternalengine.war.Sieges.Siege;
import com.eternalengine.war.Sieges.Town;
import com.eternalengine.war.Sieges.Wall;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Step 40 (D10 armies in action), part 4: the siege register.
 *
 * <p>The old {@code SiegeEngineController} picked a random block near the target every five
 * seconds and cracked it, gravelised it or deleted it. No food, no water, no disease, no relieving
 * army, no negotiation, no date it had to end, and no way it ended at all.
 *
 * <p>The four claims this probe holds the new register to:
 *
 * <ul>
 * <li><b>a siege is a race between two clocks</b>, the wall's and the food's, and the register has
 *     to land on the dates the record kept;</li>
 * <li><b>the commonest ending is the one nobody guesses</b> - a town taken by force could be sacked
 *     and one that surrendered could not, so most sieges ended in an agreement;</li>
 * <li><b>the ground decides what is possible</b> - a mine through rock or under water is not a
 *     slower mine, it is no mine at all, and a place that cannot be reached cannot be breached;</li>
 * <li><b>and the timetable changes</b> - what a mine did in weeks and hunger did in months, a
 *     battery did in days.</li>
 * </ul>
 */
public final class SiegeRun {

    static int checks = 0;
    static int failed = 0;

    public static void main(String[] args) {
        ok("the siege register loads: " + Sieges.wallCount() + " kinds of wall, "
            + Sieges.methods().size() + " methods and " + Sieges.endings().size() + " endings",
            Sieges.wallCount() == 11 && Sieges.methods().size() == 10
                && Sieges.endings().size() == 5);

        System.out.println();
        System.out.println("  -- what they were standing behind --");
        String[] PLACE = {"Megiddo", "Syracuse", "Pingyao", "Rochester", "Kenilworth",
            "Constantinople", "Constantinople", "Rome", "Antwerp", "Vicksburg", "Leningrad",
            "Sarajevo", "a Mississippian town"};
        double[][] SPOT = {{32.0d, 35.0d}, {37.0d, 15.0d}, {37.0d, 112.0d}, {51.0d, 0.5d},
            {52.0d, -1.5d}, {41.0d, 29.0d}, {41.0d, 29.0d}, {41.9d, 12.5d}, {51.0d, 4.0d},
            {32.0d, -90.0d}, {59.9d, 30.3d}, {43.8d, 18.3d}, {38.6d, -90.1d}};
        int[] YEAR = {-1450, -213, 1500, 1215, 1266, 1200, 1453, 1400, 1585, 1863, 1942, 1993,
            1100};
        String[] WANT = {"mudbrick", "ashlar", "rammed_earth", "curtain_and_tower",
            "curtain_and_tower", "theodosian", "theodosian", "curtain_and_tower",
            "trace_italienne", "field_entrenchment", "modern_city", "modern_city", "earthwork"};
        int wrong = 0;
        for (int i = 0; i < PLACE.length; i++) {
            Wall w = Sieges.wallAt(SPOT[i][0], SPOT[i][1], YEAR[i]);
            boolean good = w != null && w.id().equals(WANT[i]);
            if (!good) {
                wrong++;
            }
            System.out.println("    " + pad(PLACE[i], 16) + pad(Integer.toString(YEAR[i]), 6)
                + (w == null ? "NO ANSWER" : w.name())
                + (good ? "" : "   << wanted " + WANT[i]));
        }
        ok("every place and year gets the fortification the record says it had", wrong == 0);

        System.out.println();
        System.out.println("  -- what a besieger could do, and when --");
        for (int y : new int[] {-200, 1200, 1400, 1453, 1500, 1700, 1900}) {
            StringBuilder sb = new StringBuilder();
            for (Method m : Sieges.methodsInForce(y)) {
                sb.append(sb.length() == 0 ? "" : ", ").append(m.id());
            }
            System.out.println("    " + pad(Integer.toString(y), 6) + sb);
        }
        List<String> in1400 = ids(Sieges.methodsInForce(1400));
        List<String> in1453 = ids(Sieges.methodsInForce(1453));
        List<String> in1700 = ids(Sieges.methodsInForce(1700));
        ok("a besieger of 1453 has something a besieger of 1400 lacked: " + minus(in1453, in1400),
            !minus(in1453, in1400).isEmpty());
        ok("and a besieger of 1700 has something a besieger of 1453 lacked: "
            + minus(in1700, in1453), !minus(in1700, in1453).isEmpty());

        System.out.println();
        System.out.println("  -- does it land on the dates the record kept? --");
        int roch = Sieges.daysToBreach(wall("curtain_and_tower"),
            town("Rochester", 51.0d, 0.5d, 400L, 100L, 90, 60, 10, "dry"),
            army("john", 51.0d, 0.5d, 900L, 65, 55), 1215);
        int konst = Sieges.daysToBreach(wall("theodosian"),
            town("Constantinople", 41.0d, 29.0d, 50000L, 7000L, 180, 96, 40, "dry"),
            army("mehmed", 41.0d, 29.0d, 80000L, 80, 80), 1453);
        int vicks = Sieges.daysToBreach(wall("field_entrenchment"),
            town("Vicksburg", 32.0d, -90.0d, 34000L, 30000L, 60, 55, 5, "dry"),
            army("grant", 32.0d, -90.0d, 70000L, 75, 85), 1863);
        int kenil = Sieges.daysToBreach(wall("curtain_and_tower"),
            town("Kenilworth", 52.0d, -1.5d, 1300L, 1200L, 120, 60, 10, "wet"),
            army("henry", 52.0d, -1.5d, 1800L, 60, 50), 1266);
        System.out.println("    Rochester 1215, mined:            " + show(roch)
            + "   record: 11 Oct to 30 Nov, about 50");
        System.out.println("    Constantinople 1453, bombarded:   " + show(konst)
            + "   record: 6 April to 29 May, 53 days");
        System.out.println("    Vicksburg 1863, entrenched:       " + show(vicks)
            + "   record: 18 May to 4 July, 47 days");
        System.out.println("    Kenilworth 1266, ringed by water: " + show(kenil)
            + "   record: no breach was ever made; 172 days of hunger");
        ok("Constantinople's wall falls in the register at about the date it fell: " + konst
            + " days against 53", Math.abs(konst - 53) <= 12);
        ok("Rochester's mine takes about as long as it took: " + roch + " days against 50",
            Math.abs(roch - 50) <= 15);
        ok("Vicksburg's entrenchments hold about as long as they held: " + vicks
            + " days against 47", Math.abs(vicks - 47) <= 18);
        // Kenilworth could not be mined, and no ram, tower or engine could be brought within
        // reach of it: the register's trebuchet needs 615 days, which is no answer at all next to
        // a garrison with 120 days of bread. That is the claim - hunger decided it, not the wall.
        int kenilFood = 120 + 120;
        ok("Kenilworth's wall clock is no answer next to its food clock: " + show(kenil)
            + " against about " + kenilFood + " days of bread, so the mere decided it and hunger "
            + "finished it", kenil == Sieges.NO_BREACH || kenil > kenilFood * 2);
        // and somewhere the register does say that nothing can be done at all
        int unreachable = Sieges.daysToBreach(wall("curtain_and_tower"),
            town("a marsh castle", 52.0d, -1.5d, 900L, 400L, 120, 60, 10, "wet"),
            army("a neighbour", 52.0d, -1.5d, 1200L, 60, 50), 1100);
        ok("before the trebuchet, a castle ringed by water cannot be breached by anything: "
            + show(unreachable), unreachable == Sieges.NO_BREACH);

        System.out.println();
        System.out.println("  -- the same castle on three kinds of ground, 1266 --");
        int dryD = Sieges.daysToBreach(wall("curtain_and_tower"),
            town("Kenilworth", 52.0d, -1.5d, 1300L, 1200L, 120, 60, 10, "dry"),
            army("henry", 52.0d, -1.5d, 1800L, 60, 50), 1266);
        int rockD = Sieges.daysToBreach(wall("curtain_and_tower"),
            town("Kenilworth", 52.0d, -1.5d, 1300L, 1200L, 120, 60, 10, "rock"),
            army("henry", 52.0d, -1.5d, 1800L, 60, 50), 1266);
        System.out.println("    dry ground, a mine is possible:   " + show(dryD));
        System.out.println("    living rock, no mine:             " + show(rockD));
        System.out.println("    water all round, nothing reaches: " + show(kenil));
        ok("a mine through living rock is not a slower mine, it is no mine at all: " + show(dryD)
            + " against " + show(rockD), dryD > 0 && (rockD == Sieges.NO_BREACH || rockD > dryD));
        ok("and a place nothing can be brought up against has no wall clock worth the name: "
            + show(kenil) + " against " + show(dryD) + " for the same wall on dry ground",
            kenil > dryD * 2);
        Wall concentric = wall("concentric");
        ok("a concentric castle can be named by a caller who knows, and never guessed from a "
            + "latitude: the register admits it cannot tell Krak des Chevaliers from a curtain "
            + "wall by map reference alone",
            concentric != null && "special".equals(concentric.scope())
                && !concentric.equals(Sieges.wallAt(52.0d, -1.5d, 1266)));
        Wall trace = wall("trace_italienne");
        ok("the trace italienne is LOW, which is the whole point of it - it stopped building "
            + "upward and started building outward - and that is why it needs a ditch and a glacis "
            + "rather than height", trace != null && trace.low());
        ok("so ladders are on the table against a trace italienne and are not against a medieval "
            + "curtain: " + usable("escalade", trace, "dry") + " against "
            + usable("escalade", wall("curtain_and_tower"), "dry"),
            usable("escalade", trace, "dry")
                && !usable("escalade", wall("curtain_and_tower"), "dry"));

        System.out.println();
        System.out.println("  -- the five ways it stops, over 480 sieges --");
        Map<String, Integer> tally = new LinkedHashMap<>();
        for (Ending e : Sieges.endings()) {
            tally.put(e.id(), 0);
        }
        int sacked = 0;
        int total = 0;
        for (int i = 0; i < 480; i++) {
            int k = i % PLACE.length;
            int year = YEAR[k] + (i / PLACE.length) * 40;
            long mouths = 2000L + (i * 7919L) % 40000L;
            long garrison = Math.max(200L, mouths / 6L + (i * 31L) % 900L);
            Town t = town(PLACE[k], SPOT[k][0], SPOT[k][1], mouths, garrison,
                20 + (i * 13) % 300, 10 + (i * 17) % 80, (i * 7) % 70,
                i % 3 == 0 ? "dry" : i % 3 == 1 ? "rock" : "wet");
            Army a = army("besieger", SPOT[k][0], SPOT[k][1],
                Math.max(500L, garrison * (1L + (i % 7))), 40 + (i * 11) % 55,
                20 + (i * 23) % 75);
            int relief = i % 5 == 0 ? 30 + (i * 3) % 400 : -1;
            Siege s = Sieges.besiege(t, a, year, relief, 9000L + i);
            if (s == null) {
                continue;
            }
            total++;
            tally.merge(s.endingId(), 1, Integer::sum);
            if (s.sacked()) {
                sacked++;
            }
        }
        for (Map.Entry<String, Integer> e : tally.entrySet()) {
            Ending en = Sieges.ending(e.getKey());
            System.out.println("    " + pad(e.getKey(), 13) + pad(e.getValue().toString(), 6)
                + (en == null ? "" : en.name()) + (en != null && en.sack() ? "  * sacks it" : ""));
        }
        int terms = tally.getOrDefault("terms", 0);
        int storm = tally.getOrDefault("storm", 0);
        int starve = tally.getOrDefault("starvation", 0);
        ok("all five endings come up in a real spread of sieges: " + endingsSeen(tally) + " of 5",
            endingsSeen(tally) == 5);
        ok("and the commonest is the one nobody guesses - terms, not storm: " + terms + " against "
            + storm, terms > storm);
        ok("most sieges end without the town being sacked: " + (total - sacked) + " of " + total,
            (total - sacked) * 2 > total);
        ok("a storm stays rarer than a surrender, because it is the ending that costs "
            + "everything: " + storm + " against " + terms, storm < terms);
        ok("and a starved garrison is not a rare thing either: " + starve + " of " + total,
            starve > 0);

        System.out.println();
        System.out.println("  -- what it costs to wait one more day --");
        Town aTown = town("a town", 41.0d, 29.0d, 30000L, 4000L, 120, 60, 20, "dry");
        Army anArmy = army("besiegers", 41.0d, 29.0d, 24000L, 70, 70);
        Siege withHelp = Sieges.besiege(aTown, anArmy, 1400, 60, 4242L);
        Siege noHelp = Sieges.besiege(aTown, anArmy, 1400, -1, 4242L);
        Siege tooLate = Sieges.besiege(aTown, anArmy, 1400, 400, 4242L);
        System.out.println("    with a relief promised for day 60:  " + withHelp.days() + " days, "
            + withHelp.endingId() + ", " + withHelp.dead() + " dead");
        System.out.println("    with no help coming:                " + noHelp.days() + " days, "
            + noHelp.endingId() + ", " + noHelp.dead() + " dead");
        System.out.println("    with a relief promised for day 400: " + tooLate.days()
            + " days, " + tooLate.endingId() + ", " + tooLate.dead() + " dead");
        ok("help arriving in time lifts the siege, and the town keeps everything: "
            + withHelp.endingId(), "relief".equals(withHelp.endingId()));
        ok("help promised for a day that never comes is no help at all: " + tooLate.endingId()
            + " on day " + tooLate.days(),
            !"relief".equals(tooLate.endingId()) && tooLate.days() < 400);
        ok("a town that surrenders keeps its people; one carried by assault loses them: "
            + withHelp.endingId() + " sacks it " + withHelp.sacked(), !withHelp.sacked());

        System.out.println();
        System.out.println("  -- the useless mouths --");
        // Alesia, 52 BC: Vercingetorix put the women, the children and the old out of the
        // oppidum to make the bread last, and Caesar would not let them through his lines. They
        // died between the two armies. It is the recorded case, and it is in the register.
        Town alesia = town("Alesia", 47.5d, 4.5d, 80000L, 30000L, 20, 60, 0, "rock");
        Army caesar = army("caesar", 47.5d, 4.5d, 50000L, 70, 60);
        Siege sienaRun = Sieges.besiege(alesia, caesar, -52, -1, 777L);
        System.out.println("    Alesia, 52 BC: " + sienaRun.days() + " days, ends in "
            + sienaRun.endingId());
        System.out.println("    " + sienaRun.expelled() + " put out of the gates, "
            + sienaRun.dead() + " dead, " + sienaRun.mouthsNow() + " of " + sienaRun.mouths0()
            + " left");
        ok("a commander with the stomach for it puts the useless mouths out: "
            + sienaRun.expelled() + " of " + sienaRun.mouths0(),
            sienaRun.expelled() > 0 && sienaRun.expelled() < sienaRun.mouths0() / 2L);
        ok("and the register says what became of them: over half died in the ditch between the two "
            + "armies", sienaRun.line().contains("died in the ditch"));
        double stretch = 1.0d / (1.0d - Sieges.uselessShare());
        System.out.println("    putting out " + String.format("%.0f",
            Sieges.uselessShare() * 100.0d) + " of the mouths stretches the bread by "
            + String.format("%.2fx", stretch));
        ok("the stretch is arithmetic, not a number somebody liked: "
            + String.format("%.2fx", stretch), Math.abs(stretch - Sieges.uselessGain()) < 0.02d);

        System.out.println();
        System.out.println("  -- what the register says --");
        String[] EVENT = {"Rochester, 1215", "Kenilworth, 1266", "Constantinople, 1453",
            "Vicksburg, 1863", "Leningrad, 1941", "Sarajevo, 1992"};
        Town[] TOWN = {
            town("Rochester", 51.0d, 0.5d, 400L, 100L, 90, 60, 10, "dry"),
            town("Kenilworth", 52.0d, -1.5d, 1300L, 1200L, 120, 60, 10, "wet"),
            town("Constantinople", 41.0d, 29.0d, 50000L, 7000L, 180, 96, 40, "dry"),
            town("Vicksburg", 32.0d, -90.0d, 34000L, 30000L, 60, 55, 5, "dry"),
            town("Leningrad", 59.9d, 30.3d, 2900000L, 200000L, 35, 92, 88, "wet"),
            town("Sarajevo", 43.8d, 18.3d, 380000L, 40000L, 30, 92, 90, "rock")};
        Army[] ARMY = {
            army("john", 51.0d, 0.5d, 900L, 65, 55),
            army("henry", 52.0d, -1.5d, 1800L, 60, 50),
            army("mehmed", 41.0d, 29.0d, 80000L, 80, 80),
            army("grant", 32.0d, -90.0d, 70000L, 75, 85),
            army("leeb", 59.9d, 30.3d, 700000L, 80, 90),
            army("vrs", 43.8d, 18.3d, 13000L, 75, 80)};
        int[] WHEN = {1215, 1266, 1453, 1863, 1941, 1992};
        int[] HELP = {-1, -1, -1, -1, 872, 1425};
        for (int i = 0; i < EVENT.length; i++) {
            Siege s = Sieges.besiege(TOWN[i], ARMY[i], WHEN[i], HELP[i], 31337L + i);
            System.out.println("  " + EVENT[i] + ":");
            System.out.println("    " + s.line());
        }

        System.out.println();
        System.out.println("  card, Constantinople 1453:");
        for (String l : Sieges.card(TOWN[2], ARMY[2], 1453, -1, 5L).split("\n")) {
            System.out.println("   " + l);
        }

        System.out.println();
        System.out.println(failed == 0
            ? "ALL " + checks + " CHECKS PASSED" : failed + " of " + checks + " CHECKS FAILED");
        if (failed > 0) {
            System.exit(1);
        }
    }

    // ================================================================== helpers

    static Town town(String n, double lat, double lon, long mouths, long gar, int food,
                     int morale, int supply, String ground) {
        return new Town(n, lat, lon, mouths, gar, food, morale, supply, ground);
    }

    static Army army(String id, double lat, double lon, long size, int morale, int supply) {
        return new Army(id, "besiegers", lat, lon, size, morale, supply, "ERA", 18.0d);
    }

    static List<String> ids(List<Method> ms) {
        List<String> out = new ArrayList<>();
        for (Method m : ms) {
            out.add(m.id());
        }
        return out;
    }

    static String minus(List<String> a, List<String> b) {
        StringBuilder sb = new StringBuilder();
        for (String s : a) {
            if (!b.contains(s)) {
                sb.append(sb.length() == 0 ? "" : ", ").append(s);
            }
        }
        return sb.toString();
    }

    static Wall wall(String id) {
        for (Wall w : Sieges.walls()) {
            if (w.id().equals(id)) {
                return w;
            }
        }
        return null;
    }

    static boolean usable(String method, Wall w, String ground) {
        for (Method m : Sieges.methods()) {
            if (m.id().equals(method)) {
                return Sieges.usable(m, w,
                    new Town("t", w.box()[0], w.box()[2], 1000L, 500L, 60, 50, 0, ground));
            }
        }
        return false;
    }

    static int endingsSeen(Map<String, Integer> tally) {
        int n = 0;
        for (Integer v : tally.values()) {
            if (v > 0) {
                n++;
            }
        }
        return n;
    }

    static String show(int days) {
        return days == Sieges.NO_BREACH ? "no breach possible" : days + " days";
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
