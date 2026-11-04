package com.eternalengine.civilization;

/**
 * STUB (see CivilizationManager): the real class imports {@code net.minecraft.core.BlockPos} and
 * {@code net.minecraft.world.level.Level}. Only the three members HistoricalPresence calls are
 * declared, and each refuses, so nothing can pass by accident.
 */
public final class Civilization {

    private static UnsupportedOperationException noCiv() {
        return new UnsupportedOperationException("no Civilization outside Minecraft");
    }

    public boolean isActiveInYear(int year) { throw noCiv(); }

    public double capitalLat() { throw noCiv(); }

    public double capitalLon() { throw noCiv(); }

    public String id() { throw noCiv(); }

    public String getCurrentName(int year) { throw noCiv(); }

    public String name() { throw noCiv(); }

    public int foundingYear() { throw noCiv(); }

    public int fallYear() { throw noCiv(); }
}
