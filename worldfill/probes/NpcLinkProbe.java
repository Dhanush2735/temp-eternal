import com.eternalengine.civilization.Civilization;
import com.eternalengine.civilization.CivilizationManager;
import com.eternalengine.civilization.EventNews;
import com.eternalengine.civilization.HistoricalPresence;

import java.util.Optional;

/**
 * Turn 50 question: can villagers already use the money, trade, food and faith systems?
 *
 * Those systems (economy, farming, classes, religion, war) run on the civilization table. The
 * villagers get their civilization id from the history data (HistoricalPresence.spawnCivId).
 * This probe loads the same table the server loads (packaged table plus CivSynthesis) and, for
 * 40 well-known towns and years, prints which civilization a villager there would belong to and
 * whether the table gives that civilization real numbers (population, so tax and food) or only
 * a synthetic stub, or does not know it at all. It also prints the civ table's religion next to
 * the faith line villagers already say (history data), to show where two sources disagree.
 */
public class NpcLinkProbe {
    record Place(String name, double lat, double lon, int year) {}

    public static void main(String[] args) {
        CivilizationManager m = new CivilizationManager();
        m.loadCivilizations(null, null);
        Place[] places = {
            new Place("Paris", 48.8566, 2.3522, 1789), new Place("Hampi", 15.335, 76.46, 1520),
            new Place("Golconda", 17.383, 78.401, 1650), new Place("Rome", 41.8925, 12.4853, 100),
            new Place("Hyderabad", 17.385, 78.4867, 1850), new Place("Delhi", 28.6562, 77.241, 1650),
            new Place("Agra", 27.1767, 78.0081, 1600), new Place("Varanasi", 25.3176, 82.9739, 1600),
            new Place("Kolkata", 22.5726, 88.3639, 1850), new Place("Chennai", 13.0827, 80.2707, 1700),
            new Place("Mumbai", 18.9388, 72.8354, 1700), new Place("Thanjavur", 10.787, 79.1378, 1010),
            new Place("Patna", 25.5941, 85.1376, -250), new Place("London", 51.5074, -0.1278, 1600),
            new Place("Madrid", 40.4168, -3.7038, 1600), new Place("Vienna", 48.2082, 16.3738, 1700),
            new Place("Moscow", 55.7558, 37.6173, 1700), new Place("Istanbul", 41.0082, 28.9784, 1550),
            new Place("Athens", 37.9715, 23.7257, -430), new Place("Cairo", 30.0444, 31.2357, 1300),
            new Place("Baghdad", 33.3152, 44.3661, 900), new Place("Damascus", 33.5138, 36.2765, 700),
            new Place("Jerusalem", 31.7683, 35.2137, 30), new Place("Isfahan", 32.6546, 51.668, 1600),
            new Place("Samarkand", 39.6542, 66.9597, 1400), new Place("Beijing", 39.9042, 116.4074, 1600),
            new Place("Xi'an", 34.3416, 108.9398, 750), new Place("Kyoto", 35.0116, 135.7681, 1600),
            new Place("Angkor", 13.4125, 103.867, 1150), new Place("Timbuktu", 16.7666, -3.0026, 1350),
            new Place("Great Zimbabwe", -20.2674, 30.9338, 1300), new Place("Tenochtitlan", 19.4326, -99.1332, 1500),
            new Place("Cusco", -13.5319, -71.9675, 1500), new Place("Boston", 42.3601, -71.0589, 1775),
            new Place("Memphis (Egypt)", 29.8449, 31.2502, -2500), new Place("Babylon", 32.5364, 44.4209, -600),
            new Place("Mohenjo-daro", 27.3292, 68.1389, -2500), new Place("Kano", 12.0022, 8.592, 1500),
            new Place("Lisbon", 38.7223, -9.1393, 1500), new Place("Venice", 45.4408, 12.3155, 1500),
        };
        int real = 0, stub = 0, unknown = 0, noCiv = 0;
        System.out.println("place | year | villager's civ id | in the civ table? | population | civ-table religion | faith line villagers say");
        for (Place p : places) {
            HistoricalPresence.Result r = HistoricalPresence.query(m, p.lat(), p.lon(), p.year());
            String civId = r.spawnCivId();
            Optional<Civilization> civ = m.getCivilization(civId);
            String kind;
            String pop = "-";
            String rel = "-";
            if (civId == null || civId.isBlank() || civId.equals("neutral") || civId.equals("present")
                    || civId.equals("ohm") || civId.equals("witness")) {
                kind = "no civilization";
                noCiv++;
            } else if (civ.isEmpty()) {
                kind = "NOT KNOWN";
                unknown++;
            } else {
                Civilization c = civ.get();
                boolean synthetic = c.governmentType() != null && c.governmentType().startsWith("SYNTHETIC");
                pop = Long.toString(c.population());
                rel = c.religionId() == null ? "-" : c.religionId();
                if (synthetic || c.population() <= 0) {
                    kind = synthetic ? "stub (made up from the id)" : "record, population 0";
                    stub++;
                } else {
                    kind = "real record";
                    real++;
                }
            }
            String faith = EventNews.cultureLine(r);
            int i = faith.indexOf("The main faith");
            faith = i >= 0 ? faith.substring(i).trim() : (faith.isBlank() ? "-" : "(no faith said)");
            System.out.println(p.name() + " | " + p.year() + " | " + civId + " | " + kind + " | " + pop + " | " + rel + " | " + faith);
        }
        System.out.println();
        System.out.println("SUMMARY of " + places.length + " towns: real record " + real + ", stub or population 0 " + stub
            + ", civ id the table does not know " + unknown + ", no civilization " + noCiv);
        System.out.println("table size: " + m.size() + " civilizations");
    }
}
