/* Step 47 part 5 (B5): wild animals by era.
   The claim: a wild animal's data is not its birth date but the year its range ended, and the
   absence with a reason (a horse in the Americas) is data and not a missing row. */
import com.eternalengine.wild.Wildlife;

import java.util.List;
import java.util.Map;

public class Step47WildlifeProbe {
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

    public static void main(String[] args) {
        Wildlife w = Wildlife.get();
        System.out.println("  " + w.summary());

        // ------------------------------------------------ 1. THE REGISTER LOADS AND IS A REGISTER
        ok(w.count() >= 12, "the register carries a dozen wild animals: " + w.count());
        eq(w.areas().size(), 17, "over the mod's 17 areas");
        ok(w.has("lion") && w.has("cheetah") && w.has("aurochs") && w.has("horse_wild"),
                "including every animal the plan names");
        ok(w.extirpatedSomewhere() >= 6, "and most of them have lost ground somewhere: "
                + w.extirpatedSomewhere());

        // ------------------------------------------------ 2. THE PLAN'S OWN EXAMPLES
        // "lions and cheetahs in India"
        ok(w.present("lion", "SAS", 1500), "a lion in India in 1500");
        ok(w.present("lion", "SAS", 1800), "still there in 1800");
        ok(!w.present("lion", "SAS", 1900), "and gone by 1900: the wild lion outside Gir ends 1884");
        ok(w.present("cheetah", "SAS", 1600), "a cheetah in India in 1600");
        ok(!w.present("cheetah", "SAS", 1990), "and gone before 1990: the Indian cheetah is 1952");

        // "aurochs in Europe"
        ok(w.present("aurochs", "EUR", -1000), "an aurochs in Europe in 1000 BC");
        ok(w.present("aurochs", "EUR", 1600), "still there in 1600");
        ok(!w.present("aurochs", "EUR", 1650), "and the last one died at Jaktorow in 1627");
        eq(w.species("aurochs").goneYear("EUR"), 1627, "the year is in the data: 1627");

        // "no horses in the Americas before 1493", which is what this register is FOR
        ok(!w.present("horse_wild", "NNA", 1200), "no horse in North America in 1200");
        ok(!w.present("horse_wild", "SAM", 1400), "none in South America in 1400");
        Wildlife.Answer horse = w.why("horse_wild", "NNA", 1200);
        eq(horse.kind(), "never", "and the answer is NEVER, not 'not yet'");
        ok(horse.why().contains("Pleistocene"), "with the reason: " + horse.why());
        ok(w.species("horse_wild").neverHere("NNA"), "the absence is recorded, not left out");
        // and the live animal is still there where it is from
        ok(w.present("horse_wild", "EEU", 1200), "while the steppe has horses throughout");

        // ------------------------------------------------ 3. THREE STORIES, THREE ANSWERS
        // (a) gone from here, alive there
        Wildlife.Answer greece = w.why("lion", "EUR", 100);
        eq(greece.kind(), "gone", "the Greek lion is GONE: " + greece.why());
        ok(w.present("lion", "EAF", 100), "and the East African lion at the same moment is not");
        // (b) gone everywhere
        ok(!w.present("passenger_pigeon", "NNA", 1920), "the passenger pigeon after Martha, 1914");
        eq(w.species("passenger_pigeon").goneYear("NNA"), 1914, "1914");
        ok(!w.present("thylacine", "AUS", 1950), "and the thylacine after 1936");
        // (c) never there
        Wildlife.Answer cat = w.why("cheetah", "AUS", 1000);
        eq(cat.kind(), "never", "a cheetah in Australia is NEVER, and not 'not yet'");
        ok(!cat.recorded(), "which is what recorded() is for: a never is not a record of absence "
                + "in time, it is a different kind of fact");

        // ------------------------------------------------ 4. THE THREE ANSWERS DIFFER
        ok(!greece.kind().equals(horse.kind()), "'gone' and 'never' are different answers, which is "
                + "the whole point: an extirpated animal can come back and one that never lived "
                + "there is not a conservation problem");
        ok(w.why("lion", "EUR", 100).why().contains("100"), "a 'gone' answer carries the year: "
                + w.why("lion", "EUR", 100).why());
        eq(w.why("nonesuch", "EUR", 100).kind(), "unknown", "an unknown species is 'unknown'");

        // ------------------------------------------------ 5. WHAT IS IN A PLACE AT A TIME
        List<String> deccan1900 = w.inArea("SAS", 1900);
        ok(deccan1900.contains("tiger"), "the Deccan in 1900 has a tiger: " + deccan1900);
        ok(!deccan1900.contains("lion"), "and no lion, since 1884");
        List<String> sahara = w.inArea("NAF", 2000);
        ok(sahara.contains("crocodile"), "the Nile in 2000 still has its crocodile");
        ok(!sahara.contains("hippopotamus"), "and lost its hippo in the delta by 1800");
        System.out.println("  India 1900: " + deccan1900);
        System.out.println("  North Africa 2000: " + sahara);

        // ------------------------------------------------ 6. THE LOSSES ARE LISTED
        Map<String, Integer> lionLosses = w.losses("lion");
        ok(lionLosses.size() >= 5, "the lion has lost six areas inside the record: " + lionLosses);
        ok(lionLosses.containsKey("EUR") && lionLosses.get("EUR") == -100,
                "Greece by 100 BC");
        ok(lionLosses.get("SAS") == 1884, "and India in 1884");

        // ------------------------------------------------ 7. A UNIFORM CASE, TO SHOW THE REST
        ok(w.present("crocodile", "EAF", -2500) && w.present("crocodile", "EAF", 2500),
                "the crocodile is here in 2500 BC and in AD 2500: most rows in a wildlife register "
                + "are not like this one");
        ok(w.present("elephant_wild", "SAS", 1800), "the wild elephant is still in India");
        ok(!w.present("elephant_wild", "WAS", 0), "and the Syrian elephant is gone by AD 1");

        // ------------------------------------------------ 8. A VERDICT NEVER PUNISHES
        for (Wildlife.Answer a : List.of(greece, horse, cat)) {
            String line = a.species() + "/" + a.area() + ": " + a.kind() + " " + a.why();
            ok(!line.toLowerCase().contains("penalty") && !line.toLowerCase().contains("ban"),
                    "no answer mentions a penalty: " + line);
        }
        ok(w.why("lion", "SAS", 1900).kind().equals("gone"), "a lion in India in 1900 reads 'gone' "
                + "and says when, and says nothing about what to do about it");

        System.out.println(failed == 0
                ? "Step47WildlifeProbe: " + checks + " checks, 0 failed"
                : "Step47WildlifeProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
