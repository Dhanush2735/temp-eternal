import com.eternalengine.civilization.RulerRegister;

/** What the register records for a named polity: its spans, its place count, its core cell. */
public final class PolityProbe {
    private static final String[] NAMES = {
            "Kingdom of Prussia", "German Confederation", "Confederation of the Rhine",
            "North German Confederation", "Byzantine Empire", "Free City of Krakow",
            "Emirate of Sicily", "Austrian Empire", "Russian Empire",
    };
    public static void main(String[] args) {
        RulerRegister rr = RulerRegister.get();
        java.util.Map<String, String> hints = new java.util.HashMap<>();
        for (var pol : rr.polities()) { hints.put(pol.name(), pol.civHint()); }
        for (String n : NAMES) {
            String h = hints.getOrDefault(n, n);
            var e = rr.extentOf(h);
            if (e.isEmpty()) { System.out.println(n + " : NOT IN REGISTER"); continue; }
            var x = e.get();
            StringBuilder sp = new StringBuilder();
            for (int[] s : rr.spansOf(h)) { sp.append(s[0]).append('-').append(s[1]).append(' '); }
            var cells = rr.placesOf(h, 3);
            System.out.printf(java.util.Locale.ROOT,
                    "%-30s places=%-6d union %5d..%-5d spans: %s%n     core cell %s%n",
                    n, x.places(), x.start(), x.end(), sp,
                    cells.isEmpty() ? "-" : cells.get(0)[0] + "," + cells.get(0)[1]);
        }
    }
}
