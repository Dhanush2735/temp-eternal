/* Step 46 part 4 (E11): traffic. The register that says how much moves and by which medium.
   The probe asserts the ARITHMETIC against the three documented counts, and the LEASHES against
   known history — because a cost model that does not reproduce a recorded wagon count is a
   decoration, and one that lets grain cross a continent by road is wrong about the ancient world. */
import com.eternalengine.trade.Traffic;

public class Step46TrafficProbe {
    static int checks = 0, failed = 0;

    static void ok(boolean c, String what) {
        checks++;
        if (!c) { failed++; System.out.println("  FAIL " + what); }
    }
    static void near(double a, double b, double tol, String what) {
        checks++;
        if (Math.abs(a - b) > tol) {
            failed++; System.out.println("  FAIL " + what + "  got=" + a + " want=" + b);
        }
    }

    static final Traffic T = Traffic.get();

    static final double[] PARIS = {48.8566, 2.3522};
    static final double[] OSTIA = {41.7500, 12.2800};
    static final double[] ALEXANDRIA = {31.2001, 29.9187};
    static final double[] AGRA = {27.1750, 78.0422};
    static final double[] CUSCO = {-13.5320, -71.9675};

    public static void main(String[] args) {
        System.out.println("== " + T + " ==");
        ok(T.hasData(), "the register has data");
        ok(T.problem() == null, "no problem reported");

        // ---------------------------------------------------------------- 1. THE EDICT'S RATIOS
        // The mod quotes 1:5:10:52. It must COMPUTE them, not merely say them.
        near(T.ratio("downriver"), 5.0, 0.5, "downriver is 5 times sea");
        near(T.ratio("upriver"), 10.0, 0.5, "upriver is 10 times sea");
        near(T.ratio("road"), 52.0, 0.5, "road is 52 times sea");
        ok(T.ratio("road") > T.ratio("upriver"), "road is dearer than upriver");
        ok(T.ratio("upriver") > T.ratio("downriver"), "upriver is dearer than downriver");
        ok(T.ratio("downriver") > 1.0, "and river is dearer than sea");
        System.out.println("  road costs " + Math.round(T.ratio("road")) + " x sea per kg-km");

        // ---------------------------------------------------------------- 2. THE LEASHES
        // THE WHOLE POINT. Heavy cheap goods have a short leash; light dear ones have none.
        int wheatRoad = T.howFar("wheat", "road");
        int wheatSea = T.howFar("wheat", "sea");
        ok(wheatRoad > 200 && wheatRoad < 400,
                "wheat reaches 200-400 km inland by road before freight doubles it ("
                        + wheatRoad + ")");
        ok(wheatSea > 10000, "and over 10,000 km by sea (" + wheatSea + ")");
        ok(wheatSea / Math.max(1, wheatRoad) > 40, "a sea kilometre buys 40+ road kilometres");
        System.out.println("  wheat: " + wheatRoad + " km by road, " + wheatSea + " by sea");

        ok(T.howFar("timber", "road") < wheatRoad, "timber is cheaper and leashed shorter");
        ok(T.howFar("stone", "road") < T.howFar("timber", "road"), "stone shorter still");
        ok(T.howFar("pepper", "road") > 50000, "pepper goes anywhere by road");
        ok(T.howFar("silk", "road") > 500000, "silk has effectively no leash at all");

        // Every good must be able to move somehow, and further by sea than by road.
        for (Traffic.Good g : T.goods()) {
            ok(g.reachBy("road") > 0, g.id() + " can move by road at all");
            ok(g.reachBy("sea") > g.reachBy("road"),
                    g.id() + " goes further by sea than by road");
            ok(g.perKg() > 0, g.id() + " is worth something");
        }

        // ---------------------------------------------------------------- 3. THE DOCUMENTED COUNTS
        // Forty loaded wagons a day carried 14,000 tons a year through Bolton, Massachusetts.
        // The model must produce that number, not merely cite it.
        double boltonTonnesPerDay = 14000.0 / 365.0;
        Traffic.Street bolton = T.trafficOn("road", boltonTonnesPerDay, "wagon");
        ok(bolton.vehiclesPerDay() >= 38 && bolton.vehiclesPerDay() <= 42,
                "Bolton's 14,000 t a year is " + bolton.vehiclesPerDay()
                        + " wagons a day against 40 counted, at a " + T.loadFactor()
                        + " load factor");
        // The load factor is the measured result, so assert what it is.
        ok(T.loadFactor() > 0.7 && T.loadFactor() < 0.9,
                "wagons run about five-sixths full (" + T.loadFactor() + ")");
        System.out.println("  " + bolton.line());

        // The 1333 Westminster-York carriage: 330 km in nine days with thirty-two carters.
        double days = T.days(330, "carrier");
        near(days, 8.9, 1.0, "Westminster to York is about nine days at a carrier's pace");
        ok(T.kmPerDay("carrier") >= 30 && T.kmPerDay("carrier") <= 45,
                "and a carrier does 30-45 km a day, as Spufford records");

        // ---------------------------------------------------------------- 4. THE ROUTE CHOICE
        // Grain to Rome: 2,000 km from Alexandria, and it must go by SEA or not at all.
        var romeGrain = T.routesFor("wheat", 2000, OSTIA[0], OSTIA[1], 300);
        boolean seaOk = false, roadRefused = false;
        for (Traffic.Choice c : romeGrain) {
            if (c.route().equals("sea") && c.possible()) seaOk = true;
            if (c.route().equals("road") && !c.possible()) roadRefused = true;
        }
        ok(seaOk, "grain CAN reach Rome from Alexandria by sea");
        ok(roadRefused, "and CANNOT by road over the same 2,000 km");
        System.out.println("  Alexandria to Rome, 2,000 km of wheat:");
        for (Traffic.Choice c : romeGrain) System.out.println("    " + c.line());

        // A short haul is within the leash — the pure cost question, no map needed.
        ok(T.howFar("wheat", "road") >= 100, "100 km of wheat is inside its road leash");
        // Silk crosses a continent by road where wheat cannot.
        ok(T.howFar("silk", "road") >= 2000, "2,000 km of silk is inside its road leash");
        ok(T.howFar("wheat", "road") < 2000, "and 2,000 km of wheat is not");
        // Whether a road EXISTS at a place is WaysGrid's question, not this register's, and the
        // grid is honest about where it has no record: a missing year is absence, not permission.
        boolean gridLoaded = com.eternalengine.civilization.WaysGrid.get().loaded();
        System.out.println("  ways grid loaded: " + gridLoaded + " ("
                + com.eternalengine.civilization.WaysGrid.get().cellsWithSomething()
                + " squares with a dated way)");
        var agraRoad = T.routesFor("wheat", 100, AGRA[0], AGRA[1], 1600);
        for (Traffic.Choice c : agraRoad) {
            if (c.route().equals("road")) {
                // Either it is possible (the grid knows a road at Agra) or it is refused for a
                // reason that is about the grid, never about the cost.
                ok(c.possible() || c.why().equals("it does not reach here"),
                        "Agra road: refused only because no road is recorded there, not on cost");
                System.out.println("    Agra 1600, 100 km of wheat by road: " + c.line());
            }
        }

        // ---------------------------------------------------------------- 5. CONGESTION
        // A turnpike is a ceiling, not a pipe. The Bath trust's 2,500 waggons in a week is
        // comfortably under it; a modern city's goods traffic is not.
        Traffic.Street quiet = T.trafficOn("road", 10, "cart");
        ok(!quiet.congested(), "10 tonnes a day by cart is a quiet road");
        Traffic.Street busy = T.trafficOn("road", 20000, "cart");
        ok(busy.congested(), "20,000 tonnes a day by cart is not");
        System.out.println("  " + busy.line());
        // A single track at one train every five minutes is 288 trains a day; at 500 t a train
        // that is about 144,000 tonnes. So 100,000 fits and 300,000 does not — and the register
        // says so rather than treating rail as unlimited, which is the usual modelling mistake.
        Traffic.Street railFits = T.trafficOn("rail", 100000, "train");
        ok(!railFits.congested(), "a single track takes 100,000 t a day by train");
        Traffic.Street railOver = T.trafficOn("rail", 300000, "train");
        ok(railOver.congested(), "but not 300,000");
        System.out.println("  " + railOver.line());

        // ---------------------------------------------------------------- 6. NOTHING BEFORE ITS TIME
        // No traffic on a road that has not been built. The ways grid is the gate.
        var paris = T.routesFor("wheat", 50, PARIS[0], PARIS[1], -3000);
        for (Traffic.Choice c : paris) {
            if (c.route().equals("rail")) {
                ok(!c.possible(), "no railway traffic at Paris in 3000 BC");
            }
        }
        if (gridLoaded) {
            var paris1900 = T.routesFor("wheat", 50, PARIS[0], PARIS[1], 1900);
            boolean rail1900 = false;
            for (Traffic.Choice c : paris1900) {
                if (c.route().equals("rail") && c.possible()) rail1900 = true;
            }
            ok(rail1900, "and there is by 1900");
            // And the reason rail could not carry anything until this part added a rate: a
            // railway with no freight cost has a leash of zero and carries nothing at all.
            ok(T.freight("rail") > 0, "rail has a freight rate (" + T.freight("rail") + ")");
            ok(T.freight("rail") < T.freight("road"), "and it undercuts the road");
            ok(T.howFar("wheat", "rail") > T.howFar("wheat", "road"),
                    "so wheat travels further by rail than by road");
            boolean wheatRail = false;
            for (Traffic.Choice c : T.routesFor("wheat", 500, PARIS[0], PARIS[1], 1900)) {
                if (c.route().equals("rail") && c.possible()) wheatRail = true;
            }
            ok(wheatRail, "500 km of wheat CAN go by rail from Paris in 1900");
            System.out.println("  wheat by rail: " + T.howFar("wheat", "rail")
                    + " km leash, against " + T.howFar("wheat", "road") + " by road");
        } else {
            ok(true, "rail presence not asserted: the ways grid is not on this probe's path");
        }

        // ---------------------------------------------------------------- 7. THE SPAN AND THE FINDING
        ok(T.finding() != null && T.finding().contains("286"),
                "the finding quotes the wheat leash the register computes");
        ok(com.eternalengine.clock.Timeline.projected(3000), "the frame marks AD 3000 projected");
        // The register still answers at the far end of the timeline.
        ok(T.howFar("wheat", "road") > 0, "and it still answers in AD 3000");

        // ---------------------------------------------------------------- 8. EVERY ROUTE HAS A SPEED
        for (String r : new String[]{"road", "rail", "river", "canal", "sea"}) {
            ok(T.kmPerDay(r) > 0, "the " + r + " has a working speed");
        }
        ok(T.kmPerDay("rail") > T.kmPerDay("road"), "rail is faster than road");
        ok(T.kmPerDay("sea") > T.kmPerDay("road"), "and sea is faster than road");

        System.out.println("== step 46 traffic: " + checks + " checks, " + failed + " failed ==");
        System.out.println("  " + T.summary());
        if (failed > 0) System.exit(1);
    }
}
