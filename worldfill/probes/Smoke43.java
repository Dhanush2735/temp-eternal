import com.eternalengine.technology.TechnologyAtlas;
public class Smoke43 {
    public static void main(String[] a) {
        TechnologyAtlas at = TechnologyAtlas.get();
        String[] ids = {"fired_brick", "iron", "steam_engine", "ironworks", "cement",
                        "bessemer", "open_hearth", "gas_light", "kerosene_lamp"};
        Object[][] spots = {{53.48,-2.24,"Manchester"},{41.89,12.49,"Rome"},
            {39.90,116.40,"Beijing"},{28.61,77.21,"Delhi"},{-13.53,-71.97,"Cuzco"},
            {19.43,-99.13,"Tenochtitlan"},{35.68,139.69,"Edo"}};
        System.out.printf("%-14s", "place");
        for (String i : ids) System.out.printf("%11s", i.substring(0, Math.min(10, i.length())));
        System.out.println();
        for (Object[] p : spots) {
            System.out.printf("%-14s", p[2]);
            for (String id : ids) {
                TechnologyAtlas.Tech t = at.tech(id);
                int y = t == null ? -1 : at.arrivalAt(t, (Double) p[0], (Double) p[1]);
                System.out.printf("%11s", y >= TechnologyAtlas.NEVER ? "never" : y);
            }
            System.out.println();
        }
        System.out.println();
        System.out.println("=== share over time at Manchester (how thick the smoke is) ===");
        System.out.printf("%-5s", "year");
        for (String i : new String[]{"ironworks","steam_engine","cement","fired_brick"})
            System.out.printf("%16s", i);
        System.out.println();
        for (int y : new int[]{1700,1750,1800,1850,1900,1950,2000}) {
            System.out.printf("%-5d", y);
            for (String i : new String[]{"ironworks","steam_engine","cement","fired_brick"}) {
                TechnologyAtlas.Tech t = at.tech(i);
                System.out.printf("%16.3f", at.share(t, 53.48, -2.24, y,
                    com.eternalengine.civilization.SettlementRank.CITY));
            }
            System.out.println();
        }
    }
}
