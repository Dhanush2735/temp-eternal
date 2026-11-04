import com.eternalengine.money.MarketService;
import com.eternalengine.money.MoneyFormat;
import com.eternalengine.money.MoneyTable;
import com.eternalengine.money.ProductAtlas;
import com.eternalengine.money.ShopService;
import com.eternalengine.news.BookForms;
import com.eternalengine.news.NewsEras;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/**
 * Step 22: the forms of the history book (BookForms) with the mod's real code and data (the product atlas, the
 * ways-of-life survey, the money table), no server. Run by worldfill/probe_bookforms.sh. Exit code 1 if a check fails.
 */
public final class BookFormsProbe {
    private static int pass;
    private static int fail;

    public static void main(String[] args) {
        System.out.println("1. The forms");
        Set<String> ids = new HashSet<>();
        Set<String> items = new HashSet<>();
        for (BookForms.Form f : BookForms.Form.values()) {
            ids.add(f.id);
            items.add(f.itemId());
        }
        check("13 forms, each with its own id and item (" + String.join(", ", items) + ")",
                BookForms.Form.values().length == 13 && ids.size() == 13 && items.size() == 13
                        && BookForms.Form.NOTEBOOK.itemId().equals("history_book"), "");
        int aids = 0;
        for (BookForms.Form f : BookForms.Form.values()) {
            aids += f.writing ? 0 : 1;
        }
        check("3 of them are memory aids for places where nobody writes (knotted cords, message stick, tally stick)",
                aids == 3, aids + " memory aids");
        for (String w : new String[]{"knotted_cords", "atlas"}) {
            ProductAtlas.Product p = ProductAtlas.get().product(w);
            if (w.equals("atlas")) {
                continue;
            }
            check("the knotted cords are a code rule, not an atlas product", p == null, "");
        }
        for (String w : new String[]{"bark_paper", "bamboo_slips", "wax_tablets", "clay_tablets", "papyrus", "parchment",
                "palm_leaf", "birch_bark", "paper"}) {
            check("the atlas has the writing material " + w, ProductAtlas.get().product(w) != null, "");
        }
        long t0 = System.nanoTime();
        String self = BookForms.selfTest();
        check("the rules on their own (BookForms.selfTest, " + ms(t0) + ")", self == null, self);

        System.out.println("\n2. The test places (best form first; merchant; pedlar; price of the best in the money of the place)");
        List<String> wrong = new ArrayList<>();
        for (BookForms.Expect e : BookForms.EXPECT) {
            List<BookForms.Form> here = BookForms.here(e.lat(), e.lon(), e.year());
            List<BookForms.Form> merchant = BookForms.soldBy(MarketService.MERCHANT, e.lat(), e.lon(), e.year());
            List<BookForms.Form> pedlar = BookForms.soldBy(MarketService.PEDLAR, e.lat(), e.lon(), e.year());
            MoneyTable.Here money = MoneyTable.get().at(e.lat(), e.lon(), e.year());
            long price = ShopService.bookPrice(here.get(0), money);
            boolean ok = here.get(0) == e.form();
            if (!ok) {
                wrong.add(e.place() + " " + ProductAtlas.yearText(e.year()));
            }
            System.out.printf(Locale.ROOT, "   %s %-30s %-9s %-16s | here: %s | merchant: %s | pedlar: %s | %s%n", ok ? "ok " : "BAD",
                    e.place(), ProductAtlas.yearText(e.year()), here.get(0).title, names(here), names(merchant),
                    names(pedlar), MoneyFormat.amount(money.money(), price, e.year()));
        }
        check(BookForms.EXPECT.size() + " test places get their expected form", wrong.isEmpty(), String.join(", ", wrong));

        System.out.println("\n3. Every place and year");
        List<double[]> pts = BookForms.randomPoints(400, 22L);
        t0 = System.nanoTime();
        int[] n = BookForms.census(pts);
        long nanos = System.nanoTime() - t0;
        int total = 0;
        StringBuilder sb = new StringBuilder();
        for (BookForms.Form f : BookForms.Form.values()) {
            total += n[f.ordinal()];
            sb.append(String.format(Locale.ROOT, "%n      %-15s %5d", f.title, n[f.ordinal()]));
        }
        int calls = pts.size() * BookForms.CHECK_YEARS.length;
        System.out.println("   best form over 400 random points x " + BookForms.CHECK_YEARS.length + " years:" + sb);
        check("all " + calls + " random place-years have a form", total == calls, total + " of " + calls);
        double each = nanos / 1e6 / calls;
        check(String.format(Locale.ROOT, "fast enough for a trade screen: %.3f ms a place-year", each), each < 2.0d, "");
        for (int y : BookForms.CHECK_YEARS) {
            int w = 0;
            for (double[] p : pts) {
                w += BookForms.best(p[0], p[1], y).writing ? 1 : 0;
            }
            System.out.printf(Locale.ROOT, "   %-9s writing at %3d of 400 points%n", ProductAtlas.yearText(y), w);
        }
        int w3000 = 0;
        int w1948 = 0;
        for (double[] p : pts) {
            w3000 += BookForms.best(p[0], p[1], -3000).writing ? 1 : 0;
            w1948 += BookForms.best(p[0], p[1], 1948).writing ? 1 : 0;
        }
        check("writing spreads: fewer places write in 3000 BCE (" + w3000 + ") than in 1948 (" + w1948 + ")",
                w3000 < w1948, "");

        System.out.println("\n4. Who sells what");
        sells("merchant", MarketService.MERCHANT, 41.8925, 12.4853, 100, "parchment book, papyrus roll, wax tablets");
        sells("trader", MarketService.TRADER, 41.8925, 12.4853, 100, "parchment book, papyrus roll, wax tablets");
        sells("pedlar", MarketService.PEDLAR, 41.8925, 12.4853, 100, "wax tablets");
        sells("paper seller", NewsEras.PAPER_SELLER, 17.3616, 78.4747, 1948, "notebook");
        sells("newsletter writer", NewsEras.NEWS_WRITER, 28.6562, 77.2410, 1650, "notebook");
        sells("merchant", MarketService.MERCHANT, 15.3350, 76.4600, 1520, "palm-leaf book, notebook");
        sells("merchant", MarketService.MERCHANT, 30.9625, 46.1031, -2500, "clay tablets");
        sells("merchant", MarketService.MERCHANT, -13.5320, -71.9675, 1500, "knotted cords");
        sells("merchant", MarketService.MERCHANT, 38.6550, -90.0620, 1100, "tally stick");
        sells("farmer", "farmer", 17.3616, 78.4747, 1948, "");
        sells("money-changer", MarketService.MONEY_CHANGER, 17.3616, 78.4747, 1948, "");
        sells("merchant", MarketService.MERCHANT, 55.7520, 37.6175, 1400, "parchment book, birch-bark book");
        sells("merchant", MarketService.MERCHANT, 59.9139, 10.7522, 1200, "parchment book, wax tablets, rune sticks");
        sells("merchant", MarketService.MERCHANT, 51.5074, -0.1278, 1300, "parchment book, wax tablets");
        sells("merchant", MarketService.MERCHANT, -8.9600, 39.5100, 1350, "notebook, parchment book");
        sells("merchant", MarketService.MERCHANT, 0.3136, 32.5811, 1700, "tally stick");

        System.out.println("\n5. Prices (days of pay, in the money of the place)");
        price("a notebook in Hyderabad 1948", 17.3616, 78.4747, 1948, BookForms.Form.NOTEBOOK);
        price("a notebook in London 1450", 51.5074, -0.1278, 1450, BookForms.Form.NOTEBOOK);
        price("a notebook in London 1850", 51.5074, -0.1278, 1850, BookForms.Form.NOTEBOOK);
        price("a parchment book in Rome 100", 41.8925, 12.4853, 100, BookForms.Form.PARCHMENT);
        price("a papyrus roll in Athens 430 BCE", 37.9715, 23.7257, -430, BookForms.Form.PAPYRUS);
        price("clay tablets in Ur 2500 BCE", 30.9625, 46.1031, -2500, BookForms.Form.CLAY_TABLETS);
        price("knotted cords in Cusco 1500", -13.5320, -71.9675, 1500, BookForms.Form.KNOTTED_CORDS);
        price("a tally stick in Cahokia 1100", 38.6550, -90.0620, 1100, BookForms.Form.TALLY_STICK);
        MoneyTable.Here hy = MoneyTable.get().at(17.3616, 78.4747, 1948);
        check("a notebook in Hyderabad 1948 costs less than a day's pay and more than nothing ("
                        + MoneyFormat.amount(hy.money(), ShopService.bookPrice(BookForms.Form.NOTEBOOK, hy), 1948) + ")",
                ShopService.bookPrice(BookForms.Form.NOTEBOOK, hy) > 0
                        && ShopService.bookPrice(BookForms.Form.NOTEBOOK, hy) < hy.dayPay(), "");

        System.out.println("\n6. Edges");
        check("no place known: a tally stick", BookForms.best(Double.NaN, Double.NaN, 1948) == BookForms.Form.TALLY_STICK, "");
        check("the North Pole and the South Pole have a form (" + BookForms.best(90.0, 0.0, 1948).title + ", "
                + BookForms.best(-90.0, 0.0, 1948).title + ")", BookForms.best(90.0, 0.0, 1948) != null
                && BookForms.best(-90.0, 0.0, 1948) != null, "");
        check("the date line has a form (" + BookForms.best(0.0, 180.0, 1000).title + ", "
                + BookForms.best(0.0, -180.0, 1000).title + ")", BookForms.best(0.0, 180.0, 1000) != null
                && BookForms.best(0.0, -180.0, 1000) != null, "");
        check("Iquitos, in the Amazon below the Andes, is not in the khipu outline", !inAndes(-3.75, -73.25), "");
        check("Caral, Lima, Quito, La Paz, Cusco and Potosi are in it", inAndes(-10.89, -77.52) && inAndes(-12.05, -77.04)
                && inAndes(-0.18, -78.47) && inAndes(-16.5, -68.15) && inAndes(-13.53, -71.97) && inAndes(-19.58, -65.75), "");
        check("Bombay 1948 (the sandbox test place): a notebook", BookForms.best(18.94, 72.83, 1948) == BookForms.Form.NOTEBOOK,
                BookForms.best(18.94, 72.83, 1948).title);

        System.out.println("\n7. More places (information)");
        Object[][] more = {{"Benin City", 6.34, 5.62, 1500}, {"Kumasi", 6.69, -1.62, 1750}, {"Kano", 12.0, 8.52, 1500},
                {"Old Calabar", 4.95, 8.32, 1785}, {"Mbanza Kongo", -6.27, 14.24, 1550}, {"Mombasa", -4.04, 39.67, 1500},
                {"Aksum", 14.13, 38.72, 400}, {"Lalibela", 12.03, 39.04, 1200}, {"Ife", 7.48, 4.56, 1300},
                {"Zanzibar", -6.16, 39.19, 1700}, {"Antananarivo", -18.91, 47.53, 1800}, {"Kilwa", -8.96, 39.51, 1300}};
        for (Object[] m : more) {
            double la = (Double) m[1];
            double lo = (Double) m[2];
            int y = (Integer) m[3];
            System.out.printf(Locale.ROOT, "   %-14s %-9s here: %s | merchant: %s%n", m[0], ProductAtlas.yearText(y),
                    names(BookForms.here(la, lo, y)), names(BookForms.soldBy(MarketService.MERCHANT, la, lo, y)));
        }

        System.out.println("\n" + pass + " passed, " + fail + " failed");
        System.exit(fail == 0 ? 0 : 1);
    }

    private static boolean inAndes(double lat, double lon) {
        // the same outline as BookForms (package-private there): knotted cords before writing comes
        return BookForms.memoryAid(lat, lon, 1000) == BookForms.Form.KNOTTED_CORDS;
    }

    private static void sells(String who, String role, double lat, double lon, int year, String want) {
        String got = names(BookForms.soldBy(role, lat, lon, year));
        check(String.format(Locale.ROOT, "a %s at %.2f, %.2f in %s sells: %s", who, lat, lon, ProductAtlas.yearText(year),
                got.isEmpty() ? "no book" : got), got.equals(want), "expected " + (want.isEmpty() ? "no book" : want));
    }

    private static void price(String what, double lat, double lon, int year, BookForms.Form f) {
        MoneyTable.Here here = MoneyTable.get().at(lat, lon, year);
        long p = ShopService.bookPrice(f, here);
        System.out.printf(Locale.ROOT, "   %-36s %4.2f days -> %s (a day's pay: %s)%n", what, BookForms.days(f, year),
                MoneyFormat.amount(here.money(), p, year), MoneyFormat.amount(here.money(), here.dayPay(), year));
    }

    private static String names(List<BookForms.Form> forms) {
        StringBuilder sb = new StringBuilder();
        for (BookForms.Form f : forms) {
            sb.append(sb.length() == 0 ? "" : ", ").append(f.title.toLowerCase(Locale.ROOT));
        }
        return sb.toString();
    }

    private static String ms(long t0) {
        return String.format(Locale.ROOT, "%.0f ms", (System.nanoTime() - t0) / 1e6);
    }

    private static void check(String what, boolean ok, String detail) {
        if (ok) {
            pass++;
            System.out.println("   PASS " + what);
        } else {
            fail++;
            System.out.println("   FAIL " + what + (detail == null || detail.isEmpty() ? "" : " -- " + detail));
        }
    }
}
