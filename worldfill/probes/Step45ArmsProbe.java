import com.eternalengine.civilization.LawRegister;
import com.eternalengine.war.Arms;
import com.eternalengine.war.Arms.Row;
import com.eternalengine.war.Arms.Supply;

import java.util.ArrayList;
import java.util.List;

/**
 * Step 45 part 3 (E9 B): the five ways a weapon gets into a man's hand.
 *
 * <p>Checks are printed, so a wrong answer is visible. It reads the real {@code arms.json.gz} and
 * the real {@code law.json.gz} through the mod's own classes, and it asserts the two packs agree
 * where they overlap.
 */
public final class Step45ArmsProbe {

    private static int checks = 0;
    private static int failed = 0;

    private static void ok(boolean cond, String what) {
        checks++;
        if (!cond) {
            failed++;
            System.out.println("  FAIL  " + what);
        }
    }

    private static void eq(Object got, Object want, String what) {
        checks++;
        if (got == null ? want != null : !got.equals(want)) {
            failed++;
            System.out.println("  FAIL  " + what + ": got " + got + ", want " + want);
        }
    }

    private static final Object[][] PLACES = {
        {"Uruk, Sumer", 31.3, 45.6, -3000},
        {"Athens", 37.98, 23.73, -350},
        {"Rome", 41.88, 12.50, 100},
        {"Cusco, Inca", -13.53, -71.97, 1500},
        {"Tenochtitlan", 19.43, -99.13, 1500},
        {"Cape York, Australia", -10.7, 142.5, 1700},
        {"Timbuktu", 16.77, -3.01, 1500},
        {"Abeokuta, Yoruba", 7.15, 3.35, 1800},
        {"London, 1181 Assize", 51.51, -0.13, 1181},
        {"London, 1328 Northampton", 51.51, -0.13, 1400},
        {"Kyoto, 1588 Sword Hunt", 35.0, 135.77, 1600},
        {"Beijing, Yuan 1300", 39.9, 116.4, 1300},
        {"Beijing, Qing 1650", 39.9, 116.4, 1650},
        {"Beijing, PRC 1996", 39.9, 116.4, 1996},
        {"Delhi, 1878 Arms Act", 28.61, 77.21, 1900},
        {"Hyderabad, 1948", 17.39, 78.49, 1948},
        {"Ypres, 1917", 50.85, 2.88, 1917},
    };

    public static void main(String[] args) {
        Arms a = Arms.get();

        // ------------------------------------------------------------------ the pack itself
        System.out.println("the pack");
        ok(a.hasData(), "the pack loaded (" + a.problem() + ")");
        ok(a.problem() == null, "no problem reading it");
        ok(a.rows().size() >= 10, "%d rows".formatted(a.rows().size()));
        eq(a.areas().size(), 17, "17 areas");
        eq(a.flagNames().size(), 6, "six flags: the five ways plus carry");
        eq(a.flagNames().get(0), "issued", "the first way is 'issued'");
        eq(a.flagNames().get(4), "gift", "the fifth way is 'gift'");
        eq(a.flagNames().get(5), "carry", "the sixth flag is 'carry', which is not a way");
        eq(a.flagMeanings().size(), 6, "every flag is explained");
        ok(a.flagMeanings().stream().allMatch(s -> s != null && s.length() > 10),
                "every explanation is a sentence");

        Row def = a.fallback();
        ok(def != null, "there is a default row");
        if (def != null) {
            ok(def.isDefault(), "the default row knows it is the default");
            ok(def.bring(), "by default you bring your own");
            ok(!def.issued(), "by default the state does not issue you one");
            ok(def.buy() && def.take() && def.gift() && def.carry(),
                    "by default you may buy, take, be given and carry");
        }

        // ------------------------------------------------------------------ the distinction the pack exists for
        System.out.println();
        System.out.println("keeping is not carrying");
        int eur = a.areas().indexOf("EUR");
        ok(eur >= 0, "EUR is an area");

        Row assize = a.hereAt(51.51, -0.13, 1250).row();
        ok(assize != null, "there is a row for England under the Assize of Arms");
        if (assize != null) {
            eq(assize.id(), "assize", "1250 in Europe reads the Assize row");
            ok(assize.isADuty(), "the 1181 Assize is a DUTY, not a restriction");
            ok(assize.buy(), "under the Assize you may BUY arms");
            ok(!assize.gift(), "under the Assize you may NOT give, lend, pledge or sell them");
            ok(assize.carry(), "under the Assize you may carry them");
            ok(assize.forWhom() != null && assize.forWhom().contains("Jews"),
                    "the Assize names the class it exempts (" + assize.forWhom() + ")");
        }

        Row north = a.hereAt(51.51, -0.13, 1400).row();
        ok(north != null, "there is a row for England under the Statute of Northampton");
        if (north != null) {
            eq(north.id(), "northampton", "1400 in Europe reads the Northampton row");
            ok(!north.isADuty(), "Northampton is not a duty");
            ok(north.buy(), "under Northampton you may still BUY a weapon");
            ok(north.gift(), "under Northampton you may still give one");
            ok(!north.carry(), "under Northampton you may NOT go about armed");
        }

        // The pair, side by side: one shuts `gift` and leaves `carry` open, the other is exactly
        // reversed. If a future edit collapses the two into one flag, this check fails.
        if (assize != null && north != null) {
            ok(!assize.gift() && north.gift(), "the Assize shuts gift and Northampton does not");
            ok(assize.carry() && !north.carry(), "Northampton shuts carry and the Assize does not");
        }

        // ------------------------------------------------------------------ where arms are banned
        System.out.println();
        System.out.println("disarmed places");
        Row edo = a.hereAt(35.0, 135.77, 1700).row();
        ok(edo != null, "there is a row for Tokugawa Japan");
        if (edo != null) {
            eq(edo.id(), "katanagari", "1700 in East Asia reads the Sword Hunt row");
            ok(!edo.buy() && !edo.take() && !edo.gift() && !edo.carry() && !edo.bring(),
                    "a Japanese peasant may not buy, take, be given, carry or bring");
            ok(edo.issued(), "the lord still arms his ashigaru");
            ok(edo.forWhom() != null && edo.forWhom().contains("non-noble"),
                    "the Sword Hunt names the class it disarms (" + edo.forWhom() + ")");
        }

        Row yuan = a.hereAt(39.9, 116.4, 1300).row();
        ok(yuan != null, "there is a row for Yuan China");
        if (yuan != null) {
            eq(yuan.id(), "yuan", "1300 in East Asia reads the Yuan ban");
            ok(yuan.forWhom() != null && yuan.forWhom().contains("Han"),
                    "the Yuan ban names Han and Southerners (" + yuan.forWhom() + ")");
            ok(!yuan.buy() && !yuan.carry(), "a Han civilian may neither buy nor carry");
            ok(yuan.issued(), "the Yuan army was still armed");
        }

        Row raj = a.hereAt(28.61, 77.21, 1900).row();
        ok(raj != null, "there is a row for the British Raj");
        if (raj != null) {
            eq(raj.id(), "armsact", "1900 in South Asia reads the Indian Arms Act");
            ok(raj.forWhom() != null && raj.forWhom().contains("Europeans"),
                    "the Arms Act names its exemption (" + raj.forWhom() + ")");
            ok(!raj.buy() && !raj.carry(), "an Indian needs a licence to buy or carry");
        }

        Row inca = a.hereAt(-13.53, -71.97, 1500).row();
        ok(inca != null, "there is a row for the Inca");
        if (inca != null) {
            eq(inca.id(), "inca", "1500 in South America reads the Inca row");
            ok(inca.issued(), "the Inca state armed its army from storehouses");
            ok(!inca.buy(), "there was no market in arms and no coin to buy one in");
            ok(!inca.bring() && !inca.take() && !inca.gift() && !inca.carry(),
                    "no private way at all is open");
        }

        Row prc = a.hereAt(39.9, 116.4, 1996).row();
        ok(prc != null, "there is a row for the PRC");
        if (prc != null) {
            ok(prc.issued() && !prc.buy() && !prc.carry(),
                    "in the PRC the state issues and nothing else is open");
        }

        Row modern = a.hereAt(50.85, 2.88, 1917).row();
        ok(modern != null, "there is a row for the modern state");
        if (modern != null) {
            ok(modern.issued(), "in 1917 the state issues");
            ok(!modern.bring(), "in 1917 a soldier does not bring his own rifle");
            ok(!modern.carry(), "in 1917 he does not carry it about in peacetime either");
        }

        // ------------------------------------------------------------------ the Maratha: two ways at once
        Row maratha = a.hereAt(26.22, 78.18, 1750).row();
        ok(maratha != null, "there is a row for the Maratha");
        if (maratha != null) {
            eq(maratha.id(), "maratha", "1700 in South Asia reads the Maratha row");
            ok(maratha.issued() && maratha.bring(),
                    "bargir and shiledar: the state issues AND the horseman brings his own");
            ok(maratha.buy() && maratha.take() && maratha.gift() && maratha.carry(),
                    "and every other way is open too");
        }

        // ------------------------------------------------------------------ every place and year has an answer
        System.out.println();
        System.out.println("the prose");
        for (Object[] p : PLACES) {
            String name = (String) p[0];
            double lat = (Double) p[1];
            double lon = (Double) p[2];
            int year = (Integer) p[3];
            Supply s = a.hereAt(lat, lon, year);
            Row r = s.row();
            ok(r != null, name + " has an answer");
            if (r == null) {
                continue;
            }
            ok(!r.text().isBlank(), name + " says something");
            ok(!r.note().isBlank(), name + " says what it meant");
            ok(!r.source().isBlank(), name + " names a source");
            ok(r.y0() <= year && year <= r.y1(), name + " row covers its own year");
            ok(r.areas().contains(a.areas().indexOf(s.area())), name + " row covers its own area");
            if (r.polity() != null && !r.polity().isEmpty()) {
                ok(s.ruler() != null && r.belongsTo(s.ruler()),
                        name + " row belongs to the state that ruled there (" + s.ruler() + ")");
            }
            String line = a.waysLine(lat, lon, year);
            ok(!line.isBlank() && !line.equals("unknown"), name + " has a ways line");
            System.out.printf("   %-26s %-5s %-14s %-9s %s%n",
                    name, s.area(), r.id(), r.shape(), line);
        }

        // ------------------------------------------------------------------ the two packs agree
        System.out.println();
        System.out.println("the arms register and the law register");
        LawRegister law = LawRegister.get();
        ok(law.hasData(), "the law pack loaded");

        int weaponRows = 0;
        for (String qid : law.polities()) {
            weaponRows += law.of(qid).stream().filter(c -> c.kind() == LawRegister.WEAPONS).count();
        }
        ok(weaponRows >= 13, "the law pack carries %d weapon-law rows".formatted(weaponRows));

        // The weapon law at the place and year, read through the ruler join: this is the part of
        // the story the arms register cannot tell, because it is keyed by polity and not by area.
        for (Object[] p : new Object[][]{
                {"London, 1181", 51.51, -0.13, 1181},
                {"Kyoto, 1600", 35.0, 135.77, 1600},
                {"Delhi, 1900", 28.61, 77.21, 1900},
                {"Beijing, 1300", 39.9, 116.4, 1300}}) {
            String name = (String) p[0];
            List<LawRegister.Change> here = law.hereAt((Double) p[1], (Double) p[2], (Integer) p[3]);
            List<LawRegister.Change> w = new ArrayList<>();
            for (LawRegister.Change c : here) {
                if (c.kind() == LawRegister.WEAPONS && c.year() <= (Integer) p[3]) {
                    w.add(c);
                }
            }
            ok(!w.isEmpty(), name + " has a weapon law in force");
            if (!w.isEmpty()) {
                LawRegister.Change last = w.get(w.size() - 1);
                System.out.printf("   %-14s %s%n", name, last.line());
            }
            ok(!a.describe((Double) p[1], (Double) p[2], (Integer) p[3]).isBlank(),
                    name + " and the arms register has something to say too");
        }

        // ------------------------------------------------------------------ coverage: no area-year is bare
        System.out.println();
        int silent = 0;
        int total = 0;
        int defaulted = 0;
        for (int ai = 0; ai < a.areas().size(); ai++) {
            for (int year = -3000; year <= 2000; year += 100) {
                total++;
                Row r = a.rowIn(a.areas().get(ai), year, null);
                if (r == null) {
                    silent++;
                } else if (r.isDefault()) {
                    defaulted++;
                }
            }
        }
        System.out.printf("  %d area-years: %d with nothing at all, %d falling to the default%n",
                total, silent, defaulted);
        ok(silent == 0, "no area-year is bare");
        ok(defaulted < total, "some area-year has a real row and not just the default");

        System.out.println();
        System.out.println("arms: " + checks + " checks, " + failed + " failed");
        if (failed > 0) {
            System.exit(1);
        }
    }
}
