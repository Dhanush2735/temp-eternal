import com.eternalengine.civilization.EventNews;
import com.eternalengine.civilization.HistoricalPresence;
import com.eternalengine.civilization.LeaderRegister;
import com.eternalengine.civilization.RulerRegister;

import java.util.List;

/**
 * Step 25 (the history data fix): what villagers say about who rules, and in which language and faith, at the
 * world-wide test places of SYSTEMS_PLAN part 9, the towns of the turn-51 spot check and the places of the known
 * problems. Uses the mod's own lookups (HistoricalPresence, RulerRegister, LeaderRegister, EventNews).
 *
 * Usage: HistoryFixProbe brief|full|world
 *   brief  one line per place: state, head of state, civilization id, the language-and-faith line
 *   full   every villager line per place (as ChatFactsProbe)
 *   world  SYSTEMS_PLAN part 9's world sample: 400 land points in each test year
 * The step-25 expectations themselves are part 14 of /ee check all (HistoryChecks.FIXES).
 */
public class HistoryFixProbe {

    record Place(String name, double lat, double lon, int year) {}

    static final List<Place> PLACES = List.of(
            // SYSTEMS_PLAN part 9: every continent, every era
            new Place("Ur", 30.96, 46.10, -2500), new Place("Giza", 29.98, 31.13, -2500),
            new Place("Mohenjo-daro", 27.33, 68.14, -2500), new Place("Anyang", 36.10, 114.39, -1200),
            new Place("Athens", 37.97, 23.73, -430), new Place("Pataliputra", 25.61, 85.14, -300),
            new Place("Rome", 41.89, 12.49, 100), new Place("Teotihuacan", 19.69, -98.84, 500),
            new Place("Chang'an", 34.27, 108.95, 750), new Place("Baghdad", 33.31, 44.36, 900),
            new Place("Brattahlid", 61.16, -45.42, 1000), new Place("Cahokia", 38.655, -90.062, 1100),
            new Place("Angkor", 13.41, 103.87, 1150), new Place("Great Zimbabwe", -20.27, 30.93, 1300),
            new Place("Timbuktu", 16.77, -3.01, 1350), new Place("Tenochtitlan", 19.43, -99.13, 1500),
            new Place("Cusco", -13.53, -71.97, 1500), new Place("Amazon", -3.10, -60.02, 1500),
            new Place("Vijayanagara", 15.33, 76.46, 1520), new Place("Delhi", 28.65, 77.23, 1650),
            new Place("Edo", 35.68, 139.76, 1700), new Place("London", 51.51, -0.12, 1700),
            new Place("Paris", 48.86, 2.35, 1789), new Place("Sydney", -33.87, 151.21, 1850),
            new Place("New York", 40.71, -74.00, 1920), new Place("Hyderabad", 17.385, 78.4867, 1948),
            new Place("Lagos", 6.45, 3.39, 1960), new Place("Moscow", 55.76, 37.62, 1980),
            new Place("Sao Paulo", -23.55, -46.63, 2020), new Place("Yakutsk", 62.03, 129.73, 1900),
            new Place("Sahara", 23.0, 10.0, 1000),
            // turn-51 spot check towns
            new Place("Hyderabad", 17.385, 78.4867, 1850), new Place("Varanasi", 25.32, 83.01, 1600),
            new Place("Chennai", 13.08, 80.27, 1700), new Place("Mumbai", 18.94, 72.83, 1700),
            new Place("London", 51.51, -0.12, 1600), new Place("Vienna", 48.21, 16.37, 1700),
            new Place("Kolkata", 22.57, 88.36, 1850), new Place("Agra", 27.18, 78.01, 1650),
            new Place("Madrid", 40.42, -3.70, 1600), new Place("Cairo", 30.04, 31.24, 1300),
            new Place("Moscow", 55.76, 37.62, 1700), new Place("Thanjavur", 10.79, 79.14, 1010),
            // the known problems and the most-heard patterns of the step-12 fact check
            new Place("Mumbai", 18.94, 72.83, 1948), new Place("Delhi", 28.65, 77.23, 1949),
            new Place("Karachi", 24.86, 67.01, 1950), new Place("Gulbarga", 17.33, 76.83, 1900),
            new Place("Aurangabad", 19.88, 75.34, 1900), new Place("Warangal", 17.97, 79.59, 1850),
            new Place("Prague", 50.08, 14.42, 1980), new Place("Dresden", 51.05, 13.74, 1750),
            new Place("Jerusalem", 31.78, 35.22, 1940), new Place("Warsaw", 52.23, 21.01, 1946),
            new Place("Budapest", 47.50, 19.04, 1946), new Place("Bucharest", 44.43, 26.10, 1946),
            new Place("Sofia", 42.70, 23.32, 1946), new Place("Berlin", 52.52, 13.40, 1946),
            new Place("St Petersburg", 59.94, 30.31, 1850), new Place("St Petersburg", 59.94, 30.31, 1900),
            new Place("Paris", 48.86, 2.35, 1900), new Place("Vienna", 48.21, 16.37, 1900),
            new Place("London", 51.51, -0.12, 1850), new Place("London", 51.51, -0.12, 1950),
            new Place("Lisbon", 38.72, -9.14, 1990), new Place("Copenhagen", 55.68, 12.57, 1900),
            new Place("Athens", 37.97, 23.73, 1900), new Place("Port-au-Prince", 18.54, -72.34, 1900),
            new Place("Bamako", 12.64, -8.00, 2000), new Place("Phnom Penh", 11.56, 104.92, 1976),
            new Place("Tripoli", 32.89, 13.19, 1990), new Place("Seoul", 37.57, 126.98, 2000),
            new Place("Mumbai", 18.94, 72.83, 2026), new Place("Moscow", 55.76, 37.62, 2026),
            new Place("Washington", 38.90, -77.04, 2026), new Place("Baku", 40.41, 49.87, 2000),
            new Place("Aden", 12.79, 45.03, 2000), new Place("Moroni", -11.70, 43.26, 2000),
            new Place("Dili", -8.56, 125.57, 2000), new Place("Tehran", 35.69, 51.39, 1985),
            new Place("Amsterdam", 52.37, 4.90, 1990), new Place("Jakarta", -6.21, 106.85, 1990),
            new Place("Caracas", 10.49, -66.88, 1900), new Place("Lima", -12.05, -77.04, 1970),
            new Place("Stockholm", 59.33, 18.07, 1750), new Place("Qi (Linzi)", 36.87, 118.35, -520),
            new Place("Munich", 48.14, 11.58, 1400), new Place("Montevideo", -34.90, -56.16, 1970),
            new Place("Monaco", 43.73, 7.42, 1950), new Place("Lima", -12.05, -77.04, 1900),
            new Place("Nairobi", -1.29, 36.82, 1930), new Place("Kabul", 34.53, 69.17, 1985),
            new Place("Ulaanbaatar", 47.92, 106.92, 1960), new Place("Vienna", 48.21, 16.37, 1950),
            new Place("Bratislava", 48.15, 17.11, 1980), new Place("Tallinn", 59.44, 24.75, 1960),
            new Place("Pyongyang", 39.02, 125.75, 1950), new Place("Tabriz", 38.08, 46.29, 1945));

    public static void main(String[] args) {
        String mode = args.length > 0 ? args[0] : "brief";
        System.out.println(RulerRegister.get().summary().display());
        System.out.println(LeaderRegister.get().summary());
        if (mode.equals("world")) {
            world();
            return;
        }
        for (Place p : PLACES) {
            HistoricalPresence.Result r = HistoricalPresence.query(null, p.lat(), p.lon(), p.year());
            String state = r.ruler().map(RulerRegister.Hit::ruler).orElse("-");
            String civ = r.spawnCivId();
            if (mode.equals("full")) {
                System.out.println("== " + p.name() + " " + p.year() + "  [civ " + civ + "]");
                String[] lines = {EventNews.placeLine(r), EventNews.rulerLine(r), EventNews.cultureLine(r),
                        EventNews.famousLine(r, p.year()), EventNews.wayOfLifeLine(r), EventNews.tradeLine(r),
                        EventNews.roadLine(r)};
                for (String line : lines) {
                    if (line != null && !line.isBlank()) {
                        System.out.println("  " + line.trim());
                    }
                }
                r.event().ifPresent(e -> System.out.println("  " + EventNews.rumor(e.event(), p.year()).trim()));
            } else {
                String head = r.ruler().flatMap(h -> LeaderRegister.get().facts(h.wikidata()))
                        .flatMap(f -> f.headIn(p.year())).map(LeaderRegister.Reign::display).orElse("-");
                String culture = EventNews.cultureLine(r);
                System.out.println(p.name() + " " + p.year() + " | " + state + " | " + head + " | " + civ + " | "
                        + (culture.length() > 110 ? culture.substring(0, 110) + "…" : culture));
            }
        }
    }

    /**
     * SYSTEMS_PLAN part 9's world sample: the 400 random land points of step 4 (HistoryChecks.landPoints, seed 42) in
     * each test year. For each year: how many have people, how many of those hear a state named and a ruler named, and
     * whether empty land stays empty ("I have not heard of a town here").
     */
    static void world() {
        double[][] pts = com.eternalengine.civilization.HistoryChecks.landPoints();
        int[] years = {-2500, -500, 1, 1000, 1500, 1900, 2000, 2026};
        System.out.println("year | points with people | of those: a state named | a ruler named | empty land that says nobody lives here");
        for (int y : years) {
            int occ = 0, state = 0, head = 0, empty = 0, quiet = 0;
            for (double[] p : pts) {
                HistoricalPresence.Result r = HistoricalPresence.query(null, p[0], p[1], y);
                if (r.occupied()) {
                    occ++;
                    if (r.ruler().isPresent()) {
                        state++;
                        if (r.ruler().flatMap(h -> LeaderRegister.get().facts(h.wikidata()))
                                .flatMap(f -> f.headIn(y)).isPresent()) {
                            head++;
                        }
                    }
                } else {
                    empty++;
                    quiet += EventNews.placeLine(r).startsWith("I have not heard") ? 1 : 0;
                }
            }
            System.out.printf(java.util.Locale.ROOT, "%5d | %3d | %3d (%2.0f%%) | %3d (%2.0f%%) | %d of %d%n", y, occ, state,
                    occ == 0 ? 0.0 : 100.0 * state / occ, head, occ == 0 ? 0.0 : 100.0 * head / occ, quiet, empty);
        }
    }
}
