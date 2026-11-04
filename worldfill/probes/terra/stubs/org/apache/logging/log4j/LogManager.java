package org.apache.logging.log4j;

// STUB for the step-31 harness only (see Logger.java).
public final class LogManager {
    private LogManager() {}
    public static Logger getLogger(String name) { return new Logger(); }
    public static Logger getLogger(Class<?> c) { return new Logger(); }
}
