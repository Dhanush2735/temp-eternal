import com.eternalengine.civilization.FamousPeople;
import com.eternalengine.civilization.RulerRegister;

import java.util.*;

/**
 * Emit the correction list for people filed under a modern container, one line per row, so the change
 * is reviewable and replayable rather than buried in a script.
 *
 * <p>Output on stdout: {@code row \t oldState \t newState \t year \t name \t polityName}. The row is the
 * index into the master AFTER the rows with neither date are dropped - the same frame famous_people.tiles
 * and the mod's own reader use.
 *
 * <p>A row is only proposed when the register names a DIFFERENT id for that person's own place and
 * year. Rows where it names nothing are listed separately and not touched: no answer is not an answer.
 */
public final class FilingFixProbe {

    private static final Map<String, Integer> CONTAINER_START = Map.ofEntries(
            Map.entry("Q145", 1921), Map.entry("Q29", 1715), Map.entry("Q183", 1949),
            Map.entry("Q38", 1946), Map.entry("Q30", 1776), Map.entry("Q142", 1958),
            Map.entry("Q16", 1867), Map.entry("Q408", 1901), Map.entry("Q159", 1991),
            Map.entry("Q148", 1949), Map.entry("Q43", 1923), Map.entry("Q155", 1889),
            Map.entry("Q96", 1821), Map.entry("Q884", 1948), Map.entry("Q717", 1811));

    public static void main(String[] args) {
        FamousPeople fp = FamousPeople.get();
        RulerRegister rr = RulerRegister.get();
        List<FamousPeople.Person> people = new ArrayList<>();
        fp.all().forEach(people::add);
        people.sort(Comparator.comparingInt(FamousPeople.Person::row));

        System.out.println("#row\toldState\tnewState\tyear\tname\tpolityName");
        int proposed = 0, noAnswer = 0, agree = 0;
        for (FamousPeople.Person p : people) {
            String st = p.state();
            if (st == null) continue;
            Integer start = CONTAINER_START.get(st);
            if (start == null) continue;
            int year = p.activeFrom() > 0 ? p.activeFrom() : p.activeTo();
            if (year == 0 || year >= start) continue;
            var hit = rr.rulerAt(p.lat(), p.lon(), year);
            if (hit.isEmpty() || hit.get().wikidata() == null) { noAnswer++; continue; }
            String reg = hit.get().wikidata();
            if (reg.equals(st)) { agree++; continue; }
            System.out.printf("%d\t%s\t%s\t%d\t%s\t%s%n", p.row(), st, reg, year,
                    p.name().replace('\t', ' '), hit.get().ruler().replace('\t', ' '));
            proposed++;
        }
        System.err.printf("proposed %d corrections; %d rows where the register names nothing; %d where both use the container%n",
                proposed, noAnswer, agree);
    }
}
