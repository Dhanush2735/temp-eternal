/* Step 48 part 3 (F1, priced and gated): who can do what, in a real place.
   The claim: whether a way to change history is open depends on five things that the packs already
   know - how many people are within reach, who the player is among them, how many follow, whether
   there is a workshop, and what is in the purse - and not on the player's good intentions. */
import com.eternalengine.timeline.Agency;
import com.eternalengine.timeline.ChangeRecord;

import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.zip.GZIPInputStream;

public class Step48AgencyProbe {
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

    /** One town from the pack, only the three things this probe needs. */
    record Town(String name, double lat, double lon, int[] pops) {}

    /** Read towns.json.gz. The pack holds 30,151 towns as arrays; this keeps the name and counts. */
    static List<Town> loadTowns() {
        List<Town> out = new ArrayList<>();
        try (InputStream in = Step48AgencyProbe.class.getResourceAsStream(
                "/data/eternalengine/eternal/history/towns.json.gz")) {
            if (in == null) return out;
            JsonReader r = new JsonReader(new InputStreamReader(new GZIPInputStream(in),
                    StandardCharsets.UTF_8));
            r.beginObject();
            while (r.hasNext()) {
                if (!"towns".equals(r.nextName())) { r.skipValue(); continue; }
                r.beginArray();
                while (r.hasNext()) {
                    r.beginArray();
                    r.skipValue();                                   // qid
                    String name = r.nextString();                    // name
                    double lat = r.nextInt() / 1000.0;               // lat * 1000
                    double lon = r.nextInt() / 1000.0;
                    r.skipValue();                                   // flags
                    r.skipValue();                                   // founded
                    r.skipValue();                                   // precision
                    r.skipValue();                                   // names
                    List<Integer> pops = new ArrayList<>();
                    r.beginArray();                                  // pops: year, people, ...
                    while (r.hasNext()) pops.add(r.nextInt());
                    r.endArray();
                    r.skipValue();                                   // divs
                    r.skipValue();                                   // head
                    // The pack carries a twelfth field, the names travellers use, which
                    // build_towns.py's own header does not list. The first run of this probe
                    // stopped at town 131 because of it, so it is named here rather than skipped
                    // blindly a fourth time.
                    if (r.hasNext()) r.skipValue();                  // also
                    r.endArray();
                    int[] p = new int[pops.size()];
                    for (int k = 0; k < p.length; k++) p[k] = pops.get(k);
                    out.add(new Town(name, lat, lon, p));
                }
                r.endArray();
            }
            r.endObject();
        } catch (Exception e) {
            System.out.println("  towns pack error: " + e);
        }
        return out;
    }

    static Town nearestTown(List<Town> towns, double lat, double lon) {
        Town best = null;
        double bestD = Double.MAX_VALUE;
        for (Town t : towns) {
            double d = (t.lat() - lat) * (t.lat() - lat) + (t.lon() - lon) * (t.lon() - lon);
            if (d < bestD) { bestD = d; best = t; }
        }
        return best;
    }

    /**
     * People in a town in a year, straight line between two counts, and nothing more than fifteen
     * years past the last count. This mirrors TownFacts.peopleIn deliberately: the point is to feed
     * Agency the same number the game would show, not a different one.
     */
    static long peopleIn(Town t, int year) {
        int[] p = t.pops();
        if (p.length == 0 || year < p[0]) return -1;
        int last = p.length - 2;
        if (year >= p[last]) return year - p[last] <= 15 ? p[last + 1] : -1;
        for (int k = 0; k < last; k += 2) {
            int y0 = p[k], y1 = p[k + 2];
            if (y0 <= year && year < y1) {
                if (y1 - y0 > 100) {
                    if (year - y0 <= 15) return p[k + 1];
                    return y1 - year <= 15 ? p[k + 3] : -1;
                }
                double f = (year - y0) / (double) (y1 - y0);
                return Math.round(p[k + 1] + f * (p[k + 3] - p[k + 1]));
            }
        }
        return -1;
    }

    /**
     * The town the pack can COUNT in that year, near this point: the largest count within about a
     * degree, and the nearest town only if no count exists there. Nearest alone is wrong, and the
     * first run showed why: the nearest record to Tenochtitlan is "Greater Mexico City", a modern
     * metro area with no figure for 1500, so the probe read an empty city where the pack has 212,500
     * people at the old site.
     */
    static Town townWithPeople(List<Town> towns, double lat, double lon, int year) {
        Town best = null;
        long bestPeople = -1;
        Town nearest = null;
        double bestD = Double.MAX_VALUE;
        for (Town t : towns) {
            double dLat = t.lat() - lat;
            double dLon = t.lon() - lon;
            double d = dLat * dLat + dLon * dLon;
            if (d < bestD) { bestD = d; nearest = t; }
            if (d > 1.0) continue;
            long p = peopleIn(t, year);
            if (p > bestPeople) { bestPeople = p; best = t; }
        }
        return bestPeople > 0 ? best : nearest;
    }

    static long peopleAt(List<Town> towns, double lat, double lon, int year, String label) {
        Town t = townWithPeople(towns, lat, lon, year);
        ok(t != null, "the pack knows a town near " + label);
        if (t == null) return -1;
        long people = peopleIn(t, year);
        System.out.println("     " + label + " " + year + ": " + t.name() + ", " + people + " people");
        return people;
    }

    public static void main(String[] args) {
        // ------------------------------------------------ 1. THE SITUATION IS SMALL ON PURPOSE
        Agency.Situation village = Agency.Situation.newcomer(1200, "a village", 200);
        eq(village.place(), "a village", "a situation names its place");
        eq(Agency.Situation.newcomer(1200, "", 0).place(), "here",
                "and says 'here' rather than nothing when it has no name");

        // ------------------------------------------------ 2. A STRANGER IN A VILLAGE OF 200
        List<ChangeRecord.Way> strangerOpen = Agency.open(village);
        // The three things one person can always do, and the two that need a place with people in it.
        ok(strangerOpen.contains(ChangeRecord.Way.KILL_OR_SAVE_A_PERSON),
                "one person can always kill or save another: " + strangerOpen);
        ok(strangerOpen.contains(ChangeRecord.Way.TELL_PEOPLE_THE_FUTURE),
                "and can always tell somebody what is coming");
        eq(Agency.judge(ChangeRecord.Way.MARRY, village).answer(), Agency.Answer.NEEDS,
                "and can marry once they are known, not on the day they arrive: "
                        + Agency.judge(ChangeRecord.Way.MARRY, village).words());
        Agency.Situation residentMarried = new Agency.Situation(1200, "a village", 200,
                Agency.Standing.RESIDENT, 0, false, 0);
        ok(Agency.open(residentMarried).contains(ChangeRecord.Way.MARRY),
                "a resident can, because a marriage needs two people and there are two");
        ok(!strangerOpen.contains(ChangeRecord.Way.FOUND_A_TOWN),
                "a stranger cannot found a town: it wants twenty people who will stay and they are "
                        + "not following a stranger");
        ok(!strangerOpen.contains(ChangeRecord.Way.TRADE_OR_SABOTAGE_GOODS),
                "and cannot move goods, having no purse: "
                        + Agency.judge(ChangeRecord.Way.TRADE_OR_SABOTAGE_GOODS, village).words());
        ok(!strangerOpen.contains(ChangeRecord.Way.START_OR_ESCALATE_A_WAR),
                "and certainly cannot start a war");

        // The reason a war is impossible is arithmetic, not permission: two hundred people are not
        // two sides.
        Agency.Verdict war = Agency.judge(ChangeRecord.Way.START_OR_ESCALATE_A_WAR, village);
        eq(war.answer(), Agency.Answer.NO, "a war in a village of 200 is a no, not a not-yet");
        ok(war.because().contains("1000"), "and the reason is the count: " + war.because());

        // A crown is different: in a village it is still arithmetic, in a city it is a matter of
        // standing. Those two refusals mean different things to a player and must not read alike.
        Agency.Situation city = Agency.Situation.newcomer(1600, "a city", 50_000);
        eq(Agency.judge(ChangeRecord.Way.TAKE_THE_CROWN, city).answer(), Agency.Answer.NEEDS,
                "in a city, a crown is within reach and not yet held: "
                        + Agency.judge(ChangeRecord.Way.TAKE_THE_CROWN, city).words());
        ok(Agency.judge(ChangeRecord.Way.TAKE_THE_CROWN, city).because().contains("stranger"),
                "and it says what is missing, which is standing");

        // ------------------------------------------------ 3. CLIMBING
        Agency.Situation resident = new Agency.Situation(1600, "a city", 50_000,
                Agency.Standing.RESIDENT, 0, false, 2);
        Agency.Situation notable = new Agency.Situation(1600, "a city", 50_000,
                Agency.Standing.NOTABLE, 60, false, 100);
        Agency.Situation officer = new Agency.Situation(1600, "a city", 50_000,
                Agency.Standing.OFFICE, 120, false, 500);
        ok(Agency.open(resident).size() > Agency.open(city).size(),
                "a resident can do more than a stranger: " + Agency.open(resident).size()
                        + " against " + Agency.open(city).size());
        ok(Agency.open(notable).contains(ChangeRecord.Way.START_OR_ESCALATE_A_WAR),
                "a notable with sixty behind them can start a war");
        ok(!Agency.open(resident).contains(ChangeRecord.Way.START_OR_ESCALATE_A_WAR),
                "a resident with none cannot");
        ok(Agency.open(officer).contains(ChangeRecord.Way.TAKE_THE_CROWN),
                "and an officer with a hundred and twenty behind them can take a crown");
        ok(Agency.open(officer).contains(ChangeRecord.Way.FOUND_A_TOWN), "and can found a town");
        ok(!Agency.open(officer).contains(ChangeRecord.Way.BRING_AN_INVENTION_EARLY),
                "but cannot bring an invention early without a workshop: "
                        + Agency.judge(ChangeRecord.Way.BRING_AN_INVENTION_EARLY, officer).words());
        Agency.Situation master = new Agency.Situation(1600, "a city", 50_000,
                Agency.Standing.OFFICE, 120, true, 500);
        ok(Agency.open(master).contains(ChangeRecord.Way.BRING_AN_INVENTION_EARLY),
                "with one, they can");
        eq(Agency.open(officer).size() + 1, Agency.open(master).size(),
                "and the workshop opens exactly one more way, which is the point of a workshop");

        // ------------------------------------------------ 4. THE ORDER OF OPENNESS
        // A village, a town, a city, a capital: the count decides more than anything else.
        Agency.Situation[] ladder = {
                Agency.Situation.newcomer(1200, "a hamlet", 80),
                Agency.Situation.newcomer(1200, "a village", 200),
                Agency.Situation.newcomer(1200, "a town", 5_000),
                Agency.Situation.newcomer(1200, "a city", 50_000),
        };
        int last = -1;
        for (Agency.Situation s : ladder) {
            int open = Agency.open(s).size();
            ok(open >= last, "a bigger place opens at least as much as a smaller one: "
                    + s.place() + " " + open + " against " + last);
            last = open;
        }
        ok(Agency.open(ladder[0]).size() <= 3,
                "in a hamlet of eighty there is almost nothing to do: " + Agency.open(ladder[0]).size());
        ok(Agency.impossible(ladder[0]).size() >= 4,
                "and most of the board is impossible rather than pending: "
                        + Agency.impossible(ladder[0]));
        eq(Agency.open(ladder[0]).size() + Agency.withinReach(ladder[0]).size()
                + Agency.impossible(ladder[0]).size(), ChangeRecord.Way.values().length,
                "every way is open, pending or impossible, with none unaccounted for");

        // Cheapest first, which is the honest order for a player who has just arrived.
        List<ChangeRecord.Way> cheap = Agency.cheapest(officer);
        ok(!cheap.isEmpty() && cheap.get(0).cost() <= cheap.get(cheap.size() - 1).cost(),
                "the open ways sort by what they cost: " + cheap.get(0) + " first at "
                        + cheap.get(0).cost());

        // ------------------------------------------------ 5. THE LISTS ARE THE DETECTOR'S OWN
        // Not a copy: the same objects. If somebody adds a stoppable kind in one place, this sees it.
        Set<String> may = Agency.interruptible();
        Set<String> mayNot = Agency.untouchable();
        ok(may.equals(com.eternalengine.player.InWorldInterventionDetector.STOPPABLE_KINDS),
                "the interruptible list is the intervention detector's own: " + may);
        ok(mayNot.equals(com.eternalengine.player.InWorldInterventionDetector.REFUSED_KINDS),
                "and so is the untouchable one: " + mayNot);
        eq(Agency.judgeEventKind("battle").answer(), Agency.Answer.YES, "a battle can be stopped");
        eq(Agency.judgeEventKind("war").answer(), Agency.Answer.YES, "and so can a revolt");
        eq(Agency.judgeEventKind("earthquake").answer(), Agency.Answer.NO, "an earthquake cannot");
        eq(Agency.judgeEventKind("plague").answer(), Agency.Answer.NO, "nor a plague");
        ok(Agency.judgeEventKind("earthquake").because().contains("not players"),
                "and the reason is the good one: " + Agency.judgeEventKind("earthquake").because());
        eq(Agency.judgeEventKind("coronation").answer(), Agency.Answer.NO,
                "a kind nobody listed is not a permission: coronations are not stoppable by default");
        eq(Agency.judgeEventKind(null).answer(), Agency.Answer.NO, "and nothing is not a kind");
        System.out.println("  " + Agency.refusalLine());

        // ------------------------------------------------ 6. REAL PLACES, REAL COUNTS
        List<Town> towns = loadTowns();
        ok(towns.size() > 25_000, "the town pack holds the towns: " + towns.size());
        long cahokia = peopleAt(towns, 38.66, -90.06, 1100, "Cahokia");
        long tenochtitlan = peopleAt(towns, 19.43, -99.13, 1500, "Tenochtitlan");
        long rome = peopleAt(towns, 41.89, 12.49, -150, "Rome");
        long london = peopleAt(towns, 51.51, -0.13, 1801, "London");
        long kolkata = peopleAt(towns, 22.57, 88.36, 1710, "Kolkata");
        ok(cahokia > 15_000, "Cahokia is a town the pack counts: " + cahokia);
        ok(tenochtitlan > 150_000, "Tenochtitlan in 1500 is counted: " + tenochtitlan);
        ok(rome > 250_000, "Rome in 150 BC is counted: " + rome);
        ok(london > 900_000, "London in 1801 is counted: " + london);

        // A stranger arriving at each of them. The same person, the same rules, five different worlds.
        Object[][] places = {
                {"Cahokia", 38.66, -90.06, 1100, cahokia},
                {"Tenochtitlan", 19.43, -99.13, 1500, tenochtitlan},
                {"Rome", 41.89, 12.49, -150, rome},
                {"Kolkata", 22.57, 88.36, 1710, kolkata},
                {"London", 51.51, -0.13, 1801, london},
        };
        for (Object[] p : places) {
            Agency.Situation s = Agency.Situation.newcomer((Integer) p[3], (String) p[0], (Long) p[4]);
            List<ChangeRecord.Way> can = Agency.open(s);
            System.out.println("     " + p[0] + " " + p[3] + ": " + can.size() + " of "
                    + ChangeRecord.Way.values().length + " ways open to a stranger - " + can);
            ok(!can.contains(ChangeRecord.Way.FOUND_A_TOWN),
                    "no stranger founds a town at " + p[0]);
        }
        // The same person, settled. Now the size of the place starts to matter, and only downward:
        // a hamlet of eighty has no war in it because eighty people are not two sides.
        int lastResident = -1;
        for (Object[] p : places) {
            Agency.Situation s = new Agency.Situation((Integer) p[3], (String) p[0], (Long) p[4],
                    Agency.Standing.RESIDENT, 0, false, 5);
            List<ChangeRecord.Way> can = Agency.open(s);
            System.out.println("     " + p[0] + " " + p[3] + ": a resident has " + can.size()
                    + " - " + can);
            ok(can.size() >= lastResident, "a resident in a bigger place never has less: " + p[0]);
            lastResident = can.size();
        }
        // The finding, and it is not the one this part expected: a resident of Kolkata in 1710, with
        // 12,000 people around, holds exactly the same four ways as a resident of London in 1801 with
        // 1,011,157. Size stops mattering the moment a place is big enough to have a market, and what
        // decides the rest is standing and what the player brings. Only a hamlet under a thousand
        // people is actually narrowed by its size.
        eq(lastResident, 4, "the size of a place stops deciding once it is past a thousand people: "
                + lastResident + " ways for a resident everywhere from Cahokia to London");
        Agency.Situation hamlet = Agency.Situation.newcomer(1800, "a hamlet", 80);
        ok(Agency.impossible(hamlet).size() > Agency.impossible(
                Agency.Situation.newcomer(1800, "a city", 50_000)).size(),
                "the exception is the small place, where the count really does refuse things");

        // A city of a million is not a place where one stranger can do more, it is a place where one
        // stranger is less. The rules must not reward size with power over people.
        Agency.Situation strangerInLondon = Agency.Situation.newcomer(1801, "London", london);
        ok(!Agency.open(strangerInLondon).contains(ChangeRecord.Way.TAKE_THE_CROWN),
                "a stranger in London in 1801 cannot take the crown either");

        // ------------------------------------------------ 7. NO WAY IS FREE OF THE WORLD
        for (ChangeRecord.Way w : ChangeRecord.Way.values()) {
            ok(Agency.peopleNeeded(w) >= 1,
                    w + " needs somebody to be there: " + Agency.peopleNeeded(w));
            Agency.Situation empty = Agency.Situation.newcomer(1200, "an empty valley", 0);
            eq(Agency.judge(w, empty).answer(), Agency.Answer.NO,
                    "and in an empty valley " + w + " is impossible");
        }

        System.out.println(failed == 0
                ? "Step48AgencyProbe: " + checks + " checks, 0 failed"
                : "Step48AgencyProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
