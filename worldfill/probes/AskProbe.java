import com.eternalengine.civilization.WhoRuled;

/**
 * Ask the engine a handful of named questions and print what it says. (2026-10-27)
 *
 * <p>Every case below comes from {@code SpanHonestyProbe}: a polity that is recorded past its own end and
 * beats the polity that really held the place. The probe says "a polity loses"; this asks the question a
 * player would ask, which is the only one that decides whether a stale span is a real defect or bookkeeping.
 */
public final class AskProbe {
    private static final Object[][] CASES = {
            // lat, lon, year, what it should be, why
            {41.01, 28.98, 1460, "Ottoman Empire", "Constantinople fell 1453; register silent till 1466 (FILLED)"},
            {41.01, 28.98, 1450, "Byzantine Empire", "before the fall, still Byzantine"},
            {41.01, 28.98, 1470, "Ottoman Empire", "same, later"},
            {40.85, 14.27, 1350, "Kingdom of Naples", "Naples 1350 - the plain kingdom, not the Napoleonic one"},
            {40.85, 14.27, 1810, "has:Naples", "Naples 1810 - Murat; coverage must exist, label is the source's"},
            {40.85, 14.27, 1770, "has:Naples", "Naples 1770 BOURBON - my withdrawn clamp would have left a hole"},
            {40.85, 14.27, 1290, "Kingdom of Naples", "Naples 1290 Angevin"},
            {50.06, 19.94, 1833, "Free City of Krakow", "Free City existed 1815-1846; Austrian Empire wins here"},
            {50.06, 19.94, 1840, "Free City of Krakow", "same, later"},
            {38.12, 13.36, 1092, "Norman Italy", "Norman Italy is right: the Kingdom of Sicily was not founded until 1130"},
            {52.52, 13.40, 1821, "Kingdom of Prussia", "Berlin 1821 - Prussia's own capital"},
            {47.18, 47.45, 1600, "not the Golden Horde", "Sarai was sacked in 1502"},
            {13.41, 103.87, 1864, "not the Khmer Empire", "Angkor fell 1431"},
            // the two new boxes must not sprawl
            {53.55, 9.99, 1821, "not Kingdom of Prussia", "Hamburg 1821 - a free city, 250 km from Berlin"},
            {51.05, 13.74, 1821, "not Kingdom of Prussia", "Dresden 1821 - the Kingdom of Saxony"},
            {52.26, 21.01, 1840, "not Free City of Krakow", "Warsaw 1840 - Congress Poland, under Russia"},
            {49.84, 24.03, 1840, "not Free City of Krakow", "Lviv 1840 - Austrian Galicia"},
    };

    public static void main(String[] args) {
        var none = java.util.List.<WhoRuled.Cap>of();
        for (Object[] c : CASES) {
            double lat = (Double) c[0], lon = (Double) c[1];
            int year = (Integer) c[2];
            String expect = (String) c[3], why = (String) c[4];
            var a = WhoRuled.answer(none, lat, lon, year);
            String got = a.known() ? a.name() : "(nobody)";
            boolean ok;
            if (expect.startsWith("not ")) {
                ok = !expect.substring(4).equals(got);
            } else if (expect.startsWith("has:")) {
                ok = got.contains(expect.substring(4));
            } else {
                ok = expect.equals(got);
            }
            System.out.printf(java.util.Locale.ROOT, "%-6s %6.2f,%7.2f %5d  got %-28s %s%n",
                    ok ? "OK" : "WRONG", lat, lon, year, got, why);
        }
    }
}
