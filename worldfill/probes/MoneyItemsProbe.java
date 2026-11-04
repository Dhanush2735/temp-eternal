import com.eternalengine.money.Denominations;
import com.eternalengine.money.MoneyFormat;
import com.eternalengine.money.MoneyTable;
import com.eternalengine.money.PurseService;
import com.eternalengine.money.ShopService;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;

/**
 * Step 23b: money you can hold, with the mod's real code and data - no server. For places all over the world and
 * all eras: the pieces people held (value, look, name), the start money (a day's pay) as pieces, and paying a
 * sixteenth of a day (a newspaper) from them with change. Then every money of the table in its first, middle and last
 * year: pieces exist, a day's pay is a handful of pieces, prices are payable and change comes back exactly. Run by
 * worldfill/probe_moneyitems.sh. Exit code 1 if a check fails.
 */
public final class MoneyItemsProbe {
    private static int pass;
    private static int fail;

    record Place(String name, double lat, double lon, int year, String money) {
    }

    static final List<Place> TOUR = List.of(
            new Place("Ur", 30.96, 46.10, -2000, "silver_weighed"),
            new Place("Thebes", 25.70, 32.64, -1300, "egypt_deben"),
            new Place("Persepolis", 29.93, 52.89, -500, "siglos"),
            new Place("Anyang", 36.10, 114.35, -1200, "cowrie_cn"),
            new Place("Rome", 41.89, 12.49, 100, ""),
            new Place("Constantinople", 41.01, 28.98, 1000, "solidus"),
            new Place("Kaifeng", 34.80, 114.31, 1100, "china_cash"),
            new Place("Iceland", 64.14, -21.94, 1100, "vadmal"),
            new Place("Oslo", 59.91, 10.75, 1200, ""),
            new Place("Venice", 45.44, 12.33, 1400, ""),
            new Place("Hanoi", 21.03, 105.85, 1500, "van_vn"),
            new Place("Tenochtitlan", 19.43, -99.13, 1500, "cacao"),
            new Place("Mbanza Kongo", -6.27, 14.25, 1600, "nzimbu"),
            new Place("Gondar", 12.61, 37.47, 1700, "amole"),
            new Place("Edo", 35.68, 139.76, 1700, "mon"),
            new Place("Amsterdam", 52.37, 4.90, 1700, ""),
            new Place("York Factory", 57.00, -92.30, 1750, "made_beaver"),
            new Place("Rio", -22.91, -43.17, 1750, ""),
            new Place("Batavia", -6.13, 106.82, 1750, ""),
            new Place("Calabar", 4.95, 8.32, 1800, "manilla"),
            new Place("Bangkok", 13.75, 100.50, 1800, "baht_old"),
            new Place("Seoul", 37.57, 126.98, 1800, "mun_kr"),
            new Place("London", 51.51, -0.13, 1800, "pound_lsd"),
            new Place("Lhasa", 29.65, 91.13, 1900, ""),
            new Place("Addis Ababa", 9.03, 38.74, 1900, ""),
            new Place("Hyderabad", 17.36, 78.47, 1948, "osmania_sicca"),
            new Place("Karachi", 24.86, 67.01, 1955, ""),
            new Place("Moscow", 55.76, 37.62, 1970, ""),
            new Place("Quito", -0.22, -78.51, 2010, ""),
            new Place("Varna", 43.21, 27.91, 2026, "euro"),
            new Place("Lagos", 6.60, 3.35, 2026, "naira"),
            new Place("Hyderabad", 17.36, 78.47, 2026, ""));

    public static void main(String[] args) {
        long t0 = System.nanoTime();
        MoneyTable t = MoneyTable.get();
        System.out.println("1. The pieces' own check and the census");
        String self = Denominations.selfTest(t);
        check("the pieces' own check (Hyderabad 1948, London 1800, Lagos 2026, Rome 100, own looks, paying with change)",
                self == null, String.valueOf(self));
        Denominations.Census c = Denominations.census(t);
        System.out.printf(Locale.ROOT, "   %d monies with coins, %d with pieces; %d pieces in first, middle and last years;"
                + " at most %d in one (%s); %d looks%n", c.monies(), c.withPieces(), c.pieces(), c.most(), c.mostAt(), c.looks());
        check("every money with coins has pieces in its first, middle and last year", c.withPieces() == c.monies(),
                c.missing());
        check("all 16 looks are used", c.looks() == Denominations.Form.values().length, c.looks() + " looks");
        check("no money has more than 30 pieces in a year", c.most() <= 30, c.most() + " at " + c.mostAt());

        System.out.println();
        System.out.println("2. A tour: the pieces, a day's pay as pieces, a newspaper (a sixteenth of a day) paid from them");
        int tourBad = 0;
        for (Place p : TOUR) {
            MoneyTable.Here h = t.at(p.lat(), p.lon(), p.year());
            MoneyTable.Money m = h.money();
            int y = p.year();
            List<Denominations.Piece> pieces = Denominations.of(m, y);
            StringBuilder sb = new StringBuilder();
            for (Denominations.Piece x : pieces) {
                sb.append(sb.length() == 0 ? "" : ", ").append(x.label()).append(" ").append(short_(x.form()));
            }
            long day = PurseService.startAmount(h); // a day's pay, rounded to the smallest piece
            List<long[]> start = Denominations.split(pieces, day);
            long price = ShopService.nice(Math.max(1L, day / 16), m, y);
            Map<Long, Long> held = new TreeMap<>();
            for (long[] vn : start) {
                held.merge(vn[0], vn[1], Long::sum);
            }
            Denominations.Plan plan = Denominations.plan(held, price, pieces);
            String payWords = plan == null ? "cannot pay"
                    : "pays " + words(m, y, plan.taken()) + (plan.change() > 0 ? ", change " + MoneyFormat.amount(m,
                    plan.given(), y) + " as " + words(m, y, toMap(plan.changePieces())) : ", no change");
            boolean expectOk = p.money().isEmpty() || p.money().equals(m.id());
            boolean ok = expectOk && !pieces.isEmpty() && plan != null && plan.given() == plan.change()
                    && Denominations.splitValue(pieces, day) == day;
            if (!ok) {
                tourBad++;
            }
            System.out.printf(Locale.ROOT, "   %s %-14s %5d  %s (%s): %s%n", ok ? "ok " : "BAD", p.name(), y, m.name(), m.id(), sb);
            System.out.printf(Locale.ROOT, "        day %s = %s; paper %s: %s%n", MoneyFormat.amount(m, day, y),
                    words(m, y, toMap(start)), MoneyFormat.amount(m, price, y), payWords);
        }
        check(TOUR.size() + " tour places: the expected money, a day's pay exactly in pieces, a paper paid with exact change",
                tourBad == 0, tourBad + " bad");

        System.out.println();
        System.out.println("3. Every money in its first, middle and last year");
        int checked = 0;
        int dayManyPieces = 0;
        int notExactDay = 0;
        int priceNotPayable = 0;
        int changeCrumbs = 0;
        long worstCount = 0;
        String worstAt = "";
        double worstCrumb = 0;
        String crumbAt = "";
        EnumMap<Denominations.Form, Integer> looks = new EnumMap<>(Denominations.Form.class);
        List<String> notes = new ArrayList<>();
        for (MoneyTable.Money m : t.monies().values()) {
            if (m.inDays()) {
                continue;
            }
            int[] span = Denominations.span(t, m);
            for (int y : new int[] {span[0], span[0] + (span[1] - span[0]) / 2, span[1]}) {
                List<Denominations.Piece> pieces = Denominations.of(m, y);
                for (Denominations.Piece x : pieces) {
                    looks.merge(x.form(), 1, Integer::sum);
                }
                long small0 = Denominations.smallest(m, y);
                long day = Math.max(small0, Math.round(m.dayPay(y) / (double) small0) * small0);
                long n = Denominations.splitCount(pieces, day);
                if (n > worstCount) {
                    worstCount = n;
                    worstAt = m.id() + " " + y;
                }
                if (n > 12) {
                    dayManyPieces++;
                }
                long small = Denominations.smallest(m, y);
                if (Denominations.splitValue(pieces, day) != day) {
                    notExactDay++;
                    if (notes.size() < 6) {
                        notes.add(m.id() + " " + y + " day " + day + " -> " + Denominations.splitValue(pieces, day));
                    }
                }
                for (long share : new long[] {16, 8, 2}) {
                    long price = ShopService.nice(Math.max(1L, day / share), m, y);
                    if (price % small != 0) {
                        priceNotPayable++;
                    }
                    Map<Long, Long> held = toMap(Denominations.split(pieces, Math.max(day, price)));
                    Denominations.Plan plan = Denominations.plan(held, price, pieces);
                    if (plan == null) {
                        priceNotPayable++;
                        continue;
                    }
                    if (plan.given() != plan.change()) {
                        changeCrumbs++;
                        double crumb = (plan.change() - plan.given()) / (double) Math.max(1L, day);
                        if (crumb > worstCrumb) {
                            worstCrumb = crumb;
                            crumbAt = m.id() + " " + y + " price " + price + ": change " + plan.change() + ", given "
                                    + plan.given();
                        }
                    }
                }
                checked++;
            }
        }
        System.out.printf(Locale.ROOT, "   %d money-years: a day's pay in at most %d pieces (%s); %d need more than 12; %d"
                        + " not exact in pieces; %d prices not payable; %d payments with crumbs kept by the seller"
                        + " (worst %.5f of a day%s)%n", checked, worstCount, worstAt, dayManyPieces, notExactDay,
                priceNotPayable, changeCrumbs, worstCrumb, crumbAt.isEmpty() ? "" : ", " + crumbAt);
        StringBuilder lk = new StringBuilder();
        looks.forEach((f, k) -> lk.append(lk.length() == 0 ? "" : ", ").append(f.name().toLowerCase(Locale.ROOT)).append(' ').append(k));
        System.out.println("   pieces by look: " + lk);
        for (String s : notes) {
            System.out.println("   not exact: " + s);
        }
        check("a day's pay is at most 12 pieces in nearly every money-year (at most 1 in 20 needs more)",
                dayManyPieces * 20 <= checked, dayManyPieces + " of " + checked);
        check("no day's pay needs more than 30 pieces", worstCount <= 30, worstCount + " at " + worstAt);
        check("a day's pay (rounded to the smallest piece) is always exact in pieces", notExactDay == 0,
                String.join("; ", notes));
        check("every price (a sixteenth, an eighth, half a day) is payable in pieces", priceNotPayable == 0,
                priceNotPayable + " not payable");
        check("crumbs left with the seller stay below a thousandth of a day", worstCrumb < 0.001d, crumbAt);

        System.out.println();
        long ms = (System.nanoTime() - t0) / 1_000_000L;
        System.out.println("RESULT: " + pass + " passed, " + fail + " failed, in " + ms + " ms");
        System.exit(fail == 0 ? 0 : 1);
    }

    static String short_(Denominations.Form f) {
        return switch (f) {
            case GOLD -> "[gold]";
            case SILVER -> "[silver]";
            case COPPER -> "[copper]";
            case HOLED -> "[holed]";
            case NICKEL -> "[nickel]";
            case BANKNOTE -> "[note]";
            case COWRIE -> "[cowries]";
            case CACAO -> "[beans]";
            case SILVER_WEIGHT -> "[cut silver]";
            case COPPER_WEIGHT -> "[copper weight]";
            case MANILLA -> "[manillas]";
            case SHELL -> "[shells]";
            case SALT -> "[salt bars]";
            case CLOTH -> "[cloth]";
            case PELT -> "[pelts]";
            case BULLET -> "[bullet]";
        };
    }

    static Map<Long, Long> toMap(List<long[]> vn) {
        Map<Long, Long> m = new TreeMap<>();
        for (long[] x : vn) {
            m.merge(x[0], x[1], Long::sum);
        }
        return m;
    }

    static String words(MoneyTable.Money m, int y, Map<Long, Long> pieces) {
        List<String> out = new ArrayList<>();
        List<Long> keys = new ArrayList<>(pieces.keySet());
        java.util.Collections.reverse(keys);
        for (Long v : keys) {
            long n = pieces.get(v);
            if (n > 0) {
                out.add(n + " x " + MoneyFormat.amount(m, v, y));
            }
        }
        return out.isEmpty() ? "nothing" : String.join(" + ", out);
    }

    static void check(String what, boolean ok, String detail) {
        if (ok) {
            pass++;
            System.out.println("   PASS " + what);
        } else {
            fail++;
            System.out.println("   FAIL " + what + " -- " + detail);
        }
    }
}
