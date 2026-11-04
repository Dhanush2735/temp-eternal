import com.eternalengine.client.gui.TalkLayout;
import com.eternalengine.knowledge.TalkService;
import com.eternalengine.knowledge.TalkView;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;
import java.util.zip.ZipFile;

/**
 * Step 18c: the talk box on every screen size (probe_talk_layout.sh). Text is measured the way Minecraft 1.20.1
 * measures it, from the game's own font pictures (client-extra.jar): the width of a letter is its rightmost
 * coloured column plus one, the space is 4. Letters only in the wide fallback font (unifont, not in that jar)
 * count as 9, wider than they are, so the checks err on the safe side.
 *
 * <p>Views come from the real talk code (the Hyderabad 1948 pack and the history data) plus one made-up worst
 * case. For each screen size from 320 x 240 (the smallest Minecraft allows) to 1920 x 1080, it checks that nothing
 * leaves the screen or the box, nothing overlaps, the date is shown, and every label fits its button. It also draws
 * pictures of the box with the game's font (probes/out/talk_*.png) to look at.
 */
public final class TalkLayoutProbe {

    static final String JAR = "/home/user/.cache/gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client-extra.jar";
    static final String OUT = "/home/user/worldfill/probes/out";
    static int pass, fail;

    public static void main(String[] args) throws Exception {
        loadFont();
        System.out.println("Font: " + GLYPHS.size() + " letters from the game's font pictures; widths: \"◀ Back\" "
                + width("◀ Back") + ", \"Other topics\" " + width("Other topics") + ", \"Ask\" " + width("Ask")
                + ", \"Goodbye\" " + width("Goodbye") + ", \"Tuesday, 14 September 1948\" " + width("Tuesday, 14 September 1948"));

        Map<String, TalkView> views = views();
        int[][] sizes = {{320, 240}, {360, 240}, {400, 240}, {427, 240}, {455, 256}, {480, 270}, {512, 288},
                {569, 320}, {640, 360}, {683, 384}, {800, 450}, {960, 540}, {1280, 720}, {1920, 1080}, {480, 360}};

        // 1. The step-18 box at the user's size: why it went off the screen.
        TalkView opening = views.get("opening");
        TalkView backView = views.get("stress");
        int[] old = oldControlsEnd(480, opening);
        int[] oldBack = oldControlsEnd(480, backView);
        System.out.println("\nStep-18 box at 480 x 270 (1920 x 1080, automatic GUI scale): body " + old[2]
                + " wide; Goodbye ends at " + old[0] + " (with Back: " + oldBack[0] + ") on a screen 480 wide; date shown: "
                + (old[1] == 1 ? "yes" : "no"));
        check(old[0] > 480 || oldBack[0] > 480 || old[1] == 0, "the probe sees the user's problem in the step-18 box (off the edge or no date)",
                "Goodbye end " + old[0] + "/" + oldBack[0] + ", date " + old[1]);

        // 2. Every view on every size.
        int layouts = 0, shortened = 0, twoRows = 0, scrolled = 0, overHotbar = 0, compact = 0, dateBelow = 0, wholeBox = 0;
        List<String> problems = new ArrayList<>();
        List<String> realNotes = new ArrayList<>();
        for (int[] s : sizes) {
            for (Map.Entry<String, TalkView> e : views.entrySet()) {
                TalkLayout l = TalkLayout.of(s[0], s[1], TalkLayoutProbe::width, e.getValue(), 0);
                layouts++;
                for (String p : problems(l, e.getValue(), s[0], s[1], false)) {
                    problems.add(s[0] + "x" + s[1] + " " + e.getKey() + ": " + p);
                }
                for (TalkLayout.Box b : l.boxes) {
                    if (b.label().endsWith("…")) {
                        shortened++;
                    }
                }
                if (l.askY != firstControlY(l)) {
                    twoRows++;
                }
                if (l.scrollMax > 0) {
                    if (l.wholeBox) {
                        wholeBox++;
                    } else {
                        scrolled++;
                    }
                    // every scroll position checks out; scrolling to the end shows the last line; in the last resort
                    // every question, name and button can be reached at some position
                    java.util.Set<String> seen = new java.util.HashSet<>();
                    boolean askSeen = false;
                    for (int k = 0; k <= l.scrollMax; k++) {
                        TalkLayout at = TalkLayout.of(s[0], s[1], TalkLayoutProbe::width, e.getValue(), k);
                        for (String p : problems(at, e.getValue(), s[0], s[1], true)) {
                            problems.add(s[0] + "x" + s[1] + " " + e.getKey() + " (scroll " + k + "): " + p);
                        }
                        for (TalkLayout.Box b : at.boxes) {
                            seen.add(b.kind() + "#" + b.index());
                        }
                        askSeen |= at.askVisible;
                    }
                    TalkLayout end = TalkLayout.of(s[0], s[1], TalkLayoutProbe::width, e.getValue(), 999);
                    if (end.scroll != end.scrollMax || (!end.wholeBox && end.scroll + end.textShown != end.textLines)) {
                        problems.add(s[0] + "x" + s[1] + " " + e.getKey() + ": scrolling to the end stops at " + end.scroll
                                + " of " + end.scrollMax);
                    }
                    if (l.wholeBox) {
                        TalkView v = e.getValue();
                        int want = Math.min(9, v.options.size()) + v.names.size() + (v.canBack ? 4 : 3) + 1;
                        if (seen.size() != want || !askSeen) {
                            problems.add(s[0] + "x" + s[1] + " " + e.getKey() + ": scrolling reaches " + seen.size() + " of "
                                    + want + " things to click" + (askSeen ? "" : ", never the name box"));
                        }
                    }
                }
                if (!e.getKey().equals("stress")) {
                    int cut = 0;
                    for (TalkLayout.Box b : l.boxes) {
                        cut += b.label().endsWith("…") ? 1 : 0;
                    }
                    if (cut > 0 || l.scrollMax > 0 || l.compact || l.overHotbar) {
                        realNotes.add(s[0] + "x" + s[1] + " " + e.getKey() + ":" + (cut > 0 ? " " + cut + " label(s) with …" : "")
                                + (l.overHotbar ? " over the hotbar" : "") + (l.compact ? " packed" : "")
                                + (l.scrollMax > 0 ? (l.wholeBox ? " whole box scrolls" : " words scroll") : ""));
                    }
                }
                if (l.overHotbar) {
                    overHotbar++;
                }
                if (l.compact) {
                    compact++;
                }
                if (l.date.y() > l.name.y()) {
                    dateBelow++;
                }
            }
        }
        check(problems.isEmpty(), layouts + " layouts (" + views.size() + " views x " + sizes.length
                + " screen sizes): nothing off the screen or out of the box, nothing overlapping, the date always shown, every label fits",
                problems.size() + " problems, e.g. " + problems.subList(0, Math.min(8, problems.size())));
        System.out.println("   how they fitted: buttons in two rows " + twoRows + ", date on its own line " + dateBelow
                + ", over the hotbar " + overHotbar + ", rows packed tighter " + compact + ", words scrolled " + scrolled
                + ", whole box scrolled " + wholeBox
                + ", labels shortened with \"…\" " + shortened);

        System.out.println("   real screens (not the made-up worst case) that needed more than the plain layout: "
                + (realNotes.isEmpty() ? "none" : String.join("; ", realNotes)));

        // 3. The user's screen in detail.
        TalkLayout u = TalkLayout.of(480, 270, TalkLayoutProbe::width, opening, 0);
        int byeEnd = u.boxes.stream().filter(b -> b.kind() == TalkLayout.Kind.BYE).mapToInt(b -> b.x() + b.w()).max().orElse(-1);
        check(byeEnd > 0 && byeEnd <= u.x1 && u.x1 <= 480 && !u.date.text().isEmpty(),
                "at 480 x 270 Goodbye ends inside the box (" + byeEnd + " of " + u.x1 + ", screen 480) and the date shows (\""
                        + u.date.text() + "\")", "bye " + byeEnd + ", x1 " + u.x1 + ", date '" + u.date.text() + "'");
        check(u.portrait && u.x0 >= 4, "at 480 x 270 the box keeps the villager's portrait and starts at x " + u.x0
                + " (step 18: 144)", "portrait " + u.portrait + ", x0 " + u.x0);
        TalkLayout wide = TalkLayout.of(1280, 720, TalkLayoutProbe::width, opening, 0);
        check(wide.x0 == Math.max((int) (1280 * 0.30d), wide.x1 - 520) && wide.y1 == 720 - 30,
                "on a wide screen the box keeps its approved place (right side, above the hotbar), at most 520 wide",
                "x0 " + wide.x0 + ", x1 " + wide.x1 + ", y1 " + wide.y1);
        TalkLayout small = TalkLayout.of(320, 240, TalkLayoutProbe::width, views.get("stress"), 0);
        check(small.fits && small.y0 >= 0 && small.y1 <= 240, "the made-up worst case (9 long questions, 8 long names, a long text) fits 320 x 240"
                        + (small.wholeBox ? " with the whole box scrolling (" + (small.scrollMax + 1) + " positions)"
                        : small.textShown < small.textLines ? ", showing " + small.textShown + " of " + small.textLines
                        + " lines with scroll arrows" : ""), "fits " + small.fits);
        TalkLayout real = TalkLayout.of(320, 240, TalkLayoutProbe::width, views.get("where"), 0);
        check(!real.wholeBox && real.scrollMax == 0, "a real answer (\"where\", with Back and 8 names) shows whole on 320 x 240, nothing to scroll",
                "wholeBox " + real.wholeBox + ", scrollMax " + real.scrollMax);
        check(width(u.askHint) <= u.askW - 8 && !u.askHint.isEmpty(), "the grey hint in the name box fits it at 480 x 270 (\""
                + u.askHint + "\", step 18: \"Ask about a name…\" ran into the Ask button)", "hint '" + u.askHint + "', box " + u.askW);
        check(UNKNOWN.size() <= 1, "only " + UNKNOWN.size() + " letter(s) from the fallback font (counted 9 wide): "
                + names(UNKNOWN), names(UNKNOWN));

        // Step 21: the closing view ("Saleem has left.") on every screen size: only Goodbye and the close button, no
        // questions, no Other topics, no name box, and the box fits the screen.
        TalkView gone = TalkView.ended(opening.entityId, opening.npcName, opening.job, opening.level, opening.dateLabel,
                (opening.npcName.isBlank() ? "The person you were talking to" : opening.npcName) + " has left.");
        java.util.List<String> goneProblems = new java.util.ArrayList<>();
        for (int[] s : sizes) {
            TalkLayout g = TalkLayout.of(s[0], s[1], TalkLayoutProbe::width, gone, 0);
            long byes = g.boxes.stream().filter(b -> b.kind() == TalkLayout.Kind.BYE).count();
            long others = g.boxes.stream().filter(b -> b.kind() != TalkLayout.Kind.BYE && b.kind() != TalkLayout.Kind.CLOSE).count();
            int byeRight = g.boxes.stream().filter(b -> b.kind() == TalkLayout.Kind.BYE).mapToInt(b -> b.x() + b.w()).max().orElse(-1);
            if (byes != 1 || others != 0 || g.askVisible || !g.fits || g.y0 < 0 || g.y1 > s[1] || byeRight > g.x1
                    || g.words.isEmpty()) {
                goneProblems.add(s[0] + "x" + s[1] + ": Goodbye " + byes + ", other buttons " + others + ", name box "
                        + g.askVisible + ", fits " + g.fits);
            }
        }
        check(goneProblems.isEmpty(), "the closing view (\"" + gone.text + "\") on " + sizes.length + " screen sizes: only"
                + " Goodbye and the close button, no name box, the box on the screen", String.valueOf(goneProblems));

        // 4. Pictures.
        new File(OUT).mkdirs();
        draw(TalkLayout.of(480, 270, TalkLayoutProbe::width, opening, 0), opening, "talk_480x270_opening.png");
        draw(TalkLayout.of(480, 270, TalkLayoutProbe::width, gone, 0), gone, "talk_480x270_has_left.png");
        draw(TalkLayout.of(480, 270, TalkLayoutProbe::width, views.get("where"), 0), views.get("where"), "talk_480x270_where.png");
        draw(TalkLayout.of(320, 240, TalkLayoutProbe::width, views.get("stress"), 0), views.get("stress"), "talk_320x240_worst.png");
        draw(TalkLayout.of(320, 240, TalkLayoutProbe::width, views.get("stress"), 999), views.get("stress"), "talk_320x240_worst_end.png");
        draw(TalkLayout.of(320, 240, TalkLayoutProbe::width, views.get("where"), 0), views.get("where"), "talk_320x240_where.png");
        draw(TalkLayout.of(960, 540, TalkLayoutProbe::width, views.get("topics"), 0), views.get("topics"), "talk_960x540_topics.png");
        System.out.println("   pictures: " + OUT + "/talk_*.png");

        System.out.println("\nSUMMARY pass=" + pass + " fail=" + fail);
        System.exit(fail == 0 ? 0 : 1);
    }

    // ------------------------------------------------------------------ views

    static Map<String, TalkView> views() {
        Map<String, TalkView> m = new LinkedHashMap<>();
        TalkService.Ctx street = TalkService.context(null, null, -1, "Saleem", "merchant", 17.3616, 78.4747, 19480914, -1);
        m.put("opening", TalkService.open(street));
        m.put("where", TalkService.act(street, "ask", "polo", "where"));
        m.put("topics", TalkService.act(street, "topics", "", ""));
        m.put("referral", TalkService.act(street, "card", "laiq_ali", ""));
        TalkService.Ctx clerk = TalkService.context(null, null, -1, "Venkat Rao", "scribe", 17.3928, 78.4808, 19480917, -1);
        m.put("clerk", TalkService.open(clerk));
        // Step 22: "Where can I get something to keep notes in?" answered (no player here, so nothing is given).
        m.put("notes", TalkService.act(clerk, "topic", "notes", ""));
        TalkService.Ctx paris = TalkService.context(null, null, -1, "Jeanne", "citizen", 48.8566, 2.3522, 17890714, -1);
        m.put("paris topics", TalkService.act(paris, "topics", "", ""));
        m.put("stress", stress());
        // Step 19b: the merchant's goods and prices (the longest text so far) after a sale, with three offers, and
        // the money-changer with two. The offers are added by hand: the probe has no player carrying goods.
        TalkView sell = TalkService.act(street, "topic", "sell", "");
        sell.hint = "Sold 23 sheaves of wheat for 6 annas 5 pai. Your purse: 1 rupee 6 annas 5 pai (Osmania sicca).";
        sell.options.add(new TalkView.Option("sell", "TIMBER", "40:268", "Sell 40 logs: 1 rupee 6 annas 4 pai"));
        sell.options.add(new TalkView.Option("sell", "STONE", "128:134", "Sell 128 blocks of stone: 11 annas 2 pai"));
        sell.options.add(new TalkView.Option("sell", "GOLD_INGOT", "2:739", "Sell 16 loaves of bread: 1 rupee 1 anna 11 pai"));
        sell.canBack = true;
        m.put("merchant", sell);
        TalkService.Ctx changer = TalkService.context(null, null, -2, "Abdul Karim", "money_changer", 17.3616, 78.4747, 19480914, -1);
        TalkView swap = TalkService.act(changer, "topic", "swap", "");
        swap.hint = "Changed 3 dams (Mughal rupee) into 10 annas 9 pai (Osmania sicca). Your purse: 1 rupee 10 annas 9 pai (Osmania sicca).";
        swap.options.add(new TalkView.Option("swap", "osmania_sicca", "indian_rupee_anna:274", "Change into Indian rupee: 1 rupee 6 annas 3 pice 1 pie"));
        swap.options.add(new TalkView.Option("swap", "pound_lsd", "osmania_sicca:2926", "Change your pound sterling: 15 rupees 3 annas 10 pai"));
        swap.canBack = true;
        m.put("money-changer", swap);
        return m;
    }

    /** A made-up worst case: long name and job, a long text, a long hint, 9 long questions, 8 long names, Back. */
    static TalkView stress() {
        TalkView v = new TalkView();
        v.npcName = "Nawab Mir Mahboob Ali Khan Siddiqi Bahadur";
        v.job = "court chancellor of the Nizam's government";
        v.dateLabel = "Wednesday, 15 September 1948";
        v.text = "The fighting goes on. They say the army has taken [[suryapet|Suryapet]] in the east, and in the west it"
                + " has reached [[latur|Latur]]. My cousin came in from the station this morning; he says the trains to"
                + " the west stopped two days ago, and the telegraph office is full of people waiting for word from"
                + " their families. Nobody at the bazaar talks of anything else. Some say the [[un|United Nations]] will"
                + " stop it; others say it will be over before the week is out. Prices for rice have gone up by half"
                + " since Monday, and the shops near the [[charminar|Charminar]] close early now.";
        v.hint = "Suryapet: about 120 km east of here, past the old caravan road and the river crossing at Nalgonda";
        v.canBack = true;
        for (int i = 0; i < 9; i++) {
            v.options.add(new TalkView.Option("ask", "polo", "q" + i, "What do the people in the market say about it now that the army is near?"));
        }
        for (String n : new String[]{"Operation Polo", "Mir Laiq Ali", "General El Edroos", "Major General J. N. Chaudhuri",
                "Secunderabad", "King Kothi Palace", "United Nations Security Council in Paris", "Suryapet"}) {
            v.names.add(new TalkView.Name("x", n));
        }
        return v;
    }

    // ------------------------------------------------------------------ checks

    static int firstControlY(TalkLayout l) {
        return l.boxes.stream().filter(b -> b.kind() == TalkLayout.Kind.TOPICS).mapToInt(TalkLayout.Box::y).findFirst().orElse(l.askY);
    }

    record R(String what, int x, int y, int w, int h) {
    }

    static List<String> problems(TalkLayout l, TalkView v, int W, int H, boolean scrolled) {
        List<String> out = new ArrayList<>();
        List<R> rs = new ArrayList<>();
        for (TalkLayout.Box b : l.boxes) {
            rs.add(new R(b.kind() + (b.index() >= 0 ? "#" + (b.index() + 1) : ""), b.x(), b.y(), b.w(), b.h()));
        }
        if (l.askVisible) {
            rs.add(new R("name box", l.askX - 1, l.askY - 1, l.askW + 2, l.askH + 2)); // its border is drawn 1 outside
        }
        List<R> texts = new ArrayList<>();
        if (!l.name.text().isEmpty()) {
            texts.add(new R("name", l.name.x(), l.name.y(), l.name.w(), 9));
        }
        if (!l.job.text().isEmpty()) {
            texts.add(new R("job", l.job.x(), l.job.y(), l.job.w(), 9));
        }
        if (!l.date.text().isEmpty()) {
            texts.add(new R("date", l.date.x(), l.date.y(), l.date.w(), 9));
        }
        if (l.askAbout != null) {
            texts.add(new R("Ask about:", l.askAbout.x(), l.askAbout.y(), l.askAbout.w(), 9));
        }
        for (TalkLayout.Text t : l.hint) {
            texts.add(new R("hint", t.x(), t.y(), t.w(), 9));
        }
        for (TalkLayout.Word w : l.words) {
            texts.add(new R("word '" + w.text() + "'", w.x(), w.y(), w.w(), w.cardId() != null ? 10 : 9));
        }
        List<R> all = new ArrayList<>(rs);
        all.addAll(texts);
        boolean minimum = W >= 320 && H >= 240;
        if (minimum && !l.fits) {
            out.add("does not fit");
        }
        for (R r : all) {
            if (r.x() < 0 || r.y() < 0 || r.x() + r.w() > W || r.y() + r.h() > H) {
                out.add(r.what() + " leaves the screen " + r);
            }
            if (r.x() < l.x0 || r.x() + r.w() > l.x1 || r.y() < l.y0 || r.y() + r.h() > l.y1) {
                out.add(r.what() + " leaves the box " + r + " box " + l.x0 + "," + l.y0 + "-" + l.x1 + "," + l.y1);
            }
            if (!r.what().equals("CLOSE") && (r.x() < l.bodyX - 1 || r.x() + r.w() > l.bodyX + l.bodyW + 1)) {
                out.add(r.what() + " leaves the body " + r);
            }
        }
        for (int i = 0; i < all.size(); i++) {
            for (int j = i + 1; j < all.size(); j++) {
                R a = all.get(i), b = all.get(j);
                if (a.x() < b.x() + b.w() && b.x() < a.x() + a.w() && a.y() < b.y() + b.h() && b.y() < a.y() + a.h()) {
                    // two words on one line touch only if the layout put them over each other
                    out.add(a.what() + " overlaps " + b.what());
                }
            }
        }
        if (l.portrait && (l.portraitX + 46 > l.bodyX || l.portraitY + 75 > l.y1 || l.portraitY < l.y0)) {
            out.add("portrait out of place");
        }
        if (!v.dateLabel.isEmpty() && l.date.text().isEmpty() && !scrolled) {
            out.add("no date");
        }
        if (width(l.askHint) > l.askW - 8) {
            out.add("the name box hint '" + l.askHint + "' is wider than the box");
        }
        for (TalkLayout.Box b : l.boxes) {
            int need = switch (b.kind()) {
                case OPTION -> 5 + width(b.number()) + 4 + width(b.label()) + 4;
                case CHIP -> width(b.label()) + 10;
                case BACK, TOPICS, ASK, BYE -> width(b.label()) + 12;
                case CLOSE -> 0;
            };
            if (need > b.w()) {
                out.add(b.kind() + " label '" + b.label() + "' needs " + need + " > " + b.w());
            }
        }
        if (l.askW < 20) {
            out.add("name box only " + l.askW + " wide");
        }
        return out;
    }

    /** The step-18 placement of the buttons row: {Goodbye's right end, date shown 1/0, body width}. */
    static int[] oldControlsEnd(int W, TalkView v) {
        int margin = Math.max(6, W / 40);
        int x0 = W < 420 ? 6 : (int) (W * 0.30d);
        int x1 = W - margin;
        int portraitW = W < 360 ? 0 : 46;
        int bodyX = x0 + 6 + (portraitW > 0 ? portraitW + 8 : 0);
        int bodyW = x1 - 6 - bodyX;
        int bx = bodyX;
        if (v.canBack) {
            bx += width("◀ Back") + 12 + 4;
        }
        bx += width("Other topics") + 12 + 4;
        int byeW = width("Goodbye") + 12, askBtnW = width("Ask") + 12;
        int boxW = Math.max(60, bodyX + bodyW - bx - askBtnW - byeW - 8);
        bx += boxW + 4;
        bx += askBtnW + 4;
        int jx = bodyX + width(v.npcName) + 6;
        boolean date = jx + width(v.job) + 10 + width(v.dateLabel) < x1 - 22;
        return new int[]{bx + byeW, date ? 1 : 0, bodyW};
    }

    static void check(boolean ok, String what, String detail) {
        if (ok) {
            pass++;
            System.out.println("PASS " + what);
        } else {
            fail++;
            System.out.println("FAIL " + what + "\n     " + detail);
        }
    }

    static String names(Set<Integer> cps) {
        StringBuilder b = new StringBuilder();
        for (int cp : cps) {
            b.append(new String(Character.toChars(cp))).append(String.format(" (U+%04X) ", cp));
        }
        return b.toString().trim();
    }

    // ------------------------------------------------------------------ the game's font

    record Glyph(BufferedImage img, int x, int y, int cw, int ch, float scale, int ascent, int advance) {
    }

    static final Map<Integer, Glyph> GLYPHS = new HashMap<>();
    static final Map<Integer, Integer> SPACES = new HashMap<>();
    static final Set<Integer> UNKNOWN = new TreeSet<>();

    static void loadFont() throws Exception {
        try (ZipFile z = new ZipFile(JAR)) {
            for (JsonElement p : json(z, "assets/minecraft/font/include/space.json").getAsJsonArray("providers")) {
                for (Map.Entry<String, JsonElement> e : p.getAsJsonObject().getAsJsonObject("advances").entrySet()) {
                    SPACES.put(e.getKey().codePointAt(0), e.getValue().getAsInt());
                }
            }
            for (JsonElement pe : json(z, "assets/minecraft/font/include/default.json").getAsJsonArray("providers")) {
                JsonObject p = pe.getAsJsonObject();
                if (!"bitmap".equals(p.get("type").getAsString())) {
                    continue;
                }
                String file = p.get("file").getAsString();
                String path = "assets/minecraft/textures/" + file.substring(file.indexOf(':') + 1);
                BufferedImage img;
                try (InputStream in = z.getInputStream(z.getEntry(path))) {
                    img = ImageIO.read(in);
                }
                JsonArray rows = p.getAsJsonArray("chars");
                int height = p.has("height") ? p.get("height").getAsInt() : 8;
                int ascent = p.get("ascent").getAsInt();
                int[][] cps = new int[rows.size()][];
                for (int r = 0; r < rows.size(); r++) {
                    cps[r] = rows.get(r).getAsString().codePoints().toArray();
                }
                int cw = img.getWidth() / cps[0].length, ch = img.getHeight() / cps.length;
                float scale = (float) height / ch;
                for (int r = 0; r < cps.length; r++) {
                    for (int c = 0; c < cps[r].length; c++) {
                        int cp = cps[r][c];
                        if (cp == 0 || GLYPHS.containsKey(cp) || SPACES.containsKey(cp)) {
                            continue; // the first font that has a letter wins, as in the game
                        }
                        int advance = (int) (0.5d + actualWidth(img, cw, ch, c, r) * scale) + 1;
                        GLYPHS.put(cp, new Glyph(img, c * cw, r * ch, cw, ch, scale, ascent, advance));
                    }
                }
            }
        }
    }

    static JsonObject json(ZipFile z, String path) throws Exception {
        try (InputStream in = z.getInputStream(z.getEntry(path))) {
            return JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
        }
    }

    /** As Minecraft's BitmapProvider: the rightmost column with any visible pixel, plus one. */
    static int actualWidth(BufferedImage img, int cw, int ch, int col, int row) {
        for (int i = cw - 1; i >= 0; i--) {
            for (int k = 0; k < ch; k++) {
                if ((img.getRGB(col * cw + i, row * ch + k) >>> 24) != 0) {
                    return i + 1;
                }
            }
        }
        return 0;
    }

    static int width(String s) {
        int w = 0;
        for (int cp : s.codePoints().toArray()) {
            Integer sp = SPACES.get(cp);
            if (sp != null) {
                w += sp;
                continue;
            }
            Glyph g = GLYPHS.get(cp);
            if (g != null) {
                w += g.advance();
            } else {
                UNKNOWN.add(cp);
                w += 9;
            }
        }
        return w;
    }

    // ------------------------------------------------------------------ pictures

    static final int S = 3;
    static BufferedImage img;

    static void fill(int x0, int y0, int x1, int y1, int argb) {
        int a = argb >>> 24;
        if (a == 0) {
            return;
        }
        for (int y = y0 * S; y < y1 * S; y++) {
            for (int x = x0 * S; x < x1 * S; x++) {
                if (x < 0 || y < 0 || x >= img.getWidth() || y >= img.getHeight()) {
                    continue;
                }
                img.setRGB(x, y, blend(img.getRGB(x, y), argb));
            }
        }
    }

    static int blend(int dst, int src) {
        int a = src >>> 24;
        int r = (((src >> 16) & 255) * a + ((dst >> 16) & 255) * (255 - a)) / 255;
        int g = (((src >> 8) & 255) * a + ((dst >> 8) & 255) * (255 - a)) / 255;
        int b = ((src & 255) * a + (dst & 255) * (255 - a)) / 255;
        return 0xFF000000 | (r << 16) | (g << 8) | b;
    }

    static void outline(int ax, int ay, int bx, int by, int c) {
        fill(ax, ay, bx, ay + 1, c);
        fill(ax, by - 1, bx, by, c);
        fill(ax, ay, ax + 1, by, c);
        fill(bx - 1, ay, bx, by, c);
    }

    static void text(String s, int x, int y, int color, boolean shadow) {
        if (shadow) {
            text(s, x + 1, y + 1, (color & 0xFF000000) | ((color & 0xFCFCFC) >> 2), false);
        }
        int cx = x;
        for (int cp : s.codePoints().toArray()) {
            Integer sp = SPACES.get(cp);
            if (sp != null) {
                cx += sp;
                continue;
            }
            Glyph g = GLYPHS.get(cp);
            if (g == null) {
                outline(cx + 1, y, cx + 8, y + 7, color);
                cx += 9;
                continue;
            }
            int top = y + 7 - g.ascent();
            for (int gy = 0; gy < g.ch(); gy++) {
                for (int gx = 0; gx < g.cw(); gx++) {
                    int px = g.img().getRGB(g.x() + gx, g.y() + gy);
                    if ((px >>> 24) == 0) {
                        continue;
                    }
                    double sc = g.scale();
                    int fx0 = (int) Math.floor((cx + gx * sc) * S), fy0 = (int) Math.floor((top + gy * sc) * S);
                    int fx1 = (int) Math.floor((cx + (gx + 1) * sc) * S), fy1 = (int) Math.floor((top + (gy + 1) * sc) * S);
                    for (int yy = fy0; yy < fy1; yy++) {
                        for (int xx = fx0; xx < fx1; xx++) {
                            if (xx >= 0 && yy >= 0 && xx < img.getWidth() && yy < img.getHeight()) {
                                img.setRGB(xx, yy, blend(img.getRGB(xx, yy), color));
                            }
                        }
                    }
                }
            }
            cx += g.advance();
        }
    }

    /** The box as TalkScreen.render draws it, over a plain world, with the hotbar and hearts. */
    static void draw(TalkLayout l, TalkView v, String file) throws Exception {
        int W = l.width, H = l.height;
        img = new BufferedImage(W * S, H * S, BufferedImage.TYPE_INT_ARGB);
        fill(0, 0, W, H * 6 / 10, 0xFF79A6FF);
        fill(0, H * 6 / 10, W, H, 0xFF5E8C3B);
        // hotbar, hearts and food, as the game places them
        int hx = W / 2 - 91;
        fill(hx, H - 22, hx + 182, H, 0xFF2A2A2A);
        outline(hx, H - 22, hx + 182, H, 0xFF000000);
        for (int i = 0; i < 9; i++) {
            outline(hx + 1 + i * 20, H - 21, hx + 21 + i * 20, H - 1, 0xFF8B8B8B);
        }
        fill(hx, H - 29, hx + 182, H - 24, 0xFF305020);
        for (int i = 0; i < 10; i++) {
            fill(hx + i * 8, H - 39, hx + i * 8 + 7, H - 32, 0xFFD02020);
            fill(hx + 182 - 9 - i * 8 + 1, H - 39, hx + 182 - 9 - i * 8 + 8, H - 32, 0xFFB07030);
        }
        // the box
        fill(l.x0, l.y0, l.x1, l.y1, 0xE60E0E12);
        outline(l.x0, l.y0, l.x1, l.y1, 0xFF000000);
        outline(l.x0 + 1, l.y0 + 1, l.x1 - 1, l.y1 - 1, 0x29FFFFFF);
        if (l.portrait) {
            int px = l.portraitX, py = l.portraitY;
            fill(px, py, px + 46, py + 75, 0xFF8B8B8B);
            fill(px, py, px + 46, py + 1, 0xFF373737);
            fill(px, py, px + 1, py + 75, 0xFF373737);
            fill(px, py + 74, px + 46, py + 75, 0xFFFFFFFF);
            fill(px + 45, py, px + 46, py + 75, 0xFFFFFFFF);
            fill(px + 17, py + 10, px + 29, py + 22, 0xFFB98A64); // head
            fill(px + 15, py + 22, px + 31, py + 46, 0xFF3C5A8C); // body
            fill(px + 15, py + 46, px + 31, py + 69, 0xFF4A3A2A); // legs
        }
        text(l.name.text(), l.name.x(), l.name.y(), 0xFFFFFF55, true);
        text(l.job.text(), l.job.x(), l.job.y(), 0xFFA8A8B0, false);
        text(l.date.text(), l.date.x(), l.date.y(), 0xFF9A9AA4, false);
        for (TalkLayout.Word w : l.words) {
            int c = w.cardId() == null ? 0xFFF4F4F4 : 0xFFFFD75E;
            text(w.text(), w.x(), w.y(), c, true);
            if (w.cardId() != null) {
                for (int dx = 0; dx < w.w(); dx += 2) {
                    fill(w.x() + dx, w.y() + 9, w.x() + dx + 1, w.y() + 10, c);
                }
            }
        }
        if (l.moreBelow) {
            for (int i = 0; i < 3; i++) {
                fill(l.arrowX + 2 - i, l.arrowDownY + 2 - i, l.arrowX + 3 + i, l.arrowDownY + 3 - i, 0xFF9A9AA4);
            }
        }
        if (l.moreAbove) {
            for (int i = 0; i < 3; i++) {
                fill(l.arrowX + 2 - i, l.arrowUpY + i, l.arrowX + 3 + i, l.arrowUpY + i + 1, 0xFF9A9AA4);
            }
        }
        for (TalkLayout.Text t : l.hint) {
            text(t.text(), t.x(), t.y(), 0xFF9A9AA4, false);
        }
        if (l.askAbout != null) {
            text(l.askAbout.text(), l.askAbout.x(), l.askAbout.y(), 0xFF9A9AA4, false);
        }
        for (TalkLayout.Box b : l.boxes) {
            int ty = b.y() + (b.h() - 8) / 2;
            switch (b.kind()) {
                case OPTION -> {
                    fill(b.x(), b.y(), b.x() + b.w(), b.y() + b.h(), 0xFF6F6F6F);
                    outline(b.x(), b.y(), b.x() + b.w(), b.y() + b.h(), 0xFF000000);
                    fill(b.x() + 1, b.y() + 1, b.x() + b.w() - 1, b.y() + 2, 0xFFA0A0A0);
                    fill(b.x() + 1, b.y() + b.h() - 2, b.x() + b.w() - 1, b.y() + b.h() - 1, 0xFF464646);
                    text(b.number(), b.x() + 5, ty, 0xFFC8C8C8, true);
                    text(b.label(), b.x() + 5 + width(b.number()) + 4, ty, 0xFFFFFFFF, true);
                }
                case CHIP -> {
                    fill(b.x(), b.y(), b.x() + b.w(), b.y() + b.h(), 0x12FFD75E);
                    outline(b.x(), b.y(), b.x() + b.w(), b.y() + b.h(), 0xFF6B5A2A);
                    text(b.label(), b.x() + 5, b.y() + 2, 0xFFFFD75E, false);
                }
                case BACK, TOPICS, ASK, BYE -> {
                    fill(b.x(), b.y(), b.x() + b.w(), b.y() + b.h(), 0xFF5F5F5F);
                    outline(b.x(), b.y(), b.x() + b.w(), b.y() + b.h(), 0xFF000000);
                    text(b.label(), b.x() + 6, ty, 0xFFFFFFFF, true);
                }
                case CLOSE -> {
                    outline(b.x(), b.y(), b.x() + b.w(), b.y() + b.h(), 0xFF555555);
                    text(b.label(), b.x() + 3, b.y() + 2, 0xFFDDDDDD, false);
                }
            }
        }
        // the box to type a name, as the game's EditBox draws it (its border 1 outside)
        if (l.askVisible) {
            fill(l.askX - 1, l.askY - 1, l.askX + l.askW + 1, l.askY + l.askH + 1, 0xFFA0A0A0);
            fill(l.askX, l.askY, l.askX + l.askW, l.askY + l.askH, 0xFF000000);
            text(l.askHint, l.askX + 4, l.askY + (l.askH - 8) / 2, 0xFF808080, true);
        }
        if (l.ruleY >= 0) {
            fill(l.bodyX, l.ruleY, l.bodyX + l.bodyW, l.ruleY + 1, 0x1FFFFFFF);
        }
        ImageIO.write(img, "png", new File(OUT, file));
    }
}
