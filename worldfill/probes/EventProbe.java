import com.eternalengine.civilization.HistoryGazetteer;
import com.eternalengine.civilization.HistoryGazetteer.Event;
import com.eternalengine.civilization.HistoryGazetteer.EventHit;

import java.util.Map;
import java.util.Optional;
import java.util.TreeMap;

/**
 * Step-5 check through the mod's own HistoryGazetteer (run by worldfill/probe_events.sh):
 *  - every event pack loads; counts per pack and per confidence;
 *  - nearestEvent prefers a local pin and falls back to a regional one;
 *  - nearestLocalEvent (the intervention locator) never returns a regional pin;
 *  - "% of 400 land points with an event this year" before/after (local only vs any);
 *  - query time.
 */
public class EventProbe {
    public static void main(String[] args) {
        long t0 = System.nanoTime();
        HistoryGazetteer g = HistoryGazetteer.get();
        System.out.printf("gazetteer load: %.1f s   events=%d%n", (System.nanoTime() - t0) / 1e9, g.eventCount());
        Map<String, Integer> perPack = new TreeMap<>();
        Map<String, Integer> perConf = new TreeMap<>();
        int regional = 0;
        for (Event e : g.allEvents()) {
            perPack.merge(e.packId(), 1, Integer::sum);
            perConf.merge(String.valueOf(e.confidence()), 1, Integer::sum);
            if (HistoryGazetteer.isRegional(e)) regional++;
        }
        perPack.forEach((k, v) -> System.out.printf("  pack %-26s %6d%n", k, v));
        perConf.forEach((k, v) -> System.out.printf("  confidence %-22s %6d%n", k, v));
        System.out.printf("  regional pins: %d%n", regional);

        double[][] spots = {
                {17.385, 78.4867, 1687},   // Hyderabad, Mughal siege of Golconda
                {17.385, 78.4867, 1857},
                {48.8566, 2.3522, 1789},   // Paris
                {46.0, 2.0, 1789},         // rural France
                {41.9, 12.5, 1348},        // Rome, Black Death
                {51.5, -0.12, 1665},       // London, Great Plague
                {30.0, 31.2, -2600},       // Old Kingdom Egypt
                {34.3, 108.9, -1000},      // Western Zhou heartland
                {35.0, 103.0, 1556},       // Shaanxi earthquake region
                {-12.0, -77.0, 1746},      // Lima earthquake
                {23.0, 10.0, 1000},        // Sahara
        };
        int violations = 0;
        for (double[] s : spots) {
            int y = (int) s[2];
            Optional<EventHit> any = g.nearestEvent(s[0], s[1], y);
            Optional<EventHit> local = g.nearestLocalEvent(s[0], s[1], y);
            if (local.isPresent() && HistoryGazetteer.isRegional(local.get().event())) violations++;
            if (local.isPresent() && any.isPresent() && HistoryGazetteer.isRegional(any.get().event())) violations++;
            System.out.printf("%n%6d at %.2f,%.2f%n  nearestEvent:      %s%n  nearestLocalEvent: %s%n", y, s[0], s[1],
                    any.map(EventProbe::fmt).orElse("-"), local.map(EventProbe::fmt).orElse("-"));
        }
        System.out.printf("%nrule violations (local pin returned regional, or regional chosen over local): %d%n", violations);

        // coverage of the 400 land points of DensityProbe: any event vs local-only, by year
        double[][] pts = landPoints();
        int[] years = {-2500, -1500, -500, 1, 500, 1000, 1300, 1500, 1700, 1850, 1900, 1944, 2000};
        System.out.println("\n% of 400 land points with an event this year (local pins | local or regional news)");
        long q0 = System.nanoTime();
        int queries = 0;
        for (int y : years) {
            int loc = 0, anyc = 0;
            for (double[] p : pts) {
                if (g.nearestLocalEvent(p[0], p[1], y).isPresent()) loc++;
                if (g.nearestEvent(p[0], p[1], y).isPresent()) anyc++;
                queries += 2;
            }
            System.out.printf("  %6d  %5.1f%% | %5.1f%%%n", y, 100.0 * loc / pts.length, 100.0 * anyc / pts.length);
        }
        System.out.printf("query time: %.2f ms per query (%d queries)%n", (System.nanoTime() - q0) / 1e6 / queries, queries);
    }

    static String fmt(EventHit h) {
        Event e = h.event();
        String n = e.name().length() > 70 ? e.name().substring(0, 70) + "..." : e.name();
        return String.format("[%s %s r=%.0f %.0fkm] %s", e.kind(), HistoryGazetteer.isRegional(e) ? "REGIONAL" : "local",
                e.radiusKm(), h.distanceKm(), n);
    }

    /** The same 400 points DensityProbe uses: seed 42, its rough land mask. */
    static double[][] landPoints() {
        java.util.Random rnd = new java.util.Random(42);
        double[][] p = new double[400][];
        int n = 0;
        while (n < 400) {
            double la = -58 + rnd.nextDouble() * 141;
            double lo = -180 + rnd.nextDouble() * 360;
            if (DensityProbe.isLand(la, lo)) p[n++] = new double[] {la, lo};
        }
        return p;
    }
}
