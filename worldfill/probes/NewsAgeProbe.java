import com.eternalengine.knowledge.DatedEvents;
import com.eternalengine.knowledge.KnowledgeDate;
import com.eternalengine.knowledge.NewsIndex;

/**
 * How old is the news the game tells you? (2026-10-27)
 *
 * <p>Found while answering "what happens after 2026": standing in Legnica in the year 3000 the news card
 * still said "Word has come of Battle of Liegnitz (1760), in April 2011". The day tier has a floor but no
 * <b>recency</b> rule, so the nearest dated event in hearing is told as today's news however old it is.
 * This measures the age of every day-dated answer the coverage sample gets.
 */
public final class NewsAgeProbe {
    public static void main(String[] args) throws Exception {
        double[][] towns = readTowns();
        int[] years = {-500, 100, 500, 1000, 1200, 1400, 1500, 1600, 1700, 1800, 1850, 1900, 1939, 1960, 2000, 2020};
        long[] cuts = {1, 5, 10, 25, 50, 100, 250, 1000, Long.MAX_VALUE};
        String[] names = {"<=1 year", "<=5", "<=10", "<=25", "<=50", "<=100", "<=250", "<=1000", "older"};
        int[] bucket = new int[cuts.length];
        int hits = 0;
        int fresh2 = 0;
        int asked = 0;
        for (int y : years) {
            int key = KnowledgeDate.key(y, 6, 15);
            for (double[] t : towns) {
                asked++;
                var on = NewsIndex.onDay(t[0], t[1], key);
                if (on.isEmpty() || !on.get().dated()) {
                    continue;
                }
                hits++;
                var e = DatedEvents.get().near(t[0], t[1], key).orElse(null);
                if (e == null) {
                    continue;
                }
                long age = Math.abs((long) key - (long) e.happenedKey()) / 10000L;
                if (age <= 2) {
                    fresh2++;
                }
                for (int i = 0; i < cuts.length; i++) {
                    if (age <= cuts[i]) {
                        bucket[i]++;
                        break;
                    }
                }
            }
        }
        System.out.println("town-years asked          : " + asked);
        System.out.println("day-dated answers         : " + hits);
        System.out.println("of those, within 2 years   : " + fresh2 + "  ("
                + String.format(java.util.Locale.ROOT, "%.1f%%", 100.0 * fresh2 / Math.max(1, hits)) + " of day-dated hits)");
        System.out.println();
        int cum = 0;
        for (int i = 0; i < cuts.length; i++) {
            cum += bucket[i];
            System.out.printf(java.util.Locale.ROOT, "  age %-11s %5d  %5.1f%% of hits   %5.1f%% of all town-years%n",
                    names[i], bucket[i], 100.0 * bucket[i] / Math.max(1, hits), 100.0 * cum / asked);
        }
    }

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
        return out.toArray(new double[0][]);
    }
}
