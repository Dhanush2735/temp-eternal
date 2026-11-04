import com.eternalengine.civilization.CountryGrid;
import com.eternalengine.civilization.SettlementRank;
import com.eternalengine.towns.BuildingCulture;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;

/**
 * Step 33, part 5: what the building culture register answers, for the world-wide test set and for
 * the places where the ranking rule was in doubt. Run by worldfill/probe_towns_culture.sh.
 */
public final class BuildingCultureProbe {

    private record Place(String name, double lat, double lon, int year) {
    }

    private static Place pt(String name, double lat, double lon, int year) {
        return new Place(name, lat, lon, year);
    }

    /** The 31 test places (SYSTEMS_PLAN.md part 9), each in its own year. */
    private static final List<Place> TESTS = List.of(
        pt("Ur", 30.9625, 46.1031, -2500),
        pt("Giza", 29.9792, 31.1342, -2500),
        pt("Mohenjo-daro", 27.3242, 68.1356, -2500),
        pt("Anyang", 36.1, 114.35, -1200),
        pt("Athens", 37.9715, 23.7257, -430),
        pt("Pataliputra", 25.594, 85.137, -300),
        pt("Rome", 41.8925, 12.4853, 100),
        pt("Teotihuacan", 19.6925, -98.8438, 500),
        pt("Chang'an", 34.2611, 108.9422, 750),
        pt("Baghdad", 33.3152, 44.3661, 900),
        pt("Greenland Norse", 61.155, -45.517, 1000),
        pt("Cahokia", 38.6603, -90.0618, 1100),
        pt("Angkor", 13.4125, 103.867, 1150),
        pt("Great Zimbabwe", -20.2675, 30.9339, 1300),
        pt("Timbuktu", 16.7735, -3.0074, 1350),
        pt("Tenochtitlan", 19.4326, -99.1332, 1500),
        pt("Cusco", -13.5163, -71.9785, 1500),
        pt("the Amazon", -3.4653, -62.2159, 1500),
        pt("Vijayanagara", 15.335, 76.46, 1520),
        pt("Delhi", 28.6562, 77.241, 1650),
        pt("Edo", 35.6852, 139.7528, 1700),
        pt("London", 51.5074, -0.1278, 1700),
        pt("Paris", 48.8566, 2.3522, 1789),
        pt("Sydney", -33.8688, 151.2093, 1850),
        pt("New York", 40.7128, -74.006, 1920),
        pt("Hyderabad", 17.3616, 78.4747, 1948),
        pt("Lagos", 6.4541, 3.3947, 1960),
        pt("Moscow", 55.752, 37.6175, 1980),
        pt("Sao Paulo", -23.5505, -46.6333, 2020),
        pt("Yakutsk", 62.0355, 129.6755, 1900),
        pt("the Sahara", 23.4162, 25.6628, 1000)
    );

    /** Places where a coarse box or an era row could have taken the answer, and did not. */
    private static final List<Place> SPOTS = List.of(
        pt("Lhasa", 29.65, 91.1, 1650),
        pt("Kathmandu", 27.7, 85.3, 1700),
        pt("Leh", 34.2, 77.6, 1650),
        pt("Kashgar", 39.5, 76.0, 1200),
        pt("Dunhuang", 40.1, 94.7, 800),
        pt("Lucknow", 26.8, 80.9, 1650),
        pt("Manaus", -3.1, -60.0, 1500),
        pt("Belem", -1.45, -48.5, 1500),
        pt("Iquitos", -3.7, -73.2, 1500),
        pt("Reykjavik", 64.1, -21.9, 1000),
        pt("Nuuk", 64.2, -51.7, 1900),
        pt("Anchorage", 61.2, -149.9, 1800),
        pt("Tucson", 32.2, -110.9, 1300),
        pt("Miami", 25.8, -80.2, 1700),
        pt("Krakow", 50.1, 20.0, 1350),
        pt("Istanbul", 41.0, 29.0, 1600),
        pt("Cairo", 30.0, 31.2, 1300),
        pt("Marrakesh", 31.6, -8.0, 1400),
        pt("Kilwa", -8.96, 39.5, 1400),
        pt("Jakarta", -6.2, 106.8, 1700),
        pt("Hanoi", 21.0, 105.8, 1500),
        pt("Samarkand", 39.7, 66.9, 1400),
        pt("Ulaanbaatar", 47.9, 106.9, 1700)
    );

    public static void main(String[] args) {
        BuildingCulture bc = BuildingCulture.get();
        System.out.println("load      : " + bc.summary());
        System.out.println("problem   : " + bc.problem() + " (" + bc.loadMillis() + " ms)");
        System.out.println("sources   : " + bc.sources().size() + " articles cited");
        System.out.println("countries : " + CountryGrid.get().size() + " in the grid");
        if (!bc.loaded()) {
            System.out.println("FAILED: the pack did not load");
            System.exit(1);
        }

        System.out.println("\n-- the 31 test places, in their own year (town) --");
        Set<String> used = new LinkedHashSet<>();
        for (Place p : TESTS) {
            String code = CountryGrid.get().codeAt(p.lat(), p.lon());
            Optional<BuildingCulture.Reading> r = bc.at(p.lat(), p.lon(), p.year(), SettlementRank.TOWN);
            if (r.isEmpty()) {
                System.out.printf("  %-16s %6d  %-4s  NOTHING%n", p.name(), p.year(), code);
                continue;
            }
            BuildingCulture.Reading v = r.get();
            used.add(v.id());
            System.out.printf("  %-16s %6d  %-4s  %-26s %s%n", p.name(), p.year(), code, v.id(),
                    clip(v.house(), 58));
            System.out.printf("  %-16s %6s  %-4s  %-26s walls %s; roof %s%n", "", "", "",
                    "", clip(v.wall(), 46), clip(v.roof(), 30));
            System.out.printf("  %-16s %6s  %-4s  %-26s lanes %s; water %s; after dark %s%n", "", "",
                    "", "", clip(v.surface(), 26), clip(v.water(), 26), clip(v.light(), 22));
        }

        System.out.println("\n-- where the ranking rule was in doubt --");
        for (Place p : SPOTS) {
            String code = CountryGrid.get().codeAt(p.lat(), p.lon());
            BuildingCulture.Reading v = bc.at(p.lat(), p.lon(), p.year(), SettlementRank.TOWN)
                    .orElseThrow(() -> new IllegalStateException("no answer at " + p.name()));
            used.add(v.id());
            System.out.printf("  %-14s %6d  %-4s  %-26s %s%n", p.name(), p.year(), code, v.id(),
                    clip(v.house(), 50));
        }

        // A village keeps its thatch after the city has turned to concrete: the atlas decides, not us.
        System.out.println("\n-- the same place, three sizes of town, 1890 --");
        for (SettlementRank rank : new SettlementRank[] {SettlementRank.VILLAGE, SettlementRank.TOWN,
                                                          SettlementRank.CITY}) {
            for (Place p : List.of(pt("Yorkshire", 53.9, -1.1, 1890), pt("Bengal", 23.8, 89.5, 1890),
                                   pt("Japan", 35.0, 135.8, 1890))) {
                BuildingCulture.Reading v = bc.at(p.lat(), p.lon(), p.year(), rank).orElseThrow();
                System.out.printf("  %-9s %-11s %-8s walls %-44s light %s%n", p.name(), rank,
                        v.id(), clip(v.wall(), 42), clip(v.light(), 26));
            }
        }

        // Every row should be reachable, and every country-year should have an answer.
        List<String> never = new ArrayList<>();
        for (BuildingCulture.Words w : bc.rows()) {
            if (!used.contains(w.id()) && !"default".equals(w.id()) && !"early_camp".equals(w.id())) {
                never.add(w.id());
            }
        }
        int empty = 0;
        int total = 0;
        for (int i = 0; i < CountryGrid.get().size(); i++) {
            String code = CountryGrid.get().code(i);
            double lat = CountryGrid.get().mainLat(i);
            double lon = CountryGrid.get().mainLon(i);
            for (int year = -3000; year <= 2000; year += 250) {
                total++;
                if (bc.at(code, lat, lon, year, SettlementRank.TOWN).isEmpty()) {
                    empty++;
                }
            }
        }
        System.out.println("\ncountry-years with no answer: " + empty + " of " + total);
        System.out.println("rows not reached by the test set: " + never.size()
                + (never.isEmpty() ? "" : " -> " + String.join(", ", never)));
        System.out.println(empty == 0 && bc.rowCount() > 100 ? "OK" : "CHECK");
    }

    private static String clip(String s, int n) {
        String v = s == null ? "" : s.replace("\n", " ");
        return v.length() <= n ? v : v.substring(0, n - 1) + "\u2026";
    }
}
