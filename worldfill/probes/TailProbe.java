import com.eternalengine.civilization.RulerRegister;
import com.eternalengine.civilization.WhoRuled;

/**
 * Which spans overrun their polity, and by how much - decided from the register's own evidence. (2026-10-27)
 *
 * <p>The span probe says "this polity is right for most of its interval and loses the end". It cannot say
 * whether the <b>span</b> is wrong or the <b>ranking</b> is. This probe separates the two without reading an
 * encyclopaedia, using one fact: <b>two polities cannot rule the same cell in the same year.</b>
 *
 * <p>When polity A loses a year at a cell to polity W, the register is claiming both. If W's own span at that
 * cell <b>starts at or just before</b> the first year A loses, and continues past the last year A loses, then
 * the register is telling us W took the cell there - so A's claim is the one that is wrong, and A really ended
 * around {@code W.start - 1}. That is a date error, and it is fixable.
 *
 * <p>If instead W's span started long before the loss, the two simply overlap and W wins on rank - a vassal
 * and its overlord, or a smaller polity inside a larger one. That is not a date error and must not be clamped.
 *
 * <p><b>The five-cell rule.</b> One cell can be a rasterising artefact: Rome sits between a Roman cell and an
 * empty coastal one. A polity whose proposed end is agreed by <b>five or more independent cells</b> is a data
 * error worth source-reading. Below that, it is reported and left alone.
 */
public final class TailProbe {
    private static final int CELLS = 12;
    private static final int MIN_CELLS = 1;

    /** One cell's opinion about where a polity really ended. */
    private record Vote(double lat, double lon, int candidateEnd, String winner, int winnerStart) {}

    public static void main(String[] args) {
        RulerRegister rr = RulerRegister.get();
        java.util.List<String> rows = new java.util.ArrayList<>();
        rows.add("polity\tspanStart\tspanEnd\tboundary\tlostYears\tcandidateEnd\tcellsAgree\twinners");

        int intervals = 0, tails = 0, heads = 0, middles = 0;
        java.util.List<String> strong = new java.util.ArrayList<>();

        for (var polity : rr.polities()) {
            var ext = rr.extentOf(polity.civHint());
            if (ext.isEmpty() || ext.get().places() <= 0) {
                continue;
            }
            var spans = rr.spansOf(polity.civHint());
            var cells = rr.placesOf(polity.civHint(), CELLS);
            if (spans.isEmpty() || cells.isEmpty()) {
                continue;
            }
            for (int[] span : spans) {
                int a = span[0], b = span[1];
                if (b < a) { int t = a; a = b; b = t; }
                intervals++;
                int len = b - a;
                int n = Math.min(6, Math.max(2, len + 1));
                int[] years = new int[n];
                for (int k = 0; k < n; k++) {
                    years[k] = a + (n == 1 ? 0 : (int) Math.round((double) len * k / (n - 1)));
                }

                java.util.List<Vote> votes = new java.util.ArrayList<>();
                int lost = 0, lostAtHead = 0, lostAtTail = 0;
                java.util.Set<String> winners = new java.util.TreeSet<>();

                // The METROPOLE cell only. A multi-cell polity legitimately loses different
                // provinces in different years, so a vote across its cells measures conquests,
                // not its end. The core cell is the one that answers the existence question.
                for (double[] cell : cells.subList(0, 1)) {
                    boolean[] won = new boolean[n];
                    String[] who = new String[n];
                    int[] wStart = new int[n];
                    for (int k = 0; k < n; k++) {
                        var ans = WhoRuled.answer(java.util.List.of(), cell[0], cell[1], years[k]);
                        won[k] = ans.known() && ans.name().equals(polity.name());
                        who[k] = ans.known() ? ans.name() : "-";
                        wStart[k] = ans.known() ? ans.start() : 0;
                        if (!won[k]) {
                            lost++;
                            if (k == 0) { lostAtHead++; }
                            if (k == n - 1) { lostAtTail++; }
                            if (ans.known()) { winners.add(ans.name()); }
                        }
                    }
                    boolean all = true, none = true;
                    for (boolean w : won) {
                        if (w) { none = false; } else { all = false; }
                    }
                    if (none || all) {
                        continue;                       // nothing won anywhere, or nothing lost: no opinion
                    }

                    // A CLEAN TAIL CUT: some year after which every sampled year is lost, with at least
                    // one sampled year still won before it. That shape - held, then gone - is what an
                    // overrunning end looks like. A loss in the middle is an overlap, not a date error.
                    int cut = -1;
                    for (int k = 1; k < n; k++) {
                        if (won[k - 1] && !won[k]) {
                            boolean restLost = true;
                            for (int j = k; j < n; j++) {
                                if (won[j]) { restLost = false; break; }
                            }
                            if (restLost) { cut = years[k]; }
                        }
                    }
                    if (cut < 0) {
                        continue;
                    }
                    // The winner must be the same polity for the whole lost stretch, and its own span
                    // must have begun at or before the cut - the register saying "this one took over".
                    String tailWinner = null;
                    boolean consistent = true;
                    for (int k = 0; k < n; k++) {
                        if (years[k] < cut) {
                            continue;
                        }
                        if (tailWinner == null) { tailWinner = who[k]; }
                        else if (!tailWinner.equals(who[k])) { consistent = false; }
                        if (wStart[k] > cut + 2) { consistent = false; }
                    }
                    if (!consistent) {
                        continue;
                    }
                    // A cut within one sampling step is my own grid's resolution, not an overrun.
                    int step = Math.max(1, len / Math.max(1, n - 1));
                    if (b - (cut - 1) < Math.max(10, 2 * step)) {
                        continue;
                    }
                    votes.add(new Vote(cell[0], cell[1], cut - 1, tailWinner, 0));
                }

                if (lost == 0) {
                    continue;
                }
                String boundary = lostAtTail > lostAtHead ? "TAIL"
                        : (lostAtHead > lostAtTail ? "HEAD" : "MIDDLE/FLAT");
                if ("TAIL".equals(boundary)) { tails++; }
                else if ("HEAD".equals(boundary)) { heads++; }
                else { middles++; }

                // How many cells independently propose the same end?
                java.util.Map<Integer, Integer> agree = new java.util.TreeMap<>();
                for (Vote v : votes) {
                    if (v.candidateEnd() != Integer.MIN_VALUE) {
                        agree.merge(v.candidateEnd(), 1, Integer::sum);
                    }
                }
                int bestEnd = Integer.MIN_VALUE, bestCount = 0;
                for (var e : agree.entrySet()) {
                    if (e.getValue() > bestCount) { bestCount = e.getValue(); bestEnd = e.getKey(); }
                }
                // Allow +-2 years of slack between cells; the register's cells disagree slightly.
                int slacked = 0;
                if (bestEnd != Integer.MIN_VALUE) {
                    for (Vote v : votes) {
                        if (v.candidateEnd() != Integer.MIN_VALUE
                                && Math.abs(v.candidateEnd() - bestEnd) <= 2) {
                            slacked++;
                        }
                    }
                }
                rows.add(String.format(java.util.Locale.ROOT, "%s\t%d\t%d\t%s\t%d\t%s\t%d\t%s",
                        polity.name(), a, b, boundary, lost,
                        bestEnd == Integer.MIN_VALUE ? "-" : String.valueOf(bestEnd),
                        slacked, String.join(",", winners)));
                if (slacked >= MIN_CELLS) {
                    strong.add(String.format(java.util.Locale.ROOT,
                            "%-42s %6d-%-6d ends %6d by %2d cells (now %d)  winner %s",
                            polity.name(), a, b, bestEnd, slacked, b,
                            winners.isEmpty() ? "-" : winners.iterator().next()));
                }
            }
        }

        try {
            java.nio.file.Files.write(java.nio.file.Path.of("/home/user/testrun/verify/tails.csv"), rows);
        } catch (Exception ex) { System.out.println("write failed: " + ex.getMessage()); }

        System.out.println("intervals examined                 : " + intervals);
        System.out.println("  lose the TAIL (the candidate class): " + tails);
        System.out.println("  lose the HEAD                     : " + heads);
        System.out.println("  lose the middle / flat            : " + middles);
        System.out.println();
        System.out.println("--- spans the register contradicts itself about (" + MIN_CELLS + "+ cells agree) ---");
        for (String s : strong) {
            System.out.println("  " + s);
        }
        System.out.println("  (" + strong.size() + " of " + tails + " tails)  full data: testrun/verify/tails.csv");
    }
}
