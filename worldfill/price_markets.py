"""
Step 44 part 2 (E4, prices and wages through time): where each Allen-Unger market is.

The database names **193 markets and gives no coordinates** -- a price series for "Valencia" is
useless to a mod that asks questions by latitude and longitude. So this table places every one.

**It is written by hand, and it had to be.** The obvious shortcut -- matching each market name
against the mod's own `towns.json.gz`, 30,151 towns with coordinates -- was tried first and had to
be thrown away, because a name-only match is not merely imprecise, it is *systematically* wrong for
exactly the countries this database covers best:

    Burgos      ->  Burgos, Philippines        (16.0, 119.9)   not  Burgos, Spain      (42.3, -3.7)
    Valencia    ->  Valencia, Philippines      ( 7.9, 125.1)   not  Valencia, Spain    (39.5, -0.4)
    Zaragoza    ->  Zaragoza, Philippines      (15.4, 120.8)   not  Zaragoza, Spain    (41.7, -0.9)
    Valladolid  ->  Valladolid, Philippines    (10.5, 122.8)   not  Valladolid, Spain  (41.7, -4.7)
    Gerona      ->  Gerona, Philippines                        not  Girona, Spain
    Pamplona    ->  Pamplona, Philippines                      not  Pamplona, Spain
    Tolosa      ->  Tolosa, Philippines                        not  Tolosa, Spain
    Tudela      ->  Tudela, Philippines                        not  Tudela, Spain
    Leon        ->  Leon, Philippines                          not  Leon, Spain
    Andalusia   ->  Andalusia, Alabama         (31.3, -86.5)   not  Andalusia, Spain   (37.5, -4.5)
    Navarre     ->  Navarre, Florida                           not  Navarre, Spain
    Oviedo      ->  Oviedo, Florida                            not  Oviedo, Spain
    Braganca    ->  Braganca, Brazil                           not  Braganca, Portugal
    Nantes      ->  Nantes, Quebec                             not  Nantes, France
    Windsor     ->  Windsor, Ontario                           not  Windsor, England

Three hundred years of Spanish colonial naming means a Spanish price series would silently become
a Philippine one. Every entry below was placed by hand and none of them came from a name match.

`radiusKm` is 0 for a city and the rough radius for a region ("England", "Tuscany", "Wallachia"),
because many of these markets are not towns at all. A region's prices stand for the whole region.

`mark` is "estimated" for a coordinate placed by reading -- which is all of them, since the
database says only the name -- and "recorded" would be a lie.

Run:  python3 price_markets.py        to check the table covers every market in the data
"""

# (market name in the Allen-Unger files, modern name, lat, lon, radiusKm)
MARKETS = [
    ("Aix", "Aix-en-Provence", 43.528, 5.445, 0),
    ("Akyab", "Sittwe", 20.150, 92.900, 0),
    ("Allahabad", "Prayagraj", 25.435, 81.846, 0),
    ("Amsterdam", "Amsterdam", 52.367, 4.883, 0),
    ("Ancona", "Ancona", 43.617, 13.517, 0),
    ("Andalusia", "Andalusia", 37.500, -4.500, 250),
    ("Angers", "Angers", 47.473, -0.556, 0),
    ("Antwerp", "Antwerp", 51.221, 4.400, 0),
    ("Aragon", "Aragon", 41.600, -0.900, 200),
    ("Arequipa", "Arequipa", -16.399, -71.537, 0),
    ("Arezzo", "Arezzo", 43.463, 11.878, 0),
    ("Arles", "Arles", 43.677, 4.628, 0),
    ("Arnhem", "Arnhem", 51.983, 5.917, 0),
    ("Ath", "Ath", 50.631, 3.777, 0),
    ("Augsburg", "Augsburg", 48.369, 10.898, 0),
    ("Avignon", "Avignon", 43.949, 4.808, 0),
    ("Backerganj", "Barisal", 22.701, 90.354, 0),
    ("Balasore", "Balasore", 21.493, 86.934, 0),
    ("Bamo", "Bhamo", 24.250, 97.233, 0),
    ("Bankura", "Bankura", 23.232, 87.010, 0),
    ("Barcelona", "Barcelona", 41.383, 2.177, 0),
    ("Bardwan", "Bardhaman", 23.232, 87.861, 0),
    ("Bari", "Bari", 41.125, 16.867, 0),
    ("Basle", "Basel", 47.561, 7.591, 0),
    ("Bassano", "Bassano del Grappa", 45.767, 11.733, 0),
    ("Bassein", "Pathein", 16.779, 94.732, 0),
    ("Bavay", "Bavay", 50.297, 3.789, 0),
    ("Beijing", "Beijing", 39.904, 116.408, 0),
    ("Benares", "Varanasi", 25.319, 83.013, 0),
    ("Beziers", "Beziers", 43.345, 3.218, 0),
    ("Bilbao", "Bilbao", 43.263, -2.935, 0),
    ("Birbhum", "Birbhum", 23.910, 87.530, 60),
    ("Bogra", "Bogra", 24.847, 89.372, 0),
    ("Bordeaux", "Bordeaux", 44.838, -0.579, 0),
    ("Braganca", "Braganca", 41.806, -6.751, 0),
    ("Bravant", "Brabant", 50.800, 4.600, 80),
    ("Brescia", "Brescia", 45.542, 10.221, 0),
    ("Bruges", "Bruges", 51.209, 3.224, 0),
    ("Brussels", "Brussels", 50.847, 4.352, 0),
    ("Buenos Aires", "Buenos Aires", -34.600, -58.382, 0),
    ("Buis Les Baronnies", "Buis-les-Baronnies", 44.294, 5.274, 0),
    ("Bulgaria", "Bulgaria", 42.700, 25.300, 250),
    ("Burgos", "Burgos", 42.340, -3.700, 0),
    ("Cachar", "Cachar", 24.680, 92.780, 70),
    ("Calcutta", "Kolkata", 22.567, 88.370, 0),
    ("Cantania", "Catania", 37.502, 15.087, 0),
    ("Cervera", "Cervera", 41.667, 1.270, 0),
    ("Chateau Gonier", "Chateau-Gontier", 47.827, -0.702, 0),
    ("Chesapeake", "Chesapeake", 36.767, -76.287, 80),
    ("Chester", "Chester", 53.200, -2.883, 0),
    ("Chittagong", "Chittagong", 22.335, 91.832, 0),
    ("Clarmont-Ferrand", "Clermont-Ferrand", 45.777, 3.082, 0),
    ("Cologne", "Cologne", 50.942, 6.958, 0),
    ("Colombia", "Colombia", 4.600, -74.100, 600),
    ("Copenhagen", "Copenhagen", 55.676, 12.569, 0),
    ("Coutances", "Coutances", 49.045, -1.445, 0),
    ("Dacca", "Dhaka", 23.729, 90.394, 0),
    ("Danzig", "Gdansk", 54.352, 18.646, 0),
    ("Die", "Die", 44.752, 5.370, 0),
    ("Douai", "Douai", 50.371, 3.081, 0),
    ("Draguignan", "Draguignan", 43.540, 6.467, 0),
    ("Dresden", "Dresden", 51.049, 13.738, 0),
    ("Edinburgh", "Edinburgh", 55.953, -3.189, 0),
    ("Edo", "Tokyo", 35.689, 139.692, 0),
    ("England", "England", 52.500, -1.500, 300),
    ("Eton", "Eton", 51.492, -0.609, 0),
    ("Exeter", "Exeter", 50.726, -3.527, 0),
    ("Faridpur", "Faridpur", 23.599, 89.835, 0),
    ("Florence", "Florence", 43.771, 11.254, 0),
    ("France", "France", 46.600, 2.200, 400),
    ("Frankfurt", "Frankfurt", 50.111, 8.682, 0),
    ("Gdansk", "Gdansk", 54.352, 18.646, 0),
    ("Gerona", "Girona", 41.983, 2.824, 0),
    ("Ghent", "Ghent", 51.054, 3.725, 0),
    ("Goalpara", "Goalpara", 26.170, 90.620, 0),
    ("Granada", "Granada", 37.176, -3.600, 0),
    ("Grenoble", "Grenoble", 45.187, 5.726, 0),
    ("Henzada", "Hinthada", 17.650, 95.450, 0),
    ("Herentals", "Herentals", 51.177, 4.836, 0),
    ("Hobart", "Hobart", -42.883, 147.317, 0),
    ("Holstein", "Holstein", 54.200, 9.700, 120),
    ("Hooghly", "Hugli", 22.900, 88.390, 0),
    ("Istanbul", "Istanbul", 41.010, 28.960, 0),
    ("Jessore", "Jessore", 23.170, 89.210, 0),
    ("Kamrup", "Kamrup", 26.330, 91.500, 70),
    ("Konigsberg", "Kaliningrad", 54.717, 20.500, 0),
    ("Krakow", "Krakow", 50.061, 19.937, 0),
    ("Kyaukpyu", "Kyaukpyu", 19.433, 93.550, 0),
    ("Kyoto", "Kyoto", 35.012, 135.768, 0),
    ("La Coruna", "A Coruna", 43.371, -8.396, 0),
    ("Lakhimpur", "Lakhimpur", 27.240, 94.100, 0),
    ("Le Quesnoy", "Le Quesnoy", 50.247, 3.639, 0),
    ("Leiden", "Leiden", 52.160, 4.490, 0),
    ("Leipzig", "Leipzig", 51.341, 12.375, 0),
    ("Leon", "Leon", 42.599, -5.567, 0),
    ("Libau", "Liepaja", 56.508, 21.011, 0),
    ("Lier", "Lier", 51.131, 4.570, 0),
    ("Linkoping", "Linkoping", 58.411, 15.622, 0),
    ("Lisbon", "Lisbon", 38.708, -9.139, 0),
    ("Lleida", "Lleida", 41.617, 0.622, 0),
    ("Lolland", "Lolland", 54.770, 11.320, 50),
    ("Lombardia", "Lombardy", 45.500, 9.800, 150),
    ("Lorca", "Lorca", 37.677, -1.699, 0),
    ("Louvain", "Leuven", 50.877, 4.704, 0),
    ("Lublin", "Lublin", 51.250, 22.567, 0),
    ("Lwow", "Lviv", 49.842, 24.032, 0),
    ("Madrid", "Madrid", 40.417, -3.703, 0),
    ("Maimensing", "Mymensingh", 24.750, 90.400, 0),
    ("Malda", "Malda", 25.004, 88.146, 0),
    ("Malines", "Mechelen", 51.028, 4.480, 0),
    ("Manbhum", "Manbhum", 23.670, 86.530, 70),
    ("Mandalay", "Mandalay", 21.983, 96.084, 0),
    ("Marseilles", "Marseille", 43.296, 5.370, 0),
    ("Maryland", "Maryland", 39.000, -76.800, 150),
    ("Massachusetts", "Massachusetts", 42.300, -71.800, 180),
    ("Mauberge", "Maubeuge", 50.278, 3.972, 0),
    ("Medina", "Medina", 24.470, 39.610, 0),
    ("Metz", "Metz", 49.120, 6.177, 0),
    ("Mexico City", "Mexico City", 19.354, -99.136, 0),
    ("Midnapur", "Medinipur", 22.420, 87.320, 0),
    ("Milan", "Milan", 45.467, 9.190, 0),
    ("Milano", "Milan", 45.467, 9.190, 0),
    ("Modena", "Modena", 44.646, 10.926, 0),
    ("Mons", "Mons", 50.455, 3.953, 0),
    ("Montelimar", "Montelimar", 44.560, 4.750, 0),
    ("Munich", "Munich", 48.138, 11.575, 0),
    ("Nancy", "Nancy", 48.693, 6.184, 0),
    ("Nantes", "Nantes", 47.217, -1.554, 0),
    ("Naples", "Naples", 40.836, 14.249, 0),
    ("Navarre", "Navarre", 42.800, -1.600, 120),
    ("New Castile", "New Castile", 39.800, -3.500, 200),
    ("Old Castile", "Old Castile", 42.000, -4.000, 200),
    ("Osaka", "Osaka", 34.694, 135.502, 0),
    ("Oviedo", "Oviedo", 43.360, -5.844, 0),
    ("Pamplona", "Pamplona", 42.817, -1.644, 0),
    ("Paris", "Paris", 48.857, 2.352, 0),
    ("Pesaro", "Pesaro", 43.911, 12.911, 0),
    ("Pisa", "Pisa", 43.717, 10.400, 0),
    ("Poland", "Poland", 52.000, 19.000, 350),
    ("Porto", "Porto", 41.150, -8.611, 0),
    ("Rennes", "Rennes", 48.111, -1.678, 0),
    ("Rest of England", "the rest of England", 52.900, -1.500, 250),
    ("Rostock", "Rostock", 54.083, 12.133, 0),
    ("Rotterdam", "Rotterdam", 51.920, 4.480, 0),
    ("San Francisco", "San Francisco", 37.775, -122.419, 0),
    ("Sansepolcro", "Sansepolcro", 43.570, 12.140, 0),
    ("Santander", "Santander", 43.464, -3.804, 0),
    ("Santiago", "Santiago", -33.438, -70.650, 0),
    ("Seeland", "Zealand", 55.500, 11.800, 100),
    ("Segovia", "Segovia", 40.948, -4.118, 0),
    ("Senigallia", "Senigallia", 43.712, 13.219, 0),
    ("Shanghai", "Shanghai", 31.233, 121.469, 0),
    ("Siena", "Siena", 43.318, 11.331, 0),
    ("Sopron", "Sopron", 47.683, 16.583, 0),
    ("South Carolina", "South Carolina", 33.900, -80.900, 200),
    ("Southern England", "southern England", 51.200, -1.200, 180),
    ("Speyer", "Speyer", 49.317, 8.434, 0),
    ("St Petersburg", "Saint Petersburg", 59.950, 30.317, 0),
    ("St Polten", "Sankt Polten", 48.204, 15.626, 0),
    ("Stiftklosterneuberg", "Klosterneuburg", 48.303, 16.328, 0),
    ("Stockholm", "Stockholm", 59.329, 18.069, 0),
    ("Strasbourg", "Strasbourg", 48.573, 7.752, 0),
    ("Sydney", "Sydney", -33.868, 151.210, 0),
    ("Thayetmyo", "Thayet", 19.320, 95.180, 0),
    ("Tokyo", "Tokyo", 35.689, 139.692, 0),
    ("Tolosa", "Tolosa", 43.133, -2.083, 0),
    ("Toulouse", "Toulouse", 43.604, 1.443, 0),
    ("Toungoo", "Taungoo", 18.933, 96.433, 0),
    ("Tours", "Tours", 47.393, 0.688, 0),
    ("Tudela", "Tudela", 42.061, -1.605, 0),
    ("Tuscany", "Tuscany", 43.500, 11.200, 150),
    ("Udine", "Udine", 46.067, 13.233, 0),
    ("Utrecht", "Utrecht", 52.091, 5.122, 0),
    ("Valence", "Valence", 44.933, 4.892, 0),
    ("Valencia", "Valencia", 39.470, -0.377, 0),
    ("Valenciennes", "Valenciennes", 50.359, 3.523, 0),
    ("Valladolid", "Valladolid", 41.652, -4.724, 0),
    ("Vermont", "Vermont", 44.100, -72.700, 150),
    ("Vienna", "Vienna", 48.208, 16.372, 0),
    ("Vienne", "Vienne", 45.525, 4.875, 0),
    ("Vitoria", "Vitoria-Gasteiz", 42.847, -2.672, 0),
    ("Voiron", "Voiron", 45.364, 5.593, 0),
    ("Wallachia", "Wallachia", 44.500, 25.500, 250),
    ("Warsaw", "Warsaw", 52.230, 21.011, 0),
    ("Wels", "Wels", 48.150, 14.017, 0),
    ("West Virginia", "West Virginia", 38.600, -80.600, 200),
    ("Weyer", "Weyer", 47.850, 14.650, 0),
    ("Winchester", "Winchester", 51.063, -1.309, 0),
    ("Windsor", "Windsor", 51.483, -0.609, 0),
    ("Wollongong", "Wollongong", -34.433, 150.883, 0),
    ("Wroclaw", "Wroclaw", 51.110, 17.032, 0),
    ("Wurzburg", "Wurzburg", 49.791, 9.953, 0),
    ("Zaragoza", "Zaragoza", 41.652, -0.877, 0),
]


def by_market():
    """{market name in the data: (modern name, lat, lon, radiusKm)}."""
    return {m[0]: (m[1], m[2], m[3], m[4]) for m in MARKETS}


if __name__ == "__main__":
    import os
    import price_table as T
    problems = []
    if len(set(m[0] for m in MARKETS)) != len(MARKETS):
        dupes = [m[0] for m in MARKETS if [x[0] for x in MARKETS].count(m[0]) > 1]
        problems.append("duplicate markets: " + ", ".join(sorted(set(dupes))))
    for name, modern, lat, lon, r in MARKETS:
        if not (-90.0 <= lat <= 90.0):
            problems.append(f"{name}: latitude {lat} is out of range")
        if not (-180.0 <= lon <= 180.0):
            problems.append(f"{name}: longitude {lon} is out of range")
        if r < 0:
            problems.append(f"{name}: radius {r} is negative")
    data = T.DATA
    if os.path.isdir(data):
        have = {f[:-4].rsplit("_", 1)[0] for f in os.listdir(data) if f.endswith(".tab")}
        here = {m[0] for m in MARKETS}
        missing = sorted(have - here)
        extra = sorted(here - have)
        if missing:
            problems.append(f"{len(missing)} markets in the data are not placed: " + ", ".join(missing[:12]))
        if extra:
            problems.append(f"{len(extra)} placed markets are not in the data: " + ", ".join(extra[:12]))
        print(f"markets: {len(MARKETS)} placed, {len(have)} in the data")
    else:
        print(f"markets: {len(MARKETS)} placed (the data is not unpacked at {data})")
    for p in problems:
        print("  PROBLEM " + p)
    print(f"price_markets: {len(problems)} problem(s)")
