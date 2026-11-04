import com.eternalengine.civilization.FamousPeople;
import com.eternalengine.civilization.HistoryChecks;
import com.eternalengine.civilization.RulerRegister;
import com.eternalengine.data.TileCache;

import java.nio.file.Path;
import java.util.List;

/**
 * Step 26 (A4): the famous people read from tiles give the same answers, in the same order, as the master file.
 * Every land point of the world sample (400 points) and the test places, in 14 years from 3000 BC to 2026: the people
 * alive, the people who died that year (by the land's state, by no state, and by an unknown state), and the people
 * born within 15 km and 100 km. Then the memory and the time each way takes.
 */
public final class TilesProbe {
    private static long used() {
        Runtime rt = Runtime.getRuntime();
        long best = Long.MAX_VALUE;
        for (int i = 0; i < 4; i++) {
            System.gc();
            try { Thread.sleep(50); } catch (InterruptedException ignored) { }
            best = Math.min(best, rt.totalMemory() - rt.freeMemory());
        }
        return best;
    }

    private static String key(List<FamousPeople.Person> ps) {
        StringBuilder sb = new StringBuilder();
        for (FamousPeople.Person p : ps) {
            sb.append(p.row()).append(':').append(p.display()).append(':').append(p.birth()).append(':').append(p.death())
                    .append(':').append(p.state()).append(':').append(p.lat()).append(':').append(p.lon()).append(';');
        }
        return sb.toString();
    }

    public static void main(String[] args) {
        Path master = Path.of("/home/user/eternal/src/main/resources/data/eternalengine/eternal/history/famous_people.json.gz");
        long m0 = used();
        long t0 = System.nanoTime();
        FamousPeople tiled = FamousPeople.get();
        long tLoad = (System.nanoTime() - t0) / 1_000_000;
        long m1 = used();
        t0 = System.nanoTime();
        FamousPeople full = FamousPeople.fromFile(master);
        long fLoad = (System.nanoTime() - t0) / 1_000_000;
        long m2 = used();
        System.out.println("tiles:  " + tiled.summary());
        System.out.println("master: " + full.summary());
        System.out.printf("memory: tiles %.1f MB (loaded in %d ms), master %.1f MB (loaded in %d ms)%n",
                (m1 - m0) / 1048576.0, tLoad, (m2 - m1) / 1048576.0, fLoad);
        if (tiled.tileStore() == null) {
            System.out.println("FAIL: the register did not read the tile file");
            System.exit(1);
        }
        List<double[]> points = new java.util.ArrayList<>(java.util.Arrays.asList(HistoryChecks.landPoints()));
        double[][] places = {{18.94, 72.83}, {41.89, 12.49}, {55.76, 37.62}, {4.95, 8.32}, {35.68, 139.76},
                {48.86, 2.35}, {51.51, -0.13}, {40.71, -74.01}, {39.90, 116.40}, {30.04, 31.24}, {-33.87, 151.21},
                {-23.55, -46.63}, {19.43, -99.13}, {17.36, 78.47}, {28.61, 77.21}, {52.52, 13.40}, {59.33, 18.07},
                {-1.29, 36.82}, {6.52, 3.38}, {33.31, 44.36}, {64.15, -21.94}, {-13.53, -71.97}, {21.31, -157.86}};
        for (double[] p : places) {
            points.add(p);
        }
        int[] years = {-3000, -1000, -500, 0, 500, 1000, 1300, 1500, 1700, 1800, 1850, 1900, 1950, 2026};
        RulerRegister reg = RulerRegister.get();
        long queries = 0, bad = 0, people = 0;
        long tTiles = 0, tFull = 0;
        for (double[] p : points) {
            for (int y : years) {
                String q = reg.rulerAt(p[0], p[1], y).map(RulerRegister.Hit::wikidata).orElse(null);
                for (String state : new String[] {q, null, "Q-none"}) {
                    long a = System.nanoTime();
                    String k1 = key(tiled.livingIn(state, p[0], p[1], y)) + "|" + key(tiled.diedIn(state, p[0], p[1], y));
                    long b = System.nanoTime();
                    String k2 = key(full.livingIn(state, p[0], p[1], y)) + "|" + key(full.diedIn(state, p[0], p[1], y));
                    long c = System.nanoTime();
                    tTiles += b - a;
                    tFull += c - b;
                    queries += 2;
                    people += k2.chars().filter(ch -> ch == ';').count();
                    if (!k1.equals(k2)) {
                        bad++;
                        if (bad <= 5) {
                            System.out.printf("DIFF living/died %s at %.2f,%.2f in %d%n", state, p[0], p[1], y);
                        }
                    }
                }
                for (double km : new double[] {15.0, 100.0}) {
                    long a = System.nanoTime();
                    String k1 = key(tiled.bornNear(p[0], p[1], y, km));
                    long b = System.nanoTime();
                    String k2 = key(full.bornNear(p[0], p[1], y, km));
                    long c = System.nanoTime();
                    tTiles += b - a;
                    tFull += c - b;
                    queries++;
                    people += k2.chars().filter(ch -> ch == ';').count();
                    if (!k1.equals(k2)) {
                        bad++;
                        if (bad <= 5) {
                            System.out.printf("DIFF born within %.0f km at %.2f,%.2f in %d%n", km, p[0], p[1], y);
                        }
                    }
                }
            }
        }
        long nTiled = tiled.all().count();
        long nFull = full.all().count();
        System.out.printf("points %d x years %d: %d queries, %d people in the answers, %d different%n",
                points.size(), years.length, queries, people, bad);
        System.out.printf("everyone: tiles %d, master %d%s%n", nTiled, nFull, nTiled == nFull ? "" : "  DIFFERENT");
        System.out.printf("time: tiles %.1f s (%.2f ms a query, tiles opened when needed), master %.1f s (%.2f ms)%n",
                tTiles / 1e9, tTiles / 1e6 / queries, tFull / 1e9, tFull / 1e6 / queries);
        System.out.println(TileCache.SHARED.stats().display());
        boolean ok = bad == 0 && nTiled == nFull && tiled.size() == full.size()
                && tiled.birthplaceCount() == full.birthplaceCount()
                && TileCache.SHARED.stats().peakBytes() <= TileCache.SHARED.budgetBytes();
        System.out.println(ok ? "TILES OK: the same answers as the master" : "TILES FAIL");
        System.exit(ok ? 0 : 1);
    }
}
