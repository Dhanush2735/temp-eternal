import com.eternalengine.testing.Findings;

import java.lang.reflect.Method;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Step 61 part 4: the chain. The triage register holds every known problem exactly once with its
 * bucket and owner; the problem-60 fix really exists and does what the row asked; and the two code
 * verifications (82 is stale, 78 is not our tree) are checked against the sources on disk.
 */
public class Step61ChainProbe {

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

        // ---- the register: 83 rows, each triaged exactly once ----
        List<Findings.Finding> findings = Findings.findings();
        eq(83, findings.size(), "the register holds 83 findings");
        Set<Integer> numbers = new HashSet<>();
        for (Findings.Finding finding : findings) {
            ok(numbers.add(finding.problem()), "every problem number appears once: " + finding.problem());
            ok(finding.bucket() != null, "every finding has a bucket: " + finding.problem());
            ok(!finding.resolution().isEmpty(), "every finding has a resolution: " + finding.problem());
        }
        eq(83, numbers.size(), "the numbers 1..83 are all present");
        for (int n = 1; n <= 83; n++) {
            ok(numbers.contains(n), "problem " + n + " is in the register");
        }
        for (int n = 1; n <= 83; n++) {
            ok(Findings.of(n) != null, "of(" + n + ") finds the finding");
        }

        System.out.println("part 1 (the register): " + (checks - part1) + " checks, " + (failed - f1) + " failed");
        int part2 = checks;
        int f2 = failed;

        // ---- the buckets add up to the survey's triage ----
        eq(16, Findings.counts().get(Findings.Bucket.FIXED_IN_AN_EARLIER_STEP), "16 closed rows");
        eq(2, Findings.counts().get(Findings.Bucket.PARTLY_FIXED), "2 partly-fixed rows (23, 42)");
        eq(1, Findings.counts().get(Findings.Bucket.FIXED_IN_STEP_61), "1 row fixed now (60)");
        eq(28, Findings.counts().get(Findings.Bucket.HANDLED_BY_A_COMPLETED_STEP), "28 rows handled by completed steps");
        eq(4, Findings.counts().get(Findings.Bucket.NEEDS_A_REAL_SCREEN), "4 rows need a real screen");
        eq(15, Findings.counts().get(Findings.Bucket.NEEDS_DATA_WE_DO_NOT_HAVE), "15 rows need data we do not have");
        eq(6, Findings.counts().get(Findings.Bucket.NEEDS_A_FACT_CHECK), "6 rows need a fact check");
        eq(7, Findings.counts().get(Findings.Bucket.NEEDS_A_TERRA_PATCH), "7 rows need a Terra++ patch");
        eq(2, Findings.counts().get(Findings.Bucket.OLD_CODE_NOT_REVIEWED), "2 rows are old unreviewed code");
        eq(2, Findings.counts().get(Findings.Bucket.DOCUMENTED_LIMIT), "2 rows are documented limits");
        int sum = 0;
        for (int c : Findings.counts().values()) {
            sum += c;
        }
        eq(83, sum, "the buckets sum to 83");

        // ---- the rows that carry the most weight ----
        for (int n : List.of(11, 14, 19, 30)) {
            Findings.Finding f = Findings.of(n);
            eq(Findings.Bucket.NEEDS_A_REAL_SCREEN, f.bucket(), "problem " + n + " needs a real screen");
            ok(f.resolution().contains("step 60"), "problem " + n + " names step 60's test");
        }
        Findings.Finding sixty = Findings.of(60);
        eq(Findings.Bucket.FIXED_IN_STEP_61, sixty.bucket(), "problem 60 is fixed in this step");
        ok(sixty.resolution().contains("prettyTitle"), "problem 60 names its fix");
        eq(List.of(60), Findings.fixedNow(), "fixedNow lists exactly problem 60");
        Findings.Finding eightyTwo = Findings.of(82);
        eq(Findings.Bucket.HANDLED_BY_A_COMPLETED_STEP, eightyTwo.bucket(), "problem 82 is handled");
        ok(eightyTwo.resolution().contains("BuildingLife") && eightyTwo.resolution().contains("stale"),
                "problem 82 says it was verified stale");
        Findings.Finding seventyEight = Findings.of(78);
        eq(Findings.Bucket.NEEDS_A_TERRA_PATCH, seventyEight.bucket(), "problem 78 is a Terra++ patch");
        ok(seventyEight.resolution().contains("never calls it"), "problem 78 records the verification");
        eq(Findings.Bucket.DOCUMENTED_LIMIT, Findings.of(24).bucket(), "problem 24 is the model's own shape");
        eq(Findings.Bucket.PARTLY_FIXED, Findings.of(23).bucket(), "problem 23 keeps its residue");

        String rule = Findings.ruleLine();
        ok(rule.contains("exactly once"), "the rule: triaged exactly once");
        ok(rule.contains("re-marked, not assumed fixed"), "the rule: re-marked, not assumed");
        ok(rule.contains("prettyTitle"), "the rule names the fix");

        System.out.println("part 2 (the buckets): " + (checks - part2) + " checks, " + (failed - f2) + " failed");
        int part3 = checks;
        int f3 = failed;

        // ---- the problem-60 fix, through TownFacts.prettyTitle ----
        Class<?> townFacts = Class.forName("com.eternalengine.civilization.TownFacts");
        Method pretty = townFacts.getDeclaredMethod("prettyTitle", String.class);
        pretty.setAccessible(true);
        String[][] cases = {
                {"the mayor of Paris", "the Mayor of Paris"},
                {"mayor of Paris", "Mayor of Paris"},
                {"prime minister of the United Kingdom", "Prime Minister of the United Kingdom"},
                {"President of the United States", "President of the United States"},
                {"chairman of the board", "Chairman of the Board"},
                {"Taoiseach", "Taoiseach"},
                {"the Taoiseach", "the Taoiseach"},
                {"MAYOR OF PARIS", "Mayor of Paris"},
                {"governor of new york", "Governor of New York"},
                {"pr\u00e9sident de la R\u00e9publique", "Pr\u00e9sident de la R\u00e9publique"},
                {"commander of the honourable order of the bath, and of the order of merit",
                        "Commander of the Honourable Order of the Bath"},
                {"  lord mayor   of  london ", "Lord Mayor of London"},
                {"the", "The"},
                {"the ", "The"},
                {"   ", ""},
                {null, ""}
        };
        for (String[] c : cases) {
            String actual = (String) pretty.invoke(null, c[0]);
            eq(c[1], actual, "prettyTitle(" + c[0] + ")");
        }

        // the fix is wired where the titles are printed
        String townFactsSrc = Files.readString(Path.of(
                "/home/user/eternal/src/main/java/com/eternalengine/civilization/TownFacts.java"));
        ok(townFactsSrc.contains("prettyTitle(offTitle[office])"),
                "holderLine runs titles through prettyTitle");
        ok(townFactsSrc.contains("the mayor of Paris"), "the wording pass documents the row's example");

        System.out.println("part 3 (the fix): " + (checks - part3) + " checks, " + (failed - f3) + " failed");
        int part4 = checks;
        int f4 = failed;

        // ---- the two code verifications, against the sources ----
        String buildingLife = Files.readString(Path.of(
                "/home/user/eternal/src/main/java/com/eternalengine/buildings/BuildingLife.java"));
        ok(buildingLife.contains("FamousBuildings"),
                "BuildingLife really reads the famous-buildings register (problem 82 is stale)");

        Path srcRoot = Path.of("/home/user/eternal/src/main/java");
        boolean anyInfer = false;
        try (var files = Files.walk(srcRoot)) {
            for (Path p : files.filter(p -> p.toString().endsWith(".java")).toList()) {
                // Findings.java is the record that names problem 78; naming is not calling.
                if (p.toString().endsWith("testing" + java.io.File.separator + "Findings.java")) {
                    continue;
                }
                if (Files.readString(p).contains("inferStartYear")) {
                    anyInfer = true;
                    problems.add("found inferStartYear in " + p);
                }
            }
        }
        ok(!anyInfer, "nothing in this mod's tree calls inferStartYear (problem 78 is Terra++'s)");

        // the register is pure Java and the fix is compiled: the classes are on this run's path
        ok(Class.forName("com.eternalengine.testing.Findings") != null, "Findings loads");

        System.out.println("part 4 (the verifications): " + (checks - part4) + " checks, "
                + (failed - f4) + " failed");

        System.out.println();
        System.out.println("Step 61 chain probe: " + checks + " checks, " + failed + " failed");
        for (String p : problems) {
            System.out.println(p);
        }
        if (failed > 0) {
            System.exit(1);
        }
    }
}
