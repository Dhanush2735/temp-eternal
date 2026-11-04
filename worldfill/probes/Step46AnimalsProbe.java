/* Step 46 part 2 (D14): the working animals.
   Steps 44 and 45 both caught invented area codes and places that read right by id but wrong
   where they stood. So this probe asserts at real PLACES with real coordinates, throughout. */
import com.eternalengine.vehicle.WorkingAnimals;

public class Step46AnimalsProbe {
    static int checks = 0, failed = 0;

    static void ok(boolean c, String what) {
        checks++;
        if (!c) { failed++; System.out.println("  FAIL " + what); }
    }
    static void eq(Object a, Object b, String what) {
        checks++;
        if (a == null ? b != null : !a.equals(b)) {
            failed++;
            System.out.println("  FAIL " + what + "  expected=" + b + " actual=" + a);
        }
    }

    static final WorkingAnimals W = WorkingAnimals.get();

    static String area(double lat, double lon, int year) {
        return com.eternalengine.money.ProductAtlas.get().place(lat, lon, year).area();
    }
    static WorkingAnimals.Choice pack(double lat, double lon, int year) {
        return W.packAnimalFor(area(lat, lon, year), year);
    }

    // Real places. Cusco is -13.53/-71.97; Timbuktu 16.77/-3.00; Sydney -33.87/151.21.
    static final double[] CUSCO = {-13.5320, -71.9675};
    static final double[] TIMBUKTU = {16.7666, -3.0026};
    static final double[] SYDNEY = {-33.8688, 151.2093};
    static final double[] PARIS = {48.8566, 2.3522};
    static final double[] AGRA = {27.1750, 78.0422};
    static final double[] CHANGAN = {34.2667, 108.9000};
    static final double[] TENOCHTITLAN = {19.4326, -99.1332};
    static final double[] CAHOKIA = {38.6550, -90.0620};

    public static void main(String[] args) {
        System.out.println("== " + W + " ==");
        ok(W.hasData(), "the register has data");
        eq(W.problem(), null, "the register reports no problem");
        ok(W.animals().size() >= 8, "at least eight animals (" + W.animals().size() + ")");

        // ---------------------------------------------------------------- 1. THE BUG, AT THE PLACES
        // LogisticsManager spawned three donkeys everywhere. These are the places that proves wrong.
        eq(pack(CUSCO[0], CUSCO[1], 1500).animal().id(), "llama",
                "a caravan at CUSCO in 1500 gets LLAMAS, not donkeys");
        eq(pack(TIMBUKTU[0], TIMBUKTU[1], 1300).animal().id(), "camel",
                "a caravan at TIMBUKTU in 1300 gets CAMELS, not donkeys");
        eq(pack(SYDNEY[0], SYDNEY[1], 1700).animal().id(), "porter",
                "a caravan at SYDNEY in 1700 gets PORTERS - there were no beasts at all");
        ok(!pack(TENOCHTITLAN[0], TENOCHTITLAN[1], 1500).animal().id().equals("donkey")
                || area(TENOCHTITLAN[0], TENOCHTITLAN[1], 1500) == null,
                "a caravan at TENOCHTITLAN in 1500 does not get donkeys by reflex");

        // The donkey only becomes right once it has actually arrived.
        ok(W.byId("donkey") != null, "there is a donkey");
        eq(W.byId("donkey").hereBy("SAM", 1500), false, "donkeys have NOT reached South America by 1500");
        eq(W.byId("donkey").hereBy("SAM", 1600), true, "they have by 1600");
        eq(W.byId("donkey").hereBy("AUS", 1700), false, "nor Australia by 1700");
        eq(W.byId("donkey").hereBy("AUS", 1800), true, "they have by 1800");

        // ---------------------------------------------------------------- 2. THE PORTER IS THE DEFAULT
        // Below the tsetse belt nothing with four legs survives, so a person carries it.
        WorkingAnimals.Animal porter = W.byId("porter");
        ok(porter != null, "there is a porter");
        eq(porter.years().size(), 17, "the porter reaches all 17 areas, so nowhere is ever empty");
        for (double[] p : new double[][]{CUSCO, TIMBUKTU, SYDNEY, PARIS, AGRA, CHANGAN,
                TENOCHTITLAN, CAHOKIA}) {
            for (int year : new int[]{-3000, -1000, 0, 1000, 1500, 1800, 2000, 2500, 3000}) {
                WorkingAnimals.Choice c = pack(p[0], p[1], year);
                ok(c != null, "somebody carries something at " + p[0] + "," + p[1] + " in " + year);
            }
        }

        // ---------------------------------------------------------------- 3. THE CORRECTIONS
        WorkingAnimals.Animal reindeer = W.byId("reindeer");
        ok(reindeer != null, "there are reindeer");
        eq(reindeer.yearIn("WAF"), null, "reindeer are GONE from West Africa - the products atlas "
                + "wrongly dated them -2000 there");
        eq(reindeer.neverIn("WAF") == null, false, "and the reason is recorded");
        ok(reindeer.neverIn("WAF").contains("artefact"), "the reason names the artefact");
        eq(reindeer.yearIn("MSA"), null, "gone from Middle Africa too");
        eq(reindeer.yearIn("AUS"), null, "and from Australia");
        ok(reindeer.hereBy("EUR", -5000), "but still present in Europe in 5000 BC");

        // The donkey is African and predates the horse there; the horse is a steppe animal.
        WorkingAnimals.Animal donkey = W.byId("donkey");
        WorkingAnimals.Animal horse = W.byId("horse");
        ok(donkey != null && horse != null, "both are in the register");
        if (donkey != null && horse != null) {
            ok(donkey.yearIn("WAF") < horse.yearIn("WAF"),
                    "in West Africa the DONKEY predates the horse (" + donkey.yearIn("WAF")
                    + " vs " + horse.yearIn("WAF") + ")");
            ok(donkey.yearIn("NAF") < horse.yearIn("NAF"), "and in North Africa");
        }

        // ---------------------------------------------------------------- 4. THE TSETSE BELT
        ok(W.tsetse() != null && W.tsetse().contains("23"),
                "the measured tsetse effect is carried: it names the 23-point fall");
        ok(W.mixed().containsKey("WAF"), "West Africa is marked as two worlds at once");
        ok(W.mixed().get("WAF").contains("Sahel"), "and says which two: the Sahel and the forest");
        ok(W.mixed().containsKey("MSA"), "so is Middle Africa");
        eq(W.mixed().size(), 3, "three areas are marked mixed, and no more");
        // A mixed area must SAY it is mixed in the answer, not quietly pick one.
        WorkingAnimals.Choice waf = W.packAnimalFor("WAF", 1300);
        ok(waf.mixed(), "an answer for West Africa says it is mixed");
        ok(waf.mixedNote() != null && waf.mixedNote().contains("tsetse"),
                "and names the tsetse fly");

        // ---------------------------------------------------------------- 5. LOAD AND DISTANCE
        for (WorkingAnimals.Animal a : W.animals()) {
            ok(a.loadKg() > 0, a.id() + " carries something");
            ok(a.kmPerDay() > 0, a.id() + " goes somewhere");
            ok(!a.roles().isEmpty(), a.id() + " does something");
            ok(a.note() != null && !a.note().isBlank(), a.id() + " says what it is");
            ok(a.source() != null && !a.source().isBlank(), a.id() + " is sourced");
            ok(a.mark().equals("recorded") || a.mark().equals("estimated"),
                    a.id() + " is marked");
        }
        ok(W.byId("camel").loadKg() > W.byId("llama").loadKg(),
                "a camel carries more than a llama");
        ok(W.byId("llama").loadKg() > W.byId("porter").loadKg(),
                "a llama carries more than a person");
        // The Kano ratio the register records: over ten men to carry one camel's load.
        ok(W.byId("camel").loadKg() / W.byId("porter").loadKg() > 5,
                "it takes more than five people to carry one camel's load");
        System.out.println("  e.g. a camel carries " + W.byId("camel").loadKg()
                + " kg, a porter " + W.byId("porter").loadKg() + " kg");

        // ---------------------------------------------------------------- 6. THE PLOUGH
        for (double[] p : new double[][]{PARIS, AGRA, CHANGAN}) {
            WorkingAnimals.Choice plough = W.ploughFor(area(p[0], p[1], 1200), 1200);
            ok(plough != null, "something draws a plough at " + p[0] + "," + p[1] + " in 1200");
        }
        ok(W.ploughFor("SAM", 1200) == null,
                "NOTHING draws a plough in the Andes in 1200 - the Americas had no plough animal");
        ok(W.ploughFor("AUS", 1700) == null, "nor in Australia in 1700");

        // ---------------------------------------------------------------- 7. NO BEAST BEFORE ITS TIME
        for (double[] p : new double[][]{CUSCO, SYDNEY, TENOCHTITLAN, CAHOKIA}) {
            for (int year : new int[]{-3000, -1000, 0, 800, 1200, 1490}) {
                String a = area(p[0], p[1], year);
                if (a == null) continue;
                WorkingAnimals.Choice c = W.packAnimalFor(a, year);
                if (c == null) continue;
                Integer arrived = c.animal().yearIn(a);
                ok(arrived != null && arrived <= year, "the " + c.animal().id() + " had reached "
                        + a + " by " + year + " (it arrived " + arrived + ")");
            }
        }

        // ---------------------------------------------------------------- 8. THE TRAIN, AND THE SPAN
        // Three hardcoded donkeys carry 150 kg. What should a caravan actually be?
        System.out.println("  e.g. Cusco 1500: " + W.trainFor(area(CUSCO[0], CUSCO[1], 1500),
                1500, 500));
        System.out.println("  e.g. Timbuktu 1300: " + W.trainFor(area(TIMBUKTU[0],
                TIMBUKTU[1], 1300), 1300, 500));
        ok(W.trainFor(area(CUSCO[0], CUSCO[1], 1500), 1500, 500).contains("llama"),
                "a 500 kg caravan at Cusco is a llama train, not three donkeys");
        // And the far end of the timeline still answers.
        WorkingAnimals.Choice far = W.packAnimalFor("EUR", 3000);
        ok(far != null, "the register still answers in AD 3000");
        ok(com.eternalengine.clock.Timeline.projected(3000), "and the frame marks it projected");

        System.out.println("== step 46 animals: " + checks + " checks, " + failed + " failed ==");
        System.out.println("  " + W.summary());
        if (failed > 0) System.exit(1);
    }
}
