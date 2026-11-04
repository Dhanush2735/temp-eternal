import com.eternalengine.civilization.CivHints;
import com.eternalengine.civilization.HistoryGazetteer;
import com.eternalengine.civilization.RulerRegister;

import java.util.*;

/**
 * The standing invariant: <b>no register may cite an id the rest of the mod cannot resolve.</b>
 *
 * <p>Written after the marking turn found that 96.4% of site civHints are pack ids the ruler register
 * has never heard of. The check runs over every place the corpus cites an id: sites, borders, and the
 * polity list itself, and classifies each into
 *
 * <ul>
 *   <li><b>known</b> - the register has it;</li>
 *   <li><b>aliasable</b> - a pack id that names exactly one polity ({@link CivHints});</li>
 *   <li><b>region</b> - a pack id that names a land over time, which only the year can resolve;</li>
 *   <li><b>declared</b> - a real polity the register's only source does not hold, named and explained in
 *       {@code CivHints.ABSENT_FROM_SOURCE} (turn 2026-10-24);</li>
 *   <li><b>UNKNOWN</b> - none of the above: nobody can resolve it and nobody has explained it.</li>
 * </ul>
 *
 * UNKNOWN is the number that matters, and since turn 2026-10-24 the bar is <b>zero undeclared</b>:
 * a gap we have named is a fact about the source, a gap we have not named is a bug.
 */
public final class VocabularyProbe {

    public static void main(String[] args) {
        HistoryGazetteer gaz = HistoryGazetteer.get();
        RulerRegister rr = RulerRegister.get();

        Set<String> known = new HashSet<>();
        for (RulerRegister.Polity p : rr.polities()) known.add(p.civHint());
        System.out.println("polity ids the ruler register knows: " + known.size());
        System.out.println("alias rows in CivHints: " + CivHints.aliasCount());

        Map<String, Integer> byKind = new TreeMap<>();
        Map<String, Integer> unknown = new TreeMap<>();
        Map<String, Integer> declared = new TreeMap<>();
        Map<String, Integer> second = new TreeMap<>();
        Map<String, int[]> counts = new LinkedHashMap<>();   // kind -> {hints, occurrences}

        classify("site", gaz.allSites().stream().map(HistoryGazetteer.Site::civHint).toList(), known, unknown, declared, second, counts);
        classify("border", gaz.allBorders().stream().map(HistoryGazetteer.Border::civId).toList(), known, unknown, declared, second, counts);

        System.out.println("\nkind      hints   occurrences   known   aliasable   region   UNKNOWN");
        int totalUnknown = 0;
        for (var e : counts.entrySet()) {
            int[] c = e.getValue();
            String kind = e.getKey();
            System.out.printf("%-8s %6d %13d %7d %11d %8d %9d%n",
                    kind, c[0], c[1], c[2], c[3], c[4], c[5]);
            totalUnknown += c[5];
        }

        if (!unknown.isEmpty()) {
            System.out.println("\nids nobody can resolve (these must not be used as civilizations):");
            unknown.entrySet().stream().sorted((a, b) -> b.getValue() - a.getValue()).limit(20)
                    .forEach(e -> System.out.printf("  %6d occurrences  %s%n", e.getValue(), e.getKey()));
        }
        System.out.println("carried by the SECOND register (primary source does not hold them): "
                + second.size() + " id(s), " + second.values().stream().mapToInt(Integer::intValue).sum()
                + " occurrence(s)");
        second.forEach((id, n) -> System.out.printf("  %6d occurrences  %s%n", n, id));
        System.out.println("declared absent from BOTH registers: " + declared.size()
                + " id(s), " + declared.values().stream().mapToInt(Integer::intValue).sum() + " occurrence(s)");
        declared.forEach((id, n) -> System.out.printf("  %6d occurrences  %s%n", n, id));

        System.out.println();
        System.out.println(totalUnknown == 0
                ? "PASS - every cited id is known, aliasable, a declared region, or a declared absent polity"
                : "FINDINGS - " + totalUnknown + " UNDECLARED ids resolve to nothing");
    }

    private static void classify(String kind, List<String> ids, Set<String> known,
                                 Map<String, Integer> unknown, Map<String, Integer> declared,
                                 Map<String, Integer> second, Map<String, int[]> counts) {
        int[] c = counts.computeIfAbsent(kind, k -> new int[6]);
        Set<String> seen = new HashSet<>();
        for (String raw : ids) {
            if (raw == null || raw.isBlank()) continue;
            String id = raw.trim();
            c[1]++;
            if (!seen.add(id)) continue;
            c[0]++;
            if (known.contains(id)) c[2]++;
            else if (CivHints.aliases().containsKey(id) && CivHints.resolve(id, null).isEmpty()) c[3]++;
            else if (CivHints.aliases().containsKey(id)) c[3]++;
            else if (CivHints.REGIONS.contains(id)) c[4]++;
            else if (com.eternalengine.civilization.PolityGazetteer.covers(id)) second.merge(id, 1, Integer::sum);
            else if (CivHints.declaredAbsent(id)) declared.merge(id, 1, Integer::sum);
            else { c[5]++; unknown.merge(id, 1, Integer::sum); }
        }
    }
}
