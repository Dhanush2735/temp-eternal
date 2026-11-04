import com.eternalengine.civilization.*;
import com.eternalengine.technology.TechnologyAtlas;
import java.util.*;

/** J3 recon: is there writing here at all, per the technology atlas (arrived and not forgotten)? */
public class Write43 {
    public static void main(String[] a) {
        TechnologyAtlas at = TechnologyAtlas.get();
        var w = at.tech("writing");
        var paper = at.tech("paper");
        var press = at.tech("printing_press");
        var quipuish = at.tech("indus_script");
        System.out.println("writing tech: " + (w == null ? "MISSING" : w.id + " / " + w.name));

        System.out.println();
        System.out.println("=== when writing arrives (and whether it is ever lost) ===");
        Object[][] spots = {{31.0,44.0,"Sumer"},{35.68,23.63,"Crete"},{41.89,12.49,"Rome"},
            {48.86,2.35,"Paris"},{55.75,37.62,"Moscow"},{39.90,116.40,"Beijing"},
            {35.68,139.69,"Edo/Tokyo"},{28.61,77.21,"Delhi"},{-13.53,-71.97,"Cuzco"},
            {19.43,-99.13,"Tenochtitlan"},{20.68,-88.57,"Yucatan"},{-6.2,106.8,"Jakarta"},
            {30.05,31.25,"Cairo"},{-1.29,36.82,"Nairobi"},{-25.0,28.0,"Pretoria"},
            {64.13,-21.9,"Reykjavik"},{-36.85,174.76,"Auckland"}};
        String[] nm = {"Sumer","Crete","Rome","Paris","Moscow","Beijing","Edo/Tokyo","Delhi","Cuzco",
            "Tenochtitlan","Yucatan","Jakarta","Cairo","Nairobi","Pretoria","Reykjavik","Auckland"};
        System.out.printf("%-14s %9s %9s %9s %9s%n", "place", "writing", "paper", "press", "indus");
        for (int i = 0; i < spots.length; i++) {
            double la=(Double)spots[i][0], lo=(Double)spots[i][1];
            System.out.printf(Locale.ROOT, "%-14s %9s %9s %9s %9s%n", nm[i],
                yr(at.arrivalAt(w, la, lo)), yr(at.arrivalAt(paper, la, lo)),
                yr(at.arrivalAt(press, la, lo)), yr(at.arrivalAt(quipuish, la, lo)));
        }
        System.out.println();
        System.out.println("=== coverage: writing present (arrived and not lost), by era ===");
        int[] years = {-2500,-1500,-500,0,500,1000,1300,1500,1700,1850,1900,1950,2000};
        Random r = new Random(3);
        List<double[]> land = new ArrayList<>();
        while (land.size() < 400) {
            double lat=-56+118*r.nextDouble(), lon=-180+360*r.nextDouble();
            String cc = CountryGrid.get().codeAt(lat, lon);
            if (cc != null && !cc.isBlank()) land.add(new double[]{lat, lon});
        }
        System.out.println("year   writing   script   both");
        for (int year : years) {
            int hasW=0, hasS=0, both=0;
            for (double[] p : land) {
                boolean w1 = at.arrivalAt(w, p[0], p[1]) <= year && !at.lostAt(w, p[0], p[1], year);
                boolean s1 = scriptAt(p[0], p[1], year) != null;
                if (w1) hasW++;
                if (s1) hasS++;
                if (w1 && s1) both++;
            }
            System.out.printf(Locale.ROOT, "%5d  %5.0f%%   %5.0f%%  %5.0f%%%n",
                year, 100.0*hasW/land.size(), 100.0*hasS/land.size(), 100.0*both/land.size());
        }
    }
    static String yr(int y) { return y >= TechnologyAtlas.NEVER ? "never" : String.valueOf(y); }
    static String scriptAt(double lat, double lon, int year) {
        var h = RulerRegister.get().rulerAt(lat, lon, year);
        if (h.isEmpty()) return null;
        var f = LeaderRegister.get().facts(h.get().wikidata());
        if (f.isEmpty()) return null;
        for (String L : f.get().languages()) {
            String s = CultureAtlas.get().scriptOf(L, year);
            if (s != null) return s;
        }
        return null;
    }
}
