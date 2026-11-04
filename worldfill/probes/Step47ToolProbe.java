/* Step 47 part 2 (E7): the tools.
   The rule under test: a tool's date is not its material's date. A microscope in 2500 BC is not a
   rounding error, it is a derivation bug, and this probe refuses to let it come back. */
import com.eternalengine.tools.Tools;

import java.util.List;
import java.util.Map;
import java.util.Set;

public class Step47ToolProbe {
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

    static final Tools T = Tools.get();

    public static void main(String[] args) {
        System.out.println("== " + T + " ==");
        ok(T.hasData(), "the tool register has data");
        eq(T.problem(), null, "no problem reported");
        ok(T.finding() != null && T.finding().contains("guild"), "the finding names the guild");
        System.out.println("  " + T.summary());

        // -------------------------------------------------------------- 1. THE BUG THAT IS THE POINT
        Tools.Tool mic = T.tool("microscope");
        ok(mic != null, "the microscope is a tool");
        int oldest = Integer.MAX_VALUE;
        for (int y : mic.made().values()) oldest = Math.min(oldest, y);
        ok(oldest >= 1500, "and is not dated to the age of glass: earliest is " + oldest);
        ok(mic.note().contains("2500 BC"), "the row records the bug it corrects");
        // THE ORDERING. A microscope before the telescope's workshop would be a contradiction.
        ok(T.sane("microscope", "telescope", "EUR") || T.sane("telescope", "microscope", "EUR"),
                "the microscope and the telescope are at least comparable in Europe");

        // -------------------------------------------------------------- 2. THE TWO ADDITIONS
        ok(T.tool("loom_warp_weighted") != null, "the warp-weighted loom is here; the atlas has no loom");
        Tools.Tool warp = T.tool("loom_warp_weighted");
        ok(warp.predatesWorld(), "and it is older than the world");
        eq(T.arrival("loom_warp_weighted", "EUR"), -3000,
                "so in Europe its arrival is clamped to 3000 BC, the first year the world has");
        ok(T.has("loom_warp_weighted", "EUR", -3000), "and a player in 3000 BC finds it already there");

        Tools.Tool treadle = T.tool("loom_treadle");
        ok(treadle != null, "the treadle loom is here too");
        ok(treadle.made().get("EAS") < treadle.made().get("EUR"),
                "China has it in " + treadle.made().get("EAS") + ", Europe in " + treadle.made().get("EUR"));
        ok(treadle.note().contains("guild"), "and the row says what it did to who weaves");

        Tools.Tool press = T.tool("printing_movable");
        ok(press != null, "movable type is a tool, not only a print");
        ok(press.made().get("EAS") < press.made().get("EUR"),
                "China 1040 against Europe 1450: " + press.made().get("EAS") + " and "
                        + press.made().get("EUR"));
        // Only 26 letters to cast is WHY it exploded in Europe, and the row must say so.
        ok(press.note().contains("26"), "and the row gives the reason it exploded in Europe");

        // -------------------------------------------------------------- 3. EVERY TOOL RESOLVES
        // A13's rule, applied to an inventory.
        int noItem = 0;
        for (Tools.Tool t : T.tools()) {
            ok(t.vanilla() != null && !t.vanilla().isEmpty(), t.id() + " names an item or a placeholder");
            if (!t.hasItem()) noItem++;
        }
        eq(noItem, T.withNoItem().size(), "withNoItem counts the same " + noItem);
        ok(noItem >= 4, noItem + " have no Minecraft item, and each says so");
        for (Map.Entry<String, String> e : T.withNoItem().entrySet()) {
            ok(e.getValue().toLowerCase().contains("vanilla"),
                    e.getKey() + " explains the absence in its own words");
        }

        // -------------------------------------------------------------- 4. WHAT IT REPLACED
        int noPred = 0;
        for (Tools.Tool t : T.tools()) if (t.replaces() == null) noPred++;
        ok(noPred <= 6, noPred + " tools claim no predecessor");
        ok(T.tool("printing_block").replaces() != null, "woodblock printing replaced the scribe");
        ok(T.tool("printing_movable").replaces().contains("woodblock"),
                "and movable type replaced the block");
        // The tractor is the row that ends step 46's working animals.
        ok(T.tool("tractor").replaces().contains("horse"), "the tractor replaced the horse");
        ok(T.tool("plough_heavy").replaces().contains("ard"), "the heavy plough replaced the ard");

        // -------------------------------------------------------------- 5. PLACE AND YEAR
        Set<String> at1400 = T.familiesAt("EUR", 1400);
        ok(at1400.contains("farm"), "Europe in 1400 farms: " + at1400);
        ok(at1400.contains("write"), "and writes");
        ok(at1400.contains("measure"), "and measures the time");
        ok(!T.has("microscope", "EUR", 1400), "but has no microscope in 1400");
        ok(T.has("microscope", "EUR", 1700), "and has one by 1700");
        ok(!T.has("telegraph", "EUR", 1800), "no telegraph in 1800");
        ok(T.has("telegraph", "EUR", 1850), "and one by 1850");

        // A tool is not universal: the ard in the Americas only with the Europeans.
        ok(!T.has("plough_ard", "SAM", 1000), "no plough in Peru in AD 1000");
        ok(T.has("plough_ard", "SAM", 1600), "and one by 1600");
        // A tool older than the world is present at the first year WHERE IT WAS, and this is not
        // every area. The loom is 5000 BC in Europe and West Asia; the Americas have their own
        // traditions and Australia has none until 1788, and the register says so.
        for (String area : new String[]{"EUR", "EAS", "WAS", "SAS", "EEU"}) {
            ok(T.has("loom_warp_weighted", area, -3000),
                    "the warp-weighted loom is in " + area + " at the first year");
        }
        ok(!T.has("loom_warp_weighted", "AUS", -3000),
                "and it is NOT in Australia in 3000 BC: Australia has no loom until 1788");
        ok(T.arrival("loom_warp_weighted", "AUS") >= 1700,
                "its Australian arrival is " + T.arrival("loom_warp_weighted", "AUS"));
        // But it does predate the world where it exists, so the clamp is real rather than varnished.
        eq(T.arrival("loom_warp_weighted", "EEU"), -3000,
                "and where it is older than the world, the answer is the world's first year");

        // -------------------------------------------------------------- 6. THE CLASS OF ERROR
        // The three orderings that cannot be true. Each is a data bug if it fires.
        ok(T.sane("abacus", "telegraph", "EUR"), "the abacus is older than the telegraph");
        ok(T.sane("plough_ard", "tractor", "EUR"), "the ard is older than the tractor");
        ok(T.sane("paper", "printing_movable", "EAS"),
                "paper in China (105) is older than movable type (1040)");
        // And an unknown tool answers false rather than throwing.
        ok(!T.has("perpetual_motion", "EUR", 2000), "an unknown tool is simply absent");
        eq(T.arrival("perpetual_motion", "EUR"), null, "and has no arrival year");

        // -------------------------------------------------------------- 7. THE WHOLE SPAN
        ok(T.toolsAt("EUR", -3000).size() > 3, "Europe in 3000 BC has "
                + T.toolsAt("EUR", -3000).size() + " tools");
        ok(T.toolsAt("EUR", 3000).size() > T.toolsAt("EUR", -3000).size(),
                "and AD 3000 has more: " + T.toolsAt("EUR", 3000).size());
        ok(T.has("radio", "EUR", 3000), "the radio is still there in AD 3000, as a continuation");
        ok(T.toolsAt("AUS", 1000).size() < T.toolsAt("EUR", 1000).size(),
                "and Australia has fewer tools than Europe in AD 1000");

        List<Tools.Tool> all = T.tools();
        ok(all.size() >= 25, all.size() + " tools in the register");

        System.out.println("== step 47 tools: " + checks + " checks, " + failed + " failed ==");
        if (failed > 0) System.exit(1);
    }
}
