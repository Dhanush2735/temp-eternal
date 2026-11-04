import com.eternalengine.civilization.CultureAtlas;
import com.eternalengine.civilization.EventNews;
import com.eternalengine.civilization.HistoricalPresence;
import com.eternalengine.civilization.SettlementRank;
import com.eternalengine.knowledge.KnowledgeCard;
import com.eternalengine.knowledge.KnowledgeDate;
import com.eternalengine.knowledge.LocalCards;

import java.util.List;
import java.util.Random;

/**
 * Step 30b (C13, C14, C17, C26, C27): reading and scripts, measures, wealth and hard times, holy places, festivals and
 * pilgrimages, at a tour of places and years, and the feast days by the calendar; a sweep of the world for gaps.
 */
public final class CultureProbe {
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

    public static void main(String[] args) {
        long t0 = System.nanoTime();
        CultureAtlas c = CultureAtlas.get();
        check(c.loaded(), "the culture data loads: " + c.summary() + " (" + (System.nanoTime() - t0) / 1_000_000 + " ms)",
                String.valueOf(c.problem()));

        // 1. Reading.
        double[] ind1901 = c.literacy(20.0, 78.0, 1901, SettlementRank.TOWN);
        double[] cusco = c.literacy(-13.52, -71.97, 1500, SettlementRank.CITY);
        double[] lon1700 = c.literacy(51.507, -0.128, 1700, SettlementRank.CITY);
        double[] rome100 = c.literacy(41.9, 12.49, 100, SettlementRank.CITY);
        System.out.printf("     India 1901 %.3f (men %.3f, women %.3f); Cusco 1500 %.3f; London 1700 %.2f; Rome 100 %.2f%n",
                ind1901[0], ind1901[1], ind1901[2], cusco[0], lon1700[0], rome100[0]);
        check(Math.abs(ind1901[0] - 0.062) < 0.01 && ind1901[1] > ind1901[2] && cusco[0] == 0.0 && lon1700[0] > 0.5
                && rome100[0] > 0.05 && rome100[0] < 0.2, "who reads: India 1901 about 6% (the census, men more than women), "
                + "nobody in Cusco 1500, most of London 1700, about one in ten in Rome in 100", "");
        String tr1900 = c.scriptOf("Turkish", 1900);
        String tr1950 = c.scriptOf("Turkish", 1950);
        String az1950 = c.scriptOf("North Azerbaijani", 1950);
        String te = c.scriptOf("Telugu", 1900);
        String zh = c.scriptOf("Mandarin Chinese", 1970);
        System.out.println("     scripts: Turkish 1900 " + tr1900 + ", 1950 " + tr1950 + "; Azerbaijani 1950 " + az1950
                + "; Telugu " + te + "; Mandarin 1970 " + zh);
        check(tr1900.contains("Arabic") && tr1950.contains("Latin") && az1950.contains("Cyrillic") && te.contains("Telugu")
                && zh.contains("simplified"), "scripts by year: Turkish from Arabic to Latin letters in 1928, Azerbaijani in "
                + "Cyrillic under the Soviets, Telugu in its own script, Chinese simplified from 1956", "");

        // 2. Measures.
        String hyd1900 = c.measureLine(17.385, 78.4867, 1900);
        String hyd1970 = c.measureLine(17.385, 78.4867, 1970);
        String hyd2026 = c.measureLine(17.385, 78.4867, 2026);
        String mos1900 = c.measureLine(55.75, 37.62, 1900);
        String usa2000 = c.measureLine(40.71, -74.0, 2000);
        String lag1800 = c.measureLine(6.45, 3.39, 1800);
        System.out.println("     Hyderabad 1900: " + hyd1900);
        System.out.println("     Hyderabad 1970: " + hyd1970);
        System.out.println("     Moscow 1900: " + mos1900);
        System.out.println("     New York 2000: " + usa2000);
        System.out.println("     Lagos 1800: " + lag1800);
        check(hyd1900.contains("kos") && hyd1900.contains("seer") && hyd1970.contains("still") && hyd2026.contains("metres")
                && mos1900.contains("verst") && usa2000.contains("mile") && !lag1800.contains("mile"),
                "measures by land and year: kos and seer in Hyderabad 1900, the metric law of 1956 with the old words in "
                        + "the market, metres today; versts in Moscow 1900; miles in New York 2000; no English miles in "
                        + "Lagos 1800", "");

        // 3. Wealth and hard times.
        String ind1900 = c.wealthLine(20.0, 78.0, 1900);
        String usa2000w = c.wealthLine(40.71, -74.0, 2000);
        String ger1923 = c.wealthLine(52.52, 13.40, 1923);
        String usa1932 = c.wealthLine(40.71, -74.0, 1932);
        String zwe2008 = c.wealthLine(-17.83, 31.05, 2008);
        System.out.println("     India 1900: " + ind1900);
        System.out.println("     Berlin 1923: " + ger1923);
        check(ind1900.contains("poor") && usa2000w.contains("rich") && ger1923.contains("Prices rise")
                && usa1932.contains("no work") && zwe2008.contains("Prices double"), "wealth and hard times: India 1900 poor, "
                + "the United States rich in 2000; Germany's inflation of 1923, the Depression of 1932, Zimbabwe 2008", "");

        // 4. Holy places, festivals, pilgrimages, feasts.
        List<CultureAtlas.Holy> hyd = c.holyPlacesNear(17.36, 78.47, 2000, 12, 5);
        List<CultureAtlas.Holy> par = c.holyPlacesNear(48.853, 2.35, 1900, 6, 3);
        System.out.println("     holy places Hyderabad 2000: " + hyd.stream().map(CultureAtlas.Holy::name).toList());
        System.out.println("     holy places Paris 1900: " + par.stream().map(CultureAtlas.Holy::name).toList());
        boolean meccaMasjid = hyd.stream().anyMatch(h -> h.name().contains("Mecca Masjid"));
        boolean notreDame = par.stream().anyMatch(h -> h.name().contains("Notre-Dame"));
        List<CultureAtlas.Holy> hyd1500 = c.holyPlacesNear(17.36, 78.47, 1500, 12, 5);
        check(meccaMasjid && notreDame && hyd1500.stream().noneMatch(h -> h.name().contains("Mecca Masjid")),
                "holy places: the Mecca Masjid in Hyderabad (not in 1500, before it was built), Notre-Dame in Paris", "");
        String christmas = c.holyLine(51.507, -0.128, 1900, 12, 25, List.of("Anglicanism"), 12);
        String eid = c.holyLine(30.04, 31.24, 2024, 4, 10, List.of("Sunni Islam"), 12);
        String easter = c.holyLine(41.9, 12.49, 2026, 4, 5, List.of("Catholic Christianity"), 12);
        String orthodoxChristmas = c.holyLine(55.75, 37.62, 2000, 1, 7, List.of("Orthodox Christianity"), 12);
        System.out.println("     London, Christmas Day 1900: " + christmas);
        System.out.println("     Cairo, 10 April 2024: " + eid);
        System.out.println("     Rome, 5 April 2026: " + easter);
        check(christmas.contains("Christmas") && eid.contains("Eid al-Fitr") && easter.contains("Easter Sunday")
                && orthodoxChristmas.contains("Christmas"), "feast days by the calendar: Christmas in London 1900, Eid "
                + "al-Fitr in Cairo on 10 April 2024, Easter in Rome on 5 April 2026, Orthodox Christmas in Moscow on 7 "
                + "January 2000", orthodoxChristmas);

        // 5. A tour of the world: the four new questions.
        Object[][] tour = {{17.385, 78.4867, 1650}, {17.385, 78.4867, 1948}, {17.385, 78.4867, 2026}, {-13.52, -71.97, 1500},
                {51.507, -0.128, 1700}, {41.9, 12.49, 100}, {39.90, 116.40, 1100}, {35.68, 139.76, 1850},
                {30.04, 31.24, 1300}, {25.31, 83.01, 1800}, {6.45, 3.39, 1960}, {40.71, -74.0, 1950}, {21.42, 39.83, 1900},
                {55.75, 37.62, 1700}, {-33.87, 151.21, 1900}, {33.31, 44.36, 900}};
        int answered = 0;
        int asked = 0;
        for (Object[] t : tour) {
            double la = ((Number) t[0]).doubleValue();
            double lo = ((Number) t[1]).doubleValue();
            int y = (Integer) t[2];
            var res = HistoricalPresence.query(null, la, lo, y);
            var local = LocalCards.build(res, la, lo);
            KnowledgeCard place = local.placeCard() == null ? null : local.cards().get(local.placeCard());
            System.out.println("     == " + y + " " + la + "," + lo);
            for (String q : new String[]{"read", "measure", "wealth", "holy"}) {
                String a = text(place, q);
                asked++;
                if (!a.isEmpty()) {
                    answered++;
                    System.out.println("        " + q + ": " + a);
                }
            }
        }
        check(answered >= asked * 3 / 4, "a tour of 16 places: " + answered + " of " + asked + " of the new questions have an "
                + "answer", "");

        // 6. A sweep: every land point has an answer for reading and measures.
        Random r = new Random(30);
        int pts = 0;
        int read = 0;
        int meas = 0;
        long s0 = System.nanoTime();
        while (pts < 400) {
            double la = -45 + r.nextDouble() * 110;
            double lo = -170 + r.nextDouble() * 340;
            if (com.eternalengine.civilization.CountryGrid.get().indexAt(la, lo) < 0) {
                continue;
            }
            pts++;
            int y = -1000 + r.nextInt(3026);
            if (c.literacy(la, lo, y, SettlementRank.TOWN) != null) {
                read++;
            }
            if (!c.measureLine(la, lo, y).isEmpty()) {
                meas++;
            }
        }
        double ms = (System.nanoTime() - s0) / 1e6 / pts;
        check(read >= pts * 95 / 100 && meas == pts, "a sweep of " + pts + " land points in random years: reading known "
                + "for " + read + ", measures for " + meas + String.format(" (%.2f ms a point)", ms), "");

        System.out.println();
        System.out.println("CULTURE " + (bad == 0 ? "OK" : "FAILED") + ": " + ok + " ok, " + bad + " failed");
        System.exit(bad == 0 ? 0 : 1);
    }
}
