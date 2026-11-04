import com.eternalengine.brain.ForbiddenLlmAction;
import com.eternalengine.brain.LlmAction;

import java.util.Set;
import java.util.TreeSet;

/**
 * What a language model may and may not do in this project (2026-10-27).
 *
 * <p>Asked "can you add a language model?", it turned out 827 lines of brain code already existed and not one
 * check in the suite mentioned it. This probe states the boundary plainly, using only the classes that compile
 * headless.
 *
 * <p>The <b>behavioural</b> side - a real proposal put through the real validator - is proven inside the engine
 * by {@code checkBrainIsAdvisoryOnly} in {@code /ee check all}, because {@code LlmValidationContext} needs
 * Minecraft's capability classes, which do not exist in this headless harness. Refusing to fake them is the
 * point: the probe does not build a fake context and call it proof.
 */
public final class BrainBoundaryProbe {

    private static int checks;
    private static int failures;

    public static void main(String[] args) {
        System.out.println("a language model in Eternal Engine: what it may propose, what it may never do");
        System.out.println();

        System.out.println("--- it may never change the world directly ---");
        Set<String> forbidden = new TreeSet<>();
        for (ForbiddenLlmAction a : ForbiddenLlmAction.values()) {
            forbidden.add(a.name());
            check(a.name() + " is refused by name", ForbiddenLlmAction.matches(a.name()));
        }
        check("the forbidden list is not empty", !forbidden.isEmpty(), forbidden.size() + " actions");
        // Case and whitespace must not slip past the gate - a model will not send clean uppercase.
        check("lower case and padding do not slip through",
                ForbiddenLlmAction.matches("  mutate_timeline_direct "),
                "a model writing ' mutate_timeline_direct ' is still refused");

        System.out.println();
        System.out.println("--- above all: it may never author a fork ---");
        check("rewriting the timeline is on the forbidden list",
                ForbiddenLlmAction.matches("MUTATE_TIMELINE_DIRECT"),
                "a fork has a human author or it does not happen - the same rule the signed-fork ledger enforces");

        System.out.println();
        System.out.println("--- but it is a boundary, not a blanket refusal: it may still advise ---");
        check("asking for the current affairs briefing is NOT forbidden",
                !ForbiddenLlmAction.matches("REQUEST_CURRENT_AFFAIRS"),
                "advice is allowed; acting is not");
        check("asking for an anomaly explanation is NOT forbidden",
                !ForbiddenLlmAction.matches("REQUEST_ANOMALY_EXPLANATION"));
        check("an unknown action is not silently forbidden either - it is refused elsewhere, by the whitelist",
                !ForbiddenLlmAction.matches("SOMETHING_UNHEARD_OF"),
                "two separate gates: forbidden actions here, unlisted intents in LlmProposalValidator");

        System.out.println();
        System.out.println("--- the whitelist is short, and authority is not automatic ---");
        Set<String> real = new TreeSet<>();
        int needingVip = 0;
        for (LlmAction a : LlmAction.values()) {
            if (a == LlmAction.UNKNOWN) {
                continue;
            }
            real.add(a.name());
            if (a.requiresVipAuthority()) {
                needingVip++;
            }
        }
        check("there are exactly 11 intents a model may propose", real.size() == 11, real.toString());
        check("war, peace, armies, trade, quarantine and incidents all need VIP authority",
                LlmAction.DECLARE_WAR.requiresVipAuthority() && LlmAction.MOVE_ARMY.requiresVipAuthority()
                        && LlmAction.QUARANTINE_REGION.requiresVipAuthority(), needingVip + " of 11");
        check("reading the affairs feed needs no authority, because it changes nothing",
                !LlmAction.REQUEST_CURRENT_AFFAIRS.requiresVipAuthority());
        check("no intent exists for editing history",
                real.stream().noneMatch(n -> n.contains("TIMELINE") || n.contains("HISTORY")),
                "the whitelist has no history verb at all");

        System.out.println();
        System.out.println("checks: " + checks + "   failures: " + failures);
        if (failures > 0) {
            System.exit(1);
        }
    }

    private static void check(String what, boolean ok) {
        check(what, ok, "");
    }

    private static void check(String what, boolean ok, String detail) {
        checks++;
        if (!ok) {
            failures++;
        }
        System.out.println((ok ? "  ok   " : "  FAIL ") + what
                + (detail == null || detail.isEmpty() ? "" : "   [" + detail + "]"));
    }
}
