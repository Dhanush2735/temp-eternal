import com.eternalengine.civilization.FamousPeople;
import com.eternalengine.civilization.RulerRegister;

import java.util.*;

/**
 * The number that matters: standing at a place in year Y, how many of the people who were alive
 * there are actually FOUND by the game's join?
 *
 * The game asks: rulerAt(lat, lon, Y) -> qid, then FamousPeople.livingIn(qid, lat, lon, Y), which
 * matches a person only when their stored state id EQUALS qid. This probe reproduces exactly that
 * for real world years across the whole span, and reports the hit rate per era.
 */
public final class FamousIngameProbe {

    public static void main(String[] args) {
        int perYear = args.length > 0 ? Integer.parseInt(args[0]) : 3000;
        FamousPeople fp = FamousPeople.get();
        RulerRegister rr = RulerRegister.get();
        List<FamousPeople.Person> buf = new ArrayList<>();
        fp.all().filter(p -> p.state() != null).forEach(buf::add);

        int[] years = {-2000, -1000, -500, 1, 500, 1000, 1300, 1500, 1700, 1800, 1900, 1950, 2000, 2020};
        System.out.println("year\tpeople alive&adult\tfound by the join\thit rate");
        for (int y : years) {
            Collections.shuffle(buf, new java.util.Random(20261022L + y));
            int alive = 0, found = 0;
            for (FamousPeople.Person p : buf) {
                if (alive >= perYear) break;
                if (!p.livingAdultIn(y)) continue;
                alive++;
                // the REAL join, as the game performs it: is THIS person in the list it returns?
                // (a first version of this probe only asked whether the list was non-empty and read a
                // false 100%; a check that cannot fail is not a check)
                String q = rr.rulerAt(p.lat(), p.lon(), y).map(RulerRegister.Hit::wikidata).orElse(null);
                for (FamousPeople.Person g : fp.livingIn(q, p.lat(), p.lon(), y)) {
                    if (g.row() == p.row()) { found++; break; }
                }
            }
            System.out.printf("%d\t%d\t%d\t%.1f%%%n", y, alive, found, 100.0 * found / Math.max(1, alive));
        }
    }
}
