import com.eternalengine.civilization.HistoryGazetteer;
import com.eternalengine.civilization.RulerRegister;

import java.util.*;

/**
 * Can a site's civHint ever be resolved to a polity the rest of the mod knows?
 *
 * A site carries a civHint, and HistoricalPresence/CivSynthesis treat it as a civilization id. The
 * ruler register keeps its own list of polities with their own hints. If the two vocabularies are
 * different (the pack id "india" against the polity "bahmani_sultanate"), then a site can only be
 * attached when a ruler is named - and the site's own answer is never used.
 */
public final class SiteHintProbe {

    public static void main(String[] args) {
        HistoryGazetteer gaz = HistoryGazetteer.get();
        RulerRegister rr = RulerRegister.get();

        Set<String> known = new HashSet<>();
        for (RulerRegister.Polity p : rr.polities()) known.add(p.civHint());
        System.out.println("polity hints the ruler register knows: " + known.size());

        Map<String, Integer> sites = new HashMap<>();
        for (HistoryGazetteer.Site s : gaz.allSites()) {
            if (s.civHint() == null || s.civHint().isBlank()) continue;
            sites.merge(s.civHint(), 1, Integer::sum);
        }
        int distinct = sites.size();
        int resolvable = 0, unresolvable = 0;
        long resolvableSites = 0, unresolvableSites = 0;
        List<Map.Entry<String, Integer>> bad = new ArrayList<>();
        for (var e : sites.entrySet()) {
            if (known.contains(e.getKey())) { resolvable++; resolvableSites += e.getValue(); }
            else { unresolvable++; unresolvableSites += e.getValue(); bad.add(e); }
        }
        long total = resolvableSites + unresolvableSites;
        System.out.printf("distinct site civHints: %d  (resolvable %d, unresolvable %d)%n",
                distinct, resolvable, unresolvable);
        System.out.printf("sites carrying them   : %d  (resolvable %d = %.1f%%, unresolvable %d = %.1f%%)%n",
                total, resolvableSites, 100.0 * resolvableSites / total,
                unresolvableSites, 100.0 * unresolvableSites / total);
        bad.sort((a, b) -> b.getValue() - a.getValue());
        System.out.println("\nlargest unresolvable hints (a site carrying one can only be attached if a ruler is named):");
        for (int i = 0; i < Math.min(15, bad.size()); i++) {
            System.out.printf("  %6d sites  %s%n", bad.get(i).getValue(), bad.get(i).getKey());
        }
        System.out.println("\nthe register's own hints, for comparison (first 15):");
        known.stream().sorted().limit(15).forEach(h -> System.out.println("  " + h));
    }
}
