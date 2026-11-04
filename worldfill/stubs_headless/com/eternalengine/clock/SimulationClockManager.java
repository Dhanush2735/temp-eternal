package com.eternalengine.clock;

/**
 * Headless stand-in for the real clock, used only by probe launchers that need to compile
 * {@code knowledge/KnowledgeDate} without a Minecraft classpath.
 *
 * <p>{@code KnowledgeDate.today()} asks the clock for the current year and falls back to the middle of AD 2000
 * when there is no world. This stub reports "no world", which is exactly what a probe is, so the fallback is the
 * path a probe exercises. Nothing here is ever shipped: it lives in the worldfill tools, not in the mod.
 */
public final class SimulationClockManager {

    private SimulationClockManager() {
    }

    public static boolean isInitialized() {
        return false;
    }

    public static SimulationClockManager getInstance() {
        return null;
    }

    public int getCurrentYear() {
        return 2000;
    }
}
