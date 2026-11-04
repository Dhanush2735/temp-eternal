package com.eternalengine.clock;

/** Headless stand-in for the world calendar: no world, so nobody has set a date. See the stub beside this one. */
public final class WorldCalendar {

    /** The same sentinel the real calendar uses for "the world has not dated this". */
    public static final int ALWAYS = Integer.MIN_VALUE;

    private WorldCalendar() {
    }

    public static int today() {
        return ALWAYS;
    }
}
