/* Step 52 part 7: the chain, end to end. Each class passed its own probe; step 49 to 51 all taught that only
   a probe per chain proves the game. The chain: who a player is -> who may ask to move the world -> the world
   moving for everyone -> what a player carries, saved per timeline -> what a player owns, per timeline ->
   two players sharing or not sharing a world -> and the record underneath all of it, in its own place and
   year. */
import com.eternalengine.clock.Clocks;
import com.eternalengine.player.Permissions;
import com.eternalengine.player.Permissions.Action;
import com.eternalengine.player.Permissions.Actor;
import com.eternalengine.player.Permissions.Decision;
import com.eternalengine.player.Permissions.Vote;
import com.eternalengine.player.PocketSave;
import com.eternalengine.player.PocketSave.Key;
import com.eternalengine.player.PocketSave.Pocket;
import com.eternalengine.player.Property;
import com.eternalengine.player.Property.Kind;
import com.eternalengine.player.Together;
import com.eternalengine.player.Together.Player;
import com.eternalengine.player.WhoYouAre;

import java.io.InputStream;
import java.util.List;
import java.util.Map;
import java.util.zip.GZIPInputStream;

public class Step52ChainProbe {
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

    static InputStream gz(String n) throws Exception {
        return new GZIPInputStream(Step52ChainProbe.class.getResourceAsStream(
                "/data/eternalengine/eternal/history/" + n));
    }

    public static void main(String[] args) throws Exception {
        Actor sam = Actor.of("Sam", false);
        Actor ada = Actor.of("Ada", true);
        Actor mira = Actor.of("Mira", false);
        Actor rafi = Actor.of("Rafi", false);

        // ------------------------------------------------ 1. WHO THEY ARE (F10)
        WhoYouAre.Result samCard = WhoYouAre.make("Sam", WhoYouAre.Kind.LOCAL, 1830, 1857, "Delhi",
                List.of(new WhoYouAre.Entry("Fatima", "mother", 1, 1805, 1870),
                        new WhoYouAre.Entry("Daulat", "grandfather", 2, 1778, 1840)),
                List.of(new WhoYouAre.Item("a spade", 1)));
        ok(samCard.ok(), "Sam has a card: " + (samCard.ok() ? "" : samCard.refused()));
        WhoYouAre.Result miraCard = WhoYouAre.make("Mira", WhoYouAre.Kind.TRAVELLER, 2100, 1576, "Cuzco",
                List.of(), List.of(new WhoYouAre.Item("a notebook", 1)));
        ok(miraCard.ok(), "and so does Mira, who came from 2100");
        WhoYouAre samIs = samCard.who();
        WhoYouAre miraIs = miraCard.who();

        // The question step 53 will ask, asked honestly here: is Sam's grandfather alive in 1857?
        eq(samIs.ancestorsAliveAt(1857).size(), 1, "in 1857 one of Sam's line is alive: "
                + samIs.ancestorsAliveAt(1857).get(0).name());
        ok(!samIs.ancestorsAliveAt(1857).get(0).name().equals("Daulat"),
                "and it is not the grandfather: Daulat died in 1840");

        // ------------------------------------------------ 2. WHERE THEY STAND (A11)
        Clocks clocks = Clocks.empty();
        clocks.openWorld("delhi", 1857, "main");
        clocks.openWorld("cuzco", 1576, "main");
        clocks.join("Sam", "delhi");
        clocks.join("Rafi", "delhi");
        clocks.join("Mira", "cuzco");
        eq(clocks.standingOf("Sam").year(), 1857, "Sam stands in Delhi in 1857");
        eq(clocks.standingOf("Mira").year(), 1576, "and Mira in Cuzco in 1576, at the same moment");

        // ------------------------------------------------ 3. MOVING THE WORLD (A16 + A11)
        refused2(clocks.moveDate(sam, "delhi", 2026, null, "fast forward"), "takes their vote",
                "Delhi holds two people, so Sam alone may not move it");
        Vote.Opened asked = Permissions.Vote.open(Action.MOVE_WORLD_TIME, "delhi", sam, List.of("Sam", "Rafi"));
        ok(asked.ok(), "a vote of the people it moves opens");
        Vote vote = asked.vote();
        vote.cast(sam, true);
        vote.cast(rafi, true);
        ok(vote.close(sam).allowed(), "and passes with both their words");
        ok(clocks.moveDate(sam, "delhi", 2026, vote, "a hundred and sixty-nine years in one step").allowed(),
                "with the vote, the world moves");
        eq(clocks.standingOf("Sam").year(), 2026, "Sam is in 2026");
        eq(clocks.standingOf("Rafi").year(), 2026, "and Rafi too: a shared date moves everyone");
        eq(clocks.standingOf("Mira").year(), 1576, "and Mira's 1576 did not stir");
        refused2(clocks.jumpSelf(mira, "Mira", 2200), "one world has one date",
                "Mira still cannot have a private year");

        // ------------------------------------------------ 4. WHAT THEY CARRY, SAVED PER TIMELINE (A10)
        Key main = new Key("delhi", "main");
        Key b1 = new Key("delhi", "b1");
        Pocket dayOne = Pocket.of(
                Map.of("Fatima", "in Delhi, 1857"), Map.of("Sam", 20, "Rafi", 5),
                Map.of("Sam", List.of("the world moved to 2026 and I with it")));
        PocketSave save = PocketSave.empty().root(main, dayOne, "the real history");
        Pocket onBranch = dayOne.earn("Sam", 40).putPerson("Fatima", "in Delhi, 1861");
        save.branch(main, b1, onBranch, "the branch's own years");
        PocketSave.Restored got = save.chain(b1);
        ok(got.ok(), "the branch's pocket restores");
        eq(got.pocket().coinsOf("Sam"), 60, "Sam has 60 on the branch");
        eq(save.chain(main).pocket().coinsOf("Sam"), 20, "and 20 on the real history");
        eq(save.diff(b1, onBranch).size(), 0, "and the cheap save agrees with a full one");

        // ------------------------------------------------ 5. WHAT THEY OWN, PER TIMELINE (F4)
        Property onMain = new Property("delhi", "main");
        Property onB1 = new Property("delhi", "b1");
        ok(onMain.claim("sam-house", Kind.HOUSE, "Sam", 0, 64, 0, 6, 70, 6, 2026, "").ok(),
                "Sam's house, on the real history");
        ok(onB1.claim("sam-house", Kind.HOUSE, "Mira", 0, 64, 0, 6, 70, 6, 1861, "").ok(),
                "the same blocks, on the branch, are Mira's: lawfully");
        eq(onMain.at(3, 67, 3).owner(), "Sam", "one book, one answer");
        eq(onB1.at(3, 67, 3).owner(), "Mira", "and the other book, the other");

        // ------------------------------------------------ 6. SHARED OR SEPARATE (F7)
        Player samNow = new Player("Sam", "delhi", clocks.branchOf("delhi"), clocks.standingOf("Sam").year(),
                Permissions.Rank.PLAYER, "a resident of Delhi");
        Player rafiNow = new Player("Rafi", "delhi", clocks.branchOf("delhi"), clocks.standingOf("Rafi").year(),
                Permissions.Rank.PLAYER, "a scribe");
        Player miraNow = new Player("Mira", "cuzco", "main", 1576, Permissions.Rank.PLAYER, "a traveller");
        ok(Together.share(samNow, rafiNow).share(), "Sam and Rafi share a world");
        ok(!Together.share(samNow, miraNow).share(), "Sam and Mira do not");
        System.out.println("     " + Together.share(samNow, miraNow).line());
        System.out.println("     " + Together.share(samNow, rafiNow).line());
        eq(Together.rollCall(List.of(samNow, rafiNow, miraNow), "delhi").size(), 2,
                "a vote about Delhi is Delhi's people to make");
        eq(Together.rollCall(List.of(samNow, rafiNow, miraNow), "cuzco").size(), 1,
                "and a vote about Cuzco is Mira's alone");

        // ------------------------------------------------ 7. WHO MAY CHANGE HISTORY: BOTH AXES
        Decision inWorldYes = Decision.yes("her standing allows it");
        Decision inWorldNo = Decision.no("a sharecropper cannot start a war");
        Decision serverYes = Permissions.mayAlone(sam, Action.CLAIM_PROPERTY, 1);
        Decision serverNo = Permissions.mayAlone(sam, Action.RESTORE_BACKUP, 1);
        ok(Together.mayChangeHistory(samNow, inWorldYes, serverYes).allowed(),
                "both axes yes means yes");
        refused2(Together.mayChangeHistory(samNow, inWorldYes, serverNo), "the server says no",
                "the server axis can say no alone");
        refused2(Together.mayChangeHistory(samNow, inWorldNo, serverYes), "the world says no",
                "and so can the world axis");
        refused2(Together.mayChangeHistory(samNow, inWorldNo, serverNo), "the world says no",
                "and when both say no, both are named");
        ok(Together.mayChangeHistory(samNow, inWorldNo, serverNo).why().contains("the server says no"),
                "both of them: " + Together.mayChangeHistory(samNow, inWorldNo, serverNo).why());
        refused2(Together.mayChangeHistory(samNow, inWorldYes, null), "one axis unanswered",
                "and one axis alone is not an answer");

        // ------------------------------------------------ 8. TWO HANDS ON ONE THING
        Together world = Together.empty();
        ok(world.touch(sam, "delhi", "main", "the gate at (0,64,0)", 2026, "mending it").allowed(),
                "Sam takes the gate");
        refused2(world.touch(rafi, "delhi", "main", "the gate at (0,64,0)", 2026, "painting it"),
                "Sam is already on", "and Rafi is refused, by name");
        ok(world.touch(rafi, "delhi", "b1", "the gate at (0,64,0)", 1861, "painting it").allowed(),
                "on another timeline the same gate is free");
        ok(world.touch(mira, "cuzco", "main", "the gate at (0,64,0)", 1576, "building it").allowed(),
                "and in another world too");
        eq(world.live().size(), 3, "three hands, three worlds, no conflict");
        refused2(world.settle(rafi, "delhi", "main", "the gate at (0,64,0)"), "Sam is on",
                "only the one who touched it, or an operator, may settle");
        refused2(world.force(rafi, "delhi", "main", "the gate at (0,64,0)", "I want to"), "cannot force",
                "a player cannot force");
        refused2(world.force(ada, "delhi", "main", "the gate at (0,64,0)", ""), "must say why",
                "and a force must say why");
        ok(world.force(ada, "delhi", "main", "the gate at (0,64,0)", "Rafi is the city's mason").allowed(),
                "an operator can force, with a reason");
        eq(world.live().size(), 2, "and the hand is lifted");

        // ------------------------------------------------ 9. THE RECORD, IN ITS OWN PLACE AND YEAR
        try (InputStream towns = gz("towns.json.gz"); InputStream bld = gz("buildings_famous.json.gz");
             InputStream works = gz("ways_works.json.gz")) {
            com.eternalengine.story.PlaceRecord rec =
                    com.eternalengine.story.PlaceRecord.load(towns, bld, works);
            com.eternalengine.story.PlaceRecord.Town delhi = rec.nearest(28.61, 77.21);
            ok(delhi.nameNow().contains("Delhi"), "the record holds the place they stand in: "
                    + delhi.nameNow());
            List<com.eternalengine.story.BranchStory.Fact> facts = rec.facts(delhi, 25, 1857);
            ok(facts.size() > 3, "and rows of it by 1857: " + facts.size());
            boolean redFort = false;
            for (com.eternalengine.story.BranchStory.Fact f : facts) {
                if (f.name().toLowerCase(java.util.Locale.ROOT).contains("red fort")) {
                    redFort = true;
                }
            }
            ok(redFort, "the Red Fort is in the record for Delhi by 1857");
        }

        // ------------------------------------------------ 10. THE PAGE
        for (String line : Together.page(List.of(samNow, rafiNow, miraNow))) {
            System.out.println("     " + line);
        }
        System.out.println("     " + Together.ruleLine());
        ok(Together.ruleLine().contains("both axes"), "the rule line keeps both axes");

        System.out.println("\nStep 52 part 7: " + checks + " checks, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }

    static void refused2(Decision d, String words, String what) {
        checks++;
        if (d.allowed()) {
            failed++;
            System.out.println("  FAIL " + what + "  (it was allowed)");
            return;
        }
        if (d.why().contains(words)) return;
        failed++;
        System.out.println("  FAIL " + what + "  no reason says \"" + words + "\"; got " + d.why());
    }
}
