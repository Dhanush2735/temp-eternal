import com.eternalengine.civilization.EventNews;
import com.eternalengine.civilization.HistoricalPresence;
import com.eternalengine.civilization.HistoryGazetteer;
import com.eternalengine.civilization.LeaderRegister;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.TreeMap;

/**
 * Data-use check, part 2 (worldfill/probe_data_use.sh): how much of the history data reaches a player,
 * measured with the mod's own lookup code.
 *
 * <ol>
 *   <li><b>Events heard at home.</b> For every event pin: standing on its own spot in its own first
 *       year, is it the news the game picks ({@code HistoryGazetteer.nearestEvent})? A pin that loses
 *       even there is shadowed by another pin (same spot, or a nearer one that covers it).</li>
 *   <li><b>What villagers can say.</b> At population-weighted sample points (data_use_sample.py), which
 *       of the talk lines have something to say, and how many different events and rulers are
 *       heard.</li>
 * </ol>
 * Prints one JSON object.
 */
public class DataUseProbe {

    public static void main(String[] args) throws Exception {
        String points = args.length > 0 ? args[0] : System.getProperty("user.home") + "/.cache/data_use/points.tsv";
        StringBuilder json = new StringBuilder("{\n");

        // ---------------------------------------------------------------- 1. events heard at home
        HistoryGazetteer g = HistoryGazetteer.get();
        List<HistoryGazetteer.Event> all = g.allEvents();
        Map<String, long[]> byPack = new TreeMap<>();      // pack -> total, heard, regional, shadowedBySameSpot
        Map<String, long[]> byKind = new TreeMap<>();
        long t0 = System.currentTimeMillis();
        for (HistoryGazetteer.Event e : all) {
            String pack = e.packId() == null ? "?" : e.packId();
            long[] p = byPack.computeIfAbsent(pack, k -> new long[4]);
            long[] k = byKind.computeIfAbsent(e.kind() == null ? "?" : e.kind(), x -> new long[4]);
            p[0]++;
            k[0]++;
            boolean regional = HistoryGazetteer.isRegional(e);
            if (regional) {
                p[2]++;
                k[2]++;
            }
            if (!e.activeIn(e.start())) {
                continue;
            }
            Optional<HistoryGazetteer.EventHit> hit = g.nearestEvent(e.lat(), e.lon(), e.start());
            if (hit.isPresent() && hit.get().event().id().equals(e.id())) {
                p[1]++;
                k[1]++;
            } else if (hit.isPresent() && hit.get().distanceKm() < 0.001d) {
                p[3]++;
                k[3]++;
            }
        }
        json.append("\"events_total\": ").append(all.size()).append(",\n");
        json.append("\"events_seconds\": ").append((System.currentTimeMillis() - t0) / 1000.0).append(",\n");
        json.append("\"events_by_pack\": {");
        appendCounts(json, byPack);
        json.append("},\n\"events_by_kind\": {");
        appendCounts(json, byKind);
        json.append("},\n");

        // ---------------------------------------------------------------- 2. what villagers can say
        Map<Integer, double[]> share = new TreeMap<>();
        Map<Integer, Set<String>> eventsHeard = new TreeMap<>();
        Map<Integer, Set<String>> headsHeard = new TreeMap<>();
        String[] names = {"points", "occupied", "named_place", "people_model", "state_named", "ruler_named",
                "culture_line", "local_language", "faith", "famous_line", "famous_died", "famous_born_near",
                "famous_talk", "way_of_life", "trade_route", "roman_road", "news_any", "news_local",
                "news_regional", "way_of_life_survey", "faith_shares", "talk_lines_avg"};
        Set<String> allEvents = new HashSet<>();
        Set<String> allHeads = new HashSet<>();
        try (BufferedReader in = new BufferedReader(new FileReader(points))) {
            String line;
            while ((line = in.readLine()) != null) {
                String[] f = line.split("\t");
                int year = Integer.parseInt(f[0]);
                double lat = Double.parseDouble(f[1]);
                double lon = Double.parseDouble(f[2]);
                double[] s = share.computeIfAbsent(year, y -> new double[names.length]);
                Set<String> ev = eventsHeard.computeIfAbsent(year, y -> new HashSet<>());
                Set<String> hd = headsHeard.computeIfAbsent(year, y -> new HashSet<>());
                HistoricalPresence.Result r = HistoricalPresence.query(null, lat, lon, year);
                s[0]++;
                if (r.occupied()) s[1]++;
                if (r.site().isPresent()) s[2]++;
                if (r.peopleHere()) s[3]++;
                String ruler = EventNews.rulerLine(r);
                if (!ruler.isBlank()) s[4]++;
                if (ruler.contains(", ruled by ")) {
                    s[5]++;
                    r.ruler().flatMap(h -> LeaderRegister.get().facts(h.wikidata()))
                            .flatMap(fa -> fa.headIn(year)).ifPresent(h -> {
                                hd.add(h.display());
                                allHeads.add(h.display() + "@" + h.start());
                            });
                }
                String culture = EventNews.cultureLine(r);
                if (!culture.isBlank()) s[6]++;
                if (culture.contains("people here speak")) s[7]++;
                if (culture.contains("faith")) s[8]++;
                String famous = EventNews.famousLine(r, 7L);
                if (!famous.isBlank()) s[9]++;
                if (famous.startsWith("Sad news")) s[10]++;
                if (famous.contains("born near here")) s[11]++;
                if (famous.startsWith("People here talk about")) s[12]++;
                if (!EventNews.wayOfLifeLine(r).isBlank()) s[13]++;
                if (!EventNews.tradeLine(r).isBlank()) s[14]++;
                if (!EventNews.roadLine(r).isBlank()) s[15]++;
                if (r.event().isPresent()) {
                    s[16]++;
                    HistoryGazetteer.Event e = r.event().get().event();
                    if (HistoryGazetteer.isRegional(e)) s[18]++; else s[17]++;
                    ev.add(e.id());
                    allEvents.add(e.id());
                }
                if (EventNews.wayOfLifeSource(r).startsWith("ArchaeoGLOBE")
                        && !EventNews.wayOfLifeLine(r).startsWith("Most people around here")) s[19]++;
                if (culture.contains("%")) s[20]++;
                int lines = 0;
                for (String l : new String[] {ruler, culture, famous, EventNews.wayOfLifeLine(r), EventNews.tradeLine(r),
                        EventNews.roadLine(r)}) {
                    if (l != null && !l.isBlank()) lines++;
                }
                s[21] += lines;
            }
        }
        json.append("\"sample\": {");
        boolean first = true;
        for (var en : share.entrySet()) {
            double[] s = en.getValue();
            json.append(first ? "\n" : ",\n").append("  \"").append(en.getKey()).append("\": {");
            first = false;
            for (int i = 0; i < names.length; i++) {
                double v = i == 0 ? s[0] : (i == names.length - 1 ? s[i] / s[0] : 100.0 * s[i] / s[0]);
                json.append(i == 0 ? "" : ", ").append("\"").append(names[i]).append("\": ")
                        .append(String.format(java.util.Locale.ROOT, i == 0 ? "%.0f" : "%.1f", v));
            }
            json.append(", \"distinct_events\": ").append(eventsHeard.get(en.getKey()).size());
            json.append(", \"distinct_heads\": ").append(headsHeard.get(en.getKey()).size()).append("}");
        }
        json.append("\n},\n\"sample_distinct_events\": ").append(allEvents.size());
        json.append(",\n\"sample_distinct_heads\": ").append(allHeads.size()).append("\n}");
        System.out.println(json);
    }

    private static void appendCounts(StringBuilder json, Map<String, long[]> m) {
        boolean first = true;
        for (var en : m.entrySet()) {
            long[] v = en.getValue();
            json.append(first ? "\n" : ",\n").append("  \"").append(en.getKey()).append("\": {\"total\": ").append(v[0])
                    .append(", \"heard_at_home\": ").append(v[1]).append(", \"regional\": ").append(v[2])
                    .append(", \"hidden_by_same_spot\": ").append(v[3]).append("}");
            first = false;
        }
    }
}
