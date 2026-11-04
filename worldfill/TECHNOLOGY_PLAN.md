# Technology across places and years: what is the same, what differs, what the mod has, what is missing (turn 94, 2026-10-14)

The user: "i mean technology and improving technology across many location and year".

## 1. How technology works on the real Earth

- **It starts somewhere.** A technology is invented in one place, or in several places on their own (iron was worked
  in Africa independently of the Near East).
- **It spreads at different speeds:** along trade routes, by conquest, and with migrants and monks. The gaps between
  places are centuries before 1500, and years to decades after 1800.
- **It never arrives everywhere at once.** Cities and the rich get it first, towns later, villages last.
- **It improves in steps**, and each new version slowly replaces the old one (bullock cart → horse carriage → railway
  → car). Old versions stay longest in villages.
- **It can stop or be lost:** whole regions had no contact (the Americas before 1492), and collapses sometimes lost
  skills.

**What is the same in many places:** by 3000 BC farming, fire, pottery, weaving, houses, boats and simple tools are
found in most settled lands. Their forms differ (crops, house types, boat types). After 1800 the same machines spread
everywhere (railways, electricity, telephones), but with long delays.

**What differs:** the year a technology arrives, which version a place has, and how common it is there.

### Examples

| Technology | First | Spread |
|---|---|---|
| Wheel | Mesopotamia about 3500 BC, as a potter's wheel; on carts about 300 years later | Americas before Europeans: only on toys |
| Iron | widespread in the Near East from about 1200 BC | India: iron tools at Malhar 1800–1200 BC; Africa started on its own; Northern Europe about 500 BC; Americas: none before 1492 |
| Paper | China, reported to the emperor in AD 105 | India in the 7th century (through Tibet and Nepal); Samarkand 751; Baghdad's first paper industry 793; Europe's first paper mill 1150 |
| Gunpowder | China, 9th century | Middle East 1240–1280; Europe by 1267 |
| Printing press | Gutenberg, about 1440 | presses in 200+ European cities by 1500; India (Goa) 1556, the first in Asia |
| Railway | England 1825 | India: Bombay–Thane, 16 April 1853 |

## 2. What the mod has now

| Part | What it does | Verdict |
|---|---|---|
| Technology engine (old code, on by default) | 7 technologies (agriculture, writing, steel, printing press, steam power, electricity, computing) in 6 eras, per civilization; it unlocks the next one whenever a civilization's people and treasury are big enough | **Not real.** It knows no dates, so a big empire can reach "computing" within a few cycles in any year. Today only commands and the codex screen show it (no event uses it), so it is harmless but tells nothing true. |
| Vehicle eras (old code) | 4 world-wide eras; trains, steamships and cars allowed from 1500 | **Wrong:** cars from 1500, and horses in the Americas before 1493 |
| Medicine (old code) | world-wide steps at 500, 1450, 1800 and 1945 | the same everywhere |
| Money table (data) | money by place and year: weighed silver in Mesopotamia from 2600 BC, coins from about 600 BC by region | **Real**, by place |
| News eras (data) | crier, handwritten newsletter or printed paper by region and year; towns get print 50 years after cities | **Real-ish:** a small spread rule |
| Product atlas (data) | 132 products by area and years (step 22 added three writing materials) | real, but goods only |
| Clothes (skins) | looks by era and region | partly |
| Terra++ | buildings and roads by their dates; one world-wide rule "no railways before 1825"; the ground under today's cities follows one world-wide timetable | one rule for the whole world |

## 3. What is missing

- **One technology timeline for every place.** For each technology:
  - when it reached each region;
  - how common it was in each year (cities, towns, villages);
  - which version was in use;
  - when it was lost.
- **Most technologies.** The engine has 7; the real list runs to hundreds, in about 16 fields:
  - farming and food, water and irrigation, building, metals, energy;
  - land transport, water transport, communication, writing, money, war;
  - medicine, textiles, chemistry, lighting, timekeeping, computing.
- **The links.** Vehicles, weapons, buildings, tools, crafting, jobs, goods, medicine, news, lights and sounds should all
  ask the same timeline. Today each has its own rule, or none.
- **Changes by players.** Bringing a technology early should create a new timeline where it spreads by the same rules
  (requirement 5). Things from the future should add paradox stress (requirement 6).

## 4. The plan: a technology atlas (like the product atlas)

**What each technology records:**
- name, field, what it needs first, and its versions with years (the improvement chain);
- where and when it started (several origins allowed);
- for every region: the year it arrived, and how fast it became common (the years to 10%, 50% and 90%), cities first
  and villages last;
- losses (region and year);
- what it changes in the game: blocks, items, recipes, vehicles, building styles, jobs, goods, weapons, medicine, the
  kind of news, lights;
- a mark saying "recorded" or "estimated".

**Where the facts come from:**
- **Wikipedia** first: the "history of …" article of each technology (turn 12).
- **CHAT:** 104 technologies in 161 countries, 1800–2008 (public domain).
- **Primitive technology** (Comin, Easterly and Gong): which technologies each land had in 1000 BC, AD 0 and 1500, in
  farming, transport, communication, military and industry.
- **Wikidata is thin here.** 126,620 items have a discovery or invention date, but many of them are stars and
  asteroids. Only 1,699 are technologies, tools, devices, vehicles, machines or weapons, and only 606 items name a
  country of origin.
- **Seshat's war technology** by state and century, only if the mod stays free (it forbids commercial use).
- **The mod's own data:** the money table, the product atlas, the news eras and `WEAPONS_RESEARCH.md`.

**Where the record says nothing (estimates, marked):**
- Arrival = the nearest neighbour's arrival + distance ÷ the era's speed (slow before 1500, fast after 1800).
- Faster along trade routes and through ports.
- No crossing of oceans before contact: nothing reaches the Americas before 1492, or Australia before 1788.

**How a place improves:**
- each version spreads along its own curve and pushes the older one out;
- cities change first, and villages keep the old way longest.

**The question every system asks:** "which technology is here, at this date, in this timeline; how common is it, and
which version?" This is the key A1 from `SYSTEMS_PLAN.md`.

**What replaces what:**
- the atlas replaces the old technology engine;
- it also replaces the world-wide vehicle eras, the medicine steps and the "1825" railway rule;
- news eras and the money table stay, and are linked to the atlas.

**Size:** start with about 150 technologies (those the game shows: vehicles, weapons, tools, building, media, medicine,
lights, money), then grow to about 500.

**Checks in `/ee check all`:**
- Hyderabad 1948: railway yes, cars yes (few), radio yes, television no.
- Hyderabad 1500: paper yes, printing no.
- Cusco 1500: iron no, carts no, horses no.
- London 1700: printing yes, steam engines in use no.
- Beijing 1100: printing yes, gunpowder yes.

**Place in the order of work:**
- step 30 is split: **30a the technology atlas**, then 30b economy, faiths and languages;
- the later steps that need it read it: old towns (33), roads and industry (34), armies (40), weapons (45),
  vehicles (46), tools (47);
- changing history (48–50) uses the same spread rules.

**A small fix now (optional, with step 21):** until the atlas exists, the old engine never unlocks a technology before
its real date.

## 5. Done in step 30a (turn 108)

- **The atlas:** `history/technology_atlas.json.gz`, 130 technologies in the 16 fields above, the year each reached
  each of 258 countries: 3,499 recorded by hand from Wikipedia (`worldfill/technology_table.py`), 226 from CHAT, the
  rest estimated by the rules of part 4 (era speeds, contact years, closed lands, "not before" years, needs), marked.
  Losses and versions (what replaces what) are in it. `worldfill/README.md`, step 30a, has the details.
- **Where:** `history/countries.grid.gz`, the country of any point (Natural Earth, 0.1 degrees).
- **The question every system asks:** `TechnologyAtlas.present / share / arrivalAt (tech, lat, lon, year, rank)`.
- **The five checks of part 4** are in `/ee check all` (part 19) and pass.
- **Linked so far:** the talk ("What new things are there here?"), vehicles (the fastest travel by place), Terra++'s
  infrastructure by place (ready; Terra++ does not call it yet).
- **Not done (honest):** the primitive-technology data of Comin, Easterly and Gong holds only sector averages (no single
  technologies), so it is not used; Wikidata was not needed. The old engine, the medicine steps, buildings, weapons,
  tools and recipes are linked in their own steps (`SYSTEMS_PLAN.md` part 8, problems 61-66).

## Changes to this file

- Turn 94 (2026-10-14): written.
- Turn 108 (2026-10-15): part 5 added (step 30a done).
