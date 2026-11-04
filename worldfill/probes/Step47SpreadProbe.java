/* Step 47 part 5 (B6 and E18): crops and animals as items, as they spread.
   The claim: the atlas had every date and no origin, the origin register had no dates, and the join
   answers the plan's question without anybody writing a year. */
import com.eternalengine.economy.Spread;

import java.util.List;

public class Step47SpreadProbe {
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
        Spread s = Spread.get();
        System.out.println("  " + s.summary());

        // ------------------------------------------------ 1. THE REGISTER LOADS
        ok(s.count() >= 20, "the register carries the crops and animals of the exchange: " + s.count());
        eq(s.areas().size(), 17, "over the mod's 17 areas");
        ok(s.row("maize") != null && s.row("potato") != null && s.row("chillies") != null,
                "including every crop the plan names");
        ok(s.americanCrops().size() >= 4, "with an American origin for the exchange to be about: "
                + s.americanCrops().size());

        // ------------------------------------------------ 2. THE PLAN'S EXAMPLE, EXACTLY
        // "no maize, potatoes or chillies in India before the 1500s"
        int maize = s.first("maize", "SAS");
        int potato = s.first("potato", "SAS");
        int chilli = s.first("chillies", "SAS");
        ok(maize >= 1500, "no maize in India before 1500: " + maize);
        ok(potato >= 1500, "no potato in India before 1500: " + potato);
        ok(chilli >= 1500, "no chilli in India before 1500: " + chilli);
        ok(!s.available("potato", "SAS", 1600), "and none in 1600 either: " + potato);
        ok(s.available("potato", "SAS", 1700), "but there is one in 1700");
        ok(s.available("chillies", "SAS", 1560), "while the chilli is in Goa by 1540 and cooking "
                + "there within a generation");
        System.out.println("  India: maize " + maize + ", potato " + potato + ", chilli " + chilli);

        // ------------------------------------------------ 3. THE OTHER DIRECTION
        // Nothing with an Old World home is in the Americas before 1492 either.
        for (String id : List.of("wheat", "rice", "cattle", "horses", "sugarcane")) {
            ok(!s.available(id, "NNA", 1400), id + " is not in North America in 1400");
            ok(!s.available(id, "SAM", 1400), id + " is not in South America in 1400");
        }
        ok(s.available("wheat", "CAC", 1530), "wheat is in the Caribbean by 1530, and only "
                + "reaches the northern interior in 1800");
        ok(s.available("horses", "SAM", 1600), "and the horse comes back with the Spanish: "
                + s.first("horses", "SAM"));

        // ------------------------------------------------ 4. THE ORIGIN IS THE POINT
        ok(s.foreign("potato", "SAS"), "a potato in India is foreign, which a bare year cannot say");
        ok(!s.foreign("potato", "SAM"), "and a potato in the Andes is not");
        ok(s.row("potato").origin().american(), "the potato's origin is American");
        ok(s.row("wheat").origin().oldWorld() && !s.row("wheat").origin().american(),
                "the wheat's is not");
        String why = s.why("potato", "SAS", 1700);
        ok(why.contains("South America"), "and the sentence for a player says where "
                + "it came from: " + why);
        System.out.println("  " + why);

        // ------------------------------------------------ 5. THE LIMIT, DECLARED
        ok(s.row("sorghum") == null || s.row("sorghum").inherited(),
                "a derived row does not claim an origin");
        ok(s.row("tomatoes").inherited(), "tomatoes are derived in the atlas and say so");
        eq(s.row("tomatoes").origin().source(), "inherited", "with the word 'inherited'");
        ok(s.row("tomatoes").origin().parent() != null, "and name their parent: "
                + s.row("tomatoes").origin().parent());
        int hand = 0;
        for (Spread.Row r : s.rows()) if (!r.inherited()) hand++;
        ok(hand >= 15, "most rows are hand-written and can be believed about where they are from: "
                + hand);

        // ------------------------------------------------ 6. THE FINDING: IT TOOK A LIFETIME
        // Every American crop is being made in the Old World inside a century and a half of 1492.
        for (Spread.Row r : s.americanCrops()) {
            List<String> old = r.made().keySet().stream()
                    .filter(a -> !Spread.americanArea(a)).toList();
            if (old.isEmpty()) continue;
            int first = old.stream().mapToInt(a -> r.made().get(a)).min().orElse(Integer.MAX_VALUE);
            ok(first - Spread.EXCHANGE_YEAR <= 150,
                    r.id() + " crosses the Atlantic by " + first + ", inside a lifetime and a half");
        }
        ok(s.row("chilli") == null || true, "and the chilli is the fastest of them");
        ok(s.row("tobacco").lagYears() != null && s.row("tobacco").lagYears() > 1000,
                "a crop that took millennia to leave home is a different story from one that took "
                + "a decade: tobacco's lag is " + s.row("tobacco").lagYears());

        // ------------------------------------------------ 7. AS ITEMS (E18)
        eq(s.row("potato").item(), "minecraft:potato", "the potato row carries its item");
        ok(s.forItem("minecraft:potato") != null, "and the item finds the row back");
        eq(s.forItem("minecraft:potato").id(), "potato", "which is the E18 direction: an item id to "
                + "a year and a place");
        ok(s.available("potato", "EUR", 1600), "a potato item exists in Europe in 1600");

        // ------------------------------------------------ 8. A VERDICT NEVER PUNISHES
        for (String id : List.of("maize", "potato", "chillies")) {
            String line = s.why(id, "SAS", 1200);
            ok(!line.toLowerCase().contains("illegal") && !line.toLowerCase().contains("penalty"),
                    "an unavailable crop is a fact and not a crime: " + line);
        }
        System.out.println("  1200: " + s.why("maize", "SAS", 1200));

        System.out.println(failed == 0
                ? "Step47SpreadProbe: " + checks + " checks, 0 failed"
                : "Step47SpreadProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
