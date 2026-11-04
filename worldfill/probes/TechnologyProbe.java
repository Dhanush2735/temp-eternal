import com.eternalengine.civilization.CountryGrid;
import com.eternalengine.civilization.EventNews;
import com.eternalengine.civilization.HistoricalPresence;
import com.eternalengine.civilization.SettlementRank;
import com.eternalengine.knowledge.KnowledgeCard;
import com.eternalengine.knowledge.KnowledgeDate;
import com.eternalengine.knowledge.LocalCards;
import com.eternalengine.technology.TechnologyAtlas;
import com.eternalengine.vehicle.VehicleType;

import java.util.Random;

/**
 * Step 30a (C16): the technology atlas and the country grid.
 *
 * <p>The grid finds the right country (coasts and enclaves too); the atlas loads; the five places of TECHNOLOGY_PLAN.md;
 * how common household things are (CHAT's figures); the Americas and Australia before contact; the spread inside big
 * countries (Bombay before Hyderabad, Saint Petersburg long before Vladivostok); a sweep of the world: nothing before
 * its first year or before what it needs; what villagers say at a tour of places; the fastest way to travel by place;
 * the speed.
 */
public final class TechnologyProbe {
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
        CountryGrid grid = CountryGrid.get();
        TechnologyAtlas atlas = TechnologyAtlas.get();
        System.out.println("     loaded in " + (System.nanoTime() - t0) / 1_000_000 + " ms");
        String[][] where = {{"17.385", "78.4867", "IND"}, {"-4.32", "15.31", "COD"}, {"-4.27", "15.27", "COG"},
                {"-29.31", "27.48", "LSO"}, {"43.94", "12.45", "SMR"}, {"18.94", "72.82", "IND"},
                {"13.08", "80.29", "IND"}, {"-33.86", "151.21", "AUS"}, {"64.15", "-21.95", "ISL"},
                {"21.31", "-157.86", "USA"}, {"4.92", "-52.32", "FRA"}, {"1.29", "103.85", "SGP"}};
        int right = 0;
        StringBuilder wrong = new StringBuilder();
        for (String[] w : where) {
            String got = grid.codeAt(Double.parseDouble(w[0]), Double.parseDouble(w[1]));
            if (got.equals(w[2])) {
                right++;
            } else {
                wrong.append(w[0]).append(",").append(w[1]).append("=").append(got).append(" ");
            }
        }
        check(grid.loaded() && right == where.length, "the country grid: " + grid.size() + " countries, " + right + " of "
                + where.length + " places right (coasts: Madras, Sydney, Honolulu, Cayenne, Singapore)", wrong.toString());
        check(atlas.loaded() && atlas.size() >= 120, "the atlas: " + atlas.summary(), String.valueOf(atlas.problem()));

        // 1. The five places of the plan.
        Object[][] plan = {
                {17.385, 78.4867, 1948, "railway", true}, {17.385, 78.4867, 1948, "car", true},
                {17.385, 78.4867, 1948, "radio", true}, {17.385, 78.4867, 1948, "television", false},
                {17.385, 78.4867, 1500, "paper", true}, {17.385, 78.4867, 1500, "printing_press", false},
                {-13.52, -71.97, 1500, "iron", false}, {-13.52, -71.97, 1500, "wheel", false},
                {-13.52, -71.97, 1500, "horses", false}, {51.507, -0.128, 1700, "printing_press", true},
                {51.507, -0.128, 1700, "steam_engine", false}, {39.90, 116.40, 1100, "woodblock", true},
                {39.90, 116.40, 1100, "gunpowder", true}};
        int good = 0;
        StringBuilder detail = new StringBuilder();
        for (Object[] p : plan) {
            boolean got = atlas.present((String) p[3], ((Number) p[0]).doubleValue(), ((Number) p[1]).doubleValue(),
                    (Integer) p[2], SettlementRank.CITY);
            if (got == (Boolean) p[4]) {
                good++;
            } else {
                detail.append(p[3]).append(" ").append(p[2]).append(" ");
            }
        }
        check(good == plan.length, "the five places of the plan (" + good + " of " + plan.length + ")", detail.toString());

        // 2. How common.
        double carsHyd = atlas.share(atlas.tech("car"), 17.385, 78.4867, 1948, SettlementRank.CITY);
        double carsUsa = atlas.share(atlas.tech("car"), 41.88, -87.63, 1930, SettlementRank.CITY);
        double tvUk = atlas.share(atlas.tech("television"), 51.507, -0.128, 1965, SettlementRank.CITY);
        double tvInd = atlas.share(atlas.tech("television"), 18.94, 72.83, 1990, SettlementRank.CITY);
        double mobInd = Math.max(atlas.share(atlas.tech("mobile_phone"), 18.94, 72.83, 2026, SettlementRank.CITY),
                atlas.share(atlas.tech("smartphone"), 18.94, 72.83, 2026, SettlementRank.CITY));
        double smartVil = atlas.share(atlas.tech("smartphone"), 25.0, 80.0, 2012, SettlementRank.VILLAGE);
        System.out.printf("     cars Hyderabad 1948 %.4f, Chicago 1930 %.2f; TV London 1965 %.2f, Bombay 1990 %.2f; "
                + "mobile Bombay 2026 %.2f; smartphones in an Indian village 2012 %.3f%n", carsHyd, carsUsa, tvUk, tvInd,
                mobInd, smartVil);
        check(carsHyd < 0.02 && carsHyd > 0.0005 && carsUsa > 0.3 && tvUk > 0.5 && tvInd > 0.05 && tvInd < 0.6
                && mobInd > 0.8 && smartVil < 0.2, "how common: cars for a few in Hyderabad 1948, many in Chicago 1930; "
                + "television in most London homes 1965, some in Bombay 1990; mobiles nearly everywhere in Bombay 2026", "");

        // 3. The Americas, Australia and New Zealand before contact; uninhabited Iceland.
        Random rnd = new Random(30);
        int early = 0;
        int tried = 0;
        String[] oldWorld = {"iron", "wheel", "horses", "printing_press", "gunpowder", "glass", "plough", "steel", "paper"};
        for (int i = 0; i < 400; i++) {
            double la = -50 + rnd.nextDouble() * 110;
            double lo = -165 + rnd.nextDouble() * 130;
            if (atlas.countryAt(la, lo) < 0) {
                continue;
            }
            tried++;
            for (String id : oldWorld) {
                if (id.equals("paper") && la > 13 && la < 22 && lo > -99 && lo < -86) {
                    continue;   // Mesoamerica made bark paper of its own
                }
                if (atlas.present(id, la, lo, 1491, SettlementRank.CITY)) {
                    early++;
                    System.out.println("     early: " + id + " at " + la + "," + lo + " (" + grid.codeAt(la, lo) + ")");
                }
            }
        }
        for (String id : oldWorld) {
            early += atlas.present(id, -33.87, 151.21, 1787, SettlementRank.CITY) ? 1 : 0;
            early += atlas.present(id, 64.15, -21.95, 850, SettlementRank.CITY) ? 1 : 0;
        }
        check(early == 0, "nothing from the Old World anywhere in the Americas in 1491 (" + tried + " land points), in "
                + "Sydney in 1787, or in Iceland before its settlers (850)", early + " found");

        // 4. Spread inside a big country.
        int railBom = atlas.arrivalAt(atlas.tech("railway"), 18.94, 72.83);
        int railHyd = atlas.arrivalAt(atlas.tech("railway"), 17.385, 78.4867);
        int railSpb = atlas.arrivalAt(atlas.tech("railway"), 59.93, 30.32);
        int railVla = atlas.arrivalAt(atlas.tech("railway"), 43.12, 131.89);
        int elecDel = atlas.arrivalAt(atlas.tech("electricity"), 28.61, 77.21);
        System.out.println("     railway: Bombay " + railBom + ", Hyderabad " + railHyd + ", Saint Petersburg " + railSpb
                + ", Vladivostok " + railVla + "; electric light Delhi " + elecDel);
        check(railBom == 1853 && railHyd > 1860 && railHyd < 1885 && railSpb == 1837 && railVla > 1870,
                "spread inside big countries: Bombay 1853, Hyderabad in the 1860s-1880s (it came in 1874); Saint "
                        + "Petersburg 1837, Vladivostok decades later", "");

        // 5. A sweep: nothing before its first year, nothing before what it needs at that very place.
        int[] years = {-2500, -1000, 0, 500, 1000, 1300, 1500, 1700, 1850, 1900, 1950, 2000, 2026};
        int problems = 0;
        int points = 0;
        long presentCount = 0;
        Random r2 = new Random(42);
        while (points < 500) {
            double la = -45 + r2.nextDouble() * 110;
            double lo = -170 + r2.nextDouble() * 340;
            if (atlas.countryAt(la, lo) < 0) {
                continue;
            }
            points++;
            for (int y : years) {
                for (var t : atlas.all()) {
                    int a = atlas.arrivalAt(t, la, lo);
                    if (a != TechnologyAtlas.NEVER && a < t.first) {
                        problems++;
                    }
                    if (atlas.present(t, la, lo, y, SettlementRank.TOWN)) {
                        presentCount++;
                        if (y < t.first) {
                            problems++;
                        }
                    }
                }
            }
        }
        check(problems == 0, "a sweep of " + points + " land points in " + years.length + " years: nothing before its "
                + "first year anywhere (" + presentCount + " technology-town-years found)", problems + " problems");

        // 6. What villagers say.
        Object[][] tour = {{17.385, 78.4867, 1948}, {17.385, 78.4867, 1500}, {17.385, 78.4867, 2026},
                {-13.52, -71.97, 1500}, {-13.52, -71.97, 1900}, {51.507, -0.128, 1700}, {51.507, -0.128, 1900},
                {39.90, 116.40, 1100}, {35.68, 139.76, 1850}, {35.68, 139.76, 1880}, {30.04, 31.24, 1300},
                {6.45, 3.39, 1960}, {-33.87, 151.21, 1800}, {40.71, -74.0, 1950}, {55.75, 37.62, 1700},
                {41.9, 12.49, 100}, {-1.29, 36.82, 2010}, {9.03, 38.74, 1920}};
        String hyd48 = "";
        String cusco = "";
        for (Object[] t : tour) {
            double la = ((Number) t[0]).doubleValue();
            double lo = ((Number) t[1]).doubleValue();
            int y = (Integer) t[2];
            var res = HistoricalPresence.query(null, la, lo, y);
            String line = EventNews.technologyLine(res);
            System.out.println("     " + y + " " + la + "," + lo + " (" + EventNews.settlementRank(res) + "): " + line);
            if (la == 17.385 && y == 1948) {
                hyd48 = line;
            }
            if (la == -13.52 && y == 1500) {
                cusco = line;
            }
        }
        check(hyd48.contains("the railway") && hyd48.contains("television") && cusco.contains("iron"),
                "villagers say what is new and what is not here yet (Hyderabad 1948, Cusco 1500)", hyd48 + " / " + cusco);
        var local = LocalCards.build(HistoricalPresence.query(null, 17.385, 78.4867, 1948), 17.385, 78.4867);
        var card = local.placeCard() == null ? null : local.cards().get(local.placeCard());
        check(!text(card, "tech").isEmpty(), "the place card has \"What new things are there here?\"", "");

        // 7. Vehicles by place.
        VehicleType b1850 = VehicleType.fastestLandAt(18.94, 72.83, 1850);
        VehicleType b1870 = VehicleType.fastestLandAt(18.94, 72.83, 1870);
        VehicleType k1900 = VehicleType.fastestLandAt(34.53, 69.17, 1900);
        VehicleType c1500 = VehicleType.fastestLandAt(-13.52, -71.97, 1500);
        System.out.println("     fastest: Bombay 1850 " + b1850 + ", 1870 " + b1870 + "; Kabul 1900 " + k1900 + "; Cusco 1500 "
                + c1500);
        check(b1850 != VehicleType.TRAIN && b1870 == VehicleType.TRAIN && k1900 != VehicleType.TRAIN
                && c1500 == VehicleType.CARAVAN, "the fastest way to travel follows the place (and Cusco 1500 has no horses "
                + "or carts: on foot with llamas)", b1850 + " " + b1870 + " " + k1900 + " " + c1500);

        // 8. Speed.
        long s0 = System.nanoTime();
        int n = 0;
        for (int i = 0; i < 300; i++) {
            atlas.talkLine(10 + i * 0.1, 20 + i * 0.2, 1500 + i, SettlementRank.TOWN);
            n++;
        }
        double ms = (System.nanoTime() - s0) / 1e6 / n;
        check(ms < 5.0, String.format("a talk line takes %.2f ms", ms), "");

        System.out.println();
        System.out.println("TECHNOLOGY " + (bad == 0 ? "OK" : "FAILED") + ": " + ok + " ok, " + bad + " failed");
        System.exit(bad == 0 ? 0 : 1);
    }
}
