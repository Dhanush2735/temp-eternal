/* Step 47 part 6 (C15): music and the arts, the last part of "culture".
   The claim: there is no year a place got music, so the register is of the things that carry it, and
   every art form is older than the means of copying it. */
import com.eternalengine.culture.Arts;
import com.eternalengine.culture.Games;

import java.util.List;

public class Step47ArtsProbe {
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

    public static void main(String[] args) {
        Arts a = Arts.get();
        System.out.println("  " + a.summary());

        // ------------------------------------------------ 1. THE REGISTER LOADS
        ok(a.count() >= 12, "the register carries the instruments and media: " + a.count());
        eq(a.areas().size(), 17, "over the mod's 17 areas");
        for (String id : List.of("song", "drum", "organ", "piano", "woodblock_print",
                "oil_painting", "photography", "phonograph")) {
            ok(a.work(id) != null, "and carries " + id);
        }

        // ------------------------------------------------ 2. EVERYBODY SINGS
        for (String area : a.areas()) {
            ok(a.work("song").recordedIn(area, -3000), "somebody sings in " + area + " in 3000 BC");
        }
        ok(a.work("song").universal(), "song is universal and the register says so");
        ok(a.work("drum").recordedIn("WAF", -3000), "and West Africa has a drum in 3000 BC");
        ok(a.work("dance").recordedIn("AUS", -3000), "and Australia has dance");
        ok(a.work("flute").year() == -3000, "with the flute carried from the first year, because a "
                + "hollow bone with holes is available to anybody who finds one");

        // ------------------------------------------------ 3. THE INSTRUMENTS HAVE AN ORDER
        ok(a.work("harp").recordedIn("WAS", -3000), "a harp in Mesopotamia in 3000 BC");
        ok(!a.work("organ").recordedIn("EUR", 700), "and no organ in Europe in 700");
        eq(a.work("organ").since("EUR"), 800, "the organ reaches Europe after 757");
        ok(a.work("piano").year() > 1700, "the piano is 1709 and not before");
        ok(!a.work("piano").recordedIn("WAF", 1800), "and it is not in West Africa in 1800: "
                + a.work("piano").since("WAF"));
        ok(a.work("bowed_strings").since("CAS") == 800, "the bow is Central Asian and 800");
        ok(a.work("bowed_strings").since("EUR") >= 1000, "and reaches Europe later");

        // ------------------------------------------------ 4. THE FINDING: COPYING COMES LATE
        ok(a.work("oil_painting").year() < a.work("photography").year(),
                "photography comes after the oil painting it replaces as a record of a face");
        ok(a.work("woodblock_print").year() < a.work("photography").year(),
                "and after the woodblock, which is the first way to make a picture many times");
        ok(a.work("phonograph").year() > a.work("organ").year(),
                "the recording comes after every instrument it records");
        ok(a.work("woodblock_print").year() == 700, "the woodblock is Chinese and 700");
        eq(a.work("photography").since("EUR"), 1839, "photography is 1839");
        eq(a.work("phonograph").since("NNA"), 1877, "and the phonograph is 1877 in New Jersey");
        ok(a.work("phonograph").note().contains("separated from the performer"),
                "the note says what it means: a performance separated from the performer for the "
                + "first time");
        eq(a.work("photography").since("WAF"), 1860, "while a photograph reaches West Africa only "
                + "in 1860");

        // ------------------------------------------------ 5. THE CROSS-CHECK WITH E17
        // Photography must precede the cinema, and the two registers are separate: this is the
        // check that keeps them agreeing.
        Games g = Games.get();
        ok(a.work("photography").year() < g.game("cinema").year(),
                "photography (" + a.work("photography").year() + ") precedes the cinema ("
                        + g.game("cinema").year() + "), which is the one claim the two registers "
                        + "share");
        ok(a.work("theatre_masks").year() < g.game("theatre").year()
                        || a.work("theatre_masks").year() == -3000,
                "and the mask is older than the theatre it makes possible");

        // ------------------------------------------------ 6. AN UNKNOWN IS NOT A NEVER
        eq(a.work("piano").since("PAC"), 1900, "the piano in Polynesia has a year");
        ok(a.why("song", "EUR", 0).contains("since"), "the sentence for a player: "
                + a.why("song", "EUR", 0));
        ok(a.why("phonograph", "EUR", 1800).contains("not in"), "and before it arrives: "
                + a.why("phonograph", "EUR", 1800));

        // ------------------------------------------------ 7. WHAT A PLACE HAS
        List<String> europe1400 = a.availableIn("EUR", 1400);
        ok(europe1400.contains("organ"), "Europe in 1400 has an organ: " + europe1400);
        ok(!europe1400.contains("oil_painting"), "and no oil paint, which is 1420: the gap is the "
                + "point, because the medium is twenty years later than the century");
        ok(a.availableIn("EUR", 1450).contains("oil_painting"), "and there is in 1450");
        ok(!europe1400.contains("photography") && !europe1400.contains("piano"),
                "with no piano and no photograph either, both being centuries away");
        System.out.println("  Europe 1400: " + europe1400);

        // ------------------------------------------------ 8. NOBODY IS PUNISHED
        for (Arts.Work w : a.works()) {
            ok(!w.note().toLowerCase().contains("penalty"), "no note mentions a penalty: " + w.id());
        }
        ok(!a.why("piano", "WAF", 1800).toLowerCase().contains("banned"), "and no absence is a ban: "
                + a.why("piano", "WAF", 1800));

        System.out.println(failed == 0
                ? "Step47ArtsProbe: " + checks + " checks, 0 failed"
                : "Step47ArtsProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
