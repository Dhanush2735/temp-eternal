# Probe results (2026-10-11)

Both runs use the same code (HistoryGazetteer with the latitude skip). The only difference is whether the three places packs are listed.

## Without the places packs
```
gazetteer load: 0.9 s   sites=15954 events=35137 borders=16
  afro_islamic                     11
  americas                         11
  china                             9
  egypt                            11
  indus_harappan                   14
  mediterranean                    12
  mesopotamia                      12
  present_hyderabad_metro        1841
  present_kamareddy               599
  present_telangana             13287
  south_asia                      147

% of 400 random land points where the gazetteer has someone, by year
    year     site  hinterland      box      any  ms/query
   -2500     0.3%        0.3%     0.8%     1.0%      0.26
   -1500     0.3%        0.0%     0.8%     0.8%      0.16
    -500     0.3%        0.5%     0.8%     1.3%      0.16
       1     0.0%        0.8%     2.8%     3.3%      0.16
     500     0.0%        0.3%     1.8%     1.8%      0.16
    1000     0.0%        0.3%     0.0%     0.3%      0.18
    1300     0.0%        0.3%     0.5%     0.8%      0.22
    1500     0.0%        1.3%     0.5%     1.8%      0.25
    1700     0.0%        1.3%     2.0%     2.8%      0.23
    1850     0.0%        1.3%     2.0%     2.5%      0.24
    1900     0.0%        1.3%     0.0%     1.3%      0.26
    1944     0.0%        1.3%     0.0%     1.3%      0.25
    2000     0.0%        1.3%     5.0%     5.3%      0.24
```

## With the places packs
```
gazetteer load: 1.1 s   sites=46864 events=35137 borders=16
  afro_islamic                     11
  americas                         11
  chgis_county_seats            10446
  china                             9
  egypt                            11
  indus_harappan                   14
  mediterranean                    12
  mesopotamia                      12
  pleiades_places               18677
  present_hyderabad_metro        1841
  present_kamareddy               599
  present_telangana             13287
  reba_cities                    1787
  south_asia                      147

% of 400 random land points where the gazetteer has someone, by year
    year     site  hinterland      box      any  ms/query
   -2500     0.5%        2.3%     0.8%     3.0%      0.50
   -1500     1.0%        3.0%     0.8%     4.0%      0.44
    -500     1.0%        5.3%     0.8%     6.3%      0.50
       1     5.8%        6.0%     2.8%    12.0%      0.60
     500     5.5%        7.3%     1.8%    14.3%      0.66
    1000     1.5%        3.8%     0.0%     5.3%      0.59
    1300     1.8%        4.8%     0.5%     7.0%      0.55
    1500     2.5%        2.8%     0.5%     5.8%      0.56
    1700     2.8%        6.0%     2.0%    10.0%      0.53
    1850     2.3%        7.8%     2.0%    11.3%      0.55
    1900     3.5%        6.8%     0.0%    10.3%      0.55
    1944     2.8%        5.5%     0.0%     8.3%      0.53
    2000     3.0%        6.0%     5.0%    13.0%      0.53
```

## Spot checks (SpotProbe)
```
Rome                    100  site "rome" (mediterranean, city, 1 km, -753..1453, civ rome)  [box rome]
Rome                   1600  site "Rome" (reba_cities, city, 1 km, 1500..now, civ naples)
Athens                 -400  site "athens" (mediterranean, city, 1 km, -900..1453, civ athens)
Gaza                  -1200  site "Gaza" (pleiades_places, city, 3 km, -3300..641, civ egypt_ancient)
Trier                   300  site "Vicus Voclannionum" (pleiades_places, town, 4 km, -30..641, civ rome)
Countryside, Gaul       200  site "Margeat" (pleiades_places, town, 16 km, -30..641, civ rome)
Chang'an (Xi'an)        750  site "changan_xian" (china, city, 0 km, -1046..907, civ china_zhou)
Kaifeng                1100  site "kaifeng" (china, city, 0 km, 960..1127, civ china_song)
Rural Sichuan          1500  site "Jian Xian (简县)" (chgis_county_seats, town, 23 km, 1373..1513, civ china_ming)
Beijing                1600  site "beijing" (china, city, 1 km, 1271..1912, civ china_ming)
Paris                  1500  site "Paris" (reba_cities, city, 0 km, 1500..now, civ france)
London                 1700  site "London" (reba_cities, city, 1 km, 1500..now, civ england)
Cairo                  1300  site "cairo_fustat" (afro_islamic, city, 4 km, 641..1517, civ fatimid)
Baghdad                 900  site "baghdad" (afro_islamic, city, 1 km, 762..1258, civ caliphate_abbasid)
Tenochtitlan           1500  site "tenochtitlan" (americas, city, 0 km, 1325..1521, civ aztec)
Cuzco                  1500  site "cusco" (americas, city, 0 km, 1200..1533, civ inca)
Timbuktu               1450  site "timbuktu" (afro_islamic, city, 0 km, 1100..1591, civ mali_empire)
Hyderabad              1700  site "hyderabad" (south_asia, city, 4 km, 1591..now, civ qutb_shahi)  [box maratha]
Telangana village      1900  site "Aaiahwarpally" (present_kamareddy, village, 0 km, 1465..now, civ india)  [box hyderabad_state]
Mid-Sahara             1000  nobody (no site, no hinterland)
Siberia                1000  nobody (no site, no hinterland)
Ohio valley            1200  nobody (no site, no hinterland)
Nile delta village    -1500  estimated countryside village of "Tell el-Moqdam" (pleiades_places, 36 km)  [box egypt_ancient]
```
