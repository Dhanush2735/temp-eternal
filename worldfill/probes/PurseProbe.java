import com.eternalengine.money.MoneyFormat;
import com.eternalengine.money.MoneyTable;
import com.eternalengine.money.PlayerPurses;
import com.eternalengine.money.PurseService;

import java.util.Map;
import java.util.TreeMap;
import java.util.UUID;

/**
 * Step 19a: the money table and the purse with the mod's real code and data (the ruler register too), no server.
 * Run by worldfill/probe_purse.sh. Exit code 1 if a check fails.
 */
public final class PurseProbe {
    private static int pass;
    private static int fail;

    public static void main(String[] args) {
        MoneyTable t = MoneyTable.get();
        MoneyTable.Summary s = t.summary();
        check("the table loads with no problems (" + s.monies() + " kinds of money, " + s.rows() + " rows, "
                + s.rates() + " rates)", s.loaded() && t.problems().isEmpty(), String.join("; ", t.problems()));
        long t0 = System.nanoTime();
        String self = t.selfTest(MoneyTable.REGISTER);
        long ms = (System.nanoTime() - t0) / 1_000_000L;
        check("the table's self-test (Hyderabad 1948 and a world grid, " + ms + " ms with the ruler register)",
                self == null, self);
        String purse = PurseService.selfTest();
        check("the purse's self-test (typed amounts, words, start money once, never below nothing, save and load)",
                purse == null, purse);

        place("Hyderabad", 17.3616, 78.4747, 1948, "osmania_sicca", "1 rupee");
        place("Mancherial", 18.87, 79.43, 1948, "osmania_sicca", "1 rupee");
        place("Hyderabad", 17.3616, 78.4747, 1918, "osmania_sicca", "5 annas");
        place("Hyderabad", 17.3616, 78.4747, 1958, "osmania_sicca", null);
        place("Hyderabad", 17.3616, 78.4747, 1900, "hali_sicca", null);
        place("Hyderabad", 17.3616, 78.4747, 1800, "sicca", "1 anna 6 pai");
        place("Hyderabad", 17.3616, 78.4747, 1960, "indian_rupee_np", null);
        place("Hyderabad", 17.3616, 78.4747, 1970, "indian_rupee", "2 rupees 50 paise");
        place("Hyderabad", 17.3616, 78.4747, 1600, "hun", "8 kasu");
        place("Hyderabad", 17.3616, 78.4747, 1400, "tanka", "2 jitals");
        place("Hyderabad", 17.3616, 78.4747, 1250, "pana", null);
        place("Hyderabad", 17.3616, 78.4747, 1700, null, null);
        place("Delhi", 28.6139, 77.2090, 1948, "indian_rupee_anna", "15 annas 3 pice");
        place("Delhi", 28.6139, 77.2090, 1600, "mughal_rupee", "2 dams 1 jital");
        place("Delhi", 28.6139, 77.2090, 1300, "tanka", "2 jitals");
        place("Delhi", 28.6139, 77.2090, 1900, "indian_rupee_anna", "3 annas");
        place("Pataliputra", 25.61, 85.14, -250, "pana", "2 mashakas 3 kakanis");
        place("Babylon", 32.54, 44.42, -1750, "silver_weighed", "6 grains of silver");
        place("Thebes", 25.70, 32.65, -1200, "egypt_deben", "4 kite of copper");
        place("Athens", 37.98, 23.73, -430, "drachma", null);
        place("Rome", 41.89, 12.49, 100, "denarius", null);
        place("Constantinople", 41.01, 28.98, 550, "solidus", "12 folles");
        place("Baghdad", 33.31, 44.36, 850, "dirham", "1 dirham");
        place("Istanbul", 41.01, 28.98, 1600, "akce", "10 akçe");
        place("Isfahan", 32.65, 51.67, 1650, "toman", null);
        place("London", 51.507, -0.128, 1800, "pound_lsd", "1 shilling 8 pence");
        place("London", 51.507, -0.128, 1300, "pound_lsd", null);
        place("London", 51.507, -0.128, 1990, "gbp", "35 pounds");
        place("Paris", 48.857, 2.352, 1789, "livre", "1 livre");
        place("Paris", 48.857, 2.352, 2010, "euro", null);
        place("Calais", 50.95, 1.85, 1700, "livre", null);
        place("Dover", 51.13, 1.31, 1700, "pound_lsd", null);
        place("Leipzig", 51.34, 12.37, 1750, "thaler", "6 groschen");
        place("Madrid", 40.42, -3.70, 1600, "peso_real", "3 reales");
        place("Beijing", 39.90, 116.40, 1100, "china_cash", "100 cash");
        place("Beijing", 39.90, 116.40, 1750, "china_cash", "50 cash");
        place("Edo", 35.68, 139.69, 1800, "mon", "250 mon");
        place("Edo", 35.68, 139.69, 1870, "mon", "400 mon");
        place("Tenochtitlan", 19.43, -99.13, 1500, "cacao", "100 cacao beans");
        place("New York", 40.71, -74.00, 1950, "dollar", "8 dollars");
        place("Sydney", -33.87, 151.21, 1500, "barter", "goods worth about 1 day's work");
        place("Timbuktu", 16.77, -3.01, 1500, "cowrie", "200 cowries");
        // step 25: the Malebo Pool's map square was empty; it now takes its neighbours' Kingdom of Kongo, whose
        // nzimbu shells were the money of the Pool's markets (Wikipedia: Kingdom of Kongo, nzimbu)
        place("Kinshasa", -4.32, 15.31, 1500, "nzimbu", null);
        place("Moscow", 55.76, 37.62, 1800, "ruble", "15 kopeks");
        place("the open sea", 0.0, -30.0, 1948, "local_money", "local money worth about 1 day's work");
        place("Oslo", 59.91, 10.75, 1200, "scandi_mark", "5 penninge");
        place("Oslo", 59.91, 10.75, 900, "norse_silver", "0.3 ørtugar of silver");
        place("Leipzig", 51.34, 12.37, 1800, "thaler", null);
        place("Uruk", 31.32, 45.64, -3000, "barter", null);

        MoneyTable.Here unknown = t.at(Double.NaN, Double.NaN, 1948);
        check("an unknown place in 1948 has the year's fallback money (" + unknown.money().id() + ")",
                unknown.money().id().equals("local_money"), unknown.row().id());
        MoneyTable.Here unknownOld = t.at(Double.NaN, Double.NaN, -2500);
        check("an unknown place in 2500 BCE barters", unknownOld.money().barter(), unknownOld.row().id());

        MoneyTable.Money os = t.money("osmania_sicca");
        MoneyTable.Money inr = t.money("indian_rupee_anna");
        same("units of Osmania sicca", MoneyFormat.units(os, 1948), "1 rupee = 16 annas, 1 anna = 12 pai");
        same("units of the Indian rupee", MoneyFormat.units(inr, 1948), "1 rupee = 16 annas, 1 anna = 4 pice, 1 pice = 3 pies");
        same("the O.S. rate in words", PurseService.rateText(t, os, inr, 1948), "7 O.S. rupees = 6 Indian rupees");
        same("units of the denarius in 100 CE", MoneyFormat.units(t.money("denarius"), 100),
                "1 aureus = 25 denarii, 1 denarius = 4 sestertii, 1 sestertius = 4 asses");
        same("units of the akçe in 1500 (no para, no kuruş yet)", MoneyFormat.units(t.money("akce"), 1500), "");
        same("units of the akçe in 1700", MoneyFormat.units(t.money("akce"), 1700),
                "1 kuruş = 40 para, 1 para = 3 akçe");
        same("3.7 kite", MoneyFormat.amount(t.money("egypt_deben"), 37, -1200), "3.7 kite of copper");
        same("1 deben 2.5 kite", MoneyFormat.amount(t.money("egypt_deben"), 125, -1200), "1 deben 2.5 kite of copper");
        same("a shekel and 20 grains", MoneyFormat.amount(t.money("silver_weighed"), 200, -1750),
                "1 shekel 20 grains of silver");
        same("yen in 1990 rounds to whole yen", MoneyFormat.amount(t.money("yen"), 123456, 1990), "1235 yen");
        same("yen in 1930 counts sen", MoneyFormat.amount(t.money("yen"), 150, 1930), "1 yen 50 sen");
        same("barter: half a day", MoneyFormat.amount(t.money("barter"), 50, -3000), "goods worth about half a day's work");
        same("barter: 1¼ days", MoneyFormat.amount(t.money("barter"), 125, -3000), "goods worth about 1¼ days' work");
        same("kurus typed without the accent", String.valueOf(MoneyFormat.parse(t.money("akce"), "1", "kurus", 1700)), "120");
        same("naya paisa typed as two words", String.valueOf(MoneyFormat.parse(t.money("indian_rupee_np"), "5", "naye paise", 1960)), "5");
        same("1.5 rupees", String.valueOf(MoneyFormat.parse(os, "1.5", "rupees", 1948)), "288");

        // What a player reads on /ee purse in Hyderabad, 14 September 1948.
        PlayerPurses purses = new PlayerPurses();
        UUID who = new UUID(1L, 2L);
        MoneyTable.Here hyd = t.at(17.3616, 78.4747, 1948);
        String start = PurseService.startIfNew(purses, who, hyd, 19480914);
        System.out.println();
        System.out.println("/ee purse, Hyderabad, 14 September 1948 (first time):");
        System.out.println("  " + start);
        for (String line : PurseService.describe(t, purses.view(who), hyd)) {
            System.out.println("  " + line);
        }
        check("the start money is a day's pay: 1 rupee of Osmania sicca", start != null
                && start.startsWith("You start with 1 rupee (Osmania sicca)") && purses.view(who).amount("osmania_sicca") == 192,
                start);
        purses.add(who, "indian_rupee_anna", 72);
        purses.add(who, "denarius", 40);
        System.out.println("  ... with 6 Indian annas and 2 denarii 8 asses added:");
        for (String line : PurseService.describe(t, purses.view(who), hyd)) {
            System.out.println("  " + line);
        }
        String all = String.join(" ", PurseService.describe(t, purses.view(who), hyd));
        check("Indian rupees count as taken in Hyderabad; denarii do not",
                all.contains("Your purse: 1 rupee (Osmania sicca); 6 annas (Indian rupee)")
                        && all.contains("Not taken here: 2 denarii 2 sestertii (Roman denarius)"), all);
        check("no player line names a source or says estimate",
                !all.toLowerCase().contains("wiki") && !all.toLowerCase().contains("estimate")
                        && !all.toLowerCase().contains("enquiry"), all);
        MoneyTable.Here syd = t.at(-33.87, 151.21, 1500);
        System.out.println("/ee purse, Sydney 1500 (first time):");
        UUID other = new UUID(3L, 4L);
        System.out.println("  " + PurseService.startIfNew(purses, other, syd, 15000701));
        for (String line : PurseService.describe(t, purses.view(other), syd)) {
            System.out.println("  " + line);
        }
        MoneyTable.Here sea = t.at(0.0, -30.0, 1948);
        UUID third = new UUID(5L, 6L);
        System.out.println("/ee purse, the open sea 1948 (first time):");
        System.out.println("  " + PurseService.startIfNew(purses, third, sea, 19480914));
        for (String line : PurseService.describe(t, purses.view(third), sea)) {
            System.out.println("  " + line);
        }
        MoneyTable.Here bab = t.at(32.54, 44.42, -1750);
        System.out.println("Money in Babylon, 1750 BCE: " + PurseService.moneyHere(t, bab));
        System.out.println("Money in Rome, 100 CE: " + PurseService.moneyHere(t, t.at(41.89, 12.49, 100)));
        System.out.println("Money in London, 1800: " + PurseService.moneyHere(t, t.at(51.507, -0.128, 1800)));

        // How often each row wins on a world grid, and the time per lookup.
        Map<String, Integer> used = new TreeMap<>();
        long n = 0;
        long start2 = System.nanoTime();
        for (int year = -3000; year <= 2026; year += 25) {
            for (int lat = -55; lat <= 70; lat += 5) {
                for (int lon = -175; lon <= 180; lon += 5) {
                    used.merge(t.at(lat + 0.25, lon + 0.25, year).row().id(), 1, Integer::sum);
                    n++;
                }
            }
        }
        double us = (System.nanoTime() - start2) / 1000.0 / n;
        int rowsUsed = used.size();
        System.out.printf("%n%,d lookups, %.1f microseconds each; %d of %d rows used on the grid%n", n, us, rowsUsed,
                t.rows().size());
        StringBuilder never = new StringBuilder();
        for (MoneyTable.Row r : t.rows()) {
            if (!used.containsKey(r.id())) {
                never.append(r.id()).append(' ');
            }
        }
        System.out.println("rows never used on the 5-degree grid: " + never);
        check("a lookup takes under 200 microseconds", us < 200.0, String.format("%.1f", us));

        System.out.println();
        System.out.println("PurseProbe: " + pass + " passed, " + fail + " failed");
        System.exit(fail == 0 ? 0 : 1);
    }

    private static void place(String name, double lat, double lon, int year, String money, String day) {
        MoneyTable.Here h = MoneyTable.get().at(lat, lon, year);
        String dayText = MoneyFormat.amount(h.money(), h.dayPay(), year);
        String ruler = MoneyTable.REGISTER.at(lat, lon, year);
        String what = name + " " + (year < 0 ? -year + " BCE" : String.valueOf(year)) + ": " + h.money().name() + " ["
                + h.money().id() + ", row " + h.row().id() + ", ruler " + ruler + "], a day's work " + dayText;
        boolean ok = (money == null || h.money().id().equals(money)) && (day == null || dayText.equals(day));
        check(what, ok, "expected " + money + (day == null ? "" : " / " + day));
    }

    private static void same(String what, String got, String want) {
        check(what + ": \"" + got + "\"", got.equals(want), "expected \"" + want + "\"");
    }

    private static void check(String what, boolean ok, String why) {
        if (ok) {
            pass++;
            System.out.println("[ OK ] " + what);
        } else {
            fail++;
            System.out.println("[FAIL] " + what + "  -- " + why);
        }
    }
}
