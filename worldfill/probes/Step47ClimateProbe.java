/* The climate projection: arithmetic under a stated assumption, and every value a band.
   The claim: this is allowed where a price is refused because it is physics, and the lesson from
   the backtest is that nothing here may be printed as a point. */
import com.eternalengine.climate.ClimateProjection;
import com.eternalengine.clock.Timeline;

import java.util.List;

public class Step47ClimateProbe {
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

    public static void main(String[] args) {
        ClimateProjection c = ClimateProjection.get();
        System.out.println("  " + c.summary());

        // ------------------------------------------------ 1. THREE PATHS, NAMED ASSUMPTIONS
        eq(c.scenarios().size(), 3, "three scenarios and no more: a range, not a forecast");
        for (String id : List.of("zero", "fast", "delayed")) {
            ok(c.scenario(id) != null, "the pack carries " + id);
            ok(c.assumption(id).length() > 25, "and states its assumption in words: "
                    + c.assumption(id));
            eq(c.scenario(id).mark(), Timeline.PROJECTED, id + " is marked projected, never recorded");
        }
        ok(c.assumption("zero").contains("stop"), "the zero scenario says emissions stop");

        // ------------------------------------------------ 2. EVERY VALUE IS A BAND
        ClimateProjection.Band t = c.temperature("delayed", 2100);
        ok(t != null && !t.flat(), "temperature is a band and not a point: " + t.one());
        ok(t.high() > t.mid() && t.mid() > t.low(), "with the mid inside it");
        ok(t.contains((t.low() + t.high()) / 2), "and the band contains its own middle");
        ClimateProjection.Band co2 = c.carbon("delayed", 2100);
        ok(co2.flat(), "carbon is a FLAT band, because carbon in the air is chemistry and no "
                + "climate sensitivity changes it: " + co2.one());
        ok(c.line("delayed", 2100).contains("IF"), "and the sentence leads with the assumption: "
                + c.line("delayed", 2100).substring(0, Math.min(150,
                        c.line("delayed", 2100).length())));

        // ------------------------------------------------ 3. THE FINDING: SEA LEVEL ONLY RISES
        for (String id : c.scenarios()) {
            ok(c.rising(id), "sea level never falls in " + id + ", which is the pack's claim");
        }
        double s2026 = c.seaLevel("zero", 2026).mid();
        double s3000 = c.seaLevel("zero", 3000).mid();
        ok(s3000 > s2026, "even with emissions stopping dead in 2027 the sea still rises by 3000: "
                + s2026 + " -> " + s3000);
        ok(c.seaLevel("delayed", 3000).mid() > c.seaLevel("zero", 3000).mid(),
                "and the slow path ends higher: " + c.seaLevel("delayed", 3000).mid() + " against "
                        + c.seaLevel("zero", 3000).mid());

        // ------------------------------------------------ 4. THE GAP WIDENS, NOT CLOSES
        double gap2100 = c.seaLevel("delayed", 2100).mid() - c.seaLevel("zero", 2100).mid();
        double gap3000 = c.seaLevel("delayed", 3000).mid() - c.seaLevel("zero", 3000).mid();
        ok(gap3000 > gap2100, "the difference between acting and waiting is larger in 3000 than in "
                + "2100: " + gap2100 + " then " + gap3000);

        // ------------------------------------------------ 5. THE PHYSICS MOVES THE RIGHT WAY
        ok(c.carbon("zero", 3000).mid() < c.carbon("zero", 2026).mid(),
                "carbon falls when emissions stop");
        ok(c.carbon("delayed", 2100).mid() > c.carbon("fast", 2100).mid(),
                "and the delayed path has more carbon in 2100 than the fast one");
        ok(c.temperature("delayed", 2100).mid() > c.temperature("fast", 2100).mid(),
                "and is warmer");
        ok(c.temperature("zero", 3000).mid() < c.temperature("zero", 2050).mid(),
                "the zero path cools after its peak, which is why a peak is in the data");
        ok(c.carbon("zero", 3000).mid() > 300,
                "but not back to preindustrial: about a fifth of a tonne never leaves, so the air "
                        + "is still " + c.carbon("zero", 3000).mid() + " ppm");

        // ------------------------------------------------ 6. THE MARKS IT REFUSES
        for (String kind : List.of("person", "event", "price", "population", "war")) {
            ok(c.refused().contains(kind), "it refuses to invent a " + kind);
        }
        ok(!c.line("zero", 2400).toLowerCase().contains("government"),
                "and no line of it names a government that decided anything");

        // ------------------------------------------------ 7. BEFORE THE SPAN IS NOT A CRASH
        ok(c.seaLevel("zero", 2000) == null || c.seaLevel("zero", 2000).mid() > 0,
                "asking before the projection begins is answered, not crashed");
        ok(c.marks().get(0) == 2026, "the first mark is the seam itself");
        ok(c.marks().get(c.marks().size() - 1) == 3000, "and the last is the end of the world");

        System.out.println("  " + c.line("delayed", 2400));
        System.out.println(failed == 0
                ? "Step47ClimateProbe: " + checks + " checks, 0 failed"
                : "Step47ClimateProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
