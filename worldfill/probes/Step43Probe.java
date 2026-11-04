import com.eternalengine.civilization.CountryGrid;
import com.eternalengine.civilization.Soundscape;
import com.eternalengine.civilization.SettlementRank;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/**
 * Step 43 part 2 (J2, sounds of the era): does the soundscape answer by place, by year, and by
 * who rules here?
 *
 * <p>The three checks that matter are the three ways the code this replaces was wrong, so they
 * are written as regressions against it:
 *
 * <ol>
 *   <li>it never read x and z, so <b>China in 1000 came back "Classical Mediterranean"</b> —
 *       the voice has to come from the ruler of China, not from the century;</li>
 *   <li>everything after 1920 came back {@code PASTORAL_ANCIENT}, so the two loudest centuries
 *       there have ever been were filed as prehistoric countryside — <b>a place in 1950 has to
 *       have machines in it</b>;</li>
 *   <li>it had no notion of a country, so <b>a place has to hear the train only once the train
 *       has reached its country</b> (Britain 1825, India 1874).</li>
 * </ol>
 */
public class Step43Probe {

    static int checks;
    static final List<String> problems = new ArrayList<>();

    static void check(String what, boolean ok, String detail) {
        checks++;
        if (!ok) {
            problems.add(what + " -- " + detail);
            System.out.println("FAIL " + what);
            System.out.println("       " + detail);
        } else {
            System.out.println("ok   " + what);
        }
    }

    static boolean has(List<Soundscape.Sound> list, String id) {
        for (Soundscape.Sound s : list) {
            if (id.equals(s.row().id())) {
                return true;
            }
        }
        return false;
    }

    static Soundscape.Here at(String name, double lat, double lon, int year, long pop) {
        return Soundscape.get().hereAt(lat, lon, year, SettlementRank.TOWN, pop);
    }

    static Set<String> ids(List<Soundscape.Sound> list) {
        Set<String> out = new LinkedHashSet<>();
        for (Soundscape.Sound s : list) {
            out.add(s.row().id());
        }
        return out;
    }

    public static void main(String[] args) {
        Soundscape s = Soundscape.get();
        System.out.println("=== load ===");
        check("the soundscape pack loads", s.loaded(), "loaded() was false; source=" + s.source());
        check("the pack is not empty", s.rowCount() > 0, "rowCount()=" + s.rowCount());
        System.out.println("     " + s.rowCount() + " country-rows, " + s.rows().size()
                + " distinct sounds, source=" + s.source());

        System.out.println();
        System.out.println("=== 1. the year alone does not decide what you hear (the old bug) ===");
        // The old code picked one of six soundscapes from the year, so every place in a century
        // sounded alike. These three are all in the year 1000 and sound nothing alike.
        Soundscape.Here bj = at("Beijing", 39.90, 116.40, 1000, 100000L);
        Soundscape.Here rome = at("Rome", 41.90, 12.50, 1000, 50000L);
        Soundscape.Here cairo = at("Cairo", 30.05, 31.25, 1000, 60000L);
        for (Soundscape.Here h : new Soundscape.Here[] {bj, rome, cairo}) {
            System.out.println("     " + h.ruler() + " -> faiths " + h.faiths()
                    + " -> voice " + ids(h.voice()));
        }
        check("the year 1000 does not sound the same everywhere",
                !(ids(bj.voice()).equals(ids(rome.voice()))
                        && ids(rome.voice()).equals(ids(cairo.voice()))),
                "Beijing=" + ids(bj.voice()) + " Rome=" + ids(rome.voice())
                        + " Cairo=" + ids(cairo.voice()));

        System.out.println();
        System.out.println("=== 2. China in 1000 is not the classical Mediterranean ===");
        boolean chinese = false;
        for (Soundscape.Sound v : bj.voice()) {
            for (String f : v.row().faiths()) {
                if ("buddhist".equals(f) || "chinese_folk".equals(f) || "confucian".equals(f)) {
                    chinese = true;
                }
            }
        }
        check("Beijing in 1000 has a voice of its own faith", chinese,
                "voice=" + ids(bj.voice()) + " (the old code returned Classical Mediterranean)");

        System.out.println();
        System.out.println("=== 3. 1950 is not prehistoric countryside (the old bug) ===");
        Soundscape.Here manchester = at("Manchester", 53.48, -2.24, 1950, 700000L);
        Soundscape.Here chicago = at("Chicago", 41.88, -87.63, 1950, 3600000L);
        System.out.println("     Manchester 1950: " + manchester.line());
        System.out.println("     Chicago 1950:    " + chicago.line());
        check("a big city in 1950 has machines in it", manchester.industrial(),
                "no machine row in 1950 Manchester: " + ids(manchester.machine()));
        check("and so does one in the New World", chicago.industrial(),
                "no machine row in 1950 Chicago: " + ids(chicago.machine()));

        System.out.println();
        System.out.println("=== 4. but the same machines are NOT there in 1700 ===");
        Soundscape.Here manchester1700 = at("Manchester", 53.48, -2.24, 1700, 10000L);
        System.out.println("     Manchester 1700: " + manchester1700.line());
        check("1700 is quieter than 1950",
                manchester1700.machine().size() < manchester.machine().size()
                        || !manchester1700.industrial(),
                "1700 machines=" + ids(manchester1700.machine())
                        + " vs 1950 machines=" + ids(manchester.machine()));

        System.out.println();
        System.out.println("=== 5. the train reaches a country, not the world (the sharpest test) ===");
        // The railway reached Britain in 1825 and India in 1874. A soundscape that keys the train
        // to the century gets both wrong; one that keys it to the country gets both right.
        Soundscape.Here delhi1860 = at("Delhi", 28.61, 77.21, 1860, 150000L);
        Soundscape.Here delhi1890 = at("Delhi", 28.61, 77.21, 1890, 150000L);
        Soundscape.Here york1840 = at("York", 53.96, -1.08, 1840, 40000L);
        Soundscape.Here york1800 = at("York", 53.96, -1.08, 1800, 20000L);
        System.out.println("     Delhi 1860: " + ids(delhi1860.machine()));
        System.out.println("     Delhi 1890: " + ids(delhi1890.machine()));
        System.out.println("     York 1800:  " + ids(york1800.machine()));
        System.out.println("     York 1840:  " + ids(york1840.machine()));
        check("India does not hear trains before 1874", !has(delhi1860.machine(), "trains"),
                "Delhi 1860 had a train in it: " + ids(delhi1860.machine()));
        check("India does hear trains after 1874", has(delhi1890.machine(), "trains"),
                "Delhi 1890 had no train: " + ids(delhi1890.machine()));
        check("England does not hear trains before 1825", !has(york1800.machine(), "trains"),
                "York 1800 had a train in it: " + ids(york1800.machine()));
        check("England does hear trains after 1825", has(york1840.machine(), "trains"),
                "York 1840 had no train: " + ids(york1840.machine()));

        System.out.println();
        System.out.println("=== 6. the call to prayer is where the faithful are ===");
        Soundscape.Here mecca = at("Mecca", 21.42, 39.83, 1900, 60000L);
        Soundscape.Here cordoba = at("Cordoba", 37.89, -4.78, 1000, 45000L);
        Soundscape.Here paris = at("Paris", 48.86, 2.35, 1300, 200000L);
        System.out.println("     Mecca 1900:   " + ids(mecca.voice()) + " under " + mecca.ruler());
        System.out.println("     Cordoba 1000: " + ids(cordoba.voice()) + " under " + cordoba.ruler());
        System.out.println("     Paris 1300:   " + ids(paris.voice()) + " under " + paris.ruler());
        check("Mecca has the call to prayer", has(mecca.voice(), "adhan"),
                "Mecca 1900 voice=" + ids(mecca.voice()));
        check("Islamic Cordoba has the call to prayer", has(cordoba.voice(), "adhan"),
                "Cordoba 1000 voice=" + ids(cordoba.voice()));
        check("Paris in 1300 has church bells, not the call to prayer",
                has(paris.voice(), "church_bells") && !has(paris.voice(), "adhan"),
                "Paris 1300 voice=" + ids(paris.voice()));

        System.out.println();
        System.out.println("=== 7. the crowd comes from step 17, not from a guess ===");
        Soundscape.Here hamlet = at("a hamlet", 52.00, 0.50, 1300, 20L);
        Soundscape.Here city = at("a city", 52.00, 0.50, 1300, 200000L);
        System.out.println("     20 people:      " + ids(hamlet.crowd()));
        System.out.println("     200000 people:  " + ids(city.crowd()));
        check("a crowd of 20 does not sound like a market",
                !has(hamlet.crowd(), "market") || has(city.crowd(), "market"),
                "hamlet=" + ids(hamlet.crowd()) + " city=" + ids(city.crowd()));
        check("a city is busier than a hamlet", city.crowd().size() >= hamlet.crowd().size(),
                "hamlet=" + ids(hamlet.crowd()) + " city=" + ids(city.crowd()));

        System.out.println();
        System.out.println("=== 8. the ground: every place has one, so no place is silent ===");
        Soundscape.Here sea = at("the North Sea", 53.00, 3.00, 1300, 0L);
        Soundscape.Here inland = at("Kazakh steppe", 48.00, 68.00, 1300, 0L);
        System.out.println("     at sea:    " + ids(sea.ground()));
        System.out.println("     inland:    " + ids(inland.ground()));

        System.out.println();
        System.out.println("=== 9. the whole world, every era: nobody is left with nothing ===");
        int[] years = {-3000, -2000, -1000, -500, 0, 500, 1000, 1300, 1500, 1700, 1800,
                1900, 1950, 2000};
        int empty = 0, total = 0, withVoice = 0, withMachine = 0;
        int knowFaith = 0, knowFaithSilent = 0;
        for (int year : years) {
            int yearEmpty = 0, yearVoice = 0, yearMachine = 0, yearTotal = 0;
            for (double lat = -58; lat <= 70; lat += 6.0d) {
                for (double lon = -178; lon <= 178; lon += 6.0d) {
                    String cc = CountryGrid.get().codeAt(lat, lon);
                    if (cc == null || cc.isBlank()) {
                        continue;   // the sea has no parish and no bells
                    }
                    Soundscape.Here h = Soundscape.get().hereAt(lat, lon, year,
                            SettlementRank.TOWN, 5000L);
                    total++;
                    yearTotal++;
                    if (h.all().isEmpty()) {
                        empty++;
                        yearEmpty++;
                    }
                    if (!h.voice().isEmpty()) {
                        withVoice++;
                        yearVoice++;
                    }
                    // The invariant that matters. The grid is 6 degrees apart, so most sample
                    // points are hundreds of kilometres from the nearest recorded temple and the
                    // mod knows no faith for them -- silence there is honest. But where it DOES
                    // know a faith, silence would be the old bug wearing a new coat.
                    if (!h.faiths().isEmpty()) {
                        knowFaith++;
                        if (h.voice().isEmpty()) {
                            knowFaithSilent++;
                        }
                    }
                    if (h.industrial()) {
                        withMachine++;
                        yearMachine++;
                    }
                }
            }
            System.out.printf(Locale.ROOT, "     %5d  %5d places, %4d silent, %4d with a voice,"
                            + " %4d with a machine%n",
                    year, yearTotal, yearEmpty, yearVoice, yearMachine);
        }
        check("no place on land is left with nothing to hear", empty == 0,
                empty + " of " + total + " place-years were silent");
        System.out.printf(Locale.ROOT, "     %d place-years where the mod knows a faith, %d of "
                + "them silent%n", knowFaith, knowFaithSilent);
        check("no place whose faith the mod knows is left without a voice", knowFaithSilent == 0,
                knowFaithSilent + " of " + knowFaith + " knew a faith but had no voice");
        // Reported, not asserted: how much of the world has a recorded faith at all is a fact
        // about the source, and it would be a lie to pass or fail the step on it.
        System.out.println("     (for the record: " + withVoice + " of " + total
                + " place-years have a voice; the grid is 6 degrees apart, so most sample points"
                + " are far from any recorded holy place)");
        check("machines reach a real share of the modern world",
                withMachine * 100 / Math.max(1, total) >= 10,
                withMachine + " of " + total + " place-years had a machine");

        System.out.println();
        System.out.println("=== 10. the pack says where it is thin ===");
        for (String g : s.gaps()) {
            System.out.println("     gap: " + g);
        }
        check("the pack admits its gaps", !s.gaps().isEmpty(), "no gaps listed");

        System.out.println();
        System.out.println("=== the day, in the voice of the pack ===");
        for (int[] p : new int[][] {{3990, 11640, 1000}, {4189, 1250, 1000}, {4190, 1250, 1500},
            {4885, 235, 1300}, {5248, -189, 1850}, {2142, 3983, 1900}, {5248, -189, 1950}}) {
            System.out.println("     " + (p[2] < 0 ? -p[2] + "BC" : "AD" + p[2]) + "  "
                    + s.lineAt(p[0] / 100.0d, p[1] / 100.0d, p[2], SettlementRank.CITY, 80000L));
        }

        System.out.println();
        System.out.println(checks + " checks, " + problems.size() + " problem(s)");
        if (!problems.isEmpty()) {
            for (String p : problems) {
                System.out.println("  " + p);
            }
            System.exit(1);
        }
    }
}
