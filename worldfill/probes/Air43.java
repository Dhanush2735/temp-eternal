import com.eternalengine.civilization.CountryGrid;
import com.eternalengine.climate.ClimatePeriods;
import java.util.*;

/** J4 recon: how often does a climate period (dust, volcanic haze) apply at a place and year? */
public class Air43 {
    public static void main(String[] a) {
        ClimatePeriods cp = ClimatePeriods.get();
        System.out.println("loaded=" + cp.loaded() + " count=" + cp.count() + " problem=" + cp.problem());
        System.out.println();
        int[] years = {-3000, -2000, -1000, -500, 0, 500, 1000, 1300, 1500, 1700, 1800, 1900, 2000};
        System.out.println("year   land   any   DROUGHT  VOLCANIC  MONSOON");
        Random r = new Random(9);
        List<double[]> land = new ArrayList<>();
        while (land.size() < 300) {
            double lat = -56 + 118 * r.nextDouble(), lon = -180 + 360 * r.nextDouble();
            String cc = CountryGrid.get().codeAt(lat, lon);
            if (cc != null && !cc.isBlank()) land.add(new double[]{lat, lon});
        }
        for (int year : years) {
            int any = 0, dr = 0, vo = 0, mo = 0;
            for (double[] p : land) {
                List<ClimatePeriods.Period> act = cp.active(p[0], p[1], year);
                if (!act.isEmpty()) any++;
                for (ClimatePeriods.Period q : act) {
                    if ("DROUGHT".equals(q.type())) { dr++; break; }
                }
                for (ClimatePeriods.Period q : act) {
                    if ("VOLCANIC".equals(q.type())) { vo++; break; }
                }
                for (ClimatePeriods.Period q : act) {
                    if ("MONSOON".equals(q.type())) { mo++; break; }
                }
            }
            System.out.printf(Locale.ROOT, "%5d  %5d  %4.0f%%  %7.0f%%  %8.0f%%  %7.0f%%%n",
                year, land.size(), 100.0*any/land.size(), 100.0*dr/land.size(),
                100.0*vo/land.size(), 100.0*mo/land.size());
        }
        System.out.println();
        System.out.println("=== which period covers the whole world? (sample point 0N/20E in 1000) ===");
        for (ClimatePeriods.Period q : cp.active(0.0, 20.0, 1000)) {
            System.out.printf("   %-28s %-9s %d..%d  r=%.0fkm  lat=%.0f lon=%.0f%n",
                q.name(), q.type(), q.startYear(), q.endYear(), q.radiusKm(), q.lat(), q.lon());
        }
        System.out.println();
        System.out.println("=== radius distribution ===");
        List<Double> rs = new ArrayList<>();
        for (ClimatePeriods.Period q : cp.periods()) rs.add(q.radiusKm());
        Collections.sort(rs);
        System.out.println("   min=" + rs.get(0) + " median=" + rs.get(rs.size()/2) + " max=" + rs.get(rs.size()-1));
        System.out.println();
        System.out.println("=== what the air is like at known places ===");
        Object[][] s = {{53.48,-2.24,1850,"Manchester"},{41.89,12.49,100,"Rome"},
            {39.90,116.40,1000,"Beijing"},{22.0,15.0,-2000,"Sahara"},
            {52.5,13.4,1816,"Berlin 1816"},{-13.53,-71.97,1600,"Cuzco 1600"},
            {28.61,77.21,1900,"Delhi"},{19.43,-99.13,1500,"Tenochtitlan"}};
        for (Object[] p : s) {
            List<ClimatePeriods.Period> act = cp.active((Double)p[0], (Double)p[1], (Integer)p[2]);
            System.out.printf("%-16s ", p[3]);
            if (act.isEmpty()) System.out.println("(no period)");
            for (ClimatePeriods.Period q : act)
                System.out.printf("[%s %s r=%.0fkm sev=%.0f] ", q.type(), q.name(), q.radiusKm(), q.severity());
            System.out.println();
        }
    }
}
