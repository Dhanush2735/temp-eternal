import com.eternalengine.civilization.HistoryGazetteer;

/** What the gazetteer layers say at a few well-known places and years (site, else hinterland). */
public class SpotProbe {
    public static void main(String[] args) {
        HistoryGazetteer g = HistoryGazetteer.get();
        Object[][] spots = {
            {"Rome", 41.90, 12.50, 100}, {"Rome", 41.90, 12.50, 1600}, {"Athens", 37.98, 23.73, -400},
            {"Gaza", 31.50, 34.47, -1200}, {"Trier", 49.75, 6.64, 300}, {"Countryside, Gaul", 46.5, 3.0, 200},
            {"Chang'an (Xi'an)", 34.27, 108.95, 750}, {"Kaifeng", 34.80, 114.31, 1100}, {"Rural Sichuan", 30.6, 104.5, 1500},
            {"Beijing", 39.90, 116.40, 1600}, {"Paris", 48.86, 2.35, 1500}, {"London", 51.51, -0.13, 1700},
            {"Cairo", 30.04, 31.24, 1300}, {"Baghdad", 33.31, 44.36, 900}, {"Tenochtitlan", 19.43, -99.13, 1500},
            {"Cuzco", -13.53, -71.97, 1500}, {"Timbuktu", 16.77, -3.01, 1450}, {"Hyderabad", 17.39, 78.49, 1700},
            {"Telangana village", 18.18, 78.45, 1900}, {"Mid-Sahara", 23.0, 10.0, 1000}, {"Siberia", 60.0, 100.0, 1000},
            {"Ohio valley", 39.0, -84.0, 1200}, {"Nile delta village", 30.8, 31.0, -1500}};
        for (Object[] s : spots) {
            double la = (Double) s[1], lo = (Double) s[2];
            int y = (Integer) s[3];
            String what;
            var site = g.nearestOccupied(la, lo, y);
            if (site.isPresent()) {
                var h = site.get();
                what = String.format("site \"%s\" (%s, %s, %.0f km, %d..%s, civ %s)", h.site().name(), h.site().packId(),
                        h.site().rankAt(y).name().toLowerCase(), h.distanceKm(), h.site().occupiedStart(),
                        h.site().occupiedEnd() >= 9999 ? "now" : Integer.toString(h.site().occupiedEnd()), h.site().civHint());
            } else {
                var hin = g.estimatedHinterland(la, lo, y);
                what = hin.map(h -> String.format("estimated countryside village of \"%s\" (%s, %.0f km)",
                        h.site().name(), h.site().packId(), h.distanceKm())).orElse("nobody (no site, no hinterland)");
            }
            var box = g.borderAt(la, lo, y);
            System.out.printf("%-20s %6d  %s%s%n", s[0], y, what, box.map(b -> "  [box " + b.civId() + "]").orElse(""));
        }
    }
}
