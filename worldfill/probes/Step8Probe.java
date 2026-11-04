import com.eternalengine.civilization.EventNews;
import com.eternalengine.civilization.HistoricalPresence;
import com.eternalengine.civilization.LeaderRegister;
import com.eternalengine.civilization.TradeRoutes;

/**
 * Step-8 check through the mod's own compiled classes (run by worldfill/probe_step8.sh): the ruler a
 * villager names at places whose state id was repaired or whose ruler list was filled, and the four
 * new trade routes. Prints one line per spot: the state, the head of state, the head of government,
 * the trade line.
 */
public class Step8Probe {
    public static void main(String[] args) {
        System.out.println(LeaderRegister.get().summary());
        System.out.println(TradeRoutes.get().summary());
        Object[][] spots = {
                {"Chang'an (Han)", 34.30, 108.90, 1}, {"Luoyang (Han)", 34.62, 112.45, 150}, {"Xi'an (Wu Zetian)", 34.27, 108.95, 700},
                {"Linzi (state of Qi)", 36.85, 118.30, 400 * -1}, {"Rome (consuls)", 41.89, 12.49, -59}, {"Rome (empire)", 41.89, 12.49, 100},
                {"Constantinople", 41.01, 28.98, 1000}, {"Memphis (Khufu)", 29.85, 31.25, -2570}, {"Thebes", 25.70, 32.64, -1270},
                {"Babylon", 32.54, 44.42, -1760}, {"Pataliputra (Gupta)", 25.61, 85.14, 500}, {"Paithan (Satavahana)", 19.48, 75.38, 1},
                {"Warangal (Kakatiya)", 17.97, 79.59, 1280}, {"Golconda", 17.38, 78.40, 1600}, {"Hyderabad (Nizam)", 17.385, 78.49, 1900},
                {"Delhi", 28.61, 77.21, 1650}, {"Calcutta", 22.57, 88.36, 1850}, {"Bombay", 18.94, 72.83, 1900}, {"Batavia", -6.20, 106.82, 1900},
                {"Mexico City (colony)", 19.43, -99.13, 1650}, {"Seoul", 37.57, 126.98, 1990}, {"Pyongyang", 39.04, 125.76, 1990},
                {"Taipei", 25.03, 121.56, 1990}, {"Beijing", 39.90, 116.40, 1990}, {"Seoul (Joseon)", 37.57, 126.98, 1600},
                {"Kyiv", 50.45, 30.52, 2020}, {"Damascus", 33.51, 36.29, 2000}, {"Bratislava", 48.15, 17.11, 2000}, {"Copenhagen", 55.68, 12.57, 2000},
                {"Paris", 48.86, 2.35, 1700}, {"London", 51.51, -0.13, 1850}, {"Ctesiphon (Sasanian)", 33.09, 44.58, 550},
                {"Karachi (dominion)", 24.86, 67.01, 1950}, {"Mexico City", 19.43, -99.13, 1950}, {"Kyoto", 35.01, 135.77, 1000},
                {"Paithan (Dakshinapatha)", 19.48, 75.38, 100}, {"Taxila (Uttarapatha)", 33.74, 72.79, 100}, {"Carnuntum (Amber Road)", 48.11, 16.86, 100},
                {"Bharuch (Indian Ocean)", 21.70, 72.98, 1000},
        };
        for (Object[] s : spots) {
            double la = ((Number) s[1]).doubleValue(), lo = ((Number) s[2]).doubleValue();
            int y = ((Number) s[3]).intValue();
            HistoricalPresence.Result r = HistoricalPresence.query(null, la, lo, y);
            StringBuilder sb = new StringBuilder();
            for (String ln : HistoricalPresence.describe(r).split("\n")) {
                if (ln.matches("\\s+(head of state|head of government|trade route).*")) {
                    sb.append(" |").append(ln.trim().length() > 110 ? ln.trim().substring(0, 110) : ln.trim());
                }
            }
            String ruler = EventNews.rulerLine(r);
            System.out.printf("%-26s %5d  %s%s%n", s[0], y, ruler.isBlank() ? "(no state)" : ruler, sb);
        }
    }
}
