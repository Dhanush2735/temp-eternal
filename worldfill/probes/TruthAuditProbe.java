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

/**
 * S1 — the truth audit, pilot (2026-10-24).
 *
 * <p>The project has measured whether an answer RESOLVES. It has never measured whether an answer is
 * TRUE. This asks the ruler register "who ruled here in this year" for a spread of places and years,
 * and prints the answer plus the ids behind it, so each one can be checked against a source by hand.
 *
 * <p>The spread is chosen to cover four continents and twenty-five centuries, and to include places
 * where the register OUGHT to say nothing (open sea, empty desert) — because a register that invents a
 * ruler over the Pacific is wrong in the most expensive way.
 */
public final class TruthAuditProbe {

    /** name, lat, lon, year */
    private static final Object[][] SAMPLES = {
            {"Athens", 37.98, 23.73, -430},
            {"Rome", 41.89, 12.49, 117},
            {"Baghdad", 33.31, 44.36, 900},
            {"Delhi", 28.61, 77.21, 1300},
            {"Cusco", -13.53, -71.97, 1500},
            {"London", 51.51, -0.13, 1700},
            {"Kyoto", 35.01, 135.77, 1000},
            {"Timbuktu", 16.77, -3.00, 1400},
            {"Tenochtitlan", 19.43, -99.13, 1500},
            {"Ayutthaya", 14.35, 100.57, 1600},
            {"Mohenjo-daro", 27.33, 68.14, -2500},
            {"open Pacific", 0.0, -160.0, 1500},
    };

    public static void main(String[] args) {
        RulerRegister rr = RulerRegister.get();
        System.out.println(rr.summary().display());
        List<WhoRuled.Cap> caps = packCapitals();
        System.out.println("pack civilizations available as a fallback: " + caps.size());
        System.out.println();
        System.out.printf("%-16s %6s %15s  %s%n", "place", "year", "answer", "detail");
        int answered = 0;
        int empty = 0;
        for (Object[] row : SAMPLES) {
            String name = (String) row[0];
            double lat = (Double) row[1];
            double lon = (Double) row[2];
            int year = (Integer) row[3];
            var hit = rr.rulerAt(lat, lon, year);
            WhoRuled.Answer layered = WhoRuled.answer(caps, lat, lon, year);
            if (!layered.known()) {
                empty++;
                System.out.printf("%-16s %6d %15s  %s%n", name, year, "(nobody)",
                        "no register polity and no pack capital within " + Math.round(WhoRuled.PACK_CAPITAL_KM) + " km");
                continue;
            }
            answered++;
            if (hit.isPresent()) {
                var h = hit.get();
                System.out.printf("%-16s %6d %15s  %s [%d-%d] %s  (%.0f km)%n",
                        name, year, h.ruler(), h.civHint(), h.start(), h.end(), h.wikidata(), h.distanceKm());
            } else {
                System.out.printf("%-16s %6d %15s  %s <- REGISTER SILENT, pack answered%n",
                        name, year, layered.name(), layered.civId());
            }
        }
        System.out.println();
        System.out.println("answered: " + answered + ", empty: " + empty + " of " + SAMPLES.length);
        System.out.println("Each line above must now be checked against a source. A wrong answer is one where");
        System.out.println("the polity named did not hold that place in that year, or where a polity is named");
        System.out.println("over open sea.");
    }

    /** The pack's civilizations as capitals, read straight from the shipped JSON (no Minecraft here). */
    private static List<WhoRuled.Cap> packCapitals() {
        List<WhoRuled.Cap> out = new ArrayList<>();
        String path = "/data/eternalengine/eternal/civilizations/foundation_civilizations.json";
        try (InputStream in = TruthAuditProbe.class.getResourceAsStream(path)) {
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
