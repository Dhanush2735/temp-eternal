/* The chronicler: the years after 2026 are unwritten, not empty.
   The claim: a world that has been run makes OBSERVED facts, and after the seam the chronicle is the
   only authority there is. */
import com.eternalengine.clock.Timeline;
import com.eternalengine.timeline.Chronicler;
import com.eternalengine.timeline.Provenance;

import java.util.List;

public class Step47ChroniclerProbe {
    static int checks = 0, failed = 0;
    static void ok(boolean c, String what) {
        checks++;
        if (!c) { failed++; System.out.println("  FAIL " + what); }
    }
    static void eq(Object a, Object b, String what) {
        checks++;
        if (a == null ? b != null : !a.equals(b)) {
            failed++; System.out.println("  FAIL " + what + "  expected=" + b + " actual=" + a);
        }
    }

    static Chronicler.Change c(int year, Chronicler.Kind k, String subject, String place, int mag,
                               Provenance p) {
        return new Chronicler.Change(year, k, subject, place, mag, p);
    }

    public static void main(String[] args) {
        Chronicler ch = new Chronicler();
        System.out.println("  " + ch.seamLine());

        // ------------------------------------------------ 1. THE SEAM RULE, BOTH WAYS
        // Before 2026 the packs are the authority: a road built in 1240 is already in them.
        ok(ch.report(c(1240, Chronicler.Kind.ROAD, "road", "Deccan", 5000,
                Provenance.OBSERVED)) == null,
                "a road observed in 1240 is REFUSED: the packs already say what happened in 1240, "
                        + "and duplicating them could contradict them");
        eq(ch.size(), 0, "so the chronicle is still empty");
        // but a divergence is the one thing the packs cannot know
        Chronicler.Line div = ch.report(c(1240, Chronicler.Kind.WAR, "the battle", "Deccan", 1,
                Provenance.AUTHORED));
        ok(div != null, "while a divergence in 1240 IS recorded, because the packs cannot know it");
        ok(!div.beyondShipped(), "and it is marked as being inside the recorded years");

        // after the seam the chronicle is the only authority, so observation is enough
        Chronicler.Line rail = ch.report(c(2381, Chronicler.Kind.ROAD, "the railway", "Deccan",
                400000, Provenance.OBSERVED));
        ok(rail != null, "a railway built in 2381 is recorded");
        ok(rail.beyondShipped(), "and is marked as past the shipped record");
        eq(rail.provenance(), Provenance.OBSERVED, "with OBSERVED, because it is there to see");

        // ------------------------------------------------ 2. NOT EVERYTHING IS HISTORY
        ok(ch.report(c(2382, Chronicler.Kind.BUILDING, "a wall", "Deccan", 0,
                Provenance.OBSERVED)) == null, "a wall with magnitude zero is not history");
        ok(ch.report(c(2382, Chronicler.Kind.SETTLEMENT, "hamlet", "Deccan", 24,
                Provenance.OBSERVED)) == null, "twenty-four people is a hamlet and not a settlement");
        ok(ch.report(c(2382, Chronicler.Kind.SETTLEMENT, "village", "Deccan", 25,
                Provenance.OBSERVED)) != null, "twenty-five is");
        eq(Chronicler.Kind.SETTLEMENT.threshold(), 25, "and the threshold is where it says it is");
        ok(ch.report(c(2382, Chronicler.Kind.ROAD, "a path", "Deccan", 999,
                Provenance.OBSERVED)) == null, "999 metres of path is not a road");
        ok(ch.report(c(2382, Chronicler.Kind.TECHNOLOGY, "the telegraph", "Deccan", 99,
                Provenance.OBSERVED)) == null, "nine per cent of towns is below the technology line");
        ok(ch.report(c(2382, Chronicler.Kind.TECHNOLOGY, "the telegraph", "Deccan", 100,
                Provenance.OBSERVED)) != null, "ten per cent is a technology arriving");

        // ------------------------------------------------ 3. A PROCESS IS ONE LINE
        Chronicler ch2 = new Chronicler();
        Chronicler.Line first = ch2.report(c(2400, Chronicler.Kind.ROAD, "the canal", "Malwa",
                5000, Provenance.OBSERVED));
        for (int y = 2401; y <= 2409; y++) {
            ch2.report(c(y, Chronicler.Kind.ROAD, "the canal", "Malwa", 5000,
                    Provenance.OBSERVED));
        }
        eq(ch2.size(), 1, "ten years of building a canal is ONE line, not ten");
        eq(ch2.lines().get(0).untilYear(), 2409, "and the line now runs to 2409");
        ok(ch2.lines().get(0).spansYears(), "and says that it spans years");
        eq(ch2.lines().get(0).years(), "2400 to 2409", "in words: "
                + ch2.lines().get(0).years());
        ok(first != null && ch2.lines().get(0).year() == 2400, "starting where it started");

        // a process more than fifty years later is a different thing, not the same line
        ch2.report(c(2500, Chronicler.Kind.ROAD, "the canal", "Malwa", 5000, Provenance.OBSERVED));
        eq(ch2.size(), 2, "half a century later the same subject is a second line: " + ch2.size());

        // ------------------------------------------------ 4. A YEAR HAS ROOM FOR SO MUCH
        Chronicler busy = new Chronicler();
        for (int i = 0; i < 8; i++) {
            busy.report(c(2450, Chronicler.Kind.BUILDING, "tower " + i, "Dhaka", 1,
                    Provenance.OBSERVED));
        }
        eq(busy.size(), Chronicler.PER_YEAR, "a single year holds at most "
                + Chronicler.PER_YEAR + " lines, so a busy world stays readable");

        // ------------------------------------------------ 5. PROVENANCE IS NOT OPTIONAL
        ok(ch.report(c(2390, Chronicler.Kind.WAR, "a skirmish", "Konkan", 1, null)) != null,
                "a change with no provenance is recorded as OBSERVED");
        eq(ch.lines().get(ch.size() - 1).provenance(), Provenance.OBSERVED,
                "which is the default, and it is a real answer rather than a blank");
        ok(ch.report(c(2391, Chronicler.Kind.WAR, "a rumour", "Konkan", 1,
                Provenance.MODELLED)) == null,
                "but a MODELLED line after the seam is refused: a model is what we do when nothing "
                        + "happened, and this class is for things that did");
        Chronicler.Line named = ch.report(c(2392, Chronicler.Kind.NAMING, "Port Meera", "Konkan", 1,
                Provenance.AUTHORED));
        ok(named != null, "a name somebody gave is AUTHORED");
        ok(named.title().contains("Port Meera"), "and the line keeps the name: " + named.title());
        ok(named.body().contains("put their name"), "the body says who is asserting it: "
                + named.body());

        // ------------------------------------------------ 6. THE SEAM SENTENCE
        ok(ch.beyondSeam() >= 3, "the chronicle counts what it has written past the seam: "
                + ch.beyondSeam());
        ok(ch.seamLine().contains("only history there is"), "and says it is the only history: "
                + ch.seamLine());
        Chronicler empty = new Chronicler();
        ok(empty.seamLine().contains("unwritten, not empty"), "an empty world says the years past "
                + "the record are unwritten rather than empty: " + empty.seamLine());

        // ------------------------------------------------ 7. IT CONVERTS PROJECTED YEARS INTO RECORDED ONES
        // This is the point of the whole proposal: 2400 is a projected year in the shipped data and
        // a RECORDED year in a world that has been run.
        ok(Timeline.projected(2381), "2381 is a projected year in the shipped data");
        ok(rail.beyondShipped(), "and the railway line knows it is past the shipped record");
        eq(rail.provenance(), Provenance.OBSERVED, "yet the railway is not projected at all: it is "
                + "observed in this world, which is the difference between shipped knowledge and "
                + "lived history");

        // ------------------------------------------------ 8. READING IT BACK
        ok(ch.upTo(1240).size() == 1, "reading up to a year gives the lines that had finished by "
                + "then: " + ch.upTo(1240).size());
        ok(ch.upTo(2381).size() > ch.upTo(1240).size(), "and more by 2381");
        ok(ch.perCentury() > 0, "the rate is a number and not NaN: " + ch.perCentury());
        ch.clear();
        ok(ch.isEmpty(), "and it can be cleared, which is what a branch needs on a reload");

        System.out.println("  " + rail.title() + " - " + rail.body());
        System.out.println(failed == 0
                ? "Step47ChroniclerProbe: " + checks + " checks, 0 failed"
                : "Step47ChroniclerProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
