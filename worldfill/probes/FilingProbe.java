import com.eternalengine.civilization.FamousPeople;
import com.eternalengine.civilization.RulerRegister;

import java.util.*;

/**
 * Which people are filed under a state that did not exist while they lived, and what SHOULD they be?
 *
 * <p>The 2026-10-22 audit found 18 of 400 sampled people filed under a modern container - a man who
 * died in 1770 under "United Kingdom" (inception 1921), a Spaniard who died in 1700 under "Spain"
 * (1715). This probe finds every such row in the pack and, for each, asks the ruler register what it
 * names for that person's own place and year. That answer is the correction, and it comes from the
 * project's own record rather than from me.
 *
 * <p>It also reports the rows where the register has no answer: those cannot be corrected this way and
 * must not be guessed at.
 */
public final class FilingProbe {

    /** Polities whose Wikidata "inception" is modern but whose id is used for older people. */
    private static final Map<String, Integer> CONTAINER_START = Map.ofEntries(
            Map.entry("Q145", 1921),
            Map.entry("Q29", 1715),
            Map.entry("Q183", 1949),
            Map.entry("Q38", 1946),
            Map.entry("Q30", 1776),
            Map.entry("Q142", 1958),
            Map.entry("Q16", 1867),
            Map.entry("Q408", 1901),
            Map.entry("Q159", 1991),
            Map.entry("Q148", 1949),
            Map.entry("Q43", 1923),
            Map.entry("Q155", 1889),
            Map.entry("Q96", 1821),
            Map.entry("Q884", 1948),
            Map.entry("Q717", 1811));

    public static void main(String[] args) {
        boolean apply = args.length > 0 && args[0].equals("--report-rows");
        FamousPeople fp = FamousPeople.get();
        RulerRegister rr = RulerRegister.get();

        List<FamousPeople.Person> people = new ArrayList<>();
        fp.all().forEach(people::add);
        System.out.println("people in the master: " + people.size());

        int checked = 0, containerRows = 0, fixable = 0, unfixable = 0, alreadyRight = 0;
        Map<String, Integer> byContainer = new TreeMap<>();
        Map<String, Integer> fixes = new TreeMap<>();
        List<String> examples = new ArrayList<>();

        for (FamousPeople.Person p : people) {
            String st = p.state();
            if (st == null) continue;
            Integer start = CONTAINER_START.get(st);
            if (start == null) continue;
            // the year the row is really about: the middle of the person's active life
            int from = p.activeFrom() > 0 ? p.activeFrom() : p.activeTo();
            if (from == 0 || from >= start) continue;      // not a container misuse
            checked++;
            containerRows++;
            byContainer.merge(st, 1, Integer::sum);
            var hit = rr.rulerAt(p.lat(), p.lon(), from);
            String reg = hit.map(RulerRegister.Hit::wikidata).orElse(null);
            if (reg == null) { unfixable++; continue; }
            if (reg.equals(st)) { alreadyRight++; continue; }
            fixable++;
            fixes.merge(st + " -> " + reg + " (" + hit.get().ruler() + ")", 1, Integer::sum);
            if (examples.size() < 12) {
                examples.add(String.format("%-34s active %5d, filed %s, register says %s (%s)",
                        p.name(), from, st, reg, hit.get().ruler()));
            }
        }
        System.out.printf("%nrows using a modern container for an older life: %d%n", containerRows);
        System.out.printf("  the register has a better answer : %d (%.1f%%)%n",
                fixable, 100.0 * fixable / Math.max(1, containerRows));
        System.out.printf("  the register names nothing       : %d%n", unfixable);
        System.out.printf("  the register agrees with the row : %d%n", alreadyRight);
        System.out.println("\nby container:");
        byContainer.forEach((k, v) -> System.out.printf("  %-6s %6d%n", k, v));
        System.out.println("\nsuggested corrections, most common first:");
        fixes.entrySet().stream().sorted((a, b) -> b.getValue() - a.getValue()).limit(15)
                .forEach(e -> System.out.printf("  %5d  %s%n", e.getValue(), e.getKey()));
        System.out.println("\nsample rows:");
        for (String e : examples) System.out.println("  " + e);
    }
}
