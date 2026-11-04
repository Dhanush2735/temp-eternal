import com.eternalengine.knowledge.DatedEvents;
import com.eternalengine.player.EventKind;

/**
 * How far across Earth can a player actually fork history? (butterfly effect, 2026-10-27)
 *
 * <p>The detector refuses any event whose kind it does not trust. This measures, over the whole worldwide
 * dated corpus, how many events were stoppable BEFORE the kind was recovered from the title and how many are
 * stoppable AFTER - and, crucially, that disasters are still refused.
 */
public final class ButterflyReachProbe {
    public static void main(String[] args) {
        var dated = DatedEvents.get();
        int total = 0, before = 0, after = 0, disastersRefused = 0, stillRefused = 0;
        java.util.Map<String, Integer> afterKind = new java.util.TreeMap<>();
        java.util.Map<String, int[]> byContinent = new java.util.TreeMap<>();

        for (var e : dated.all()) {
            total++;
            String raw = "event";
            String kind = EventKind.effective(raw, e.name());
            boolean wasStoppable = com.eternalengine.player.InWorldInterventionDetector.STOPPABLE_KINDS
                    .contains(raw);
            boolean isStoppable = com.eternalengine.player.InWorldInterventionDetector.STOPPABLE_KINDS
                    .contains(kind);
            if (wasStoppable) {
                before++;
            }
            if (isStoppable) {
                after++;
                afterKind.merge(kind, 1, Integer::sum);
            } else {
                if (com.eternalengine.player.InWorldInterventionDetector.REFUSED_KINDS.contains(kind)
                        || EventKind.looksLikeDisaster(e.name())) {
                    disastersRefused++;
                } else {
                    stillRefused++;
                }
            }
            String c = continent(e.lat(), e.lon());
            byContinent.computeIfAbsent(c, k -> new int[3]);
            byContinent.get(c)[0]++;
            if (isStoppable) {
                byContinent.get(c)[1]++;
            }
            if (EventKind.looksLikeDisaster(e.name())) {
                byContinent.get(c)[2]++;
            }
        }

        System.out.println("worldwide dated events      : " + total);
        System.out.println("stoppable BEFORE this fix   : " + before + "  (kind is \"event\", which is in neither list)");
        System.out.println("stoppable AFTER  this fix   : " + after + "  ("
                + String.format(java.util.Locale.ROOT, "%.1f%%", 100.0 * after / total) + ")");
        System.out.println("refused as disasters        : " + disastersRefused + "  (correct: nobody stops a plague)");
        System.out.println("refused, not a disaster     : " + stillRefused + "  (unrecognised, so still refused)");
        System.out.println();
        System.out.println("kinds recovered:");
        afterKind.forEach((k, n) -> System.out.println("  " + k + ": " + n));
        System.out.println();
        System.out.printf(java.util.Locale.ROOT, "%-12s %8s %10s %10s%n", "continent", "events", "forkable", "disasters");
        byContinent.forEach((c, a) ->
                System.out.printf(java.util.Locale.ROOT, "%-12s %8d %10d %10d%n", c, a[0], a[1], a[2]));
    }

    private static String continent(double lat, double lon) {
        if (lon >= -25 && lon <= 60 && lat >= 34) return "Europe";
        if (lon >= -25 && lon <= 60 && lat < 34) return "Africa";
        if (lon > 60 && lon <= 180 && lat >= 0) return "Asia";
        if (lon > 60 && lon <= 180) return "Oceania/SEA";
        if (lon >= -170 && lon <= -25 && lat >= 12) return "N.America";
        if (lon >= -170 && lon <= -25) return "S.America";
        return "other";
    }
}
