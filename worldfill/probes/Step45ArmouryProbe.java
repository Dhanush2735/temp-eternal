import com.eternalengine.technology.TechnologyAtlas;
import com.eternalengine.war.Armoury;
import com.eternalengine.war.Armoury.Kind;
import com.eternalengine.war.Armoury.Kit;

import java.util.ArrayList;
import java.util.List;

/** Step 45 part 2 (E9 A): the armoury. Checks are printed, so a wrong answer is visible. */
public final class Step45ArmouryProbe {

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
        {"Uruk, Sumer, later", 31.3, 45.6, -1700},
        {"Thebes, Egypt", 25.7, 32.6, -1300},
        {"Athens", 37.98, 23.73, -350},
        {"Rome", 41.88, 12.50, 100},
        {"Pataliputra, Maurya", 25.6, 85.1, -250},
        {"Chang'an, Tang", 34.3, 108.9, 800},
        {"Kyoto, Japan", 35.0, 135.77, 1580},
        {"Tenochtitlan", 19.43, -99.13, 1500},
        {"Cusco, Inca", -13.53, -71.97, 1500},
        {"Cahokia", 38.65, -90.11, 1100},
        {"Timbuktu", 16.77, -3.01, 1500},
        {"Great Zimbabwe", -20.27, 30.93, 1400},
        {"Abeokuta, Yoruba", 7.15, 3.35, 1800},
        {"Cape York, Australia", -10.7, 142.5, 1700},
        {"Tahiti", -17.65, -149.45, 1750},
        {"Delhi, Mughal", 28.61, 77.21, 1650},
        {"Agra, 1526 Panipat year", 27.18, 78.02, 1526},
        {"London, 1181 Assize", 51.51, -0.13, 1181},
        {"London, 1700", 51.51, -0.13, 1700},
        {"London, 1900", 51.51, -0.13, 1900},
        {"Paris, 1420", 48.86, 2.35, 1420},
        {"Istanbul, 1453", 41.01, 28.98, 1453},
        {"Hyderabad, 1948", 17.39, 78.49, 1948},
        {"Philadelphia, 1863", 39.95, -75.17, 1863},
        {"Ypres, 1917", 50.85, 2.88, 1917},
    };

    public static void main(String[] args) {
        Armoury a = Armoury.get();
        System.out.println("armoury: " + a.summary());
        ok(a.loaded(), "the armoury loads");
        eq(a.problem(), null, "no problem reading the armoury");
        ok(a.count() >= 20, "at least twenty kinds (have " + a.count() + ")");

        // ---------------------------------------------------------------- the join to step 40
        //
        // D10's formations name twelve arms. If this register does not speak all twelve, step 40
        // and step 45 cannot join, and a formation's weapon will never resolve.
        List<String> spoken = new ArrayList<>();
        for (Kind k : a.kinds()) {
            if (k.arm() != null && !spoken.contains(k.arm())) {
                spoken.add(k.arm());
            }
        }
        System.out.println();
        System.out.println("the join to step 40:");
        for (String arm : a.d10Arms()) {
            List<String> by = new ArrayList<>();
            for (Kind k : a.kinds()) {
                if (arm.equals(k.arm())) {
                    by.add(k.id());
                }
            }
            System.out.printf("  %-9s <- %s%n", arm, String.join(", ", by));
            ok(!by.isEmpty(), "D10 arm '" + arm + "' is named by no kind: the registers will not join");
        }

        // ---------------------------------------------------------------- what is here
        System.out.println();
        System.out.println("what they carry:");
        for (Object[] p : PLACES) {
            String nm = (String) p[0];
            Kit kit = a.at((Double) p[1], (Double) p[2], (Integer) p[3]);
            System.out.printf("  %-26s %s%n", nm, Armoury.sentence(kit));
            ok(!kit.area().isEmpty(), nm + ": no area");
        }

        // ---------------------------------------------------------------- the debt step 44 left
        //
        // "Australia had no bows; the weapons step decides who may have them."
        System.out.println();
        System.out.println("the question step 44 handed to this step:");
        Kit aus = a.at(-25.0, 134.0, 1700);
        Kind bow = a.kind("bow");
        Kind spear = a.kind("spear");
        ok(bow != null, "there is a bow kind");
        ok(bow.neverIn("AUS") != null, "the bow is recorded as never in Australia");
        System.out.println("  why: " + (bow == null ? "?" : bow.neverIn("AUS")));
        ok(spear != null, "there is a spear kind");
        ok(spear.neverIn("AUS") == null, "the spear is NOT recorded as absent in Australia");
        // and the spear must actually be present in Australia in 1700
        boolean spearHere = false;
        for (Kind k : aus.here()) {
            if ("spear".equals(k.id())) {
                spearHere = true;
            }
        }
        ok(spearHere, "the spear is in the Australian kit of 1700 (it was not, while it inherited "
                + "the bow's date of 1800)");
        boolean bowHere = false;
        for (Kind k : aus.here()) {
            if ("bow".equals(k.id())) {
                bowHere = true;
            }
        }
        ok(!bowHere, "the bow is NOT in the Australian kit of 1700");
        System.out.println("  Australia 1700: " + Armoury.sentence(aus));

        // ---------------------------------------------------------------- absences are facts
        System.out.println();
        System.out.println("recorded absences (no metal sword in the Americas, and so on):");
        for (Kind k : a.kinds()) {
            if (k.never().isEmpty()) {
                continue;
            }
            System.out.printf("  %-14s never in %s%n", k.id(), k.never().keySet());
            for (String area : k.never().keySet()) {
                ok(k.neverIn(area) != null && k.neverIn(area).length() > 10,
                        k.id() + ": absence in " + area + " has no reason");
            }
        }
        int absentAreas = a.absentAreas().size();
        System.out.println("  " + a.kinds().stream().mapToInt(k -> k.never().size()).sum()
                + " absences across " + absentAreas + " areas");

        // no sword in the Americas before Columbus
        for (double[] where : new double[][]{{19.43, -99.13}, {-13.53, -71.97}, {38.65, -90.11}}) {
            int y = a.arrivalOf(a.kind("sword"), where[0], where[1],
                    com.eternalengine.money.ProductAtlas.get().place(where[0], where[1], 1491).area());
            ok(y == TechnologyAtlas.NEVER || y > 1491,
                    "no sword in the Americas by 1491 (arrival " + y + " at "
                            + where[0] + "," + where[1] + ")");
        }
        // but a spear everywhere
        for (double[] where : new double[][]{{19.43, -99.13}, {-25.0, 134.0}, {-17.65, -149.45}}) {
            int y = a.arrivalOf(a.kind("spear"), where[0], where[1],
                    com.eternalengine.money.ProductAtlas.get().place(where[0], where[1], 1000).area());
            ok(y != TechnologyAtlas.NEVER && y <= 1000, "a spear by 1000 at "
                    + where[0] + "," + where[1] + " (arrival " + y + ")");
        }

        // ---------------------------------------------------------------- supersession
        System.out.println();
        System.out.println("what has been supplanted:");
        for (Object[] p : PLACES) {
            Kit kit = a.at((Double) p[1], (Double) p[2], (Integer) p[3]);
            if (kit.goneIn().isEmpty()) {
                continue;
            }
            StringBuilder b = new StringBuilder();
            for (java.util.Map.Entry<Kind, List<Kind>> e : kit.goneIn().entrySet()) {
                if (b.length() > 0) {
                    b.append("; ");
                }
                List<String> ns = new ArrayList<>();
                for (Kind o : e.getValue()) {
                    ns.add(o.name());
                }
                b.append(e.getKey().name()).append(" -> ").append(String.join("/", ns));
            }
            System.out.printf("  %-26s %s%n", p[0], b);
        }

        // ---------------------------------------------------------------- coverage
        System.out.println();
        int silent = 0, total = 0, minKinds = 999, maxKinds = 0;
        for (double lat = -50.0; lat <= 66.0; lat += 8.0) {
            for (double lon = -178.0; lon <= 178.0; lon += 12.0) {
                for (int year = -3000; year <= 1900; year += 500) {
                    Kit kit = a.at(lat, lon, year);
                    total++;
                    if (kit.empty()) {
                        silent++;
                    }
                    minKinds = Math.min(minKinds, kit.here().size());
                    maxKinds = Math.max(maxKinds, kit.here().size());
                }
            }
        }
        System.out.printf("  %d place-years: %d with nothing, kinds per place %d to %d%n",
                total, silent, minKinds, maxKinds);
        ok(silent == 0, "every place and year has something (a club and a spear, at the least)");
        ok(maxKinds > 3, "some place and year has more than three kinds");

        System.out.println();
        System.out.println("armoury: " + checks + " checks, " + failed + " failed");
        if (failed > 0) {
            System.exit(1);
        }
    }
}
