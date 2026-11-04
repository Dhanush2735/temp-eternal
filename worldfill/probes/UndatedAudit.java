import com.eternalengine.civilization.RulerRegister;
import com.eternalengine.civilization.WhoRuled;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonParser;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.TreeMap;
import java.util.Map;

/**
 * The 68% the first audit never saw (2026-10-24).
 *
 * <p>The 200-sample and full-scale audits drew each year from a town's founding year, so every town with
 * a blank founding year was invisible to them - 20,361 of 30,151. Geneva is one of those, and a single
 * Wikipedia page showed four wrong answers there.
 *
 * <p>This pass samples only the undated towns and asks the <b>register</b> whether it knows the cell at a
 * year drawn at random across 3000 BC .. 2025. A town's own birth is unknown; who held the ground is a
 * separate question, and this measures that question alone.
 */
public final class UndatedAudit {

    private static final int SAMPLES = 600;
    private static final long SEED = 771077L;

    public static void main(String[] args) {
        List<WhoRuled.Cap> caps = packCapitals();
        List<Object[]> undated = undatedTowns();
        System.out.println(RulerRegister.get().summary().display());
        System.out.println("undated towns: " + undated.size() + "   pack capitals: " + caps.size());

        Random random = new Random(SEED);
        int answered = 0, none = 0, taken = 0;
        Map<String, int[]> tally = new TreeMap<>();
        Map<String, int[]> byEra = new TreeMap<>();
        List<String> rows = new ArrayList<>();
        rows.add("town\tlat\tlon\tyear\tanswer\tsource");
        while (taken < SAMPLES && !undated.isEmpty()) {
            Object[] t = undated.get(random.nextInt(undated.size()));
            String name = (String) t[0];
            double lat = (double) t[1] / 1000.0d;
            double lon = (double) t[2] / 1000.0d;
            int year = -3000 + random.nextInt(3000 + 2025);
            WhoRuled.Answer a = WhoRuled.answer(caps, lat, lon, year);
            taken++;
            String label = a.known() ? a.name() : "(nobody)";
            if (a.known()) answered++; else none++;
            tally.computeIfAbsent(label, k -> new int[] {0, Integer.MAX_VALUE, Integer.MIN_VALUE});
            int[] s = tally.get(label);
            s[0]++; s[1] = Math.min(s[1], year); s[2] = Math.max(s[2], year);
            String era = (year < -1000 ? "3000-1000 BC" : year < 1 ? "1000 BC-AD 1"
                    : year < 1000 ? "AD 1-1000" : year < 1500 ? "AD 1000-1500"
                    : year < 1800 ? "AD 1500-1800" : "AD 1800-2025");
            byEra.computeIfAbsent(era, k -> new int[] {0, 0});
            byEra.get(era)[0]++;
            if (a.known()) byEra.get(era)[1]++;
            rows.add(name + "\t" + String.format(java.util.Locale.ROOT, "%.3f\t%.3f", lat, lon)
                    + "\t" + year + "\t" + label + "\t" + a.source());
        }
        try {
            java.nio.file.Files.write(java.nio.file.Path.of("/home/user/testrun/verify/answers_undated.csv"), rows);
        } catch (Exception e) { System.out.println("write failed: " + e.getMessage()); }

        System.out.println();
        System.out.println("samples                 : " + taken);
        System.out.println("register could answer   : " + answered + pct(answered, taken));
        System.out.println("register said nobody    : " + none + pct(none, taken));
        System.out.println();
        System.out.println("--- by era (answered / sampled) ---");
        byEra.forEach((era, c) -> System.out.printf(java.util.Locale.ROOT,
                "  %-14s %3d / %3d = %5.1f%%%n", era, c[1], c[0], 100.0 * c[1] / c[0]));
        System.out.println();
        System.out.println("--- the ten commonest answers ---");
        tally.entrySet().stream().sorted((x, y) -> Integer.compare(y.getValue()[0], x.getValue()[0])).limit(10)
             .forEach(e -> System.out.printf(java.util.Locale.ROOT, "%6d  %-40s %d .. %d%n",
                     e.getValue()[0], e.getKey(), e.getValue()[1], e.getValue()[2]));
    }

    private static String pct(int n, int total) {
        return String.format(java.util.Locale.ROOT, "  (%.1f%%)", 100.0 * n / total);
    }

    /** name, lat*1000, lon*1000 - towns with a null founding year. */
    private static List<Object[]> undatedTowns() {
        List<Object[]> out = new ArrayList<>();
        try (InputStream raw = UndatedAudit.class.getResourceAsStream(
                "/data/eternalengine/eternal/history/towns.json.gz")) {
            if (raw == null) return out;
            try (Reader r = new InputStreamReader(new java.util.zip.GZIPInputStream(raw), StandardCharsets.UTF_8)) {
                JsonArray list = JsonParser.parseReader(r).getAsJsonObject().getAsJsonArray("towns");
                for (JsonElement el : list) {
                    JsonArray row = el.getAsJsonArray();
                    if (row.size() < 6 || row.get(1).isJsonNull() || row.get(2).isJsonNull()
                            || row.get(3).isJsonNull() || !row.get(5).isJsonNull()) {
                        continue;
                    }
                    out.add(new Object[] {row.get(1).getAsString(), row.get(2).getAsDouble(),
                            row.get(3).getAsDouble()});
                }
            }
        } catch (Exception e) { System.out.println("towns: " + e.getMessage()); }
        return out;
    }

    private static List<WhoRuled.Cap> packCapitals() {
        List<WhoRuled.Cap> out = new ArrayList<>();
        try (InputStream in = UndatedAudit.class.getResourceAsStream(
                "/data/eternalengine/eternal/civilizations/foundation_civilizations.json")) {
            if (in == null) return out;
            try (Reader r = new InputStreamReader(in, StandardCharsets.UTF_8)) {
                JsonElement root = JsonParser.parseReader(r);
                JsonArray list = root.isJsonArray() ? root.getAsJsonArray()
                        : root.getAsJsonObject().getAsJsonArray("civilizations");
                for (JsonElement el : list) {
                    if (!el.isJsonObject()) continue;
                    var row = el.getAsJsonObject();
                    if (!row.has("capitalLat") || !row.has("capitalLon")) continue;
                    out.add(new WhoRuled.Cap(row.get("id").getAsString(),
                            row.has("name") ? row.get("name").getAsString() : row.get("id").getAsString(),
                            row.has("foundingYear") ? row.get("foundingYear").getAsInt() : -3000,
                            row.has("fallYear") ? row.get("fallYear").getAsInt() : 3000,
                            row.get("capitalLat").getAsDouble(), row.get("capitalLon").getAsDouble()));
                }
            }
        } catch (Exception e) { System.out.println("pack: " + e.getMessage()); }
        return out;
    }
}
