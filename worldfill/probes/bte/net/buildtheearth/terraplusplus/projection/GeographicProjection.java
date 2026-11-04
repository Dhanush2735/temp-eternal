package net.buildtheearth.terraplusplus.projection;

/**
 * Base interface for geographic projections.
 * Converts between geographic coordinates (lat/lon) and projected coordinates (x/y in blocks).
 */
public interface GeographicProjection {
    
    /**
     * Convert geographic coordinates to projected (block) coordinates.
     * @param latitude Latitude in degrees (-90 to 90)
     * @param longitude Longitude in degrees (-180 to 180)
     * @return Array of [x, z] in block coordinates
     */
    double[] toProjected(double latitude, double longitude);
    
    /**
     * Convert projected (block) coordinates to geographic coordinates.
     * @param x X coordinate in blocks
     * @param z Z coordinate in blocks
     * @return Array of [latitude, longitude] in degrees
     */
    double[] toGeographic(double x, double z);
    
    /**
     * Get the scale at a given point (meters per block).
     */
    double metersPerBlock(double latitude, double longitude);
    
    /**
     * Get the projection name.
     */
    String getName();
    
    /**
     * Check if coordinates are within valid range.
     */
    default boolean isValidGeographic(double latitude, double longitude) {
        return latitude >= -90 && latitude <= 90 && longitude >= -180 && longitude <= 180;
    }
    
    /**
     * Get bounds of this projection in block coordinates.
     * Returns [minX, minZ, maxX, maxZ] or null if unbounded.
     */
    default double[] getBounds() {
        return null;
    }
}
