import com.eternalengine.civilization.HistoryGazetteer;
import com.eternalengine.civilization.RulerRegister;

import java.util.*;

/**
 * Derive the site-hint alias table FROM THE DATA, instead of guessing it.
 *
 * For every site hint the ruler register does not know, ask the register what it names for each of
 * those sites at the site's own years. Then:
 *
 *   - if every site under the hint resolves to ONE register hint, the pack id names one polity and
 *     the alias is safe ("china_tang -> tang_dynasty");
 *   - if it resolves to many, the pack id names a REGION, and no single alias is honest
 *     ("india -> maurya, saka, kushan, gupta, ...") - those must be resolved by year, not by table.
 *
 * Prints the safe aliases as Java-ready lines, and the regional ones as a list to leave alone.
 */
public final class AliasDeriveProbe {

    public static void main(String[] args) {
        HistoryGazetteer gaz = HistoryGazetteer.get();
        RulerRegister rr = RulerRegister.get();

        Set<String> known = new HashSet<>();
        for (RulerRegister.Polity p : rr.polities()) known.add(p.civHint());

        Map<String, Map<String, Integer>> votes = new TreeMap<>();
        Map<String, Integer> siteCount = new TreeMap<>();
        for (HistoryGazetteer.Site s : gaz.allSites()) {
            String h = s.civHint();
            if (h == null || h.isBlank() || known.contains(h)) continue;
            siteCount.merge(h, 1, Integer::sum);
            int year = Math.max(s.occupiedStart(), Math.min(s.occupiedEnd() - 1, s.occupiedStart() + 1));
            if (year < -3000 || year > 2026) continue;
            var hit = rr.rulerAt(s.lat(), s.lon(), year);
            if (hit.isEmpty() || hit.get().civHint() == null) continue;
            votes.computeIfAbsent(h, k -> new HashMap<>()).merge(hit.get().civHint(), 1, Integer::sum);
        }

        List<String> safe = new ArrayList<>();
        List<String> regional = new ArrayList<>();
        for (var e : votes.entrySet()) {
            String hint = e.getKey();
            var v = e.getValue();
            if (v.isEmpty()) continue;
            List<Map.Entry<String, Integer>> sorted = new ArrayList<>(v.entrySet());
            sorted.sort((a, b) -> b.getValue() - a.getValue());
            int all = sorted.stream().mapToInt(Map.Entry::getValue).sum();
            String top = sorted.get(0).getKey();
            double share = 100.0 * sorted.get(0).getValue() / all;
            String line = String.format("%-16s sites %6d  votes %2d  top %-28s %5.1f%%",
                    hint, siteCount.get(hint), all, top, share);
            // a safe alias: one register polity explains at least 90% of the sites, and the hint is
            // not one of the obvious multi-era packs
            boolean obviousRegion = hint.equals("india") || hint.equals("rome") || hint.equals("china")
                    || hint.equals("egypt") || hint.equals("greece");
            if (sorted.size() == 1 || (share >= 90.0 && !obviousRegion)) {
                safe.add(hint + "\t" + top + "\t" + line);
            } else {
                regional.add(line);
            }
        }
        System.out.println("SAFE ALIASES (" + safe.size() + ")");
        for (String s : safe) System.out.println("  " + s.split("\t")[2]);
        System.out.println("\nREGION IDS - no single alias is honest (" + regional.size() + ")");
        for (String s : regional.subList(0, Math.min(25, regional.size()))) System.out.println("  " + s);
        System.out.println("\nJAVA TABLE");
        for (String s : safe) {
            String[] p = s.split("\t");
            System.out.printf("        table.put(\"%s\", \"%s\");%n", p[0], p[1]);
        }
    }
}
