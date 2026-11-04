import com.eternalengine.civilization.*;
import java.util.*;

/** Faith coverage of RULED place-years, by era. CoW's data is about modern states, so the skew
 *  should be visible if it is real. */
public class Cov43 {
    public static void main(String[] a) {
        int[] eras = {-1000, -500, 0, 500, 1000, 1300, 1500, 1700, 1800, 1900, 1950, 2000};
        Random r = new Random(11);
        System.out.println("era      land  ruled   faith    %");
        for (int era : eras) {
            int land = 0, ruled = 0, faith = 0;
            for (int i = 0; i < 2500; i++) {
                double lat = -56 + 112 * r.nextDouble();
                double lon = -180 + 360 * r.nextDouble();
                String cc = CountryGrid.get().codeAt(lat, lon);
                if (cc == null || cc.isBlank()) continue;
                land++;
                var h = RulerRegister.get().rulerAt(lat, lon, era);
                if (h.isEmpty()) continue;
                ruled++;
                String qid = h.get().wikidata();
                if (qid == null) continue;
                var f = LeaderRegister.get().facts(qid);
                if (f.isPresent() && f.get().faithIn(era).isPresent()) faith++;
            }
            System.out.printf("%6d  %5d  %5d  %5d   %3.0f%%%n",
                    era, land, ruled, faith, ruled == 0 ? 0 : 100.0 * faith / ruled);
        }
    }
}
