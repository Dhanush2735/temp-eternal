import com.eternalengine.knowledge.DatedEvents;
import com.eternalengine.knowledge.KnowledgeDate;
import com.eternalengine.knowledge.NewsIndex;

/** What does the day-aware news question cost? (R2-7, 2026-10-27) */
public final class NewsCostProbe {
    public static void main(String[] args) {
        int key = KnowledgeDate.key(1850, 6, 15);
        double[][] towns = new double[52][2];
        java.util.Random r = new java.util.Random(7);
        for (int i = 0; i < towns.length; i++) {
            towns[i][0] = -50 + r.nextDouble() * 110;
            towns[i][1] = -170 + r.nextDouble() * 340;
        }
        for (int warm = 0; warm < 3; warm++) {
            for (double[] t : towns) {
                NewsIndex.onDay(t[0], t[1], key);
            }
        }
        int rounds = 5;
        double[] best = new double[towns.length];
        double[] bestDated = new double[towns.length];
        java.util.Arrays.fill(best, 1e9);
        java.util.Arrays.fill(bestDated, 1e9);
        for (int i = 0; i < towns.length; i++) {
            double[] t = towns[i];
            for (int round = 0; round < rounds; round++) {
                long t0 = System.nanoTime();
                NewsIndex.onDay(t[0], t[1], key);
                best[i] = Math.min(best[i], (System.nanoTime() - t0) / 1e6);
                long t1 = System.nanoTime();
                DatedEvents.get().near(t[0], t[1], key);
                bestDated[i] = Math.min(bestDated[i], (System.nanoTime() - t1) / 1e6);
            }
        }
        double[] bestBrute = new double[towns.length];
        java.util.Arrays.fill(bestBrute, 1e9);
        var all = NewsIndex.all();
        int today = 1850;
        for (int i = 0; i < towns.length; i++) {
            double[] t = towns[i];
            for (int round = 0; round < rounds; round++) {
                long t0 = System.nanoTime();
                brute(t[0], t[1], today, all);
                bestBrute[i] = Math.min(bestBrute[i], (System.nanoTime() - t0) / 1e6);
            }
        }
        System.out.printf(java.util.Locale.ROOT, "brute scan avg %.3f ms  max %.3f ms  (%d events read each time)%n",
                avg(bestBrute), max(bestBrute), all.size());
        System.out.printf(java.util.Locale.ROOT, "onDay      avg %.3f ms  max %.3f ms%n", avg(best), max(best));
        System.out.printf(java.util.Locale.ROOT, "dated only avg %.3f ms  max %.3f ms%n", avg(bestDated), max(bestDated));
    }

    /** The year-only fallback as it was before the index: read every event. */
    private static String brute(double lat, double lon, int today, java.util.List<NewsIndex.Event> all) {
        NewsIndex.Event best = null;
        double bestKm = Double.MAX_VALUE;
        for (NewsIndex.Event e : all) {
            if (e.end() >= today || e.end() < today - NewsIndex.NEWS_YEARS) {
                continue;
            }
            double km = km(lat, lon, e.lat(), e.lon());
            if (km > e.radiusKm() + NewsIndex.HEAR_KM) {
                continue;
            }
            if (km < bestKm - 1e-9) {
                bestKm = km;
                best = e;
            }
        }
        return best == null ? "-" : best.name();
    }

    private static double km(double a, double b, double c, double d) {
        double r = 6371.0;
        double p1 = Math.toRadians(a), p2 = Math.toRadians(c);
        double dp = p2 - p1, dl = Math.toRadians(d - b);
        double h = Math.sin(dp / 2) * Math.sin(dp / 2)
                + Math.cos(p1) * Math.cos(p2) * Math.sin(dl / 2) * Math.sin(dl / 2);
        return 2 * r * Math.asin(Math.min(1.0, Math.sqrt(h)));
    }

    private static double avg(double[] a) {
        double s = 0;
        for (double v : a) {
            s += v;
        }
        return s / a.length;
    }

    private static double max(double[] a) {
        double m = 0;
        for (double v : a) {
            m = Math.max(m, v);
        }
        return m;
    }
}
