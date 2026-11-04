import com.eternalengine.knowledge.KnowledgeDate;
import com.eternalengine.knowledge.NewsIndex;

/**
 * Does the spatial grid give the same answer as reading every event? (R2-7, 2026-10-27)
 *
 * <p>The day-aware news question is asked for every card, so it cannot afford to read all 129,232 events.
 * The grid is an optimisation; this proves it is a <b>faithful</b> one - same town, same year, indexed
 * answer against brute-force answer, over the whole 152 x 23 sample. Any mismatch is printed.
 */
public final class NewsGridCheckProbe {
    public static void main(String[] args) throws Exception {
        double[][] towns = readTowns();
        int[] years = {-500, -100, 100, 500, 1000, 1200, 1400, 1500, 1600, 1700, 1750, 1800,
                1815, 1850, 1870, 1900, 1914, 1939, 1945, 1960, 1980, 2000, 2020};
        var all = NewsIndex.all();
        int asked = 0, mismatch = 0;
        for (int y : years) {
            int key = KnowledgeDate.key(y, 6, 15);
            for (double[] t : towns) {
                asked++;
                String indexed = NewsIndex.onDay(t[0], t[1], key).map(NewsIndex.OnDay::name).orElse("-");
                String brute = brute(t[0], t[1], y, all);
                if (!indexed.equals(brute)) {
                    mismatch++;
                    System.out.printf(java.util.Locale.ROOT, "MISMATCH %.3f,%.3f %d  indexed=%s  brute=%s%n",
                            t[0], t[1], y, indexed, brute);
                }
            }
        }
        System.out.println();
        System.out.println("town-years checked : " + asked);
        System.out.println("mismatches         : " + mismatch);
    }

    /** The same rule as NewsIndex.onDay's fallback, but reading every single event. */
    private static String brute(double lat, double lon, int today, java.util.List<NewsIndex.Event> all) {
        var dated = com.eternalengine.knowledge.DatedEvents.get().near(lat, lon, KnowledgeDate.key(today, 6, 15));
        if (dated.isPresent()) {
            return dated.get().name();
        }
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
            if (km < bestKm - 1e-9d
                    || (Math.abs(km - bestKm) <= 1e-9d && best != null && e.name().compareTo(best.name()) < 0)) {
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

    /** The same 152 towns the coverage probe uses, read out of its source so the two cannot drift apart. */
    private static double[][] readTowns() throws Exception {
        String src = java.nio.file.Files.readString(java.nio.file.Path.of("worldfill/probes/NewsCoverageProbe.java"));
        int a = src.indexOf("TOWNS = {");
        int b = src.indexOf("};", a);
        var out = new java.util.ArrayList<double[]>();
        for (String line : src.substring(a, b).split("\n")) {
            int o = line.indexOf('{');
            int c = line.indexOf('}', o);
            if (o < 0 || c < 0) {
                continue;
            }
            String[] parts = line.substring(o + 1, c).split(",");
            if (parts.length < 2) {
                continue;
            }
            out.add(new double[] {Double.parseDouble(parts[0].trim()), Double.parseDouble(parts[1].trim())});
        }
        System.out.println("towns read from coverage probe: " + out.size());
        return out.toArray(new double[0][]);
    }
}
