package com.eternalengine.money;

import java.util.Locale;

/**
 * A stand-in for the mod's {@code MarketService}, which cannot be compiled without the Minecraft
 * jars. Step 43 part 5 probes {@code BookForms} (step 22) on a plain JDK, and {@code BookForms}
 * reads exactly four things from this class: the three buyer roles and {@link #buyer(String)}.
 * Everything else in the real class — prices, containers, tags — is absent here on purpose.
 */
public final class MarketService {

    public static final String MERCHANT = "merchant";
    public static final String TRADER = "trader";
    public static final String PEDLAR = "pedlar";

    private MarketService() {
    }

    /** Test double: HistoricalPresence asks for a talk line builder. Returns the lines unchanged. */
    public static String[] withMoneyChanger(String[] lines, double lat, double lon, int year) { return lines; }

    /** Test double, as above. */
    public static String[] withTrader(String[] lines, Object rank, double lat, double lon, int year) { return lines; }

    public static boolean buyer(String role) {
        String r = role == null ? "" : role.toLowerCase(Locale.ROOT);
        return r.equals(MERCHANT) || r.equals(TRADER) || r.equals(PEDLAR);
    }
}
