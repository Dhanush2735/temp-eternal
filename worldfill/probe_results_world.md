# World probe: the mod's real occupancy answer (2026-10-11)

HistoricalPresence.query (no civilization manager) on the 400 DensityProbe land points; the compiled mod classes from `gradlew compileJava` plus the resources. Columns name the first layer that answers. Source: `probes/WorldProbe.java`.

```
first query (loads gazetteer, rulers, HYDE): 2.1 s
ruler register: 78388 places, 8725 timelines, 229468 spans from /data/eternalengine/eternal/history/deccan_rulers.json + /data/eternalengine/eternal/history/world_rulers.json.gz
HYDE grid: /data/eternalengine/eternal/population/hyde_density.bin.gz, 28 slices

% of 400 random land points where the mod has someone, by the layer that answers first
   year   place  hinter     box   ruler  people |     ANY ms/query
  -2500    0.5%    2.3%    0.3%    0.0%   11.5% |   14.5%     0.84
  -1500    1.0%    3.0%    0.0%    0.0%   13.3% |   17.3%     0.50
   -500    1.0%    5.3%    0.0%    1.3%   15.5% |   23.0%     0.58
      1    5.8%    6.0%    0.3%    2.8%    9.8% |   24.5%     0.78
    500    5.5%    7.3%    1.5%    4.0%   10.0% |   28.3%     0.89
   1000    1.5%    3.8%    0.0%   10.3%    9.8% |   25.3%     0.58
   1300    1.8%    4.8%    0.5%   11.5%   10.5% |   29.0%     0.86
   1500    2.5%    2.8%    0.5%   13.5%   10.8% |   30.0%     0.76
   1700    2.8%    6.0%    1.3%   13.0%    6.0% |   29.0%     0.72
   1850    2.3%    7.8%    1.3%   16.5%    5.3% |   33.0%     0.77
   1900    3.5%    6.8%    0.0%   25.3%    1.0% |   36.5%     0.85
   1944    2.8%    5.5%    0.0%   29.3%    0.5% |   38.0%     0.72
   2000    3.0%    6.0%    4.0%   30.3%    0.8% |   44.0%     0.68

== Mid-Sahara ==
Year 1000 at lat=23.0000 lon=10.0000 (named site; present map; dated OHM; estimated hinterland; box; ruler; estimated people)
  occupant: none — no sourced site here this year
  -> occupied=false civ=neutral rank=VILLAGE

== Nile valley, Upper Egypt ==
Year -1500 at lat=26.1000 lon=32.7000 (named site; present map; dated OHM; estimated hinterland; box; ruler; estimated people)
  site: pleiades_places/pl_786047 "Kaine/Maximianopolis" 6 km occupied -5000..641 rank=city civHint=egypt_ancient confidence=pleiades
  ruler: New Kingdom of Egypt (new_kingdom_of_egypt) -1500..-801 at cell_26.25_32.75 17 km
  estimated people: ~10 people/km2 (HYDE 3.2.1 population model, 0.5-degree cell, slices -2000..-1000) (unnamed countryside; a population model, not a record)
  border: egypt_nile civ=egypt_ancient -3100..-30 rank=village (approx core, not a surveyed frontier)
  -> occupied=true civ=new_kingdom_of_egypt rank=CITY

== Gaul countryside ==
Year -300 at lat=46.5000 lon=3.0000 (named site; present map; dated OHM; estimated hinterland; box; ruler; estimated people)
  estimated people: ~4.34 people/km2 (HYDE 3.2.1 population model, 0.5-degree cell, slices -1000..0) (unnamed countryside; a population model, not a record)
  -> occupied=true civ=neutral rank=VILLAGE

== Ohio valley ==
Year 1200 at lat=39.0000 lon=-84.0000 (named site; present map; dated OHM; estimated hinterland; box; ruler; estimated people)
  occupant: none — no sourced site here this year
  -> occupied=false civ=neutral rank=VILLAGE

== Amazon ==
Year 1400 at lat=-5.0000 lon=-62.0000 (named site; present map; dated OHM; estimated hinterland; box; ruler; estimated people)
  occupant: none — no sourced site here this year
  -> occupied=false civ=neutral rank=VILLAGE

== Siberia ==
Year 1900 at lat=60.0000 lon=100.0000 (named site; present map; dated OHM; estimated hinterland; box; ruler; estimated people)
  ruler: Russian Empire (russian_empire) 1721..1916 at cell_60.25_100.25 31 km
  no one on this spot this year by the population model: ~0.02 people/km2 (HYDE 3.2.1 population model, 0.5-degree cell, slices 1900); people on about 1% of the land around here
  occupant: none — no sourced site here this year
  -> occupied=false civ=russian_empire rank=VILLAGE

== Mongolian steppe ==
Year 1250 at lat=47.0000 lon=103.0000 (named site; present map; dated OHM; estimated hinterland; box; ruler; estimated people)
  ruler: Mongol Empire (mongol_empire) 1206..1293 at cell_47.25_102.75 33 km
  no one on this spot this year by the population model: ~1.22 people/km2 (HYDE 3.2.1 population model, 0.5-degree cell, slices 1200..1300); people on about 61% of the land around here
  occupant: none — no sourced site here this year
  -> occupied=false civ=mongol_empire rank=VILLAGE

== Rural Poland ==
Year 1600 at lat=52.0000 lon=19.5000 (named site; present map; dated OHM; estimated hinterland; box; ruler; estimated people)
  ruler: Polish-Lithuanian Commonwealth (polish_lithuanian_commonwealth) 1572..1705 at cell_52.25_19.25 32 km
  estimated people: ~17 people/km2 (HYDE 3.2.1 population model, 0.5-degree cell, slices 1600) (unnamed countryside; a population model, not a record)
  -> occupied=true civ=polish_lithuanian_commonwealth rank=VILLAGE

== Congo basin ==
Year 1500 at lat=-2.0000 lon=23.0000 (named site; present map; dated OHM; estimated hinterland; box; ruler; estimated people)
  estimated people: ~2.00 people/km2 (HYDE 3.2.1 population model, 0.5-degree cell, slices 1500) (unnamed countryside; a population model, not a record)
  -> occupied=true civ=neutral rank=VILLAGE

== Australian outback ==
Year 1700 at lat=-25.0000 lon=135.0000 (named site; present map; dated OHM; estimated hinterland; box; ruler; estimated people)
  occupant: none — no sourced site here this year
  -> occupied=false civ=neutral rank=VILLAGE

== Telangana village ==
Year 1900 at lat=18.1800 lon=78.4500 (named site; present map; dated OHM; estimated hinterland; box; ruler; estimated people)
  site: present_kamareddy/aaiahwarpally_18184_78451 "Aaiahwarpally" 0 km occupied 1465..9999 rank=village civHint=india confidence=estimated (estimated year: gravity/diffusion/parent, not a sourced founding) partOf=kamareddy
  ruler: British Raj (british_raj) 1895..1910 at aaiahwarpally_18184_78451 0 km
  estimated people: ~84 people/km2 (HYDE 3.2.1 population model, 0.5-degree cell, slices 1900) (unnamed countryside; a population model, not a record)
  border: nizam_hyderabad_state civ=hyderabad_state 1724..1948 rank=village (approx core, not a surveyed frontier)
  event: gaz_auto_154 "The eff«ct of the famine of 1900 on the birth-rate has already been^ alluded to," 88 km 1900..1901 kind=disaster effect=lockdown (short overlay; not a town; not attacker spawn)
  -> occupied=true civ=british_raj rank=VILLAGE
```
