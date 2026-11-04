import com.eternalengine.civilization.CivilizationManager;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonParser;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.util.HashSet;
import java.util.Set;
import com.eternalengine.civilization.PolityFacts;
import com.eternalengine.civilization.RulerRegister;

import java.util.*;

/**
 * R2-d2: every polity the register can name can now say its name and its years, with or without a
 * full civilization record. This probe asks the two questions a player would ask.
 */
public final class PolityFactsProbe {

    public static void main(String[] args) {
        RulerRegister rr = RulerRegister.get();
        // NB: no Minecraft here, so this manager is the throwing stub and has no records. The pack's
        // record ids are read straight from the shipped JSON instead, so the number below is the
        // game's number and not the harness's.
        CivilizationManager civs = null;
        Set<String> packIds = packRecordIds();

        System.out.println("== the display, for six ids a player can actually meet ==");
        for (String id : List.of("china_zhou", "ahmadnagar_sultanate", "mewar", "khmer_empire",
                "indus_valley", "cit-cit")) {
            System.out.printf("  %-24s -> %s%n", id, PolityFacts.describe(civs, id));
        }

        System.out.println();
        System.out.println("== coverage, over every polity the register can answer with ==");
        int total = 0, named = 0, dated = 0, recorded = 0;
        String firstNameless = null, firstUndated = null;
        for (RulerRegister.Polity p : rr.polities()) {
            String id = p.civHint();
            if (id == null || id.isBlank()) continue;
            total++;
            if (PolityFacts.name(id) != null) named++; else if (firstNameless == null) firstNameless = id;
            if (PolityFacts.span(id) != null) dated++; else if (firstUndated == null) firstUndated = id;
            if (packIds.contains(id)) recorded++;
        }
        System.out.println("  polities the register names : " + total);
        System.out.println("  can say their own name      : " + named + (firstNameless == null ? "" : "  (first nameless: " + firstNameless + ")"));
        System.out.println("  can say their own years     : " + dated + (firstUndated == null ? "" : "  (first undated: " + firstUndated + ")"));
        System.out.println("  have a full civilization record : " + recorded + "  (read from the pack, not the harness)");
        System.out.println("  -> before this step, only the " + recorded + " with a record could be read at all;"
                + " the other " + (total - recorded) + " read as \"no civilization called ...\"");
        System.out.println();
        System.out.println(named == total && dated == total
                ? "PASS - every named polity can say what it is and when it stood"
                : "FINDINGS - " + (total - named) + " nameless, " + (total - dated) + " undated");
    }

    /** The ids the shipped civilization pack carries a full record for. */
    private static Set<String> packRecordIds() {
        Set<String> ids = new HashSet<>();
        String path = "/data/eternalengine/eternal/civilizations/foundation_civilizations.json";
        try (InputStream in = PolityFactsProbe.class.getResourceAsStream(path)) {
            if (in == null) {
                System.out.println("  (the pack was not on the classpath: record count not measured)");
                return ids;
            }
            try (Reader reader = new InputStreamReader(in, StandardCharsets.UTF_8)) {
                JsonElement root = JsonParser.parseReader(reader);
                JsonArray list = root.isJsonArray() ? root.getAsJsonArray()
                        : root.getAsJsonObject().getAsJsonArray("civilizations");
                for (JsonElement element : list) {
                    if (element.isJsonObject() && element.getAsJsonObject().has("id")) {
                        ids.add(element.getAsJsonObject().get("id").getAsString());
                    }
                }
            }
        } catch (Exception e) {
            System.out.println("  (the pack could not be read: " + e.getMessage() + ")");
        }
        return ids;
    }
}
