package com.eternalengine.civilization;
/** Headless compile stub: exact haversine implementation from HistoricalPresence. */
public final class HistoricalPresence {
    public static double haversineKm(double lat1, double lon1, double lat2, double lon2) {
        double r = 6371.0d;
        double p1 = Math.toRadians(lat1), p2 = Math.toRadians(lat2);
        double dLat = Math.toRadians(lat2 - lat1), dLon = Math.toRadians(lon2 - lon1);
        double a = Math.sin(dLat / 2.0d) * Math.sin(dLat / 2.0d)
                + Math.cos(p1) * Math.cos(p2) * Math.sin(dLon / 2.0d) * Math.sin(dLon / 2.0d);
        return 2.0d * r * Math.asin(Math.min(1.0d, Math.sqrt(a)));
    }
}
