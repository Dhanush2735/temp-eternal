import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Supplier;

/**
 * Step 26 (I6): how much memory and load time each data register takes. Each register is loaded on its own,
 * in the order the game loads them; the heap is measured after full garbage collections before and after.
 * Usage: probe_memory.sh
 */
public final class MemoryProbe {
    private static long used() {
        Runtime rt = Runtime.getRuntime();
        long best = Long.MAX_VALUE;
        for (int i = 0; i < 4; i++) {
            System.gc();
            try { Thread.sleep(60); } catch (InterruptedException ignored) { }
            best = Math.min(best, rt.totalMemory() - rt.freeMemory());
        }
        return best;
    }

    public static void main(String[] args) {
        Map<String, Supplier<Object>> regs = new LinkedHashMap<>();
        regs.put("HistoryGazetteer (places, events)", com.eternalengine.civilization.HistoryGazetteer::get);
        regs.put("RulerRegister (who rules)", com.eternalengine.civilization.RulerRegister::get);
        regs.put("LeaderRegister (heads, faiths)", com.eternalengine.civilization.LeaderRegister::get);
        regs.put("FamousPeople", com.eternalengine.civilization.FamousPeople::get);
        regs.put("CardStore.events (event cards)", () -> {
            // step 28: the compressed event file and its index
            var c = com.eternalengine.knowledge.CardStore.events();
            c.indexSize();
            return c;
        });
        regs.put("OccupiedLands (occupations, disputes)", com.eternalengine.civilization.OccupiedLands::get);
        regs.put("TownFacts (towns through time)", com.eternalengine.civilization.TownFacts::get);           // step 29
        regs.put("StateRelations (ties between states)", com.eternalengine.civilization.StateRelations::get); // step 29
        regs.put("CountryGrid (countries of today)", com.eternalengine.civilization.CountryGrid::get);        // step 30a
        regs.put("TechnologyAtlas (technologies)", com.eternalengine.technology.TechnologyAtlas::get);        // step 30a
        regs.put("CultureAtlas (reading, measures, holy places)", com.eternalengine.civilization.CultureAtlas::get); // 30b
        regs.put("CardStore (knowledge cards)", () -> {
            // step 27: the compressed card file, its index and its names (tiles open later, inside the tile budget)
            var c = com.eternalengine.knowledge.CardStore.get();
            c.indexSize();
            c.byName("Akbar");
            return c;
        });
        regs.put("LocalLanguages", com.eternalengine.civilization.LocalLanguages::get);
        regs.put("HydeGrid (people per km2)", com.eternalengine.population.HydeGrid::get);
        regs.put("PopulationResolver", com.eternalengine.population.PopulationResolver::get);
        regs.put("WaysOfLife", com.eternalengine.civilization.WaysOfLife::get);
        regs.put("TradeRoutes", com.eternalengine.civilization.TradeRoutes::get);
        regs.put("MoneyTable", com.eternalengine.money.MoneyTable::get);
        regs.put("GoodsTable", com.eternalengine.money.GoodsTable::get);
        regs.put("ProductAtlas", com.eternalengine.money.ProductAtlas::get);
        long base = used();
        System.out.printf("baseline heap %.1f MB%n", base / 1048576.0);
        long total = 0, totalMs = 0;
        for (Map.Entry<String, Supplier<Object>> e : regs.entrySet()) {
            long before = used();
            long t0 = System.nanoTime();
            Object o = e.getValue().get();
            long ms = (System.nanoTime() - t0) / 1_000_000;
            long after = used();
            long d = Math.max(0, after - before);
            total += d; totalMs += ms;
            System.out.printf("%-36s %7.1f MB %6d ms   %s%n", e.getKey(), d / 1048576.0, ms, o == null ? "null" : "loaded");
        }
        System.out.printf("%-36s %7.1f MB %6d ms%n", "TOTAL", total / 1048576.0, totalMs);
        System.out.printf("heap now %.1f MB (max %.0f MB)%n", used() / 1048576.0, Runtime.getRuntime().maxMemory() / 1048576.0);
    }
}
