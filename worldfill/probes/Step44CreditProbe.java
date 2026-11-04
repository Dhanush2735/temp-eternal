import com.eternalengine.money.Credit;
import java.util.ArrayList;
import java.util.List;
import com.eternalengine.money.Credit.Loan;
import com.eternalengine.money.Credit.Terms;

/** Step 44 part 8 (E19): banking and credit. Checks are printed, so a wrong number is visible. */
public final class Step44CreditProbe {

    private static int checks = 0;
    private static int failed = 0;

    private static void ok(boolean cond, String what) {
        checks++;
        if (!cond) {
            failed++;
            System.out.println("  FAIL  " + what);
        }
    }

    private static void eq(Object got, Object want, String what) {
        checks++;
        if (got == null ? want != null : !got.equals(want)) {
            failed++;
            System.out.println("  FAIL  " + what + ": got " + got + ", want " + want);
        }
    }

    /** A point for each row's own box and century, plus the places a player would ask about. */
    private static final Object[][] PLACES = {
        {"Ur, silver or grain", 31.0, 46.0, -1800},
        {"Ur, Sumer (grain)", 31.0, 46.0, -1950},
        {"Babylon, later", 32.5, 44.5, -500},
        {"Thebes, Egypt", 25.7, 32.6, -1200},
        {"Athens", 37.98, 23.73, -350},
        {"Rome", 41.88, 12.50, 100},
        {"Rome, at the Lex Poetelia", 41.88, 12.50, -326},
        {"Constantinople", 41.0, 28.9, 900},
        {"Chang'an, Tang", 34.3, 108.9, 800},
        {"Hangzhou, Song", 30.3, 120.2, 1100},
        {"Bursa, Ottoman", 40.2, 29.1, 1700},
        {"Cairo", 30.04, 31.24, 1400},
        {"Agra, Mughal", 27.18, 78.02, 1650},
        {"Agra, as the empire fails", 27.18, 78.02, 1780},
        {"Pataliputra, Maurya", 25.6, 85.1, -250},
        {"Florence, Datini", 43.77, 11.26, 1400},
        {"Genoa", 44.41, 8.93, 1200},
        {"Venice, early", 45.44, 12.32, 1440},
        {"Venice, late", 45.44, 12.32, 1490},
        {"London, Jews", 51.51, -0.13, 1200},
        {"London, Tudor", 51.51, -0.13, 1600},
        {"London, Bank", 51.51, -0.13, 1750},
        {"Amsterdam", 52.37, 4.90, 1580},
        {"Philadelphia", 39.95, -75.17, 1830},
        {"Philadelphia, 1940s", 39.95, -75.17, 1940},
        {"Abeokuta, Yoruba", 7.15, 3.35, 1800},
        {"Cusco, Inca", -13.53, -71.97, 1500},
        {"Hyderabad, 1600", 17.39, 78.49, 1600},
        {"Hyderabad, 1900", 17.39, 78.49, 1900},
    };

    public static void main(String[] args) {
        Credit credit = Credit.get();
        System.out.println("credit: " + credit.summary());
        ok(credit.loaded(), "the credit pack loads");
        eq(credit.problem(), null, "no problem reading the credit pack");
        ok(credit.count() >= 20, "at least twenty rows (have " + credit.count() + ")");

        // ---------------------------------------------------------------- the register itself
        int recorded = 0, measured = 0, estimated = 0, noRate = 0;
        for (Loan l : credit.rows()) {
            switch (l.mark()) {
                case "recorded" -> recorded++;
                case "measured" -> measured++;
                default -> estimated++;
            }
            if (l.noRate()) {
                noRate++;
                ok(l.instead() != null || l.note() != null,
                        l.id() + ": a row with no rate must say what was done instead");
            } else {
                ok(l.high() >= l.low(), l.id() + ": high is below low");
                ok(l.low() > 0 && l.high() <= 60, l.id() + ": a rate outside 0-60 per cent");
            }
            ok(credit.kindWord(l.kind()) != null, l.id() + ": no words for its kind");
            ok(credit.lenderWord(l.lender()) != null, l.id() + ": no words for its lender");
        }
        System.out.println("  recorded " + recorded + ", measured " + measured
                + ", estimated " + estimated + "; " + noRate + " recording no rate at all");
        ok(measured > 0 && recorded > 0, "the pack has both measured and recorded rows");
        ok(noRate > 0, "some rows record that there was no price for credit");

        // ---------------------------------------------------------------- what it says
        System.out.println();
        System.out.println("what borrowing costs:");
        for (Object[] p : PLACES) {
            String nm = (String) p[0];
            Terms t = credit.at((Double) p[1], (Double) p[2], (Integer) p[3]);
            System.out.printf("  %-30s %s%n", nm, Credit.sentence(t));
            if (t.silent()) {
                continue;
            }
            Loan best = t.best();
            // the row quoted must really cover this place and year
            ok(best != null, nm + ": a best row");
            // a row marked measured is never quoted below one marked recorded
            boolean sawWorse = false;
            for (Loan l : t.loans()) {
                if (sawWorse) {
                    ok(!"measured".equals(l.mark()),
                            nm + ": a measured row is quoted after a worse one");
                }
                if (!"measured".equals(l.mark())) {
                    sawWorse = true;
                }
            }
        }

        // ---------------------------------------------------------------- the absences are real
        System.out.println();
        System.out.println("where there is no price for credit:");
        for (Object[] p : new Object[][]{{"Cusco, Inca", -13.53, -71.97, 1500},
                {"Abeokuta, Yoruba", 7.15, 3.35, 1800},
                {"Pataliputra, Maurya", 25.6, 85.1, -250},
                {"Timbuktu, Mali", 16.77, -3.01, 1500}}) {
            Terms t = credit.at((Double) p[1], (Double) p[2], (Integer) p[3]);
            Loan best = t.best();
            if (!t.silent() && best.noRate()) {
                System.out.printf("  %-36s %s%n", p[0],
                        Credit.sentence(t).substring(0, Math.min(150, Credit.sentence(t).length())));
                ok(best.instead() != null, p[0] + ": says what was done instead");
            } else {
                System.out.printf("  %-36s (has a rate: %s)%n", p[0],
                        best == null ? "silent" : best.rate());
            }
        }
        // the Inca row must be reachable, and must carry no rate
        Terms inca = credit.at(-13.53, -71.97, 1500);
        ok(!inca.silent(), "Cusco is reached by the register");
        ok(inca.best() != null && inca.best().noRate(),
                "Cusco in 1500 has no rate, because the Inca had no money");
        ok(inca.best() != null && "none".equals(inca.best().lender()),
                "Cusco in 1500 has no lender");

        // ---------------------------------------------------------------- a ban is not an absence
        System.out.println();
        System.out.println("where interest is forbidden but credit is not:");
        for (Loan l : credit.rows()) {
            if (!l.forbidden()) {
                continue;
            }
            System.out.printf("  %-22s %-9s %s%n", l.id(), l.mark(),
                    l.instead() == null ? "(nothing recorded)" : l.instead().substring(0,
                            Math.min(110, l.instead().length())));
            ok(l.instead() != null, l.id() + ": forbids interest but says nothing of what replaced it");
        }

        // ---------------------------------------------------------------- coverage
        System.out.println();
        int silent = 0, withRate = 0, without = 0, forbidden = 0, capped = 0;
        for (double lat = -50.0; lat <= 66.0; lat += 4.0) {
            for (double lon = -178.0; lon <= 178.0; lon += 6.0) {
                for (int year = -2000; year <= 1900; year += 200) {
                    Terms t = credit.at(lat, lon, year);
                    if (t.silent()) {
                        silent++;
                        continue;
                    }
                    if (t.best().noRate()) {
                        without++;
                    } else {
                        withRate++;
                    }
                    if (t.best().forbidden()) {
                        forbidden++;
                    } else if (t.best().capped()) {
                        capped++;
                    }
                }
            }
        }
        int total = silent + withRate + without;
        System.out.printf("  %d place-years: %d with a rate, %d with a recorded absence, "
                + "%d outside the register%n", total, withRate, without, silent);
        System.out.printf("  of those with terms: %d where interest is forbidden, %d where it is capped%n",
                forbidden, capped);
        ok(withRate > 0, "somewhere has a rate");
        ok(without > 0, "somewhere records that it has no rate");
        ok(silent < total, "the register reaches some of the world");

        // ---------------------------------------------------------------- over real cities
        //
        // The raw grid above is mostly ocean, so it says little. Sample real cities across the
        // inhabited world and every era, and see how often the register has something to say.
        String[] cities = {"Ur", "Memphis", "Mohenjo-daro", "Anyang", "Athens", "Carthage",
                "Rome", "Pataliputra", "Chang'an", "Constantinople", "Baghdad", "Cairo",
                "Córdoba", "Timbuktu", "Kyoto", "Angkor", "Tenochtitlan", "Cusco",
                "Hangzhou", "Novgorod", "Venice", "Bruges", "Paris", "Bursa", "Agra",
                "Beijing", "Istanbul", "Lisbon", "Amsterdam", "London", "Isfahan",
                "Delhi", "Edo", "Philadelphia", "Cape Town", "Sydney", "Abeokuta",
                "Zanzibar", "Samarkand", "Vijayanagara", "Great Zimbabwe", "Cahokia"};
        double[][] where = {{31, 46}, {29.85, 31.26}, {27.32, 68.14}, {36.06, 114.35},
                {37.98, 23.73}, {37.0, 10.32}, {41.88, 12.5}, {25.6, 85.1}, {34.3, 108.9},
                {41.0, 28.9}, {33.3, 44.4}, {30.04, 31.24}, {37.89, -4.78}, {16.77, -3.01},
                {35.0, 135.77}, {13.41, 103.86}, {19.43, -99.13}, {-13.53, -71.97},
                {30.3, 120.2}, {58.52, 31.28}, {45.44, 12.32}, {51.21, 3.22}, {48.86, 2.35},
                {40.2, 29.1}, {27.18, 78.02}, {39.9, 116.4}, {41.01, 28.98}, {38.72, -9.14},
                {52.37, 4.9}, {51.51, -0.13}, {32.65, 51.67}, {28.61, 77.21}, {35.69, 139.69},
                {39.95, -75.17}, {-33.92, 18.42}, {-33.87, 151.21}, {7.15, 3.35},
                {-6.16, 39.19}, {39.65, 66.96}, {15.33, 76.46}, {-20.27, 30.93}, {38.65, -90.11}};
        System.out.println();
        System.out.println("coverage over 42 cities:");
        for (int era = 0; era < 6; era++) {
            int[] yrs = {-1500, -200, 500, 1100, 1600, 1850};
            String[] names = {"1500 BC", "200 BC", "500 AD", "1100 AD", "1600 AD", "1850 AD"};
            int hit = 0;
            List<String> miss = new ArrayList<>();
            for (int i = 0; i < cities.length; i++) {
                Terms t = credit.at(where[i][0], where[i][1], yrs[era]);
                if (t.silent()) {
                    miss.add(cities[i]);
                } else {
                    hit++;
                }
            }
            System.out.printf("  %-8s %2d of %d cities%n", names[era], hit, cities.length);
            if (!miss.isEmpty() && miss.size() <= 12) {
                System.out.println("           no row: " + String.join(", ", miss));
            }
        }

        System.out.println();
        System.out.println("credit: " + checks + " checks, " + failed + " failed");
        if (failed > 0) {
            System.exit(1);
        }
    }
}
