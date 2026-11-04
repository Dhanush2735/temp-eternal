import com.eternalengine.civilization.Justice;
import com.eternalengine.civilization.LawRegister;

import java.util.List;

/**
 * Step 42 part 6 (F3, law and crime by era) probes.
 *
 *   F3  who keeps the peace, who judges, and what can be done to a man - by place and year,
 *       with the one hard fact (whether a place still hangs people) taken from the law pack
 *       and not from the justice table.
 */
public final class Step42dProbe {

    static int checks = 0;
    static int bad = 0;

    static void ok(boolean cond, String what) {
        checks++;
        if (!cond) {
            bad++;
            System.out.println("  FAIL " + what);
        }
    }

    public static void main(String[] args) {
        System.out.println("Justice: " + Justice.get());
        System.out.println("LawRegister: " + LawRegister.get());
        System.out.println();

        loaded();
        guardsAndCourts();
        repertoire();
        theHardFact();
        alwaysAnswers();

        System.out.println();
        System.out.println(bad == 0
                ? "step 42 part 6: " + checks + " checks, 0 problems"
                : "step 42 part 6: " + checks + " checks, " + bad + " FAILED");
        if (bad > 0) {
            System.exit(1);
        }
    }

    static void loaded() {
        System.out.println("F3  the pack");
        ok(Justice.get().hasData(), "the justice pack loaded");
        ok(Justice.get().rowCount() >= 35, "it has its rows: " + Justice.get().rowCount());
        ok(!Justice.get().gaps().isEmpty(), "it names its own limits: " + Justice.get().gaps().size());
        ok(Justice.get().counts().getOrDefault("guards", 0) >= 12,
                "guards: " + Justice.get().counts().get("guards"));
        ok(Justice.get().counts().getOrDefault("courts", 0) >= 12,
                "courts: " + Justice.get().counts().get("courts"));
        ok(Justice.get().counts().getOrDefault("punishments", 0) >= 8,
                "punishments: " + Justice.get().counts().get("punishments"));
    }

    /** The three questions, asked of real places in real years. */
    static void guardsAndCourts() {
        System.out.println("F3  who keeps the peace, and who judges");
        String[][] cases = {
            {"GBR", "1400", "hundred_shire", "jury_court"},
            {"GBR", "1850", "police_force", "professional_court"},
            {"CHN", "1800", "magistrate_runners", "professional_court"},
            {"JPN", "1750", "bugyo_men", "bugyo_court"},
            {"IND", "1700", "headman_caste", "panchayat_court"},
            {"EGY", "1200", "city_watch", "qadi_court"},
            {"RUS", "1960", "political_police", "peoples_court"},
            {"IRQ", "-1800", "palace_temple", "kings_judgement"},
        };
        for (String[] c : cases) {
            int year = Integer.parseInt(c[1]);
            Justice.Row g = Justice.get().guards(c[0], year);
            Justice.Row ct = Justice.get().courts(c[0], year);
            ok(c[2].equals(g.id()), "%s %s is kept by %s (%s)".formatted(c[0], c[1], c[2], g.id()));
            ok(c[3].equals(ct.id()), "%s %s is judged by %s (%s)".formatted(c[0], c[1], c[3], ct.id()));
            if (c[0].equals("GBR") || c[0].equals("IRQ")) {
                System.out.println("    " + c[0] + " " + c[1] + ": " + g.head());
                System.out.println("             " + ct.head());
            }
        }

        // Britain has no gendarmerie: the row says so, and the check holds it to it.
        ok(!"gendarmerie".equals(Justice.get().guards("GBR", 1900).id()),
                "Britain never gets a gendarmerie: " + Justice.get().guards("GBR", 1900).name());
        ok("gendarmerie".equals(Justice.get().guards("FRA", 1900).id()),
                "but France does: " + Justice.get().guards("FRA", 1900).name());

        // Every row names the work it was read from.
        for (String[] c : cases) {
            int year = Integer.parseInt(c[1]);
            ok(Justice.get().guards(c[0], year).source() != null,
                    "%s %s guards name a source".formatted(c[0], c[1]));
        }
    }

    /** Punishment is a repertoire, not a choice. */
    static void repertoire() {
        System.out.println("F3  what can be done to him");
        List<Justice.Row> england = Justice.get().punishments("GBR", 1300);
        ok(england.size() >= 4, "England in 1300 has %d punishments, not one".formatted(england.size()));
        ok(england.stream().anyMatch(r -> r.id().equals("judicial_death")), "hanging is among them");
        ok(england.stream().anyMatch(r -> r.id().equals("public_shame")), "and the stocks");
        ok(england.stream().noneMatch(r -> r.id().equals("prison_term")),
                "and not a term of years, which had not been invented");
        System.out.println("    1300 England: " + england.stream().map(Justice.Row::name)
                .reduce((a, b) -> a + ", " + b).orElse("none"));

        ok(Justice.get().punishments("FRA", 1790).stream().anyMatch(r -> r.id().equals("prison_term")),
                "by 1790 France can sentence a term of years");

        // The fallback is reachable, but only where no row reaches.
        List<Justice.Row> deep = Justice.get().punishments("AUS", -5000);
        ok(deep.size() == 1 && "blood_price".equals(deep.get(0).id()),
                "before any row reaches, the fallback answers alone: " + deep.get(0).name());
    }

    /**
     * The one hard fact. It is not read from the justice table: it is the C18 law pack, which
     * carries real abolition dates.
     */
    static void theHardFact() {
        System.out.println("F3  whether they can still hang you");
        // France abolished in 1981; Portugal in 1867.
        System.out.println("    1780 France:   can hang = " + Justice.get().deathPenaltyAt(46.5, 2.5, 1780));
        System.out.println("    2000 France:   can hang = " + Justice.get().deathPenaltyAt(46.5, 2.5, 2000));
        System.out.println("    1860 Portugal: can hang = " + Justice.get().deathPenaltyAt(39.5, -8.0, 1860));
        System.out.println("    1900 Portugal: can hang = " + Justice.get().deathPenaltyAt(39.5, -8.0, 1900));

        ok(Justice.get().deathPenaltyAt(46.5, 2.5, 1780), "France could hang a man in 1780");
        ok(!Justice.get().deathPenaltyAt(46.5, 2.5, 2000), "and cannot now");
        ok(Justice.get().deathPenaltyAt(39.5, -8.0, 1860), "Portugal could in 1860");
        ok(!Justice.get().deathPenaltyAt(39.5, -8.0, 1900), "and could not by 1900 - it went in 1867");

        // The abolition year is carried, so the register can say why.
        Justice.Here portugal = Justice.get().hereAt(39.5, -8.0, 1900);
        ok(portugal.abolishedIn() != null && portugal.abolishedIn() <= 1900,
                "and the answer carries the year: " + portugal.abolishedIn());
        ok(!portugal.deathPenalty(), "and says the death penalty is gone");
        ok(portugal.punishments().stream().noneMatch(Justice.Row::death),
                "with no judicial death in the list at all");

        // The gate is the law register's, and it really is dated.
        ok(LawRegister.get().rowCount() > 300, "the law pack behind it: " + LawRegister.get().rowCount());

        System.out.println();
        System.out.println("    " + Justice.get().hereAt(47.0, 2.0, 1400).line());
    }

    /** Every point of the map, in every year, gets an answer in all three tables. */
    static void alwaysAnswers() {
        System.out.println("F3  every place, every year");
        int[] years = {-5000, -2400, -500, 0, 500, 1000, 1300, 1600, 1800, 1900, 1950, 2000};
        String[] places = {"FRA", "CHN", "IND", "RUS", "USA", "BRA", "NGA", "AUS", "IRQ", "JPN", "ZAF"};
        for (int y : years) {
            for (String p : places) {
                Justice.Row g = Justice.get().guards(p, y);
                Justice.Row c = Justice.get().courts(p, y);
                List<Justice.Row> ps = Justice.get().punishments(p, y);
                if (g == null || c == null || ps == null || ps.isEmpty()) {
                    ok(false, "%s in %d answered nothing".formatted(p, y));
                    return;
                }
            }
        }
        ok(true, "%d places x %d years all answered in all three tables".formatted(places.length, years.length));

        // And the world is not all one answer in any era we cover.
        for (int y : new int[] {-2400, 0, 1000, 1500, 1900}) {
            long n = java.util.Arrays.stream(places)
                    .map(p -> Justice.get().guards(p, y).id()).distinct().count();
            ok(n > 1, "%5d: more than one kind of peace-keeping in the world (%d)".formatted(y, n));
        }
    }
}
