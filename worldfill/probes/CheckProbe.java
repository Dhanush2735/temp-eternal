import com.eternalengine.civilization.HistoryChecks;
import com.eternalengine.civilization.HistoryChecks.Line;
import com.eternalengine.civilization.HistoryChecks.Part;
import com.eternalengine.civilization.HistoryChecks.Section;
import com.eternalengine.civilization.HistoryChecks.Status;

import java.util.ArrayList;
import java.util.List;

/**
 * The history part of /ee check, run outside the game (worldfill/probe_check.sh): the very same
 * HistoryChecks code against the mod's compiled classes and resources. Prints every line, the way
 * the in-game check writes them to the Minecraft log; exit code 1 if any check fails.
 *
 *   probe_check.sh              all parts
 *   probe_check.sh places talk  only these parts
 */
public class CheckProbe {
    public static void main(String[] args) {
        List<Part> parts = new ArrayList<>();
        for (String a : args) {
            parts.add(Part.byId(a).orElseThrow(() -> new IllegalArgumentException("unknown part " + a)));
        }
        if (parts.isEmpty()) {
            parts = List.of(Part.values());
        }
        int ok = 0, fail = 0, known = 0;
        for (Part p : parts) {
            Section s = HistoryChecks.run(p);
            System.out.printf("%n== %s (%s, %.1f s) ==%n", p.title(), p.id(), s.millis() / 1000.0);
            for (Line l : s.lines()) {
                String tag = switch (l.status()) {
                    case OK -> l.counted() ? "[ OK ] " : "[ OK*] ";
                    case FAIL -> l.counted() ? "[FAIL] " : "[FAIL*]";
                    case KNOWN -> "[KNOWN]";
                    case INFO -> "  ·    ";
                };
                System.out.println("  " + tag + " " + l.text());
                if (!l.detail().isEmpty()) {
                    System.out.println("           " + l.detail());
                }
            }
            ok += s.count(Status.OK);
            fail += s.count(Status.FAIL);
            known += s.count(Status.KNOWN);
        }
        System.out.printf("%n%d checks: %d OK, %d failed, %d known limits  (* = summary line, not counted)%n",
                ok + fail + known, ok, fail, known);
        System.exit(fail > 0 ? 1 : 0);
    }
}
