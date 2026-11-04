import com.eternalengine.civilization.HistoryGazetteer;
import com.eternalengine.civilization.Presence;
import com.eternalengine.civilization.RulerRegister;
import com.eternalengine.knowledge.CardStore;

import java.util.*;

/**
 * The OTHER id joins, after the famous-people join turned out to hide one person in five.
 *
 * <p><b>Join A, presence -> person.</b> The real call path is
 * {@code PlaceCards}: {@code Presence.stayNear(card.qid(), ...)} - the id is a Wikidata Q-number,
 * and presence.json is keyed by Q-number too, so the two id spaces agree by construction. This
 * probe spot-checks that agreement: for well-known people, do the stays filed under a Q-number
 * overlap the life their card records? <b>A first version of this probe used the famous-people row
 * index instead and reported 62% of stays outside the person's life; that was my error, not the
 * code's</b> - nothing in the mod reads presence by row. It is kept here as the corrected test.
 *
 * <p><b>Join B, site -> polity.</b> A gazetteer site carries a {@code civHint}; the ruler register
 * names a polity for the same point and year; the two are compared as strings. Where they differ,
 * one line calls the place by one name and the next by another.
 */
public final class RegisterJoinProbe {

    private static final String[] NAMES = {
            "Nikos Skalkottas", "Wolfgang Amadeus Mozart", "Ibn al-Nafis", "Enheduanna",
            "Charles Darwin", "Ibn Battuta", "Rani of Jhansi", "Hammurabi", "Aristotle",
            "Rabindranath Tagore", "Genghis Khan", "Leonardo da Vinci", "Mansa Musa",
            "Zheng He", "Aethelred the Unready", "Napoleon", "Murasaki Shikibu", "Srinivasa Ramanujan",
            "Christopher Wren", "Ada Lovelace"};

    public static void main(String[] args) {
        int sample = args.length > 0 ? Integer.parseInt(args[0]) : 3000;

        // ---------------------------------------------------------------- Join A
        System.out.println("JOIN A  presence -> person (by Wikidata Q-number, the way the mod does it)");
        Presence pres = Presence.get();
        CardStore cards = CardStore.get();
        int seen = 0, withStays = 0, overlapping = 0, outside = 0, dated = 0;
        for (String n : NAMES) {
            List<CardStore.Card> found = cards.byName(n);
            for (CardStore.Card c : found) {
                if (!c.person()) continue;
                seen++;
                List<Presence.Stay> stays = pres.of(c.qid());
                if (stays.isEmpty()) continue;
                withStays++;
                boolean any = false;
                for (Presence.Stay s : stays) {
                    if (s.from() == Presence.UNKNOWN && s.to() == Presence.UNKNOWN) continue;
                    dated++;
                    int from = s.from() == Presence.UNKNOWN ? c.from() : s.from();
                    int to = s.to() == Presence.UNKNOWN ? from + 100 : s.to();
                    if (to >= c.from() && from <= c.to()) any = true;
                }
                if (any) overlapping++; else outside++;
                System.out.printf("  %-28s qid %-12d life %5d..%-5d stays %2d %s%n",
                        c.name(), c.qid(), c.from(), c.to(), stays.size(),
                        any ? "ok" : "OUTSIDE THE LIFE");
                break;
            }
        }
        System.out.printf("  cards found %d, with stays %d, overlap %d, outside %d, dated stays %d%n",
                seen, withStays, overlapping, outside, dated);

        // ---------------------------------------------------------------- Join B
        RulerRegister rr = RulerRegister.get();
        HistoryGazetteer gaz = HistoryGazetteer.get();
        List<HistoryGazetteer.Site> sites = new ArrayList<>(gaz.allSites());
        Collections.shuffle(sites, new Random(20261022L));
        int checked = 0, agree = 0, differ = 0, notNamed = 0;
        Map<String, Integer> pairs = new HashMap<>();
        List<String> examples = new ArrayList<>();
        for (HistoryGazetteer.Site s : sites) {
            if (checked >= sample) break;
            if (s.civHint() == null || s.civHint().isBlank()) continue;
            int year = Math.max(s.occupiedStart(), Math.min(s.occupiedEnd() - 1, s.occupiedStart() + 1));
            if (year < -3000 || year > 2026) continue;
            var hit = rr.rulerAt(s.lat(), s.lon(), year);
            checked++;
            if (hit.isEmpty() || hit.get().civHint() == null) { notNamed++; continue; }
            String reg = hit.get().civHint();
            if (reg.equals(s.civHint())) agree++;
            else {
                differ++;
                pairs.merge(s.civHint() + " -> " + reg, 1, Integer::sum);
                if (examples.size() < 8) {
                    examples.add(String.format("%s (%d): site says %s, register says %s (%s)",
                            s.displayName(), year, s.civHint(), reg, hit.get().ruler()));
                }
            }
        }
        System.out.printf("%nJOIN B  site -> polity (string equality on civHint)%n");
        System.out.printf("  sites checked %d: agree %d (%.1f%%), differ %d (%.1f%%), no ruler named %d%n",
                checked, agree, 100.0 * agree / Math.max(1, checked),
                differ, 100.0 * differ / Math.max(1, checked), notNamed);
        for (String e : examples) System.out.println("     " + e);
        System.out.println("\n  most common disagreements:");
        pairs.entrySet().stream().sorted((a, b) -> b.getValue() - a.getValue()).limit(8)
                .forEach(e -> System.out.printf("     %4d  %s%n", e.getValue(), e.getKey()));
    }
}
