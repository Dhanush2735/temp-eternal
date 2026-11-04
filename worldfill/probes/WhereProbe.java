import com.eternalengine.here.HereAndNow;
import com.eternalengine.civilization.HistoryGazetteer;
import com.eternalengine.civilization.TownFacts;
import com.eternalengine.civilization.RulerRegister;

/** One-off: the user's exact doubt point (17.4346, 78.5016), year 3000 BC and neighbours. */
public class WhereProbe {
    public static void main(String[] args) {
        double lat = 17.434603127612625, lon = 78.50157785389962;
        int[] years = {-3000, -2500, -2000, -1500, -1000, -500, 1, 500, 1000, 1500};
        HistoryGazetteer g = HistoryGazetteer.get();
        for (int y : years) {
            var site = g.nearestOccupied(lat, lon, y);
            var hin = g.estimatedHinterland(lat, lon, y);
            var town = TownFacts.get().near(lat, lon, y);
            var ruler = RulerRegister.get().rulerAt(lat, lon, y);
            System.out.println("==== year " + y + " (" + HereAndNow.yearText(y) + ")");
            System.out.println("  site:     " + site.map(h -> h.site().displayName() + " @ " + h.site().occupiedStart() + ".."
                    + h.site().occupiedEnd() + " " + h.distanceKm() + " km rank " + h.site().rankAt(y)).orElse("none"));
            System.out.println("  hinter:   " + hin.map(h -> h.site().displayName() + " " + h.distanceKm() + " km").orElse("none"));
            System.out.println("  town:     " + town.map(t -> t.nameIn(y) + " exists=" + t.existsIn(y) + " people=" + t.peopleIn(y)).orElse("none"));
            System.out.println("  ruler:    " + ruler.map(r -> r.ruler() + " (" + r.start() + ".." + r.end() + ") est=" + r.estimated()).orElse("none"));
        }
    }
}
