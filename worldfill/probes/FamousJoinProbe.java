import com.eternalengine.civilization.FamousPeople;
import com.eternalengine.civilization.RulerRegister;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * Does the game's own lookup find the people the pack files?
 *
 * The wiring is: EventNews/HistoricalPresence ask RulerRegister for the ruler at (lat, lon, year),
 * take that ruler's Wikidata id, and call FamousPeople.livingIn(qid, ...). So a person is only ever
 * shown if the state id on their row EQUALS the ruler register's id for the same place and year.
 * This probe asks both registers the same question and counts the disagreements.
 *
 * Written 2026-10-22 (the marking turn) after the Wikidata audit found a Greek composer who died in
 * 1949 filed under "Nazi Germany": a wrong id is not a wrong label, it is a person who cannot be found.
 */
public final class FamousJoinProbe {

    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 400;
        FamousPeople fp = FamousPeople.get();
        RulerRegister rr = RulerRegister.get();

        List<FamousPeople.Person> all = new ArrayList<>();
        fp.all().filter(pp -> pp.state() != null).forEach(all::add);
        System.out.println("people with a state id: " + all.size());
        Random rnd = new Random(20261022L);
        int checked = 0, agree = 0, noRuler = 0, mismatch = 0;
        List<String> examples = new ArrayList<>();
        for (int i = 0; i < n && !all.isEmpty(); i++) {
            FamousPeople.Person p = all.get(rnd.nextInt(all.size()));
            String st = p.state();
            if (st == null) continue;
            int year = p.activeFrom() > 0 ? p.activeFrom() : p.activeTo();
            if (year == 0) continue;
            var hit = rr.rulerAt(p.lat(), p.lon(), year);
            checked++;
            if (hit.isEmpty()) {
                noRuler++;
                if (examples.size() < 12) {
                    examples.add("no ruler   | " + p.name() + " (" + year + ") state=" + st
                            + " @" + p.lat() + "," + p.lon());
                }
                continue;
            }
            String rulerQid = hit.get().wikidata();
            if (st.equals(rulerQid)) {
                agree++;
            } else {
                mismatch++;
                if (examples.size() < 12) {
                    examples.add("MISMATCH   | " + p.name() + " (" + year + ") state=" + st
                            + " but the ruler register says " + rulerQid
                            + " (" + hit.get().ruler() + ") @" + p.lat() + "," + p.lon());
                }
            }
        }
        for (String e : examples) System.out.println("  " + e);
        System.out.printf("%nchecked %d: agree %d, mismatch %d, no ruler named %d%n",
                checked, agree, mismatch, noRuler);
        System.out.printf("joinable: %.1f%% of sampled people would be found by the game's own lookup%n",
                100.0 * agree / Math.max(1, checked));
        System.out.println(mismatch == 0 && noRuler == 0 ? "PASS" : "FINDINGS: see the lines above");
    }
}
