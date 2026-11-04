import com.eternalengine.civilization.RulerRegister;
import com.eternalengine.civilization.WhoRuled;

/**
 * Does a polity win where and when it says it ruled? (2026-10-27)
 *
 * <p>Two questions, deliberately kept apart, because one probe answered them together and misled me twice:
 *
 * <ol>
 *   <li><b>Core accuracy</b> - at the cell that records the polity for the most years (its metropole, for
 *       a normal state), is the polity the answer, year by year? Reported as a rate, so a span that is
 *       right for three centuries and wrong in its last twenty shows up as a tail rather than a pass.</li>
 *   <li><b>Existence</b> - across up to twelve cells spread over the polity's whole recorded territory,
 *       does it win <em>anywhere</em> in its own interval? A polity that wins nowhere it claims to have
 *       ruled is a real defect. A polity that wins at its capital but not in a colony it held for six
 *       years is not.</li>
 * </ol>
 *
 * <p>The earlier version measured "core" as one cell plus its nearest neighbours, which put the British
 * Empire's sample in India and the Astrakhan Khanate's in Crimea, and then reported them as polities that
 * lose at their own centre. They were losing in possessions, which is a different and unremarkable thing.
 */
public final class SpanHonestyProbe {
    private static final int SPREAD_CELLS = 12;

    public static void main(String[] args) {
        RulerRegister rr = RulerRegister.get();
        java.util.List<String> rows = new java.util.ArrayList<>();
        rows.add("polity\tspanStart\tspanEnd\tyear\tlat\tlon\tanswered\tverdict\tcentreKm");

        int polities = 0, intervals = 0, coreSamples = 0, coreSelf = 0, coreOther = 0, coreNone = 0;
        int neverCore = 0, neverAnywhere = 0, partlyLost = 0, clean = 0;
        int terrSamples = 0, terrSelf = 0;
        java.util.List<String> coreGaps = new java.util.ArrayList<>();
        java.util.List<String> ghost = new java.util.ArrayList<>();

        for (var polity : rr.polities()) {
            var ext = rr.extentOf(polity.civHint());
            if (ext.isEmpty()) {
                continue;
            }
            var e = ext.get();
            if (e.places() <= 0) {
                continue;
            }
            var spans = rr.spansOf(polity.civHint());
            if (spans.isEmpty()) {
                continue;
            }
            polities++;
            java.util.List<double[]> cells = rr.placesOf(polity.civHint(), SPREAD_CELLS);
            if (cells.isEmpty()) {
                cells = java.util.List.of(new double[] {e.lat(), e.lon()});
            }
            double[] core = cells.get(0);

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

                // (1) the core cell, year by year - the rate that shows the tail
                int cSelf = 0, cLost = 0, cNone = 0;
                double worstKm = -1;
                for (int year : years) {
                    coreSamples++;
                    var ans = WhoRuled.answer(java.util.List.of(), core[0], core[1], year);
                    String verdict;
                    if (!ans.known()) {
                        coreNone++; cNone++; verdict = "NOBODY";
                    } else if (ans.name().equals(polity.name())) {
                        coreSelf++; cSelf++; verdict = "SELF";
                    } else {
                        coreOther++; cLost++; verdict = "OTHER";
                        var oe = rr.extentOf(ans.civId());
                        if (oe.isPresent()) {
                            double km = WhoRuled.distanceKmStatic(core[0], core[1],
                                    oe.get().lat(), oe.get().lon());
                            if (km > worstKm) { worstKm = km; }
                        }
                    }
                    rows.add(String.format(java.util.Locale.ROOT,
                            "%s\t%d\t%d\t%d\t%.2f\t%.2f\t%s\t%s\t%.0f",
                            polity.name(), a, b, year, core[0], core[1],
                            ans.known() ? ans.name() : "-", verdict, worstKm));
                }
                if (cSelf == 0) {
                    neverCore++;
                    coreGaps.add(String.format(java.util.Locale.ROOT,
                            "%-42s %6d-%-6d never wins at the core cell (worst %.0f km)",
                            polity.name(), a, b, worstKm));
                } else if (cLost + cNone > 0) {
                    partlyLost++;
                } else {
                    clean++;
                }

                // (2) existence: does it win anywhere in the territory it claims? Also the harsh rate:
                // over EVERY cell it is recorded on, possessions included, how often is it the answer?
                // Reported so the favourable core-cell figure cannot be the only one on the page.
                boolean wonSomewhere = cSelf > 0;
                for (int i = 1; i < cells.size(); i++) {
                    for (int year : years) {
                        var ans = WhoRuled.answer(java.util.List.of(), cells.get(i)[0], cells.get(i)[1], year);
                        terrSamples++;
                        if (ans.known() && ans.name().equals(polity.name())) {
                            terrSelf++;
                            wonSomewhere = true;
                        }
                    }
                }
                if (!wonSomewhere) {
                    neverAnywhere++;
                    ghost.add(String.format(java.util.Locale.ROOT,
                            "%-42s %6d-%-6d wins NOWHERE in %d cells", polity.name(), a, b, cells.size()));
                }
            }
        }

        try {
            java.nio.file.Files.write(java.nio.file.Path.of("/home/user/testrun/verify/span_honesty.csv"), rows);
        } catch (Exception ex) { System.out.println("write failed: " + ex.getMessage()); }

        System.out.println("polities measured                  : " + polities);
        System.out.println("recorded intervals                 : " + intervals);
        System.out.println();
        System.out.println("--- (1) at the core cell, year by year ---");
        System.out.println("sampled years                      : " + coreSamples);
        System.out.println("  polity is the answer            : " + coreSelf + pct(coreSelf, coreSamples));
        System.out.println("  a DIFFERENT polity is           : " + coreOther + pct(coreOther, coreSamples));
        System.out.println("  nobody is                       : " + coreNone + pct(coreNone, coreSamples));
        System.out.println("intervals held cleanly             : " + clean + pct(clean, intervals));
        System.out.println("intervals partly lost (class A)    : " + partlyLost + pct(partlyLost, intervals));
        System.out.println("intervals never won at the core    : " + neverCore + pct(neverCore, intervals));
        System.out.println();
        System.out.println("--- (2) over the WHOLE recorded territory, colonies included (the harsh rate) ---");
        System.out.println("sampled cell-years               : " + terrSamples);
        System.out.println("  polity is the answer          : " + terrSelf + pct(terrSelf, terrSamples));
        System.out.println();
        System.out.println("--- (3) existence: won anywhere in up to " + SPREAD_CELLS + " spread cells ---");
        System.out.println("intervals won NOWHERE              : " + neverAnywhere + pct(neverAnywhere, intervals));
        System.out.println();
        System.out.println("--- never won at the core, but exists somewhere (sampling, not a defect) ---");
        for (String s : coreGaps) {
            System.out.println("  " + s);
        }
        System.out.println("  (" + coreGaps.size() + ")");
        System.out.println();
        System.out.println("--- wins NOWHERE in its own territory ---");
        for (String s : ghost) {
            System.out.println("  " + s);
        }
        System.out.println("  (" + ghost.size() + ")  full data: testrun/verify/span_honesty.csv");
    }

    private static String pct(int n, int d) {
        return d == 0 ? "" : String.format(java.util.Locale.ROOT, "  (%4.1f%%)", 100.0 * n / d);
    }
}
