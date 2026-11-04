import com.eternalengine.knowledge.KnowledgeCard;
import com.eternalengine.knowledge.KnowledgeDate;
import com.eternalengine.knowledge.KnowledgePacks;
import com.eternalengine.knowledge.PlayerKnowledge;
import com.eternalengine.knowledge.TalkService;
import com.eternalengine.knowledge.TalkView;
import io.netty.buffer.Unpooled;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Step 18: the villager talk, without Minecraft running. Uses the real knowledge pack, the real history
 * data and the mod's TalkService, the same code the talk screen and /ee talk use.
 *
 * Exit code 1 if any check fails.
 */
public class KnowledgeProbe {

    static int pass, fail;
    static final List<String> failures = new ArrayList<>();
    static final double CHARMINAR_LAT = 17.3616, CHARMINAR_LON = 78.4747;
    static final double KING_KOTHI_LAT = 17.3928, KING_KOTHI_LON = 78.4808;

    public static void main(String[] args) {
        long t0 = System.currentTimeMillis();
        packs();
        dates();
        street1948();
        court();
        future();
        allAnswers();
        noSources();
        elsewhere();
        bce();
        wire();
        notes();
        back();
        terraDays();
        everyDay();
        beforeTheEvent();
        System.out.printf(Locale.ROOT, "%nKnowledgeProbe: %d passed, %d failed (%.1f s)%n", pass, fail,
                (System.currentTimeMillis() - t0) / 1000.0);
        for (String f : failures) {
            System.out.println("  FAIL " + f);
        }
        System.exit(fail == 0 ? 0 : 1);
    }

    static void check(boolean ok, String what, String detail) {
        if (ok) {
            pass++;
            System.out.println("  ok   " + what);
        } else {
            fail++;
            failures.add(what + " :: " + detail);
            System.out.println("  FAIL " + what + "\n       " + detail);
        }
    }

    static TalkService.Ctx street(int date) {
        return TalkService.context(null, null, -1, "Saleem", "merchant", CHARMINAR_LAT, CHARMINAR_LON, date, -1);
    }

    static TalkService.Ctx clerk(int date) {
        return TalkService.context(null, null, -1, "Venkat Rao", "scribe", KING_KOTHI_LAT, KING_KOTHI_LON, date, -1);
    }

    static String say(TalkService.Ctx c, String action, String a, String b) {
        TalkView v = TalkService.act(c, action, a, b);
        return v == null ? "" : v.plainText();
    }

    static void packs() {
        System.out.println("\n1. The knowledge packs");
        List<KnowledgePacks.Pack> all = KnowledgePacks.all();
        check(all.size() == 1 && KnowledgePacks.loadProblems().isEmpty(), "one pack loads without problems",
                all.size() + " packs, problems " + KnowledgePacks.loadProblems());
        KnowledgePacks.Pack p = all.isEmpty() ? null : all.get(0);
        check(p != null && p.cards().size() == 28 && p.news().size() == 14 && p.papers().size() == 6,
                "Hyderabad 1948: 28 cards, 14 news lines (the preview's 12 and two for 15 September), 6 newspapers",
                p == null ? "none" : p.cards().size() + " / " + p.news().size() + " / " + p.papers().size());
        List<String> problems = p == null ? List.of("no pack") : KnowledgePacks.validate(p);
        check(problems.isEmpty(), "every link, distance, track and topic leads to a card", String.valueOf(problems));
        check(p != null && p.covers(CHARMINAR_LAT, CHARMINAR_LON, 19480914) && !p.covers(48.8566, 2.3522, 19480914)
                        && !p.covers(CHARMINAR_LAT, CHARMINAR_LON, 19500101),
                "the pack covers Hyderabad in 1948, not Paris, not 1950", "covers wrong");
    }

    static void dates() {
        System.out.println("\n2. Dates");
        boolean round = true;
        String bad = "";
        for (int year : new int[]{1948, 1949, 2000, 1900, -44, -250}) {
            for (int d = 1; d <= KnowledgeDate.daysIn(year); d++) {
                int key = KnowledgeDate.fromDayOfYear(year, d);
                if (KnowledgeDate.dayOfYear(key) != d || KnowledgeDate.year(key) != year) {
                    round = false;
                    bad = year + " day " + d + " -> " + key;
                }
            }
        }
        check(round, "day of year <-> date, for leap years, 1900, 2000 and BCE years", bad);
        // Step 18d: /ee date with the Eternal Engine clock moves the calendar's starting point (WorldCalendar.anchorFor);
        // today is that point plus the Minecraft days since (dateAt). Every day of 1948 and 1949, at three times of
        // day, at each speed, must read back as itself.
        boolean clock = true;
        String cbad = "";
        for (int speed : new int[]{1, 5, 10, 25, 50}) {
            for (int year : new int[]{1948, 1949}) {
                for (int d = 1; d <= KnowledgeDate.daysIn(year); d++) {
                    int key = KnowledgeDate.fromDayOfYear(year, d);
                    for (long t : new long[]{0L, 7000L, 23999L}) {
                        long now = 1806020L * 24000L + t;
                        long[] a = com.eternalengine.clock.WorldCalendar.anchorFor(key, now, speed);
                        int got = com.eternalengine.clock.WorldCalendar.dateAt((int) a[0], a[1], speed, now);
                        if (got != key) {
                            clock = false;
                            cbad = "speed " + speed + " " + key + " at " + t + " reads back " + got;
                        }
                    }
                }
            }
        }
        check(clock, "/ee date: the day set on the calendar reads back as the same day (1x, 5x, 10x, 25x, 50x)", cbad);
        check(KnowledgeDate.label(19480914).equals("14 September 1948") && TalkService.dateLabel(19480914).equals("Tuesday, 14 September 1948")
                        && TalkService.dateLabel(19480913).startsWith("Monday") && TalkService.dateLabel(19480918).startsWith("Saturday"),
                "14 September 1948 is a Tuesday; the 13th a Monday; the 18th a Saturday", TalkService.dateLabel(19480914));
        check(KnowledgeDate.label(KnowledgeDate.key(-44, 3, 15)).equals("15 March 44 BCE") && KnowledgeDate.key(-44, 3, 15) < KnowledgeDate.key(-43, 1, 1),
                "BCE dates: 15 March 44 BCE, and they sort in time order", KnowledgeDate.label(KnowledgeDate.key(-44, 3, 15)));
    }

    static void street1948() {
        System.out.println("\n3. A street villager at the Charminar, 13-18 September 1948");
        String g12 = TalkService.open(street(19480912)).plainText();
        String g14 = TalkService.open(street(19480914)).plainText();
        String g17 = TalkService.open(street(19480917)).plainText();
        System.out.println("       12 Sep: " + g12 + "\n       14 Sep: " + g14 + "\n       17 Sep: " + g17);
        check(g12.contains("United Nations") && g14.contains("police action") && g14.contains("Naldurg") && g17.contains("ceasefire"),
                "the opening news follows the days (UN on the 12th, police action on the 14th, ceasefire on the 17th)", g14);
        String where = say(street(19480914), "ask", "polo", "where");
        System.out.println("       Where? " + where);
        Matcher m = Pattern.compile("Naldurg[^.]*?about (\\d+) km west").matcher(where);
        int km = m.find() ? Integer.parseInt(m.group(1)) : -1;
        check(km >= 220 && km <= 260, "Where? Naldurg about 240 km west of the Charminar (measured from the villager)", where);
        String when13 = say(street(19480913), "ask", "polo", "when");
        String when16 = say(street(19480916), "ask", "polo", "when");
        check(!when13.isEmpty() && !when13.equals(when16), "When? the answer changes with the day (13th vs 16th)", when13 + " | " + when16);
        TalkView kk = TalkService.act(street(19480914), "ask", "king_kothi", "where");
        System.out.println("       King Kothi, where? " + (kk == null ? "" : kk.plainText() + "  [" + kk.hint + "]"));
        check(kk != null && kk.hint.contains("3.5 km north"), "King Kothi Palace is 3.5 km north of the Charminar (the hint line)",
                kk == null ? "null" : kk.hint);
        String ruler = say(street(19480914), "topic", "ruler", "");
        check(ruler.contains("Nizam") && !ruler.contains("George VI"),
                "Who rules here? the checked card (the Nizam), not the known-wrong data line (George VI)", ruler);
        String typed = say(street(19480914), "free", "tell me about king kothi", "");
        check(typed.toLowerCase(Locale.ROOT).contains("palace"), "typing \"king kothi\" finds King Kothi Palace", typed);
        TalkView greet = TalkService.open(street(19480914));
        boolean names = greet.names.stream().anyMatch(n -> n.cardId().equals("naldurg")) && greet.names.stream().anyMatch(n -> n.cardId().equals("polo"));
        check(names && !greet.options.isEmpty() && greet.options.size() <= 9, "the opening shows gold names (police action, Naldurg) and 1-9 options",
                greet.names + " " + greet.options.size());
    }

    static void court() {
        System.out.println("\n4. Street knowledge and court knowledge");
        TalkView sent = TalkService.act(street(19480917), "card", "laiq_ali", "");
        String told = say(clerk(19480917), "card", "laiq_ali", "");
        System.out.println("       street: " + (sent == null ? "" : sent.plainText()) + "\n       clerk: " + told);
        check(sent != null && sent.plainText().contains("King Kothi") && sent.hint.startsWith("King Kothi"),
                "a street villager sends court questions to the palace, with the way there", sent == null ? "null" : sent.plainText());
        check(told.contains("prime minister") && !told.contains("court business"), "a palace clerk answers court questions", told);
        String clerkNews = TalkService.open(clerk(19480917)).plainText();
        check(clerkNews.contains("cabinet"), "a clerk opens with court news (the cabinet resigned on the 17th)", clerkNews);
        String how = say(street(19480914), "ask", "polo", "how");
        check(!how.isEmpty() && !how.toLowerCase(Locale.ROOT).contains("wiki"), "How do you know? in the villager's own words", how);
    }

    static void future() {
        System.out.println("\n5. Nobody knows the future");
        String polo12 = say(street(19480912), "card", "polo", "");
        check(polo12.contains("haven't heard"), "12 September: nobody has heard of the police action", polo12);
        String bidar16 = say(street(19480916), "card", "bidar", "");
        String bidar17 = say(street(19480917), "card", "bidar", "");
        check(bidar16.contains("haven't heard") && !bidar17.contains("haven't heard"),
                "Bidar comes into the news on the 17th, not before", bidar16 + " | " + bidar17);
        TalkView g13 = TalkService.open(street(19480913));
        boolean leak = false;
        for (TalkView.Name n : g13.names) {
            leak |= n.cardId().equals("bidar") || n.cardId().equals("zahirabad");
        }
        check(!leak, "no names from later days among the 13 September names", g13.names.toString());
    }

    static void allAnswers() {
        System.out.println("\n6. Every card, every question, every day, both levels");
        KnowledgePacks.Pack p = KnowledgePacks.all().get(0);
        int answers = 0, problems = 0;
        String first = "";
        for (int day = 12; day <= 18; day++) {
            int date = 19480900 + day;
            for (TalkService.Ctx c : new TalkService.Ctx[]{street(date), clerk(date)}) {
                for (KnowledgeCard card : p.cards().values()) {
                    for (KnowledgeCard.Question q : card.questions()) {
                        TalkView v = TalkService.act(c, "ask", card.id(), q.id());
                        answers++;
                        String raw = v == null ? "" : v.text;
                        boolean bad = v == null || raw.isBlank() || raw.contains("{d:") || raw.contains("[[") && !TalkView.LINK.matcher(raw).find()
                                || v.options.size() > 16;
                        if (bad) {
                            problems++;
                            if (first.isEmpty()) {
                                first = card.id() + "." + q.id() + " on " + day + ": " + raw;
                            }
                        }
                    }
                }
            }
        }
        check(problems == 0, answers + " answers, none empty, no raw distance or broken link left", problems + " bad, first: " + first);
    }

    static void noSources() {
        System.out.println("\n7. No source names anywhere a player can see");
        KnowledgePacks.Pack p = KnowledgePacks.all().get(0);
        StringBuilder all = new StringBuilder();
        for (KnowledgeCard c : p.cards().values()) {
            all.append(c.title()).append(' ');
            for (KnowledgeCard.Question q : c.questions()) {
                all.append(q.label()).append(' ');
                for (KnowledgeCard.Answer a : q.answers()) {
                    all.append(a.text()).append(' ');
                }
            }
            for (KnowledgeCard.Later l : c.later()) {
                all.append(l.text()).append(' ');
            }
        }
        for (KnowledgePacks.News n : p.news()) {
            all.append(n.text()).append(' ');
        }
        for (KnowledgePacks.PaperDay d : p.papers()) {
            for (KnowledgePacks.Story s : d.stories()) {
                all.append(s.headline()).append(' ').append(s.text()).append(' ');
            }
        }
        for (int level = 1; level <= 2; level++) {
            for (String kind : new String[]{"Event", "Person", "Place", "State", "Group", "Family"}) {
                all.append(com.eternalengine.knowledge.KnowledgeLevels.howIKnow(level, kind, true)).append(' ')
                        .append(com.eternalengine.knowledge.KnowledgeLevels.howIKnow(level, kind, false)).append(' ');
            }
        }
        String low = all.toString().toLowerCase(Locale.ROOT);
        List<String> found = new ArrayList<>();
        for (String w : new String[]{"wikipedia", "wikidata", "wiki", "source:", "according to", "openhistoricalmap", "glottolog"}) {
            if (low.contains(w)) {
                found.add(w);
            }
        }
        check(found.isEmpty(), "no wiki, source or database names in cards, news, papers or \"how do you know\"", found.toString());
    }

    static void elsewhere() {
        System.out.println("\n8. Everywhere else: basic cards from the history data");
        String[][] places = {{"Paris", "48.8566", "2.3522", "1789"}, {"Rome", "41.8925", "12.4853", "1500"},
                {"Varanasi", "25.3176", "82.9739", "1700"}, {"Hyderabad 1850", "17.3616", "78.4747", "1850"},
                {"Kyoto", "35.0116", "135.7681", "1600"}};
        for (String[] pl : places) {
            int date = KnowledgeDate.key(Integer.parseInt(pl[3]), 7, 1);
            TalkService.Ctx c = TalkService.context(null, null, -1, "Villager", "farmer", Double.parseDouble(pl[1]), Double.parseDouble(pl[2]), date, -1);
            TalkView g = TalkService.open(c);
            String ruler = say(c, "topic", "ruler", "");
            String place = say(c, "topic", "place", "");
            System.out.println("       " + pl[0] + " " + pl[3] + ": " + c.local().cards().size() + " cards, packs " + c.packs().size()
                    + "\n         opens: " + g.plainText() + "\n         ruler: " + ruler + "\n         place: " + place);
            check(c.packs().isEmpty() && !g.plainText().isBlank() && c.local().cards().size() >= 1 && g.options.size() >= 2,
                    pl[0] + " " + pl[3] + ": the villager opens, and has topics to ask (" + g.options.size() + ")", g.plainText());
        }
    }

    static void bce() {
        System.out.println("\n9. Before the common era");
        int date = KnowledgeDate.key(-44, 3, 15);
        TalkService.Ctx c = TalkService.context(null, null, -1, "Marcus", "citizen", 41.8925, 12.4853, date, -1);
        TalkView g = TalkService.open(c);
        System.out.println("       Rome, " + g.dateLabel + ": " + g.plainText());
        check(g.dateLabel.equals("15 March 44 BCE") && !g.plainText().isBlank(), "Rome on 15 March 44 BCE: dated and talking", g.dateLabel);
    }

    static void wire() {
        System.out.println("\n10. The packet");
        TalkView v = TalkService.act(street(19480914), "ask", "polo", "where");
        FriendlyByteBuf buf = new FriendlyByteBuf(Unpooled.buffer());
        v.encode(buf);
        int size = buf.readableBytes();
        TalkView w = TalkView.decode(buf);
        boolean same = w.text.equals(v.text) && w.hint.equals(v.hint) && w.options.equals(v.options) && w.names.equals(v.names)
                && w.npcName.equals(v.npcName) && w.dateLabel.equals(v.dateLabel) && w.cardTitle.equals(v.cardTitle) && w.level == v.level;
        check(same && buf.readableBytes() == 0, "the talk view arrives the same as it left (" + size + " bytes)", "differs");
    }

    static void notes() {
        System.out.println("\n11. Notes saved with the world");
        PlayerKnowledge k = new PlayerKnowledge();
        UUID id = UUID.randomUUID();
        k.heard(id, "naldurg", "Naldurg", "Place");
        k.note(id, "polo", "Operation Polo", "Event", new PlayerKnowledge.Note(19480914, "Saleem, merchant", "Where is it?", "At Naldurg."));
        k.note(id, "polo", "Operation Polo", "Event", new PlayerKnowledge.Note(19480914, "Saleem, merchant", "Where is it?", "At Naldurg."));
        k.note(id, "polo", "Operation Polo", "Event", new PlayerKnowledge.Note(19480916, "Venkat Rao, court clerk", "When?", "On the 13th."));
        CompoundTag tag = k.save(new CompoundTag());
        PlayerKnowledge back = PlayerKnowledge.load(tag);
        var mine = back.of(id);
        check(mine.size() == 2 && mine.get("polo").notes().size() == 2 && mine.get("polo").asked() && !mine.get("naldurg").asked()
                        && mine.get("polo").notes().get(1).by().startsWith("Venkat"),
                "names heard and notes (who said it, which day) survive a save; the same answer is kept once", String.valueOf(mine.keySet()));
    }

    /** Step 18b: Terra++ time. The numbers are from the user's log: the jump to 1948 set day 1,806,020. */
    static void terraDays() {
        System.out.println("\n13. Terra++ time: the date from the Minecraft day count");
        int jan1 = KnowledgeDate.fromTerraDay(1_806_020L, 1, -3000, 365);
        int sep14 = KnowledgeDate.fromTerraDay(1_806_020L + 257, 1, -3000, 365);
        check(jan1 == 19480101 && sep14 == 19480914,
                "day 1,806,020 (the user's jump to 1948) is 1 January 1948; 257 Minecraft days later it is 14 September",
                KnowledgeDate.label(jan1) + " / " + KnowledgeDate.label(sep14));
        boolean round = true;
        String bad = "";
        for (int year : new int[]{1948, 1949, 1, -44, -2999}) {
            for (int d = 1; d <= KnowledgeDate.daysIn(year); d++) {
                int key = KnowledgeDate.fromDayOfYear(year, d);
                long day = KnowledgeDate.terraDayFor(key, 1, -3000, 365);
                int back = KnowledgeDate.fromTerraDay(day, 1, -3000, 365);
                int expect = d <= 365 ? key : KnowledgeDate.fromDayOfYear(year, 365);
                if (back != expect) {
                    round = false;
                    bad = KnowledgeDate.label(key) + " -> day " + day + " -> " + KnowledgeDate.label(back);
                }
            }
        }
        check(round, "/ee date with Terra++ time at 1x: every day goes to the right Minecraft day and back (leap years end on 30 December: 365-day years)", bad);
        boolean scaled = true;
        String sbad = "";
        for (int scale : new int[]{2, 10, 25}) {
            for (int d = 1; d <= 365; d += 7) {
                int key = KnowledgeDate.fromDayOfYear(1948, d);
                int back = KnowledgeDate.fromTerraDay(KnowledgeDate.terraDayFor(key, scale, -3000, 365), scale, -3000, 365);
                int diff = KnowledgeDate.dayOfYear(back) - d;
                if (KnowledgeDate.year(back) != 1948 || diff <= -scale || diff >= scale) {
                    scaled = false;
                    sbad = scale + "x: " + KnowledgeDate.label(key) + " -> " + KnowledgeDate.label(back);
                }
            }
        }
        check(scaled, "at 2x, 10x and 25x /ee date lands within one Minecraft day of the date (a day there is 2, 10 or 25 days), in the same year", sbad);
    }

    /** Step 18b: every day of the pack comes in a Terra++ world, not only the preview's six. */
    static void everyDay() {
        System.out.println("\n14. Every day of the pack, 15 August 1947 to 31 December 1948");
        KnowledgePacks.Pack p = KnowledgePacks.all().get(0);
        int days = 0, shown = 0;
        List<String> wrongDay = new ArrayList<>();
        List<String> silent = new ArrayList<>();
        for (java.time.LocalDate d = java.time.LocalDate.of(1947, 8, 15); !d.isAfter(java.time.LocalDate.of(1948, 12, 31)); d = d.plusDays(1)) {
            int date = KnowledgeDate.key(d.getYear(), d.getMonthValue(), d.getDayOfMonth());
            days++;
            for (KnowledgeCard c : p.cards().values()) {
                for (KnowledgeCard.Question q : c.questions()) {
                    KnowledgeCard.Answer a = q.at(date);
                    boolean started = q.answers().stream().anyMatch(x -> x.from() <= date);
                    if (started && a == null) {
                        silent.add(c.id() + "." + q.id() + " on " + KnowledgeDate.label(date));
                    }
                    if (a != null) {
                        shown++;
                        if (KnowledgeCard.DAY_WORDS.matcher(a.text()).find() && a.from() != date) {
                            wrongDay.add(c.id() + "." + q.id() + " on " + KnowledgeDate.label(date) + ": " + a.text());
                        }
                    }
                }
            }
            for (int level = 1; level <= 2; level++) {
                KnowledgePacks.News n = p.newsFor(date, level);
                if (n != null && KnowledgeCard.DAY_WORDS.matcher(n.text()).find() && n.from() != date) {
                    wrongDay.add("news L" + level + " on " + KnowledgeDate.label(date) + ": " + n.text());
                }
            }
        }
        check(wrongDay.isEmpty(), days + " days, " + shown + " answers shown: no \"today\", \"yesterday\" or \"this morning\" on any other day",
                wrongDay.size() + ", first: " + (wrongDay.isEmpty() ? "" : wrongDay.get(0)));
        check(silent.isEmpty(), "no question goes silent on a day after it was first answered",
                silent.size() + ", first: " + (silent.isEmpty() ? "" : silent.get(0)));
        String g15 = TalkService.open(street(19480915)).plainText();
        String w15 = say(street(19480915), "ask", "polo", "where");
        System.out.println("       15 Sep: " + g15 + "\n       15 Sep, where? " + w15);
        check(!g15.toLowerCase(Locale.ROOT).contains("yesterday") && g15.contains("Suryapet") && w15.contains("Suryapet"),
                "15 September has its own news and its own \"where\" (Suryapet taken), not the 14th's \"yesterday\"", g15 + " | " + w15);
        String w25 = say(street(19480925), "ask", "polo", "where");
        String n25 = say(clerk(19480925), "ask", "nizam", "ministers");
        String g1oct = TalkService.open(street(19481001)).plainText();
        System.out.println("       25 Sep, where? " + w25 + "\n       25 Sep, ministers? " + n25 + "\n       1 Oct: " + g1oct);
        check(w25.contains("On 18 September") && n25.contains("17 September") && !g1oct.contains("surrendered")
                        && g1oct.startsWith("Good day to you. This is Hyderabad"),
                "after the week: the same facts with their dates (\"On 18 September\"), and from October the surrender is no longer news",
                w25 + " | " + n25 + " | " + g1oct);
        List<String> problems = KnowledgePacks.validate(p);
        check(problems.isEmpty(), "the pack check (now also: day words, end dates, silent days) finds nothing", String.valueOf(problems));
    }

    /** Step 18b: the user's world showed 1 July 1948; the year-level data would have told of Operation Polo already. */
    static void beforeTheEvent() {
        System.out.println("\n15. Before the event: nobody talks of it early");
        for (int date : new int[]{19480101, 19480701, 19480912}) {
            TalkService.Ctx c = street(date);
            TalkView g = TalkService.open(c);
            String all = g.plainText() + " " + g.names + " " + g.options;
            TalkView news = TalkService.act(c, "topic", "news", "");
            String newsText = news == null ? "" : news.plainText();
            System.out.println("       " + KnowledgeDate.label(date) + ": " + g.plainText() + (newsText.isEmpty() ? "" : "  | news: " + newsText));
            boolean early = (all + " " + newsText).toLowerCase(Locale.ROOT).matches(".*(polo|police action|soldiers on the roads).*");
            check(!early && c.local().newsCard() == null, KnowledgeDate.label(date) + ": nothing about the police action (it starts on 13 September)", all + " | " + newsText);
        }
        TalkService.Ctx after = TalkService.context(null, null, -1, "Saleem", "merchant", CHARMINAR_LAT, CHARMINAR_LON, 19490301, -1);
        System.out.println("       1 March 1949 (after the pack): " + TalkService.open(after).plainText());
        check(after.packs().isEmpty(), "after the pack ends (1949) the history data speaks again", String.valueOf(after.packs().size()));
    }

    static void back() {
        System.out.println("\n12. Back");
        UUID id = UUID.randomUUID();
        TalkService.Ctx c = TalkService.context(id, null, 7, "Saleem", "merchant", CHARMINAR_LAT, CHARMINAR_LON, 19480914, -1);
        String g = TalkService.open(c).plainText();
        TalkView a = TalkService.act(c, "ask", "polo", "where");
        TalkView b = TalkService.act(c, "card", "naldurg", "");
        TalkView back1 = TalkService.act(c, "back", "", "");
        TalkView back2 = TalkService.act(c, "back", "", "");
        check(a != null && a.canBack && back1 != null && back1.plainText().equals(a.plainText()) && back2 != null
                        && back2.plainText().equals(g) && !back2.canBack,
                "Back goes to the answer before, then to the opening", back1 == null ? "null" : back1.plainText());
        TalkService.forget(id);
    }
}
