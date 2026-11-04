import com.eternalengine.civilization.WhoRuled;

/** What the engine answers year by year at three places that the span probe says are wrong. */
public final class TimelineProbe {
    private static final Object[][] PLACES = {
            {"Istanbul", 41.01, 28.98, 1440, 1475, 5},
            {"Berlin",   52.52, 13.40, 1800, 1875, 5},
            {"Krakow",   50.06, 19.94, 1815, 1850, 3},
            {"Palermo",  38.12, 13.36, 1085, 1135, 5},
    };
    public static void main(String[] args) {
        var none = java.util.List.<WhoRuled.Cap>of();
        for (Object[] p : PLACES) {
            System.out.println("=== " + p[0] + "  (" + p[1] + ", " + p[2] + ")");
            int from = (Integer) p[3], to = (Integer) p[4], step = (Integer) p[5];
            String prev = null;
            StringBuilder line = new StringBuilder();
            for (int y = from; y <= to; y += step) {
                var a = WhoRuled.answer(none, (Double) p[1], (Double) p[2], y);
                String got = a.known() ? a.name() : "(nobody)";
                if (prev == null || !got.equals(prev)) {
                    if (line.length() > 0) { System.out.println("  " + line); }
                    line = new StringBuilder(String.format(java.util.Locale.ROOT, "%d- %-30s", y, got));
                    prev = got;
                } else {
                    line.append(".");
                }
            }
            if (line.length() > 0) { System.out.println("  " + line); }
        }
    }
}
