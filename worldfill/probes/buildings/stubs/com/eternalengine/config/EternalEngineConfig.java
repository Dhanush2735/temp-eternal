package com.eternalengine.config;
/**
 * Stub so TerraOsmBridge compiles outside a Forge build. The real COMMON is a Forge config spec,
 * so osmTimeoutMs is an IntValue you call get() on; this mimics that shape and nothing else.
 */
public final class EternalEngineConfig {
    public static final Common COMMON = new Common();
    public static final class Common {
        public final IntValue osmTimeoutMs = new IntValue();
    }
    public static final class IntValue {
        public int get() { return 30_000; }
    }
}
