import com.eternalengine.civilization.EventNews;
import com.eternalengine.civilization.HistoricalPresence;

/**
 * The facts a villager would be allowed to use in an AI chat: exactly the lines the mod's current
 * affairs briefing already builds for a place and year (EventNews, as in CurrentAffairsEngine).
 * Used by tools/local_chat_demo.py to show the AI chat working with a local model.
 *
 * Usage: ChatFactsProbe "Hyderabad" 17.385 78.4867 1850 ["Rome" 41.9 12.5 100 ...]
 * Prints one block per place: "== name year" followed by one fact per line.
 */
public class ChatFactsProbe {
    public static void main(String[] args) {
        for (int i = 0; i + 3 < args.length; i += 4) {
            String name = args[i];
            double lat = Double.parseDouble(args[i + 1]);
            double lon = Double.parseDouble(args[i + 2]);
            int year = Integer.parseInt(args[i + 3]);
            HistoricalPresence.Result r = HistoricalPresence.query(null, lat, lon, year);
            System.out.println("== " + name + " " + year);
            String[] lines = {
                    EventNews.placeLine(r), EventNews.rulerLine(r), EventNews.cultureLine(r),
                    EventNews.famousLine(r, year), EventNews.wayOfLifeLine(r),
                    EventNews.tradeLine(r), EventNews.roadLine(r)};
            for (String line : lines) {
                if (line != null && !line.isBlank()) {
                    System.out.println(line.trim());
                }
            }
            r.event().ifPresent(e -> System.out.println(EventNews.rumor(e.event(), year).trim()));
        }
    }
}
