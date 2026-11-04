import com.eternalengine.civilization.WhoRuled;
import java.util.List;

/** Geneva, asked as a settlement rather than as bare coordinates. */
public final class GenevaProbe {
    public static void main(String[] args) {
        double lat = 46.200d, lon = 6.147d;
        int[] years = {-500, -121, -58, 400, 1200, 1400, 1541, 1798, 1815, 2024};
        System.out.println("Geneva 46.200 / 6.147 - asked as a SETTLEMENT");
        for (int y : years) {
            System.out.printf("  %5d  %s%n", y, WhoRuled.answerForSettlement(List.of(), lat, lon, y).display());
        }
    }
}
