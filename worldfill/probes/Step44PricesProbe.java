// Step 44 part 2 (E4): run Prices.java against the real pack and check it against history.
// The checks are not "did it load"; they are "does it say what the archives say".
import com.eternalengine.money.Prices;
import com.eternalengine.money.Prices.*;

import java.util.List;
import java.util.Optional;

public final class Step44PricesProbe {

    static int fails = 0;
    static int checks = 0;

    static void ok(boolean cond, String what) {
        checks++;
        if (!cond) { fails++; System.out.println("  FAIL  " + what); }
    }

    public static void main(String[] args) {
        Prices p = Prices.get();
        System.out.println(p.summary());

        // ---------------------------------------------------------------- loaded
        ok(p.marketList().size() == 193, "193 markets (got " + p.marketList().size() + ")");
        ok(p.goodList().size() == 89, "89 goods (got " + p.goodList().size() + ")");
        ok(p.shortageCount() == 1225, "1225 shortage years (got " + p.shortageCount() + ")");

        // ---------------------------------------------------------------- no human beings
        boolean hasSlave = p.goodList().stream().anyMatch(g -> g.id().equals("slave"));
        ok(!hasSlave, "the pack prices no human beings");

        // ---------------------------------------------------------------- nearest market
        // Hyderabad has no market within 500 km: the nearest is Allahabad at 960 km. That is the
        // honest answer and a real gap in the source, not a bug -- the Deccan was never surveyed.
        ok(p.marketAt(17.385, 78.487).isEmpty(),
           "the Deccan has no market within 500 km, and says so rather than guessing");
        ok(p.nearestMarket(17.385, 78.487, 1200.0).isPresent(),
           "a market is found near Hyderabad only if you look 1,200 km");
        Optional<Market> florence = p.marketAt(43.770, 11.256);
        ok(florence.isPresent(), "a market is found near Florence");
        ok(florence.isPresent() && florence.get().id().equals("Florence"),
           "Florence resolves to Florence, not " + (florence.isPresent() ? florence.get().id() : "nothing"));
        // the bug this gazetteer exists to prevent: Burgos must not be in the Philippines
        Optional<Market> burgos = p.marketAt(42.340, -3.700);
        ok(burgos.isPresent() && burgos.get().id().equals("Burgos"),
           "Burgos is in Spain (got " + (burgos.isPresent() ? burgos.get().id() : "nothing") + ")");
        Optional<Market> midAtlantic = p.marketAt(0.0, -30.0);
        ok(midAtlantic.isEmpty(), "the mid-Atlantic has no market (500 km limit)");

        // ---------------------------------------------------------------- the Great Famine
        Optional<Reading> famine = p.price("Southern England", "wheat", 1316);
        ok(famine.isPresent(), "southern England priced wheat in 1316");
        ok(famine.isPresent() && famine.get().index() >= 2.0,
           "the Great Famine of 1315-17 reads as a shortage (got "
           + (famine.isPresent() ? famine.get().index() : 0) + ")");
        ok(famine.isPresent() && famine.get().isShortage(), "1316 is flagged a shortage year");

        // ---------------------------------------------------------------- the Black Death
        // Fewer buyers: grain got cheaper. A pack that spikes here has the sign wrong.
        Optional<Reading> plague = p.price("Southern England", "wheat", 1352);
        ok(plague.isPresent() && plague.get().index() < famine.get().index(),
           "grain is cheaper after the Black Death than during the Great Famine");

        // ---------------------------------------------------------------- Kipper und Wipper
        Optional<Reading> leipzig = p.price("Leipzig", "barley", 1622);
        ok(leipzig.isPresent() && leipzig.get().index() >= 5.0,
           "Leipzig barley 1622 shows the inflation (got " + (leipzig.isPresent() ? leipzig.get().index() : 0) + ")");

        // ---------------------------------------------------------------- Tambora, 1816-17
        // The year without a summer: Tambora's dust made 1816 the coldest year in six centuries.
        // At Augsburg it is the barley that spikes, not the wheat.
        Optional<Reading> tambora = p.price("Augsburg", "barley", 1817);
        ok(tambora.isPresent() && tambora.get().index() >= 1.8,
           "Augsburg barley 1817 shows the year without a summer (got "
           + (tambora.isPresent() ? tambora.get().index() : 0) + ")");
        ok(tambora.isPresent() && tambora.get().isShortage(), "1817 is flagged a shortage year");

        // ---------------------------------------------------------------- India survives
        Optional<Market> allahabad = p.marketAt(25.435, 81.846);
        ok(allahabad.isPresent(), "a market is found near Allahabad");
        Optional<Reading> indianWheat = p.priceAt(25.435, 81.846, "wheat", 1861);
        ok(indianWheat.isPresent(), "Allahabad priced wheat in 1861");
        ok(indianWheat.isPresent() && indianWheat.get().measure().equals("Kilogram"),
           "grain is in kilograms everywhere (got "
           + (indianWheat.isPresent() ? indianWheat.get().measure() : "nothing") + ")");
        ok(indianWheat.isPresent() && !indianWheat.get().suspect(),
           "the Indian series is not marked suspect");
        if (indianWheat.isPresent()) {
            System.out.println("        Allahabad wheat 1861: " + indianWheat.get().grams()
                + " g of silver per " + indianWheat.get().measure().toLowerCase());
        }

        // ---------------------------------------------------------------- suspect handling
        Optional<Reading> tuscany = p.price("Tuscany", "wheat", 1347);
        ok(tuscany.isPresent(), "Tuscany priced wheat in 1347");
        ok(tuscany.isPresent() && tuscany.get().suspect(),
           "Tuscany's silver conversion is marked suspect");
        // ...and the index is still usable, which is the entire point
        ok(tuscany.isPresent() && tuscany.get().index() > 0.1 && tuscany.get().index() < 10.0,
           "Tuscany's index is still sane despite the bad conversion (got "
           + (tuscany.isPresent() ? tuscany.get().index() : 0) + ")");

        // ---------------------------------------------------------------- grain is all one unit
        boolean grainOk = p.goodList().stream()
            .filter(g -> g.id().equals("wheat") || g.id().equals("rye") || g.id().equals("barley")
                      || g.id().equals("oats") || g.id().equals("rice"))
            .allMatch(g -> g.measure().equals("Kilogram"));
        ok(grainOk, "every grain is stored in kilograms, so markets can be compared");

        // ---------------------------------------------------------------- out of range
        ok(p.price("Southern England", "wheat", 1950).isEmpty(), "1950 is outside the source");
        ok(p.price("Southern England", "wheat", 800).isEmpty(), "800 is outside the source");
        ok(p.price("Southern England", "electricity", 1700).isEmpty(), "an unknown good gives nothing");
        ok(p.price("Atlantis", "wheat", 1700).isEmpty(), "an unknown market gives nothing");

        // ---------------------------------------------------------------- shortages
        List<Shortage> se = p.shortagesAt("Southern England");
        ok(!se.isEmpty(), "southern England has recorded shortages");
        ok(se.isEmpty() || se.get(0).worst() >= 2.0, "its worst shortage is severe");
        List<Shortage> around1709 = p.shortagesAround(1709, 1);
        ok(!around1709.isEmpty(), "the Great Winter of 1709 is recorded somewhere");
        if (!around1709.isEmpty()) {
            System.out.println("        1709: " + around1709.get(0).sentence());
        }

        // ---------------------------------------------------------------- sentences
        if (famine.isPresent()) System.out.println("        " + famine.get().sentence());
        if (leipzig.isPresent()) System.out.println("        " + leipzig.get().sentence());
        Optional<Reading> ordinary = p.price("Southern England", "wheat", 1500);
        if (ordinary.isPresent()) System.out.println("        " + ordinary.get().sentence());

        System.out.printf("%nprices probe: %d checks, %d failed%n", checks, fails);
        if (fails > 0) System.exit(1);
    }
}
