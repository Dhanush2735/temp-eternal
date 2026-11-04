import com.eternalengine.civilization.EventNews;
import com.eternalengine.civilization.HistoricalPresence;
import com.eternalengine.civilization.HistoryGazetteer;
import com.eternalengine.civilization.OccupiedLands;
import com.eternalengine.knowledge.CardStore;
import com.eternalengine.knowledge.KnowledgeCard;
import com.eternalengine.knowledge.KnowledgeDate;
import com.eternalengine.knowledge.LocalCards;
import com.eternalengine.knowledge.PlaceCards;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Step 28 (C8, C9, C21, known problems 39 and 40): event cards, the cause-and-effect graph, natural events, occupied
 * and disputed land.
 *
 * <p>The event file loads and its index finds every card; named events are worded right for their date (nobody hears
 * of an effect, a part, a death toll or a winner before its time); every link opens a card known on that date; the graph
 * is stored both ways; places remember their past events; the news names an event with a card; storms and other natural
 * events reach the news; occupied squares add "... troops have held this land since ..."; disputed land has its own
 * line, and the land next to it does not.
 */
public final class EventCardsProbe {
    static int ok;
    static int bad;
    static final Pattern LINK = Pattern.compile("\\[\\[(\\w+)\\|([^\\]]+)\\]\\]");
    static final Pattern YEAR_IN = Pattern.compile("\\((\\d{1,4})( BCE)?\\)");

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

    static KnowledgeCard ev(int qid, int year, double lat, double lon) {
        return PlaceCards.resolve("ec_" + qid, KnowledgeDate.key(year, 7, 1), lat, lon);
    }

    /** Problems of a worded event card in a year: links not known yet, a later year in brackets, source names. */
    static String problems(KnowledgeCard k, int year) {
        String t = all(k);
        Matcher m = LINK.matcher(t);
        while (m.find()) {
            KnowledgeCard l = PlaceCards.resolve(m.group(1), KnowledgeDate.key(year, 7, 1), Double.NaN, Double.NaN);
            if (l == null) {
                return "link " + m.group(1) + " does not open";
            }
            if (!l.knownOn(KnowledgeDate.key(year, 7, 1))) {
                return "link " + m.group(1) + " (" + m.group(2) + ") is not known yet in " + year + ": " + t;
            }
        }
        Matcher y = YEAR_IN.matcher(t);
        while (y.find()) {
            int v = Integer.parseInt(y.group(1)) * (y.group(2) != null ? -1 : 1);
            if (v > year) {
                return "a later year " + v + " in: " + t;
            }
        }
        String low = t.toLowerCase(Locale.ROOT);
        if (low.contains("wiki")) {
            return "a source name in: " + t;
        }
        if (t.length() > 3900) {
            return "too long (" + t.length() + ")";
        }
        return "";
    }

    public static void main(String[] args) {
        long t0 = System.nanoTime();
        CardStore store = CardStore.events();
        long load = (System.nanoTime() - t0) / 1_000_000;
        check(store.loaded() && store.size() > 25_000, "the event file loads: " + store.summary() + " in " + load + " ms",
                String.valueOf(store.problem()));
        if (!store.loaded()) {
            System.exit(1);
        }
        int tried = 0;
        int found = 0;
        int step = Math.max(1, store.indexSize() / 2000);
        for (int i = 0; i < store.indexSize(); i += step) {
            int q = store.indexQid(i);
            tried++;
            CardStore.Card c = store.byQid(q);
            if (c != null && c.qid() == q && c.isEvent()) {
                found++;
            }
        }
        check(found == tried && store.indexSize() == store.size(), "every sampled event is in the tile its index names ("
                + found + " of " + tried + ")", "");

        // 1. Named events at their dates.
        String mar = all(ev(330, 1520, 45.46, 9.19));
        System.out.println("     Marignano in 1520 (asked in Milan): " + mar);
        check(mar.contains("The Battle of Marignano was") && mar.contains("1515") && mar.contains("took part")
                        && mar.contains("Melegnano"),
                "a battle: what it was, when, where and who took part (Marignano, 1515)", mar);
        KnowledgeCard ww1in13 = ev(361, 1913, 48.86, 2.35);
        check(ww1in13 != null && !ww1in13.knownOn(KnowledgeDate.key(1913, 7, 1)), "the First World War is unknown in 1913",
                "");
        String ww16 = all(ev(361, 1916, 48.86, 2.35));
        String ww25 = all(ev(361, 1925, 48.86, 2.35));
        System.out.println("     First World War in 1916: " + ww16);
        System.out.println("     First World War in 1925: " + ww25);
        check(ww16.contains("is a global conflict") && ww16.contains("still going on") && !ww16.contains("died")
                        && !ww16.contains("1917") && !ww16.contains("1918"),
                "a war in its third year: going on, no death toll, nothing from 1917 or 1918", ww16);
        check(ww25.contains("was a global conflict") && ww25.contains("lasted from 1914 to 1918")
                        && ww25.contains("million people died") && ww25.contains("After it came"),
                "the same war in 1925: over, its dead counted, what came of it", ww25);
        String ww2 = all(ev(362, 1950, 51.51, -0.13));
        System.out.println("     Second World War in 1950: " + ww2);
        check(ww2.contains("came about because of") && ww2.contains("[[ec_"), "why it happened, with links to the causes"
                + " (the Second World War)", ww2);

        // 2. No future anywhere in the graph: a sample of cards, each worded in five years from its start.
        int worded = 0;
        int problems = 0;
        String first = "";
        int k = 0;
        for (int i = 0; i < store.indexSize(); i += Math.max(1, store.indexSize() / 2500)) {
            CardStore.Card c = store.byQid(store.indexQid(i));
            if (c == null) {
                continue;
            }
            for (int dy : new int[]{0, 1, 3, 10, 60}) {
                int year = c.from() + dy;
                if (year > 2026) {
                    continue;
                }
                KnowledgeCard kc = PlaceCards.event(c, KnowledgeDate.key(year, 7, 1), c.hasLocation() ? c.lat() + 0.1 : Double.NaN,
                        c.hasLocation() ? c.lon() : Double.NaN);
                worded++;
                String p = problems(kc, year);
                if (!p.isEmpty()) {
                    problems++;
                    if (problems <= 4) {
                        System.out.println("     problem: " + c.name() + " in " + year + ": " + p);
                    }
                    if (first.isEmpty()) {
                        first = c.name() + " " + year + ": " + p;
                    }
                }
            }
            k++;
        }
        check(problems == 0, "every sampled event card is right for its year (" + k + " events, " + worded
                + " wordings): no later year, every link known then, no source names", problems + " problems, e.g. " + first);

        // 3. The graph both ways.
        int edges = 0;
        int both = 0;
        String oneWay = "";
        for (int i = 0; i < store.indexSize(); i += 3) {
            CardStore.Card c = store.byQid(store.indexQid(i));
            if (c == null) {
                continue;
            }
            for (CardStore.Link l : c.links()) {
                int back = switch (l.role()) {
                    case CardStore.CAUSE -> CardStore.EFFECT;
                    case CardStore.EFFECT -> CardStore.CAUSE;
                    case CardStore.PART_OF -> CardStore.HAS_PART;
                    case CardStore.AFTER -> CardStore.BEFORE;
                    case CardStore.BEFORE -> CardStore.AFTER;
                    default -> -1;
                };
                if (back < 0) {
                    continue;
                }
                CardStore.Card o = store.byQid(l.qid());
                if (o == null) {
                    continue;
                }
                edges++;
                boolean has = false;
                for (CardStore.Link m : o.links()) {
                    has |= m.role() == back && m.qid() == c.qid();
                }
                // a long list (a war's parts) keeps its best known links only
                long same = o.links().stream().filter(m -> m.role() == back).count();
                if (has || same >= 6) {
                    both++;
                } else if (oneWay.isEmpty()) {
                    oneWay = c.name() + " -> " + o.name() + " (role " + l.role() + ")";
                }
            }
        }
        check(edges > 5000 && both * 100 >= edges * 97, "the cause-and-effect graph is stored both ways (" + both + " of "
                + edges + " links checked)", oneWay);
        System.out.println("     graph: " + store.tileStore().meta("links_cause", "?") + " cause links, "
                + store.tileStore().meta("links_effect", "?") + " effect links, " + store.tileStore().meta("links_partof", "?")
                + " part-of links");

        // 4. The past of a place.
        String hastings = PlaceCards.pastText(PlaceCards.pastEvents(50.91, 0.49, 1200));
        String waterloo = PlaceCards.pastText(PlaceCards.pastEvents(50.68, 4.41, 1900));
        String panipat = PlaceCards.pastText(PlaceCards.pastEvents(29.39, 76.97, 1800));
        System.out.println("     Hastings 1200: " + hastings);
        System.out.println("     Waterloo 1900: " + waterloo);
        System.out.println("     Panipat 1800: " + panipat);
        check(hastings.contains("Hastings") && waterloo.contains("Waterloo") && panipat.contains("Panipat"),
                "a place remembers its past events (Hastings, Waterloo, Panipat)", hastings + " / " + waterloo + " / " + panipat);
        check(!PlaceCards.pastText(PlaceCards.pastEvents(50.91, 0.49, 1050)).contains("Hastings"),
                "but not before they happen (Hastings in 1050)", "");

        // 5. The news names an event with a card.
        double[][] news = {{45.36, 9.31, 1515}, {30.37, -89.09, 2005}, {11.24, 125.00, 2013}};
        int linkedNews = 0;
        for (double[] p : news) {
            HistoricalPresence.Result r = HistoricalPresence.query(null, p[0], p[1], (int) p[2]);
            LocalCards.Local local = LocalCards.build(r, p[0], p[1]);
            KnowledgeCard n = local.newsCard() == null ? null : local.cards().get(local.newsCard());
            String said = n == null ? "" : text(n, "what");
            System.out.println("     news at " + p[0] + "," + p[1] + " in " + (int) p[2] + ": " + said
                    + (n == null ? "" : " | who: " + text(n, "who")));
            if (said.contains("[[ec_")) {
                linkedNews++;
            }
        }
        check(linkedNews == news.length, "the news names an event with its card (Marignano 1515, Katrina at Gulfport 2005, Haiyan 2013)",
                linkedNews + " of " + news.length);

        // 6. Natural events reach the history data.
        HistoryGazetteer gz = HistoryGazetteer.get();
        String[][] nature = {{"29.30", "-94.80", "1900", "1900"}, {"23.70", "90.40", "1970", "cyclone"},
                {"29.95", "-90.07", "2005", "Katrina"}, {"16.80", "96.15", "2008", "Nargis"}};
        int naturalOk = 0;
        for (String[] n : nature) {
            var hits = gz.eventsNear(Double.parseDouble(n[0]), Double.parseDouble(n[1]), Integer.parseInt(n[2]), 300);
            boolean any = false;
            for (var h : hits) {
                any |= "cyclone".equals(h.event().kind()) && h.event().name().contains(n[3]);
            }
            if (any) {
                naturalOk++;
            } else {
                System.out.println("     no storm with \"" + n[3] + "\" near " + n[0] + "," + n[1] + " in " + n[2]);
            }
        }
        check(naturalOk == nature.length, "storms reach the history data: Galveston 1900, Bhola 1970, Katrina 2005, Nargis "
                + "2008 (" + naturalOk + " of " + nature.length + ")", "");
        long kinds = gz.allEvents().stream().filter(e -> "ibtracs".equals(e.confidence())).count();
        long natural = gz.allEvents().stream().filter(e -> List.of("flood", "wildfire", "landslide", "avalanche", "tornado",
                "heatwave", "drought", "famine", "epidemic").contains(e.kind()) && e.confidence() != null
                && e.confidence().startsWith("wikidata")).count();
        check(kinds > 5000 && natural > 1500, "storm landfalls (" + kinds + ") and other natural events (" + natural
                + ") are in the history data", "");

        // 7. Occupied land.
        String[][] occ = {{"Paris", "48.86", "2.35", "1942", "German troops have held this land since 1940"},
                {"Oslo", "59.91", "10.75", "1942", "German troops"}, {"Copenhagen", "55.68", "12.57", "1942", "German troops"},
                {"Batavia", "-6.20", "106.85", "1944", "Japanese troops"}, {"Nanjing", "32.06", "118.80", "1940", "Japanese troops"},
                {"Tehran", "35.69", "51.39", "1943", "troops have held"}};
        int occOk = 0;
        for (String[] o : occ) {
            HistoricalPresence.Result r = HistoricalPresence.query(null, Double.parseDouble(o[1]), Double.parseDouble(o[2]),
                    Integer.parseInt(o[3]));
            String line = EventNews.rulerLine(r);
            System.out.println("     " + o[0] + " " + o[3] + ": " + line);
            if (line.contains(o[4])) {
                occOk++;
            }
        }
        check(occOk == occ.length, "occupied land names its state and the occupier (Paris, Oslo, Copenhagen, Batavia, Nanjing,"
                + " Tehran: " + occOk + " of " + occ.length + ")", "");
        String paris46 = EventNews.rulerLine(HistoricalPresence.query(null, 48.86, 2.35, 1946));
        String paris38 = EventNews.rulerLine(HistoricalPresence.query(null, 48.86, 2.35, 1938));
        check(!paris46.contains("troops") && !paris38.contains("troops"), "and only in the years of the occupation (Paris 1938,"
                + " 1946)", paris38 + " / " + paris46);

        // 8. Disputed land.
        String[][] disp = {{"Ramallah", "31.90", "35.20", "2020", "Palestinian Authority"},
                {"Gaza", "31.50", "34.45", "2024", "since October 2023"}, {"Golan", "33.00", "35.75", "2000", "Syria claims"},
                {"Simferopol", "44.95", "34.10", "2020", "Ukraine claims"}, {"Kyrenia", "35.34", "33.32", "2000", "Turkish troops"},
                {"Laayoune", "27.15", "-13.20", "2000", "Morocco has held"}};
        int dOk = 0;
        for (String[] d : disp) {
            String line = EventNews.rulerLine(HistoricalPresence.query(null, Double.parseDouble(d[1]), Double.parseDouble(d[2]),
                    Integer.parseInt(d[3])));
            System.out.println("     " + d[0] + " " + d[3] + ": " + line);
            if (line.contains(d[4])) {
                dOk++;
            }
        }
        check(dOk == disp.length, "disputed land says who holds it and who claims it (" + dOk + " of " + disp.length + ")", "");
        String[][] notDisp = {{"Tel Aviv", "32.08", "34.78", "2020"}, {"West Jerusalem", "31.78", "35.20", "2020"},
                {"Sevastopol", "44.60", "33.52", "2010"}, {"Limassol", "34.68", "33.04", "2000"}, {"Ramallah", "31.90", "35.20", "1960"}};
        int nOk = 0;
        for (String[] d : notDisp) {
            String line = EventNews.rulerLine(HistoricalPresence.query(null, Double.parseDouble(d[1]), Double.parseDouble(d[2]),
                    Integer.parseInt(d[3])));
            System.out.println("     " + d[0] + " " + d[3] + ": " + line);
            if (line.startsWith("This land belongs to")) {
                nOk++;
            }
        }
        check(nOk == notDisp.length, "the land beside it, and the years before, keep the record's line (Tel Aviv, West "
                + "Jerusalem, Sevastopol 2010, Limassol, Ramallah 1960)", nOk + " of " + notDisp.length);
        OccupiedLands ol = OccupiedLands.get();
        check(ol.problem() == null && ol.squares() > 5000 && ol.areas().size() == 6, "occupations (" + ol.squares()
                + " squares) and disputed areas (" + ol.areas().size() + ") load", String.valueOf(ol.problem()));

        // 9. Speed.
        long s0 = System.nanoTime();
        int n = 0;
        for (double[] p : new double[][]{{50.91, 0.49}, {50.68, 4.41}, {29.39, 76.97}, {48.86, 2.35}, {41.89, 12.49},
                {35.68, 139.76}, {30.04, 31.24}, {40.71, -74.01}}) {
            for (int year : new int[]{1000, 1500, 1800, 1900, 2000}) {
                PlaceCards.pastEvents(p[0], p[1], year);
                n++;
            }
        }
        double ms = (System.nanoTime() - s0) / 1e6 / n;
        check(ms < 10.0, String.format(Locale.ROOT, "a place's past events take %.2f ms", ms), "too slow");

        System.out.println();
        System.out.println(bad == 0 ? "EVENT CARDS OK (" + ok + " checks)" : "EVENT CARDS: " + bad + " FAILED, " + ok + " OK");
        System.exit(bad == 0 ? 0 : 1);
    }
}
