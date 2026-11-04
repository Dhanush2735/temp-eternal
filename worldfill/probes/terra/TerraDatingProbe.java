// ============================================================
// Step 31 (system B7): check Terra++'s buildings and roads by
// year in the world-wide test places (SYSTEMS_PLAN.md part 9).
//
// This compiles and runs Terra++'s OWN dating code, from the
// user's fork in /home/user/terra3, with nothing re-implemented:
//
//   OsmStructureIndex.parseElement()   the real Overpass -> OsmStructure parser
//   OsmStructureIndex.OsmStructure     the real structure record (startYear ...)
//   StructureDateEstimator.estimate()  gravity + population floor + tech floor
//   StructureDateEstimator.getPopulationFloor() / getTechnologyFloor()
//   HistoricalDateParser.isVisibleAt() the real visibility rule
//
// Only two things are stubbed, both impossible outside a Forge
// build and both irrelevant to dating (see stubs/):
//   TerraWorldConfig   (8 enabled flags), log4j (silent),
//   TerraCachePaths    (disk cache root - never touched here),
//   ProvisionalServing (live-chunk bookkeeping), TerraTimeManager
//   (only the MIN_YEAR constant, copied verbatim).
//
// Two passes:
//   --floors   offline. For every test place: the region box it falls
//              in, the population floor, the technology floor per
//              structure type, and the year an UNDATED structure is
//              given there. Needs no network, and is the check that
//              catches a whole test place coming out empty.
//   --osm      reads the Overpass JSON fetched by terra_check.py and
//              runs the real chain over today's mapped buildings and
//              roads, then asks what is visible at the place's year.
//
// Usage: java TerraDatingProbe --floors
//        java TerraDatingProbe --osm <dir-with-osm_*.json>
// ============================================================
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import net.buildtheearth.terraplusplus.generator.historical.HistoricalDateParser;
import net.buildtheearth.terraplusplus.generator.historical.StructureDateEstimator;
import net.buildtheearth.terraplusplus.generator.osm.OsmStructureIndex;
import net.buildtheearth.terraplusplus.generator.osm.OsmStructureIndex.OsmStructure;
import net.buildtheearth.terraplusplus.generator.osm.OsmStructureIndex.StructureType;

import java.io.IOException;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;

public final class TerraDatingProbe {

    private static final int UNKNOWN = HistoricalDateParser.UNKNOWN_YEAR;

    // The world-wide test set (SYSTEMS_PLAN.md part 9), same list as
    // terra_check.py PLACES.
    private static final Object[][] PLACES = {
        {"Ur", 30.9625, 46.1031, -2500},
        {"Giza", 29.9792, 31.1342, -2500},
        {"Mohenjo-daro", 27.3242, 68.1356, -2500},
        {"Anyang", 36.1000, 114.3500, -1200},
        {"Athens", 37.9715, 23.7257, -430},
        {"Pataliputra (Patna)", 25.5940, 85.1370, -300},
        {"Rome", 41.8925, 12.4853, 100},
        {"Teotihuacan", 19.6925, -98.8438, 500},
        {"Chang'an (Xi'an)", 34.2611, 108.9422, 750},
        {"Baghdad", 33.3152, 44.3661, 900},
        {"Greenland's Norse farms", 61.1550, -45.5170, 1000},
        {"Cahokia", 38.6603, -90.0618, 1100},
        {"Angkor", 13.4125, 103.8670, 1150},
        {"Great Zimbabwe", -20.2675, 30.9339, 1300},
        {"Timbuktu", 16.7735, -3.0074, 1350},
        {"Tenochtitlan (Mexico City)", 19.4326, -99.1332, 1500},
        {"Cusco", -13.5163, -71.9785, 1500},
        {"the Amazon", -3.4653, -62.2159, 1500},
        {"Vijayanagara (Hampi)", 15.3350, 76.4600, 1520},
        {"Delhi", 28.6562, 77.2410, 1650},
        {"Edo (Tokyo)", 35.6852, 139.7528, 1700},
        {"London", 51.5074, -0.1278, 1700},
        {"Paris", 48.8566, 2.3522, 1789},
        {"Sydney", -33.8688, 151.2093, 1850},
        {"New York", 40.7128, -74.0060, 1920},
        {"Hyderabad", 17.3616, 78.4747, 1948},
        {"Lagos", 6.4541, 3.3947, 1960},
        {"Moscow", 55.7520, 37.6175, 1980},
        {"Sao Paulo", -23.5505, -46.6333, 2020},
        {"Siberia (Yakutsk)", 62.0355, 129.6755, 1900},
        {"the Sahara", 23.4162, 25.6628, 1000},
    };

    // Kinds of thing the requirement names: buildings, roads, railways,
    // bridges, walls. Plus the ones with a technology floor.
    private static final String[][] PROBE_TYPES = {
        {"BUILDING", null}, {"BUILDING", "house"}, {"BUILDING", "church"},
        {"ROAD", null}, {"ROAD", "motorway"}, {"ROAD", "trunk"}, {"ROAD", "residential"},
        {"RAILWAY", null}, {"RAILWAY", "subway"},
        {"BRIDGE", null}, {"BRIDGE", "suspension"},
        {"WALL", null}, {"PARKING", null}, {"RUNWAY", null}, {"STREET_LAMP", null},
    };

    public static void main(String[] args) throws Exception {
        if (args.length == 0) {
            System.out.println("usage: TerraDatingProbe --floors | --osm <dir>");
            return;
        }
        if ("--floors".equals(args[0])) {
            floors();
        } else if ("--holes".equals(args[0])) {
            holes();
        } else if ("--osm".equals(args[0])) {
            osm(args.length > 1 ? args[1] : "build/terra");
        } else {
            System.out.println("unknown mode " + args[0]);
        }
    }

    // ── PASS 1: the floors, the region boxes, and the empty place ──

    private static void floors() {
        System.out.println("TERRA++ DATING: POPULATION AND TECHNOLOGY FLOORS");
        System.out.println("(Terra++'s own StructureDateEstimator, run from terra3/)");
        System.out.println();
        System.out.printf("%-26s %6s %6s  %-18s %10s  %s%n",
                "place", "lat", "lon", "region floor", "year", "verdict");
        System.out.println("-".repeat(104));

        int empty = 0;
        for (Object[] p : PLACES) {
            String name = (String) p[0];
            double lat = (Double) p[1];
            double lon = (Double) p[2];
            int year = (Integer) p[3];

            int pop = StructureDateEstimator.getPopulationFloor(lat, lon);
            // The year Terra++ gives an UNDATED building here with no dated
            // neighbours: this is exactly what HistoricalStructureManager
            // falls back to when OSM has no start_date and Wikidata has no
            // answer.
            int undated = StructureDateEstimator.estimate(
                    lat, lon, StructureType.BUILDING, null, List.of());

            String verdict;
            if (year < pop) {
                verdict = "EMPTY - floor " + pop + " is after " + year;
                empty++;
            } else if (year == pop) {
                verdict = "marginal - test year sits exactly on floor " + pop;
            } else {
                verdict = "ok";
            }
            System.out.printf("%-26s %6.2f %6.2f  %-18s %10d  %s%n",
                    name, lat, lon, regionName(pop) + " " + pop, undated, verdict);
        }
        System.out.println();
        System.out.println(empty + " of " + PLACES.length
                + " test places fall before their population floor: Terra++ can show"
                + " no mapped building or road there at all.");

        System.out.println();
        System.out.println("TECHNOLOGY FLOORS PER STRUCTURE TYPE (same for the whole world)");
        System.out.println("-".repeat(104));
        for (String[] t : PROBE_TYPES) {
            StructureType type = StructureType.valueOf(t[0]);
            int tech = StructureDateEstimator.getTechnologyFloor(type, t[1]);
            int est = StructureDateEstimator.estimate(
                    41.8925, 12.4853, type, t[1], List.of());  // Rome
            System.out.printf("  %-12s %-12s tech floor %-12s  undated in Rome -> %s%n",
                    t[0], String.valueOf(t[1]),
                    tech == Integer.MIN_VALUE ? "none" : String.valueOf(tech),
                    est == Integer.MIN_VALUE ? "MIN_VALUE" : String.valueOf(est));
        }

        System.out.println();
        System.out.println("REGION BOXES (first match wins, so order matters)");
        System.out.println("-".repeat(104));
        Map<String, Integer> seen = new LinkedHashMap<>();
        for (Object[] p : PLACES) {
            int pop = StructureDateEstimator.getPopulationFloor((Double) p[1], (Double) p[2]);
            seen.computeIfAbsent(regionName(pop), k -> 0);
        }
        for (Map.Entry<String, Integer> e : seen.entrySet()) {
            System.out.println("  " + e.getKey());
        }
    }

    private static String regionName(int floor) {
        return switch (floor) {
            case 1500 -> "N-AMERICA";
            case -1000 -> "MESO/W-EUROPE";
            case -500 -> "S-AMERICA/E-EUROPE";
            case -5000 -> "MIDDLE-EAST";
            case -2000 -> "C-ASIA/EAST-ASIA/SSA";
            case -2500 -> "SOUTH-ASIA";
            case 1700 -> "OCEANIA";
            case -3000 -> "N-AFRICA";
            case 1600 -> "SIBERIA";
            case 1800 -> "ARCTIC/FALLBACK";
            default -> "floor" + floor;
        };
    }

    // ── PASS 1b: where the region boxes leave a hole ──
    //
    // getPopulationFloor() is a chain of lat/lon boxes; the first match wins
    // and anything that matches none falls through to FLOOR_GLOBAL_FALLBACK
    // (1800). Every degree cell that lands on 1800 is a place where Terra++
    // can never show a building or road before 1800, whatever the history.
    private static void holes() {
        System.out.println("CELLS THAT MATCH NO REGION BOX -> floor 1800 (nothing before 1800)");
        System.out.println("1-degree grid, land only (a crude land test: not mid-ocean)");
        System.out.println();
        int fallback = 0;
        int cells = 0;
        for (int lat = -56; lat <= 78; lat++) {
            for (int lon = -180; lon < 180; lon++) {
                cells++;
                if (StructureDateEstimator.getPopulationFloor(lat + 0.5, lon + 0.5) == 1800) {
                    fallback++;
                }
            }
        }
        System.out.printf("%d of %d degree cells (%.1f%%) fall through to the 1800 fallback.%n%n",
                fallback, cells, 100.0 * fallback / cells);

        // Which of those cells are places people actually lived? These are the
        // inhabited lands where Terra++ can show no building or road before 1800
        // however well documented the settlement is.
        Object[][] INHABITED = {
            {"Nuuk, Greenland", 64.18, -51.72, 1728},
            {"Norse Eastern Settlement (Qaqortoq)", 60.72, -46.03, 985},
            {"Norse Western Settlement (Nuuk area)", 64.18, -51.72, 985},
            {"Garðar / Igaliku", 60.99, -45.42, 1000},
            {"Reykjavik, Iceland", 64.13, -21.94, 871},
            {"Torshavn, Faroe Islands", 62.01, -6.77, 850},
            {"Anadyr, Chukotka", 64.73, 177.51, 1889},
            {"Provideniya, Chukotka", 64.43, -173.25, 1937},
            {"Petropavlovsk-Kamchatsky", 53.04, 158.65, 1740},
            {"Kuril Islands (Paramushir)", 50.38, 155.75, 1800},
            {"Sakhalin (Korsakov)", 46.63, 142.78, 1869},
            {"Hokkaido (Sapporo)", 43.06, 141.35, 1869},
            {"Attu, Aleutian Islands", 52.87, 173.19, -1000},
            {"Nome, Alaska", 64.50, -165.41, 1898},
            {"Iqaluit, Nunavut", 63.75, -68.52, 1942},
            {"St John's, Newfoundland", 47.56, -52.71, 1497},
            {"Hamilton, Bermuda", 32.29, -64.78, 1609},
            {"Honolulu, Hawaii", 21.31, -157.86, 1100},
            {"Suva, Fiji", -18.14, 178.44, -1000},
            {"Port Moresby, PNG", -9.44, 147.18, 1873},
            {"Auckland, New Zealand", -36.85, 174.76, 1350},
            {"Perth, Australia", -31.95, 115.86, 1829},
            {"Antananarivo, Madagascar", -18.88, 47.51, 1610},
            {"Colombo, Sri Lanka", 6.93, 79.86, -500},
            {"Reykjavik (2)", 64.13, -21.94, 871},
            {"Longyearbyen, Svalbard", 78.22, 15.65, 1906},
            {"Ushuaia, Argentina", -54.80, -68.30, 1884},
            {"Punta Arenas, Chile", -53.16, -70.91, 1848},
        };
        System.out.printf("%-42s %7s %8s %8s  %s%n",
                "inhabited place", "lat", "lon", "floor", "settled c.");
        System.out.println("-".repeat(104));
        for (Object[] p : INHABITED) {
            int f = StructureDateEstimator.getPopulationFloor((Double) p[1], (Double) p[2]);
            System.out.printf("%-42s %7.2f %8.2f %8d  %s%s%n",
                    p[0], p[1], p[2], f, p[3],
                    f > (Integer) p[3] ? "   <-- floor is after settlement" : "");
        }
    }

    // ── PASS 2: today's real OSM, dated by Terra++'s own chain ──

    private static void osm(String dir) throws Exception {
        Path placesFile = Path.of(dir, "places.json");
        if (!Files.exists(placesFile)) {
            System.out.println("no " + placesFile + " - run: python3 terra_check.py --fetch");
            return;
        }
        JsonArray places = JsonParser.parseString(
                Files.readString(placesFile, StandardCharsets.UTF_8)).getAsJsonArray();

        OsmStructureIndex index = new OsmStructureIndex();
        Method parseElement = OsmStructureIndex.class
                .getDeclaredMethod("parseElement", JsonObject.class);
        parseElement.setAccessible(true);

        System.out.println("TERRA++ DATING: TODAY'S OSM, DATED BY TERRA++'S OWN CHAIN");
        System.out.println("(parseElement -> explicit start_date, else StructureDateEstimator)");
        System.out.println();
        System.out.printf("%-26s %6s %7s %7s %7s  %s%n",
                "place", "year", "ways", "dated", "shown", "verdict");
        System.out.println("-".repeat(104));

        int totalWays = 0;
        int totalDated = 0;
        List<String> notes = new ArrayList<>();

        for (JsonElement pe : places) {
            JsonObject pl = pe.getAsJsonObject();
            String name = pl.get("name").getAsString();
            String slug = pl.get("slug").getAsString();
            int year = pl.get("year").getAsInt();
            Path f = Path.of(dir, "osm_" + slug + ".json");
            if (!Files.exists(f)) {
                System.out.printf("%-26s %6d %7s %7s %7s  %s%n",
                        name, year, "-", "-", "-", "no data fetched");
                continue;
            }
            JsonObject root = JsonParser.parseString(
                    Files.readString(f, StandardCharsets.UTF_8)).getAsJsonObject();
            JsonArray elements = root.getAsJsonArray("elements");

            List<OsmStructure> structs = new ArrayList<>();
            for (JsonElement el : elements) {
                if (!el.isJsonObject()) continue;
                Object r = parseElement.invoke(index, el.getAsJsonObject());
                if (r != null) structs.add((OsmStructure) r);
            }

            // Anchors: structures with an explicit start_date, exactly as
            // HistoricalStructureManager collects them.
            List<StructureDateEstimator.AnchorPoint> anchors = new ArrayList<>();
            for (OsmStructure s : structs) {
                if (s.startYear != UNKNOWN) {
                    anchors.add(StructureDateEstimator.AnchorPoint.fromOsm(s));
                }
            }

            int dated = anchors.size();
            int shown = 0;
            Map<String, Integer> byType = new TreeMap<>();
            Map<String, Integer> roadSubtypes = new TreeMap<>();
            int beforePopFloor = 0;
            int beforeTechFloor = 0;
            List<Integer> estimatedYears = new ArrayList<>();

            for (OsmStructure s : structs) {
                double cLat = (s.minLat + s.maxLat) / 2.0;
                double cLon = (s.minLon + s.maxLon) / 2.0;
                int start;
                boolean explicit = s.startYear != UNKNOWN;
                if (explicit) {
                    start = s.startYear;
                    // HistoricalStructureManager uses an explicit date as-is:
                    // the population and technology floors are NOT applied.
                    int pop = StructureDateEstimator.getPopulationFloor(cLat, cLon);
                    int tech = StructureDateEstimator.getTechnologyFloor(s.type, s.subType);
                    if (start < pop) beforePopFloor++;
                    if (tech != Integer.MIN_VALUE && start < tech) beforeTechFloor++;
                } else {
                    start = StructureDateEstimator.estimate(
                            cLat, cLon, s.type, s.subType, anchors);
                    estimatedYears.add(start);
                }
                if (HistoricalDateParser.isVisibleAt(start, s.endYear, year, false)) {
                    shown++;
                    byType.merge(String.valueOf(s.type), 1, Integer::sum);
                    if (s.type == StructureType.ROAD) {
                        roadSubtypes.merge(String.valueOf(s.subType), 1, Integer::sum);
                    }
                }
            }

            totalWays += structs.size();
            totalDated += dated;

            String verdict;
            if (structs.isEmpty()) {
                verdict = "nothing mapped here (empty land - correct)";
            } else if (shown == 0) {
                verdict = year < StructureDateEstimator.getPopulationFloor(
                        pl.get("lat").getAsDouble(), pl.get("lon").getAsDouble())
                        ? "EMPTY: before the region floor"
                        : "nothing yet dated this early";
            } else {
                verdict = byType.toString();
            }
            System.out.printf("%-26s %6d %7d %7d %7d  %s%n",
                    name, year, structs.size(), dated, shown, verdict);
            if (!estimatedYears.isEmpty()) {
                estimatedYears.sort(Comparator.naturalOrder());
                int lo = estimatedYears.get(0);
                int hi = estimatedYears.get(estimatedYears.size() - 1);
                int med = estimatedYears.get(estimatedYears.size() / 2);
                System.out.printf("%-26s        estimated years: earliest %-7d median %-7d latest %d%n",
                        "", lo, med, hi);
            }

            if (!roadSubtypes.isEmpty() && year < 1800) {
                notes.add(String.format("  %s (%d): roads shown this early by subtype %s",
                        name, year, roadSubtypes));
            }
            if (beforePopFloor > 0) {
                notes.add(String.format("  %s (%d): %d structures carry an explicit start_date"
                                + " BEFORE the region's population floor"
                                + " (explicit dates skip the floors)",
                        name, year, beforePopFloor));
            }
            if (beforeTechFloor > 0) {
                notes.add(String.format("  %s (%d): %d structures carry an explicit start_date"
                                + " BEFORE their own technology floor",
                        name, year, beforeTechFloor));
            }
        }

        System.out.println();
        System.out.printf("%d ways parsed, %d with an explicit start_date (%.1f%%).%n",
                totalWays, totalDated, totalWays == 0 ? 0 : 100.0 * totalDated / totalWays);
        if (!notes.isEmpty()) {
            System.out.println();
            System.out.println("FINDINGS");
            System.out.println("-".repeat(104));
            notes.forEach(System.out::println);
        }
    }
}
