import com.eternalengine.civilization.HistoryGazetteer;
import com.eternalengine.civilization.HistoryGazetteer.Event;
import com.eternalengine.civilization.HistoryGazetteer.EventHit;

import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Same-answer check for the per-year event index (run by worldfill/probe_index.sh).
 * Writes one line per query (nearestEvent, nearestLocalEvent, eventsNear 100 km) to args[0],
 * so the output of the old linear scan and of the index can be diffed byte for byte.
 */
public class IndexProbe {
    public static void main(String[] args) throws Exception {
        long t0 = System.nanoTime();
        HistoryGazetteer g = HistoryGazetteer.get();
        System.out.printf("load %.1f s, events=%d%n", (System.nanoTime() - t0) / 1e9, g.eventCount());
        List<double[]> q = new ArrayList<>();
        double[][] land = EventProbe.landPoints();
        int[] years = {-2500, -1500, -500, 1, 500, 1000, 1300, 1500, 1700, 1850, 1900, 1944, 1990, 2000, 2010, 2020, 2024};
        for (int y : years) for (double[] p : land) q.add(new double[] {p[0], p[1], y});
        java.util.Random rnd = new java.util.Random(7);
        List<Event> all = g.allEvents();
        for (int i = 0; i < all.size(); i += 37) {
            Event e = all.get(i);
            q.add(new double[] {e.lat() + (rnd.nextDouble() - 0.5), e.lon() + (rnd.nextDouble() - 0.5), e.start()});
        }
        long q0 = System.nanoTime();
        try (PrintWriter out = new PrintWriter(args[0], "UTF-8")) {
            for (double[] p : q) {
                int y = (int) p[2];
                Optional<EventHit> a = g.nearestEvent(p[0], p[1], y);
                Optional<EventHit> l = g.nearestLocalEvent(p[0], p[1], y);
                List<EventHit> near = g.eventsNear(p[0], p[1], y, 100.0d);
                StringBuilder ids = new StringBuilder();
                for (EventHit h : near) ids.append(h.event().id()).append(',');
                out.printf("%.4f %.4f %d | %s | %s | %d %08x%n", p[0], p[1], y,
                        a.map(h -> h.event().id() + String.format("@%.3f", h.distanceKm())).orElse("-"),
                        l.map(h -> h.event().id() + String.format("@%.3f", h.distanceKm())).orElse("-"),
                        near.size(), ids.toString().hashCode());
            }
        }
        System.out.printf("%d queries, %.3f ms per query (3 lookups each)%n", q.size(), (System.nanoTime() - q0) / 1e6 / q.size());
    }
}
