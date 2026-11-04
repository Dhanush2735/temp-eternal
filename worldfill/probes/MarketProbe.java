import com.eternalengine.knowledge.KnowledgeDate;
import com.eternalengine.knowledge.TalkService;
import com.eternalengine.knowledge.TalkView;
import com.eternalengine.money.GoodsTable;
import com.eternalengine.money.MarketService;
import com.eternalengine.money.MoneyFormat;
import com.eternalengine.money.MoneyTable;
import com.eternalengine.money.PlayerPurses;
import com.eternalengine.population.SettlementDensity;

import java.util.Arrays;
import java.util.List;
import java.util.UUID;

/**
 * Step 19b: merchants, the money-changer and the talk screen's trade views, with the mod's real code and data (the
 * ruler register too), no server. Run by worldfill/probe_market.sh. Exit code 1 if a check fails.
 */
public final class MarketProbe {
    private static int pass;
    private static int fail;
    private static final MarketService.Terms T = MarketService.Terms.DEFAULT;

    public static void main(String[] args) {
        MoneyTable table = MoneyTable.get();
        GoodsTable goods = GoodsTable.get();
        GoodsTable.Summary gs = goods.summary();
        System.out.println("1. The tables");
        check("the goods table loads with no problems (" + gs.goods() + " goods, " + gs.withItems() + " with items)",
                gs.loaded() && goods.problems().isEmpty() && gs.goods() == 13 && gs.withItems() == 10,
                String.join("; ", goods.problems()));
        check("the goods table's self-test (wheat and iron by place and year)", goods.selfTest() == null, goods.selfTest());
        check("the money table loads with the new fixed rates (" + table.summary().rates() + " rates)",
                table.problems().isEmpty() && table.summary().rates() >= 25, String.join("; ", table.problems()));
        long t0 = System.nanoTime();
        String self = MarketService.selfTest();
        check("the market's self-test (offers, swaps, money-changers, a saved day; "
                + (System.nanoTime() - t0) / 1_000_000L + " ms)", self == null, self);

        System.out.println("\n2. What a merchant pays (full price, " + T.buyPercent() + " in 100 of the worth)");
        price("Hyderabad", 17.3616, 78.4747, 1948, "WHEAT", "4 annas 5 pai for 16 sheaves of wheat");
        price("Hyderabad", 17.3616, 78.4747, 1948, "IRON_INGOT", "5 annas 7 pai for a bar of iron");
        price("Hyderabad", 17.3616, 78.4747, 1948, "STONE", "5 annas 7 pai for 64 blocks of stone");
        price("Hyderabad", 17.3616, 78.4747, 1948, "GOLD_INGOT", "1 rupee 14 annas 9 pai for a bar of gold");
        price("Hyderabad", 17.3616, 78.4747, 1948, "TIMBER", "8 annas 11 pai for 16 logs");
        price("Delhi", 28.6139, 77.2090, 1600, "WHEAT", null);
        price("London", 51.507, -0.128, 1800, "WHEAT", null);
        price("Rome", 41.89, 12.49, 100, "IRON_INGOT", null);
        price("Babylon", 32.54, 44.42, -1750, "WHEAT", "6 grains of silver for 64 sheaves of wheat");
        price("Babylon", 32.54, 44.42, -1750, "IRON_INGOT", "-");
        price("Babylon", 32.54, 44.42, -1000, "IRON_INGOT", null);
        price("Beijing", 39.9, 116.4, -1000, "IRON_INGOT", "-");
        price("Tenochtitlan", 19.43, -99.13, 1500, "WHEAT", "-");
        price("Tenochtitlan", 19.43, -99.13, 1500, "GOLD_INGOT", "192 cacao beans for a bar of gold");
        price("Mexico City", 19.43, -99.13, 1600, "WHEAT", null);
        price("Sydney", -33.87, 151.21, 1500, "TIMBER", "goods worth about half a day's work for 16 logs");
        price("Sydney", -33.87, 151.21, 1500, "IRON_INGOT", "-");
        price("Sydney", -33.87, 151.21, 1850, "WOOL", null);
        int problems = 0;
        String first = "";
        int priced = 0;
        int nothing = 0;
        int[] years = {-3000, -1500, -500, 0, 500, 1000, 1500, 1700, 1850, 1948, 2000, 2026};
        for (int year : years) {
            for (int lat = -40; lat <= 60; lat += 20) {
                for (int lon = -120; lon <= 150; lon += 30) {
                    MoneyTable.Here h = table.at(lat + 0.5, lon + 0.5, year);
                    for (GoodsTable.Good g : goods.boughtAt(lat + 0.5, lon + 0.5, year)) {
                        String e = MarketService.priceEntry(g, MarketService.pays(g, h, "market", T), h.money(), year);
                        priced++;
                        if (e.startsWith("next to nothing")) {
                            nothing++; // the smallest coin is worth more than 64 of it (stone where a day is 2 jitals)
                        }
                        if (e.isBlank() || e.contains("minus")) {
                            problems++;
                            if (first.isEmpty()) {
                                first = lat + "," + lon + " " + year + " " + g.id() + ": " + e;
                            }
                        }
                    }
                }
            }
        }
        check(priced + " prices over a world grid from 3000 BCE to 2026 all have words (" + nothing
                        + " are \"next to nothing\": 64 of it are worth less than the smallest coin)",
                problems == 0 && priced > 1000 && nothing * 20 < priced, problems + " bad, first: " + first);

        System.out.println("\n3. A merchant's day in Hyderabad in 1948 (a sheaf of wheat 3.36 pai, 8 rupees a day)");
        MoneyTable.Here hyd = table.at(17.3616, 78.4747, 1948);
        GoodsTable.Good wheat = goods.good("WHEAT");
        GoodsTable.Good gold = goods.good("GOLD_INGOT");
        double each = MarketService.pays(wheat, hyd, "market", T);
        long budget = MarketService.budget(hyd, T);
        offer("64 sheaves", each, wheat.want(), 64, 0, budget, 64, 215);
        offer("200 sheaves: 64 at full price, 64 at half, then he has enough", each, wheat.want(), 200, 0, budget, 128, 322);
        offer("10 more after 128 today", each, wheat.want(), 10, 128, budget, 0, 0);
        offer("10 more after 100 today: 10 at half price", each, wheat.want(), 10, 100, budget, 10, 16);
        offer("100 sheaves with 1 rupee left: as many as 1 rupee pays", each, wheat.want(), 100, 0, 192, 57, 191);
        offer("1 sheaf", each, wheat.want(), 1, 0, budget, 1, 3);
        double goldEach = MarketService.pays(gold, hyd, "market", T);
        offer("4 bars of gold at full price", goldEach, gold.want(), 4, 0, budget, 4, 1478);
        offer("40 bars of gold: no more than his 8 rupees pay for", goldEach, gold.want(), 40, 0, budget, 4, 1478);
        MoneyTable.Here babylon = table.at(32.54, 44.42, -1750);
        MarketService.Offer little = MarketService.offer(MarketService.pays(goods.good("STONE"), babylon, "market", T),
                goods.good("STONE").want(), 3, 0, MarketService.budget(babylon, T));
        check("3 blocks of stone in Babylon are too little to pay for (" + little.reason() + ")",
                MarketService.Offer.LITTLE.equals(little.reason()) && little.count() == 0, String.valueOf(little));

        System.out.println("\n4. The money-changer (keeps " + T.feePercent() + " in 100 with a fixed rate, "
                + T.strangeFeePercent() + " otherwise)");
        swap(table, "7 O.S. rupees into Indian rupees, Hyderabad 1948", "osmania_sicca", 7 * 192, "indian_rupee_anna", 1948,
                true, "5 rupees 14 annas");
        swap(table, "6 Indian rupees into O.S. rupees", "indian_rupee_anna", 6 * 192, "osmania_sicca", 1948, true,
                "6 rupees 13 annas 9 pai");
        swap(table, "3 dams of 1700 into O.S. rupees", "mughal_rupee", 75, "osmania_sicca", 1948, false, "10 annas 9 pai");
        swap(table, "a pound into O.S. rupees (through the Indian rupee)", "pound_lsd", 960, "osmania_sicca", 1948, true,
                "15 rupees 3 annas 10 pai");
        swap(table, "a dollar into O.S. rupees in 1950", "dollar", 100, "osmania_sicca", 1950, true, null);
        swap(table, "a dollar into Indian rupees in 1948 (Rs 3.31)", "dollar", 100, "indian_rupee_anna", 1948, true, null);
        swap(table, "a dollar into rupees in 1930 (through sterling)", "dollar", 100, "indian_rupee_anna", 1930, true, null);
        swap(table, "a dollar into rupees in 1920 (no fixed rate then: by what it buys)", "dollar", 100,
                "indian_rupee_anna", 1920, false, null);
        swap(table, "a pound into Hali sicca in 1880 (through the Indian rupee, Rs 15)", "pound_lsd", 960, "hali_sicca",
                1880, true, null);
        swap(table, "goods worth a day into O.S. rupees", "barter", 100, "osmania_sicca", 1948, false, "14 annas 4 pai");
        swap(table, "a pound into rupees after the devaluation (1966: Rs 21)", "pound_lsd", 960, "indian_rupee", 1966, true,
                "20 rupees 58 paise");
        PlayerPurses purses = new PlayerPurses();
        UUID who = new UUID(0L, 19L);
        purses.add(who, "osmania_sicca", 192);
        purses.add(who, "mughal_rupee", 75);
        purses.add(who, "indian_rupee_anna", 96);
        List<MarketService.Swap> offers = MarketService.swaps(table, purses.view(who), hyd, T);
        check("a purse of O.S. rupees, Mughal dams and Indian rupees gets 3 offers in Hyderabad (O.S. into Indian, both"
                + " others into O.S.)", offers.size() == 3 && offers.get(0).to().id().equals("indian_rupee_anna")
                && offers.get(1).to().id().equals("osmania_sicca") && offers.get(2).to().id().equals("osmania_sicca"),
                offers.toString());
        boolean swapped = purses.swap(who, "mughal_rupee", 75, "osmania_sicca", 129);
        boolean tooMuch = purses.swap(who, "indian_rupee_anna", 97, "osmania_sicca", 100);
        check("a swap moves both amounts together, and a swap of more than the purse holds changes nothing",
                swapped && !tooMuch && purses.view(who).amount("osmania_sicca") == 321
                        && purses.view(who).amount("mughal_rupee") == 0 && purses.view(who).amount("indian_rupee_anna") == 96,
                purses.view(who).money().toString());
        check("emptying every purse (a reset of history)", purses.resetAll() == 1 && purses.playerCount() == 0, "");

        System.out.println("\n5. Money-changers in the crowd");
        String[] city = {"farmer", "artisan", "merchant", "citizen"};
        roles("Hyderabad 1948", MarketService.withMoneyChanger(city, 17.3616, 78.4747, 1948), true);
        roles("Rome 100", MarketService.withMoneyChanger(city, 41.89, 12.49, 100), true);
        roles("Babylon 1750 BCE (weighed silver)", MarketService.withMoneyChanger(city, 32.54, 44.42, -1750), true);
        roles("Sydney 1500 (no money)", MarketService.withMoneyChanger(city, -33.87, 151.21, 1500), false);
        roles("a village (no merchants)", MarketService.withMoneyChanger(new String[] {"farmer"}, 17.3616, 78.4747, 1948),
                false);
        String[] five = MarketService.withMoneyChanger(city, 17.3616, 78.4747, 1948);
        slots(five, 40, new int[] {10, 10, 10, 1, 9});
        slots(five, 4, new int[] {1, 1, 1, 1, 0});
        slots(five, 2, new int[] {1, 1, 0, 0, 0});
        slots(city, 40, new int[] {10, 10, 10, 10});

        System.out.println("\n6. The talk screen (no player, no villager: views only)");
        int date = KnowledgeDate.key(1948, 9, 14);
        TalkService.Ctx merchant = TalkService.context(null, null, -1, "Saleem", "merchant", 17.3616, 78.4747, date, -1);
        TalkView greet = TalkService.open(merchant);
        // Step 24: "Let's trade." (Minecraft's trade screen: his goods, and your goods he buys) comes first, then "What do
        // you buy?" (his prices); step 19d adds "Where can I get the news?" at the end. No option per good any more.
        check("a merchant's opening offers \"Let's trade.\" and \"What do you buy?\" first and \"Who changes"
                        + " money here?\" (" + greet.options.size() + " options)",
                greet.options.size() >= 2 && greet.options.get(0).action().equals("trade")
                        && greet.options.get(0).label().equals("Let's trade.")
                        && greet.options.get(1).label().equals("What do you buy?")
                        && has(greet, "Who changes money here?") && greet.options.size() <= 9, greet.options.toString());
        TalkView sell = TalkService.act(merchant, "topic", "sell", "");
        check("his goods and prices: \"I buy wheat, bread, logs ... I pay 4 annas 5 pai for 16 sheaves of wheat\"",
                // Step 19g: and the atlas products people here make or bring in.
                sell.text.startsWith("I buy wheat, bread, logs, stone, coal, iron, copper, wool, gold and emeralds, and"
                        + " things people here make or bring in: ")
                        && sell.text.contains("4 annas 5 pai for 16 sheaves of wheat")
                        && sell.text.contains("2 rupees 4 annas 4 pai for an emerald") && sell.options.isEmpty(),
                sell.text);
        TalkView sold = TalkService.act(merchant, "sell", "WHEAT", "16:53");
        check("step 24: the talk no longer sells (that is on the trade screen): an old \"sell\" just shows the talk",
                sold != null && sold.options.stream().noneMatch(o -> o.action().equals("sell")) && sold.hint.isEmpty(),
                sold == null ? "null" : sold.hint + " | " + sold.options);
        TalkView back = TalkService.act(merchant, "back", "", "");
        check("going back after a sale shows what came before it, not the sale again",
                !back.text.startsWith("I buy") || back.hint.isEmpty(), back.text);
        TalkService.Ctx changer = TalkService.context(null, null, -2, "Abdul", "money_changer", 17.3616, 78.4747, date, -1);
        TalkView cg = TalkService.open(changer);
        TalkView cv = TalkService.act(changer, "topic", "swap", "");
        check("a money-changer: \"Can you change my money?\" first; he names his cut and the money taken here",
                cg.options.get(0).label().equals("Can you change my money?") && cg.job.equals("money-changer")
                        && cv.text.startsWith("I change money into the Osmania sicca. Where the rate is fixed I keep 2 in every 100")
                        && cv.text.contains("7 O.S. rupees = 6 Indian rupees"), cg.job + " | " + cv.text);
        TalkService.Ctx citizen = TalkService.context(null, null, -3, "Ramaiah", "citizen", 17.3616, 78.4747, date, -1);
        TalkView zg = TalkService.open(citizen);
        TalkView where = TalkService.act(citizen, "topic", "market", "");
        TalkView notHis = TalkService.act(citizen, "topic", "sell", "");
        check("anyone else: \"Who buys goods here?\" and \"Where can I get the news?\" last; with nobody near, he says"
                        + " where merchants keep",
                zg.options.get(zg.options.size() - 2).label().equals("Who buys goods here?")
                        && zg.options.get(zg.options.size() - 1).label().equals("Where can I get the news?")
                        && where.text.startsWith("Nobody near here buys goods.") && !has(where, "Who buys goods here?")
                        && notHis.text.startsWith("I don't buy goods."), where.text + " | " + notHis.text);
        TalkService.Ctx rome = TalkService.context(null, null, -4, "Marcus", "merchant", 41.8925, 12.4853,
                KnowledgeDate.key(100, 6, 1), -1);
        TalkView rs = TalkService.act(rome, "topic", "sell", "");
        check("a merchant in Rome in 100 pays in asses and denarii", rs.text.contains(" as") || rs.text.contains("denari"),
                rs.text);

        System.out.println("\n" + pass + " passed, " + fail + " failed");
        System.exit(fail == 0 ? 0 : 1);
    }

    static boolean has(TalkView v, String label) {
        for (TalkView.Option o : v.options) {
            if (o.label().equals(label)) {
                return true;
            }
        }
        return false;
    }

    /** expect: the price entry, null for any, "-" for not bought there. */
    static void price(String name, double lat, double lon, int year, String good, String expect) {
        MoneyTable.Here h = MoneyTable.get().at(lat, lon, year);
        GoodsTable.Good g = GoodsTable.get().good(good);
        String when = year < 0 ? (-year) + " BCE" : String.valueOf(year);
        if (!g.boughtAt(lat, lon, year)) {
            check(name + " " + when + ": nobody buys " + g.name(), "-".equals(expect), "but expected " + expect);
            return;
        }
        String e = MarketService.priceEntry(g, MarketService.pays(g, h, "market", T), h.money(), year);
        check(name + " " + when + " (" + h.money().name() + "): " + e, expect == null ? !e.isBlank() && !e.contains("next to")
                : e.equals(expect), "expected " + expect);
    }

    static void offer(String what, double each, int want, int carried, int sold, long left, int count, long amount) {
        MarketService.Offer o = MarketService.offer(each, want, carried, sold, left);
        check(what + ": " + o.count() + " for " + o.amount() + " pai" + (o.reason().isEmpty() ? "" : " (" + o.reason() + ")"),
                o.count() == count && o.amount() == amount, "expected " + count + " for " + amount);
    }

    static void swap(MoneyTable t, String what, String from, long amount, String to, int year, boolean fixed, String expect) {
        MarketService.Swap s = MarketService.swapOffer(t, t.money(from), amount, t.money(to), year, T);
        String words = MoneyFormat.amount(s.to(), s.result(), year);
        check(what + ": " + words + " (" + s.fee() + " in 100 kept" + (s.fixed() ? ", fixed rate)" : ", by what it buys)"),
                s.fixed() == fixed && s.result() > 0 && (expect == null || words.equals(expect)), "expected " + expect
                        + (fixed ? " at a fixed rate" : " by what it buys"));
    }

    static void roles(String where, String[] roles, boolean changer) {
        boolean has = Arrays.asList(roles).contains(MarketService.MONEY_CHANGER);
        check(where + ": " + String.join(", ", roles), has == changer, "expected a money-changer: " + changer);
    }

    static void slots(String[] roles, int budget, int[] expect) {
        int[] s = SettlementDensity.roleSlots(budget, roles);
        check(budget + " people as " + String.join("/", roles) + ": " + Arrays.toString(s), Arrays.equals(s, expect),
                "expected " + Arrays.toString(expect));
    }

    static void check(String what, boolean ok, String detail) {
        if (ok) {
            pass++;
            System.out.println("  PASS " + what);
        } else {
            fail++;
            System.out.println("  FAIL " + what + "  <- " + detail);
        }
    }
}
