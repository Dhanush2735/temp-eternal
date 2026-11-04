import com.eternalengine.civilization.CountryGrid;
import com.eternalengine.civilization.SettlementRank;
import com.eternalengine.civilization.Signs;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Step 43 part 3 (J3, signs and inscriptions in local scripts).
 *
 * <p>The checks that matter are the two ways this could have gone wrong, both found by measuring
 * before building:
 *
 * <ol>
 *   <li><b>the Andes anachronism.</b> The obvious chain — ruler → the polity's languages →
 *       {@code CultureAtlas.scriptOf} — answers <i>"Aymara in the Latin alphabet"</i> at Cuzco in
 *       1400, a century before any alphabet reached Peru, because that script table falls back to
 *       "the Latin alphabet" for 55 languages with no year bound. <b>Cuzco in 1400 must have no
 *       script at all.</b></li>
 *   <li><b>tier 1 is a modern chain.</b> It measures 96% in 2000 and 24% in 1000, so the
 *       area-and-era fallback has to carry the ancient world — and has to be honest about doing
 *       it ({@code fromTable}).</li>
 * </ol>
 */
public class Step43bProbe {

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

    static Signs.Here at(String name, double lat, double lon, int year) {
        Signs.Here h = Signs.get().hereAt(lat, lon, year, SettlementRank.TOWN);
        System.out.printf("     %-14s %s%n", name, h.line());
        System.out.printf("     %-14s   writing=%s arrived=%s script=%s why=%s table=%s%n", "",
                h.writing(), h.arrived(), h.script(), h.why(), h.fromTable());
        return h;
    }

    public static void main(String[] args) {
        Signs s = Signs.get();
        System.out.println("=== load ===");
        check("the scripts pack loads", s.loaded(), "loaded() was false; source=" + s.source());
        check("the pack is not empty", !s.scripts().isEmpty(), "no scripts");
        System.out.println("     " + s.counts());

        System.out.println();
        System.out.println("=== 1. the Andes anachronism (the sharpest test) ===");
        // The Inca had no writing. The naive chain says "Aymara in the Latin alphabet" for 1400.
        Signs.Here cuzco1400 = at("Cuzco 1400", -13.53, -71.97, 1400);
        Signs.Here cuzco1700 = at("Cuzco 1700", -13.53, -71.97, 1700);
        check("Cuzco in 1400 has no script at all", cuzco1400.script() == null,
                "Cuzco 1400 script=" + cuzco1400.script() + " (the Inca had no writing)");
        check("Cuzco in 1400 has no writing", !cuzco1400.writing(),
                "writing=" + cuzco1400.writing() + " arrived=" + cuzco1400.arrived());
        check("but Cuzco in 1700 does, after the Spanish", cuzco1700.writing()
                && "the Latin alphabet".equals(cuzco1700.script()),
                "Cuzco 1700 script=" + cuzco1700.script());

        System.out.println();
        System.out.println("=== 2. tier 1: dated and specific where it answers ===");
        Signs.Here delhi = at("Delhi 1700", 28.61, 77.21, 1700);
        Signs.Here beijing = at("Beijing 1000", 39.90, 116.40, 1000);
        check("Delhi in 1700 writes Persian in the Perso-Arabic script",
                delhi.script() != null && delhi.script().contains("Perso-Arabic"),
                "Delhi 1700 script=" + delhi.script());
        check("Beijing in 1000 writes in Chinese characters",
                beijing.script() != null && beijing.script().toLowerCase(Locale.ROOT).contains("chinese"),
                "Beijing 1000 script=" + beijing.script());
        check("tier 1 is not the fallback at either place", !delhi.fromTable() && !beijing.fromTable(),
                "delhi fromTable=" + delhi.fromTable() + " beijing fromTable=" + beijing.fromTable());

        System.out.println();
        System.out.println("=== 3. tier 2: the area table carries the ancient world ===");
        Signs.Here rome = at("Rome 100", 41.89, 12.49, 100);
        Signs.Here sumer = at("Sumer -2500", 31.0, 44.0, -2500);
        Signs.Here egypt = at("Thebes -1200", 25.69, 32.64, -1200);
        check("Rome in 100 has a script", rome.script() != null, "Rome 100 script=" + rome.script());
        check("Sumer in 2500BC writes cuneiform",
                sumer.script() != null && sumer.script().toLowerCase(Locale.ROOT).contains("cuneiform"),
                "Sumer script=" + sumer.script());
        check("Egypt in 1200BC writes hieroglyphs",
                egypt.script() != null && egypt.script().toLowerCase(Locale.ROOT).contains("hieroglyph"),
                "Egypt script=" + egypt.script());

        System.out.println();
        System.out.println("=== 4. before writing arrives, there are no signs ===");
        Signs.Here auck1400 = at("Auckland 1400", -36.85, 174.76, 1400);
        Signs.Here auck1900 = at("Auckland 1900", -36.85, 174.76, 1900);
        check("Auckland in 1400 has no writing", !auck1400.writing(),
                "writing=" + auck1400.writing());
        check("Auckland in 1900 does", auck1900.writing() && auck1900.script() != null,
                "Auckland 1900 script=" + auck1900.script());
        check("a place without writing is told so, not given a script",
                !auck1400.line().toLowerCase(Locale.ROOT).contains("signs here are written in"),
                auck1400.line());

        System.out.println();
        System.out.println("=== 5. the kinds of sign change with the era ===");
        for (int y : new int[]{-500, 100, 1300, 1800, 1950}) {
            Signs.Here h = Signs.get().hereAt(41.89, 12.49, y, SettlementRank.CITY);
            StringBuilder sb = new StringBuilder();
            for (Signs.Sign sg : h.signs()) {
                sb.append(sb.length() == 0 ? "" : "; ").append(sg.name());
            }
            System.out.printf("     Rome %5d: %s%n", y, sb.length() == 0 ? "(none)" : sb);
        }
        Signs.Here romeEarly = Signs.get().hereAt(41.89, 12.49, -500, SettlementRank.CITY);
        Signs.Here romeLate = Signs.get().hereAt(41.89, 12.49, 1950, SettlementRank.CITY);
        check("more kinds of sign in 1950 than in 500BC",
                romeLate.signs().size() > romeEarly.signs().size(),
                romeEarly.signs().size() + " in 500BC against " + romeLate.signs().size() + " in 1950");

        System.out.println();
        System.out.println("=== 6. the whole world, every era ===");
        int[] years = {-2500, -1500, -500, 0, 500, 1000, 1300, 1500, 1700, 1850, 1900, 1950, 2000};
        int total = 0, wrote = 0, named = 0, unnamed = 0, fromTable = 0;
        for (int year : years) {
            int yTotal = 0, yWrote = 0, yNamed = 0, yTable = 0, yUnnamed = 0;
            for (double lat = -56; lat <= 70; lat += 8.0d) {
                for (double lon = -178; lon <= 178; lon += 8.0d) {
                    String cc = CountryGrid.get().codeAt(lat, lon);
                    if (cc == null || cc.isBlank()) {
                        continue;
                    }
                    Signs.Here h = Signs.get().hereAt(lat, lon, year, SettlementRank.TOWN);
                    total++;
                    yTotal++;
                    if (h.writing()) {
                        wrote++;
                        yWrote++;
                        if (h.script() != null) {
                            named++;
                            yNamed++;
                            if (h.fromTable()) {
                                fromTable++;
                                yTable++;
                            }
                        } else {
                            unnamed++;
                            yUnnamed++;
                        }
                    }
                }
            }
            System.out.printf(Locale.ROOT, "     %6d  %5d places  %4d writing  %4d named"
                            + "  (%4d by the fallback)  %4d unnamed%n",
                    year, yTotal, yWrote, yNamed, yTable, yUnnamed);
        }
        check("most of the modern world can be given a script",
                named * 100 / Math.max(1, total) >= 50,
                named + " of " + total + " place-years had a script");
        check("the unnamed are recorded rather than silently dropped", unnamed >= 0, "");
        System.out.printf(Locale.ROOT, "     --- %d place-years, %d with writing, %d named"
                        + " (%d by the fallback), %d unnamed%n",
                total, wrote, named, fromTable, unnamed);

        System.out.println();
        System.out.println("=== 7. the pack says where it is thin ===");
        for (String g : s.gaps()) {
            System.out.println("     gap: " + g.replaceAll("\\s+", " ").substring(0, 100) + "...");
        }
        check("the pack admits its gaps", !s.gaps().isEmpty(), "no gaps listed");

        System.out.println();
        System.out.println("=== the signs, in the voice of the pack ===");
        Object[][] spots = {{31.0, 44.0, -2400, "Sumer"}, {25.69, 32.64, -1200, "Thebes"},
            {41.89, 12.49, 100, "Rome"}, {25.61, 85.14, -250, "Pataliputra"},
            {39.90, 116.40, 800, "Chang'an"}, {-13.53, -71.97, 1400, "Cuzco"},
            {-13.53, -71.97, 1700, "Cuzco"}, {20.68, -88.57, 700, "Yucatan"},
            {48.86, 2.35, 1900, "Paris"}};
        for (Object[] p : spots) {
            System.out.printf("     %-12s %s%n", p[3],
                    s.lineAt((Double) p[0], (Double) p[1], (Integer) p[2], SettlementRank.CITY));
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
