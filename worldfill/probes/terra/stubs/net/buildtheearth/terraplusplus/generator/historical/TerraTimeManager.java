package net.buildtheearth.terraplusplus.generator.historical;

// STUB for the step-31 harness only.
// The real class is a Forge @Mod.EventBusSubscriber that ticks the in-game
// clock. WorldLineRegistry needs exactly one thing from it: the MIN_YEAR
// constant, used as the divergence year of the main branch. The value below is
// copied verbatim from the real source (TerraTimeManager.java line 31), so the
// harness runs the REAL WorldLineRegistry unchanged.
public final class TerraTimeManager {

    public static final int MIN_YEAR = -3000;
    public static final int MAX_YEAR = 9999;

    private TerraTimeManager() {}
}
