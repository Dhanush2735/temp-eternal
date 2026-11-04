/* Step 48 part 6 (F11): errands tied to real history.
   The claim: an errand can be read out of the record instead of authored, because the packs date 23,535
   famous buildings and 184,060 people - and the rule that makes it honest is that a task is only offered
   when the record says the thing is there. */
import com.eternalengine.timeline.Errands;
import com.eternalengine.timeline.PlayerRoles;

import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.zip.GZIPInputStream;

public class Step48ErrandProbe {
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

    static InputStream open(String name) {
        return Step48ErrandProbe.class.getResourceAsStream(
                "/data/eternalengine/eternal/history/" + name);
    }

    /** buildings_famous: [name, lat*1000, lon*1000, kind, from, to, ...]. Undated rows are skipped. */
    static List<Errands.Landmark> loadBuildings() {
        List<Errands.Landmark> out = new ArrayList<>();
        try (InputStream in = open("buildings_famous.json.gz")) {
            if (in == null) return out;
            JsonReader r = new JsonReader(new InputStreamReader(new GZIPInputStream(in),
                    StandardCharsets.UTF_8));
            r.beginObject();
            while (r.hasNext()) {
                if (!"buildings".equals(r.nextName())) { r.skipValue(); continue; }
                r.beginArray();
                while (r.hasNext()) {
                    r.beginArray();
                    String name = r.nextString();
                    double lat = r.nextInt() / 1000.0;
                    double lon = r.nextInt() / 1000.0;
                    String kind = r.nextString();
                    Integer from = null;
                    if (r.peek() == JsonToken.NUMBER) from = r.nextInt(); else r.skipValue();
                    Integer to = null;
                    if (r.peek() == JsonToken.NUMBER) to = r.nextInt(); else r.skipValue();
                    while (r.hasNext()) r.skipValue();
                    r.endArray();
                    if (from != null) out.add(new Errands.Landmark(name, kind, lat, lon, from, to));
                }
                r.endArray();
            }
            r.endObject();
        } catch (Exception e) {
            System.out.println("  buildings error: " + e);
        }
        return out;
    }

    /** famous_people: [name, description, birth, death, state, lat, lon, radiusKm]. */
    static List<Errands.Life> loadPeople() {
        List<Errands.Life> out = new ArrayList<>();
        try (InputStream in = open("famous_people.json.gz")) {
            if (in == null) return out;
            JsonReader r = new JsonReader(new InputStreamReader(new GZIPInputStream(in),
                    StandardCharsets.UTF_8));
            r.beginObject();
            while (r.hasNext()) {
                if (!"people".equals(r.nextName())) { r.skipValue(); continue; }
                r.beginArray();
                while (r.hasNext()) {
                    r.beginArray();
                    String name = r.nextString();
                    String what = r.nextString();
                    int born = Integer.MIN_VALUE, died = Integer.MIN_VALUE;
                    if (r.peek() == JsonToken.NUMBER) born = r.nextInt(); else r.skipValue();
                    if (r.peek() == JsonToken.NUMBER) died = r.nextInt(); else r.skipValue();
                    r.skipValue();                              // state
                    r.skipValue();                              // lat
                    r.skipValue();                              // lon
                    r.skipValue();                              // radiusKm
                    r.endArray();
                    if (born != Integer.MIN_VALUE && died != Integer.MIN_VALUE && died >= born) {
                        // The description is read again from the row: Gson has already consumed it, so
                        // the order above had to be exact. Kept simple: the name carries the errand.
                        out.add(new Errands.Life(name, "", born, died, 0, 0));
                    }
                }
                r.endArray();
            }
            r.endObject();
        } catch (Exception e) {
            System.out.println("  people error: " + e);
        }
        return out;
    }

    /** The same reader, but keeping the coordinates, which make an errand offerable. */
    static List<Errands.Life> loadPeopleWithPlaces() {
        List<Errands.Life> out = new ArrayList<>();
        try (InputStream in = open("famous_people.json.gz")) {
            if (in == null) return out;
            JsonReader r = new JsonReader(new InputStreamReader(new GZIPInputStream(in),
                    StandardCharsets.UTF_8));
            r.beginObject();
            while (r.hasNext()) {
                if (!"people".equals(r.nextName())) { r.skipValue(); continue; }
                r.beginArray();
                while (r.hasNext()) {
                    r.beginArray();
                    String name = r.nextString();
                    String what = r.nextString();
                    Integer born = r.peek() == JsonToken.NUMBER ? r.nextInt() : null;
                    if (born == null) r.skipValue();
                    Integer died = r.peek() == JsonToken.NUMBER ? r.nextInt() : null;
                    if (died == null) r.skipValue();
                    r.skipValue();                              // state
                    Double lat = r.peek() == JsonToken.NUMBER ? r.nextDouble() : null;
                    if (lat == null) r.skipValue();
                    Double lon = r.peek() == JsonToken.NUMBER ? r.nextDouble() : null;
                    if (lon == null) r.skipValue();
                    r.skipValue();                              // radiusKm
                    r.endArray();
                    if (born != null && died != null && died >= born && lat != null && lon != null) {
                        out.add(new Errands.Life(name, what, born, died, lat, lon));
                    }
                }
                r.endArray();
            }
            r.endObject();
        } catch (Exception e) {
            System.out.println("  people error: " + e);
        }
        return out;
    }

    public static void main(String[] args) {
        List<Errands.Landmark> buildings = loadBuildings();
        List<Errands.Life> people = loadPeopleWithPlaces();
        ok(buildings.size() > 20_000, "the record dates the famous buildings: " + buildings.size());
        // 184,060 rows, of which 124,941 carry both dates and a place. The rest are dated people with no
        // coordinates or no year, and an errand cannot be offered to a person with no place to be.
        ok(people.size() > 120_000, "and the people who have both dates and a place: " + people.size());

        // ------------------------------------------------ 1. A BUILDING STANDS ONLY IN ITS YEARS
        Errands.Landmark neverBuilt = new Errands.Landmark("An Unbuilt Palace", "palace", 28.6, 77.2,
                1700, null);
        ok(!neverBuilt.standsIn(1699), "a building does not stand before it is begun");
        ok(neverBuilt.standsIn(1700), "and does from the year the record gives");
        ok(neverBuilt.standsIn(2000), "and for as long as it stands");
        ok(neverBuilt.buildingIn(1680), "and is going up for the twenty-five years before");
        ok(!neverBuilt.buildingIn(1660), "but not before that");

        // The Red Fort, from the record and not from memory.
        Errands.Landmark redFort = null;
        for (Errands.Landmark l : buildings) {
            if (l.name().equals("Red Fort")) { redFort = l; break; }
        }
        ok(redFort != null, "the record has the Red Fort");
        if (redFort != null) {
            System.out.println("     Red Fort: " + redFort.kind() + ", from " + redFort.from() + ", to "
                    + redFort.to() + ", at " + redFort.lat() + "," + redFort.lon());
            ok(!redFort.standsIn(1600), "and it is not standing in 1600");
            ok(redFort.standsIn(1800), "and is in 1800");
        }

        // ------------------------------------------------ 2. NO ERRAND TO A BUILDING THAT IS NOT THERE
        // Delhi, 1600: sweep every offer in a hundred years either side and check the rule holds.
        int anachronisms = 0, offered = 0;
        for (int y = 1400; y <= 1800; y += 25) {
            for (Errands.Errand e : Errands.allOffers(y, 28.61, 77.21, buildings, people)) {
                offered++;
                if (e.kind() == Errands.Kind.DELIVER && !e.dated()) anachronisms++;
            }
        }
        ok(offered > 100, "the record offers work around Delhi across the centuries: " + offered);
        eq(anachronisms, 0, "and not one errand sends a player to a building that is not standing yet");

        // ------------------------------------------------ 3. THREE OFFERS, NEAREST FIRST
        List<Errands.Errand> delhi1600 = Errands.offers(1600, 28.61, 77.21, buildings, people);
        ok(!delhi1600.isEmpty(), "there is work in Delhi in 1600: "
                + Errands.summary(1600, 28.61, 77.21, buildings, people));
        ok(delhi1600.size() <= Errands.OFFER, "and no more than three offers at once: "
                + delhi1600.size());
        for (int i = 1; i < delhi1600.size(); i++) {
            ok(delhi1600.get(i).km() >= delhi1600.get(i - 1).km(), "sorted nearest first");
        }
        for (Errands.Errand e : delhi1600) {
            ok(e.km() <= Errands.REACH_KM, "and none of them is beyond the reach: " + e.where());
        }
        for (Errands.Errand e : delhi1600) System.out.println("     " + e.line());

        // A letter from Delhi to a place on the other side of the world is not offered.
        List<Errands.Errand> londonOnly = Errands.allOffers(1800, 51.51, -0.13,
                List.of(new Errands.Landmark("A Palace in Delhi", "palace", 28.6, 77.2, 1600, null)),
                List.of());
        ok(londonOnly.isEmpty(), "a letter from London to Delhi is not offered: "
                + Errands.REACH_KM + " km is the limit");

        // ------------------------------------------------ 4. HELPING ON A SCAFFOLD
        Errands.Errand building = null;
        for (Errands.Errand e : Errands.allOffers(1630, 28.61, 77.21, buildings, people)) {
            if (e.kind() == Errands.Kind.HELP_BUILD) { building = e; break; }
        }
        if (building != null) {
            System.out.println("     " + building.line());
            ok(building.body().contains("scaffolding"), "helping on a building is a day of work: "
                    + building.body());
        } else {
            ok(false, "there is work on a building going up in Delhi in 1630");
        }

        // ------------------------------------------------ 5. NOBODY IS MET OUT OF THEIR YEARS
        int wrongYears = 0, met = 0;
        for (int y = 1500; y <= 1700; y += 10) {
            for (Errands.Errand e : Errands.allOffers(y, 27.18, 78.02, buildings, people)) {
                if (e.kind() != Errands.Kind.MEET) continue;
                met++;
                if (!e.dated()) wrongYears++;
            }
        }
        ok(met > 50, "the record offers people to meet around Agra: " + met);
        eq(wrongYears, 0, "and never one outside the years they were alive");

        // ------------------------------------------------ 6. PAST THE SEAM THERE IS NOBODY, AND IT SAYS SO
        ok(!Errands.possible(Errands.Kind.MEET, 2400), "nobody is recorded in 2400");
        ok(Errands.impossibleBecause(Errands.Kind.MEET, 2400).contains("2026"),
                "and the refusal names the seam: " + Errands.impossibleBecause(Errands.Kind.MEET, 2400));
        ok(Errands.possible(Errands.Kind.DELIVER, 2400),
                "while a letter to a building that still stands is still work");
        List<Errands.Errand> future = Errands.offers(2400, 28.61, 77.21, buildings, people);
        int meetings = 0;
        for (Errands.Errand e : future) if (e.kind() == Errands.Kind.MEET) meetings++;
        eq(meetings, 0, "so no offer past the seam sends anybody to find a person");
        ok(!future.isEmpty(), "and there is still work, because the buildings stand: "
                + Errands.summary(2400, 28.61, 77.21, buildings, people));

        // ------------------------------------------------ 7. AN ERRAND PAYS IN DEEDS, NOT IN COIN
        PlayerRoles.Deeds deeds = PlayerRoles.Deeds.none();
        int year = 1600;
        int done = 0;
        for (Errands.Errand e : Errands.allOffers(year, 28.61, 77.21, buildings, people)) {
            if (e.kind() != Errands.Kind.DELIVER) continue;
            for (int k = 0; k < 20; k++) {
                PlayerRoles.Deeds gain = e.earned(year);
                deeds = new PlayerRoles.Deeds(deeds.sales() + gain.sales(), deeds.fights()
                        + gain.fights(), deeds.courtDays() + gain.courtDays(),
                        deeds.cardsLearned() + gain.cardsLearned(), false, year);
                done++;
            }
            break;
        }
        eq(done, 20, "twenty letters carried");
        eq(deeds.courtDays(), 20, "is twenty days of being useful to people who matter");
        eq(PlayerRoles.held(deeds, year), PlayerRoles.Role.COURTIER,
                "which is what makes a courtier, without a single coin changing hands: "
                        + PlayerRoles.progressLine(deeds, year));

        // ------------------------------------------------ 8. AND IT IS NOT HISTORY
        Errands.Errand one = delhi1600.get(0);
        ok(!one.records(), "an errand is not written into the chronicle");
        ok(one.whyNotHistory().contains("chronicle"), "and says why: " + one.whyNotHistory());
        for (Errands.Refused r : Errands.Refused.values()) {
            ok(r.why().length() > 40, r + " is refused in a sentence rather than a shrug");
        }
        ok(Errands.Refused.A_LETTER_TO_A_BUILDING_NOT_YET_BEGUN.why().contains("1648"),
                "the anachronism is named with its own example: "
                        + Errands.Refused.A_LETTER_TO_A_BUILDING_NOT_YET_BEGUN.why());

        System.out.println("  " + Errands.ruleLine(1600));
        System.out.println("  " + Errands.summary(1800, 51.51, -0.13, buildings, people));
        System.out.println(failed == 0
                ? "Step48ErrandProbe: " + checks + " checks, 0 failed"
                : "Step48ErrandProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
