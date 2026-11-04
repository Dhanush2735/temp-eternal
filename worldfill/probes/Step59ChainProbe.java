import com.eternalengine.player.FirstSteps;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Step 59 part 4: the chain. A new player walks the route in order and out of order, the refusals
 * and once-only rules hold, and every command named in the steps is checked against the real
 * command tree on disk (a guide that names commands that do not exist is a lie).
 */
public class Step59ChainProbe {

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

    static void refuse(java.util.function.Supplier<FirstSteps.Answer> call, String needle, String label) {
        FirstSteps.Answer a = call.get();
        ok(!a.ok(), label + " is refused");
        ok(a.refused().contains(needle), label + " refusal says \"" + needle + "\" (actual: " + a.refused() + ")");
    }

    public static void main(String[] args) throws Exception {
        int part1 = checks;
        int f1 = failed;

        // ---- the route: six steps, each naming its command and its rule ----
        List<FirstSteps.Step> steps = FirstSteps.steps();
        eq(6, steps.size(), "the route has six steps");
        Set<FirstSteps.Fact> facts = new HashSet<>();
        for (FirstSteps.Step step : steps) {
            eq(step.index(), steps.indexOf(step) + 1, "the steps are numbered in order");
            ok(!step.title().isEmpty(), "every step has a title");
            ok(!step.doThis().isEmpty(), "every step says what to do");
            ok(!step.command().isEmpty(), "every step names a command");
            ok(!step.teaches().isEmpty(), "every step says what it teaches");
            ok(facts.add(step.doneWhen()), "every step has its own fact: " + step.doneWhen());
            ok(step.line(false).contains("(/ee " + step.command() + ")"),
                    "the line names the exact command: " + step.title());
        }
        eq(6, facts.size(), "the six facts are all used once");
        for (FirstSteps.Fact fact : FirstSteps.Fact.values()) {
            ok(facts.contains(fact), "every fact is attached to a step: " + fact);
        }

        System.out.println("part 1 (the route): " + (checks - part1) + " checks, " + (failed - f1) + " failed");
        int part2 = checks;
        int f2 = failed;

        // ---- Ada walks it in order ----
        FirstSteps.Progress start = FirstSteps.progress("Ada");
        eq(0, start.count(), "Ada starts with nothing counted");
        eq(1, FirstSteps.next("Ada").index(), "the next step is the first one");
        String page0 = String.join("\n", FirstSteps.page("Ada"));
        ok(page0.contains("0 of 6 done"), "the page says nothing is done");
        ok(page0.contains("not yet"), "the page marks the steps not yet walked");

        FirstSteps.Answer one = FirstSteps.mark("Ada", "seen date");
        ok(one.ok(), "counting the first fact works");
        ok(one.line().contains("counted: seen date (1 of 6 steps)"), "the count says 1 of 6");
        ok(one.line().contains("Next: 2. Talk to a person (/ee talk)"), "the next step is pointed out");

        FirstSteps.Answer again = FirstSteps.mark("Ada", "SEEN_DATE");
        ok(again.ok(), "counting twice is not an error");
        ok(again.line().contains("already counted: seen date (1 of 6 steps)"), "and says already counted");
        eq(1, FirstSteps.progress("Ada").count(), "nothing is double counted");

        refuse(() -> FirstSteps.mark("Ada", "dragon riding"), "there is no such fact to count",
                "an unknown fact");
        FirstSteps.Answer unknown = FirstSteps.mark("Ada", "dragon riding");
        ok(unknown.refused().contains("seen date") && unknown.refused().contains("heard time rules"),
                "the refusal lists the six facts");
        refuse(() -> FirstSteps.mark("Ada", ""), "a fact with no name", "a blank fact");
        refuse(() -> FirstSteps.mark("Ada", null), "a fact with no name", "a missing fact (check order: the player is fine)");
        refuse(() -> FirstSteps.mark("", "seen date"), "a player with no name", "a blank player");
        refuse(() -> FirstSteps.graduate("Ada"), "the route is not finished: 2. Talk to a person",
                "graduating too early");
        FirstSteps.Answer early = FirstSteps.graduate("Ada");
        ok(early.refused().contains("(/ee talk)") && early.refused().contains("(1 of 6 done)"),
                "the early refusal names the step and the count");

        FirstSteps.Answer last = null;
        for (String fact : List.of("spoke to someone", "looked at the purse", "bought a book",
                "heard the era", "heard time rules")) {
            last = FirstSteps.mark("Ada", fact);
        }
        ok(last.line().contains("The route is finished: /ee firststeps graduate."),
                "the last mark points at the graduation");
        ok(FirstSteps.next("Ada") == null, "nothing is left to walk");

        FirstSteps.Answer grad = FirstSteps.graduate("Ada");
        ok(grad.ok(), "the graduation is earned now");
        String gradLine = grad.line();
        ok(gradLine.contains("3000 BC to AD 3000"), "the graduation names the years");
        ok(gradLine.contains("the record ends at 2026"), "the graduation names where the record ends");
        ok(gradLine.contains("projected"), "the graduation marks the projections");
        FirstSteps.Answer grad2 = FirstSteps.graduate("Ada");
        ok(grad2.ok() && grad2.line().contains("already graduated: the line was earned once and stands"),
                "graduating twice says so and does not reprint");
        String page1 = String.join("\n", FirstSteps.page("Ada"));
        ok(page1.contains("6 of 6 done"), "the page says all six are done");
        ok(page1.contains("You have your bearings"), "the page shows the earned line");

        System.out.println("part 2 (Ada walks it in order): " + (checks - part2) + " checks, "
                + (failed - f2) + " failed");
        int part3 = checks;
        int f3 = failed;

        // ---- Bob walks it out of order: the sequence is the next step, not the order walked ----
        for (String fact : List.of("heard time rules", "bought a book", "spoke to someone",
                "heard the era", "looked at the purse", "seen date")) {
            FirstSteps.mark("Bob", fact);
        }
        eq(6, FirstSteps.progress("Bob").count(), "Bob counted all six out of order");
        ok(FirstSteps.next("Bob") == null, "Bob is finished too");
        ok(FirstSteps.graduate("Bob").ok(), "Bob graduates");
        eq(6, FirstSteps.progress("Ada").count(), "Ada's notes are untouched by Bob");
        FirstSteps.Answer trimmed = FirstSteps.mark("  Ada  ", "seen date");
        ok(trimmed.line().contains("already counted"), "the player name is trimmed before it is looked up");

        // ---- the rules, in words ----
        String rule = FirstSteps.ruleLine();
        ok(rule.contains("written once") && rule.contains("no reset"), "the rule says notes are written once");
        String grad0 = FirstSteps.graduation().line();
        ok(grad0.contains("a purse cannot go below zero"), "the graduation repeats the purse rule");
        ok(grad0.contains("a branch is a difference from its parent"), "the graduation repeats the branch rule");
        ok(grad0.contains("notes are written once"), "the graduation repeats the notes rule");

        System.out.println("part 3 (out of order, and the rules): " + (checks - part3) + " checks, "
                + (failed - f3) + " failed");
        int part4 = checks;
        int f4 = failed;

        // ---- every command named in the steps exists in the real command tree ----
        Path cmdDir = Path.of("/home/user/eternal/src/main/java/com/eternalengine/commands");
        StringBuilder tree = new StringBuilder();
        try (var files = Files.walk(cmdDir)) {
            for (Path p : files.filter(p -> p.toString().endsWith(".java")).toList()) {
                tree.append(Files.readString(p)).append('\n');
            }
        }
        for (FirstSteps.Step step : steps) {
            ok(tree.toString().contains("literal(\"" + step.command() + "\")"),
                    "the command tree really has literal(\"" + step.command() + "\") for step "
                            + step.index() + " " + step.title());
        }
        ok(tree.toString().contains("literal(\"firststeps\")"),
                "the command tree really has literal(\"firststeps\")");
        Path module = cmdDir.resolve("FirstStepsCommands.java");
        String moduleText = Files.readString(module);
        ok(moduleText.contains("implements CommandModule"), "the module joins the command framework");
        ok(moduleText.contains("notes are written once"), "the module refuses reset with the notes rule");
        String mod = Files.readString(Path.of("/home/user/eternal/src/main/java/com/eternalengine/EternalEngineMod.java"));
        ok(mod.contains("CommandModuleRegistry") && mod.contains("FirstStepsCommands"),
                "EternalEngineMod wires the module registry");
        ok(tree.toString().contains("/ee firststeps - New here?"),
                "the help text points new players at the route");

        System.out.println("part 4 (the commands exist): " + (checks - part4) + " checks, "
                + (failed - f4) + " failed");

        System.out.println();
        System.out.println("Step 59 chain probe: " + checks + " checks, " + failed + " failed");
        for (String p : problems) {
            System.out.println(p);
        }
        if (failed > 0) {
            System.exit(1);
        }
    }
}
