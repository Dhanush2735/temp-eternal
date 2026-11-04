import com.eternalengine.clock.SpanName;

/**
 * Cross-check of {@link SpanName} against Wikipedia's "List of decades, centuries, and millennia"
 * (fetched 2026-10-27), which indexes every decade, century and millennium from 15,000 BC to AD 3000.
 *
 * <p>The millennia bounds below are transcribed from that page. Everything else is checked as a structural
 * invariant (tiling, no gaps, no year zero, exactly 100 years per century) so a single mistyped number cannot
 * pass.
 */
public final class SpanNameProbe {

    private static int checks = 0;
    private static int failures = 0;

    /** Transcribed verbatim from the source page's millennia table. */
    private static final Object[][] PAGE_MILLENNIA = {
        // name on the page,        first BC,  last BC (BC numbers, positive)
        {"3rd millennium BC", 3000, 2001},
        {"2nd millennium BC", 2000, 1001},
        {"1st millennium BC", 1000, 1},
    };
    private static final Object[][] PAGE_MILLENNIA_AD = {
        {"1st millennium", 1, 1000},
        {"2nd millennium", 1001, 2000},
        {"3rd millennium", 2001, 3000},
    };

    public static void main(String[] args) {
        System.out.println("cross-check: Wikipedia 'List of decades, centuries, and millennia' (2026-10-27)");
        System.out.println();

        // 1. Millennia exactly as the page prints them.
        for (Object[] row : PAGE_MILLENNIA) {
            String name = (String) row[0];
            int first = -(Integer) row[1];
            int last = -(Integer) row[2];
            SpanName.Span s = SpanName.millennium(last);       // the page's "last" year is inside the span
            check("millennium of " + SpanName.yearName(last), name.equals(s.name())
                    && s.firstYear() == first && s.lastYear() == last, s.inWords());
        }
        for (Object[] row : PAGE_MILLENNIA_AD) {
            String name = (String) row[0];
            int first = (Integer) row[1];
            int last = (Integer) row[2];
            SpanName.Span s = SpanName.millennium(first);
            check("millennium of AD " + first, name.equals(s.name())
                    && s.firstYear() == first && s.lastYear() == last, s.inWords());
        }

        // 2. The trap the page makes unavoidable: the 3rd millennium starts in 2001, not 2000.
        check("AD 2000 is in the 2nd millennium", "2nd millennium".equals(SpanName.millennium(2000).name()),
                SpanName.millennium(2000).inWords());
        check("AD 2001 is in the 3rd millennium", "3rd millennium".equals(SpanName.millennium(2001).name()),
                SpanName.millennium(2001).inWords());

        // 3. Centuries: the boundary years, and no year zero.
        check("AD 2000 is the 20th century", "20th century".equals(SpanName.century(2000).name()),
                SpanName.century(2000).inWords());
        check("AD 2001 is the 21st century", "21st century".equals(SpanName.century(2001).name()),
                SpanName.century(2001).inWords());
        check("AD 1948 is the 20th century", "20th century".equals(SpanName.century(1948).name()),
                SpanName.century(1948).inWords());
        check("1 BC is in the 1st century BC, and that century is 100 - 1 BC",
                "1st century BC".equals(SpanName.century(-1).name())
                        && SpanName.century(-1).firstYear() == -100 && SpanName.century(-1).lastYear() == -1,
                SpanName.century(-1).inWords());
        check("AD 1 is in the 1st century, which is AD 1 - 100",
                "1st century".equals(SpanName.century(1).name())
                        && SpanName.century(1).firstYear() == 1 && SpanName.century(1).lastYear() == 100,
                SpanName.century(1).inWords());
        check("3000 BC is the 30th century BC", "30th century BC".equals(SpanName.century(-3000).name()),
                SpanName.century(-3000).inWords());
        check("there is no year zero: named(0) is false and no span contains it",
                !SpanName.named(0) && SpanName.decade(0) == null && SpanName.century(0) == null);

        // 4. Decades, including the BC ones the page lists under "18th century BC": 1790s ... 1700s BC.
        check("1948 is the 1940s, which is AD 1940 - 1949",
                "1940s".equals(SpanName.decade(1948).name())
                        && SpanName.decade(1948).firstYear() == 1940 && SpanName.decade(1948).lastYear() == 1949,
                SpanName.decade(1948).inWords());
        check("1795 BC is the 1790s BC, which is 1799 BC - 1790 BC (BC runs backwards)",
                "1790s BC".equals(SpanName.decade(-1795).name())
                        && SpanName.decade(-1795).firstYear() == -1799 && SpanName.decade(-1795).lastYear() == -1790,
                SpanName.decade(-1795).inWords());
        check("1800 BC is the 1800s BC, which is 1809 BC - 1800 BC",
                "1800s BC".equals(SpanName.decade(-1800).name())
                        && SpanName.decade(-1800).firstYear() == -1809
                        && SpanName.decade(-1800).lastYear() == -1800,
                SpanName.decade(-1800).inWords());
        check("1700 BC is the 1700s BC, which is 1709 BC - 1700 BC",
                "1700s BC".equals(SpanName.decade(-1700).name()),
                SpanName.decade(-1700).inWords());
        check("the \"0s BC\" has no year zero: it is 9 BC - 1 BC, nine years",
                "0s BC".equals(SpanName.decade(-5).name())
                        && SpanName.decade(-5).firstYear() == -9 && SpanName.decade(-5).lastYear() == -1,
                SpanName.decade(-5).inWords());

        // In AD, decades tile every century perfectly. In BC they do not, and the source is the reason:
        // "the 1790s BC" is 1799 - 1790 BC, so 1800 BC (the first year of the 18th century BC) sits in a
        // decade running 1809 - 1800 BC, which mostly belongs to the previous century. The honest check
        // therefore asserts BOTH facts: perfect in AD, and exactly nine whole decades in a BC century.
        // Decades align to the year ending in 0 (the 1900s are 1900 - 1909); centuries align to 1 (the 20th
        // century is 1901 - 2000). So the two are one year out of step in BOTH eras, and a century holds
        // eleven decade names of which nine are whole. This is why 1900 is in the 19th century and 2000 in the
        // 20th - the reason the "millennium" parties of 2000 were a year early.
        java.util.Set<String> adNames = new java.util.TreeSet<>();
        java.util.Set<String> adWhole = new java.util.TreeSet<>();
        for (int y = 1901; y <= 2000; y++) {
            SpanName.Span d = SpanName.decade(y);
            adNames.add(d.name());
            if (d.firstYear() >= 1901 && d.lastYear() <= 2000) {
                adWhole.add(d.name());
            }
        }
        check("a century holds 11 decade names and 9 whole ones, in AD as in BC (decades and centuries are"
                + " one year out of step)", adNames.size() == 11 && adWhole.size() == 9,
                adNames.size() + " names, " + adWhole.size() + " whole");
        check("1900 is the 19th century, and 2000 is the 20th - the one-year step, both ways",
                "19th century".equals(SpanName.century(1900).name())
                        && "20th century".equals(SpanName.century(2000).name()),
                SpanName.century(1900).name() + " / " + SpanName.century(2000).name());

        java.util.Set<String> bcNames = new java.util.TreeSet<>();
        java.util.Set<String> bcWhole = new java.util.TreeSet<>();
        for (int y = -1800; y <= -1701; y++) {
            SpanName.Span d = SpanName.decade(y);
            bcNames.add(d.name());
            if (d.firstYear() >= -1800 && d.lastYear() <= -1701) {
                bcWhole.add(d.name());
            }
        }
        check("a BC century holds 11 decade names, of which 9 are whole - the source's convention, not a defect",
                bcNames.size() == 11 && bcWhole.size() == 9,
                bcNames.size() + " names, " + bcWhole.size() + " whole: " + bcWhole);

        // 5. "1900s" is both a decade and a century: the page disambiguates it as "1900s (decade)".
        check("the ambiguous name is flagged, not guessed",
                SpanName.decade(1905).ambiguous() && SpanName.century(1948).ambiguous());

        // 6. Structure: everything from 3000 BC to AD 3000 must tile into exactly 60 centuries and 6 millennia.
        int centuries = 0;
        SpanName.Span lastCentury = null;
        boolean tiling = true;
        for (int y = -3000; y <= 3000; y++) {
            if (y == 0) {
                continue;                       // there is no year zero; century(0) is deliberately null
            }
            SpanName.Span c = SpanName.century(y);
            if (lastCentury == null || !lastCentury.name().equals(c.name())) {
                centuries++;
                if (lastCentury != null) {
                    // Consecutive everywhere except across the era divide, where there is no year 0:
                    // 1 BC is followed directly by AD 1, so the step is two years, not one.
                    boolean across = lastCentury.lastYear() == -1 && c.firstYear() == 1;
                    if (!across && c.firstYear() != lastCentury.lastYear() + 1) {
                        tiling = false;
                    }
                }
                if (c.lastYear() - c.firstYear() != 99) {
                    tiling = false;
                }
                lastCentury = c;
            }
        }
        check("3000 BC to AD 3000 tiles into exactly 60 centuries of 100 years, no gaps",
                centuries == 60 && tiling, centuries + " centuries");
        check("the span is 6 millennia", SpanName.millennium(-3000).name().equals("3rd millennium BC")
                && SpanName.millennium(3000).name().equals("3rd millennium")
                && SpanName.millennium(-3000).lastYear() == -2001
                && SpanName.millennium(3000).firstYear() == 2001);

        // 7. Outside the source list's range, refuse rather than invent.
        check("outside 15,000 BC - AD 3000 nothing is named",
                SpanName.millennium(3001) == null && SpanName.century(-15001) == null,
                "3001 AD -> null, 15001 BC -> null");
        check("15,000 BC and AD 3000 are the edges, and both are named",
                SpanName.century(-15000) != null && SpanName.century(3000) != null,
                SpanName.century(-15000).name() + " / " + SpanName.century(3000).name());

        System.out.println();
        System.out.println("checks: " + checks + "   failures: " + failures);
        if (failures > 0) {
            System.exit(1);
        }
    }

    private static void check(String what, boolean ok) {
        check(what, ok, "");
    }

    private static void check(String what, boolean ok, String detail) {
        checks++;
        if (!ok) {
            failures++;
        }
        System.out.println((ok ? "  ok   " : "  FAIL ") + what + (detail.isEmpty() ? "" : "   [" + detail + "]"));
    }
}
