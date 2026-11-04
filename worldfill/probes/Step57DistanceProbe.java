/* Step 57 part 5 (I4, I5): one distance table, two readers. The claim: far away means numbers only -
   people, vehicles and armies become counts, not bodies - and the draw thins by distance and hides what
   cannot be seen. The lines are game defaults and say so. */
import com.eternalengine.core.Distances;
import com.eternalengine.core.Distances.Detail;
import com.eternalengine.core.Distances.Level;
import com.eternalengine.core.Distances.Sim;

public class Step57DistanceProbe {
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
        // ------------------------------------------------ 1. THE LINES
        eq(Distances.NEAR, 24.0, "full detail to 24 blocks");
        eq(Distances.REDUCED, 64.0, "thinned to 64");
        eq(Distances.NUMBERS_ONLY, 128.0, "numbers only past 128");
        eq(Distances.HIDDEN, 160.0, "hidden past 160");

        // ------------------------------------------------ 2. THE SIMULATION SIDE (I4)
        eq(Distances.simulateAs(0), Sim.ENTITIES, "here in person");
        eq(Distances.simulateAs(128), Sim.ENTITIES, "up to the line");
        eq(Distances.simulateAs(128.5), Sim.NUMBERS, "and past it: numbers only");
        eq(Distances.simulateAs(5000), Sim.NUMBERS, "even far away");
        eq(Distances.simulateAs(-1), null, "a distance below none is refused");
        ok(Sim.NUMBERS.words().contains("people, vehicles and armies are counts"),
                "the numbers say what they count: " + Sim.NUMBERS.words());
        ok(Sim.NUMBERS.words().contains("population engine"),
                "and who remembers them: " + Sim.NUMBERS.words());

        // ------------------------------------------------ 3. THE DRAW SIDE (I5)
        eq(Distances.draw(10, 256), Detail.FULL, "near: every figure");
        eq(Distances.draw(40, 256), Detail.REDUCED, "thinned: every second figure");
        eq(Distances.draw(100, 256), Detail.CROWD_ONLY, "a cluster, not figures");
        eq(Distances.draw(200, 256), Detail.HIDDEN, "and far: hidden");
        eq(Distances.draw(100, 80), Detail.HIDDEN, "the client's own view hides first when it is nearer");
        eq(Distances.draw(-5, 256), null, "and a refused distance draws nothing at all");
        ok(Detail.HIDDEN.words().contains("cannot be seen"), "hiding says why: " + Detail.HIDDEN.words());

        // ------------------------------------------------ 4. BOTH READERS AT ONCE
        Level both = Distances.at(50, 256);
        ok(both.ok(), "one question, both answers: " + both.line());
        eq(both.sim(), Sim.ENTITIES, "50 blocks is still people in person");
        eq(both.draw(), Detail.REDUCED, "and drawn thinned");
        Level far = Distances.at(300, 256);
        eq(far.sim(), Sim.NUMBERS, "300 blocks is numbers only");
        eq(far.draw(), Detail.HIDDEN, "and nothing drawn");
        ok(far.line().contains("numbers only") && far.line().contains("hidden"),
                "in words: " + far.line());
        Level bad = Distances.at(-1, 256);
        ok(!bad.ok() && bad.refused().contains("below none"), "a distance below none is refused: "
                + bad.refused());
        Level noView = Distances.at(50, 0);
        ok(!noView.ok() && noView.refused().contains("the client's to say"),
                "and no view distance is refused, not guessed: " + noView.refused());

        // ------------------------------------------------ 5. THE RULE
        System.out.println("     " + Distances.ruleLine());
        ok(Distances.ruleLine().contains("game defaults"), "the rule names its sources");
        ok(Distances.ruleLine().contains("numbers only"), "and keeps the two readers");

        System.out.println("\nStep 57 part 5: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }
}
