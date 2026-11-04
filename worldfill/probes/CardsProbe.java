import com.eternalengine.civilization.HistoricalPresence;
import com.eternalengine.civilization.HistoryChecks;
import com.eternalengine.data.TileCache;
import com.eternalengine.knowledge.CardStore;
import com.eternalengine.knowledge.KnowledgeCard;
import com.eternalengine.knowledge.KnowledgeDate;
import com.eternalengine.knowledge.LocalCards;
import com.eternalengine.knowledge.PlaceCards;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Step 27 (C10, C12, C22): the knowledge cards of famous people and groups, for every place and year.
 *
 * <p>The card file loads and its index finds every card; named places and years give the expected people and groups;
 * nobody and nothing is known before its time (people, offices, works, lines that name an office, deaths, groups and
 * their closing); every link opens a card that is known on that date; no source names; the world sample (every land
 * point of the check list, 10 years from 3000 BC to 2026) has names to tell almost everywhere people wrote; the time a
 * place's lists take, cold and warm; the memory of the opened tiles.
 */
public final class CardsProbe {
    static int ok;
    static int bad;
    static final Pattern LINK = Pattern.compile("\\[\\[(\\w+)\\|([^\\]]+)\\]\\]");
    static final Pattern BCE_TAIL = Pattern.compile("-\\d{1,4}\\s*(BCE|BC\\b|B\\.C\\.)");
    static final Pattern NUMBER = Pattern.compile("(?<![\\w.])(\\d{1,4})(?![\\w])( BCE| B\\.C\\.| BC\\b| years| km| m\\b)?");

    static void check(boolean good, String what, String detail) {
        if (good) {
            ok++;
            System.out.println("OK   " + what);
        } else {
            bad++;
            System.out.println("FAIL " + what + "  -- " + detail);
        }
    }

    static String text(KnowledgeCard k, String q) {
        if (k == null || k.question(q) == null) {
            return "";
        }
        KnowledgeCard.Answer a = k.question(q).at(KnowledgeDate.key(3000, 1, 1));
        return a == null ? "" : a.text();
    }

    static String all(KnowledgeCard k) {
        StringBuilder sb = new StringBuilder();
        for (KnowledgeCard.Question q : k.questions()) {
            sb.append(text(k, q.id())).append(' ');
        }
        return sb.toString();
    }

    static KnowledgeCard at(String id, int year, double lat, double lon) {
        return PlaceCards.resolve(id, KnowledgeDate.key(year, 7, 1), lat, lon);
    }

    /** Problems of one worded card in a year: future years, links that do not open or are not known yet, source names. */
    static String problems(KnowledgeCard k, CardStore.Card c, int year) {
        String t = all(k);
        String scan = t;
        for (CardStore.Work w : c.works()) {
            scan = scan.replace(w.title(), "");
        }
        Matcher m = LINK.matcher(t);
        while (m.find()) {
            KnowledgeCard l = PlaceCards.resolve(m.group(1), KnowledgeDate.key(year, 7, 1), Double.NaN, Double.NaN);
            if (l == null) {
                return "link " + m.group(1) + " does not open";
            }
            if (!l.knownOn(KnowledgeDate.key(year, 7, 1))) {
                return "link " + m.group(1) + " (" + m.group(2) + ") is not known yet in " + year;
            }
            scan = scan.replace(m.group(0), "");
        }
        scan = scan.replace(c.name(), "");
        Matcher n = NUMBER.matcher(scan);
        while (n.find()) {
            String unit = n.group(2) == null ? "" : n.group(2);
            if (unit.equals(" years") || unit.equals(" km") || unit.startsWith(" m")) {
                continue;
            }
            int y = Integer.parseInt(n.group(1));
            // "1559-1550 BCE": the era is written once, after the range, but BOTH years are BCE.
            // Without this the scanner read 1559 as a year of the common era and called a Hittite
            // queen's marriage a year in the future of a card dated 1500 BCE.
            boolean bceRange = unit.isEmpty()
                    && BCE_TAIL.matcher(scan.substring(n.end(), Math.min(scan.length(), n.end() + 14))).lookingAt();
            if (bceRange) {
                continue;
            }
            if (unit.equals(" BCE") || unit.equals(" B.C.") || unit.equals(" BC")) {
                y = -y;
            } else if (y < 100 && !scan.substring(Math.max(0, n.start() - 3), n.start()).endsWith("in ")) {
                continue; // an age or a count, not a year
            } else if (scan.substring(Math.max(0, n.start() - 6), n.start()).endsWith("about ")
                    && scan.startsWith(" now", n.end())) {
                continue; // "he is about 102 now": an age
            }
            if (y > year && y <= 2100) {
                return "a later year " + y + " in: " + t;
            }
        }
        String low = t.toLowerCase(Locale.ROOT);
        if (low.contains("wiki") || low.contains("wikidata") || Pattern.compile("\\bq\\d{2,}\\b").matcher(low).find()) {
            return "a source name in: " + t;
        }
        if (t.length() > 3900) {
            return "too long for the talk box (" + t.length() + ")";
        }
        return "";
    }

    static String yearText(int y) {
        return y == CardStore.UNKNOWN ? "?" : y < 0 ? (-y) + " BC" : String.valueOf(y);
    }

    record Spot(String label, double lat, double lon, int year, int expectPerson, int expectGroup, boolean needPeople) {
        Spot(String label, double lat, double lon, int year, int expectPerson, int expectGroup) {
            this(label, lat, lon, year, expectPerson, expectGroup, true);
        }
    }

    public static void main(String[] args) {
        long t0 = System.nanoTime();
        CardStore store = CardStore.get();
        long load = (System.nanoTime() - t0) / 1_000_000;
        check(store.loaded(), "the card file loads: " + store.summary() + " in " + load + " ms", String.valueOf(store.problem()));
        if (!store.loaded()) {
            System.exit(1);
        }
        check(store.indexSize() == store.size() && store.people() > 100_000 && store.organisations() > 20_000,
                "the index holds every card (" + store.indexSize() + " of " + store.size() + ")", "");

        // 1. The index finds what it lists.
        int found = 0;
        int tried = 0;
        String missing = "";
        int step = Math.max(1, store.indexSize() / 3000);
        for (int i = 0; i < store.indexSize(); i += step) {
            int q = store.indexQid(i);
            tried++;
            CardStore.Card c = store.byQid(q);
            if (c != null && c.qid() == q) {
                found++;
            } else if (missing.isEmpty()) {
                missing = "Q" + q;
            }
        }
        check(found == tried, "every sampled card is in the tile its index names (" + found + " of " + tried + ")", missing);

        // 2. Named places and years.
        List<Spot> spots = List.of(
                new Spot("Florence 1610", 43.77, 11.25, 1610, 307, 0),
                new Spot("Bologna 1300", 44.49, 11.34, 1300, 0, 131262),
                new Spot("London 1700", 51.51, -0.13, 1700, 0, 83164),
                new Spot("Bombay 1948", 18.94, 72.83, 1948, 0, 0),
                new Spot("Hyderabad 1948", 17.385, 78.4867, 1948, 0, 0),
                new Spot("Rome 100", 41.89, 12.49, 100, 0, 0),
                new Spot("Kyoto 1600", 35.01, 135.77, 1600, 0, 0),
                new Spot("Beijing 1700", 39.90, 116.40, 1700, 0, 0),
                new Spot("Cusco 1500", -13.53, -71.97, 1500, 0, 0),
                new Spot("Cairo 1250", 30.04, 31.24, 1250, 0, 0),
                new Spot("Timbuktu 1330", 16.77, -3.01, 1330, 0, 0, false),
                new Spot("Washington 1865", 38.90, -77.04, 1865, 0, 0),
                new Spot("Lagos 1990", 6.52, 3.38, 1990, 0, 0),
                new Spot("Sydney 2000", -33.87, 151.21, 2000, 0, 0),
                new Spot("Kinshasa 2026", -4.32, 15.31, 2026, 0, 0),
                new Spot("Athens 400 BC", 37.98, 23.73, -400, 0, 0),
                new Spot("Memphis (Egypt) 2500 BC", 29.85, 31.25, -2500, 0, 0),
                new Spot("Reykjavik 1900", 64.15, -21.94, 1900, 0, 0));
        for (Spot sp : spots) {
            long s0 = System.nanoTime();
            PlaceCards.Lists l = PlaceCards.lists(sp.lat(), sp.lon(), sp.year());
            long ms = (System.nanoTime() - s0) / 1_000_000;
            List<String> names = new ArrayList<>();
            boolean hasPerson = sp.expectPerson() == 0;
            boolean hasGroup = sp.expectGroup() == 0;
            String prob = "";
            for (CardStore.Card c0 : l.people()) {
                CardStore.Card c = store.byQid(c0.qid());
                names.add(c.name() + " (" + yearText(c.from()) + ")");
                hasPerson |= c.qid() == sp.expectPerson();
                KnowledgeCard k = PlaceCards.card(c, KnowledgeDate.key(sp.year(), 7, 1), sp.lat(), sp.lon());
                String p = problems(k, c, sp.year());
                if (!p.isEmpty() && prob.isEmpty()) {
                    prob = c.name() + ": " + p;
                }
                if (!c.knownIn(sp.year())) {
                    prob = c.name() + " is not known yet";
                }
            }
            List<String> gnames = new ArrayList<>();
            for (CardStore.Card c : l.groups()) {
                gnames.add(c.name() + " (" + yearText(c.from()) + ")");
                hasGroup |= c.qid() == sp.expectGroup();
                KnowledgeCard k = PlaceCards.card(c, KnowledgeDate.key(sp.year(), 7, 1), sp.lat(), sp.lon());
                String p = problems(k, c, sp.year());
                if (!p.isEmpty() && prob.isEmpty()) {
                    prob = c.name() + ": " + p;
                }
            }
            System.out.println("     " + sp.label() + " (" + ms + " ms): " + (l.longAgo() ? "long ago: " : "")
                    + String.join("; ", names) + " | groups" + (l.groupsFar() ? " (not far)" : "") + ": "
                    + String.join("; ", gnames));
            check(hasPerson && hasGroup && prob.isEmpty() && (!l.people().isEmpty() || !sp.needPeople()),
                    sp.label() + ": names to tell, each card right for the year", prob.isEmpty()
                            ? "expected person " + sp.expectPerson() + " " + hasPerson + ", group " + sp.expectGroup() + " " + hasGroup
                            : prob);
        }

        // 3. Nobody knows the future.
        check(at("pc_307", 1580, 43.77, 11.25) != null && !at("pc_307", 1580, 43.77, 11.25).knownOn(KnowledgeDate.key(1580, 7, 1))
                        && at("pc_307", 1610, 43.77, 11.25).knownOn(KnowledgeDate.key(1610, 7, 1)),
                "Galileo is not known in 1580 (aged 16), known in 1610", "");
        String jfk50 = text(at("pc_9696", 1950, 38.9, -77.04), "who");
        String jfk62 = text(at("pc_9696", 1962, 38.9, -77.04), "who");
        String jfk70 = text(at("pc_9696", 1970, 38.9, -77.04), "who");
        System.out.println("     Kennedy 1950: " + jfk50);
        System.out.println("     Kennedy 1962: " + jfk62);
        System.out.println("     Kennedy 1970: " + jfk70);
        check(!jfk50.toLowerCase(Locale.ROOT).contains("president") && jfk62.contains("is the president of the United States")
                        && jfk70.contains("was a president") && jfk70.contains("died in Dallas in 1963"),
                "a line that names an office waits for it: Kennedy is not called president in 1950, is in 1962, was in 1970",
                jfk50 + " / " + jfk62 + " / " + jfk70);
        String deeds62 = text(at("pc_9696", 1962, 38.9, -77.04), "deeds");
        System.out.println("     Kennedy's deeds 1962: " + deeds62);
        check(deeds62.contains("has been President of the United States since 1961") && !deeds62.contains("Ich bin"),
                "offices and works count from their year (1962: president since 1961; the 1963 speech not yet)", deeds62);
        String vic30 = text(at("pc_9439", 1830, 51.5, -0.13), "who");
        String vic40 = text(at("pc_9439", 1840, 51.5, -0.13), "who");
        System.out.println("     Victoria 1830: " + vic30);
        System.out.println("     Victoria 1840: " + vic40);
        check(!vic30.contains("queen") && vic40.contains("is the queen of the United Kingdom") && vic40.contains("She was born"),
                "Victoria is not called queen in 1830, is in 1840 (and she is a she)", vic30 + " / " + vic40);
        String nap = text(at("pc_517", 1800, 48.86, 2.35), "who");
        String nap10 = text(at("pc_517", 1810, 48.86, 2.35), "who");
        System.out.println("     Napoleon 1800: " + nap);
        System.out.println("     Napoleon 1810: " + nap10);
        check(nap.contains("French military leader") && !nap.contains("Emperor") && nap10.contains("Emperor"),
                "the early part of a line is said before the office: Napoleon in 1800 a military leader, in 1810 emperor",
                nap + " / " + nap10);
        String gan40 = text(at("pc_1001", 1940, 18.94, 72.83), "who");
        String gan50 = text(at("pc_1001", 1950, 18.94, 72.83), "who");
        System.out.println("     Gandhi 1940: " + gan40);
        System.out.println("     Gandhi 1950: " + gan50);
        check(gan40.contains("is an Indian") && !gan40.contains("died") && gan50.contains("died") && gan50.contains("1948"),
                "a death is told from its year on (Gandhi alive in 1940, dead in 1950)", gan40 + " / " + gan50);
        KnowledgeCard bo1000 = at("oc_131262", 1000, 44.49, 11.34);
        String bo1100 = text(at("oc_131262", 1100, 44.49, 11.34), "what");
        System.out.println("     University of Bologna 1100: " + bo1100);
        check(bo1000 != null && !bo1000.knownOn(KnowledgeDate.key(1000, 7, 1)) && bo1100.contains("founded in 1088"),
                "a group is known from its founding (Bologna's university not in 1000, founded 1088 in 1100)", bo1100);
        String eic = text(at("oc_83164", 1700, 51.51, -0.13), "what");
        String eic80 = text(at("oc_83164", 1880, 51.51, -0.13), "what");
        System.out.println("     East India Company 1700: " + eic);
        System.out.println("     East India Company 1880: " + eic80);
        check(eic.contains("is a British trading company") && eic80.contains("closed in 1874"),
                "a group that closed is told as closed (the East India Company in 1880)", eic + " / " + eic80);
        String where = text(at("pc_307", 1610, 43.77, 11.25), "where");
        KnowledgeCard gal = at("pc_307", 1610, 43.77, 11.25);
        System.out.println("     Galileo, where (Florence 1610): " + where);
        check(where.contains("Pisa") && where.contains("km") && gal.hasLocation(),
                "where people come from, with the distance and a place for the compass (Galileo from Pisa)", where);

        String tra = text(at("pc_1425", 105, 41.89, 12.49), "who");
        System.out.println("     Trajan 105: " + tra);
        check(tra.contains("is the 13th Roman Emperor"), "an ordinal takes \"the\" (Trajan is the 13th Roman Emperor)", tra);
        KnowledgeCard bookCard = com.eternalengine.knowledge.BookService.card("pc_307");
        KnowledgeCard bookGroup = com.eternalengine.knowledge.BookService.card("oc_131262");
        check(bookCard != null && bookCard.hasLocation() && bookGroup != null && bookGroup.hasLocation(),
                "the history book finds people and groups by their ids, with a place to track (Galileo, Bologna's university)",
                bookCard + " / " + bookGroup);

        // 4. The world sample.
        double[][] land = HistoryChecks.landPoints();
        int[] years = {-3000, -1500, -500, 1, 800, 1200, 1500, 1800, 1900, 1950, 2026};
        int spotsN = 0;
        int withPeople = 0;
        int withGroups = 0;
        int problemsN = 0;
        String firstProblem = "";
        long cold = 0;
        long slowest = 0;
        String slowAt = "";
        int cardsChecked = 0;
        for (int year : years) {
            for (double[] p : land) {
                spotsN++;
                long s0 = System.nanoTime();
                PlaceCards.Lists l = PlaceCards.lists(p[0], p[1], year);
                long ns = System.nanoTime() - s0;
                cold += ns;
                if (ns > slowest) {
                    slowest = ns;
                    slowAt = p[0] + "," + p[1] + " " + year;
                }
                if (!l.people().isEmpty()) {
                    withPeople++;
                }
                if (!l.groups().isEmpty()) {
                    withGroups++;
                }
                List<CardStore.Card> both = new ArrayList<>(l.people());
                both.addAll(l.groups());
                for (CardStore.Card c0 : both) {
                    CardStore.Card c = store.byQid(c0.qid());
                    KnowledgeCard k = PlaceCards.card(c, KnowledgeDate.key(year, 7, 1), p[0], p[1]);
                    cardsChecked++;
                    String pr = problems(k, c, year);
                    if (!pr.isEmpty()) {
                        problemsN++;
                        if (problemsN <= 5) {
                            System.out.println("     problem: " + c.name() + " " + year + ": " + pr);
                        }
                        if (firstProblem.isEmpty()) {
                            firstProblem = c.name() + " " + year + ": " + pr;
                        }
                    }
                }
            }
        }
        long warm0 = System.nanoTime();
        for (int year : years) {
            for (double[] p : land) {
                PlaceCards.lists(p[0], p[1], year);
            }
        }
        long warm = System.nanoTime() - warm0;
        System.out.printf(Locale.ROOT, "     world sample: %d spots, %d with people (%.0f%%), %d with groups (%.0f%%), %d cards worded%n",
                spotsN, withPeople, 100.0 * withPeople / spotsN, withGroups, 100.0 * withGroups / spotsN, cardsChecked);
        for (int year : years) {
            int wp = 0;
            for (double[] p : land) {
                if (!PlaceCards.lists(p[0], p[1], year).people().isEmpty()) {
                    wp++;
                }
            }
            System.out.printf(Locale.ROOT, "       %s: people at %d of %d land points%n", yearText(year), wp, land.length);
        }
        check(problemsN == 0, "every worded card of the world sample is right for its year (" + cardsChecked + " cards)",
                problemsN + " problems, e.g. " + firstProblem);
        int modern = 0;
        int modernWith = 0;
        for (int year : new int[]{1800, 1900, 1950, 2026}) {
            for (double[] p : land) {
                modern++;
                if (!PlaceCards.lists(p[0], p[1], year).people().isEmpty()) {
                    modernWith++;
                }
            }
        }
        check(modernWith * 100 >= modern * 70 && withPeople * 100 >= spotsN * 40,
                "people to tell at most land points since 1800 (" + modernWith + " of " + modern + "), and at "
                        + withPeople + " of " + spotsN + " over all years", "too few");
        double coldMs = cold / 1e6 / spotsN;
        double warmMs = warm / 1e6 / spotsN;
        System.out.printf(Locale.ROOT, "     time per place: %.2f ms the first time, %.2f ms after; slowest %.1f ms at %s%n",
                coldMs, warmMs, slowest / 1e6, slowAt);
        check(warmMs < 5.0 && coldMs < 40.0, String.format(Locale.ROOT, "a place's lists are quick (%.2f ms warm, %.2f ms cold)",
                warmMs, coldMs), "too slow");
        var cache = TileCache.SHARED.stats();
        System.out.println("     tile cache: " + cache.display());
        check(cache.peakBytes() <= cache.budgetBytes(), "opened tiles stay within the budget", cache.display());

        // 5. With the place's history (LocalCards): the famous answer and the place's groups.
        double[][] lc = {{43.77, 11.25, 1610}, {18.94, 72.83, 1948}, {41.89, 12.49, 100}, {35.01, 135.77, 1600},
                {51.51, -0.13, 1700}, {48.86, 2.35, 1789}, {39.90, 116.40, 1700}, {38.90, -77.04, 1865},
                {28.61, 77.21, 1600}, {55.76, 37.62, 1980}};
        int rulersLinked = 0;
        for (double[] p : lc) {
            HistoricalPresence.Result r = HistoricalPresence.query(null, p[0], p[1], (int) p[2]);
            LocalCards.Local local = LocalCards.build(r, p[0], p[1]);
            KnowledgeCard famous = local.famousCard() == null ? null : local.cards().get(local.famousCard());
            KnowledgeCard place = local.placeCard() == null ? null : local.cards().get(local.placeCard());
            String f = famous == null ? "" : text(famous, "who");
            String g = place == null ? "" : text(place, "groups");
            KnowledgeCard state = local.rulerCard() == null ? null : local.cards().get(local.rulerCard());
            String ru = state == null ? "" : text(state, "who");
            System.out.println("     talk at " + p[0] + "," + p[1] + " " + (int) p[2] + ": famous: " + f);
            System.out.println("        groups: " + g);
            System.out.println("        ruler: " + ru);
            if (ru.contains("[[pc_")) {
                rulersLinked++;
            }
            check(f.contains("[[pc_") && local.listed().size() >= 1, "the famous answer names people with cards at "
                    + p[0] + "," + p[1] + " in " + yearText((int) p[2]), f);
        }
        check(rulersLinked >= 7, "who rules here names the ruler with a card of their own (" + rulersLinked + " of "
                + lc.length + " places)", "too few");
        // The ruler's card by name.
        CardStore.Card trajan = PlaceCards.ruler("Trajan", 105);
        check(trajan != null && trajan.qid() == 1425, "a ruler's card is found by name and year (Trajan in 105)",
                trajan == null ? "none" : trajan.name() + " Q" + trajan.qid());
        System.out.println();
        System.out.println(bad == 0 ? "CARDS OK (" + ok + " checks)" : "CARDS: " + bad + " FAILED, " + ok + " OK");
        System.exit(bad == 0 ? 0 : 1);
    }
}
