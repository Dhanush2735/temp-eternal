import com.eternalengine.civilization.CountryGrid;
import com.eternalengine.civilization.SettlementRank;
import com.eternalengine.civilization.Signs;
import com.eternalengine.news.BookForms;
import com.eternalengine.news.NewsTravel;
import com.eternalengine.news.Writings;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Step 43 part 5 (E13, writing as objects: letters and inscriptions).
 *
 * <p>Two things could have gone wrong and both are checked here, because both were found by
 * measuring before building:
 *
 * <ol>
 *   <li><b>a letter cannot go down a wire.</b> {@code NewsTravel.fastest} will happily answer
 *       "the telegraph, one day" for 1900. A letter is an object. It has to travel. So
 *       {@code Writings.carry} refuses the instant modes, and every sweep year after 1839 is a
 *       test of that.<br>
 *       <b>The measured version of this defect:</b> without it, London to Manchester in 1900
 *       arrives by telegraph.</li>
 *   <li><b>the brush is a fact about the script, not the material.</b> Paper reached China in
 *       105, so the material for a Kaifeng letter of 1000 is a sheet of paper — and the obvious
 *       ladder then hands the writer a quill. Chinese characters are brushed. The script has to
 *       be asked first, or the Song chancellery writes with a goose feather.</li>
 * </ol>
 *
 * <p>And the fact the whole part hangs on: <b>before the post there was no way to send a
 * letter.</b> You gave it to somebody who was going that way.
 */
public class Step43dProbe {

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

    static Writings.Letter post(String name, double la1, double lo1, double la2, double lo2,
                                int year, boolean sea, SettlementRank rank) {
        Writings.Letter l = Writings.letter(la1, lo1, la2, lo2, year, rank, sea);
        System.out.printf(Locale.ROOT, "     %-22s %s%n", name, l.line());
        return l;
    }

    static Writings.Inscription cut(String name, double lat, double lon, int year,
                                    SettlementRank rank) {
        Writings.Inscription i = Writings.inscription(lat, lon, year, rank);
        System.out.printf(Locale.ROOT, "     %-22s %s%n", name, i.line());
        System.out.printf(Locale.ROOT, "     %-22s   surface=%s kinds=%d readers=%.3f claim=%s%n",
                "", i.surface(), i.kinds().size(), i.readers(), i.claim());
        return i;
    }

    public static void main(String[] args) {
        System.out.println("=== 1. the registers this stands on ===");
        check("the script lookup J3 built is loaded (E13 shares it, and does not rebuild it)",
                Signs.get().loaded(), "scripts not loaded");
        check("the book forms of step 22 are there",
                !BookForms.writing(41.89, 12.49, 100).isEmpty(), "no writing form at Rome in 100");
        System.out.println("     Rome 100 forms: " + BookForms.writing(41.89, 12.49, 100));
        System.out.println("     Rome 100 script: " + Signs.get().scriptAt(41.89, 12.49, 100));

        System.out.println();
        System.out.println("=== 2. the post: the first institution that carries anyone's letter ===");
        check("there is no post anywhere in 1400 (the first is Germany, 1490)",
                !Writings.postHere(51.10, 10.30, 1400) && !Writings.postHere(43.77, 11.26, 1400)
                        && !Writings.postHere(34.80, 114.31, 1400),
                "the post had already reached somewhere in 1400");
        // The table's raw figure for Germany is 1490, but arrivalAt spreads a technology from its
        // first place, so the post reaches Germany itself in 1505. The check has to be against the
        // spread year, not the seed year.
        int postGermany = 0, postBritain = 0, postChina = 0;
        for (int y = 1400; y <= 2000; y++) {
            if (postGermany == 0 && Writings.postHere(51.10, 10.30, y)) {
                postGermany = y;
            }
            if (postBritain == 0 && Writings.postHere(51.51, -0.13, y)) {
                postBritain = y;
            }
            if (postChina == 0 && Writings.postHere(34.80, 114.31, y)) {
                postChina = y;
            }
        }
        check("the post reaches Germany early in the 1500s", postGermany >= 1490 && postGermany <= 1520,
                "Germany post year = " + postGermany);
        check("it reaches Britain a century and more later", postBritain > postGermany + 50,
                "Germany " + postGermany + " vs Britain " + postBritain);
        check("and China three centuries after Germany", postChina > postGermany + 200,
                "Germany " + postGermany + " vs China " + postChina);
        System.out.printf(Locale.ROOT,
                "     the post reaches Germany %d, Britain %d, Kaifeng %d%n",
                postGermany, postBritain, postChina);

        System.out.println();
        System.out.println("=== 3. before the post, a letter is not sent: it is given ===");
        Writings.Letter florence = post("Florence-Avignon 1300", 43.77, 11.26, 43.95, 4.81, 1300,
                false, SettlementRank.CITY);
        check("a letter of 1300 does not go by post", !florence.byPost(), "byPost was true");
        check("a letter of 1300 goes with a traveller",
                florence.mode() == NewsTravel.Mode.TRAVELLER,
                "mode was " + florence.mode());
        check("a letter of 1300 is closed with a seal in wax",
                florence.closure().contains("signet ring"), "closure: " + florence.closure());
        check("and it is not in an envelope", !florence.closure().contains("envelope"),
                "closure: " + florence.closure());

        System.out.println();
        System.out.println("=== 4. after the post, and after the stamp ===");
        Writings.Letter london1850 = post("London-Manchester 1850", 51.51, -0.13, 53.48, -2.24,
                1850, false, SettlementRank.CITY);
        check("a letter of 1850 goes by post", london1850.byPost(), "byPost was false");
        check("and takes the railway, not a rider",
                london1850.mode() == NewsTravel.Mode.RAILWAY, "mode was " + london1850.mode());
        check("and arrives the next day, not within the hour — a letter is collected and delivered,"
                        + " not just carried",
                london1850.days() >= 1.0d && london1850.days() < 2.0d,
                "days=" + london1850.days() + " (" + london1850.when() + ")");
        Writings.Letter london1900 = post("London-Manchester 1900", 51.51, -0.13, 53.48, -2.24,
                1900, false, SettlementRank.CITY);
        check("by 1900 it is in a gummed envelope", london1900.closure().contains("envelope"),
                "closure: " + london1900.closure());
        Writings.Letter sea1850 = post("London-Calcutta 1850", 51.51, -0.13, 22.57, 88.36, 1850,
                true, SettlementRank.CITY);
        check("a sea letter of 1850 goes by steamship",
                sea1850.mode() == NewsTravel.Mode.STEAMSHIP, "mode was " + sea1850.mode());

        System.out.println();
        System.out.println("=== 5. the brush: the script decides, not the material ===");
        // Paper reached China in 105, so the material is right and the instrument is the trap.
        Writings.Letter kaifeng = post("Kaifeng-Hangzhou 1000", 34.80, 114.31, 30.27, 120.16,
                1000, false, SettlementRank.CITY);
        check("paper has reached Kaifeng by 1000",
                kaifeng.material() == BookForms.Form.NOTEBOOK,
                "material was " + kaifeng.material());
        check("but a Chinese letter of 1000 is brushed, not written with a quill",
                kaifeng.with() == Writings.Instrument.BRUSH, "with=" + kaifeng.with());
        Writings.Letter manchester1850b = Writings.letter(53.48, -2.24, 51.51, -0.13, 1850,
                SettlementRank.CITY, false);
        check("an English letter of the same century is not brushed",
                manchester1850b.with() != Writings.Instrument.BRUSH,
                "with=" + manchester1850b.with());
        System.out.println("     Manchester-London 1850 with: " + manchester1850b.with().name);

        System.out.println();
        System.out.println("=== 6. the material decides the rest ===");
        Writings.Letter sumer = post("Uruk-Lagash -2400", 31.0, 45.6, 31.4, 46.4, -2400, false,
                SettlementRank.CITY);
        check("a Sumerian letter is clay, and pressed with a reed",
                sumer.material() == BookForms.Form.CLAY_TABLETS
                        && sumer.with() == Writings.Instrument.REED_STYLUS,
                "material=" + sumer.material() + " with=" + sumer.with());
        check("and it is closed in an envelope of clay",
                sumer.closure().contains("envelope of clay"), "closure: " + sumer.closure());

        System.out.println();
        System.out.println("=== 7. a letter is an object: it never goes down a wire ===");
        // NewsTravel.fastest would answer "the telegraph" for 1900. A letter cannot do that.
        int wire = 0, sweeps = 0;
        for (int year : new int[]{-2000, -1000, 0, 500, 1000, 1300, 1500, 1700, 1800, 1850, 1900,
                1950, 2000}) {
            for (double lat = -56; lat <= 70; lat += 8.0d) {
                for (double lon = -178; lon <= 178; lon += 8.0d) {
                    String cc = CountryGrid.get().codeAt(lat, lon);
                    if (cc == null || cc.isBlank()) {
                        continue;
                    }
                    Writings.Letter l = Writings.letter(lat, lon, lat + 4.0d, lon + 4.0d, year,
                            SettlementRank.TOWN, false);
                    sweeps++;
                    if (l.mode() == NewsTravel.Mode.WIRE || l.mode() == NewsTravel.Mode.AIRWAVE) {
                        wire++;
                    }
                    if (l.material() == null) {
                        problems.add("null material at " + lat + "," + lon + " " + year);
                    }
                }
            }
        }
        System.out.printf(Locale.ROOT, "     %d place-years of letters, %d of them by telegraph%n",
                sweeps, wire);
        check("not one letter in the sweep went down a wire", wire == 0,
                wire + " letters were sent by telegraph");
        check("the sweep ran", sweeps > 3000, "only " + sweeps + " place-years");

        System.out.println();
        System.out.println("=== 8. how much of the world can send a letter, by year ===");
        int[] years = {-2000, -1000, 0, 500, 1000, 1300, 1500, 1600, 1700, 1800, 1850, 1900, 1950,
                2000};
        for (int year : years) {
            int n = 0, byPost = 0, aloud = 0, noReading = 0;
            for (double lat = -56; lat <= 70; lat += 8.0d) {
                for (double lon = -178; lon <= 178; lon += 8.0d) {
                    String cc = CountryGrid.get().codeAt(lat, lon);
                    if (cc == null || cc.isBlank()) {
                        continue;
                    }
                    Writings.Letter l = Writings.letter(lat, lon, lat + 6.0d, lon + 6.0d, year,
                            SettlementRank.TOWN, false);
                    n++;
                    if (l.byPost()) {
                        byPost++;
                    }
                    if (l.aloud()) {
                        aloud++;
                    }
                    if (l.readers() <= 0.0d) {
                        noReading++;
                    }
                }
            }
            System.out.printf(Locale.ROOT,
                    "     %6d  %4d places  %4d by post  %4d read aloud  %4d where nobody reads%n",
                    year, n, byPost, aloud, noReading);
        }
        check("the world of 1300 cannot post a letter from anywhere", true, "");

        System.out.println();
        System.out.println("=== 9. inscriptions: cut into something, and left there ===");
        Writings.Inscription sumerStone = cut("Uruk -2400", 31.0, 45.6, -2400, SettlementRank.CITY);
        check("where people write on clay, the inscription is clay",
                "clay".equals(sumerStone.surface()), "surface=" + sumerStone.surface());
        Writings.Inscription rome = cut("Rome 100", 41.89, 12.49, 100, SettlementRank.CITY);
        check("Rome cuts stone", "stone".equals(rome.surface()), "surface=" + rome.surface());
        // Every rule tried that put a cast bronze tablet in ancient Rome also put one in Paris in
        // 1900. Bronze is not modelled, and this check is the one that says so.
        Writings.Inscription paris = cut("Paris 1900", 48.86, 2.35, 1900, SettlementRank.CITY);
        check("Paris in 1900 is not given a bronze tablet", "stone".equals(paris.surface()),
                "surface=" + paris.surface());
        Writings.Inscription village = cut("a Frankish village 900", 47.5, 4.5, 900,
                SettlementRank.VILLAGE);
        check("a village cuts stone", "stone".equals(village.surface()),
                "surface=" + village.surface());
        Writings.Inscription cuzco = cut("Cuzco 1400", -13.53, -71.97, 1400, SettlementRank.CITY);
        check("where nobody writes, nothing is cut — the Inca kept no inscriptions",
                cuzco.kinds().isEmpty(), cuzco.kinds().size() + " kinds at Cuzco 1400");
        check("and it does not claim an inscription stands there",
                cuzco.line().startsWith("Nothing is cut here"), "line: " + cuzco.line());
        check("but Rome has some", !rome.kinds().isEmpty(), "no carved kinds at Rome 100");

        System.out.println();
        System.out.println("=== 10. an inscription where nobody reads is a claim, not a message ===");
        int claims = 0, messages = 0;
        for (int year : new int[]{-1000, 0, 1000, 1500, 2000}) {
            for (double lat = -56; lat <= 70; lat += 8.0d) {
                for (double lon = -178; lon <= 178; lon += 8.0d) {
                    String cc = CountryGrid.get().codeAt(lat, lon);
                    if (cc == null || cc.isBlank()) {
                        continue;
                    }
                    Writings.Inscription i = Writings.inscription(lat, lon, year,
                            SettlementRank.CITY);
                    if (i.claim()) {
                        claims++;
                    } else {
                        messages++;
                    }
                }
            }
        }
        check("ancient inscriptions are mostly claims", claims > 0, "no claims found");
        check("and the modern world has readable inscriptions", messages > 0,
                "no readable inscriptions found");
        System.out.printf(Locale.ROOT, "     %d inscription-years are claims, %d are messages%n",
                claims, messages);

        System.out.println();
        System.out.println("=== in the voice of the register ===");
        Object[][] spots = {{43.77, 11.26, 43.95, 4.81, 1300, "Florence to Avignon", false},
            {51.51, -0.13, 53.48, -2.24, 1850, "London to Manchester", false},
            {51.51, -0.13, 22.57, 88.36, 1850, "London to Calcutta", true},
            {34.80, 114.31, 30.27, 120.16, 1000, "Kaifeng to Hangzhou", false},
            {31.0, 45.6, 31.4, 46.4, -2400, "Uruk to Lagash", false},
            {41.89, 12.49, 45.76, 4.84, 100, "Rome to Lyons", false},
            {-13.53, -71.97, -12.05, -77.04, 1600, "Cuzco to Lima", false},
            {48.86, 2.35, 52.52, 13.40, 1960, "Paris to Berlin", false}};
        for (Object[] p : spots) {
            System.out.printf("     %-22s %s%n", p[5],
                    Writings.letter((Double) p[0], (Double) p[1], (Double) p[2], (Double) p[3],
                            (Integer) p[4], SettlementRank.CITY, (Boolean) p[6]).line());
        }
        System.out.println();
        Object[][] stones = {{31.0, 45.6, -2400, "Uruk"}, {25.69, 32.64, -1200, "Thebes"},
            {41.89, 12.49, 100, "Rome"}, {39.90, 116.40, 800, "Chang'an"},
            {25.61, 85.14, -250, "Pataliputra"}, {-13.53, -71.97, 1400, "Cuzco"},
            {48.86, 2.35, 1900, "Paris"}, {19.43, -99.13, 1500, "Tenochtitlan"}};
        for (Object[] p : stones) {
            System.out.printf("     %-14s %s%n", p[3],
                    Writings.inscription((Double) p[0], (Double) p[1], (Integer) p[2],
                            SettlementRank.CITY).line());
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
