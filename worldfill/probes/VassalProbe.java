import com.eternalengine.civilization.RulerRegister;
import com.eternalengine.civilization.WhoRuled;
import java.util.List;

/** Why does the vassal rule fire or not fire? */
public final class VassalProbe {
    public static void main(String[] args) {
        RulerRegister rr = RulerRegister.get();
        for (var p : rr.polities()) {
            if (p.name().contains("Legnica") || p.name().contains("Crimean")) {
                System.out.println("polity: '" + p.name() + "'  civHint='" + p.civHint() + "'");
                var ext = rr.extentOf(p.civHint());
                ext.ifPresent(e -> System.out.println("    extent centre " + e.lat() + "," + e.lon()
                        + " places " + e.places() + " years " + e.start() + "-" + e.end()));
                var near = rr.rulerNear(p.civHint(), 51.207, 16.155, 1619);
                System.out.println("    rulerNear(Legnica,1619) = " + near.map(h -> h.ruler() + " @ " + h.distanceKm() + " km").orElse("EMPTY"));
                var near2 = rr.rulerNear(p.civHint(), 46.726, 32.102, 1755);
                System.out.println("    rulerNear(Tavriiske,1755) = " + near2.map(h -> h.ruler() + " @ " + h.distanceKm() + " km").orElse("EMPTY"));
            }
        }
        System.out.println();
        for (int[] c : new int[][] {{51, 1619}, {46, 1755}}) {
            var a = WhoRuled.answer(List.of(), c[0] == 51 ? 51.207 : 46.726, c[0] == 51 ? 16.155 : 32.102, c[1]);
            System.out.println("answer " + c[0] + "/" + c[1] + " -> " + a.display() + "  [" + a.source() + "]");
        }
    }
}
