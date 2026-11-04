import net.buildtheearth.terraminusminus.projection.dymaxion.BTEDymaxionProjection;
import java.util.Locale;

public class Probe {
    static final double S = 7318261.522857145;
    static final BTEDymaxionProjection P = new BTEDymaxionProjection();

    // The world's real projection: scale(flip_vertical(bte_conformal_dymaxion)).
    static double[] fromGeo(double lat, double lon) throws Exception {
        double[] c = P.fromGeo(lon, lat);
        return new double[] { c[0] * S, -c[1] * S };
    }
    static double[] toGeo(double x, double z) throws Exception {
        double[] g = P.toGeo(x / S, -(z / S));
        return new double[] { g[1], g[0] }; // lat, lon
    }
    static double hav(double la1, double lo1, double la2, double lo2) {
        double R = 6371008.8, p1 = Math.toRadians(la1), p2 = Math.toRadians(la2);
        double dp = p2 - p1, dl = Math.toRadians(lo2 - lo1);
        double a = Math.sin(dp/2)*Math.sin(dp/2) + Math.cos(p1)*Math.cos(p2)*Math.sin(dl/2)*Math.sin(dl/2);
        return 2*R*Math.asin(Math.sqrt(a));
    }
    public static void main(String[] a) throws Exception {
        Object[][] places = {
            {"Hyderabad (Charminar)", 17.3616, 78.4747},
            {"Delhi (India Gate)", 28.6129, 77.2295},
            {"Mumbai", 18.9220, 72.8347},
            {"London", 51.5007, -0.1246},
            {"New York", 40.7484, -73.9857},
            {"Tokyo", 35.6586, 139.7454},
            {"Sydney", -33.8568, 151.2153},
            {"Cape Town", -33.9249, 18.4241},
            {"Moscow", 55.7539, 37.6208},
            {"Rio de Janeiro", -22.9519, -43.2105},
            {"Cairo (Giza)", 29.9792, 31.1342},
            {"Beijing", 39.9042, 116.4074},
        };
        double d = 0.0045; // about 500 m of latitude
        for (Object[] pl : places) {
            String n = (String) pl[0]; double lat = (Double) pl[1], lon = (Double) pl[2];
            double[] c = fromGeo(lat, lon);
            double[] nN = fromGeo(lat + d, lon), nS = fromGeo(lat - d, lon);
            double dl = d / Math.cos(Math.toRadians(lat));
            double[] eE = fromGeo(lat, lon + dl), eW = fromGeo(lat, lon - dl);
            double blocksNS = Math.hypot(nN[0]-nS[0], nN[1]-nS[1]);
            double metersNS = hav(lat - d, lon, lat + d, lon);
            double blocksEW = Math.hypot(eE[0]-eW[0], eE[1]-eW[1]);
            double metersEW = hav(lat, lon - dl, lat, lon + dl);
            // True north as a direction on the block grid; Minecraft north is -Z.
            double vx = nN[0]-nS[0], vz = nN[1]-nS[1];
            double ang = Math.toDegrees(Math.atan2(vx, -vz)); // 0 = Minecraft north, + = turned towards +X (east)
            double[] back = toGeo(c[0], c[1]);
            System.out.printf(Locale.ROOT, "%-22s block X %12.0f Z %12.0f | 1 km N-S = %6.0f blocks, 1 km E-W = %6.0f blocks | true north is %6.1f deg from Minecraft north | round trip %.2f m%n",
                n, c[0], c[1], 1000*blocksNS/metersNS, 1000*blocksEW/metersEW, ang, hav(lat, lon, back[0], back[1]));
        }
        // The public API's projection (terra3 ProjectionRegistry "bte"): the simplified class.
        net.buildtheearth.terraplusplus.projection.impl.BTEProjection api = new net.buildtheearth.terraplusplus.projection.impl.BTEProjection();
        System.out.println("--- the public API (ProjectionRegistry 'bte', the 'simplified version') ---");
        for (Object[] pl : places) {
            String n = (String) pl[0]; double lat = (Double) pl[1], lon = (Double) pl[2];
            double[] real = fromGeo(lat, lon);
            double[] apiXZ = api.toProjected(lat, lon);
            double[] realGeoOfApi;
            String where;
            try { realGeoOfApi = toGeo(apiXZ[0], apiXZ[1]); where = String.format(Locale.ROOT, "%.2f, %.2f (%.0f km away)", realGeoOfApi[0], realGeoOfApi[1], hav(lat, lon, realGeoOfApi[0], realGeoOfApi[1]) / 1000); }
            catch (Exception e) { where = "outside the map"; }
            System.out.printf(Locale.ROOT, "%-22s API block X %12.0f Z %12.0f vs real X %12.0f Z %12.0f -> the API's block is really at %s%n",
                n, apiXZ[0], apiXZ[1], real[0], real[1], where);
        }
    }
}
