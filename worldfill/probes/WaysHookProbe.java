import com.eternalengine.terrabridge.TerraOsmBridge;
import com.eternalengine.terrabridge.TerraOsmBridge.OsmStructure;

import java.util.List;

/**
 * Step 34 (B12, B14, B15, B18, B24, B26): the public hooks between the map and the dated world.
 *
 * <p>Terra++ draws from today's OpenStreetMap, and step 31 measured what that costs: Sydney in 1850
 * was given two railways that did not exist, Patna in 300 BC was given 98 modern roads. Three
 * methods on {@link TerraOsmBridge} are the mod's answer, and this runs them outside Minecraft —
 * with five stubs standing in for the logger, the config and one coordinate check — to make sure
 * what they hand back is usable by a caller that knows nothing about the registers.
 *
 * <ul>
 *   <li>{@code waysAllowed(lat, lon, year)} — may a railway, a road or a canal be drawn here yet?</li>
 *   <li>{@code getDatedWorks(lat, lon, year, km)} — the works standing here then, in Terra++'s own
 *       {@code OsmStructure} shape, every one carrying a year.</li>
 *   <li>{@code mineralsUnder(lat, lon, km)} — what lies under the ground here (system B24).</li>
 * </ul>
 */
public final class WaysHookProbe {

    private static int ok;
    private static int bad;

    private static void check(boolean good, String what, String detail) {
        if (good) {
            ok++;
            System.out.println("OK   " + what);
        } else {
            bad++;
            System.out.println("FAIL " + what + "  -- " + detail);
        }
    }

    public static void main(String[] args) {
        TerraOsmBridge bridge = TerraOsmBridge.getInstance();

        System.out.println("=== waysAllowed: may this network be drawn here yet? ===");
        // the two findings of step 31, answered
        var sydney1850 = bridge.waysAllowed(-33.8688d, 151.2093d, 1850);
        check(!sydney1850.rail(),
                "Sydney in 1850 may not draw a railway (Australia's first opened in 1854)",
                "rail from " + sydney1850.railFrom());
        var patna300bc = bridge.waysAllowed(25.594d, 85.137d, -300);
        check(!patna300bc.rail() && !patna300bc.road(),
                "Pataliputra in 300 BC may not draw a railway or a dated road",
                "rail from " + patna300bc.railFrom() + ", road from " + patna300bc.roadFrom());
        var rome100 = bridge.waysAllowed(41.8925d, 12.4853d, 100);
        check(!rome100.rail() && rome100.road(),
                "Rome in AD 100 may draw its Roman roads and no railway",
                "rail from " + rome100.railFrom() + ", road from " + rome100.roadFrom());
        var newYork1920 = bridge.waysAllowed(40.7128d, -74.006d, 1920);
        check(newYork1920.rail() && newYork1920.road(),
                "New York in 1920 may draw both",
                "rail from " + newYork1920.railFrom() + ", road from " + newYork1920.roadFrom());
        var edo1700 = bridge.waysAllowed(35.6852d, 139.7528d, 1700);
        check(edo1700.road() && edo1700.canal() && !edo1700.rail(),
                "Edo in 1700 may draw its roads and canals, and no railway",
                "rail from " + edo1700.railFrom() + ", canal from " + edo1700.canalFrom());
        var ur2500bc = bridge.waysAllowed(30.9625d, 46.1031d, -2500);
        check(!ur2500bc.any(),
                "Ur in 2500 BC is offered no dated network at all, rather than today's map",
                "rail " + ur2500bc.railFrom() + ", road " + ur2500bc.roadFrom());

        System.out.println();
        System.out.println("=== getDatedWorks: what stands here, in Terra++'s own shape ===");
        List<OsmStructure> ny = bridge.getDatedWorks(40.7128d, -74.006d, 1920, 25.0d);
        check(!ny.isEmpty(), "New York in 1920 is offered works", "none at all");
        boolean allDated = true;
        int stations = 0;
        for (OsmStructure s : ny) {
            if (s.startDate == null || s.startDate.isEmpty()) {
                allDated = false;
            }
            if ("station".equals(s.buildingType)) {
                stations++;
            }
            if (s.geometry == null || s.geometry.isEmpty()) {
                allDated = false;
            }
        }
        check(allDated, "every work handed back carries a start date and a geometry",
                "one of " + ny.size() + " is missing one");
        check(stations > 100, "New York's railway stations are among them", stations + " stations");
        List<OsmStructure> rome = bridge.getDatedWorks(41.8925d, 12.4853d, 100, 25.0d);
        boolean modern = rome.stream().anyMatch(s -> "station".equals(s.buildingType)
                || "works".equals(s.buildingType) || "air".equals(s.buildingType));
        check(!modern, "Rome in AD 100 is offered no station, factory or airport",
                "one was handed back");
        check(!rome.isEmpty(), "Rome in AD 100 is offered its dated bridges and ports",
                "nothing at all");
        boolean estimatedMarked = false;
        for (OsmStructure s : bridge.getDatedWorks(55.752d, 37.6175d, 1980, 25.0d)) {
            if (s.historicType != null && s.historicType.endsWith("(estimated)")) {
                estimatedMarked = true;
                break;
            }
        }
        check(estimatedMarked, "a work whose year is estimated says so in its historicType",
                "none was marked");

        System.out.println();
        System.out.println("=== mineralsUnder: what lies under the ground ===");
        List<String> cusco = bridge.mineralsUnder(-13.5163d, -71.9785d, 50.0d);
        check(cusco.contains("SILVER"), "silver lies under Cusco", String.join(", ", cusco));
        List<String> athens = bridge.mineralsUnder(37.9715d, 23.7257d, 50.0d);
        check(athens.contains("SILVER"), "silver lies under Athens (Laurium, 45 km away)",
                String.join(", ", athens));
        List<String> sahara = bridge.mineralsUnder(23.4162d, 25.6628d, 50.0d);
        check(sahara.isEmpty(), "the Sahara is honestly empty, not guessed at",
                String.join(", ", sahara));

        System.out.println();
        System.out.println(ok + " checks passed, " + bad + " failed");
        System.exit(bad == 0 ? 0 : 1);
    }
}
