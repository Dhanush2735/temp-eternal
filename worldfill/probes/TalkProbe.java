import com.eternalengine.civilization.EventNews;
import com.eternalengine.civilization.FamousPeople;
import com.eternalengine.civilization.HistoricalPresence;
import com.eternalengine.civilization.LeaderRegister;
import com.eternalengine.civilization.LocalLanguages;
import com.eternalengine.civilization.TradeRoutes;
import com.eternalengine.civilization.WaysOfLife;

/**
 * Step-6 check through the mod's own compiled classes (run by worldfill/probe_talk.sh):
 * what /ee who (HistoricalPresence.describe) and villagers (EventNews talk lines) say at the
 * standard test spots, plus load summaries and timings.
 */
public class TalkProbe {
    public static void main(String[] args) {
        long t0 = System.nanoTime();
        System.out.println(LeaderRegister.get().summary());
        System.out.println(FamousPeople.get().summary());
        System.out.println(WaysOfLife.get().summary());
        System.out.println(LocalLanguages.get().summary());
        System.out.println(TradeRoutes.get().summary());
        System.out.printf("registers loaded in %.1f s%n", (System.nanoTime() - t0) / 1e9);
        Object[][] spots = {
                {"Hyderabad", 17.385, 78.4867, 1700}, {"Via Appia south of Rome", 41.80, 12.60, 100},
                {"Merv (Silk Road)", 37.66, 62.18, 1000}, {"Lubeck (Hansa)", 53.87, 10.69, 1400},
                {"Varanasi (Grand Trunk Road)", 25.32, 83.0, 1600}, {"Sydney", -33.87, 151.2, 1500},
                {"Mongolia", 47.0, 103.0, 1200}, {"Paris", 48.86, 2.35, 1789}, {"Washington", 38.9, -77.03, 1863},
                {"Hyderabad", 17.385, 78.4867, 2000}, {"Egypt", 26.5, 31.5, -1300}, {"Ohio valley", 39.0, -84.0, 1200},
        };
        for (Object[] s : spots) {
            double la = (Double) s[1], lo = (Double) s[2];
            int y = (Integer) s[3];
            long q0 = System.nanoTime();
            HistoricalPresence.Result r = HistoricalPresence.query(null, la, lo, y);
            String d = HistoricalPresence.describe(r);
            double ms = (System.nanoTime() - q0) / 1e6;
            StringBuilder keep = new StringBuilder();
            for (String ln : d.split("\n")) {
                if (ln.matches("\\s+(head of|way of life|language of|faiths|trade route|road \\(|born near).*")) {
                    keep.append(ln.length() > 230 ? ln.substring(0, 230) + "..." : ln).append("\n");
                }
            }
            System.out.printf("%n===== %s %d (%.1f ms) =====%n%s", s[0], y, ms, keep);
            System.out.println("  -- villager lines:");
            for (String line : new String[] {EventNews.rulerLine(r), EventNews.cultureLine(r),
                    EventNews.famousLine(r, 7L), EventNews.famousLine(r, 8L), EventNews.wayOfLifeLine(r), EventNews.tradeLine(r), EventNews.roadLine(r)}) {
                if (!line.isBlank()) System.out.println("     \"" + line + "\"");
            }
            r.event().ifPresent(e -> System.out.println("     news: \"" + EventNews.rumor(e.event(), y) + "\""));
        }
    }
}
