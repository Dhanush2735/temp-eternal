package com.eternalengine.terrabridge;
/**
 * Stub so TerraOsmBridge compiles outside a Forge build. The real class needs a Minecraft Level to
 * turn a block position into a lon/lat; TerraOsmBridge only asks it to sanity-check a coordinate
 * pair, which needs nothing but arithmetic. The check is copied from the real class verbatim.
 */
public final class TerraCoordinateHelper {
    public static boolean isValidCoordinates(double lat, double lon) {
        return lat >= -90.0d && lat <= 90.0d && lon >= -180.0d && lon <= 180.0d;
    }
}
