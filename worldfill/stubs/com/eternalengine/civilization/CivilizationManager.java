package com.eternalengine.civilization;

import java.util.List;
import java.util.Optional;

/**
 * STUB for the headless probes (2026-10-22). The real {@code CivilizationManager} reaches
 * {@code EternalEngineMod} and so Forge and the Minecraft jars. {@code HistoricalPresence.query}
 * returns before touching a manager when it is null, which is exactly how the probes call it, so
 * the probe measures the real query path and only the manager branch is unreachable. Every method
 * here refuses rather than pretending: if a probe ever reaches one, it fails loudly.
 */
public final class CivilizationManager {

    private static UnsupportedOperationException noManager() {
        return new UnsupportedOperationException(
                "no CivilizationManager outside Minecraft: the probes pass null on purpose");
    }

    public Optional<Civilization> getCivilization(String id) { throw noManager(); }

    public List<String> ids() { throw noManager(); }

    public TerritoryManager territoryManager() { throw noManager(); }
}
