import com.eternalengine.civilization.FamousPeople;
import com.eternalengine.civilization.RulerRegister;

import java.util.*;

/**
 * When the join fails, is it the POLITY that is wrong, or the YEAR we ask about?
 *
 * The pack records a state for a person; the game asks RulerRegister for the ruler at
 * (lat, lon, activeFrom) and keeps the person only if the two ids are equal. activeFrom is
 * birth+20. This probe takes people the join misses and asks the SAME register at other plausible
 * years of their life - birth, birth+10, birth+20, mid-life, death-10, death - and reports which
 * year, if any, reproduces the id the pack stores.
 *
 * If one year explains most of the misses, the defect is a year convention, not a bad polity, and
 * the fix is one line rather than a re-scrape.
 */
public final class FamousYearProbe {

    public static void main(String[] args) {
        int limit = args.length > 0 ? Integer.parseInt(args[0]) : 3000;
        FamousPeople fp = FamousPeople.get();
        RulerRegister rr = RulerRegister.get();

        List<FamousPeople.Person> buf = new ArrayList<>();
        fp.all().filter(p -> p.state() != null && p.birth() != -1 && p.death() != -1).forEach(buf::add);
        Collections.shuffle(buf, new java.util.Random(20261022L));

        String[] names = {"birth", "birth+10", "birth+20 (what the game asks)", "mid-life", "death-10", "death"};
        int[] hit = new int[names.length];
        int tried = 0, anyYear = 0;
        int[] birthKnown = {0};

        for (FamousPeople.Person p : buf) {
            if (tried >= limit) break;
            int b = p.birth(), d = p.death();
            if (b == FamousPeople.UNKNOWN || d == FamousPeople.UNKNOWN || b > d) continue;
            int active = p.activeFrom() > 0 ? p.activeFrom() : p.activeTo();
            if (active == 0) continue;
            var now = rr.rulerAt(p.lat(), p.lon(), active);
            if (now.isEmpty() || p.state().equals(now.get().wikidata())) continue;   // already joins
            tried++;
            int[] years = {b, b + 10, b + 20, (b + d) / 2, d - 10, d};
            boolean found = false;
            for (int i = 0; i < years.length; i++) {
                var h = rr.rulerAt(p.lat(), p.lon(), years[i]);
                if (h.isPresent() && p.state().equals(h.get().wikidata())) { hit[i]++; found = true; }
            }
            if (found) anyYear++;
        }
        System.out.println("people the normal join misses: " + tried);
        for (int i = 0; i < names.length; i++) {
            System.out.printf("  %-28s reproduces the pack's state for %5d  (%5.1f%%)%n",
                    names[i], hit[i], 100.0 * hit[i] / Math.max(1, tried));
        }
        System.out.printf("%nany of those years explains %d of %d (%.1f%%)%n",
                anyYear, tried, 100.0 * anyYear / Math.max(1, tried));
    }
}
