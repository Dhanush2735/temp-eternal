import com.eternalengine.here.HereAndNow;

/**
 * Step 62: the reading at the plan's own test places and years, and the empty places beside them.
 * Prints every reading in full (only reading the output checks the claim) and asserts the rules
 * that must hold wherever it is asked.
 */
public class HereProbe {

    private static int checks = 0;
    private static int failed = 0;

    private static void check(boolean ok, String what) {
        checks++;
        if (!ok) {
            failed++;
            System.out.println("  FAIL " + what);
        }
    }

    private static boolean containsAny(String line, String[] words) {
        for (String w : words) {
            if (line.contains(w)) {
                return true;
            }
        }
        return false;
    }

    public static void main(String[] args) {
        Object[][] spots = {
            {"Hyderabad 1500", 17.39, 78.49, 1500},
            {"Hyderabad 1700", 17.39, 78.49, 1700},
            {"Hyderabad 1948", 17.39, 78.49, 1948},
            {"Hyderabad 2026", 17.39, 78.49, 2026},
            {"Hyderabad 3000 (guardrail)", 17.39, 78.49, 3000},
            {"Hyderabad outskirts 3000 BC (doubt 1)", 17.4346, 78.5016, -3000},
            {"Delhi 1650", 28.65, 77.23, 1650},
            {"Rome AD 100", 41.90, 12.50, 100},
            {"London 1700", 51.51, -0.13, 1700},
            {"Beijing 1500", 39.90, 116.40, 1500},
            {"Cusco 1500", -13.53, -71.97, 1500},
            {"Ur 2500 BC", 30.96, 46.10, -2500},
            {"Mohenjo-daro 2500 BC", 27.32, 68.14, -2500},
            {"Mid-Sahara 1000", 23.0, 10.0, 1000},
            {"Siberia 1000", 60.0, 100.0, 1000},
            {"Ohio valley 1200", 39.0, -84.0, 1200},
        };
        for (Object[] s : spots) {
            String label = (String) s[0];
            double lat = (Double) s[1], lon = (Double) s[2];
            int year = (Integer) s[3];
            HereAndNow.Reading r = HereAndNow.read(lat, lon, year);
            System.out.println("==== " + label);
            System.out.println(r.text());
            System.out.println("---- one line: " + r.shortLine());
            System.out.println();

            // ---- the rules that must hold everywhere
            check(r.year() == year, label + ": the reading remembers the year asked");
            check(!r.lines().isEmpty(), label + ": the reading is never empty");
            check(r.lines().get(0).equals("It is " + HereAndNow.yearText(year) + "."),
                    label + ": the first line is the year");
            for (String line : r.lines()) {
                check(!line.isBlank(), label + ": no blank line");
                check(!line.contains("\n"), label + ": one claim per line");
                check(!containsAny(line, new String[]{"null", "NaN", "Infinity"}),
                        label + ": no raw values leak out (" + line + ")");
            }
            check(r.shortLine().startsWith("It is "), label + ": the one-line form opens with the year");
            check(!r.shortLine().contains("\n"), label + ": the one-line form is one line");
            check(r.shortLine().length() <= 200, label + ": the one-line form stays short");

            // ---- determinism: the same question twice, the same page twice
            HereAndNow.Reading again = HereAndNow.read(lat, lon, year);
            check(again.lines().equals(r.lines()) && again.shortLine().equals(r.shortLine()),
                    label + ": the same question twice gives the same answer");
        }

        // ---- the empty places say "nobody" rather than inventing someone (or say the grid's thin
        // presence, marked as a modelled presence: the spawner reads the same grid, so the page and
        // the people in front of you must agree - turn 221, doubt 1)
        for (Object[] s : new Object[][]{
                {"Mid-Sahara 1000", 23.0, 10.0, 1000},
                {"Siberia 1000", 60.0, 100.0, 1000},
                {"Ohio valley 1200", 39.0, -84.0, 1200},
                {"Hyderabad outskirts 3000 BC (doubt 1)", 17.4346, 78.5016, -3000}}) {
            String label = (String) s[0];
            HereAndNow.Reading r = HereAndNow.read((Double) s[1], (Double) s[2], (Integer) s[3]);
            check(r.lines().get(1).startsWith("Nobody the data records lives near here")
                            || r.lines().get(1).startsWith("Nobody the record names lives near here"),
                    label + ": nobody, said as nobody");
            check(r.text().contains("population grid") || r.shortLine().contains("nobody the data records"),
                    label + ": the grid's presence is marked, or nobody stands");
            if (r.text().contains("population grid")) {
                check(r.text().contains("a modelled presence, not a measurement"),
                        label + ": a grid presence is marked as modelled");
            }
        }

        // ---- the settled places say somebody
        for (Object[] s : new Object[][]{
                {"Hyderabad 1500", 17.39, 78.49, 1500},
                {"Rome AD 100", 41.90, 12.50, 100},
                {"London 1700", 51.51, -0.13, 1700},
                {"Delhi 1650", 28.65, 77.23, 1650},
                {"Beijing 1500", 39.90, 116.40, 1500},
                {"Ur 2500 BC", 30.96, 46.10, -2500}}) {
            String label = (String) s[0];
            HereAndNow.Reading r = HereAndNow.read((Double) s[1], (Double) s[2], (Integer) s[3]);
            check(!r.lines().get(1).startsWith("Nobody the data records"),
                    label + ": somebody is here");
        }

        // ---- the year words
        check(HereAndNow.yearText(-2500).equals("2500 BC"), "2500 BC is written 2500 BC");
        check(HereAndNow.yearText(100).equals("AD 100"), "the year 100 is written AD 100");
        check(HereAndNow.yearText(1500).equals("1500"), "the year 1500 is written 1500");
        check(HereAndNow.yearText(3000).equals("3000"), "the year 3000 is written 3000");

        // ---- the AD 3000 guardrail: no projected people, and rulers only as a marked stretch
        HereAndNow.Reading future = HereAndNow.read(17.39, 78.49, 3000);
        for (String line : future.lines()) {
            check(!line.startsWith("About "), "3000: no projected population (" + line + ")");
            check(!line.startsWith("The town is growing"), "3000: no projected growth (" + line + ")");
        }
        String rulerLine = "";
        for (String line : future.lines()) {
            if (line.startsWith("The ruler the data names here is")
                    || line.startsWith("The register names no ruler")) {
                rulerLine = line;
            }
        }
        check(!rulerLine.isEmpty(), "3000: the ruler question is always answered");
        check(rulerLine.startsWith("The register names no ruler")
                        || rulerLine.contains("marks as an estimate"),
                "3000: any ruler named is marked as an estimate (" + rulerLine + ")");

        // ---- events: at most three lines, plus at most one "more" line
        int eventLines = 0;
        int moreLines = 0;
        for (String line : HereAndNow.read(17.39, 78.49, 1948).lines()) {
            if (line.startsWith("Near here the record names ") || line.startsWith("Also ")) {
                eventLines++;
            }
            if (line.startsWith("The record names ") && line.contains("more hereabouts")) {
                moreLines++;
            }
        }
        check(eventLines <= HereAndNow.MAX_EVENTS, "events: at most " + HereAndNow.MAX_EVENTS + " lines");
        check(moreLines <= 1, "events: at most one 'more' line");

        // ---- an estimate is always marked
        for (Object[] s : spots) {
            HereAndNow.Reading r = HereAndNow.read((Double) s[1], (Double) s[2], (Integer) s[3]);
            for (String line : r.lines()) {
                if (line.contains("countryside of")) {
                    check(line.contains("estimated"), (String) s[0] + ": countryside is marked estimated");
                }
                if (line.startsWith("The ruler the data names here is") && line.contains("estimate")) {
                    check(line.contains("marks as an estimate"), (String) s[0] + ": a marked answer says so");
                }
            }
        }

        // ---- the tidy pass: pack ids read as names ("golconda" -> "Golconda", "mohenjo_daro" -> "Mohenjo Daro")
        check(HereAndNow.read(41.90, 12.50, 100).lines().get(1).contains("You stand at Rome,"),
                "Rome AD 100: the place reads as Rome");
        check(HereAndNow.read(27.32, 68.14, -2500).lines().get(1).contains("You stand at Mohenjo Daro,"),
                "Mohenjo-daro 2500 BC: the place reads as Mohenjo Daro");
        check(!HereAndNow.read(17.39, 78.49, 1500).text().contains("golconda"),
                "Hyderabad 1500: no raw lower-case id in the page");
        for (Object[] s : spots) {
            HereAndNow.Reading r = HereAndNow.read((Double) s[1], (Double) s[2], (Integer) s[3]);
            check(!r.shortLine().contains("_"), (String) s[0] + ": no underscores in the one-line form");
        }

        System.out.println("HereProbe: " + checks + " checks, " + failed + " failed");
        if (failed > 0) {
            System.exit(1);
        }
        System.out.println("ALL " + checks + " HERE CHECKS PASSED");
    }
}
