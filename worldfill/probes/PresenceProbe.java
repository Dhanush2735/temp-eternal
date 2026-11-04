import com.eternalengine.civilization.HistoryGazetteer;

import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;

/**
 * "Would anyone be here?" measured with the mod's own HistoryGazetteer, on the same 400 random
 * land points and years as DensityProbe (same seed, same coarse land mask).
 *
 *   site       nearestOccupied(): a dated or present place covers the point this year
 *   hinterland estimatedHinterland(): unnamed countryside within 80 km of a dated town or city
 *   box        borderAt(): an approximate empire core box (rank village)
 *   any        any of the three - the gazetteer layers of HistoricalPresence's occupancy order
 *              (OHM and the ruler register are outside the gazetteer and not counted here)
 *
 * Also prints load time and sites per pack, and with an argument writes every present-only
 * site's estimated occupiedStart to that file (to diff the settlement-year estimator before /
 * after a pack change).
 */
public class PresenceProbe {
    public static void main(String[] args) throws Exception {
        long t0 = System.nanoTime();
        HistoryGazetteer g = HistoryGazetteer.get();
        long t1 = System.nanoTime();
        System.out.printf("gazetteer load: %.1f s   sites=%d events=%d borders=%d%n",
                (t1 - t0) / 1e9, g.siteCount(), g.eventCount(), g.allBorders().size());
        Map<String, Integer> perPack = new TreeMap<>();
        for (var s : g.allSites()) perPack.merge(s.packId(), 1, Integer::sum);
        perPack.forEach((k, v) -> System.out.printf("  %-28s %6d%n", k, v));

        if (args.length > 0) {
            try (PrintWriter w = new PrintWriter(Files.newBufferedWriter(Path.of(args[0]), StandardCharsets.UTF_8))) {
                for (var s : g.allSites()) {
                    if (s.presentOnly()) w.println(s.id() + "\t" + s.occupiedStart());
                }
            }
        }

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
        System.out.println("\n% of " + N + " random land points where the gazetteer has someone, by year");
        System.out.printf("%8s %8s %11s %8s %8s %9s%n", "year", "site", "hinterland", "box", "any", "ms/query");
        for (int y : years) {
            int site = 0, hin = 0, box = 0, any = 0;
            long q0 = System.nanoTime();
            for (int i = 0; i < N; i++) {
                boolean a = g.nearestOccupied(lat[i], lon[i], y).isPresent();
                boolean b = !a && g.estimatedHinterland(lat[i], lon[i], y).isPresent();
                boolean c = g.borderAt(lat[i], lon[i], y).isPresent();
                if (a) site++;
                if (b) hin++;
                if (c) box++;
                if (a || b || c) any++;
            }
            double ms = (System.nanoTime() - q0) / 1e6 / N;
            System.out.printf("%8d %7.1f%% %10.1f%% %7.1f%% %7.1f%% %9.2f%n", y,
                    100.0 * site / N, 100.0 * hin / N, 100.0 * box / N, 100.0 * any / N, ms);
        }
    }
}
