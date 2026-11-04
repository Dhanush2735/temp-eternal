import com.eternalengine.knowledge.DatedEvents;
import com.eternalengine.knowledge.KnowledgeDate;
import com.eternalengine.knowledge.NewsIndex;

/** Show, on a real day-dated event, that the news is silent before it and told on the day. (R2-7) */
public final class NewsDayProbe {
    public static void main(String[] args) {
        var d = DatedEvents.get();
        System.out.println(d);
        System.out.println();
        int shown = 0;
        for (var e : d.all()) {
            if (e.prec() != 11 || e.m() < 3 || e.m() > 10 || e.y() < 1000) {
                continue;
            }
            int day = KnowledgeDate.key(e.y(), e.m(), e.d());
            var before = NewsIndex.onDay(e.lat(), e.lon(), day - 1);
            var on = NewsIndex.onDay(e.lat(), e.lon(), day);
            String b = before.map(NewsIndex.OnDay::name).orElse("(nothing)");
            String o = on.map(NewsIndex.OnDay::name).orElse("(nothing)");
            boolean good = !b.equals(e.name()) && o.equals(e.name());
            System.out.printf(java.util.Locale.ROOT, "%-5s %-38s %s%n",
                    good ? "OK" : "CHECK", e.name().length() > 36 ? e.name().substring(0, 36) : e.name(), e.when());
            System.out.printf("        day before -> %s%n        on the day -> %s%n", b, o);
            if (++shown >= 6) {
                break;
            }
        }
        System.out.println();
        // The old loophole, stated: a year-only event may not speak about a running year.
        var june1619 = NewsIndex.onDay(51.207d, 16.155d, KnowledgeDate.key(1619, 6, 15));
        System.out.println("Legnica, 15 June 1619 -> " + june1619.map(NewsIndex.OnDay::text)
                .orElse("(nothing - and nothing from 1619 or later may be told)"));
    }
}
