import com.eternalengine.civilization.FamousPeople;
import com.eternalengine.civilization.RulerRegister;

import java.util.*;

/**
 * The whole population, not a sample: ask the game's own join for every person the pack files
 * under a state, and tally which pairs disagree.
 *
 * The point is not the percentage - it is the SHORT LIST. If a few hundred (pack state, ruler state)
 * pairs explain most of the failures, the fix is a translation table, not 45,000 hand edits.
 *
 * Writes a TSV on stdout: pair\tcount\tpackLabel\trulerLabel
 */
public final class FamousJoinFullProbe {

    public static void main(String[] args) throws Exception {
        boolean full = args.length > 0 && args[0].equals("--full");
        int limit = args.length > 1 ? Integer.parseInt(args[1]) : (full ? Integer.MAX_VALUE : 5000);
        FamousPeople fp = FamousPeople.get();
        RulerRegister rr = RulerRegister.get();

        Map<String, Integer> pairs = new HashMap<>();
        Map<String, String> packName = new HashMap<>();
        Map<String, String> rulerName = new HashMap<>();
        int checked = 0, agree = 0, noRuler = 0, mismatch = 0;
        List<FamousPeople.Person> buf = new ArrayList<>();
        fp.all().filter(p -> p.state() != null).forEach(buf::add);
        System.out.println("people with a state id: " + buf.size() + " (checking " + Math.min(limit, buf.size()) + ")");

        java.util.Random rnd = new java.util.Random(20261022L);
        Collections.shuffle(buf, rnd);
        long t0 = System.currentTimeMillis();
        for (FamousPeople.Person p : buf) {
            if (checked >= limit) break;
            String st = p.state();
            if (st == null) continue;
            int year = p.activeFrom() > 0 ? p.activeFrom() : p.activeTo();
            if (year == 0) continue;
            var hit = rr.rulerAt(p.lat(), p.lon(), year);
            checked++;
            if (hit.isEmpty()) { noRuler++; continue; }
            String rq = hit.get().wikidata();
            if (rq == null) { noRuler++; continue; }
            if (st.equals(rq)) { agree++; continue; }
            mismatch++;
            String key = st + "\t" + rq;
            pairs.merge(key, 1, Integer::sum);
            packName.putIfAbsent(st, "");
            rulerName.putIfAbsent(rq, hit.get().ruler());
        }
        long ms = System.currentTimeMillis() - t0;
        System.err.printf("checked %d in %d ms: agree %d, mismatch %d, no ruler %d, joinable %.1f%%%n",
                checked, ms, agree, mismatch, noRuler, 100.0 * agree / Math.max(1, checked));
        System.err.println("distinct mismatching pairs: " + pairs.size());

        List<Map.Entry<String, Integer>> sorted = new ArrayList<>(pairs.entrySet());
        sorted.sort((a, b) -> b.getValue() - a.getValue());
        System.out.println("count\tpackState\trulerQid\trulerLabel");
        long cum = 0;
        for (var e : sorted) {
            String[] k = e.getKey().split("\t");
            cum += e.getValue();
            System.out.println(e.getValue() + "\t" + k[0] + "\t" + k[1] + "\t" + rulerName.getOrDefault(k[1], ""));
        }
        System.err.printf("top 200 pairs cover %.1f%% of all %d mismatches%n",
                100.0 * sorted.stream().limit(200).mapToInt(Map.Entry::getValue).sum() / Math.max(1, mismatch), mismatch);
    }
}
