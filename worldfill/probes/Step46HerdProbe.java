/* Step 46 part 7 (D14, the second half): the herds, and the roads they made.
   The claim under test is the one that reorders the subject: **a road you can eat is a different
   object from a road you can drive on**, so the widest route in the world is a sheep corridor. */
import com.eternalengine.vehicle.Herds;
import com.eternalengine.vehicle.VehicleMods;

import java.util.List;
import java.util.Set;

public class Step46HerdProbe {
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

    static final Herds H = Herds.get();

    public static void main(String[] args) {
        System.out.println("== " + H + " ==");
        ok(H.hasData(), "the herd register has data");
        eq(H.problem(), null, "no problem reported");
        ok(H.finding() != null && H.finding().contains("eat"),
                "the finding is the one-line version: a road you can eat");

        // -------------------------------------------------------------- 1. THE FINDING, IN NUMBERS
        // A vehicle road is 4 to 6 m. A cañada is 75 m. That is not a detail, it is the thesis.
        Herds.Drove canada = H.drove("canada_real");
        ok(canada != null, "the cañada real is in the register");
        eq(canada.widthM(), 75.0, "and it is 75 m wide");
        ok(canada.roadWidths() > 10, "which is " + String.format("%.1f", canada.roadWidths())
                + " vehicle roads side by side");
        ok(H.isDroveWidth(canada.widthM()), "so by its own test it is a drove and not a road");
        ok(!H.isDroveWidth(6.0), "a 6 m Roman road is not");
        System.out.println("  " + H.widestLine());

        // And the narrowest drove shows the rule is about GRAZING, not about herds being big:
        // a bullock track is a vehicle road with a herd's habits.
        ok(H.narrowestDroveM() <= 10, "the narrowest drove is "
                + (int) H.narrowestDroveM() + " m, because it is a CART road");
        ok(!H.isDroveWidth(H.drove("bullock_track_india").widthM()),
                "and the Indian bullock track fails the drove test, correctly: it was worn by carts");

        // -------------------------------------------------------------- 2. THE MESTA, BOTH HALVES
        Herds.Herd mesta = H.herd("sheep_castile");
        ok(mesta != null, "Castile has a herd row");
        eq(mesta.year(), 1273, "from the Mesta's charter in 1273");
        ok(mesta.note().contains("fewer than 100"),
                "and the row itself refuses the giant-flock myth");
        ok(mesta.sizeHigh() <= 1000, "its own upper band is " + mesta.sizeHigh() + " head");
        eq(canada.end(), 1836, "the cañadas end with the Mesta in 1836");

        // -------------------------------------------------------------- 3. THE HERD BEFORE WOOL
        Herds.Herd sheep = H.herd("sheep_near_east");
        ok(sheep.yields().contains("milk"), "the first herd gave milk");
        ok(sheep.note().contains("hair sheep"), "and was a hair sheep, so no fleece");
        ok(sheep.note().contains("4000 BC"), "wool arrives about 4000 BC, six thousand years later");

        // -------------------------------------------------------------- 4. THE CHICKEN'S NEW DATE
        Herds.Herd chicken = H.herd("chicken_thailand");
        eq(chicken.year(), -1650, "the chicken is dated 1650 BC at the earliest");
        ok(chicken.source().contains("PNAS"), "on a PNAS 2022 reanalysis, not a textbook");
        ok(H.herdOf("chicken", "SEA", -3000) == null, "so there is no chicken in Thailand in 3000 BC");
        ok(H.herdOf("chicken", "SEA", -1000) != null, "and there is in 1000 BC");
        ok(H.herdOf("chicken", "EUR", -1000) == null, "and none in Europe in 1000 BC");
        ok(H.herdOf("chicken", "EUR", -900) == null, "and none in Europe in 900 BC either");
        eq(H.herdOf("chicken", "EUR", -700).year(), -800,
                "but by 800 BC the Mediterranean has them, kept for cockfighting before the pot");
        ok(H.herdOf("chicken", "SAS", -700) != null,
                "and South Asia gets them from the east, not the other way round");

        // -------------------------------------------------------------- 5. THE HERD THAT ENDED
        ok(H.herdOf("bison", "NNA", 1800) != null, "the bison herd is there in 1800");
        ok(H.herdOf("bison", "NNA", 1900) == null, "and gone by 1900");
        Herds.Herd bison = H.herd("bison_plains");
        eq(bison.markAt(1889), "recorded", "in 1889 it is still a recorded herd");
        eq(bison.markAt(1890), "gone", "and in 1890 it is not");
        ok(bison.note().contains("1,091"), "Hornaday counted 1,091 in 1889");
        // A KEPT herd does not end: this is the projection rule, and it is why the two differ.
        eq(mesta.markAt(3000), "recorded", "a kept herd carries on, so Castile still has sheep");

        // -------------------------------------------------------------- 6. DROVES OPEN AND SHUT
        Herds.Drove chisholm = H.drove("chisholm");
        ok(!chisholm.open(1800), "the Chisholm Trail is not a road in 1800");
        ok(chisholm.open(1870), "it is in 1870");
        ok(!chisholm.open(1900), "and it is not in 1900");
        ok(chisholm.shutWhy(1800).contains("not a road yet"), "and it says so: "
                + chisholm.shutWhy(1800));
        ok(chisholm.shutWhy(1900).contains("closed"), "and says when it closed: "
                + chisholm.shutWhy(1900));
        eq(chisholm.end(), 1884, "the last year is 1884");
        ok(chisholm.note().contains("barbed wire"), "closed by barbed wire and a quarantine law");

        // On the ground.
        ok(H.droveAt(33.0, -97.5, 1800) == null, "standing in Texas in 1800 there is no drove");
        Herds.Drove on = H.droveAt(33.0, -97.5, 1870);
        ok(on != null, "in 1870 there is one");
        ok(on != null && "chisholm".equals(on.id()), "the Chisholm");
        ok(H.droveAt(10.0, 100.0, 1870) == null, "and nothing in Siam, ever");

        // -------------------------------------------------------------- 7. HERDS BY AREA AND YEAR
        Set<String> andes = H.herdAnimalsAt("SAM", 1400);
        ok(andes.contains("llama"), "the Andes have llamas in 1400: " + andes);
        ok(!andes.contains("sheep") && !andes.contains("cattle"),
                "and no sheep or cattle before 1540: " + andes);
        ok(H.herdAnimalsAt("SAM", 1600).contains("cattle"), "but by 1600 the cattle have arrived");
        ok(H.herdAnimalsAt("AUS", 1700).isEmpty(), "Australia has no herd at all in 1700");
        ok(H.herdAnimalsAt("AUS", 1800).contains("sheep"), "and merinos by 1800");

        // The yields really do change with the animal, which is the difference between a beast
        // and an industry.
        Set<String> y1400 = H.yieldsAt("EUR", 1400);
        ok(y1400.contains("wool"), "Europe in 1400 gets wool: " + y1400);
        ok(y1400.contains("manure"), "and manure, which is the fertiliser of the open field");
        Set<String> y1600 = H.yieldsAt("SAM", 1600);
        ok(y1600.contains("hide"), "Spanish America in 1600 gets hides: " + y1600);
        // And it ALREADY had wool, from the llama, six thousand years before the sheep arrived.
        // The fibre was never the missing thing in the Andes; the draught animal was.
        ok(y1600.contains("wool"), "and wool, from the llama, which got there first");
        // A hide arrives in 1400 too, and from the LLAMA: the thing the Andes lacked was never a
        // carcass or a fleece, it was a draught animal.
        ok(H.yieldsAt("SAM", 1400).contains("hide"), "and it had hides in 1400, from the llama");
        ok(H.herdOf("cattle", "SAM", 1400) == null, "but no cattle: " + H.herdAnimalsAt("SAM", 1400));
        ok(H.herdOf("cattle", "SAM", 1600) != null, "and cattle in 1600");

        // -------------------------------------------------------------- 8. THE JOIN TO PART 2
        // Six thousand years of herds and no draught animal. This is the sharpest join in the step.
        ok(H.canPull("llama") == false, "a llama cannot pull, asked of part 2's own register");
        ok(H.canPull("horse"), "a horse can");
        ok(H.canPull("ox"), "an ox can");
        // Part 6's report at Cusco in 1400 is NOT empty, and the one entry in it is the finding:
        // the only thing in the Andes that can draw a cart is a DOG, because a dog can and a
        // llama cannot. Six thousand years of herds, and the draught animal was a dog.
        List<String> pull = VehicleMods.get().pullAnimals("SAM", 1400);
        ok(!pull.contains("minecraft:llama"), "part 6's pull_animals has no llama at Cusco: " + pull);
        ok(!pull.contains("minecraft:horse"), "and no horse either: " + pull);
        ok(pull.contains("minecraft:wolf"), "the one beast that can draw a cart there is a dog: "
                + pull);

        // -------------------------------------------------------------- 9. THE MARKS AND REFUSALS
        ok(H.refusals().size() >= 4, H.refusals().size() + " claims are refused");
        boolean chicks = false;
        for (String r : H.refusals()) if (r.contains("8000 BC")) chicks = true;
        ok(chicks, "including the chicken's old date");
        for (Herds.Herd h : H.herds()) {
            ok(h.mark().equals("recorded") || h.mark().equals("estimated"),
                    h.id() + " carries a mark: " + h.mark());
            ok(h.source() != null && !h.source().isBlank(), h.id() + " cites a source");
        }

        // -------------------------------------------------------------- 10. THE FAR END
        // AD 3000 is a projection, and a herd is a continuable state: it does not end.
        ok(!H.herdsAt("EUR", 3000).isEmpty(), "Europe still has herds in AD 3000");
        ok(H.herdOf("cattle", "WAS", 3000) != null, "including cattle in West Asia");
        ok(H.herdOf("sheep", "EUR", 3000) != null, "and sheep in Europe");
        // But a bison that was destroyed stays destroyed: this register does not restore it.
        ok(H.herdOf("bison", "NNA", 3000) == null, "and the bison is still gone in AD 3000");
        ok(H.droveAt(33.0, -97.5, 3000) == null, "and the Chisholm Trail is not rebuilt");

        System.out.println("== step 46 herds: " + checks + " checks, " + failed + " failed ==");
        if (failed > 0) System.exit(1);
    }
}
