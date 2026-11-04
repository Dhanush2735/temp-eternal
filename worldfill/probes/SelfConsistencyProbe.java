import com.eternalengine.civilization.RulerRegister;
import com.eternalengine.civilization.WhoRuled;

/**
 * Does every polity in the register win at its own centre? (2026-10-24)
 *
 * <p>Found by hand-checking places against sources: at Legnica, the capital of the Duchy of Legnica, the
 * register answered "Holy Roman Empire" in 1619, not the Duchy - although "Duchy of Legnica" is in the
 * register. A polity that loses at its own centre is either not covered where it should be, or is being
 * outranked by its own overlord.
 */
public final class SelfConsistencyProbe {
    public static void main(String[] args) {
        RulerRegister rr = RulerRegister.get();
        int tested = 0, self = 0, other = 0, none = 0, unionWrong = 0, unionItself = 0;
        java.util.Map<String, Integer> losers = new java.util.TreeMap<>();
        java.util.List<String> rows = new java.util.ArrayList<>();
        rows.add("polity\tstart\tend\tlat\tlon\tyear\tanswered\tverdict\townPlaces\tansweredPlaces\tsizeRatio\tcentreKm\tgapYear\tgapAnswered");
        for (var polity : rr.polities()) {
            var ext = rr.extentOf(polity.civHint());
            if (ext.isEmpty()) {
                continue;
            }
            var e = ext.get();
            if (e.start() >= e.end() || e.places() <= 0) {
                continue;
            }
            // Measure at a year the polity certainly existed, NOT the midpoint of its first-to-last
            // union: a polity that came and went (Niebla 1023-53, 1145-50, 1234-62) has a union
            // midpoint inside a gap, so the "wrong" answer was right for a year it was not there.
            int year = e.core();
            int unionYear = e.start() + (e.end() - e.start()) / 2;
            var unionAnswer = WhoRuled.answer(java.util.List.of(), e.lat(), e.lon(), unionYear);
            boolean unionOther = (!unionAnswer.known() || !unionAnswer.name().equals(polity.name()));
            if (unionOther) { unionWrong++; } else { unionItself++; }
            tested++;
            var answer = WhoRuled.answer(java.util.List.of(), e.lat(), e.lon(), year);
            var hit = answer.known() ? java.util.Optional.of(answer) : java.util.Optional.<WhoRuled.Answer>empty();
            String verdict;
            if (hit.isEmpty()) {
                none++;
                verdict = "NOBODY";
            } else if (hit.get().name().equals(polity.name())) {
                self++;
                verdict = "SELF";
            } else {
                other++;
                verdict = "OTHER";
                losers.merge(polity.name() + " -> " + hit.get().name(), 1, Integer::sum);
            }
            int ownPlaces = e.places();
            int otherPlaces = 0;
            double centreKm = -1;
            if (hit.isPresent()) {
                var oe = rr.extentOf(hit.get().civId());
                otherPlaces = oe.map(RulerRegister.Extent::places).orElse(0);
                if (oe.isPresent()) {
                    // How far apart the two polities' recorded centres are. A winner on another continent
                    // cannot be a span overrun - it is a plainly wrong answer (class B, board: batch 1).
                    centreKm = com.eternalengine.civilization.WhoRuled.distanceKmStatic(
                            e.lat(), e.lon(), oe.get().lat(), oe.get().lon());
                }
            }
            double ratio = ownPlaces == 0 ? 0 : (double) otherPlaces / ownPlaces;
            rows.add(String.format(java.util.Locale.ROOT,
                    "%s\t%d\t%d\t%.3f\t%.3f\t%d\t%s\t%s\t%d\t%d\t%.1f\t%.0f\t%d\t%s",
                    polity.name(), e.start(), e.end(), e.lat(), e.lon(), year,
                    hit.isPresent() ? hit.get().name() : "-", verdict, ownPlaces, otherPlaces, ratio, centreKm,
                    unionYear, unionAnswer.known() ? unionAnswer.name() : "-"));
        }
        try {
            java.nio.file.Files.write(java.nio.file.Path.of("/home/user/testrun/verify/self_consistency.csv"), rows);
        } catch (Exception ex) { System.out.println("write failed: " + ex.getMessage()); }

        System.out.println("polities tested at their own centre : " + tested);
        System.out.println("  answered as itself                : " + self + pct(self, tested));
        System.out.println("  answered as a DIFFERENT polity    : " + other + pct(other, tested));
        System.out.println("  answered nobody                   : " + none + pct(none, tested));
        System.out.println();
        // Triage: a polity that loses to something recorded on many more places is an overlord class;
        // a polity that loses to something recorded on FEWER places is more likely a genuine neighbour
        // dispute. This separates the two, because the raw count cannot.
        int overlord = 0, similar = 0, smaller = 0;
        for (String line : rows) {
            String[] f = line.split("\t");
            if (f.length < 11 || !"OTHER".equals(f[7])) {
                continue;
            }
            double ratio = Double.parseDouble(f[10]);
            if (ratio >= 5.0) {
                overlord++;
            } else if (ratio >= 0.5) {
                similar++;
            } else {
                smaller++;
            }
        }
        System.out.println("--- triage of the " + other + " that lose ---");
        System.out.println("  lost to a polity recorded on 5x more places (overlord class) : " + overlord);
        System.out.println("  lost to a polity of comparable size (neighbour/claim)        : " + similar);
        System.out.println("  lost to a polity recorded on far FEWER places                : " + smaller);
        int crossContinent = 0;
        for (String line : rows) {
            String[] f = line.split("\t");
            if (f.length >= 12 && "OTHER".equals(f[7]) && Double.parseDouble(f[11]) > 3000) {
                crossContinent++;
            }
        }
        System.out.println("  winner's centre is >3,000 km away (a plainly WRONG answer)   : " + crossContinent);
        System.out.println();
        System.out.println("--- the twenty commonest collapses ---");
        losers.entrySet().stream().sorted((a, b) -> Integer.compare(b.getValue(), a.getValue())).limit(20)
              .forEach(e -> System.out.printf(java.util.Locale.ROOT, "  %3d  %s%n", e.getValue(), e.getKey()));
    }

    private static String pct(int n, int total) {
        return total == 0 ? "" : String.format(java.util.Locale.ROOT, "  (%.1f%%)", 100.0 * n / total);
    }
}
