import com.eternalengine.civilization.HistoricalPresence;
import com.eternalengine.civilization.RulerRegister;
import com.eternalengine.population.HydeGrid;

import java.util.Random;

/**
 * The mod's real occupancy answer (HistoricalPresence.query, no civilization manager) on the
 * same 400 random land points and years as DensityProbe, split by the layer that answered:
 * a dated or present place, an estimated hinterland village, an empire box, a ruler (Deccan, or a
 * world-record ruler where the population model has people), or estimated people only.
 * Then a few spot descriptions.
 */
public class WorldProbe {
    public static void main(String[] args) {
        long t0 = System.nanoTime();
        HistoricalPresence.query(null, 17.39, 78.49, 1700);           // load everything once
        System.out.printf("first query (loads gazetteer, rulers, HYDE): %.1f s%n", (System.nanoTime() - t0) / 1e9);
        System.out.println(RulerRegister.get().summary().display());
        System.out.println("HYDE grid: " + HydeGrid.get().source() + ", " + HydeGrid.get().sliceCount() + " slices");

        int[] years = {-2500, -1500, -500, 1, 500, 1000, 1300, 1500, 1700, 1850, 1900, 1944, 2000};
        Random rnd = new Random(42);
        int N = 400;
        double[] lat = new double[N], lon = new double[N];
        int n = 0;
        while (n < N) {
            double la = -58 + rnd.nextDouble() * 141;
            double lo = -180 + rnd.nextDouble() * 360;
            if (DensityProbe.isLand(la, lo)) { lat[n] = la; lon[n] = lo; n++; }
        }
        System.out.println("\n% of 400 random land points where the mod has someone, by the layer that answers first");
        System.out.printf("%7s %7s %7s %7s %7s %7s | %7s %8s%n", "year", "place", "hinter", "box", "ruler", "people", "ANY", "ms/query");
        for (int y : years) {
            int place = 0, hin = 0, box = 0, rul = 0, ppl = 0, any = 0;
            long q0 = System.nanoTime();
            for (int i = 0; i < N; i++) {
                var r = HistoricalPresence.query(null, lat[i], lon[i], y);
                if (!r.occupied()) continue;
                any++;
                if (r.site().isPresent() || r.presentMap().isPresent() || r.ohm().isPresent()) place++;
                else if (r.hinterland().isPresent()) hin++;
                else if (r.border().isPresent()) box++;
                else if (r.ruler().isPresent() && (!RulerRegister.isGridPlace(r.ruler().get().place()) || r.peopleHere())) rul++;
                else if (r.peopleHere()) ppl++;
            }
            double ms = (System.nanoTime() - q0) / 1e6 / N;
            System.out.printf("%7d %6.1f%% %6.1f%% %6.1f%% %6.1f%% %6.1f%% | %6.1f%% %8.2f%n", y,
                    100.0 * place / N, 100.0 * hin / N, 100.0 * box / N, 100.0 * rul / N, 100.0 * ppl / N, 100.0 * any / N, ms);
        }

        Object[][] spots = {
            {"Mid-Sahara", 23.0, 10.0, 1000}, {"Nile valley, Upper Egypt", 26.1, 32.7, -1500},
            {"Gaul countryside", 46.5, 3.0, -300}, {"Ohio valley", 39.0, -84.0, 1200},
            {"Amazon", -5.0, -62.0, 1400}, {"Siberia", 60.0, 100.0, 1900},
            {"Mongolian steppe", 47.0, 103.0, 1250}, {"Rural Poland", 52.0, 19.5, 1600},
            {"Congo basin", -2.0, 23.0, 1500}, {"Australian outback", -25.0, 135.0, 1700},
            {"Telangana village", 18.18, 78.45, 1900}};
        for (Object[] s : spots) {
            var r = HistoricalPresence.query(null, (Double) s[1], (Double) s[2], (Integer) s[3]);
            System.out.println("\n== " + s[0] + " ==");
            System.out.println(HistoricalPresence.describe(r));
            System.out.println("  -> occupied=" + r.occupied() + " civ=" + r.spawnCivId() + " rank=" + r.rank());
        }
    }
}
