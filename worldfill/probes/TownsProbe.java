import com.eternalengine.civilization.EventNews;
import com.eternalengine.civilization.HistoricalPresence;
import com.eternalengine.civilization.StateRelations;
import com.eternalengine.civilization.TownFacts;
import com.eternalengine.knowledge.KnowledgeCard;
import com.eternalengine.knowledge.KnowledgeDate;
import com.eternalengine.knowledge.LocalCards;

import java.util.Random;

/**
 * Step 29 (C2, C3, C4, C5, C6, C28): towns through time and the ties between states.
 *
 * <p>The town file loads; a town's name follows the year everywhere on the map (Bombay / Mumbai, Edo / Tokyo,
 * Leopoldville / Kinshasa, Constantinople / Istanbul, Petrograd / Leningrad / Saint Petersburg, Stalingrad, Danzig,
 * Breslau, Salisbury, Saigon, Rangoon, Christiania / Kristiania / Oslo ...); people by year come from the census figures
 * (a straight line between two, nothing before the first); provinces and heads follow the year; a sweep of land points
 * and years finds no town named before it is known and no head out of office; state ties follow the year; and a town
 * lookup is fast.
 */
public final class TownsProbe {
    static int ok;
    static int bad;

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

    static HistoricalPresence.Result at(double lat, double lon, int year) {
        return HistoricalPresence.query(null, lat, lon, year);
    }

    public static void main(String[] args) {
        long t0 = System.nanoTime();
        TownFacts tf = TownFacts.get();
        check(tf.loaded() && tf.size() > 25_000, "the town file loads: " + tf.summary() + ", about "
                + tf.approxBytes() / 1_000_000 + " MB", String.valueOf(tf.problem()));
        System.out.println("     first load " + (System.nanoTime() - t0) / 1_000_000 + " ms");

        // 1. Names by era, through the place line, all over the world.
        Object[][] names = {
                {18.94, 72.83, 1900, "Bombay"}, {18.94, 72.83, 2026, "Mumbai"},
                {13.08, 80.27, 1900, "Madras"}, {13.08, 80.27, 2010, "Chennai"},
                {22.57, 88.36, 1900, "Calcutta"}, {22.57, 88.36, 2010, "Kolkata"},
                {35.68, 139.76, 1700, "Edo"}, {35.68, 139.76, 1900, "Tokyo"},
                {-4.32, 15.31, 1955, "Léopoldville"}, {-4.32, 15.31, 2000, "Kinshasa"},
                {41.01, 28.98, -500, "Byzantium"}, {41.01, 28.98, 1000, "Constantinople"},
                {41.01, 28.98, 1800, "Constantinople"}, {41.01, 28.98, 1950, "Istanbul"},
                {59.94, 30.31, 1920, "Petrograd"}, {59.94, 30.31, 1950, "Leningrad"},
                {59.94, 30.31, 2000, "Saint Petersburg"}, {48.71, 44.51, 1940, "Stalingrad"},
                {48.71, 44.51, 1990, "Volgograd"}, {54.35, 18.65, 1900, "Danzig"}, {54.35, 18.65, 1990, "Gda"},
                {51.11, 17.03, 1900, "Breslau"}, {51.11, 17.03, 1990, "Wrocław"},
                {-17.83, 31.05, 1970, "Salisbury"}, {-17.83, 31.05, 1990, "Harare"},
                {10.78, 106.70, 1960, "Saigon"}, {10.78, 106.70, 2000, "Ho Chi Minh City"},
                {16.80, 96.16, 1950, "Rangoon"}, {16.80, 96.16, 2000, "Yangon"},
                {59.91, 10.75, 1850, "Christiania"}, {59.91, 10.75, 1900, "Kristiania"}, {59.91, 10.75, 1950, "Oslo"},
                {39.90, 116.40, 1935, "Beiping"}, {39.90, 116.40, 1960, "Beijing"},
                {54.71, 20.51, 1900, "Königsberg"}, {-6.20, 106.85, 1900, "Batavia"},
                {40.71, -74.01, 1650, "New Amsterdam"}, {40.71, -74.01, 1700, "New York"},
                {19.43, -99.13, 1450, "Tenochtitlan"}, {43.24, 76.89, 1950, "Alma-Ata"},
                {12.97, 77.59, 1990, "Bangalore"}, {12.97, 77.59, 2020, "Bengaluru"}};
        int right = 0;
        for (Object[] n : names) {
            double la = ((Number) n[0]).doubleValue();
            double lo = ((Number) n[1]).doubleValue();
            int y = (Integer) n[2];
            String line = EventNews.placeLine(at(la, lo, y));
            boolean good = line.contains((String) n[3]);
            right += good ? 1 : 0;
            System.out.println("     " + (good ? "ok  " : "MISS") + " " + y + " " + n[3] + ": " + line);
        }
        check(right >= names.length - 3, "a town's name follows the year (" + right + " of " + names.length
                + "; a miss is a place the history data has no site or town for in that year)", "");

        // 2. People by year.
        var kolkata = tf.byLabelNear("Kolkata", 22.57, 88.37);
        check(kolkata.isPresent() && kolkata.get().peopleIn(1901) == 847_796L && kolkata.get().peopleIn(1600) == -1L,
                "people by year: Calcutta 847,796 in 1901, unknown before the first count", "");
        int outside = 0;
        long counted = 0;
        for (int i = 0; i < tf.size(); i++) {
            TownFacts.Town t = tf.town(i);
            for (int y = -500; y <= 2026; y += 13) {
                long p = t.peopleIn(y);
                if (p == 0 || p < -1) {
                    outside++;
                }
                counted += p > 0 ? 1 : 0;
            }
        }
        check(outside == 0, "no zero or negative people counts (" + tf.size() + " towns, every 13th year from 500 BCE: "
                + counted + " town-years with a count)", "" + outside);

        // 3. Provinces and heads by year.
        String[][] prov = {{"18.94", "72.83", "1900", "Bombay Presidency"}, {"18.94", "72.83", "1955", "Bombay State"},
                {"18.94", "72.83", "2000", "Maharashtra"}, {"17.385", "78.4867", "1952", "Hyderabad State"},
                {"17.385", "78.4867", "1990", "Andhra Pradesh"}, {"17.385", "78.4867", "2020", "Telangana"},
                {"22.57", "88.36", "1900", "Bengal Presidency"}, {"22.57", "88.36", "2000", "West Bengal"},
                {"40.71", "-74.01", "1900", "New York"}};
        int pr = 0;
        for (String[] p : prov) {
            String line = EventNews.provinceLine(at(Double.parseDouble(p[0]), Double.parseDouble(p[1]), Integer.parseInt(p[2])));
            boolean good = line.contains(p[3]);
            pr += good ? 1 : 0;
            System.out.println("     " + (good ? "ok  " : "MISS") + " " + p[2] + " " + p[3] + ": " + line);
        }
        String h1900 = EventNews.provinceLine(at(17.385, 78.4867, 1900));
        check(pr == prov.length && h1900.isEmpty(), "the province follows the year (" + pr + " of " + prov.length
                + "); none when it has the ruling state's name (Hyderabad State under the Nizam, 1900)", h1900);
        String[][] heads = {{"48.857", "2.352", "2015", "Anne Hidalgo"}, {"40.713", "-74.006", "2010", "Bloomberg"},
                {"51.507", "-0.128", "2010", "Boris Johnson"}, {"35.689", "139.692", "2020", "Koike"},
                {"18.94", "72.83", "2015", "Fadnavis"}};
        int hd = 0;
        for (String[] h : heads) {
            String line = EventNews.headLine(at(Double.parseDouble(h[0]), Double.parseDouble(h[1]), Integer.parseInt(h[2])));
            boolean good = line.contains(h[3]);
            hd += good ? 1 : 0;
            System.out.println("     " + (good ? "ok  " : "MISS") + " " + h[2] + " " + h[3] + ": " + line);
        }
        check(hd >= heads.length - 1, "who runs the town and its province (" + hd + " of " + heads.length + ")", "");

        // 4. A sweep of 400 towns (a point 1 km from each) and 13 years: names never before the town is known.
        int lines = 0;
        int townLines = 0;
        int provLines = 0;
        int headLines = 0;
        int early = 0;
        int anachronism = 0;
        long lookNanos = 0;
        int looks = 0;
        int[] years = {-1000, -300, 300, 800, 1200, 1500, 1700, 1800, 1850, 1900, 1950, 1990, 2026};
        Random r2 = new Random(42);
        for (int i = 0; i < 400; i++) {
            TownFacts.Town pick = tf.town(r2.nextInt(tf.size()));
            double la = pick.lat() + 0.009;
            double lo = pick.lon();
            for (int y : years) {
                var res = at(la, lo, y);
                long a = System.nanoTime();
                var here = EventNews.townHere(res);
                lookNanos += System.nanoTime() - a;
                looks++;
                if (here.isEmpty()) {
                    continue;
                }
                lines++;
                if (!here.get().isSite() || res.site().isEmpty()) {
                    // A town found by its reach must be known by then.
                    if (!here.get().town().existsIn(y)) {
                        early++;
                    }
                }
                // A dated name never shows outside its years.
                String line = EventNews.placeLine(res);
                TownFacts.Town t = here.get().town();
                if (here.get().isSite() && !t.nameIn(y).equals(t.label()) && !line.contains(t.nameIn(y))
                        && res.site().isEmpty()) {
                    anachronism++;
                }
                townLines += EventNews.townLine(res).isBlank() ? 0 : 1;
                provLines += EventNews.provinceLine(res).isBlank() ? 0 : 1;
                headLines += EventNews.headLine(res).isBlank() ? 0 : 1;
            }
        }
        check(early == 0 && anachronism == 0, "no town is named before it is known, and no name outside its years ("
                + lines + " of " + looks + " place-years near 400 towns have a town; " + townLines + " with town facts, "
                + provLines + " with a province, " + headLines + " with a head)", early + " / " + anachronism);
        double perLook = looks == 0 ? 0 : lookNanos / 1000.0d / looks;
        check(perLook < 500.0d, String.format("a town lookup is fast: %.1f microseconds on average (%d lookups)", perLook,
                looks), "");

        // 5. A tour of the world: the place card, its province and head questions, and the state's ties.
        Object[][] tour = {{17.385, 78.4867, 1650}, {17.385, 78.4867, 1900}, {17.385, 78.4867, 2026},
                {18.94, 72.83, 1900}, {48.857, 2.352, 1900}, {48.857, 2.352, 2026}, {35.68, 139.76, 1700},
                {-33.87, 151.21, 1950}, {-12.05, -77.04, 1700}, {30.04, 31.24, 1900}, {55.75, 37.62, 1980},
                {-1.29, 36.82, 1990}, {41.9, 12.49, 1500}, {39.90, 116.40, 1935}, {6.45, 3.39, 2000}};
        int asked = 0;
        for (Object[] t : tour) {
            double la = ((Number) t[0]).doubleValue();
            double lo = ((Number) t[1]).doubleValue();
            int y = (Integer) t[2];
            var res = at(la, lo, y);
            var local = LocalCards.build(res, la, lo);
            KnowledgeCard place = local.placeCard() == null ? null : local.cards().get(local.placeCard());
            KnowledgeCard state = local.rulerCard() == null ? null : local.cards().get(local.rulerCard());
            System.out.println("     " + y + " " + la + "," + lo + ": " + text(place, "what"));
            if (!text(place, "province").isEmpty()) {
                System.out.println("          province: " + text(place, "province"));
            }
            if (!text(place, "head").isEmpty()) {
                System.out.println("          head: " + text(place, "head"));
            }
            if (!text(state, "ties").isEmpty()) {
                System.out.println("          ties: " + text(state, "ties"));
            }
            asked += place != null ? 1 : 0;
        }
        check(asked == tour.length, "every place of the tour has its card", asked + " of " + tour.length);

        // 6. Ties between states.
        StateRelations rel = StateRelations.get();
        String joseon = rel.line("Joseon", 1500);
        String bohemia = rel.line("Kingdom of Bohemia", 1400);
        String hre = rel.line("Holy Roman Empire", 1400);
        String italy = rel.line("Republic of Italy", 1960);
        String gdr = rel.line("German Democratic Republic", 1970);
        String gdr50 = rel.line("German Democratic Republic", 1950);
        String usa1900 = rel.line("United States of America", 1900);
        System.out.println("     Joseon 1500: " + joseon);
        System.out.println("     Bohemia 1400: " + bohemia);
        System.out.println("     Holy Roman Empire 1400: " + hre);
        System.out.println("     Italy 1960: " + italy);
        System.out.println("     East Germany 1970: " + gdr);
        check(rel.loaded() && joseon.contains("allegiance to the Ming Dynasty") && bohemia.contains("vassal of the Holy Roman Empire")
                        && hre.contains("Kingdom of Bohemia is its vassal") && italy.contains("NATO (since 1949)")
                        && gdr.contains("Warsaw Pact") && !gdr50.contains("Warsaw Pact") && usa1900.isEmpty(),
                "ties between states follow the year (" + rel.size() + " ties)", joseon + " / " + bohemia + " / " + gdr);

        System.out.println();
        System.out.println("TOWNS " + (bad == 0 ? "OK" : "FAILED") + ": " + ok + " ok, " + bad + " failed");
        System.exit(bad == 0 ? 0 : 1);
    }
}
