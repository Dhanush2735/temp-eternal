import com.eternalengine.civilization.RulerRegister;
import com.eternalengine.villager.VillagerNameDatabase;

import java.util.*;

/**
 * Does every polity that rules a cell get a name pool?
 *
 * <p>Born 2026-10-24 (R2-d). The project's standing claim is that the ~1,500 world polities need no
 * civilization record because {@code VillagerNameDatabase.cultureFor} names their people from a
 * regional pool. That claim is testable, and this probe tests it: for every polity id the ruler
 * register can actually answer with, ask {@code cultureFor} and count the ones that fall through to
 * {@code global}.
 *
 * <p>{@code global} is not a crash. It is the generic pool - "Villager Alex Stone" - and it is the
 * difference between a town in Mewar and a town of nobody in particular.
 */
public final class NameCoverageProbe {

    public static void main(String[] args) {
        RulerRegister rr = RulerRegister.get();
        Set<String> ids = new TreeSet<>();
        for (RulerRegister.Polity p : rr.polities()) {
            if (p.civHint() != null && !p.civHint().isBlank()) ids.add(p.civHint());
        }
        System.out.println("polities the register names: " + ids.size());

        Map<String, List<String>> byPool = new TreeMap<>();
        for (String id : ids) {
            byPool.computeIfAbsent(VillagerNameDatabase.cultureFor(id), k -> new ArrayList<>()).add(id);
        }
        System.out.println();
        System.out.println("pool            polities   share");
        int generic = 0;
        for (var e : byPool.entrySet()) {
            int n = e.getValue().size();
            if (VillagerNameDatabase.GENERIC.equals(e.getKey())) generic = n;
            System.out.printf("%-14s %8d %6.1f%%%n", e.getKey(), n, 100.0 * n / ids.size());
        }
        System.out.println();
        if (generic > 0) {
            List<String> g = byPool.get(VillagerNameDatabase.GENERIC);
            System.out.println("no pool (named from the generic list): " + generic);
            g.stream().limit(40).forEach(id -> System.out.println("   " + id));
            if (g.size() > 40) System.out.println("   ... and " + (g.size() - 40) + " more");
        }
        System.out.println();
        System.out.println(generic == 0
                ? "PASS - every polity the register names has a regional name pool"
                : "FINDINGS - " + generic + " of " + ids.size() + " polities fall through to the generic pool ("
                  + String.format("%.1f", 100.0 * generic / ids.size()) + "%)");
    }
}
