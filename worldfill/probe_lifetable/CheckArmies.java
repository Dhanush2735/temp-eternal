package com.eternalengine.lifeprobe;

import com.eternalengine.war.ArmyChecks;

import java.util.ArrayList;
import java.util.List;

/**
 * Runs the {@code armies} part of {@code /ee check} outside the game.
 *
 * <p>The checks live in {@code com.eternalengine.war.ArmyChecks} rather than inside
 * {@code HistoryChecks}, precisely so that this is possible: {@code HistoryChecks} reaches into
 * half the mod and will not compile without Minecraft on the classpath, so {@code probe_check.sh}
 * needs a Gradle build that this sandbox does not keep ({@code build/} is not in the workspace
 * snapshot). Here the very same code runs against the mod's own source and resources every time
 * the probe runs, so a claim cannot pass in the build and fail in the game.
 *
 * <p>Everything here is also covered by {@code ArmiesRun}, the step's own probe. Running it twice
 * is the point: the in-game check and the build-time probe are the same code asking the same
 * questions.
 */
public final class CheckArmies {

    static final List<String> LINES = new ArrayList<>();
    static int ok;
    static int failed;
    static int known;

    public static void main(String[] args) {
        long t0 = System.nanoTime();
        ArmyChecks.run(new ArmyChecks.Sink() {
            @Override
            public void check(boolean good, String text, String whyNot) {
                if (good) {
                    ok++;
                    LINES.add("  ok   " + text);
                } else {
                    failed++;
                    LINES.add("  FAIL " + text);
                    if (whyNot != null && !whyNot.isBlank()) {
                        LINES.add("        because: " + whyNot);
                    }
                }
            }

            @Override
            public void known(String text, String detail) {
                known++;
                LINES.add("  known " + text);
            }

            @Override
            public void info(String text) {
                LINES.add("       " + text);
            }
        });
        long ms = (System.nanoTime() - t0) / 1_000_000L;
        for (String l : LINES) {
            System.out.println(l);
        }
        System.out.println();
        System.out.println("  /ee check armies: " + ok + " passed, " + failed + " failed, "
            + known + " known limits, in " + ms + " ms");
        System.out.println(failed == 0 ? "ALL " + (ok + known) + " ARMIES CHECKS PASSED"
            : failed + " ARMIES CHECKS FAILED");
        if (failed > 0) {
            System.exit(1);
        }
    }
}
