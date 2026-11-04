import com.eternalengine.civilization.HistoricalPresence;
import com.eternalengine.civilization.RulerRegister;
import com.eternalengine.civilization.WhoRuled;
import com.eternalengine.knowledge.KnowledgeCard;
import com.eternalengine.knowledge.LocalCards;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonParser;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * R2-6, the test set for card coverage (2026-10-24).
 *
 * <p>The row says "a card for every town in the test set". This probe defines that set: <b>50 towns drawn
 * from the town register with a fixed seed</b>, so the number is reproducible and cannot drift by choice of
 * sample. For each town it builds the town's cards and counts the answers a player can actually ask for.
 *
 * <p>It runs headless. {@code HistoricalPresence.query} needs the civilization manager, which throws without a
 * world (a known limit), so the result is built from {@code nobody(...)} — which is the honest worst case:
 * a place the history data does not otherwise describe. A card that answers here answers anywhere.
 */
public final class CardCoverageProbe {

    private static final int TOWNS = 50;
    private static final long SEED = 606060L;

    public static void main(String[] args) {
        RulerRegister rr = RulerRegister.get();
        List<WhoRuled.Cap> caps = WhoRuled.packCapitals();
        List<Object[]> towns = towns();
        System.out.println(rr.summary().display());
        System.out.println("town register for the test set: " + towns.size());

        Random random = new Random(SEED);
        int built = 0, withPlaceCard = 0, withRulerCard = 0, withNews = 0, withPeople = 0;
        long answers = 0, nonEmpty = 0;
        List<String> rows = new ArrayList<>();
        rows.add("town\tlat\tlon\tyear\tcards\tquestions\tanswered\tplaceCard\trulerCard\tnewsCard\tfamousCard");
        while (built < TOWNS && !towns.isEmpty()) {
            Object[] t = towns.get(random.nextInt(towns.size()));
            String name = (String) t[0];
            double lat = (double) t[1] / 1000.0d;
            double lon = (double) t[2] / 1000.0d;
            int founded = (int) t[3];
            int year = Math.max(founded, Math.min(2025, founded + random.nextInt(Math.max(1, 2025 - founded))));

            var result = HistoricalPresence.nobody(lat, lon, year);
            LocalCards.Local local = LocalCards.build(result, lat, lon);
            // The ruler card needs a ruler in the Result. Headless there is no civilization manager, but the
            // layered answer supplies one, so the result is rebuilt with it: this is the honest measurement
            // of the ruler card rather than a zero produced by an empty input.
            var layered = WhoRuled.hit(lat, lon, year);
            HistoricalPresence.Result withRuler = new HistoricalPresence.Result(year, lat, lon,
                    java.util.Optional.empty(), java.util.Optional.empty(), java.util.Optional.empty(),
                    java.util.Optional.empty(), java.util.Optional.empty(), java.util.Optional.empty(),
                    java.util.Optional.empty(), layered, java.util.Optional.empty(),
                    java.util.Optional.empty(),
                    layered.map(RulerRegister.Hit::civHint).orElse(""));
            LocalCards.Local localWithRuler = LocalCards.build(withRuler, lat, lon);
            built++;
            int cards = local.cards() == null ? 0 : local.cards().size();
            int qTotal = 0, qFilled = 0;
            if (local.cards() != null) {
                for (KnowledgeCard card : local.cards().values()) {
                    if (card == null || card.questions() == null) {
                        continue;
                    }
                    for (KnowledgeCard.Question q : card.questions()) {
                        qTotal++;
                        if (q.answers() != null && !q.answers().isEmpty()) {
                            qFilled++;
                        }
                    }
                }
            }
            boolean place = local.placeCard() != null;
            boolean ruler = localWithRuler.rulerCard() != null;
            boolean news = local.newsCard() != null;
            boolean people = local.famousCard() != null;
            if (place) withPlaceCard++;
            if (ruler) withRulerCard++;
            if (news) withNews++;
            if (people) withPeople++;
            answers += qTotal;
            nonEmpty += qFilled;
            rows.add(String.format(java.util.Locale.ROOT, "%s\t%.3f\t%.3f\t%d\t%d\t%d\t%d\t%s\t%s\t%s\t%s",
                    name, lat, lon, year, cards, qTotal, qFilled, place, ruler, news, people));
        }
        try {
            java.nio.file.Files.write(java.nio.file.Path.of("/home/user/testrun/verify/cards_test_set.csv"), rows);
        } catch (Exception e) {
            System.out.println("write failed: " + e.getMessage());
        }

        System.out.println();
        System.out.println("test set                        : " + built + " towns");
        System.out.println("towns with a place card         : " + withPlaceCard + pct(withPlaceCard, built));
        System.out.println("towns with a ruler card         : " + withRulerCard + pct(withRulerCard, built));
        System.out.println("towns with a news card          : " + withNews + pct(withNews, built));
        System.out.println("towns with a famous-people card : " + withPeople + pct(withPeople, built));
        System.out.println("  (ruler card measured with the layered ruler handed to the card builder)");
        System.out.println("questions on cards              : " + answers);
        System.out.println("  answered in words             : " + nonEmpty + pct((int) nonEmpty, (int) answers));
        System.out.println();
        System.out.println("rows: testrun/verify/cards_test_set.csv");
    }

    private static String pct(int n, int total) {
        return total == 0 ? "" : String.format(java.util.Locale.ROOT, "  (%.1f%%)", 100.0 * n / total);
    }

    /** name, lat*1000, lon*1000, founded - dated towns only, so the year asked is inside the town's life. */
    private static List<Object[]> towns() {
        List<Object[]> out = new ArrayList<>();
        try (InputStream raw = CardCoverageProbe.class.getResourceAsStream(
                "/data/eternalengine/eternal/history/towns.json.gz")) {
            if (raw == null) {
                return out;
            }
            try (Reader r = new InputStreamReader(new java.util.zip.GZIPInputStream(raw), StandardCharsets.UTF_8)) {
                JsonArray list = JsonParser.parseReader(r).getAsJsonObject().getAsJsonArray("towns");
                for (JsonElement el : list) {
                    JsonArray row = el.getAsJsonArray();
                    if (row.size() < 6 || row.get(1).isJsonNull() || row.get(2).isJsonNull()
                            || row.get(3).isJsonNull() || row.get(5).isJsonNull()) {
                        continue;
                    }
                    int founded = row.get(5).getAsInt();
                    if (founded == 0 || founded < -3000) {
                        continue;
                    }
                    out.add(new Object[] {row.get(1).getAsString(), row.get(2).getAsDouble(),
                            row.get(3).getAsDouble(), founded});
                }
            }
        } catch (Exception e) {
            System.out.println("towns: " + e.getMessage());
        }
        return out;
    }
}
