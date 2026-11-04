import com.eternalengine.money.MoneyFormat;
import com.eternalengine.money.MoneyPlaces;
import com.eternalengine.money.MoneyTable;
import com.eternalengine.news.BookForms;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Step 23a: the money of the whole world (the world layer of the money table) with the mod's real code and data -
 * the ruler register and the HYDE grid included - no server. Run by worldfill/probe_moneyworld.sh. Exit code 1 if a
 * check fails.
 */
public final class MoneyWorldProbe {
    private static int pass;
    private static int fail;

    public static void main(String[] args) {
        long t0 = System.nanoTime();
        MoneyTable t = MoneyTable.get();
        MoneyTable.Rulers rulers = MoneyTable.REGISTER;
        System.out.println("1. The table");
        MoneyTable.Summary s = t.summary();
        check("the table loads: " + s.monies() + " kinds of money, " + s.rows() + " rows, " + s.rates() + " fixed rates",
                s.loaded() && s.monies() >= 300 && t.problems().isEmpty(), String.valueOf(t.problems()));
        check("the table's own check (Hyderabad 1948, a grid of places over 5,000 years)", t.selfTest(rulers) == null,
                String.valueOf(t.selfTest(rulers)));

        System.out.println();
        System.out.println("2. The test places (money, and a labourer's day's pay in it)");
        List<String> bad = MoneyPlaces.wrongPlaces(t, rulers);
        for (MoneyPlaces.Expect e : MoneyPlaces.EXPECT) {
            MoneyTable.Here h = t.at(e.lat(), e.lon(), e.year(), rulers);
            String day = MoneyFormat.amount(h.money(), h.dayPay(), e.year());
            System.out.printf(Locale.ROOT, "   %-14s %5d  %-28s %s%n", e.place(), e.year(), h.money().name(), day);
        }
        check(MoneyPlaces.EXPECT.size() + " test places get their money", bad.isEmpty(), String.join("; ", bad));

        System.out.println();
        System.out.println("3. The census of settled random points");
        List<double[]> pts = BookForms.randomPoints(400, 23L);
        MoneyPlaces.Census c = MoneyPlaces.census(t, rulers, MoneyPlaces.HYDE, pts, MoneyPlaces.CHECK_YEARS);
        System.out.printf(Locale.ROOT, "   %d points x %d years: %d settled answers: %d real money, %d barter, %d placeholder;"
                        + " %d kinds of money met%n", pts.size(), MoneyPlaces.CHECK_YEARS.length, c.settled(), c.named(),
                c.barter(), c.placeholder(), c.monies());
        for (int y : MoneyPlaces.CHECK_YEARS) {
            MoneyPlaces.Census cy = MoneyPlaces.census(t, rulers, MoneyPlaces.HYDE, pts, new int[]{y});
            System.out.printf(Locale.ROOT, "   %5d: %3d settled, %3d real money, %3d barter, %d placeholder, %d kinds%n", y,
                    cy.settled(), cy.named(), cy.barter(), cy.placeholder(), cy.monies());
        }
        check("no more than 1 in 100 settled answers is a placeholder", c.settled() > 0 && c.placeholderShare() <= 0.01d,
                c.placeholder() + " at " + c.placeholderAt());
        check("the world self-test", MoneyPlaces.selfTest(t, rulers, MoneyPlaces.HYDE) == null,
                String.valueOf(MoneyPlaces.selfTest(t, rulers, MoneyPlaces.HYDE)));

        System.out.println();
        System.out.println("4. After the register's last year (" + MoneyTable.LAST_RULER_YEAR + ")");
        Object[][] late = {{"Sofia", 42.70, 23.32, 2025, "lev_1999"}, {"Sofia", 42.70, 23.32, 2026, "euro"},
                {"Lagos", 6.45, 3.39, 2026, "naira"}, {"Moscow", 55.76, 37.62, 2026, "ruble_ru"},
                {"Harare", -17.83, 31.05, 2026, "zig"}, {"Hyderabad", 17.3616, 78.4747, 2026, "indian_rupee"}};
        for (Object[] o : late) {
            MoneyTable.Here h = t.at((double) o[1], (double) o[2], (int) o[3], rulers);
            check(o[0] + " " + o[3] + ": " + h.money().name() + " (" + MoneyFormat.amount(h.money(), h.dayPay(), (int) o[3])
                    + " a day)", h.money().id().equals(o[4]), h.money().id() + ", not " + o[4]);
        }

        System.out.println();
        System.out.println("5. Every row can pay a day's work in its own coins");
        List<String> zero = new ArrayList<>();
        for (MoneyTable.Row r : t.rows()) {
            for (int y : new int[]{Math.max(r.from(), -3000), Math.min(r.to(), 2026)}) {
                if (y < r.from() || y > r.to()) {
                    continue;
                }
                MoneyTable.Money m = r.money();
                long day = m.dayPay(y);
                String text = MoneyFormat.amount(m, day, y);
                if (day <= 0 || text.isBlank() || text.startsWith("0 ") || text.contains("no goods")) {
                    zero.add(r.id() + " " + y + ": " + text);
                }
            }
        }
        check("all " + t.rows().size() + " rows give a day's pay in words in their first and last year", zero.isEmpty(),
                zero.size() + ": " + String.join("; ", zero.subList(0, Math.min(8, zero.size()))));

        System.out.println();
        System.out.println("6. Fixed rates and redenominations");
        int rates = 0;
        List<String> trips = new ArrayList<>();
        List<String> jumps = new ArrayList<>();
        for (String a : t.monies().keySet()) {
            for (String b : t.monies().keySet()) {
                if (a.compareTo(b) >= 0) {
                    continue;
                }
                for (int y : new int[]{-3000, 1, 1500, 1800, 1900, 1950, 1975, 2000, 2026}) {
                    long[] r = t.rate(a, b, y);
                    if (r == null) {
                        continue;
                    }
                    rates++;
                    MoneyTable.Money ma = t.money(a);
                    MoneyTable.Money mb = t.money(b);
                    long big = Math.max(r[0], 1000L) * 1000L;
                    long back = t.convert(mb, t.convert(ma, big, mb, y), ma, y);
                    if (Math.abs(back - big) > big / 20) {
                        trips.add(a + "/" + b + " " + y);
                    }
                }
            }
        }
        check(rates + " fixed rates (pairs and years) convert there and back within 5 in 100", trips.isEmpty(),
                String.join(", ", trips));
        // Old and new money of one place should pay about the same day's work across the change (the official rate).
        Object[][] changes = {{"Istanbul", 41.01, 28.98, 2005}, {"Sao Paulo", -23.55, -46.63, 1994},
                {"Moscow", 55.76, 37.62, 1998}, {"Mexico City", 19.43, -99.13, 1993}, {"Accra", 5.60, -0.19, 2007},
                {"Warsaw", 52.23, 21.01, 1995}, {"Bucharest", 44.43, 26.10, 2005}, {"Sofia", 42.70, 23.32, 1999},
                {"Sofia", 42.70, 23.32, 2026}, {"Buenos Aires", -34.60, -58.38, 1992}, {"Lima", -12.05, -77.04, 1991},
                {"Kabul", 34.53, 69.17, 2003}, {"Karachi", 24.86, 67.01, 1961}, {"Sydney", -33.87, 151.21, 1966},
                {"Johannesburg", -26.20, 28.05, 1961}, {"Tel Aviv", 32.09, 34.78, 1986}, {"Maputo", -25.97, 32.57, 2006},
                {"Zagreb", 45.81, 15.98, 2023}, {"Bangkok", 13.75, 100.50, 1897}, {"Moscow", 55.76, 37.62, 1961},
                {"Helsinki", 60.17, 24.94, 1963}, {"Rio de Janeiro", -22.91, -43.17, 1942}, {"Freetown", 8.48, -13.23, 2022},
                {"Tallinn", 59.44, 24.75, 2011}, {"Riga", 56.95, 24.11, 2014}, {"Vilnius", 54.69, 25.28, 2015},
                {"Bratislava", 48.15, 17.11, 2009}, {"Lisbon", 38.72, -9.14, 2002}, {"Athens", 37.98, 23.73, 2002},
                {"Quito", -0.18, -78.47, 2000}, {"San Salvador", 13.69, -89.22, 2001}, {"Paris", 48.857, 2.352, 2002}};
        int compared = 0;
        for (Object[] ch : changes) {
            double lat = (double) ch[1];
            double lon = (double) ch[2];
            int y = (int) ch[3];
            MoneyTable.Here before = t.at(lat, lon, y - 1, rulers);
            MoneyTable.Here after = t.at(lat, lon, y, rulers);
            if (before.money().id().equals(after.money().id())) {
                jumps.add(ch[0] + " " + y + ": no change of money (" + after.money().id() + ")");
                continue;
            }
            if (!t.fixed(before.money().id(), after.money().id(), y)) {
                jumps.add(ch[0] + " " + y + ": no fixed rate " + before.money().id() + " -> " + after.money().id());
                continue;
            }
            compared++;
            // The old money's pay in the year of the change itself (its row held at its last anchor), so that a
            // hyperinflation inside the last year does not count.
            long oldPay = before.row().dayPay(y);
            long converted = t.convert(before.money(), oldPay, after.money(), y);
            double ratio = converted / (double) after.dayPay();
            String line = String.format(Locale.ROOT, "%-13s %d: %s a day = %s; then %s (x%.2f)", ch[0], y,
                    MoneyFormat.amount(before.money(), oldPay, y) + " (" + before.money().name() + ")",
                    MoneyFormat.amount(after.money(), converted, y), MoneyFormat.amount(after.money(), after.dayPay(), y)
                            + " (" + after.money().name() + ")", ratio);
            System.out.println("   " + line);
            if (ratio < 0.4d || ratio > 2.5d) {
                jumps.add(line);
            }
        }
        check(compared + " changes of money at their places keep a day's pay within 2.5 times across the official rate",
                jumps.isEmpty() && compared == changes.length, String.join("; ", jumps));

        long ms = (System.nanoTime() - t0) / 1_000_000L;
        System.out.println();
        System.out.println("RESULT: " + pass + " passed, " + fail + " failed (" + ms + " ms)");
        System.exit(fail == 0 ? 0 : 1);
    }

    private static void check(String what, boolean ok, String why) {
        if (ok) {
            pass++;
            System.out.println("  PASS " + what);
        } else {
            fail++;
            System.out.println("  FAIL " + what + " -- " + why);
        }
    }
}
