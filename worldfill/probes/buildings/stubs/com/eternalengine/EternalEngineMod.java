package com.eternalengine;
import org.slf4j.Logger;
/** Stub so TerraOsmBridge compiles outside a Forge build. Only getLogger is used by that file. */
public final class EternalEngineMod {
    public static Logger getLogger() {
        return new Logger() {
            public void debug(String s) {}
            public void debug(String s, Object a) {}
            public void info(String s) {}
            public void info(String s, Object a) {}
            public void warn(String s) {}
            public void warn(String s, Object a) {}
            public void error(String s, Object a) {}
        };
    }
}
