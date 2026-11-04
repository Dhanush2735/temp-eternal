import com.eternalengine.client.gui.paint.BookPainter;
import com.eternalengine.client.gui.paint.Canvas;
import com.eternalengine.client.gui.paint.MapPainter;
import com.eternalengine.client.gui.paint.PaperPainter;
import com.eternalengine.client.gui.paint.TradeMenuPainter;
import com.eternalengine.client.gui.paint.TradePainter;
import com.eternalengine.money.Denominations;
import com.eternalengine.money.TradeRules;
import com.eternalengine.knowledge.BookService;
import com.eternalengine.knowledge.BookView;
import com.eternalengine.knowledge.KnowledgeCard;
import com.eternalengine.knowledge.KnowledgeDate;
import com.eternalengine.knowledge.KnowledgePacks;
import com.eternalengine.knowledge.PlayerKnowledge;
import com.eternalengine.money.GoodsTable;
import com.eternalengine.money.MarketService;
import com.eternalengine.money.MoneyFormat;
import com.eternalengine.money.MoneyTable;
import com.eternalengine.money.ShopService;
import com.eternalengine.money.TradeView;
import com.eternalengine.news.MapService;
import com.eternalengine.news.MapView;
import com.eternalengine.news.NewsEras;
import com.eternalengine.news.NewsService;
import com.eternalengine.news.PaperView;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.zip.ZipFile;

/**
 * Steps 19c to 19f without a game: the news and shop checks with the mod's real code and data (who brings the news,
 * prices, money taken, today's papers in five places, maps), and the trade, newspaper and map screens drawn with the
 * game's own font (from TalkLayoutProbe) into probes/out/screen_*.png at 480 x 270 (the user's 1920 x 1080 screen) and
 * smaller. Every element must stay on the screen. Exit code 1 if a check fails.
 */
public class ScreenProbe {

    static int fails;
    static int sw, sh;
    static int minX, minY, maxX, maxY;
    static final Map<String, BufferedImage> ICONS = new HashMap<>();

    public static void main(String[] args) throws Exception {
        TalkLayoutProbe.loadFont();
        new File(TalkLayoutProbe.OUT).mkdirs();

        // ------------------------------------------------------------------ data checks
        check(NewsEras.selfTest() == null, "who brings the news: " + NewsEras.selfTest());
        check(ShopService.selfTest() == null, "shops: " + ShopService.selfTest());
        check(MapService.selfTest() == null, "map: " + MapService.selfTest());

        int d14 = KnowledgeDate.key(1948, 9, 14), d15 = KnowledgeDate.key(1948, 9, 15), d17 = KnowledgeDate.key(1948, 9, 17);
        PaperView p14 = NewsService.paper(17.3616, 78.4747, d14, false);
        print(p14);
        KnowledgePacks.Pack pack = KnowledgePacks.covering(17.3616, 78.4747, d14).get(0);
        String first = "";
        int packStories = 0;
        for (KnowledgePacks.PaperDay d : pack.papers()) {
            if (d.date() == d14) {
                first = d.stories().get(0).headline();
                packStories = d.stories().size();
            }
        }
        check("The Evening Herald".equals(p14.name), "the Hyderabad paper is the Evening Herald: " + p14.name);
        // The check used to demand "TUESDAY, 14 SEPTEMBER 1948". That was the probe being stale, not
        // the paper: NewsService.dateLine(lat, lon, date) dates a paper in the calendar its own place
        // uses (step 37, A2 - a Hyderabad paper of 1948 was written in Fasli 1358), and offers a
        // weekday only where the place dates by a Christian calendar. The line must carry the Fasli
        // date, the price, and the year of the rule counted from the start of the rule.
        check(p14.line.contains("Fasli 1358") && p14.line.contains("Bhadrapada") && p14.line.contains("1 ANNA")
                && !p14.line.contains("first year of Hyderabad State rule"), "the date line: " + p14.line);
        check(!p14.stories.isEmpty() && p14.stories.get(0).headline().equals(first), "the pack's lead story comes first: "
                + (p14.stories.isEmpty() ? "none" : p14.stories.get(0).headline()));
        int placed = 0, places = 0;
        for (int i = 0; i < Math.min(packStories, p14.stories.size()); i++) {
            for (String pl : p14.stories.get(i).places()) {
                places++;
                placed += NewsService.placeAt(pl) != null ? 1 : 0;
            }
        }
        check(places > 0 && placed == places, "every place in the pack's stories is on the map: " + placed + " of " + places);
        check(p14.prices.size() >= 3 && !p14.ad.isBlank(), "prices and the map advertisement: " + p14.prices + " / " + p14.ad);

        PaperView p15 = NewsService.paper(17.3616, 78.4747, d15, false);
        print(p15);
        boolean noThisYear = true;
        for (PaperView.Story s : p15.stories) {
            noThisYear &= !s.text().endsWith("This year.");
        }
        check(!p15.stories.isEmpty() && noThisYear, "15 September (no paper in the pack): no story of an event that starts in"
                + " 1948, which might not have happened yet");

        PaperView hand = NewsService.paper(17.3616, 78.4747, KnowledgeDate.key(1700, 3, 1), true);
        print(hand);
        check(hand.handwritten && hand.stories.size() <= 3 && hand.line.contains("WRITTEN BY HAND") && hand.prices.isEmpty(),
                "a handwritten newsletter in Hyderabad in 1700: few stories, no prices: " + hand.line);
        PaperView rome = NewsService.paper(41.8925, 12.4853, KnowledgeDate.key(100, 6, 1), true);
        print(rome);
        PaperView london = NewsService.paper(51.5074, -0.1278, KnowledgeDate.key(1851, 5, 1), false);
        print(london);
        check(london.name.equals("The London News") && !london.stories.isEmpty(), "London in 1851: " + london.name);
        PaperView london1800 = NewsService.paper(51.5074, -0.1278, KnowledgeDate.key(1800, 5, 1), false);
        check(london1800.name.equals("The London Gazette"), "London in 1800 has a Gazette: " + london1800.name);
        List<String> crier = NewsService.crierLines(18.87, 79.43, d17);
        System.out.println("Crier at Kothapalle on 17 Sep 1948: " + crier);
        check(!crier.isEmpty(), "the town crier in a Telangana village has news on 17 September 1948");

        // Money: a paper and a map in Hyderabad in 1948, at a few other places and years.
        Object[][] prices = {{17.3616, 78.4747, 1948}, {51.5074, -0.1278, 1800}, {51.5074, -0.1278, 1900},
                {41.8925, 12.4853, 100}, {17.3616, 78.4747, 1700}};
        for (Object[] p : prices) {
            double lat = (double) p[0], lon = (double) p[1];
            int y = (int) p[2];
            MoneyTable.Here here = MoneyTable.get().at(lat, lon, y);
            long paper = Math.max(1L, Math.round(here.dayPay() * NewsEras.paperDays(y)));
            long letter = Math.max(1L, Math.round(here.dayPay() * NewsEras.newsletterDays()));
            long map = Math.max(1L, Math.round(here.dayPay() * NewsEras.mapDays(true)));
            System.out.println("Prices at " + lat + "," + lon + " in " + y + ": paper " + MoneyFormat.amount(here.money(), paper, y)
                    + ", newsletter " + MoneyFormat.amount(here.money(), letter, y) + ", map " + MoneyFormat.amount(here.money(), map, y)
                    + " (a day's pay " + MoneyFormat.amount(here.money(), here.dayPay(), y) + ")");
        }

        // Maps.
        MapView hydMap = MapService.view(mapTag(17.3616, 78.4747, d14, "Map of Hyderabad State", marks(pack)), new double[]{17.3616, 78.4747});
        check(hydMap.towns.size() == 24 && hydMap.roads.size() == 2 && hydMap.marks.size() >= 8, "the Hyderabad State map: "
                + hydMap.towns.size() + " towns, " + hydMap.roads.size() + " roads, " + hydMap.marks.size() + " marks");
        MapView romeMap = MapService.view(mapTag(41.8925, 12.4853, KnowledgeDate.key(100, 6, 1), "Map of the land around Rome",
                new ListTag()), new double[]{41.8925, 12.4853});
        System.out.println("Rome 100: " + romeMap.towns.size() + " towns, " + romeMap.roads.size() + " roads; " + names(romeMap));
        check(romeMap.towns.size() >= 10 && romeMap.roads.size() >= 5, "the map around Rome in 100 has towns and Roman roads");
        MapView kodad = MapService.view(mapTag(16.9978, 79.9653, KnowledgeDate.key(1700, 1, 1), "Map of the land around Kodad",
                new ListTag()), null);
        System.out.println("Kodad 1700: " + kodad.towns.size() + " towns, " + kodad.roads.size() + " roads; " + names(kodad));
        MapView london1900 = MapService.view(mapTag(51.5074, -0.1278, KnowledgeDate.key(1900, 1, 1), "Map of the land around London",
                new ListTag()), null);
        System.out.println("London 1900: " + london1900.towns.size() + " towns, " + london1900.roads.size() + " roads; " + names(london1900));

        // ------------------------------------------------------------------ the screens
        TradeView papers = tradePapers(d14);
        TradeView goods = tradeGoods(d14);
        // Step 20: the history book (notes with the time traveller view, the journal, a family tree, an empty book).
        BookView[] books = books(pack, d14);
        check(books[0].notes.size() >= 3 && books[0].canTrack && !books[0].later.isEmpty() && books[1].journal.size() >= 20
                && !books[2].tree.isEmpty() && books[3].entries.isEmpty(), "the history book views: " + books[0].notes.size()
                + " notes about " + books[0].title + ", " + books[1].journal.size() + " journal lines, " + books[2].tree.size()
                + " people in the family tree, an empty book");
        int[][] sizes = {{480, 270}, {320, 240}, {640, 360}};
        for (int[] s : sizes) {
            String tag = s[0] + "x" + s[1];
            String[] bookNames = {"book_notes_", "book_journal_", "book_tree_", "book_empty_"};
            for (int b = 0; b < books.length; b++) {
                BookView bv = books[b];
                BookPainter.State bs = new BookPainter.State();
                screen(s, bookNames[b] + tag, c -> BookPainter.paint(c, bv, bs, sw, sh, -1, -1));
                if (b == 0) {
                    bs.rightScroll = 100000;
                    bs.leftScroll = 100000;
                    screen(s, "book_notes_end_" + tag, c -> BookPainter.paint(c, bv, bs, sw, sh, -1, -1));
                    check(bs.rightScroll == bs.maxRight && bs.leftScroll == bs.maxLeft, "book_notes_end_" + tag
                            + ": scrolling stops at the end (" + bs.rightScroll + " of " + bs.maxRight + ")");
                    BookPainter.State fs = new BookPainter.State();
                    fs.filter = "niz";
                    screen(s, "book_find_" + tag, c -> BookPainter.paint(c, bv, fs, sw, sh, -1, -1));
                }
            }
            // Step 24: the trade screen is Minecraft's (TradeProbe draws it with coins in its slots).
            TradeView pv = rowsOf(papers, 17.3616, 78.4747, 1948, 0);
            screen(s, "trade_papers_" + tag, c -> tradeScreen(c, pv, sw, sh, null));
            TradeView gv = rowsOf(goods, 17.3616, 78.4747, 1948, -1);
            for (int i = 0; i < gv.rows.size(); i++) {
                if (gv.rows.get(i).id().equals("prod:osmania_biscuits")) {
                    gv.selected = i;
                }
            }
            screen(s, "trade_goods_" + tag, c -> tradeScreen(c, gv, sw, sh, null));
            PaperPainter.State ps = new PaperPainter.State();
            PaperView read = NewsService.paper(17.3616, 78.4747, d14, false);
            read.note = "Names in this paper are now in your history book, and its places are marked on your map.";
            screen(s, "paper_" + tag, c -> PaperPainter.paint(c, read, ps, sw, sh, -1, -1));
            int max = ps.maxScroll;
            if (s[0] == 480) {
                ps.scroll = max;
                screen(s, "paper_end_" + tag, c -> PaperPainter.paint(c, read, ps, sw, sh, -1, -1));
                check(max > 0, "the Hyderabad paper is longer than the screen at 480 x 270 and scrolls (" + max + ")");
                PaperPainter.State hs = new PaperPainter.State();
                screen(s, "letter_" + tag, c -> PaperPainter.paint(c, hand, hs, sw, sh, -1, -1));
            }
            MapPainter.State ms = new MapPainter.State();
            ms.selected = "Naldurg";
            screen(s, "map_" + tag, c -> MapPainter.paint(c, hydMap, ms, sw, sh, -1, -1, true));
            if (s[0] == 480) {
                MapPainter.State rs = new MapPainter.State();
                screen(s, "map_rome_" + tag, c -> MapPainter.paint(c, romeMap, rs, sw, sh, -1, -1, false));
            }
        }
        System.out.println(fails == 0 ? "ALL SCREEN CHECKS PASSED" : fails + " SCREEN CHECK(S) FAILED");
        System.exit(fails == 0 ? 0 : 1);
    }

    /** Step 20: books from the Hyderabad pack: notes (time traveller on), the journal, the family tree, an empty book. */
    static BookView[] books(KnowledgePacks.Pack pack, int date) {
        PlayerKnowledge pk = new PlayerKnowledge();
        java.util.UUID who = new java.util.UUID(20L, 2L);
        int n = 0;
        for (KnowledgeCard c : pack.cards().values()) {
            pk.heard(who, c.id(), c.title(), c.kind());
            boolean ask = n++ < 8 || c.id().equals("nizam") || c.id().equals("asaf_jahi");
            if (!ask) {
                continue;
            }
            for (KnowledgeCard.Question q : c.questions()) {
                KnowledgeCard.Answer a = q.at(date);
                if (a != null) {
                    pk.note(who, c.id(), c.title(), c.kind(), new PlayerKnowledge.Note(date,
                            q.level() >= 2 ? "Venkat Rao, court clerk" : "Saleem, paper seller", q.id(), a.text()));
                }
            }
        }
        for (int i = 0; i < 30; i++) {
            pk.journal(who, date - (i / 3), "Learned about something from somebody in the bazaar, number " + i + ".",
                    i % 3 == 0 ? "nizam" : "");
        }
        double[] at = {17.3616, 78.4747};
        return new BookView[] {
                BookService.build(pk, who, at, date, "nizam", "notes", "Your compass now points to King Kothi.", true),
                BookService.build(pk, who, at, date, "nizam", "journal", "", false),
                BookService.build(pk, who, at, date, "asaf_jahi", "tree", "", false),
                BookService.build(new PlayerKnowledge(), who, at, date, "", "notes", "", false)};
    }

    interface Paint {
        List<TradePainter.Hot> run(Canvas c);
    }

    static void screen(int[] size, String name, Paint p) throws Exception {
        sw = size[0];
        sh = size[1];
        TalkLayoutProbe.img = new BufferedImage(sw * TalkLayoutProbe.S, sh * TalkLayoutProbe.S, BufferedImage.TYPE_INT_ARGB);
        TalkLayoutProbe.fill(0, 0, sw, sh, 0xFF5B7A52); // grass, the world behind the screen
        minX = minY = Integer.MAX_VALUE;
        maxX = maxY = Integer.MIN_VALUE;
        List<TradePainter.Hot> hots = p.run(new ProbeCanvas());
        for (TradePainter.Hot h : hots) {
            track(h.x0(), h.y0());
            track(h.x1(), h.y1());
        }
        boolean inside = minX >= 0 && minY >= 0 && maxX <= sw && maxY <= sh;
        check(inside, name + ": everything on the screen (" + minX + "," + minY + " to " + maxX + "," + maxY + " in " + sw
                + "x" + sh + ")");
        ImageIO.write(TalkLayoutProbe.img, "png", new File(TalkLayoutProbe.OUT, "screen_" + name + ".png"));
    }

    static void track(int x, int y) {
        minX = Math.min(minX, x);
        minY = Math.min(minY, y);
        maxX = Math.max(maxX, x);
        maxY = Math.max(maxY, y);
    }

    /** The game's font and fills, through TalkLayoutProbe. */
    static final class ProbeCanvas implements Canvas {
        @Override
        public void fill(int x0, int y0, int x1, int y1, int argb) {
            track(x0, y0);
            track(x1, y1);
            TalkLayoutProbe.fill(x0, y0, x1, y1, argb);
        }

        @Override
        public void text(String s, int x, int y, int argb, boolean shadow) {
            if (s.isEmpty()) {
                return;
            }
            track(x, y);
            track(x + width(s), y + 8);
            TalkLayoutProbe.text(s, x, y, argb, shadow);
        }

        @Override
        public void textScaled(String s, int x, int y, int argb, float scale) {
            track(x, y);
            track(x + (int) (width(s) * scale), y + (int) (8 * scale));
            int w = width(s) + 2, h = 10;
            BufferedImage keep = TalkLayoutProbe.img;
            BufferedImage tmp = new BufferedImage(w * TalkLayoutProbe.S, h * TalkLayoutProbe.S, BufferedImage.TYPE_INT_ARGB);
            TalkLayoutProbe.img = tmp;
            TalkLayoutProbe.text(s, 0, 0, argb, false);
            TalkLayoutProbe.img = keep;
            java.awt.Graphics2D g = keep.createGraphics();
            g.drawImage(tmp, x * TalkLayoutProbe.S, y * TalkLayoutProbe.S, (int) (w * TalkLayoutProbe.S * scale),
                    (int) (h * TalkLayoutProbe.S * scale), null);
            g.dispose();
        }

        @Override
        public int width(String s) {
            return TalkLayoutProbe.width(s);
        }

        @Override
        public void blit(String texture, int x, int y, int u, int v, int w, int h, int texW, int texH) {
            track(x, y);
            track(x + w, y + h);
            BufferedImage tex = texture(texture);
            if (tex == null) {
                TalkLayoutProbe.fill(x, y, x + w, y + h, 0xFF8B8B8B);
                return;
            }
            double fx = tex.getWidth() / (double) texW;
            double fy = tex.getHeight() / (double) texH;
            BufferedImage part = tex.getSubimage((int) (u * fx), (int) (v * fy), (int) Math.max(1, w * fx),
                    (int) Math.max(1, h * fy));
            java.awt.Graphics2D g = TalkLayoutProbe.img.createGraphics();
            g.setRenderingHint(java.awt.RenderingHints.KEY_INTERPOLATION,
                    java.awt.RenderingHints.VALUE_INTERPOLATION_NEAREST_NEIGHBOR);
            int S = TalkLayoutProbe.S;
            g.drawImage(part, x * S, y * S, w * S, h * S, null);
            g.dispose();
        }

        @Override
        public void item(String id, int count, int x, int y, int scale) {
            track(x, y);
            track(x + 16 * scale, y + 16 * scale);
            BufferedImage icon = icon(id);
            java.awt.Graphics2D g = TalkLayoutProbe.img.createGraphics();
            int S = TalkLayoutProbe.S;
            if (icon != null) {
                g.drawImage(icon, x * S, y * S, 16 * scale * S, 16 * scale * S, null);
            } else {
                g.setColor(java.awt.Color.MAGENTA);
                g.fillRect(x * S, y * S, 16 * scale * S, 16 * scale * S);
            }
            g.dispose();
            if (count > 1 && scale == 1) {
                String n = String.valueOf(count);
                TalkLayoutProbe.text(n, x + 17 - width(n), y + 9, 0xFFFFFFFF, true);
            }
        }
    }

    static final Map<String, BufferedImage> TEXTURES = new HashMap<>();

    /** A picture of the game ("minecraft:textures/gui/...png") from its own files. */
    static BufferedImage texture(String id) {
        return TEXTURES.computeIfAbsent(id, k -> {
            String ns = k.substring(0, k.indexOf(':')), path = k.substring(k.indexOf(':') + 1);
            try (ZipFile z = new ZipFile(TalkLayoutProbe.JAR)) {
                var e = z.getEntry("assets/" + ns + "/" + path);
                if (e != null) {
                    try (InputStream in = z.getInputStream(e)) {
                        BufferedImage raw = ImageIO.read(in);
                        BufferedImage argb = new BufferedImage(raw.getWidth(), raw.getHeight(), BufferedImage.TYPE_INT_ARGB);
                        java.awt.Graphics2D g = argb.createGraphics();
                        g.drawImage(raw, 0, 0, null);
                        g.dispose();
                        return argb;
                    }
                }
            } catch (Exception ignored) {
                // A grey box.
            }
            return null;
        });
    }

    static BufferedImage icon(String id) {
        return ICONS.computeIfAbsent(id, k -> {
            String ns = k.substring(0, k.indexOf(':')), name = k.substring(k.indexOf(':') + 1);
            try {
                if (ns.equals("eternalengine")) {
                    return ImageIO.read(new File("/home/user/eternal/src/main/resources/assets/eternalengine/textures/item/"
                            + name + ".png"));
                }
                try (ZipFile z = new ZipFile(TalkLayoutProbe.JAR)) {
                    for (String path : new String[]{"assets/minecraft/textures/item/" + name + ".png",
                            "assets/minecraft/textures/block/" + name + ".png"}) {
                        var e = z.getEntry(path);
                        if (e != null) {
                            try (InputStream in = z.getInputStream(e)) {
                                return ImageIO.read(in);
                            }
                        }
                    }
                }
            } catch (Exception ignored) {
                // A magenta square.
            }
            return null;
        });
    }

    static TradeView tradePapers(int date) {
        TradeView v = new TradeView();
        v.npcName = "Saleem Qureshi";
        v.title = v.npcName + "'s paper stand";
        v.dateLabel = KnowledgeDate.label(date);
        v.says = "Papers and maps! Have a look.";
        v.purse = "Your purse: 1 rupee (Osmania sicca)";
        PaperView p = NewsService.paper(17.3616, 78.4747, date, false);
        v.offers.add(new TradeView.Offer("paper", "eternalengine:newspaper", 1, p.name + ", 14 Sep 1948", "Today's paper",
                "Today's news. Its names go into your history book, and its places onto your map.", "1 anna", 12, -1, false));
        v.offers.add(new TradeView.Offer("map", "eternalengine:map", 1, "Map of Hyderabad State", "Map of the state",
                "Towns and main roads. It also marks the places from every paper you read while you carry it.", "8 annas", 96,
                -1, true));
        return v;
    }

    static TradeView tradeGoods(int date) {
        TradeView v = new TradeView();
        v.npcName = "Ramesh Goud";
        v.title = v.npcName + "'s goods";
        v.dateLabel = KnowledgeDate.label(date);
        v.says = "Bought 8 × Osmania biscuits for 1 anna. Your purse: 15 annas (Osmania sicca).";
        v.purse = "Your purse: 15 annas (Osmania sicca); 3 rupees 2 annas (Indian rupee)";
        MoneyTable.Here here = MoneyTable.get().at(17.3616, 78.4747, 1948);
        String[] items = {"minecraft:wheat", "minecraft:bread", "minecraft:oak_log", "minecraft:stone", "minecraft:coal",
                "minecraft:iron_ingot", "minecraft:copper_ingot", "minecraft:white_wool", "minecraft:gold_ingot",
                "minecraft:emerald"};
        int i = 0;
        for (GoodsTable.Good g : GoodsTable.get().all()) {
            if (g.items().isEmpty() || i >= items.length) {
                continue;
            }
            double each = MarketService.worth(g, here, MarketService.basePrice(g.id()));
            int q = ShopService.lotSize(each, here.money(), 1948);
            long price = Math.max(1L, (long) Math.ceil(each * q - 1e-9));
            boolean coal = g.id().equals("COAL");
            v.offers.add(new TradeView.Offer("good:" + g.id(), items[i++], Math.min(64, q),
                    coal ? q + " × Singareni coal" : cap(g.some(q)), coal ? "Singareni coal" : cap(g.name()),
                    (coal ? "Coal from the Singareni mines, first worked in 1889. " : "") + "He has " + Math.max(1, g.want() / q)
                            + " lots like this a day; he buys it back for less.",
                    MoneyFormat.amount(here.money(), price, 1948), price, g.id().equals("GOLD_INGOT") ? 0 : 3, false));
        }
        for (ShopService.Product p : ShopService.products()) {
            if (!p.item().startsWith("minecraft:") || !p.here(17.3616, 78.4747, 1948)) {
                continue;
            }
            long price = Math.max(1L, Math.round(p.days() * here.dayPay()));
            v.offers.add(new TradeView.Offer("prod:" + p.id(), p.item(), p.count(), (p.count() > 1 ? p.count() + " × " : "")
                    + p.name(), p.shortName(), p.lore(), MoneyFormat.amount(here.money(), price, 1948), price, 4, false));
        }
        System.out.println("Merchant in Hyderabad, 14 Sep 1948, sells: " + offersText(v));
        return v;
    }

    /**
     * Step 24: a seller's wares as rows of Minecraft's trade screen: the price in pieces (two kinds at most, "+" when it
     * takes more), an arrow, the thing.
     */
    static TradeView rowsOf(TradeView wares, double lat, double lon, int year, int selected) {
        MoneyTable table = MoneyTable.get();
        MoneyTable.Here here = table.at(lat, lon, year);
        TradeView v = new TradeView();
        v.npcName = wares.npcName;
        v.title = wares.title;
        v.dateLabel = wares.dateLabel;
        v.says = wares.says;
        v.purse = wares.purse.replace("Your purse: ", "Your money: ");
        v.status = "";
        for (TradeView.Offer o : wares.offers) {
            MoneyTable.Money m = o.money().isEmpty() ? here.money() : table.money(o.money());
            List<long[]> split = Denominations.split(TradeRules.pieces(table, m, year), o.price());
            TradeView.Stack c1 = split.isEmpty() ? TradeView.Stack.NONE : pieceStack(table, m, year, split.get(0));
            TradeView.Stack c2 = split.size() < 2 ? TradeView.Stack.NONE : pieceStack(table, m, year, split.get(1));
            v.rows.add(new TradeView.Row(o.id(), TradeView.Kind.BUY, c1, c2, split.size() > 2,
                    new TradeView.Stack(o.item(), o.count(), null), false, o.name(), o.priceText(), o.lore(), o.left(),
                    o.owned()));
        }
        v.selected = selected;
        return v;
    }

    static TradeView.Stack pieceStack(MoneyTable table, MoneyTable.Money m, int year, long[] vn) {
        for (Denominations.Piece p : TradeRules.pieces(table, m, year)) {
            if (p.value() == vn[0]) {
                return new TradeView.Stack("eternalengine:" + p.form().itemId, (int) Math.min(9999, vn[1]), null);
            }
        }
        return TradeView.Stack.NONE;
    }

    /**
     * Step 24: Minecraft's trade screen at the middle of the screen, as the game puts it, with what the game itself draws
     * in its slots ({@code slots}: the two slots, the result, then the inventory row by row and the hotbar; null: empty).
     */
    static List<TradePainter.Hot> tradeScreen(Canvas c, TradeView v, int sw, int sh, TradeView.Stack[] slots) {
        int left = (sw - TradeMenuPainter.W) / 2;
        int top = (sh - TradeMenuPainter.H) / 2;
        TradeMenuPainter.State st = new TradeMenuPainter.State();
        if (v.selected >= TradeMenuPainter.ROWS) {
            st.scroll = Math.min(v.selected - 3, TradeMenuPainter.maxScroll(v));
        }
        List<TradePainter.Hot> hots = TradeMenuPainter.paint(c, v, st, left, top, sw, sh, -1, -1, "Trades", "Inventory");
        if (slots != null) {
            int[][] at = new int[3 + 36][];
            at[0] = new int[] {136, 37};
            at[1] = new int[] {162, 37};
            at[2] = new int[] {220, 37};
            for (int r = 0; r < 3; r++) {
                for (int col = 0; col < 9; col++) {
                    at[3 + r * 9 + col] = new int[] {108 + col * 18, 84 + r * 18};
                }
            }
            for (int col = 0; col < 9; col++) {
                at[30 + col] = new int[] {108 + col * 18, 142};
            }
            for (int i = 0; i < slots.length && i < at.length; i++) {
                if (slots[i] != null && !slots[i].isEmpty()) {
                    c.stack(slots[i], left + at[i][0], top + at[i][1]);
                }
            }
        }
        return hots;
    }

    static String offersText(TradeView v) {
        List<String> out = new ArrayList<>();
        for (TradeView.Offer o : v.offers) {
            out.add(o.name() + " " + o.priceText());
        }
        return String.join("; ", out);
    }

    static String cap(String s) {
        return s.isEmpty() ? s : Character.toUpperCase(s.charAt(0)) + s.substring(1);
    }

    static CompoundTag mapTag(double lat, double lon, int date, String title, ListTag marks) {
        CompoundTag t = new CompoundTag();
        t.putString("title", title);
        t.putDouble("lat", lat);
        t.putDouble("lon", lon);
        t.putInt("year", KnowledgeDate.year(date));
        t.putInt("date", date);
        t.putString("home", "");
        t.put("marks", marks);
        return t;
    }

    /** The marks the pack's six papers would leave on a map. */
    static ListTag marks(KnowledgePacks.Pack pack) {
        ListTag list = new ListTag();
        for (KnowledgePacks.PaperDay d : pack.papers()) {
            PaperView p = NewsService.paper(17.3616, 78.4747, d.date(), false);
            for (PaperView.Story s : p.stories) {
                for (String pl : s.places()) {
                    double[] at = NewsService.placeAt(pl);
                    if (at == null) {
                        continue;
                    }
                    CompoundTag c = new CompoundTag();
                    c.putString("name", NewsService.placeName(pl));
                    c.putDouble("lat", at[0]);
                    c.putDouble("lon", at[1]);
                    c.putInt("date", d.date());
                    c.putString("headline", s.headline());
                    c.putString("paper", p.name);
                    list.add(c);
                }
            }
        }
        return list;
    }

    static String names(MapView v) {
        List<String> n = new ArrayList<>();
        for (MapView.Town t : v.towns) {
            n.add(t.name() + (t.major() ? "*" : ""));
        }
        return String.join(", ", n.subList(0, Math.min(25, n.size())));
    }

    static void print(PaperView p) {
        System.out.println("PAPER " + p.name + " | " + p.line + (p.fork.isBlank() ? "" : " | " + p.fork));
        for (PaperView.Story s : p.stories) {
            System.out.println("   * " + s.headline() + ": " + com.eternalengine.knowledge.TalkView.plain(s.text())
                    + (s.places().isEmpty() ? "" : "  " + s.places()));
        }
        if (!p.prices.isEmpty()) {
            System.out.println("   $ " + p.pricesTitle + ": " + String.join("; ", p.prices));
        }
        if (!p.ad.isBlank()) {
            System.out.println("   ad: " + p.ad);
        }
    }

    static void check(boolean ok, String what) {
        System.out.println((ok ? "  OK   " : "  FAIL ") + what);
        if (!ok) {
            fails++;
        }
    }
}
