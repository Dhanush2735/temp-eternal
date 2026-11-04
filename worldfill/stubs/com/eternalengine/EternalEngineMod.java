package com.eternalengine;

import org.slf4j.Logger;

/** Headless stub (2026-10-24): the probes need the logger, not the mod's Forge bootstrap. */
public final class EternalEngineMod {
    private static final Logger LOGGER = new Logger() {
        @Override public void info(String msg, Object... args) { print("INFO", msg, args); }
        @Override public void warn(String msg, Object... args) { print("WARN", msg, args); }
        @Override public void error(String msg, Object... args) { print("ERROR", msg, args); }
    };

    private EternalEngineMod() {
    }

    public static Logger getLogger() {
        return LOGGER;
    }

    private static void print(String level, String msg, Object[] args) {
        String out = msg;
        if (args != null && args.length > 0) {
            for (Object arg : args) {
                out = out.replaceFirst("\\{\\}", String.valueOf(arg).replace("\\", "\\\\").replace("$", "\\$"));
            }
        }
        System.out.println("[" + level + "] " + out);
    }
}
