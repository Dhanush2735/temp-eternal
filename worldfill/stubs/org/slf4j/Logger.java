package org.slf4j;
/** Stub: only what ProductAtlas uses, so the probe can compile it without Minecraft. */
public interface Logger {
    void info(String msg, Object... args);
    void warn(String msg, Object... args);
    void error(String msg, Object... args);
}
