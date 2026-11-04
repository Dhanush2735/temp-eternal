package org.slf4j;
/** Stub so TerraOsmBridge compiles outside a Forge build. Nothing reads it in a probe. */
public interface Logger {
    void debug(String s);
    void debug(String s, Object a);
    void info(String s);
    void info(String s, Object a);
    void warn(String s);
    void warn(String s, Object a);
    void error(String s, Object a);
}
