/* Step 47 part 6 (E17): games and sports.
   The claim: board games travel with merchants and codified sports are all astonishingly late, and
   this register refuses to invent an arrival where the record gives none. */
import com.eternalengine.culture.Games;

import java.util.List;

public class Step47GamesProbe {
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
        Games g = Games.get();
        System.out.println("  " + g.summary());

        // ------------------------------------------------ 1. THE PLAN'S SIX ARE ALL HERE
        for (String id : List.of("chess", "polo", "cricket", "kites", "theatre", "cinema")) {
            ok(g.game(id) != null, "the plan names " + id + " and the register carries it");
        }
        eq(g.areas().size(), 17, "over the mod's 17 areas");
        ok(g.count() >= 18, "and a dozen more besides: " + g.count());

        // ------------------------------------------------ 2. BOARD GAMES TRAVEL
        eq(g.game("chess").since("SAS"), 600, "chess is Indian and dated 600");
        ok(g.game("chess").since("EUR") >= 1000, "and it is not in Europe before 1000: "
                + g.game("chess").since("EUR"));
        ok(!g.game("chess").recordedIn("EUR", 800), "no chess in Europe in 800");
        ok(g.game("chess").recordedIn("EUR", 1200), "and there is in 1200");
        eq(g.game("backgammon").since("WAS"), -3000, "the tables are Mesopotamian and 3000 BC");
        eq(g.game("playing_cards").since("EUR"), 1370, "and cards reach Europe in 1370");

        // ------------------------------------------------ 3. THE CODIFIED SPORTS ARE LATE
        ok(g.game("football").year() > 1800, "football has a RULE only after 1800: "
                + g.game("football").year());
        ok(g.game("basketball").year() > 1800, "basketball is 1891");
        ok(g.game("olympic_games").year() < -700 && g.game("cinema").year() > 1800,
                "and the two things called 'Olympic' and 'cinema' are two thousand years apart");
        ok(!g.game("football").recordedIn("SAM", 1800), "no codified football in South America in "
                + "1800");
        ok(g.game("football").recordedIn("SAM", 1900), "and there is by 1900");
        ok(g.game("go").year() < -400, "while go is 500 BC and still played by the same rules");

        // ------------------------------------------------ 4. THE SPECTACLE IS NOT A SPORT
        ok(g.game("gladiator").spectacle(), "the gladiator is watched and not played");
        ok(g.game("mesoamerican_ball").year() < g.game("football").year(),
                "the ball game of Mesoamerica is the oldest ball game in the register");
        ok(!g.game("mesoamerican_ball").recordedIn("EUR", 1500), "and it never reaches Europe");
        ok(g.game("gladiator").spread().size() <= 4, "the gladiator never leaves the Roman world: "
                + g.game("gladiator").spread().keySet());
        ok(g.game("theatre").year() == -534, "the theatre is 534 BC Athens");

        // ------------------------------------------------ 5. THE REFUSAL: UNKNOWN IS NOT NEVER
        eq(g.game("kabaddi").since("SAM"), Games.UNKNOWN, "kabaddi in South America is UNKNOWN");
        ok(!g.game("kabaddi").recordedIn("SAM", 2000), "and an unknown is never a yes, even in 2000");
        ok(g.why("kabaddi", "SAM", 2000).contains("does not record"),
                "the sentence says so in words: " + g.why("kabaddi", "SAM", 2000));
        ok(g.why("kabaddi", "SAS", 2000).contains("since -500") || g.why("kabaddi", "SAS", 2000)
                .contains("since -500"), "and in its home it has a date: "
                + g.why("kabaddi", "SAS", 2000));
        int sparse = 0;
        for (Games.Game x : g.games()) if (x.spread().size() < 9) sparse++;
        ok(sparse >= 3, "several games are unrecorded across most of the world, which is the "
                + "refusal showing in the data: " + sparse);

        // ------------------------------------------------ 6. EQUIPMENT FINDS THE GAME
        eq(g.forEquipment("chess").id(), "chess", "an item finds its game where there is one");
        eq(g.forEquipment("kites").id(), "kites", "kites too");
        eq(g.forEquipment("playing_cards").id(), "playing_cards", "and cards");
        ok(g.game("go").equipment() == null, "and go has no item, which the register records rather "
                + "than inventing one");

        // ------------------------------------------------ 7. WHAT A PLACE HAS TO PLAY WITH
        List<String> europe1400 = g.playableIn("EUR", 1400);
        ok(europe1400.contains("chess"), "Europe in 1400 has chess: " + europe1400);
        ok(europe1400.contains("playing_cards"), "and cards");
        ok(!europe1400.contains("football"), "and no codified football, because there is no such "
                + "thing in 1400");
        ok(europe1400.contains("theatre"), "and a theatre");
        System.out.println("  Europe 1400: " + europe1400);

        // ------------------------------------------------ 8. NOBODY IS PUNISHED
        ok(!g.why("gladiator", "SAS", -200).toLowerCase().contains("penalty"),
                "an unavailable game is a fact about a place and not a rule about a player: "
                + g.why("gladiator", "SAS", -200));

        System.out.println(failed == 0
                ? "Step47GamesProbe: " + checks + " checks, 0 failed"
                : "Step47GamesProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
