package com.mojang.logging;
import org.slf4j.Logger;
/** Stub: ProductAtlas keeps one logger and calls LOGGER.info on load. */
public final class LogUtils {
    public static Logger getLogger() {
        return new Logger() {
            public void info(String m, Object... a) {}
            public void warn(String m, Object... a) {}
            public void error(String m, Object... a) {}
        };
    }
}
