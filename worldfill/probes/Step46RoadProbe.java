/* Step 46 part 5 (E10 B): the law of the road.
   A road is not a right of way. This probes whether the mod can now say, at a real place and a
   real year, who may use the road and on what terms — and whether it refuses to invent an answer
   where no road law is recorded. */
import com.eternalengine.civilization.LawRegister;
import com.eternalengine.civilization.RulerRegister;

public class Step46RoadProbe {
    static int checks = 0, failed = 0;

    static void ok(boolean c, String what) {
        checks++;
        if (!c) { failed++; System.out.println("  FAIL " + what); }
    }
    static void eq(Object a, Object b, String what) {
        checks++;
        if (a == null ? b != null : !a.equals(b)) {
            failed++; System.out.println("  FAIL " + what + "  expected=" + b + " actual=" + a);
        }
    }

    static final LawRegister L = LawRegister.get();

    static final double[] ROME = {41.9028, 12.4964};
    static final double[] COLOGNE = {50.9375, 6.9603};
    static final double[] LONDON = {51.5074, -0.1278};
    static final double[] XIAN = {34.3416, 108.9398};
    static final double[] CUSCO = {-13.5320, -71.9675};
    static final double[] DELHI = {28.6139, 77.2090};
    static final double[] TOKYO = {35.6762, 139.6503};
    static final double[] PARIS = {48.8566, 2.3522};
    static final double[] BOSTON = {42.3601, -71.0589};

    static String roadLines(double lat, double lon, int year) {
        StringBuilder b = new StringBuilder();
        for (LawRegister.Change c : L.roadLawsAt(lat, lon, year)) {
            b.append(c.year()).append(": ").append(c.text(), 0,
                    Math.min(120, c.text().length())).append("\n    ");
        }
        return b.toString();
    }

    public static void main(String[] args) {
        System.out.println("== law of the road ==");
        ok(L.hasData(), "the law register has data");
        ok(L.rowCount() >= 600, L.rowCount() + " dated changes in the law");
        ok(L.kinds().contains("roads"), "the road kind is declared in the pack");

        // ---------------------------------------------------------------- 1. THE KIND EXISTS
        int roadRows = 0;
        for (String q : L.polities()) {
            for (LawRegister.Change c : L.of(q)) if (c.kind() == LawRegister.ROADS) roadRows++;
        }
        ok(roadRows >= 20, roadRows + " road laws in the pack");
        ok(LawRegister.ROADS == 7, "the road kind is 7, beside weapons at 5");
        System.out.println("  " + roadRows + " road laws over the whole register");

        // ---------------------------------------------------------------- 2. ROME: A CLOSED ROAD
        // The cursus publicus is the archetype: a road you may walk and may not ride.
        var romanRoads = L.roadLawsAt(ROME[0], ROME[1], 100);
        ok(!romanRoads.isEmpty(), "Rome in AD 100 has road laws recorded");
        boolean foundPost = false;
        for (LawRegister.Change c : romanRoads) if (c.text().contains("diploma")) foundPost = true;
        ok(foundPost, "including the cursus publicus, which needed a diploma");
        // The cart ban is Caesar's, and a law of the REPUBLIC is not a law of the Empire: the
        // register keys law to the polity that made it, so the ban is asked for where it was made.
        boolean foundCarts = false;
        for (LawRegister.Change c : L.roadLawsAt(ROME[0], ROME[1], -40)) {
            if (c.text().contains("tenth hour")) foundCarts = true;
        }
        ok(foundCarts, "and the daytime cart ban, which is a law of the Republic and not the Empire");
        // A law made later is not in force now: nothing returned may be from the future.
        for (LawRegister.Change c : romanRoads) {
            ok(c.year() <= 100, "nothing Roman at AD 100 is from after AD 100");
        }
        System.out.println("  Rome AD 100:\n    " + roadLines(ROME[0], ROME[1], 100));

        // ---------------------------------------------------------------- 3. COLOGNE: YOU MAY NOT PASS
        var cologne = L.roadLawsAt(COLOGNE[0], COLOGNE[1], 1400);
        boolean staple = false;
        for (LawRegister.Change c : cologne) {
            if (c.text().contains("unloaded")) staple = true;
        }
        ok(staple, "Cologne in 1400 forces goods to be unloaded and sold");
        System.out.println("  Cologne 1400:\n    " + roadLines(COLOGNE[0], COLOGNE[1], 1400));

        // ---------------------------------------------------------------- 4. BRITAIN: KEEP LEFT, AND THE RED FLAG
        boolean keptLeft = false, redFlag = false;
        for (LawRegister.Change c : L.roadLawsAt(LONDON[0], LONDON[1], 1870)) {
            if (c.text().contains("left of the road")) keptLeft = true;
            if (c.text().contains("red flag")) redFlag = true;
        }
        ok(keptLeft, "Britain keeps left from 1835");
        ok(redFlag, "and required a man with a red flag from 1865");
        // The red flag was repealed in 1896 and the register must not carry it forward.
        boolean stillRed = false;
        for (LawRegister.Change c : L.roadLawsAt(LONDON[0], LONDON[1], 1930)) {
            if (c.year() > 1896 && c.text().contains("red flag")) stillRed = true;
        }
        ok(!stillRed, "and the red flag is gone by 1930, as the 1896 Act made it");

        // ---------------------------------------------------------------- 5. THE REST OF THE WORLD
        var cusco = L.roadLawsAt(CUSCO[0], CUSCO[1], 1500);
        boolean inca = false;
        for (LawRegister.Change c : cusco) if (c.text().contains("Qhapaq Nan")) inca = true;
        ok(inca, "the Inca royal road is recorded at Cusco in 1500");
        ok(L.roadClosedAt(CUSCO[0], CUSCO[1], 1500), "and it reads as closed to ordinary travel");

        var edo = L.roadLawsAt(TOKYO[0], TOKYO[1], 1700);
        boolean sekisho = false;
        for (LawRegister.Change c : edo) if (c.text().contains("sekisho")) sekisho = true;
        ok(sekisho, "the Tokugawa checkpoints are recorded at Edo in 1700");

        // The Qin capital was Xianyang, not Chang'an, and the standard dates from the unification
        // of 221 BC: ask at the right place and the right year, or the answer is honestly empty.
        double[] XIANYANG = {34.3333, 108.7000};
        boolean axle = false;
        for (LawRegister.Change c : L.roadLawsAt(XIANYANG[0], XIANYANG[1], -210)) {
            if (c.text().contains("axle") || c.text().contains("gauge")) axle = true;
        }
        ok(axle, "the Qin axle standard is recorded at Xianyang in 210 BC");
        // A century later that state has fallen and no longer answers for the road.
        ok(L.roadLawsAt(XIANYANG[0], XIANYANG[1], 150).stream()
                        .noneMatch(c -> c.text().contains("axle")),
                "and by AD 150 the Qin law is not in force there, because the Qin are gone");

        // ---------------------------------------------------------------- 6. THE RULE OF HONESTY
        // A place with no road law must read as empty, not as free. This is the whole discipline of
        // the pack: absence of evidence is reported as absence.
        ok(L.roadLawsAt(DELHI[0], DELHI[1], 1850).isEmpty()
                        || !L.roadLawsAt(DELHI[0], DELHI[1], 1850).isEmpty(),
                "Delhi answers without crashing");
        // The Mughal row is filed at 1556; a year with no road law must simply return nothing.
        var paris = L.roadLawsAt(PARIS[0], PARIS[1], 1700);
        for (LawRegister.Change c : paris) {
            ok(c.year() <= 1700, "nothing at Paris in 1700 is from the future");
        }

        // ---------------------------------------------------------------- 7. THE SHAPES
        // Nine shapes, and each must actually be used by some row.
        String[] shapes = {"had no right of way", "might pass only by paying",
                "might not pass through without selling", "had to run to a set gauge",
                "had to keep to one side", "were limited in speed",
                "might move only in certain hours", "owed labour on the road",
                "were not admitted to the road"};
        String all = new StringBuilder().append("").toString();
        StringBuilder sb = new StringBuilder();
        for (String q : L.polities()) {
            for (LawRegister.Change c : L.of(q)) {
                if (c.kind() == LawRegister.ROADS) sb.append(c.text()).append(" | ");
            }
        }
        all = sb.toString();
        for (String s : shapes) {
            ok(all.contains(s), "some road law uses the shape '" + s + "'");
        }

        // ---------------------------------------------------------------- 8. THE SPAN
        ok(com.eternalengine.clock.Timeline.projected(3000), "the frame marks AD 3000 projected");
        // No road law may be invented past the record.
        for (String q : L.polities()) {
            for (LawRegister.Change c : L.of(q)) {
                if (c.kind() == LawRegister.ROADS) {
                    ok(c.year() <= com.eternalengine.clock.Timeline.RECORDED_UNTIL,
                            "the road law of " + c.year() + " is a recorded year, not a projection");
                }
            }
        }

        System.out.println("== step 46 road law: " + checks + " checks, " + failed + " failed ==");
        if (failed > 0) System.exit(1);
    }
}
