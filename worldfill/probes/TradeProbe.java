import com.eternalengine.client.gui.paint.Canvas;
import com.eternalengine.client.gui.paint.TradeMenuPainter;
import com.eternalengine.knowledge.KnowledgeDate;
import com.eternalengine.money.CoinPurse;
import com.eternalengine.money.Denominations;
import com.eternalengine.money.GoodsTable;
import com.eternalengine.money.MarketService;
import com.eternalengine.money.MoneyFormat;
import com.eternalengine.money.MoneyTable;
import com.eternalengine.money.ShopService;
import com.eternalengine.money.Tender;
import com.eternalengine.money.TradeRules;
import com.eternalengine.money.TradeView;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/**
 * Step 24: Minecraft's trade screen with townspeople, checked without a game. The rules of the two slots
 * (TradeRules.selfTest); every money with pieces in its first, middle and last year paying prices from a fiftieth of a
 * day to a whole day out of a day's pay (two slots, change back, out of the purse when two slots cannot hold it); where
 * small change is used (cowries beside manillas) and the prices it makes; selling a lot at the test places; changing
 * money at the test places, any amount; bigger and smaller pieces of every money; and pictures of the screen with coins
 * in its slots, drawn with the game's own pictures and font, into probes/out/trade_*.png (copies for the README in
 * pictures/). Exit code 1 if a check fails.
 */
public class TradeProbe {

    static int pass;
    static int fail;

    public static void main(String[] args) throws Exception {
        TalkLayoutProbe.loadFont();
        new File(TalkLayoutProbe.OUT).mkdirs();
        MoneyTable table = MoneyTable.get();
        MarketService.Terms terms = MarketService.Terms.DEFAULT;

        System.out.println("1. The rules of the two slots");
        String t = TradeRules.selfTest();
        check("the trade rules' own check (paying, change, Indian rupees at 7 for 6, old money, selling a lot, changing one"
                + " rupee of two, bigger and smaller pieces, the purse, cowries beside manillas, swapping with a tab)",
                t == null, t == null ? "all well" : t);

        System.out.println("\n2. Every money with pieces pays from a day's pay");
        int moneyYears = 0;
        int prices = 0;
        int slots2 = 0;
        int purse = 0;
        int unpaid = 0;
        int crumbs = 0;
        int missesRich = 0;
        List<String> unpaidAt = new ArrayList<>();
        double[] fs = {0.02, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0};
        for (MoneyTable.Money m : table.monies().values()) {
            if (m.inDays()) {
                continue;
            }
            int[] span = Denominations.span(table, m);
            for (int y : new int[] {span[0], (span[0] + span[1]) / 2, span[1]}) {
                List<Denominations.Piece> ps = Denominations.of(m, y);
                if (ps.isEmpty()) {
                    continue;
                }
                moneyYears++;
                long day = m.dayPay(y);
                for (int days : new int[] {1, 3}) {
                    List<long[]> split = Denominations.split(ps, day * days);
                    List<Tender.Kind> kinds = new ArrayList<>();
                    Map<Long, Long> held = new TreeMap<>();
                    long total = 0L;
                    for (long[] vn : split) {
                        total += vn[0] * vn[1];
                        held.merge(vn[0], vn[1], Long::sum);
                        long n = vn[1];
                        while (n > 0) {
                            long c = Math.min(64L, n);
                            kinds.add(new Tender.Kind(String.valueOf(vn[0]), vn[0], c, 64));
                            n -= c;
                        }
                    }
                    for (double f : fs) {
                        long price = ShopService.nice(Math.max(1L, Math.round(f * day)), m, y);
                        if (price > total) {
                            continue;
                        }
                        prices++;
                        Tender.Pick p = Tender.choose(kinds, price);
                        if (p != null) {
                            slots2++;
                            long change = p.value() - price;
                            if (change > 0 && Denominations.splitValue(ps, change) != change) {
                                crumbs++;
                            }
                            continue;
                        }
                        if (days > 1) {
                            missesRich++;
                        }
                        if (Denominations.plan(held, price, ps) != null) {
                            purse++;
                        } else {
                            unpaid++;
                            if (unpaidAt.size() < 5) {
                                unpaidAt.add(m.id() + " " + y + " " + price);
                            }
                        }
                    }
                }
            }
        }
        System.out.println("  " + moneyYears + " money-years, " + prices + " prices: " + slots2 + " paid from the two slots, "
                + purse + " out of the purse (more kinds of pieces than two slots hold), " + unpaid + " not paid, "
                + crumbs + " with change that is not whole pieces");
        check("every price up to a day's pay is paid, from the two slots or out of the purse, with change in whole pieces",
                unpaid == 0 && crumbs == 0 && moneyYears >= 1100, unpaid + " unpaid " + unpaidAt + ", " + crumbs + " crumbs");
        check("with three days' pay every price is paid from the two slots", missesRich == 0, missesRich + " not");
        check("most prices go through the two slots (more than 95 in 100)", slots2 * 100 > prices * 95,
                slots2 + " of " + prices);

        System.out.println("\n3. Small change");
        Map<String, Integer> smallAt = new LinkedHashMap<>();
        int rowsWithAccepts = 0;
        for (MoneyTable.Row r : table.rows()) {
            if (r.accepts().isEmpty()) {
                continue;
            }
            rowsWithAccepts++;
            for (int y = Math.max(r.from(), -3000); y <= Math.min(r.to(), 2026); y += Math.max(1, (r.to() - r.from()) / 6)) {
                MoneyTable.Here h = new MoneyTable.Here(r, r.money(), r.accepts(), y, Double.NaN, Double.NaN);
                MoneyTable.Money s = TradeRules.smallChange(table, h);
                if (s != null) {
                    smallAt.merge(r.id() + " (" + r.money().id() + " with " + s.id() + ")", 1, Integer::sum);
                }
            }
        }
        System.out.println("  rows that also take another money: " + rowsWithAccepts + "; small change at: " + smallAt);
        check("small change is used only where a coarse money takes a fine one beside it (manillas and cowries)",
                smallAt.size() == 1 && smallAt.keySet().iterator().next().startsWith("biafra_manilla"), smallAt.toString());
        MoneyTable.Here cal = table.at(4.95, 8.32, 1800);
        List<String> calPrices = new ArrayList<>();
        boolean calOk = true;
        for (double f : new double[] {0.05, 0.25, 0.9, 1.5, 3.0}) {
            TradeRules.Price p = TradeRules.price(f * cal.dayPay(), table, cal, false);
            calPrices.add(f + " day: " + MoneyFormat.amount(p.money(), p.amount(), 1800));
            boolean small = f * cal.dayPay() < TradeRules.SMALL_BELOW;
            calOk &= small == p.money().id().equals("cowrie");
        }
        System.out.println("  Calabar 1800 (a day's pay " + MoneyFormat.amount(cal.money(), cal.dayPay(), 1800) + "): "
                + String.join("; ", calPrices));
        check("Calabar 1800: cheap things cost cowries, dear things manillas", calOk, calPrices.toString());

        System.out.println("\n4. Selling a lot");
        GoodsTable.Good wheat = GoodsTable.get().good("WHEAT");
        Object[][] places = {{"Bombay", 18.94, 72.83, 1948}, {"Varna", 43.21, 27.91, 2026}, {"Moscow", 55.76, 37.62, 2026},
                {"Calabar", 4.95, 8.32, 1800}, {"Edo", 35.68, 139.76, 1700}, {"Rome", 41.89, 12.49, 100},
                {"London", 51.51, -0.13, 1800}, {"Lagos", 6.45, 3.38, 2026}};
        int sold = 0;
        for (Object[] p : places) {
            MoneyTable.Here h = table.at((double) p[1], (double) p[2], (int) p[3]);
            if (h.money().inDays()) {
                System.out.println("  " + p[0] + " " + p[3] + ": people swap goods");
                continue;
            }
            MarketService.Terms mt = terms.as(MarketService.MERCHANT);
            double each = MarketService.pays(wheat, h, "market", mt);
            int q = ShopService.lotSize(each, h.money(), h.year());
            MarketService.Offer o = MarketService.payable(MarketService.offer(each, wheat.want(), q, 0,
                    MarketService.budget(h, mt)), h.money(), h.year());
            MoneyTable.Money in = h.money();
            MoneyTable.Money small = TradeRules.smallChange(table, h);
            if (small != null && (!o.ok() || o.amount() < TradeRules.SMALL_BELOW * Denominations.smallest(in, h.year()))) {
                double r = TradeRules.rate(table, in, small, h.year());
                MarketService.Offer os = MarketService.payable(MarketService.offer(each * r, wheat.want(), q, 0,
                        (long) (MarketService.budget(h, mt) * r)), small, h.year());
                if (os.ok()) {
                    o = os;
                    in = small;
                }
            }
            List<Denominations.Piece> ps = TradeRules.pieces(table, in, h.year());
            boolean whole = o.ok() && Denominations.splitValue(ps, o.amount()) == o.amount();
            sold += whole ? 1 : 0;
            System.out.println("  " + p[0] + " " + p[3] + ": " + wheat.count(o.count()) + " for "
                    + (o.ok() ? MoneyFormat.amount(in, o.amount(), h.year()) + " (" + Denominations.splitCount(ps, o.amount())
                    + " pieces)" : "nothing (" + o.reason() + ")"));
        }
        check("a lot of wheat sells for whole pieces at every test place with money (Calabar in cowries)", sold >= 7,
                sold + " places");

        System.out.println("\n5. Changing money, any amount");
        int changed = 0;
        int changes = 0;
        String[][] pairs = {{"17.3616,78.4747,1948", "osmania_sicca", "indian_rupee_anna"},
                {"17.3616,78.4747,1948", "indian_rupee_anna", "osmania_sicca"}, {"17.3616,78.4747,1948", "sicca", "osmania_sicca"},
                {"55.76,37.62,2026", "euro", "ruble_ru"}, {"6.45,3.38,2026", "gbp", "naira"},
                {"4.95,8.32,1800", "cowrie", "manilla"}, {"4.95,8.32,1800", "manilla", "cowrie"},
                {"51.51,-0.13,1800", "livre", "pound_lsd"}};
        for (String[] pr : pairs) {
            String[] ll = pr[0].split(",");
            MoneyTable.Here h = table.at(Double.parseDouble(ll[0]), Double.parseDouble(ll[1]), Integer.parseInt(ll[2]));
            MoneyTable.Money from = table.money(pr[1]);
            MoneyTable.Money to = table.money(pr[2]);
            if (from == null || to == null) {
                System.out.println("  (no money " + pr[1] + " or " + pr[2] + ")");
                continue;
            }
            changes++;
            TradeRules.Ctx c = new TradeRules.Ctx(table, h, terms, false, Map.of());
            TradeRules.Deal d = new TradeRules.Deal("change:" + from.id() + ">" + to.id(), TradeView.Kind.CHANGE);
            d.from = from;
            d.money = to;
            List<Denominations.Piece> fp = TradeRules.pieces(table, from, h.year());
            long day = from.dayPay(Denominations.yearFor(table, from, h.year()));
            List<long[]> purseSplit = Denominations.split(fp, day);
            List<TradeRules.Lump> lumps = new ArrayList<>();
            for (int i = 0; i < Math.min(2, purseSplit.size()); i++) {
                lumps.add(TradeRules.Lump.money(i, from.id(), purseSplit.get(i)[0], Math.min(64, purseSplit.get(i)[1])));
            }
            TradeRules.Outcome all = TradeRules.judge(d, lumps, c);
            TradeRules.Outcome one = TradeRules.judge(d, List.of(TradeRules.Lump.money(0, from.id(),
                    fp.get(fp.size() - 1).value(), 1)), c);
            boolean ok = all.ok() && all.given() > 0 && one.ok();
            changed += ok ? 1 : 0;
            System.out.println("  " + h.year() + ": " + all.words() + " One piece: " + one.words());
        }
        check("the money-changers change a day's pay and a single piece at the test places", changed == changes,
                changed + " of " + changes);

        System.out.println("\n6. Bigger and smaller pieces of every money");
        int regroups = 0;
        int regroupBad = 0;
        List<String> badAt = new ArrayList<>();
        for (MoneyTable.Money m : table.monies().values()) {
            if (m.inDays()) {
                continue;
            }
            int[] span = Denominations.span(table, m);
            int y = (span[0] + span[1]) / 2;
            List<Denominations.Piece> ps = Denominations.of(m, y);
            if (ps.size() < 2) {
                continue;
            }
            MoneyTable.Here h = new MoneyTable.Here(table.rows().get(0), m, List.of(), y, Double.NaN, Double.NaN);
            TradeRules.Ctx c = new TradeRules.Ctx(table, h, terms, false, Map.of());
            TradeRules.Deal brk = new TradeRules.Deal("break", TradeView.Kind.BREAK);
            brk.from = m;
            brk.money = m;
            TradeRules.Deal mk = new TradeRules.Deal("make", TradeView.Kind.MAKE);
            mk.from = m;
            mk.money = m;
            long big = ps.get(ps.size() - 1).value();
            long small = ps.get(0).value();
            long n = Math.min(64L, Math.max(2L, ps.get(1).value() / small * 2));
            TradeRules.Outcome b = TradeRules.judge(brk, List.of(TradeRules.Lump.money(0, m.id(), big, 1)), c);
            TradeRules.Outcome k = TradeRules.judge(mk, List.of(TradeRules.Lump.money(0, m.id(), small, n)), c);
            regroups++;
            boolean bOk = b.ok() ? b.given() == big && b.givenPieces() >= 2 : b.words().contains("carry");
            boolean kOk = k.ok() && k.given() == small * n && k.givenPieces() < n;
            if (!bOk || !kOk) {
                regroupBad++;
                if (badAt.size() < 5) {
                    badAt.add(m.id() + " " + y + ": " + b.words() + " / " + k.words());
                }
            }
        }
        check("every money with two or more pieces breaks its biggest piece and makes bigger pieces of its smallest",
                regroupBad == 0 && regroups > 300, regroups + " monies, " + regroupBad + " wrong " + badAt);

        System.out.println("\n7. The screen");
        pictures(table, terms);

        System.out.println("\n" + pass + " passed, " + fail + " failed");
        System.exit(fail == 0 ? 0 : 1);
    }

    // ------------------------------------------------------------------------------------------- pictures

    /**
     * A merchant's wares as the shop lists them (ShopService.lots needs the game's items; this builds the same list
     * from the same tables and prices): his goods by the lot, the history book in the form people keep notes in here,
     * and the products sold here.
     */
    static TradeView waresOf(MoneyTable table, String name, double lat, double lon, int year) {
        MoneyTable.Here here = table.at(lat, lon, year);
        TradeView v = new TradeView();
        v.npcName = name;
        for (GoodsTable.Good g : GoodsTable.get().boughtAt(lat, lon, year)) {
            String item = "";
            for (String id : g.items()) {
                if (!id.startsWith("#")) {
                    item = id;
                    break;
                }
                item = id.contains("log") ? "minecraft:oak_log" : id.contains("wool") ? "minecraft:white_wool" : item;
            }
            if (item.isEmpty()) {
                continue;
            }
            double each = MarketService.worth(g, here, MarketService.basePrice(g.id())) * ShopService.SELL_PERCENT / 100.0d;
            int q = ShopService.lotSize(each, here.money(), year);
            TradeRules.Price p = TradeRules.price(each * q, table, here, true);
            v.offers.add(new TradeView.Offer("good:" + g.id(), item, Math.min(64, q), Character.toUpperCase(g.some(q).charAt(0))
                    + g.some(q).substring(1), g.name(), "He has a few lots like this a day.", MoneyFormat.amount(p.money(),
                    p.amount(), year), p.amount(), 3, false, p.money().id()));
        }
        for (com.eternalengine.news.BookForms.Form f : com.eternalengine.news.BookForms.soldBy("merchant", lat, lon, year)) {
            TradeRules.Price p = TradeRules.price(com.eternalengine.news.BookForms.days(f, year) * here.dayPay(), table, here,
                    false);
            String item = f == com.eternalengine.news.BookForms.Form.NOTEBOOK ? "eternalengine:history_book"
                    : "eternalengine:" + f.itemId();
            v.offers.add(new TradeView.Offer(ShopService.BOOK + f.id, item, 1, f.offerName(), "History book", f.lore,
                    MoneyFormat.amount(p.money(), p.amount(), year), p.amount(), -1, false, p.money().id()));
        }
        for (ShopService.Product pr : ShopService.products()) {
            if (pr.item().isBlank() || !pr.soldBy("merchant") || !pr.here(lat, lon, year) || pr.days() <= 0) {
                continue;
            }
            TradeRules.Price p = TradeRules.price(pr.days() * here.dayPay(), table, here, false);
            v.offers.add(new TradeView.Offer("prod:" + pr.id(), pr.item(), pr.count(), (pr.count() > 1 ? pr.count() + " × " : "")
                    + pr.name(), pr.shortName(), pr.lore(), MoneyFormat.amount(p.money(), p.amount(), year), p.amount(), 4,
                    false, p.money().id()));
        }
        return v;
    }

    static TradeView.Stack piece(MoneyTable table, MoneyTable.Money m, int year, long value, long count) {
        return ScreenProbe.pieceStack(table, m, year, new long[] {value, count});
    }

    static void pictures(MoneyTable table, MarketService.Terms terms) throws Exception {
        // Bombay, 1948: a merchant; the notebook picked; the coins of the start money in the slots, change to come.
        int d = KnowledgeDate.key(1948, 9, 14);
        double lat = 18.94;
        double lon = 72.83;
        MoneyTable.Here bom = table.at(lat, lon, 1948);
        ShopService.Seller s = new ShopService.Seller("merchant", "Ramesh Patil", -1, new java.util.UUID(24L, 1L), "market",
                lat, lon, d);
        TradeView wares = waresOf(table, "Ramesh Patil", lat, lon, 1948);
        TradeView v = ScreenProbe.rowsOf(wares, lat, lon, 1948, -1);
        v.title = "Ramesh Patil's goods";
        v.says = "Have a look. These are today's prices. I buy wheat, bread, logs, stone and 9 more: full price for the"
                + " first few of each, half for more. Pick a trade on the left.";
        // His offer for 16 sheaves of wheat, as the screen lists it after his goods.
        GoodsTable.Good wheat = GoodsTable.get().good("WHEAT");
        MarketService.Terms mt = terms.as(MarketService.MERCHANT);
        double each = MarketService.pays(wheat, bom, "market", mt);
        MarketService.Offer o = MarketService.payable(MarketService.offer(each, wheat.want(), 16, 0,
                MarketService.budget(bom, mt)), bom.money(), 1948);
        List<long[]> pay = Denominations.split(TradeRules.pieces(table, bom.money(), 1948), o.amount());
        v.rows.add(0, new TradeView.Row("sell:WHEAT", TradeView.Kind.SELL, new TradeView.Stack("minecraft:wheat", 16, null),
                TradeView.Stack.NONE, false, piece(table, bom.money(), 1948, pay.get(0)[0], pay.get(0)[1]), pay.size() > 1,
                "Sell 16 sheaves of wheat", MoneyFormat.amount(bom.money(), o.amount(), 1948), "", -1, false));
        int book = -1;
        for (int i = 0; i < v.rows.size(); i++) {
            if (v.rows.get(i).id().startsWith(ShopService.BOOK)) {
                book = i;
            }
        }
        check("the Bombay merchant sells a history book on the trade screen", book >= 0, v.rows.size() + " rows");
        if (book >= 0) {
            TradeView.Row br = v.rows.get(book);
            // The start money: a day's pay in pieces; the screen fills the slots with the best two kinds for the price.
            List<Denominations.Piece> ps = Denominations.of(bom.money(), 1948);
            List<long[]> start = Denominations.split(ps, PurseServiceStart.amount(bom));
            List<Tender.Kind> kinds = new ArrayList<>();
            for (long[] vn : start) {
                kinds.add(new Tender.Kind(String.valueOf(vn[0]), vn[0], vn[1], 64));
            }
            long price = Long.parseLong(wares.offer(br.id()).price() + "");
            Tender.Pick p = Tender.choose(kinds, price);
            List<TradeRules.Lump> lumps = new ArrayList<>();
            TradeView.Stack[] slots = new TradeView.Stack[39];
            if (p != null) {
                long[] a = start.get(p.a());
                lumps.add(TradeRules.Lump.money(0, bom.money().id(), a[0], p.na()));
                slots[0] = piece(table, bom.money(), 1948, a[0], p.na());
                if (p.b() >= 0) {
                    long[] b = start.get(p.b());
                    lumps.add(TradeRules.Lump.money(1, bom.money().id(), b[0], p.nb()));
                    slots[1] = piece(table, bom.money(), 1948, b[0], p.nb());
                }
            }
            TradeRules.Deal deal = new TradeRules.Deal(br.id(), TradeView.Kind.BUY);
            deal.money = bom.money();
            deal.amount = price;
            deal.priceText = br.price();
            TradeRules.Outcome out = TradeRules.judge(deal, lumps, new TradeRules.Ctx(table, bom, terms, false, Map.of()));
            check("Bombay 1948: the start money in the two slots pays for the notebook, with change (\"" + out.words() + "\")",
                    out.ok() && out.given() > 0, out.words());
            slots[2] = br.result();
            int k = 3;
            for (int i = 0; i < start.size(); i++) {
                long left = start.get(i)[1] - (p == null ? 0 : p.of(i));
                if (left > 0) {
                    slots[30 + (k++ % 9)] = piece(table, bom.money(), 1948, start.get(i)[0], left);
                }
            }
            slots[3] = new TradeView.Stack("minecraft:wheat", 32, null);
            slots[4] = new TradeView.Stack("minecraft:bread", 5, null);
            v.selected = book;
            v.status = out.words();
            v.purse = "Your money: " + MoneyFormat.amount(bom.money(), PurseServiceStart.amount(bom), 1948) + " (Indian rupee)";
            v.dateLabel = KnowledgeDate.label(d);
            shot("trade_bombay_1948", v, slots);
        }

        // Calabar, 1800: the notebook costs cowries; a manilla pays and cowries come back.
        int dc = KnowledgeDate.key(1800, 6, 1);
        MoneyTable.Here cal = table.at(4.95, 8.32, 1800);
        ShopService.Seller cs = new ShopService.Seller("merchant", "Efiom Duke", -1, new java.util.UUID(24L, 2L), "market",
                4.95, 8.32, dc);
        TradeView cw = waresOf(table, "Efiom Duke", 4.95, 8.32, 1800);
        TradeView cv = ScreenProbe.rowsOf(cw, 4.95, 8.32, 1800, -1);
        cv.title = "Efiom Duke's goods";
        cv.says = "Have a look. These are today's prices. Small things cost cowries; a manilla is worth "
                + MoneyFormat.amount(table.money("cowrie"), Math.round(TradeRules.rate(table, cal.money(),
                table.money("cowrie"), 1800)), 1800) + " today. Pick a trade on the left.";
        int cbook = -1;
        for (int i = 0; i < cv.rows.size(); i++) {
            if (cv.rows.get(i).id().startsWith(ShopService.BOOK)) {
                cbook = i;
            }
        }
        if (cbook >= 0) {
            TradeView.Offer co = cw.offer(cv.rows.get(cbook).id());
            MoneyTable.Money cm = table.money(co.money().isEmpty() ? cal.money().id() : co.money());
            TradeRules.Deal deal = new TradeRules.Deal(co.id(), TradeView.Kind.BUY);
            deal.money = cm;
            deal.amount = co.price();
            deal.priceText = co.priceText();
            TradeRules.Outcome out = TradeRules.judge(deal, List.of(TradeRules.Lump.money(0, "manilla", 1, 1)),
                    new TradeRules.Ctx(table, cal, terms, false, Map.of()));
            check("Calabar 1800: the notebook costs " + co.priceText() + " and a manilla pays it, cowries back (\""
                    + out.words() + "\")", cm.id().equals("cowrie") && out.ok() && out.given() > 0, co.priceText() + " / "
                    + out.words());
            TradeView.Stack[] slots = new TradeView.Stack[39];
            slots[0] = piece(table, cal.money(), 1800, 1, 1);
            slots[2] = cv.rows.get(cbook).result();
            slots[30] = piece(table, cal.money(), 1800, 1, 2);
            slots[31] = piece(table, table.money("cowrie"), 1800, Denominations.of(table.money("cowrie"), 1800).get(0).value(), 40);
            cv.selected = cbook;
            cv.status = out.words();
            cv.purse = "Your money: 3 manillas";
            cv.dateLabel = KnowledgeDate.label(dc);
            shot("trade_calabar_1800", cv, slots);
        }

        // Hyderabad, 1948: the money-changer; two O.S. rupees in the slots become Indian money.
        MoneyTable.Here hyd = table.at(17.3616, 78.4747, 1948);
        MoneyTable.Money os = hyd.money();
        MoneyTable.Money inr = table.money("indian_rupee_anna");
        TradeView hv = new TradeView();
        hv.npcName = "Abdul Karim";
        hv.title = "Abdul Karim, money-changer";
        hv.dateLabel = KnowledgeDate.label(d);
        hv.says = "I change money into the Osmania sicca. Where the rate is fixed I keep 2 in every 100; for old money, or"
                + " money from far away, 10 in every 100. Pick a trade on the left.";
        TradeRules.Deal ch = new TradeRules.Deal("change:osmania_sicca>indian_rupee_anna", TradeView.Kind.CHANGE);
        ch.from = os;
        ch.money = inr;
        TradeRules.Outcome two = TradeRules.judge(ch, List.of(TradeRules.Lump.money(0, os.id(), 192, 2)),
                new TradeRules.Ctx(table, hyd, terms, false, Map.of()));
        List<long[]> got = two.give();
        hv.rows.add(new TradeView.Row(ch.id, TradeView.Kind.CHANGE, piece(table, os, 1948, 192, 3), piece(table, os, 1948, 12, 5),
                false, piece(table, inr, 1948, got.get(0)[0], got.get(0)[1]), got.size() > 1, "Change into Indian rupee",
                "all your 3 rupees 5 annas for 2 rupees 10 annas (Indian rupee)", "", -1, false));
        hv.rows.add(new TradeView.Row("make:osmania_sicca", TradeView.Kind.MAKE, piece(table, os, 1948, 12, 5),
                TradeView.Stack.NONE, false, piece(table, os, 1948, 48, 1), true, "Bigger pieces", "the same money, for nothing",
                "", -1, false));
        hv.rows.add(new TradeView.Row("break:osmania_sicca", TradeView.Kind.BREAK, piece(table, os, 1948, 192, 1),
                TradeView.Stack.NONE, false, piece(table, os, 1948, 96, 2), false, "Smaller pieces", "the same money, for nothing",
                "", -1, false));
        hv.selected = 0;
        hv.status = two.words();
        hv.purse = "Your money: 3 rupees 5 annas (Osmania sicca)";
        TradeView.Stack[] hs = new TradeView.Stack[39];
        hs[0] = piece(table, os, 1948, 192, 2);
        hs[2] = piece(table, inr, 1948, got.get(0)[0], Math.min(64, got.get(0)[1]));
        hs[30] = piece(table, os, 1948, 192, 1);
        hs[31] = piece(table, os, 1948, 12, 5);
        check("Hyderabad 1948: two O.S. rupees change into Indian money (\"" + two.words() + "\")", two.ok() && two.given() > 0,
                two.words());
        shot("trade_hyderabad_changer_1948", hv, hs);
    }

    /** Draws a trade screen at the user's 480 x 270 and at the smallest common GUI (426 x 240); copies the first. */
    static void shot(String name, TradeView v, TradeView.Stack[] slots) throws Exception {
        for (int[] size : new int[][] {{480, 270}, {426, 240}}) {
            String tag = size[0] + "x" + size[1];
            ScreenProbe.screen(size, name + "_" + tag, c -> ScreenProbe.tradeScreen(c, v, ScreenProbe.sw, ScreenProbe.sh,
                    slots));
        }
        File out = new File(TalkLayoutProbe.OUT, "screen_" + name + "_480x270.png");
        File pics = new File("/home/user/worldfill/pictures");
        pics.mkdirs();
        if (out.exists()) {
            Files.copy(out.toPath(), new File(pics, name + ".png").toPath(), StandardCopyOption.REPLACE_EXISTING);
        }
        if (ScreenProbe.fails > 0) {
            fail += ScreenProbe.fails;
            ScreenProbe.fails = 0;
        } else {
            pass++;
        }
    }

    /** The start money of a place (PurseService.startAmount needs only the place). */
    static final class PurseServiceStart {
        static long amount(MoneyTable.Here h) {
            return com.eternalengine.money.PurseService.startAmount(h);
        }
    }

    static void check(String what, boolean ok, String detail) {
        if (ok) {
            pass++;
            System.out.println("  PASS " + what);
        } else {
            fail++;
            System.out.println("  FAIL " + what + " -- " + detail);
        }
    }
}
