/* Step 46 part 3 (E10 A): the vehicle register.
   Steps 44, 45 and 46 part 2 all caught invented area codes and places that read right by id but
   wrong where they stood. So this probe asserts at real PLACES, and it asserts the NEEDS join,
   which is the only thing this register adds over the three that already existed. */
import com.eternalengine.vehicle.Vehicles;
import com.eternalengine.vehicle.WorkingAnimals;

public class Step46VehiclesProbe {
    static int checks = 0, failed = 0;

    static void ok(boolean c, String what) {
        checks++;
        if (!c) { failed++; System.out.println("  FAIL " + what); }
    }
    static void eq(Object a, Object b, String what) {
        checks++;
        if (a == null ? b != null : !a.equals(b)) {
            failed++; System.out.println("  FAIL " + what + "  expected=" + b + " actual=" + a);
        }
    }

    static final Vehicles V = Vehicles.get();

    static String area(double lat, double lon, int year) {
        return com.eternalengine.money.ProductAtlas.get().place(lat, lon, year).area();
    }
    static Vehicles.Verdict at(String id, double lat, double lon, int year) {
        return V.availableAt(V.byId(id), area(lat, lon, year), year, lat, lon);
    }

    /** The atlas's own 17 areas. */
    static final String[] AREAS = {"EUR", "EEU", "WAS", "NAF", "CAS", "SAS", "EAS", "SEA", "WAF",
            "MSA", "EAF", "NNA", "MNA", "CAC", "SAM", "PAC", "AUS"};

    static final double[] PARIS = {48.8566, 2.3522};
    static final double[] AGRA = {27.1750, 78.0422};
    static final double[] CHANGAN = {34.2667, 108.9000};
    static final double[] CUSCO = {-13.5320, -71.9675};
    static final double[] SYDNEY = {-33.8688, 151.2093};
    static final double[] TIMBUKTU = {16.7666, -3.0026};
    static final double[] TENOCH = {19.4326, -99.1332};
    static final double[] LONDON = {51.5074, -0.1278};

    public static void main(String[] args) {
        System.out.println("== " + V + " ==");
        ok(V.hasData(), "the register has data");
        eq(V.problem(), null, "no problem reported");
        ok(V.vehicles().size() >= 25, "at least 25 vehicles (" + V.vehicles().size() + ")");

        // ---------------------------------------------------------------- 1. THE PLAN'S LIST
        String[] want = {"porter", "litter", "cart", "chariot", "riding_horse", "riding_camel",
                "elephant_howdah", "bicycle", "rickshaw", "tram", "bus", "car", "lorry", "raft",
                "dhow", "galley", "junk", "sailing_ship", "steamship", "train", "balloon",
                "aeroplane"};
        for (String id : want) {
            ok(V.byId(id) != null, "the register carries " + id);
        }
        // "palanquin" is the litter; "airship" is the balloon row; "plane" is the aeroplane.
        ok(V.byId("litter").name().contains("palanquin"), "the palanquin is the litter row");
        ok(V.byId("balloon").name().contains("airship"), "the airship is the balloon row");
        ok(V.byId("aeroplane").name().contains("aeroplane"), "the plane is the aeroplane row");

        // ---------------------------------------------------------------- 2. EVERY VEHICLE IS WHOLE
        for (Vehicles.Vehicle v : V.vehicles()) {
            ok(v.kmPerDay() > 0, v.id() + " goes somewhere");
            ok(!v.needs().isEmpty(), v.id() + " needs something");
            ok(Vehicles.MEDIUMS.contains(v.medium()), v.id() + " moves on a known medium");
            for (String n : v.needs()) {
                ok(Vehicles.NEEDS.contains(n), v.id() + " needs a known thing (" + n + ")");
            }
            ok(v.note() != null && !v.note().isBlank(), v.id() + " says what it is");
            ok(v.yearSource() != null && !v.yearSource().isBlank(), v.id() + " names its source");
            ok(v.mark().equals("recorded") || v.mark().equals("estimated"), v.id() + " is marked");
        }

        // ---------------------------------------------------------------- 3. THE NEEDS JOIN (THE NEW PART)
        // A train that has arrived is not a train on a railway. This is the question no other
        // register in the mod answers, and it is what E11 is built on.
        Vehicles.Vehicle train = V.byId("train");
        ok(train.needs("rail"), "the train needs a railway");
        ok(V.byId("lorry").needs("road"), "the lorry needs a road");
        ok(V.byId("cart").needs("beast"), "the cart needs a beast");
        ok(V.byId("tram").needs("tramline"), "the tram needs a tram line");
        ok(V.byId("porter").needs("none"), "the porter needs nothing at all");
        ok(V.byId("litter").needs("none"), "and neither does the litter");
        ok(V.byId("wheelbarrow").needs("none"), "nor the wheelbarrow - one wheel, one person");

        // A beast-drawn vehicle must be refused where its beast has not arrived. Cusco is the
        // sharpest case: the cart reaches South America in 1540 with the Spanish, and there was
        // nothing to hitch to one before that.
        Vehicles.Verdict cartAtCusco = at("cart", CUSCO[0], CUSCO[1], 1400);
        ok(!cartAtCusco.here(), "a CART is not available at Cusco in 1400");
        System.out.println("  e.g. a cart at Cusco in 1400 -> " + cartAtCusco.line());
        ok(at("cart", CUSCO[0], CUSCO[1], 1700).here(), "but it is by 1700");
        // And the beast check must actually BITE somewhere - that is, there must be a place and a
        // year where the vehicle's own date has passed and the beast has not arrived. If this
        // never happens, the join is decorative.
        int bitten = 0;
        String example = null;
        for (Vehicles.Vehicle v : V.vehicles()) {
            if (!v.needs("beast")) continue;
            for (String a : AREAS) {
                Integer arrived = v.yearIn(a);
                if (arrived == null) continue;
                for (int year = arrived; year <= arrived + 400 && year <= 3000; year += 7) {
                    if (!V.arrivedBy(v, a, year)) continue;
                    Vehicles.Verdict d = V.availableAt(v, a, year, 0, 0);
                    if (d != null && !d.here() && d.why() != null && d.why().startsWith("it needs ")) {
                        bitten++;
                        if (example == null) example = v.id() + " in " + a + " in " + year + ": "
                                + d.why();
                    }
                }
            }
        }
        ok(bitten > 0, "the beast check actually refuses a vehicle somewhere (" + bitten
                + " cases)");
        if (example != null) System.out.println("  e.g. " + example);
        // And the sharpest case, asserted directly rather than found by scanning: the armoury
        // dates war elephants in Europe from -280 (Pyrrhus crossed into Italy with twenty), but
        // there has never been a working elephant population in Europe, so a howdah is not a way
        // of getting about in Gaul. Arrival and beast are two questions and only this register
        // asks the second one.
        Vehicles.Verdict howdah = at("elephant_howdah", PARIS[0], PARIS[1], -200);
        ok(!howdah.here(), "no elephant howdah at Paris in 200 BC, whatever the armoury's date");
        System.out.println("  e.g. an elephant howdah at Paris in 200 BC -> " + howdah.line());

        // A chariot needs a horse, and there were none in the Americas.
        Vehicles.Verdict chariotAtTenoch = at("chariot", TENOCH[0], TENOCH[1], 1400);
        ok(!chariotAtTenoch.here(), "no chariot at Tenochtitlan in 1400");

        // ---------------------------------------------------------------- 4. NOTHING BEFORE ITS TIME
        for (double[] p : new double[][]{PARIS, AGRA, CHANGAN, CUSCO, SYDNEY, TIMBUKTU}) {
            for (int year : new int[]{-3000, -1000, 0, 1000, 1500, 1800, 1900, 2000, 3000}) {
                String a = area(p[0], p[1], year);
                if (a == null) continue;
                for (Vehicles.Vehicle v : V.usableAt(a, year, p[0], p[1])) {
                    Integer arrived = v.yearIn(a);
                    ok(arrived == null || arrived <= year,
                            "the " + v.id() + " had reached " + a + " by " + year);
                    Integer gone = v.endIn(a);
                    ok(gone == null || year <= gone,
                            "the " + v.id() + " had not left " + a + " by " + year);
                }
            }
        }
        // Specifically: no train in Paris in 1700, no car anywhere in 1800.
        ok(!at("train", PARIS[0], PARIS[1], 1700).here(), "no train in Paris in 1700");
        ok(!at("car", PARIS[0], PARIS[1], 1800).here(), "no car in Paris in 1800");
        ok(!at("aeroplane", PARIS[0], PARIS[1], 1900).here(), "no aeroplane in Paris in 1900");
        ok(at("porter", PARIS[0], PARIS[1], -3000).here(), "but a porter in Paris in 3000 BC");
        ok(at("litter", CHANGAN[0], CHANGAN[1], -3000).here(), "and a litter in Chang'an");

        // A ship is not a vehicle for Paris. This is what stops E11 routing a caravan onto one.
        ok(!at("sailing_ship", PARIS[0], PARIS[1], 1500).here(),
                "no sailing ship in Paris in 1500 - it is 150 km from the sea");
        ok(at("sailing_ship", 43.2965, 5.3698, 1500).here(),
                "but there is one at Marseille, which is a port");
        // And no ship before the sail, which is what the products atlas claimed (boats, -10000).
        ok(!at("sailing_ship", 43.2965, 5.3698, -3000).here(),
                "no 200-tonne sailing ship at Marseille in 3000 BC");
        ok(at("canoe", 43.2965, 5.3698, -3000).here(), "but there is a canoe");
        System.out.println("  e.g. a sailing ship at Paris in 1500 -> "
                + at("sailing_ship", PARIS[0], PARIS[1], 1500).line());

        // ---------------------------------------------------------------- 5. THE FASTEST, AT PLACES
        for (double[] p : new double[][]{PARIS, AGRA, CHANGAN, CUSCO, SYDNEY, TIMBUKTU, LONDON}) {
            for (int year : new int[]{-3000, 0, 1000, 1500, 1800, 1900, 2000, 3000}) {
                ok(V.fastestAt(area(p[0], p[1], year), year, p[0], p[1], true) != null,
                        "somebody can travel at " + p[0] + "," + p[1] + " in " + year);
            }
        }
        Vehicles.Vehicle fast1900 = V.fastestAt("EUR", 1900, PARIS[0], PARIS[1], true);
        Vehicles.Vehicle fast1500 = V.fastestAt("EUR", 1500, PARIS[0], PARIS[1], true);
        ok(fast1900 != null && fast1500 != null, "both answer");
        if (fast1900 != null && fast1500 != null) {
            ok(fast1900.kmPerDay() > fast1500.kmPerDay(),
                    "travel got faster: " + fast1500.name() + " in 1500 -> " + fast1900.name()
                            + " in 1900");
        }
        System.out.println("  e.g. fastest for people, Paris 1500: "
                + (fast1500 == null ? "none" : fast1500.describe()));
        System.out.println("  e.g. fastest for people, Paris 1900: "
                + (fast1900 == null ? "none" : fast1900.describe()));

        // ---------------------------------------------------------------- 6. THE CORRECTIONS ARE HONEST
        ok(V.corrections().size() >= 6, "%d corrected dates are shipped".formatted(
                V.corrections().size()));
        ok(V.finding() != null && V.finding().toLowerCase().contains("template"),
                "the systematic finding is stated, not patched around");
        // A rickshaw must NOT be dated -3000, which is what the products atlas said.
        Vehicles.Vehicle rickshaw = V.byId("rickshaw");
        ok(rickshaw.corrected() != null, "the rickshaw row says its date was corrected");
        Integer rickEur = rickshaw.yearIn("EUR");
        ok(rickEur != null && rickEur > 1800,
                "the rickshaw reaches Europe after 1800, not in 3000 BC (" + rickEur + ")");
        Vehicles.Vehicle barrow = V.byId("wheelbarrow");
        Integer barrowEur = barrow.yearIn("EUR");
        ok(barrowEur != null && barrowEur > 1000,
                "the wheelbarrow reaches Europe after 1000, not in 3000 BC (" + barrowEur + ")");
        Integer barrowEas = barrow.yearIn("EAS");
        ok(barrowEas != null && barrowEas < barrowEur,
                "and it reaches East Asia first, where it was invented (" + barrowEas + ")");
        // A dhow must not be in the Americas.
        eq(V.byId("dhow").yearIn("NNA"), null, "no dhow in North America");
        eq(V.byId("dhow").yearIn("SAM"), null, "nor in South America");
        eq(V.byId("junk").yearIn("EUR"), null, "no junk in Europe");
        ok(V.byId("junk").yearIn("EAS") != null, "but there is one in East Asia");

        // ---------------------------------------------------------------- 7. THE CHARIOT, FROM TWO REGISTERS
        Vehicles.Vehicle chariot = V.byId("chariot");
        eq(chariot.atlasId(), "chariot", "the chariot is dated by the technology atlas's own tech");
        ok(chariot.neverIn("NNA") != null, "and the armoury says why not in North America");
        ok(chariot.neverIn("WAF") != null, "and why not in West Africa");
        ok(chariot.neverIn("WAF").toLowerCase().contains("tsetse"),
                "the reason names the tsetse belt: " + chariot.neverIn("WAF"));

        // ---------------------------------------------------------------- 8. ORDERING, AND THE SPAN
        for (double[] p : new double[][]{PARIS, AGRA, CUSCO, SYDNEY}) {
            var list = V.usableAt(area(p[0], p[1], 1900), 1900, p[0], p[1]);
            for (int i = 1; i < list.size(); i++) {
                ok(list.get(i - 1).kmPerDay() >= list.get(i).kmPerDay(),
                        "the usable vehicles are fastest-first at " + p[0] + "," + p[1]);
            }
        }
        // The far end of the timeline still answers.
        ok(V.fastestAt("EUR", 3000, PARIS[0], PARIS[1], true) != null,
                "the register still answers in AD 3000");
        ok(com.eternalengine.clock.Timeline.projected(3000), "and the frame marks it projected");

        System.out.println("== step 46 vehicles: " + checks + " checks, " + failed + " failed ==");
        System.out.println("  " + V.summary());
        if (failed > 0) System.exit(1);
    }
}
