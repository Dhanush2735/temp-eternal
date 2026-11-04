import com.eternalengine.buildings.FamousBuildings;
import com.eternalengine.terrabridge.TerraOsmBridge;
import com.eternalengine.terrabridge.TerraOsmBridge.OsmStructure;

import java.util.List;

/**
 * Step 32 (B8): the public hook between the map and the dated buildings.
 *
 * Terra++ draws the world from OpenStreetMap, and step 31 measured the consequence: 0.9% of mapped
 * structures carry a start date. {@code TerraOsmBridge.getFamousBuildings} is the dated answer
 * offered in Terra++'s own OsmStructure shape, so nothing downstream has to learn a second type.
 * This runs it outside Minecraft to make sure the shape it hands back is usable.
 */
public final class BuildingsHookProbe {

    static int ok;
    static int bad;

    static void check(boolean good, String what, String detail) {
        if (good) {
            ok++;
            System.out.println("OK   " + what);
        } else {
            bad++;
            System.out.println("FAIL " + what + "  -- " + detail);
        }
    }

    public static void main(String[] args) {
        // the four facts /ee check all asserts
        FamousBuildings fb = FamousBuildings.get();
        boolean col100 = fb.near(41.8902, 12.4922, 100, 25.0d, 60).stream()
                .anyMatch(b -> b.name().contains("Colosseum"));
        boolean col500bc = fb.near(41.8902, 12.4922, -500, 25.0d, 60).stream()
                .anyMatch(b -> b.name().contains("Colosseum"));
        boolean hampi1520 = fb.near(15.335, 76.46, 1520, 25.0d, 60).stream()
                .anyMatch(b -> b.name().contains("Hampi"));
        boolean hampi1700 = fb.near(15.335, 76.46, 1700, 25.0d, 60).stream()
                .anyMatch(b -> b.name().contains("Hampi"));
        check(col100 && !col500bc && hampi1520 && !hampi1700, "what /ee check all asserts: the Colosseum stands in "
                + "Rome in 100 and not in 500 BC; Hampi stands in 1520 and not in 1700 (1565 is the year "
                + "Vijayanagara fell)", "Rome 100 " + col100 + ", Rome -500 " + col500bc + ", Hampi 1520 "
                + hampi1520 + ", Hampi 1700 " + hampi1700);

        // the hook itself
        System.out.println("\n=== the hook: Rome, AD 100, 5 km ===");
        List<OsmStructure> rome = TerraOsmBridge.getInstance().getFamousBuildings(41.8902, 12.4922, 100, 5.0d);
        System.out.println("  " + rome.size() + " structures");
        for (int i = 0; i < Math.min(4, rome.size()); i++) {
            OsmStructure s = rome.get(i);
            System.out.printf("    %-26s type=%-7s kind=%-22s start=%-6s point=[%.3f, %.3f]%n",
                    s.name, s.type, s.buildingType, s.startDate, s.longitude, s.latitude);
        }
        check(!rome.isEmpty(), "the hook answers for Rome in 100", "empty");
        check(rome.stream().allMatch(s -> s.startDate != null && !s.startDate.isEmpty()),
                "every structure it hands back carries a year --- the one thing an OSM structure "
                        + "usually does not (0.9% of them do)", "some have none");
        check(rome.stream().allMatch(s -> s.geometry != null && !s.geometry.isEmpty()
                        && s.geometry.get(0).length == 2),
                "every one carries a point in Terra++ order, [longitude, latitude]", "some do not");
        check(rome.get(0).name.contains("Colosseum"), "the most famous comes first",
                rome.isEmpty() ? "empty" : rome.get(0).name);

        // and the year changes the answer
        int in100 = TerraOsmBridge.getInstance().getFamousBuildings(41.8902, 12.4922, 100, 5.0d).size();
        int in0 = TerraOsmBridge.getInstance().getFamousBuildings(41.8902, 12.4922, 0, 5.0d).size();
        int in1900 = TerraOsmBridge.getInstance().getFamousBuildings(41.8902, 12.4922, 1900, 5.0d).size();
        System.out.printf("  Rome: %d standing in 1 BC, %d in 100, %d in 1900%n", in0, in100, in1900);
        check(in0 < in100 && in100 < in1900, "the count grows with the year, which is what a dated "
                + "register is for", in0 + " / " + in100 + " / " + in1900);

        System.out.println("\n" + ok + " ok, " + bad + " failed");
        System.exit(bad == 0 ? 0 : 1);
    }
}
