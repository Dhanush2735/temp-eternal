import com.eternalengine.knowledge.DatedEvents;
import com.eternalengine.knowledge.KnowledgeDate;
import com.eternalengine.knowledge.NewsIndex;

/**
 * What is the news between 2027 and 3000? (2026-10-27)
 *
 * <p>Requirements 1 and 2 are re-scoped to 3000 BC - 3000 AD, and the coverage probe stopped at 2020, so
 * this range was unmeasured. Two things are asked: is there any news at all after the last recorded year,
 * and can a future event ever be told as today's news.
 */
public final class FutureNewsProbe {
    private static final double[][] TOWNS = {
            {51.207, 16.155}, {52.520, 13.400}, {41.010, 28.980}, {48.857, 2.352}, {51.507, -0.128},
            {41.900, 12.500}, {40.417, -3.704}, {55.756, 37.617}, {30.044, 31.235}, {28.614, 77.209},
            {35.689, 139.692}, {39.904, 116.407}, {40.712, -74.006}, {19.433, -99.133}, {-23.551, -46.633},
            {-1.292, 36.822}, {-33.925, 18.424}, {-33.869, 151.209}, {64.146, -21.942}, {1.352, 103.820},
    };

    private static final int[] YEARS = {2020, 2025, 2026, 2027, 2030, 2050, 2100, 2400, 2700, 2999, 3000};

    public static void main(String[] args) {
        var dated = DatedEvents.get();
        System.out.println(dated);
        int futureDated = 0;
        int latest = Integer.MIN_VALUE;
        for (var e : dated.all()) {
            latest = Math.max(latest, e.y());
            if (e.y() > 2026) {
                futureDated++;
            }
        }
        System.out.println("latest dated event year in the file: " + latest);
        System.out.println("dated events after 2026:             " + futureDated);
        System.out.println();
        System.out.printf(java.util.Locale.ROOT, "%-6s %12s %12s %12s   %s%n",
                "year", "day-dated", "year-only", "no news", "example");
        for (int y : YEARS) {
            int key = KnowledgeDate.key(y, 6, 15);
            int day = 0, yonly = 0, nil = 0;
            String example = "";
            for (double[] t : TOWNS) {
                var on = NewsIndex.onDay(t[0], t[1], key);
                if (on.isEmpty()) {
                    nil++;
                } else if (on.get().dated()) {
                    day++;
                    if (example.isEmpty()) {
                        example = on.get().text();
                    }
                } else {
                    yonly++;
                    if (example.isEmpty()) {
                        example = on.get().text();
                    }
                }
            }
            if (example.length() > 96) {
                example = example.substring(0, 93) + "...";
            }
            System.out.printf(java.util.Locale.ROOT, "%-6d %12d %12d %12d   %s%n", y, day, yonly, nil, example);
        }
    }
}
