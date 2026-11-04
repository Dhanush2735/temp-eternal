import com.eternalengine.compatibility.PerformanceMods;
import com.eternalengine.core.PerfGuide;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Step 58 part 4: the chain. The guide answering three players (a laptop, a server, a bad value
 * refused), the mod list packed in its recommended order with every verdict honest, and the player
 * document agreeing with the class that computed its numbers.
 */
public class Step58ChainProbe {

    static int checks = 0;
    static int failed = 0;
    static List<String> problems = new ArrayList<>();

    static void ok(boolean condition, String label) {
        checks++;
        if (!condition) {
            failed++;
            problems.add("FAIL  " + label);
        }
    }

    static void eq(Object expected, Object actual, String label) {
        ok(expected == null ? actual == null : expected.equals(actual),
                label + " (expected=" + expected + " actual=" + actual + ")");
    }

    public static void main(String[] args) throws Exception {
        int part1 = checks;
        int f1 = failed;

        // ---- the floor is arithmetic, and it adds up ----
        eq(2496, PerfGuide.floorMb(), "the memory floor is the sum 2048+128+64+256");
        eq(3520, PerfGuide.comfortableMb(), "the comfortable line is the floor + 1024");
        eq(8, PerfGuide.recommendedViewChunks(), "8 chunks is the recommended view distance");
        eq(2048 + 128 + 64 + 256, PerfGuide.floorMb(), "the sum is really the floor");

        // ---- settings: every tip names its source ----
        List<PerfGuide.Tip> settings = PerfGuide.settings();
        ok(settings.size() >= 6, "the settings list has the presence and tick settings");
        for (PerfGuide.Tip tip : settings) {
            ok(!tip.text().isEmpty(), "a tip has words: " + tip.text().substring(0, Math.min(24, tip.text().length())));
            ok(tip.line().endsWith("[source: " + tip.source().words() + "]"),
                    "a tip line names its source: " + tip.line().substring(0, Math.min(40, tip.line().length())));
        }
        String joined = String.join(" | ", settings.stream().map(PerfGuide.Tip::text).toList());
        ok(joined.contains("presenceDrawnFiguresMax"), "the drawn-figures budget is in the guide");
        ok(joined.contains("presenceCrowdCeiling"), "the crowd ceiling is in the guide");
        ok(joined.contains("32,767"), "Minecraft's packet limit is in the guide");

        System.out.println("part 1 (the numbers and settings): " + (checks - part1) + " checks, "
                + (failed - f1) + " failed");
        int part2 = checks;
        int f2 = failed;

        // ---- a laptop: under the comfortable line, a short view ----
        PerfGuide.Advice laptop = PerfGuide.advise(3072, 6);
        ok(laptop.ok(), "the laptop is not refused");
        String laptopAll = String.join(" / ", laptop.lines());
        ok(laptopAll.contains("clears the floor of 2496"), "the laptop is told where it sits");
        ok(laptopAll.contains("64 blocks"), "6 chunks is spelled out in blocks");
        ok(laptopAll.contains("[source: computed from measured numbers]"),
                "the laptop's memory line names its source");

        // ---- a server: the comfortable line and the recommended view ----
        PerfGuide.Advice server = PerfGuide.advise(4096, 8);
        ok(server.ok(), "the server is not refused");
        String serverAll = String.join(" / ", server.lines());
        ok(serverAll.contains("covers the comfortable line of 3520"), "the server is told it is comfortable");
        ok(serverAll.contains("8 chunks is the recommended line"), "the recommended line is pointed out");
        ok(serverAll.contains("128 blocks"), "8 chunks is spelled out in blocks");

        // ---- a laptop under the floor: advice, not refusal ----
        PerfGuide.Advice tight = PerfGuide.advise(1536, 8);
        ok(tight.ok(), "under the floor is advice, not a refusal");
        ok(String.join(" / ", tight.lines()).contains("below the floor of 2496"),
                "the shortfall is named");

        // ---- a bad value is refused, in the promised order ----
        PerfGuide.Advice noMemory = PerfGuide.advise(0, 8);
        ok(!noMemory.ok(), "a machine with no memory is refused");
        ok(noMemory.refused().contains("a machine given no memory runs nothing"),
                "the memory refusal says why");
        ok(noMemory.refused().contains("2496"), "the memory refusal names the floor");
        ok(noMemory.lines().isEmpty(), "a refusal carries no advice");

        PerfGuide.Advice noView = PerfGuide.advise(4096, -1);
        ok(!noView.ok(), "a view below none is refused");
        ok(noView.refused().contains("below none is no view distance"), "the view refusal says why");

        PerfGuide.Advice tooFar = PerfGuide.advise(4096, 40);
        ok(!tooFar.ok(), "a view past Minecraft's own 32 chunks is refused");
        ok(tooFar.refused().contains("at most 32 chunks"), "the far refusal names the engine's limit");

        // check order: when both are wrong, memory is named first
        PerfGuide.Advice both = PerfGuide.advise(0, -1);
        ok(!both.ok() && both.refused().contains("no memory"),
                "check order: no memory is refused before no view");

        // the long view is told what still happens at 160 blocks
        PerfGuide.Advice longView = PerfGuide.advise(4096, 12);
        ok(String.join(" / ", longView.lines()).contains("hides people at 160 blocks"),
                "the long view is told people hide at 160 blocks");

        String guideRule = PerfGuide.ruleLine();
        ok(guideRule.contains("names its source"), "the guide's rule names sources");
        ok(guideRule.contains("2496") && guideRule.contains("3520"), "the rule carries the computed lines");

        System.out.println("part 2 (the three players): " + (checks - part2) + " checks, "
                + (failed - f2) + " failed");
        int part3 = checks;
        int f3 = failed;

        // ---- the mod list: every verdict honest ----
        List<PerformanceMods.Mod> mods = PerformanceMods.mods();
        eq(6, mods.size(), "the plan names six mods and the register holds six");
        Set<String> names = new HashSet<>();
        for (PerformanceMods.Mod m : mods) {
            names.add(m.name());
            ok(!m.whatItDoes().isEmpty(), "every mod says what it does: " + m.name());
            ok(!m.touches().isEmpty(), "every mod says what in this mod it touches: " + m.name());
            ok(!m.reason().isEmpty(), "every mod has a reason: " + m.name());
            ok(m.line().contains(m.verdict().words()), "the line shows the verdict words: " + m.name());
        }
        ok(names.contains("Spark") && names.contains("ModernFix") && names.contains("FerriteCore")
                        && names.contains("Entity Culling") && names.contains("Embeddium")
                        && names.contains("Canary"),
                "the six named mods are all here");

        int confident = 0;
        int checkLive = 0;
        for (PerformanceMods.Mod m : mods) {
            if (m.verdict() == PerformanceMods.Verdict.PACK_WITH_CONFIDENCE) {
                confident++;
                ok(m.checkedHere(), "pack-with-confidence counts as checked here");
                ok(m.liveTest().isEmpty(), "a confident mod owes no live test: " + m.name());
            } else {
                checkLive++;
                ok(!m.liveTest().isEmpty(), "a check-live mod names its live test: " + m.name());
            }
        }
        eq(3, confident, "three mods pack with confidence");
        eq(3, checkLive, "three mods owe a live test");
        eq(3, PerformanceMods.checkedHere().size(), "checked here names the three");
        eq(3, PerformanceMods.notCheckedHere().size(), "not checked here names the other three");
        ok(PerformanceMods.notCheckedHere().stream().allMatch(s -> s.contains("owes a live test")),
                "the not-checked list is all live tests");

        List<String> pack = PerformanceMods.pack();
        eq(4, pack.size(), "the pack order has four steps");
        ok(pack.get(0).startsWith("1. Spark"), "Spark comes first: measure before you tune");
        ok(pack.get(0).contains("measure before you tune"), "the first rule is spelled out");
        ok(pack.get(3).startsWith("4. Canary"), "the server-side mod comes last");

        String modsRule = PerformanceMods.ruleLine();
        ok(modsRule.contains("Checked here is not checked live"), "the register's rule keeps the split");
        ok(modsRule.contains("No verdict claims a live check that did not happen"),
                "the rule forbids the lie of omission");

        System.out.println("part 3 (the mod list): " + (checks - part3) + " checks, "
                + (failed - f3) + " failed");
        int part4 = checks;
        int f4 = failed;

        // ---- the player document agrees with the class ----
        Path doc = Path.of("/home/user/eternal/HARDWARE_GUIDE.md");
        ok(Files.exists(doc), "the player guide exists at eternal/HARDWARE_GUIDE.md");
        String text = Files.readString(doc);
        ok(text.contains("2,496"), "the doc carries the computed floor");
        ok(text.contains("3,520"), "the doc carries the comfortable line");
        ok(text.contains("2,048") && text.contains("1,024"), "the doc shows the floor's parts");
        ok(text.contains("128 blocks"), "the doc ties 8 chunks to 128 blocks");
        ok(text.contains("32,767"), "the doc names Minecraft's packet limit");
        ok(text.contains("Checked here is not checked live"), "the doc keeps the honesty split");
        ok(text.contains("Spark"), "the doc starts the tuning list with Spark");
        ok(!text.contains("\u2014") && !text.contains("\u2013"), "the doc has no em-dashes");

        System.out.println("part 4 (the document agrees): " + (checks - part4) + " checks, "
                + (failed - f4) + " failed");

        System.out.println();
        System.out.println("Step 58 chain probe: " + checks + " checks, " + failed + " failed");
        for (String p : problems) {
            System.out.println(p);
        }
        if (failed > 0) {
            System.exit(1);
        }
    }
}
