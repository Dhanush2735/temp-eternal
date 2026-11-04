import com.eternalengine.knowledge.DatedEvents;
import com.eternalengine.knowledge.KnowledgeDate;
import com.eternalengine.knowledge.NewsIndex;

/**
 * How often is there day-dated news near a player? (R2-7, 2026-10-27)
 *
 * <p>The mechanism being right does not make the feature useful. This measures the thing a player actually
 * experiences: stand somewhere in some year, in the middle of the year, and ask whether there is news that
 * has <b>already happened</b> within hearing - and whether it is dated to the day or only to the year.
 *
 * <p>150 real towns, ten sample years, all reported separately so a thin dataset cannot hide behind an
 * average.
 */
public final class NewsCoverageProbe {
    private static final double[][] TOWNS = {
            {51.207, 16.155},  // Legnica
            {52.520, 13.400},  // Berlin
            {50.060, 19.940},  // Krakow
            {41.010, 28.980},  // Istanbul
            {40.850, 14.270},  // Naples
            {48.857, 2.352},   // Paris
            {51.507, -0.128},  // London
            {41.900, 12.500},  // Rome
            {40.417, -3.704},  // Madrid
            {38.722, -9.139},  // Lisbon
            {52.370, 4.895},   // Amsterdam
            {50.850, 4.352},   // Brussels
            {48.208, 16.373},  // Vienna
            {52.230, 21.011},  // Warsaw
            {50.075, 14.437},  // Prague
            {47.497, 19.040},  // Budapest
            {44.426, 26.103},  // Bucharest
            {43.856, 18.413},  // Sarajevo
            {44.787, 20.448},  // Belgrade
            {41.998, 21.425},  // Skopje
            {37.983, 23.727},  // Athens
            {39.933, 32.859},  // Ankara
            {35.689, 51.389},  // Tehran
            {33.315, 44.366},  // Baghdad
            {31.768, 35.214},  // Jerusalem
            {30.044, 31.235},  // Cairo
            {36.202, 36.160},  // Antakya
            {33.513, 36.292},  // Damascus
            {24.713, 46.675},  // Riyadh
            {21.389, 39.857},  // Mecca
            {15.369, 44.191},  // Sanaa
            {25.204, 55.270},  // Dubai
            {19.076, 72.877},  // Mumbai
            {28.614, 77.209},  // Delhi
            {22.573, 88.364},  // Kolkata
            {13.082, 80.275},  // Chennai
            {17.385, 78.486},  // Hyderabad
            {12.972, 77.594},  // Bengaluru
            {26.912, 75.787},  // Jaipur
            {25.318, 82.973},  // Varanasi
            {27.717, 85.324},  // Kathmandu
            {23.810, 90.412},  // Dhaka
            {16.866, 96.195},  // Yangon
            {13.756, 100.501}, // Bangkok
            {17.975, 102.633}, // Vientiane
            {11.556, 104.928}, // Phnom Penh
            {21.028, 105.854}, // Hanoi
            {10.823, 106.630}, // Ho Chi Minh City
            {1.352, 103.820},  // Singapore
            {-6.208, 106.846}, // Jakarta
            {3.139, 101.687},  // Kuala Lumpur
            {14.600, 120.984}, // Manila
            {35.689, 139.692}, // Tokyo
            {34.694, 135.502}, // Osaka
            {37.567, 126.978}, // Seoul
            {39.904, 116.407}, // Beijing
            {31.230, 121.474}, // Shanghai
            {22.320, 114.174}, // Hong Kong
            {23.129, 113.264}, // Guangzhou
            {30.572, 104.066}, // Chengdu
            {34.342, 108.940}, // Xi'an
            {43.817, 125.324}, // Changchun
            {55.756, 37.617},  // Moscow
            {59.934, 30.336},  // St Petersburg
            {50.450, 30.523},  // Kyiv
            {46.482, 30.723},  // Odesa
            {49.993, 36.230},  // Kharkiv
            {53.900, 27.567},  // Minsk
            {56.949, 24.105},  // Riga
            {54.687, 25.280},  // Vilnius
            {59.437, 24.754},  // Tallinn
            {60.170, 24.941},  // Helsinki
            {59.329, 18.069},  // Stockholm
            {59.913, 10.752},  // Oslo
            {55.676, 12.568},  // Copenhagen
            {64.147, -21.942}, // Reykjavik
            {53.350, -6.260},  // Dublin
            {55.953, -3.188},  // Edinburgh
            {53.483, -2.244},  // Manchester
            {45.501, -73.567}, // Montreal
            {43.653, -79.383}, // Toronto
            {49.283, -123.121},// Vancouver
            {40.713, -74.006}, // New York
            {39.952, -75.165}, // Philadelphia
            {38.907, -77.037}, // Washington
            {41.878, -87.630}, // Chicago
            {29.760, -95.370}, // Houston
            {34.052, -118.244},// Los Angeles
            {37.775, -122.419},// San Francisco
            {25.762, -80.192}, // Miami
            {19.433, -99.133}, // Mexico City
            {14.634, -90.507}, // Guatemala City
            {9.928, -84.091},  // San Jose CR
            {8.983, -79.517},  // Panama City
            {4.711, -74.072},  // Bogota
            {10.480, -66.904}, // Caracas
            {-0.181, -78.467}, // Quito
            {-12.046, -77.043},// Lima
            {-16.500, -68.150},// La Paz
            {-33.449, -70.669},// Santiago
            {-34.604, -58.382},// Buenos Aires
            {-34.901, -56.164},// Montevideo
            {-23.551, -46.633},// Sao Paulo
            {-22.907, -43.173},// Rio de Janeiro
            {-15.794, -47.883},// Brasilia
            {6.524, 3.379},    // Lagos
            {5.560, -0.205},   // Accra
            {14.693, -17.448}, // Dakar
            {12.639, -8.003},  // Bamako
            {13.512, 2.112},   // Niamey
            {15.500, 32.560},  // Khartoum
            {9.030, 38.740},   // Addis Ababa
            {-1.292, 36.822},  // Nairobi
            {-6.792, 39.208},  // Dar es Salaam
            {-4.442, 15.266},  // Kinshasa
            {-8.839, 13.289},  // Luanda
            {-25.969, 32.573}, // Maputo
            {-26.204, 28.047}, // Johannesburg
            {-33.925, 18.424}, // Cape Town
            {-17.825, 31.053}, // Harare
            {-15.387, 28.323}, // Lusaka
            {36.753, 3.059},   // Algiers
            {33.573, -7.590},  // Casablanca
            {34.021, -6.836},  // Rabat
            {36.807, 10.181},  // Tunis
            {32.887, 13.191},  // Tripoli
            {24.687, 46.721},  // Riyadh (dup ok)
            {-18.141, 178.442},// Suva
            {-36.848, 174.763},// Auckland
            {-33.869, 151.209},// Sydney
            {-37.814, 144.963},// Melbourne
            {-27.470, 153.026},// Brisbane
            {-31.953, 115.857},// Perth
            {-12.463, 130.846},// Darwin
            {35.280, 149.130}, // Canberra
            {1.290, 103.851},  // Singapore (dup)
            {-8.556, 125.560}, // Dili
            {-3.320, 114.590}, // Banjarmasin
            {7.073, 125.613},  // Davao
            {16.402, 120.596}, // Baguio
            {26.223, 50.588},  // Manama
            {25.286, 51.531},  // Doha
            {29.376, 47.977},  // Kuwait City
            {23.588, 58.408},  // Muscat
            {33.684, 73.048},  // Islamabad
            {31.549, 74.343},  // Lahore
            {24.861, 67.001},  // Karachi
            {34.530, 69.166},  // Kabul
            {38.560, 68.773},  // Dushanbe
            {41.299, 69.240},  // Tashkent
            {43.238, 76.945},  // Almaty
            {47.886, 106.906}, // Ulaanbaatar
    };

    private static final int[] YEARS = {-500, -100, 100, 500, 1000, 1200, 1400, 1500, 1600, 1700, 1750, 1800,
            1815, 1850, 1870, 1900, 1914, 1939, 1945, 1960, 1980, 2000, 2020};

    public static void main(String[] args) {
        var d = DatedEvents.get();
        System.out.println(d);
        System.out.println();
        int total = 0, datedToday = 0, yearOnly = 0, none = 0;
        java.util.Map<Integer, int[]> byYear = new java.util.TreeMap<>();
        for (int y : YEARS) {
            int day = 0, yonly = 0, nil = 0;
            int mid = KnowledgeDate.key(y, 6, 15);
            for (double[] t : TOWNS) {
                var on = NewsIndex.onDay(t[0], t[1], mid);
                total++;
                if (on.isEmpty()) {
                    nil++;
                    none++;
                } else if (on.get().dated()) {
                    day++;
                    datedToday++;
                } else {
                    yonly++;
                    yearOnly++;
                }
            }
            byYear.put(y, new int[] {day, yonly, nil});
        }
        System.out.printf(java.util.Locale.ROOT, "%-8s %10s %10s %10s    %s%n",
                "year", "day-dated", "year-only", "no news", "day-dated share");
        for (var e : byYear.entrySet()) {
            int[] v = e.getValue();
            int n = v[0] + v[1] + v[2];
            System.out.printf(java.util.Locale.ROOT, "%-8d %10d %10d %10d    %5.1f%%%n",
                    e.getKey(), v[0], v[1], v[2], n == 0 ? 0 : 100.0 * v[0] / n);
        }
        System.out.println();
        System.out.println("town-years asked        : " + total);
        System.out.println("day-dated news found    : " + datedToday + pct(datedToday, total));
        System.out.println("year-only news found    : " + yearOnly + pct(yearOnly, total));
        System.out.println("no news at all          : " + none + pct(none, total));
    }

    private static String pct(int n, int d) {
        return d == 0 ? "" : String.format(java.util.Locale.ROOT, "  (%4.1f%%)", 100.0 * n / d);
    }
}
