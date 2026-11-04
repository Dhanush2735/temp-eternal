import com.eternalengine.testing.LiveTest;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Step 60 part 3: the chain. The register is complete (every §9 place-year, the timeline's ends,
 * the four deferred looks, a projected year), every test names its source, coverage is computed
 * (not typed), and the session script agrees with the register that generated it.
 */
public class Step60ChainProbe {

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

    /** The named place-years of the world-wide test set (SYSTEMS_PLAN part 9, turn 96). */
    static final String[][] PLAN_STOPS = {
            {"Ur", "2500 BC"}, {"Giza", "2500 BC"}, {"Mohenjo-daro", "2500 BC"}, {"Anyang", "1200 BC"},
            {"Athens", "430 BC"}, {"Pataliputra", "300 BC"}, {"Rome", "AD 100"}, {"Teotihuacan", "AD 500"},
            {"Chang'an", "750"}, {"Baghdad", "900"}, {"Greenland's Norse farms", "1000"}, {"Cahokia", "1100"},
            {"Angkor", "1150"}, {"Great Zimbabwe", "1300"}, {"Timbuktu", "1350"}, {"the Sahara", "1000"},
            {"Tenochtitlan", "1500"}, {"Cusco", "1500"}, {"the Amazon", "1500"}, {"Vijayanagara", "1520"},
            {"Delhi", "1650"}, {"Edo", "1700"}, {"London", "1700"}, {"Paris", "1789"},
            {"Sydney", "1850"}, {"New York", "1920"}, {"Hyderabad", "1948"}, {"Lagos", "1960"},
            {"Moscow", "1980"}, {"Sao Paulo", "2020"}, {"Siberia", "1900"}
    };

    public static void main(String[] args) throws Exception {
        int part1 = checks;
        int f1 = failed;

        // ---- the register: complete, and every test names its source ----
        List<LiveTest.Test> tests = LiveTest.tests();
        eq(55, tests.size(), "the register holds 55 tests");
        Set<String> ids = new HashSet<>();
        Set<LiveTest.Phase> phases = new HashSet<>();
        for (LiveTest.Test test : tests) {
            ok(ids.add(test.id()), "every test id is unique: " + test.id());
            ok(test.phase() != null, "every test has a phase: " + test.id());
            phases.add(test.phase());
            ok(!test.where().isEmpty(), "every test says where: " + test.id());
            ok(!test.when().isEmpty(), "every test says when: " + test.id());
            ok(!test.doThis().isEmpty(), "every test says what to do: " + test.id());
            ok(!test.goodLooks().isEmpty(), "every test says what good looks like: " + test.id());
            ok(!test.from().isEmpty(), "every test names its source: " + test.id());
        }
        eq(8, phases.size(), "all eight phases are used");
        for (LiveTest.Phase phase : LiveTest.Phase.values()) {
            ok(phases.contains(phase), "the phase is in use: " + phase);
        }

        System.out.println("part 1 (the register): " + (checks - part1) + " checks, " + (failed - f1) + " failed");
        int part2 = checks;
        int f2 = failed;

        // ---- coverage is computed from the tests, not typed in ----
        LiveTest.Coverage coverage = LiveTest.coverage();
        eq(31, coverage.namedPlaceYears(), "31 named place-years from the plan's test set");
        eq(6, coverage.continents().size(), "six continents");
        ok(coverage.continents().containsAll(List.of("Africa", "Asia", "Europe", "North America",
                "South America", "Oceania")), "the six continents are the inhabited ones");
        eq(5, coverage.eraBands().size(), "five era bands");
        ok(coverage.eraBands().containsAll(List.of("before 1000 BC", "1000 BC to AD 500",
                "500 to 1500", "1500 to 1800", "1800 to now")), "the era bands are the plan's");
        ok(coverage.timelineEnds(), "both ends of the timeline are covered");
        ok(coverage.projectedYear(), "a projected year is covered");
        ok(coverage.deferredProblems().containsAll(List.of("11", "14", "19", "30")),
                "the four deferred looks (problems 11, 14, 19, 30) each have their test, got "
                        + coverage.deferredProblems());

        // ---- the route: the named stops, in era order, plus the two ends ----
        List<String> route = LiveTest.route();
        eq(33, route.size(), "the route walks 31 named stops plus the timeline's two ends");
        ok(route.get(0).startsWith("2500 BC at Ur"), "the route starts at Ur 2500 BC");
        ok(route.get(route.size() - 1).startsWith("AD 3000"), "the route ends at AD 3000");

        System.out.println("part 2 (coverage): " + (checks - part2) + " checks, " + (failed - f2) + " failed");
        int part3 = checks;
        int f3 = failed;

        // ---- every place-year the plan names is in the register and in the doc ----
        Path doc = Path.of("/home/user/eternal/FINAL_TEST.md");
        ok(Files.exists(doc), "the session script exists at eternal/FINAL_TEST.md");
        String text = Files.readString(doc);
        for (String[] stop : PLAN_STOPS) {
            boolean inRegister = tests.stream().anyMatch(t -> t.where().equals(stop[0])
                    && t.when().equals(stop[1]));
            ok(inRegister, "the register has " + stop[0] + " " + stop[1]);
            ok(text.contains(stop[0]) && text.contains(stop[1]),
                    "the session script has " + stop[0] + " " + stop[1]);
        }

        // ---- the deferred looks name their problem numbers ----
        for (String number : List.of("11", "14", "19", "30")) {
            ok(tests.stream().anyMatch(t -> t.from().contains("problem " + number)),
                    "a test comes from known problem " + number);
            ok(text.contains("known problem " + number), "the script names known problem " + number);
        }

        System.out.println("part 3 (the plan's stops and deferrals): " + (checks - part3) + " checks, "
                + (failed - f3) + " failed");
        int part4 = checks;
        int f4 = failed;

        // ---- the session script agrees with the register ----
        ok(text.contains("55 tests in 8 phases"), "the script carries the computed count");
        for (String heading : List.of("## P -", "## R -", "## X -", "## S -", "## L -", "## F -",
                "## G -", "## M -")) {
            ok(text.contains(heading), "the script has the phase heading " + heading);
        }
        ok(text.contains("3000 BC") && text.contains("AD 3000"), "the script covers the timeline's ends");
        ok(text.contains("projected"), "the script checks the projected mark");
        ok(text.contains("2100 and 2500"), "the script checks a projected year's answers");
        ok(text.contains("Entity Culling") && text.contains("Embeddium") && text.contains("Canary"),
                "the script carries step 58's three live tests");
        ok(text.contains("nobody lives here"), "the script covers empty land");
        ok(text.contains("400 random land points"), "the script covers the world sample");
        ok(text.contains("step 61's input"), "the script says the results go to step 61");
        ok(!text.contains("\u2014") && !text.contains("\u2013"), "the script has no em-dashes");

        String rule = LiveTest.ruleLine();
        ok(rule.contains("names its source"), "the rule: every test names its source");
        ok(rule.contains("computed"), "the rule: coverage is computed");
        ok(rule.contains("never claimed") || rule.contains("the run is never claimed"),
                "the rule: the run is never claimed");

        // the plan itself still defers exactly four rows to this step
        String plan = Files.readString(Path.of("/home/user/worldfill/SYSTEMS_PLAN.md"));
        int deferredRows = (int) plan.lines().filter(l -> l.contains("your final test (step 60)")).count();
        eq(4, deferredRows, "the plan still defers exactly four look rows to step 60");

        System.out.println("part 4 (the script agrees): " + (checks - part4) + " checks, "
                + (failed - f4) + " failed");

        System.out.println();
        System.out.println("Step 60 chain probe: " + checks + " checks, " + failed + " failed");
        for (String p : problems) {
            System.out.println(p);
        }
        if (failed > 0) {
            System.exit(1);
        }
    }
}
