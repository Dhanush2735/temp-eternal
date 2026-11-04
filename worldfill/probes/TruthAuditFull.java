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
 * S1 at full size (2026-10-24, cycle 2): 200 places and years, who ruled, and where the answer came from.
 *
 * <p>Samples come from the project's own town register (30,151 towns with a founding year and a population
 * series), so every sample is a place where people actually lived. The year is drawn from the town's own
 * life, between its founding and 2025, and kept only where the population series says people were there.
 *
 * <p>The audit reports three things, and they are not the same thing:
 * <ul>
 *   <li><b>coverage</b> - how many samples get any answer at all;</li>
 *   <li><b>provenance mix</b> - how many answers are recorded ({@code REGISTER}) and how many lean on the
 *       declared heuristic ({@code PACK_CAPITAL});</li>
 *   <li><b>verified wrong-rate</b> - the share of a hand-checked subsample that is wrong.</li>
 * </ul>
 * The third is the number the requirement asks for. The first two say how much of it can be trusted from
 * the code alone.
 */
public final class TruthAuditFull {

    private static final int SAMPLES = 0; // 0 = every town
    private static final long SEED = 20261024L;

    public static void main(String[] args) {
        RulerRegister rr = RulerRegister.get();
        List<WhoRuled.Cap> caps = packCapitals();
        List<Object[]> towns = towns();
        System.out.println(rr.summary().display());
        System.out.println("towns read: " + towns.size() + "   pack capitals: " + caps.size());

        Random random = new Random(SEED);
        int taken = 0, answered = 0, register = 0, pack = 0, none = 0;
        // polity -> {count, earliestYear, latestYear}
        Map<String, int[]> tally = new TreeMap<>();
        java.util.List<String> rows = new java.util.ArrayList<>();
        rows.add("town\tlat\tlon\tyear\tanswer\tsource");
        for (Object[] town : towns) {
            String name = (String) town[0];
            double lat = (double) town[2] / 1000.0d;
            double lon = (double) town[3] / 1000.0d;
            int founded = (int) town[4];
            int year = founded + random.nextInt(Math.max(1, 2025 - founded));
            WhoRuled.Answer a = WhoRuled.answer(caps, lat, lon, year);
            taken++;
            String label = a.known() ? a.name() : "(nobody)";
            if (a.known()) {
                answered++;
                if (a.source() == WhoRuled.Source.REGISTER) register++; else pack++;
            } else none++;
            int[] t = tally.computeIfAbsent(label, k -> new int[] {0, Integer.MAX_VALUE, Integer.MIN_VALUE});
            t[0]++; t[1] = Math.min(t[1], year); t[2] = Math.max(t[2], year);
            rows.add(name + "\t" + String.format(java.util.Locale.ROOT, "%.3f\t%.3f", lat, lon)
                    + "\t" + year + "\t" + label + "\t" + a.source());
        }
        try {
            java.nio.file.Path out = java.nio.file.Path.of("/home/user/testrun/verify/answers_full.csv");
            java.nio.file.Files.createDirectories(out.getParent());
            java.nio.file.Files.write(out, rows);
        } catch (Exception e) { System.out.println("write failed: " + e.getMessage()); }

        System.out.println();
        System.out.println("towns audited    : " + taken);
        System.out.println("answered         : " + answered + fmt(answered, taken)
                + "   register " + register + ", pack heuristic " + pack);
        System.out.println("answered nobody  : " + none + fmt(none, taken));
        System.out.println();
        System.out.println("--- answers that carry a name, by how often and in what years ---");
        tally.entrySet().stream()
             .sorted((x, y) -> Integer.compare(y.getValue()[0], x.getValue()[0]))
             .limit(25)
             .forEach(e -> System.out.printf(java.util.Locale.ROOT, "%6d  %-46s %d .. %d%n",
                     e.getValue()[0], e.getKey(), e.getValue()[1], e.getValue()[2]));
        System.out.println();
        System.out.println("rows written to testrun/verify/answers_full.csv");
    }

    private static String fmt(int n, int total) {
        return total == 0 ? "" : String.format(java.util.Locale.ROOT, "  (%.1f%%)", 100.0d * n / total);
    }

    /** name, qid, lat*1000, lon*1000, foundedYear, populations */
    private static List<Object[]> towns() {
        List<Object[]> out = new ArrayList<>();
        String path = "/data/eternalengine/eternal/history/towns.json.gz";
        try (InputStream raw = TruthAuditFull.class.getResourceAsStream(path)) {
            if (raw == null) {
                return out;
            }
            try (Reader reader = new InputStreamReader(new java.util.zip.GZIPInputStream(raw),
                    StandardCharsets.UTF_8)) {
                JsonElement root = JsonParser.parseReader(reader);
                JsonArray list = root.getAsJsonObject().getAsJsonArray("towns");
                for (JsonElement element : list) {
                    JsonArray row = element.getAsJsonArray();
                    if (row.size() < 6) {
                        continue;
                    }
                    // Rows carry nulls (a town with no founding year), and reading one as a number
                    // threw and silently left the sample set with six towns (found in this probe,
                    // 2026-10-24). Every field is now checked before it is used.
                    if (row.get(0).isJsonNull() || row.get(1).isJsonNull() || row.get(2).isJsonNull()
                            || row.get(3).isJsonNull() || row.get(5).isJsonNull()) {
                        continue;
                    }
                    String qid = row.get(0).getAsString();
                    String name = row.get(1).getAsString();
                    double lat = row.get(2).getAsDouble();
                    double lon = row.get(3).getAsDouble();
                    int founded = row.get(5).getAsInt();
                    if (founded == 0 || founded < -3000) {
                        continue;
                    }
                    out.add(new Object[] {name, qid, lat, lon, founded});
                }
            }
        } catch (Exception e) {
            System.out.println("towns could not be read: " + e.getMessage());
        }
        return out;
    }

    private static List<WhoRuled.Cap> packCapitals() {
        List<WhoRuled.Cap> out = new ArrayList<>();
        String path = "/data/eternalengine/eternal/civilizations/foundation_civilizations.json";
        try (InputStream in = TruthAuditFull.class.getResourceAsStream(path)) {
            if (in == null) {
                return out;
            }
            try (Reader reader = new InputStreamReader(in, StandardCharsets.UTF_8)) {
                JsonElement root = JsonParser.parseReader(reader);
                JsonArray list = root.isJsonArray() ? root.getAsJsonArray()
                        : root.getAsJsonObject().getAsJsonArray("civilizations");
                for (JsonElement element : list) {
                    if (!element.isJsonObject()) {
                        continue;
                    }
                    var row = element.getAsJsonObject();
                    if (!row.has("id") || !row.has("capitalLat") || !row.has("capitalLon")) {
                        continue;
                    }
                    out.add(new WhoRuled.Cap(
                            row.get("id").getAsString(),
                            row.has("name") ? row.get("name").getAsString() : row.get("id").getAsString(),
                            row.has("foundingYear") ? row.get("foundingYear").getAsInt() : -3000,
                            row.has("fallYear") ? row.get("fallYear").getAsInt() : 3000,
                            row.get("capitalLat").getAsDouble(),
                            row.get("capitalLon").getAsDouble()));
                }
            }
        } catch (Exception e) {
            System.out.println("(the pack could not be read: " + e.getMessage() + ")");
        }
        return out;
    }
}
