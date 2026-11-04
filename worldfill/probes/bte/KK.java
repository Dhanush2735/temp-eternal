import java.util.Locale;
public class KK {
    public static void main(String[] a) throws Exception {
        double lat = 17.3928, lon = 78.4808;
        double[] real = Probe.fromGeo(lat, lon);
        double[] api = new net.buildtheearth.terraplusplus.projection.impl.BTEProjection().toProjected(lat, lon);
        System.out.printf(Locale.ROOT, "King Kothi real block %.0f, %.0f ; public-API block %.0f, %.0f%n", real[0], real[1], api[0], api[1]);
        double[] ch = Probe.fromGeo(17.3616, 78.4747);
        System.out.printf(Locale.ROOT, "Charminar real block %.0f, %.0f ; distance Charminar->King Kothi in blocks %.0f%n", ch[0], ch[1], Math.hypot(real[0]-ch[0], real[1]-ch[1]));
        // /tpll-style check: Everest, Dead Sea vertical mapping from TerraDensityFunctions.scaleElevation
        for (double e : new double[]{505, 1000, 2000, 4500, 8849}) {
            int y = e <= 0 ? 0 : e <= 1000 ? (int)Math.round(e) : e >= 8849 ? 1969 : 1000 + Math.min((int)Math.round(969.0*Math.pow((e-1000.0)/7849.0, 0.65)), 969);
            System.out.printf(Locale.ROOT, "elevation %5.0f m -> %4d blocks above sea level%n", e, y);
        }
    }
}
