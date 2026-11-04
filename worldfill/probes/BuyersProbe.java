import com.eternalengine.civilization.HistoricalPresence;
import com.eternalengine.civilization.HistoryGazetteer;
import com.eternalengine.civilization.SettlementRank;
import com.eternalengine.knowledge.KnowledgeDate;
import com.eternalengine.knowledge.TalkService;
import com.eternalengine.knowledge.TalkView;
import com.eternalengine.money.GoodsTable;
import com.eternalengine.money.MarketService;
import com.eternalengine.money.MoneyFormat;
import com.eternalengine.money.MoneyTable;
import com.eternalengine.money.ProductAtlas;
import com.eternalengine.population.SettlementDensity;

import java.util.Arrays;
import java.util.List;

/**
 * Step 19g: somebody buys in every settled place (a merchant in a city, a trader in a town, a pedlar in a village with
 * money, anybody where people swap), buyers take the atlas products, and the talk screen says so. The mod's real code
 * and data, no server (the trade screen's items need the game: see TEST_CHECKLIST step 13). Run by
 * worldfill/probe_buyers.sh. Exit code 1 if a check fails.
 */
public final class BuyersProbe {
    private static int pass;
    private static int fail;
    private static final MarketService.Terms T = MarketService.Terms.DEFAULT;

    public static void main(String[] args) {
        MoneyTable table = MoneyTable.get();

        System.out.println("1. The rules");
        String self = MarketService.selfTest();
        check("the market's own check passes (with step 19g's part)", self == null, String.valueOf(self));
        check("terms: merchant 70 in 100 and 8 days' pay; trader 60 and 4; pedlar 50 and 2; anybody 50 and 1; the"
                        + " trader keeps 10 in 100 of any money he changes",
                T.as("merchant") == T && T.as(MarketService.TRADER).equals(new MarketService.Terms(60, 4, 10, 10))
                        && T.as(MarketService.PEDLAR).equals(new MarketService.Terms(50, 2, 10, 10))
                        && T.as(MarketService.LOCAL).equals(new MarketService.Terms(50, 1, 10, 10)),
                T.as(MarketService.TRADER) + " " + T.as(MarketService.PEDLAR) + " " + T.as(MarketService.LOCAL));
        check("buyers and changers: merchant, trader, pedlar buy; money-changer and trader change money",
                MarketService.buyer("merchant") && MarketService.buyer("trader") && MarketService.buyer("Pedlar")
                        && !MarketService.buyer("farmer") && !MarketService.buyer("money_changer")
                        && MarketService.changes("money_changer") && MarketService.changes("trader")
                        && !MarketService.changes("pedlar") && !MarketService.changes("merchant"), "");
        String[] slots = {"farmer", "pedlar", "town_crier"};
        int[] s5 = SettlementDensity.roleSlots(5, slots);
        int[] s2 = SettlementDensity.roleSlots(2, slots);
        check("a village of 5 has one pedlar and one crier (" + Arrays.toString(s5) + "); a village of 2 only farmers ("
                + Arrays.toString(s2) + ")", Arrays.equals(s5, new int[] {3, 1, 1}) && Arrays.equals(s2, new int[] {2, 0, 0}),
                "");

        System.out.println("\n2. The people of real places");
        roles("Hyderabad 1948 (a city)", 17.3616, 78.4747, 1948, "merchant,money_changer", "trader,pedlar");
        roles("Kothapalle 1948 (a village with money)", 18.87, 79.43, 1948, "pedlar", "merchant,trader,money_changer");
        String[] kothapalle = HistoricalPresence.query(null, 18.87, 79.43, 1948).spawnRoles();
        check("in Kothapalle the pedlar stands before the crier: " + String.join(",", kothapalle),
                Arrays.equals(kothapalle, new String[] {"farmer", "pedlar", "town_crier"}), "");
        roles("Harappa 2500 BCE (a city where people swap)", 30.63, 72.86, -2500, "merchant", "money_changer,trader,pedlar");
        roles("the Deccan 3000 BCE (a village where people swap)", 17.36, 78.47, -3000, "", "merchant,trader,pedlar");
        check("in the Deccan in 3000 BCE anybody swaps a little", MarketService.swapsALittle(
                HistoricalPresence.query(null, 17.36, 78.47, -3000).spawnRoles(), table.at(17.36, 78.47, -3000)), "");
        double[] town = townSite(1500);
        check("a town in 1500 has a trader: " + (town == null ? "none found" : String.format("%.3f, %.3f", town[0], town[1])),
                town != null, "");
        double[] camp = campNear(-33.87, 151.21, 1500);
        boolean campSwaps = camp != null && MarketService.swapsALittle(
                HistoricalPresence.query(null, camp[0], camp[1], 1500).spawnRoles(), table.at(camp[0], camp[1], 1500));
        check("a camp near Sydney in 1500: anybody swaps a little"
                + (camp == null ? " (no camp found)" : String.format(" (%.2f, %.2f)", camp[0], camp[1])), campSwaps, "");
        check("deep in the Siberian forest in 3000 BCE nobody lives, so nobody buys",
                !HistoricalPresence.query(null, 62.0, 100.0, -3000).occupied(), "");
        int[] count = sample(new int[] {-2000, 0, 1500, 1948});
        check("every sampled settled place has somebody who buys (" + count[0] + " places: " + count[1] + " traders, "
                + count[2] + " pedlars, " + count[3] + " where anybody swaps)", count[4] == 0 && count[0] > 500,
                count[4] + " with nobody");

        System.out.println("\n3. Atlas products bought back");
        MoneyTable.Here bombay = table.at(18.94, 72.83, 1948);
        List<GoodsTable.Good> atlas = MarketService.atlasGoods(18.94, 72.83, 1948);
        GoodsTable.Good paper = MarketService.atlasGood(MarketService.ATLAS + "paper", 18.94, 72.83, 1948);
        String paperPrice = paper == null ? "none" : MarketService.priceEntry(paper,
                MarketService.pays(paper, bombay, "market", T), bombay.money(), 1948);
        check("a merchant in Bombay in 1948 takes " + atlas.size() + " atlas products, paper among them (" + paperPrice + ")",
                atlas.size() >= 10 && paper != null && paper.want() == 32, names(atlas));
        boolean cheaper = true;
        for (GoodsTable.Good g : atlas) {
            double pays = MarketService.pays(g, bombay, "market", T);
            double worth = MarketService.worth(g, bombay, MarketService.enginePrice(g.id(), "market"));
            cheaper &= pays > 0 && pays < worth && Math.abs(pays - 0.7d * worth) < 1e-9;
        }
        check("he always pays 70 in 100 of what a seller asks, never more", cheaper, "");
        ProductAtlas.Answer brought = null;
        for (ProductAtlas.Answer a : ProductAtlas.get().forSale(MarketService.MERCHANT, 17.3616, 78.4747, 1948)) {
            if (a.status() == ProductAtlas.Status.BROUGHT) {
                brought = a;
            }
        }
        if (brought != null) {
            GoodsTable.Good far = MarketService.atlasGood(brought);
            GoodsTable.Good near = MarketService.atlasGood(new ProductAtlas.Answer(brought.product(),
                    ProductAtlas.Status.MADE_HERE, brought.since(), ""));
            MoneyTable.Here hyd = table.at(17.3616, 78.4747, 1948);
            double a = MarketService.pays(far, hyd, "market", T);
            double b = MarketService.pays(near, hyd, "market", T);
            check("brought from far (" + brought.product().shortName() + " in Hyderabad in 1948), an item fetches twice as"
                    + " much", Math.abs(a - 2 * b) < 1e-9, a + " vs " + b);
        } else {
            check("something is brought from far to Hyderabad in 1948", false, "nothing brought");
        }
        List<GoodsTable.Good> harappa = MarketService.atlasGoods(30.63, 72.86, -2500);
        check("in Harappa in 2500 BCE no paper, no iron axes (" + names(harappa) + ")",
                MarketService.atlasGood(MarketService.ATLAS + "paper", 30.63, 72.86, -2500) == null
                        && MarketService.atlasGood(MarketService.ATLAS + "iron_tools", 30.63, 72.86, -2500) == null, "");
        check("buyers count atlas goods in their own words (16 sheets of paper, 1 iron axe)",
                paper != null && paper.count(16).equals("16 sheets of paper") && "1 iron axe".equals(
                        MarketService.atlasGood(MarketService.ATLAS + "iron_tools", 18.94, 72.83, 1948) == null ? ""
                                : MarketService.atlasGood(MarketService.ATLAS + "iron_tools", 18.94, 72.83, 1948).count(1)),
                paper == null ? "" : paper.count(16));

        System.out.println("\n4. The talk screen (no player, no villager: views only)");
        int d1948 = KnowledgeDate.key(1948, 9, 14);
        TalkService.Ctx merchant = TalkService.context(null, null, -1, "Saleem", "merchant", 17.3616, 78.4747, d1948, -1);
        TalkView ms = TalkService.act(merchant, "topic", "sell", "");
        check("a city merchant: \"I buy wheat, ... gold and emeralds, and things people here make or bring in: ...\"",
                ms.text.startsWith("I buy wheat, bread, logs, stone, coal, iron, copper, wool, gold and emeralds, and things"
                        + " people here make or bring in: ") && ms.text.contains(" more. I pay 4 annas 5 pai for 16 sheaves"),
                ms.text);
        if (town != null) {
            int d1500 = KnowledgeDate.key(1500, 6, 1);
            TalkService.Ctx trader = TalkService.context(null, null, -2, "Hans", "trader", town[0], town[1], d1500, -1);
            TalkView tg = TalkService.open(trader);
            TalkView ts = TalkService.act(trader, "topic", "sell", "");
            TalkView tx = TalkService.act(trader, "topic", "swap", "");
            TalkView me = TalkService.act(trader, "topic", "self", "");
            boolean barter = table.at(town[0], town[1], 1500).money().barter();
            // Step 24: selling, swapping and changing are on Minecraft's trade screen ("Let's trade."); the talk keeps one
            // question about his prices.
            check("a town trader (" + tg.job + "): \"Let's trade.\" (the trade screen: his goods, yours, money) and \""
                            + (barter ? "What do you swap for?" : "What do you buy?") + "\" first",
                    tg.job.equals("trader") && tg.options.size() >= 2 && tg.options.get(0).action().equals("trade")
                            && tg.options.get(0).label().equals("Let's trade.")
                            && tg.options.get(1).label().equals(barter ? "What do you swap for?" : "What do you buy?")
                            && !has(tg, "Who buys goods here?") && !has(tg, "Who changes money here?")
                            && !has(tg, "Can you change my money?"), tg.options.toString());
            check("he buys for the town market for less: \"" + cut(ts.text, 70) + "\"",
                    ts.text.startsWith("I buy for the market of this town, so I pay a little less than a city merchant."),
                    ts.text);
            check("he changes money keeping 10 in 100: \"" + cut(tx.text, 70) + "\"", barter
                    ? tx.text.startsWith("Coins are only metal here.")
                    : tx.text.contains(" and keep 10 in every 100, whatever the money."), tx.text);
            check("he says who he is: \"" + cut(me.text, 90) + "\"",
                    me.text.startsWith("I am Hans, a trader. I buy and sell for the market of this town, and I change money."),
                    me.text);
        }
        TalkService.Ctx pedlar = TalkService.context(null, null, -3, "Mallesh", "pedlar", 18.87, 79.43, d1948, -1);
        TalkView pg = TalkService.open(pedlar);
        TalkView ps = TalkService.act(pedlar, "topic", "sell", "");
        TalkView px = TalkService.act(pedlar, "topic", "swap", "");
        check("a village pedlar: \"Let's trade.\", \"What do you buy?\", and \"Who changes money here?\"",
                pg.job.equals("pedlar") && pg.options.get(0).action().equals("trade")
                        && pg.options.get(1).label().equals("What do you buy?") && has(pg, "Who changes money here?")
                        && !has(pg, "Can you change my money?"), pg.options.toString());
        check("he pays less than a town trader and changes no money: \"" + cut(ps.text, 60) + "\"",
                ps.text.startsWith("I carry what I buy to the towns, so I pay less than a trader there.")
                        && px.text.startsWith("I don't change money."), ps.text + " | " + px.text);
        int d3000 = KnowledgeDate.key(-3000, 6, 1);
        TalkService.Ctx farmer = TalkService.context(null, null, -4, "Kavi", "farmer", 17.36, 78.47, d3000, -1);
        TalkView fg = TalkService.open(farmer);
        TalkView fs = TalkService.act(farmer, "topic", "sell", "");
        check("where people swap and nobody trades, a farmer swaps a little: \"Let's swap goods.\" (the trade screen) first",
                fg.options.get(0).label().equals("Let's swap goods.") && fg.options.get(0).action().equals("trade")
                        && !has(fg, "Who buys goods here?"), fg.options.toString());
        check("\"" + cut(fs.text, 80) + "\"", fs.text.startsWith("I can swap a little. I swap my goods for "), fs.text);
        TalkService.Ctx citizen = TalkService.context(null, null, -5, "Ramaiah", "citizen", 17.3616, 78.4747, d1948, -1);
        TalkView cw = TalkService.act(citizen, "topic", "market", "");
        check("with nobody near who buys, no wrong hint about towns: \"" + cw.text + "\"",
                cw.text.equals("Nobody near here buys goods. Every town and city has a market, and pedlars go round the"
                        + " villages.") && !cw.text.contains("bigger town"), cw.text);
        TalkView pw = TalkService.act(pedlar, "topic", "market", "");
        check("asked who changes money, the pedlar names a city money-changer or a town trader: \"" + pw.text + "\"",
                pw.text.equals("Nobody near here changes money. A money-changer in a city will, or a trader in a town market."),
                pw.text);
        TalkService.Ctx bronzeTrader = TalkService.context(null, null, -6, "Ur-Nanshe", "trader", 30.63, 72.86,
                KnowledgeDate.key(-2500, 6, 1), -1);
        TalkView bg = TalkService.open(bronzeTrader);
        TalkView bx = TalkService.act(bronzeTrader, "topic", "swap", "");
        check("a trader where people swap: \"Let's trade.\" and \"What do you swap for?\"; he takes coins as metal",
                has(bg, "Let's trade.") && has(bg, "What do you swap for?")
                        && bx.text.startsWith("Coins are only metal here. I take them for goods, by what they buy, and keep 10"),
                bg.options + " | " + bx.text);
        MoneyTable.Here h2500 = table.at(30.63, 72.86, -2500);
        MarketService.Swap metal = MarketService.swapOffer(table, table.money("osmania_sicca"), 192, h2500.money(), -2500,
                T.as(MarketService.TRADER));
        check("1 O.S. rupee taken as metal in 2500 BCE: " + MoneyFormat.amount(h2500.money(), metal.result(), -2500),
                metal.result() > 0 && !metal.fixed() && metal.fee() == 10, "");

        System.out.println("\n" + pass + " passed, " + fail + " failed");
        System.exit(fail == 0 ? 0 : 1);
    }

    /** The first gazetteer town of the year whose spot gets a trader, as {lat, lon}; null when none. */
    static double[] townSite(int year) {
        HistoryGazetteer gaz = HistoryGazetteer.get();
        int tried = 0;
        for (HistoryGazetteer.Site s : gaz.allSites()) {
            if (!s.occupiedIn(year) || s.rankAt(year) != SettlementRank.TOWN) {
                continue;
            }
            if (++tried > 400) {
                break;
            }
            String[] roles = HistoricalPresence.query(null, s.lat(), s.lon(), year).spawnRoles();
            if (Arrays.asList(roles).contains(MarketService.TRADER)) {
                return new double[] {s.lat(), s.lon()};
            }
        }
        return null;
    }

    /** An occupied tile within half a degree, as {lat, lon}; null when none. */
    static double[] campNear(double lat, double lon, int year) {
        for (double dl = -0.5; dl <= 0.5; dl += 0.05) {
            for (double dn = -0.5; dn <= 0.5; dn += 0.05) {
                if (HistoricalPresence.query(null, lat + dl, lon + dn, year).occupied()) {
                    return new double[] {lat + dl, lon + dn};
                }
            }
        }
        return null;
    }

    /** {places, traders, pedlars, anybody swaps, nobody} over every 17th gazetteer site in these years. */
    static int[] sample(int[] years) {
        HistoryGazetteer gaz = HistoryGazetteer.get();
        MoneyTable table = MoneyTable.get();
        List<HistoryGazetteer.Site> sites = gaz.allSites();
        int[] out = new int[5];
        for (int y : years) {
            for (int i = 0; i < sites.size(); i += 17) {
                HistoryGazetteer.Site s = sites.get(i);
                if (!s.occupiedIn(y)) {
                    continue;
                }
                String[] roles = MarketService.withTrader(gaz.spawnRoles(s, y), s.rankAt(y), s.lat(), s.lon(), y);
                out[0]++;
                boolean buyer = false;
                for (String r : roles) {
                    if (MarketService.buyer(r)) {
                        buyer = true;
                        out[1] += r.equals(MarketService.TRADER) ? 1 : 0;
                        out[2] += r.equals(MarketService.PEDLAR) ? 1 : 0;
                    }
                }
                if (!buyer && MarketService.swapsALittle(roles, table.at(s.lat(), s.lon(), y))) {
                    buyer = true;
                    out[3]++;
                }
                out[4] += buyer ? 0 : 1;
            }
        }
        return out;
    }

    static void roles(String name, double lat, double lon, int year, String must, String mustNot) {
        String[] roles = HistoricalPresence.query(null, lat, lon, year).spawnRoles();
        List<String> list = Arrays.asList(roles);
        boolean ok = true;
        for (String r : must.split(",")) {
            ok &= r.isEmpty() || list.contains(r);
        }
        for (String r : mustNot.split(",")) {
            ok &= r.isEmpty() || !list.contains(r);
        }
        check(name + ": " + String.join(", ", roles), ok, "must have " + must + ", must not have " + mustNot);
    }

    static String names(List<GoodsTable.Good> goods) {
        StringBuilder b = new StringBuilder();
        for (GoodsTable.Good g : goods) {
            b.append(b.length() == 0 ? "" : ", ").append(g.name());
        }
        return b.toString();
    }

    static boolean has(TalkView v, String label) {
        for (TalkView.Option o : v.options) {
            if (o.label().equals(label)) {
                return true;
            }
        }
        return false;
    }

    static String cut(String s, int n) {
        return s.length() <= n ? s : s.substring(0, n) + "...";
    }

    static void check(String what, boolean ok, String detail) {
        if (ok) {
            pass++;
            System.out.println("  PASS " + what);
        } else {
            fail++;
            System.out.println("  FAIL " + what + (detail == null || detail.isEmpty() ? "" : " -- " + detail));
        }
    }
}
