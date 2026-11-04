// Step 44 part E (E5: disruptions and replacements): does a failed harvest actually make the
// grain short, and does the mod know what people ate instead?
//
// The checks are about the join, not the file: that a disaster's own field loss reaches a crop,
// that a plague's mortality reaches a smith, that an earthquake's damage reaches the roof over
// the work, and that the substitute offered is one the atlas says exists here and now.
import com.eternalengine.money.ProductAtlas;
import com.eternalengine.money.ProductAtlas.Product;
import com.eternalengine.money.Shortages;
import com.eternalengine.money.Shortages.Instead;
import com.eternalengine.money.Shortages.Shock;
import com.eternalengine.money.Shortages.Supply;

import java.util.List;

public final class Step44ShortageProbe {

    static int checks = 0;
    static int fails = 0;

    static void ok(boolean cond, String what) {
        checks++;
        if (!cond) {
            fails++;
            System.out.println("  FAIL  " + what);
        }
    }

    public static void main(String[] args) {
        ProductAtlas a = ProductAtlas.get();
        Shortages s = Shortages.get();
        System.out.println(a.summary());
        System.out.println(s.summary());
        ok(s.loaded(), "the substitute pack loads: " + s.problem());
        ok(s.count() > 30, "it carries a real number of products (" + s.count() + ")");

        // ------------------------------------------------------------------ the table itself
        Product wheat = a.product("wheat");
        Product sugar = a.product("sugar");
        Product paper = a.product("paper");
        List<Instead> forWheat = s.insteadOf(wheat);
        ok(!forWheat.isEmpty(), "there is something to eat instead of wheat");
        boolean anyFamine = forWheat.stream().anyMatch(Instead::famine);
        ok(anyFamine, "and at least one of them is a famine food: "
                + forWheat.stream().filter(Instead::famine).map(Instead::id).toList());
        ok(!s.insteadOf(sugar).isEmpty(), "sugar has a substitute: "
                + s.insteadOf(sugar).stream().map(Instead::id).toList());
        ok(!s.insteadOf(paper).isEmpty(), "paper has a substitute: "
                + s.insteadOf(paper).stream().map(Instead::id).toList());
        // every id in the table must be a real product, or the answer names nothing
        int bad = 0;
        for (Product p : a.products()) {
            for (Instead in : s.insteadOf(p)) {
                if (a.product(in.id()) == null) {
                    bad++;
                }
            }
        }
        ok(bad == 0, "no substitute names a product that does not exist (" + bad + ")");

        // ------------------------------------------------------------------ the four shocks
        // A quiet place first: nothing happening, so nothing short.
        ProductAtlas.Place quiet = a.place(30.0, 31.0, -2500);
        Shock q = s.shockAt(30.0, 31.0, -2500);
        System.out.println("\nNile -2500 shock: " + q);
        ok(q.field() >= 0 && q.field() <= 1, "a shock is a fraction");
        Supply quietGrain = s.supplyOf(wheat, q);
        ok(!quietGrain.none(), "grain is not wiped out everywhere and always: "
                + quietGrain.sentence(wheat));

        // The Great Famine: 1315 in northern Europe, yield down 60% in the register.
        Shock famine = s.shockAt(51.5, -0.13, 1316);
        System.out.println("London 1316 shock: " + famine);
        ok(famine.field() > 0.05d, "the Great Famine reaches the fields in London in 1316 (field="
                + String.format("%.3f", famine.field()) + ")");
        Supply londonGrain = s.supplyOf(wheat, famine);
        ok(londonGrain.short1(), "so the grain is short: " + londonGrain.sentence(wheat));
        ok(londonGrain.supply() < 1.0d, "and by less than everything: "
                + String.format("%.3f", londonGrain.supply()));

        // A crop takes the field; a smith does not. That is what part D's work is for.
        Product iron = a.product("iron");
        Supply londonIron = s.supplyOf(iron, famine);
        ok(londonIron.supply() > londonGrain.supply(),
                "the same famine hits the grain harder than the iron (grain "
                        + String.format("%.3f", londonGrain.supply()) + " vs iron "
                        + String.format("%.3f", londonIron.supply()) + ")");

        // ------------------------------------------------------------------ labour and roofs
        // A plague kills people and leaves buildings standing: the hands go, the roof does not.
        boolean sawPlague = false;
        for (int year = 1347; year <= 1352; year++) {
            Shock pl = s.shockAt(43.77, 11.26, year);   // Florence
            if (pl.hand() > 0.05d) {
                sawPlague = true;
                System.out.println("Florence " + year + " shock: " + pl);
                ok(pl.hand() > pl.roof(), "the sickness takes the people and leaves the roof (hand="
                        + String.format("%.3f", pl.hand()) + " roof="
                        + String.format("%.3f", pl.roof()) + ")");
                Product pottery = a.product("pottery");
                Supply pots = s.supplyOf(pottery, pl);
                ok(pots.short1(), "so fewer pots get made: " + pots.sentence(pottery));
                break;
            }
        }
        if (!sawPlague) {
            System.out.println("  (no plague reaches Florence in 1347-52 in this register)");
        }

        // ------------------------------------------------------------------ the road
        // The trade shock means a road that ran here has stopped running — not that the place is
        // remote. Samarkand sits on the Silk Road, which is recorded -150 to 1450, so the road is
        // open in 800 and shut by 1600.
        Shock samarkandOpen = s.shockAt(39.65, 66.96, 800);
        Shock samarkandShut = s.shockAt(39.65, 66.96, 1600);
        System.out.println("Samarkand 800 (Silk Road open)  trade=" + samarkandOpen.trade());
        System.out.println("Samarkand 1600 (Silk Road shut) trade=" + samarkandShut.trade()
                + " [" + samarkandShut.why() + "]");
        ok(samarkandOpen.trade() == 0.0d, "the Silk Road is open at Samarkand in 800");
        ok(samarkandShut.trade() > 0.5d, "and shut by 1600, which is a real disruption (trade="
                + samarkandShut.trade() + ")");
        ok(s.routeRecordedNear(39.65, 66.96), "the register does cover Samarkand");

        // The register does not cover everywhere, and where it is thin it must say nothing rather
        // than declare a place cut off. The nearest route town to Hyderabad is 622 km away.
        ok(!s.routeRecordedNear(17.36, 78.47),
                "the register does NOT cover Hyderabad, so it may not claim a shortage there "
                        + "(nearest route town " + String.format("%.0f", s.nearestRouteKm(17.36, 78.47))
                        + " km)");
        ok(s.shockAt(17.36, 78.47, 1700).trade() == 0.0d,
                "so Hyderabad is not reported as cut off in 1700");
        System.out.println("Hyderabad 1700 nearest route town: "
                + String.format("%.0f", s.nearestRouteKm(17.36, 78.47)) + " km, trade shock "
                + s.shockAt(17.36, 78.47, 1700).trade());

        // What arrives from elsewhere lives on the road; what is grown here does not. Pick a
        // product Samarkand makes and one it only receives, and the road must tell them apart.
        ProductAtlas.Place sam = a.place(39.65, 66.96, 1600);
        Product made = null;
        Product brought = null;
        for (Product p : a.products()) {
            if (a.status(p, sam).status() == ProductAtlas.Status.MADE_HERE && made == null) {
                made = p;
            }
            if (a.status(p, sam).status() == ProductAtlas.Status.BROUGHT && brought == null) {
                brought = p;
            }
        }
        if (made != null && brought != null) {
            Supply home = s.supplyOf(made, samarkandShut, sam);
            Supply far = s.supplyOf(brought, samarkandShut, sam);
            System.out.println("  Samarkand 1600, road shut: " + made.id() + " (made here) "
                    + String.format("%.3f", home.supply()) + " vs " + brought.id()
                    + " (brought) " + String.format("%.3f", far.supply()));
            ok(far.supply() < home.supply(),
                    "a closed road hurts what is brought (" + brought.id() + " "
                            + String.format("%.3f", far.supply()) + ") more than what is made here ("
                            + made.id() + " " + String.format("%.3f", home.supply()) + ")");
        }

        // ------------------------------------------------------------------ the answer in words
        System.out.println("\nWhat the mod says, in four places:");
        int[][] pts = {{51, -0, 1316}, {43, 11, 1348}, {30, 31, -2500}, {17, 78, 1700}};
        String[] names = {"London 1316", "Florence 1348", "Nile -2500", "Hyderabad 1700"};
        for (int k = 0; k < pts.length; k++) {
            double lat = pts[k][0], lon = pts[k][1];
            int yr = pts[k][2];
            ProductAtlas.Place pl = a.place(lat, lon, yr);
            Shock sh = s.shockAt(lat, lon, yr);
            System.out.println("  " + names[k] + " (" + pl.area() + ") worst="
                    + String.format("%.3f", sh.worst()) + " " + sh.worstName()
                    + (sh.why().isBlank() ? "" : " [" + sh.why() + "]"));
            for (String id : new String[]{"wheat", "bread", "pottery", "iron"}) {
                Product p = a.product(id);
                if (p == null) {
                    continue;
                }
                Supply sup = s.supplyOf(p, sh);
                System.out.println("     " + id + ": " + s.sentence(p, pl, lat, lon));
            }
        }

        // ------------------------------------------------------------------ how much world this covers
        // A disruption model that only ever fires in Europe is not finished. Sweep nine places
        // across four thousand years and count how often the mod has something to say.
        System.out.println("\nCoverage: does anything ever go wrong outside Europe?");
        double[][] world = {{17.36, 78.47, 1630, 1}, {17.36, 78.47, 1876, 1}, {30.05, 31.25, -2200, 1},
                {34.31, 108.86, 750, 1}, {19.43, -99.13, 1450, 1}, {6.52, 3.38, 1700, 1},
                {-13.16, -72.55, 1400, 1}, {-33.87, 151.21, 1800, 1}, {60.0, 100.0, -2000, 0}};
        String[] worldNames = {"Hyderabad 1630 (Deccan famine)", "Hyderabad 1876", "Memphis -2200",
                "Chang'an 750", "Tenochtitlan 1450", "Lagos 1700", "Cusco 1400",
                "Sydney 1800", "Siberia -2000"};
        int spoke = 0;
        for (int k = 0; k < world.length; k++) {
            double lat = world[k][0], lon = world[k][1];
            int yr = (int) world[k][2];
            Shock sh = s.shockAt(lat, lon, yr);
            if (!sh.quiet()) {
                spoke++;
            }
            System.out.println("  " + String.format("%-30s", worldNames[k])
                    + " worst=" + String.format("%.2f", sh.worst())
                    + " " + String.format("%-24s", sh.worstName())
                    + (sh.why().isBlank() ? "(nothing)" : sh.why()));
        }
        ok(spoke >= 4, "the register has something to say in at least four of nine places ("
                + spoke + ")");

        // ------------------------------------------------------------------ finding a thing by name
        // A player types "wheat", not "wheat_and_barley". The /ee shortage command needs this.
        ok(a.byName("wheat") != null, "byName finds wheat");
        ok(a.byName("Wheat and barley") != null, "byName matches a full name exactly");
        ok(a.byName("porridge") != null, "byName finds porridge and gruel");
        ok(a.byName("flour") != null, "byName finds flour and meal");
        ok(a.byName("nonsense_xyz") == null, "byName returns null for something that is not there");
        ok(a.byName(null) == null, "byName copes with null");
        System.out.println("\nbyName: 'wheat' -> " + a.byName("wheat").id()
                + ", 'flour' -> " + a.byName("flour").id());
        ok(a.loaded(), "the atlas loads: " + a.problem());

        System.out.printf("%nshortage probe: %d checks, %d failed%n", checks, fails);
        if (fails > 0) {
            System.exit(1);
        }
    }
}
