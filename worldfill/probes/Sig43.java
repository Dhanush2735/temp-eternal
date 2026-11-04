import com.eternalengine.civilization.*;
import java.util.*;

/** How far does place -> ruler -> polity languages -> script reach? (J3 recon) */
public class Sig43 {
    public static void main(String[] a) {
        RulerRegister rr = RulerRegister.get();
        LeaderRegister lr = LeaderRegister.get();
        CultureAtlas ca = CultureAtlas.get();
        int[] years = {-500, 0, 500, 1000, 1300, 1500, 1700, 1850, 1900, 1950, 2000};
        System.out.println("year    land   ruled   w/lang   w/script      %");
        Random r = new Random(3);
        List<double[]> land = new ArrayList<>();
        while (land.size() < 400) {
            double lat = -56 + 118 * r.nextDouble(), lon = -180 + 360 * r.nextDouble();
            String cc = CountryGrid.get().codeAt(lat, lon);
            if (cc != null && !cc.isBlank()) land.add(new double[]{lat, lon});
        }
        for (int year : years) {
            int ruled = 0, withLang = 0, withScript = 0;
            for (double[] p : land) {
                var h = rr.rulerAt(p[0], p[1], year);
                if (h.isEmpty()) continue;
                ruled++;
                var f = lr.facts(h.get().wikidata());
                if (f.isEmpty()) continue;
                List<String> langs = f.get().languages();
                if (langs == null || langs.isEmpty()) continue;
                withLang++;
                for (String L : langs) {
                    if (ca.scriptOf(L, year) != null) { withScript++; break; }
                }
            }
            System.out.printf(Locale.ROOT, "%5d  %5d  %6d  %7d  %9d  %5.0f%%%n",
                    year, land.size(), ruled, withLang, withScript,
                    100.0 * withScript / land.size());
        }
        System.out.println();
        System.out.println("=== what it says at a few places ===");
        Object[][] spots = {{41.89,12.49,100},{48.86,2.35,1300},{39.90,116.40,1000},
            {28.61,77.21,1700},{21.42,39.83,1000},{35.68,139.69,1800},{-13.53,-71.97,1400}};
        String[] nm = {"Rome 1000","Paris 1300","Beijing 1000","Delhi 1700","Mecca 1000","Edo 1800","Cuzco 1400"};
        for (int i = 0; i < spots.length; i++) {
            double lat=(Double)spots[i][0], lon=(Double)spots[i][1]; int y=(Integer)spots[i][2];
            var h = rr.rulerAt(lat, lon, y);
            StringBuilder sb = new StringBuilder(String.format("%-14s ", nm[i]));
            if (h.isEmpty()) { sb.append("no ruler"); }
            else {
                var f = lr.facts(h.get().wikidata());
                sb.append(h.get().ruler());
                if (f.isPresent()) {
                    sb.append("  langs=").append(f.get().languages());
                    List<String> sc = new ArrayList<>();
                    for (String L : f.get().languages()) {
                        String s = ca.scriptOf(L, y);
                        if (s != null) sc.add(L + " -> " + s);
                    }
                    sb.append("  ").append(sc.isEmpty() ? "(no script)" : sc);
                }
            }
            System.out.println(sb);
        }
    }
}
