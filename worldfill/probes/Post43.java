import com.eternalengine.news.NewsTravel;
import com.eternalengine.technology.TechnologyAtlas;
import com.eternalengine.civilization.CountryGrid;

public class Post43 {
    public static void main(String[] a) {
        TechnologyAtlas at = TechnologyAtlas.get();
        TechnologyAtlas.Tech post = at.tech("post");
        System.out.println("post tech: " + (post == null ? "NULL" : post.id + " first=" + post.first));
        Object[][] spots = {{51.10, 10.30, "Germany"}, {48.86, 2.35, "Paris"},
            {51.51, -0.13, "London"}, {41.89, 12.49, "Rome"}, {34.80, 114.31, "Kaifeng"},
            {43.77, 11.26, "Florence"}, {-13.53, -71.97, "Cuzco"}, {22.57, 88.36, "Calcutta"}};
        for (Object[] s : spots) {
            double lat = (Double) s[0], lon = (Double) s[1];
            System.out.printf("  %-10s cc=%-4s arrivalOf(POST)=%d  arrivalAt(tech)=%d  available(1500)=%s%n",
                s[2], CountryGrid.get().codeAt(lat, lon),
                NewsTravel.arrivalOf(NewsTravel.Mode.POST, lat, lon),
                post == null ? -1 : at.arrivalAt(post, lat, lon),
                NewsTravel.available(NewsTravel.Mode.POST, lat, lon, 1500));
        }
        System.out.println();
        System.out.println("=== BookForms.writing at the check spots ===");
        for (Object[] s : new Object[][]{{41.89, 12.49, 100, "Rome 100"}, {48.86, 2.35, 1900, "Paris 1900"},
            {25.69, 32.64, -1200, "Thebes"}, {39.90, 116.40, 800, "Chang'an"}}) {
            System.out.printf("  %-12s %s%n", s[3],
                com.eternalengine.news.BookForms.writing((Double) s[0], (Double) s[1], (Integer) s[2]));
        }
    }
}
