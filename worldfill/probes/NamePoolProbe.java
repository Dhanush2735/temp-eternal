import com.eternalengine.civilization.LocalLanguages;
import com.eternalengine.villager.VillagerNameDatabase;

import java.util.Locale;
import java.util.Random;

/**
 * Step 17, fix B: which name list a townsperson gets at a place (worldfill/probe_name_pools.sh). The real
 * VillagerNameDatabase and the mod's own language data (LocalLanguages, the same answer as the talk's "People here
 * speak Bengali"), at places a player meets, with the state id the game passes. Before step 17 only the state
 * counted: every id with "india" got the Deccan's Telugu names, and a state no rule knew got "Alex Stone".
 * Exit code 1 if a place with an expected list gets another one.
 */
public class NamePoolProbe {
    private static int pass;
    private static int fail;

    public static void main(String[] args) {
        VillagerNameDatabase names = new VillagerNameDatabase();
        LocalLanguages languages = LocalLanguages.get();
        Object[][] places = {
                // place, lat, lon, year, the ruling state's id, expected list (null: print only)
                {"Calcutta (Kolkata)", 22.57, 88.36, 1850, "british_india", "indic"},
                {"Hyderabad", 17.385, 78.4867, 1948, "republic_of_india", "deccan"},
                {"Hyderabad", 17.385, 78.4867, 1700, "mughal_empire", "deccan"},
                {"Golconda", 17.38, 78.40, 1600, "golconda_sultanate", "deccan"},
                {"Delhi", 28.61, 77.21, 1650, "mughal_empire", "indic"},
                {"Madras (Chennai)", 13.08, 80.27, 1800, "british_india", null}, // no language point within 300 km
                {"Bombay (Mumbai)", 19.08, 72.88, 1900, "british_raj", "indic"}, // was the Greek-Roman list
                {"Beijing", 39.90, 116.40, 1700, "qing_dynasty", "east_asian"},
                {"Istanbul", 41.01, 28.98, 1600, "ottoman_empire", "persianate"},
                {"Rome", 41.89, 12.49, 1600, "papal_states", "mediterranean"},
                {"Lagos", 6.45, 3.39, 1900, "british_empire", "african"},
                {"Mexico City", 19.43, -99.13, 1700, "spanish_empire", null},
                {"London", 51.51, -0.13, 1850, "british_empire", null},
                {"Rome (before 1500: the state decides)", 41.89, 12.49, 100, "roman_empire", "mediterranean"},
        };
        for (Object[] p : places) {
            String place = (String) p[0];
            double lat = (Double) p[1];
            double lon = (Double) p[2];
            int year = (Integer) p[3];
            String civ = (String) p[4];
            String want = (String) p[5];
            String before = civ.contains("india") ? "deccan" : names.poolFor(civ);
            String language = languages.peoplesLanguage(lat, lon, year).map(h -> h.language().name()).orElse("-");
            String pool = names.poolForPlace(lat, lon, year, civ);
            Random random = new Random(year * 31L + place.hashCode());
            String sample = names.getRandomName(pool, "", "farmer", false, random) + "; "
                    + names.getRandomName(pool, "", "merchant", true, random) + "; "
                    + names.getRandomName(pool, "", "citizen", false, random);
            String line = String.format(Locale.ROOT, "%s %d (%s): people speak %s -> list %s (before step 17: %s), e.g. %s",
                    place, year, civ, language, pool, before, sample);
            if (want == null) {
                System.out.println("  INFO " + line);
            } else if (want.equals(pool)) {
                pass++;
                System.out.println("  PASS " + line);
            } else {
                fail++;
                System.out.println("  FAIL " + line + " -- expected " + want);
            }
        }
        System.out.println("SUMMARY pass=" + pass + " fail=" + fail);
        System.exit(fail == 0 ? 0 : 1);
    }
}
