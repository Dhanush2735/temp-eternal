# Product atlas plan: which products exist in every place and year, and how

Written 13 Oct 2026, after: "what are the products from every location and year, you are planning to add in the project. what are your plans on adding product lifecycle products or its journey products or requirement products of every location and year?"

This is a plan only. Nothing in the mod was changed.

- Sources are for design only: no source names appear in the game.
- "(check)" marks general knowledge that still needs a source check before it goes into data.

---

## 1. What the question asks (three kinds of products)

| Kind | Meaning | Example |
|---|---|---|
| **Life products** | Products that appear, spread and fade with time. Each has a birth year (per region), a common period, and a successor that replaces it. | oil lamp → kerosene lamp → electric bulb; palm leaf → paper; matchlock → flintlock → rifle |
| **Journey products** | The products in between, from the raw material to the finished thing. | cotton → yarn → cloth → dyed cloth → shirt; iron ore → iron → steel → blade → sword |
| **Requirement products** | What a product needs before it can exist or be used: inputs, tools, fuel, workplace, know-how, season, climate, permits. It also covers what **people** need: food, clothes, shelter, light, fuel, tools, medicine, faith, fun. | gunpowder needs saltpetre + sulphur + charcoal; a gun needs gunpowder + a licence; bronze needs copper + tin, often from far apart |

The plan covers all three for **every place and year**, not only the newspaper and the map.

---

## 2. The plan in one picture

```
ONE WORLD PRODUCT LIST (about 400 kinds, in 14 families)
        |
        v
"IS IT HERE?" check for any place + year
   nature (raw material nearby?) + know-how (invented and spread here yet?)
   + trade (brought by a route?) + people (who needs it, who can pay?)
        |
        v
answer: MADE HERE / BROUGHT FROM FAR (dearer) / NOT HERE YET / GONE (replaced)
        |
        v
JOURNEY + REQUIREMENTS: who makes it, from what, where, how it travels,
who sells it, what it needs, how it ends
        |
        v
PRICE in days of work x scarcity (season, distance, war, blockade)
        |
        v
IN THE GAME: item you can hold / item with a local name / background good
```

### What the mod already has for this

| Already in the mod | Used for |
|---|---|
| **146 world regions** with their outlines, each saying how people lived from 8050 BC to AD 1850: foraging, farming, herding, cities (`ways_of_life.json.gz`) | The regions products belong to. No farming means no grain market. No city means no workshops. |
| 1,544 states by place and year (`world_rulers`) | Laws, money, who rules (licences, bans) |
| Dated towns (cities 3700 BC–AD 2000, ancient places, Chinese county seats) | Where workshops and markets can be |
| Roads and trade routes with years | Whether a product can be **brought** |
| Crops by region (rice, wheat and barley …), famine | Grain products and their failures |
| 7 transport kinds with speeds (foot, donkey, caravan, ship, train, truck, air); caravans and ships with cargo | How products travel, and how fast |
| Wars, events, classes | Disruptions and who can afford what |

---

## 3. The product card (one per product kind)

| Field | Example (gunpowder) |
|---|---|
| name, family, local names | Gunpowder; weapons; *barud* (check) |
| **life**: origin, first year per region, common from, replaced by | China 9th century → Europe and the Middle East 1300s → India 1300s–1500s; replaced by smokeless powder in the 1880s+ (check) |
| **made from** (journey inputs) | saltpetre + sulphur + charcoal |
| **made by, where** | powder maker; powder works (needs water, fire safety) |
| **needs** (requirements) | saltpetre source (Bihar was the main one 1600–1850), sulphur (often brought from far), know-how |
| **used for** (which need it fills) | guns, cannon, fireworks, mining |
| **travels by** | cart, caravan, ship; dangerous cargo |
| **sold by, where** | arsenal, gunsmith, black market where banned |
| **laws** | licence or ban (from the state table) |
| **wear and end** | spoils when damp; burned when used |
| **in the game** | item (gun mods' powder) or background good |
| **price** | days of work x scarcity |

---

## 4. The world product list: 14 families (first sketch, about 100 of the planned 400)

Years are approximate first appearances and must be checked before they go into data.

| Family | Products, with their life (birth → spread → replaced) |
|---|---|
| 1. **Staple food** | wheat and barley (Near East, very early); rice (China, India); millets and jowar; maize (the Americas; elsewhere only after 1492); potato (the Andes; India 1600s+, common later); flatbread and roti; bread from bakeries (towns) |
| 2. **Other food and drink** | jaggery and crystal sugar (India, early centuries AD; a luxury in Europe until the 1700s); beer (Mesopotamia ~3000 BC); wine; toddy (palm); tea (China; a daily drink in India only in the 1900s); coffee (Yemen 1400s); chillies (the Americas; India 1500s); spices (pepper from India) |
| 3. **Animals and animal goods** | cattle, sheep, goats; horses (steppe ~3500 BC); camels; elephants; milk and ghee; wool; leather; silk (China, very old); pearls |
| 4. **Cloth and clothes** | cotton (Indus, very early); linen; wool; silk; dyes (indigo from India); ikat; mill cloth (1800s+); nylon (1930s+) |
| 5. **Building** | mud brick; fired brick (Indus); stone; timber; lime mortar; Roman concrete; Portland cement (1824+); glass windows; steel beams (1800s+) |
| 6. **Fuel and light** | firewood, charcoal, dung cakes; oil lamps (sesame, castor); candles; coal (common 1700s+; Singareni from 1889); kerosene (1850s+); electricity (1880s+); petrol (1900s+) |
| 7. **Metals and tools** | copper (~5000 BC); bronze (~3300 BC); iron (~1200 BC); steel (South Indian wootz); ploughs, axes, sickles; machines (1800s+) |
| 8. **Weapons and armour** | as in `WEAPONS_RESEARCH.md`: stone and wood → bronze → iron → early guns → matchlock → flintlock → rifles → modern; armour fades after guns |
| 9. **Transport** | on foot; donkey; ox cart (the wheel ~3500 BC); horse; camel caravan; boats and ships; railway (Britain 1825, India 1853); bicycle (1880s); car (1886); truck and bus; aeroplane (1903, air travel 1920s+) |
| 10. **Writing and knowledge** | clay tablets (~3200 BC); papyrus; palm leaf (South India); birch bark (North India); parchment; paper (China ~AD 105; India 1000s–1200s); printed books (1450s; India 1556); newspapers (1605; India 1780); maps; telegraph (India 1850s); radio (1920s); TV (India 1959); internet (1990s) |
| 11. **Money** | barter; weighed silver; coins (~600 BC); paper money (China 1000s; Hyderabad 1918); bank notes; digital |
| 12. **Medicine and care** | herbs (Ayurveda, Unani); quinine; smallpox vaccine (1796; India 1802); penicillin (1940s) |
| 13. **Luxury, faith and fun** | gems (Golconda diamonds), pearls; perfume (*attar*); betel leaf (*paan*); tobacco (the Americas; India ~1600); incense; religious objects; chess (India, ~6th century); playing cards (*ganjifa*) |
| 14. **Papers and permits** (requirement products) | trade passes (*dastak*); land deeds; railway tickets (India 1853+); weapon licences (India 1878+); passports (1920s+); ration cards (India 1940s) |

---

## 5. "Is it here?": the four checks for any place and year

| Check | Question | Data |
|---|---|---|
| **Nature** | Does the raw material exist here? Does the crop grow in this climate? | Crop origins (151 crops, 23 regions of origin) [D3]; mineral deposits (to find); the mod's crops by region and ways of life |
| **Know-how** | Was it invented, and had it spread here by this year? | Origin + first year per region + spread speed. Anchors from Wikipedia's invention timelines; the weapons research; the Columbian exchange (crops crossing the Atlantic after 1492) |
| **Trade** | If it is not made here, does a road or sea route bring it? | The mod's trade routes and roads. Distance and transport speed make it dearer and rarer |
| **People** | Who needs it here, and who can pay? | Classes, town size, faith rules (food and drink), laws (bans, licences) |

**Answers:**
- **MADE HERE:** normal price, sold by local makers.
- **BROUGHT FROM FAR:** dearer, sold only by merchants, sometimes missing.
- **NOT HERE YET:** nobody has heard of it.
- **GONE:** replaced by its successor (old stock may remain).

After a **fork**, rulers, wars and routes change, so supply chains change too.

---

## 6. Journeys and requirements: example chains

| Product | Journey (inputs → steps → product) | Requirements |
|---|---|---|
| Bread | wheat → mill → flour → dough → oven | wheat growing nearby or brought; fuel; a baker in town (villages make roti at home) |
| Cotton cloth | cotton → ginning → spinning wheel → loom → dyeing (indigo) → tailor | warm climate for cotton; dye plants; weavers |
| Bronze sword | copper + tin → bronze → casting → smith | copper and tin, often far apart, so trade is needed; charcoal |
| Gunpowder | saltpetre + sulphur + charcoal → powder works | saltpetre (Bihar), sulphur (often brought from far), know-how |
| Newspaper (1948) | news (reporters, telegraph) → *katib* writes the pages → press → hawkers | newsprint (to check: India's first newsprint mill came in the 1950s, so paper may be brought from far), ink, a press, censors' rules |
| Map | survey → drawing → engraving or litho → printing → seller | survey office (India 1767+), printing press, paper |
| Coins | silver or copper → mint → treasury → markets | metal, a mint, a ruler's die; a money-changer checks them |

**The player can join any step:** grow, carry, make, sell, or buy finished goods.

---

## 7. What the player sees (three levels)

| Level | How many | What |
|---|---|---|
| **Items you can hold** | about 100–150 | Normal Minecraft items (wheat, bread, iron, paper, wool …), mod items (weapons, food mods), and our own key items (newspaper, map, coins, licence) |
| **Items with a local name** | many | A normal item with a local name and look. Paper becomes a "palm-leaf book" before paper; the wine item becomes "toddy" in Telangana. Cheap to add, and covers many products |
| **Background goods** | the rest | Only in the economy: villagers make and use them, shops list them, the news mentions shortages |

---

## 8. Examples: what you would find in different places and years

### Indus city (Harappa), 2500 BC
- **Made here:** wheat and barley, cotton cloth, fired bricks, clay pots, copper and bronze tools, carnelian beads, stone weights, seals.
- **Brought from far:** lapis lazuli (Afghanistan); tin (check).
- **Not here yet:** iron, coins, paper, crystal sugar, chillies, tea.

### Rome, AD 100
- **Made here:** bakery bread, wine, olive oil, fish sauce, blown glass, iron tools, wool clothes, concrete, coins.
- **Brought from far:** pepper (India), silk (China, through traders), papyrus (Egypt), grain (Egypt).
- **Not here yet:** paper, sugar (only as medicine), gunpowder, potatoes, coffee, tea.

### Golconda / Hyderabad area, 1650
- **Made here:** diamonds (Kollur mine), rice and jowar, toddy, betel leaf; painted cotton cloth for export (check); steel (check).
- **Brought from far:** horses (Persia, Arabia; check); chillies and tobacco (the Americas, via the Portuguese).
- **Not here yet:** newspapers (1780), tea as a daily drink, railways, potatoes as common food.

### London, 1850
- **Made here:** newspapers, gas light, steam engines, beer, bread.
- **Brought from far:** tea (China; India from the 1840s, check), sugar (the Caribbean), cotton (the USA, for the mills).
- **Not here yet:** electric light (1880s), telephone (1876), cars (1886), plastic.

### Hyderabad, 1948
- **Made here:**
  - handwritten Urdu newspapers;
  - Osmania biscuits and Irani tea;
  - toddy;
  - gongadi blankets;
  - Singareni coal;
  - checked later: cigarettes, pearls, mill cloth.
- **Brought from far:** kerosene, petrol, radios, rifles (secret flights), newsprint (check).
- **Not here yet:** TV, common plastic goods, Pochampally ikat as a famous product (1950s).

### Hyderabad, 2026
- **Made here:** medicines, software services, biryani, pearls, ikat (check).
- **Brought from far:** phones, petrol, gold.
- **Gone:** handwritten newspapers (late 1980s), the Hyderabad rupee (1959), horse carts.

---

## 9. Data sources and their limits

| Source | What it gives | Limit |
|---|---|---|
| Wikipedia (primary, by the user's rule) | invention timelines, histories of each product, the Columbian exchange, regional products | Must be read per product; no single table |
| Wikidata (checked today with QLever) | 126,619 items have an invention or discovery date; 12,760 foods have a country of origin | Noisy (stars, species, artworks). Only **606** items have both an invention date and a country of origin, so it can only support a hand-checked list |
| Crop origins (Khoury et al. 2016) [D3] | Where 151 crops come from (23 regions); foreign crops are 69% of national food today | Origins, not spread dates |
| Allen–Unger prices [D2] | 165 goods, 192 towns, 1237–1914, over 125,000 prices, converted to silver | Mostly Europe; few Indian towns |
| Seshat military technologies [D1] | Weapons and armour by state and century (bronze, iron, crossbow, guns …) | Licence unclear (non-commercial, share-alike on some copies), so check before use |
| The mod's own data | 146 regions with ways of life, 1,544 states, dated towns, roads and routes, crops, transport | Ways of life stop at 1850 |

---

## 10. Build order

| Part | What | When |
|---|---|---|
| **A** | Product cards for the step-19 goods + Hyderabad 1948: newspaper, map, coins, grain, bread and biscuits, toddy, gongadi, coal, gold, gems, weapons | **step 19** |
| **B** | The "is it here?" check with defaults for all 146 regions, so no place or year is empty, plus a command `/ee products here` (list what exists at your place and year) and `/ee check all` lines | **done (turn 86)**: 129 products in 14 families (132 since step 22: bark paper, bamboo slips, wax tablets), years for the 17 areas of the survey (`build_product_atlas.py`, `PRODUCT_ATLAS_TABLE.md`), `money/ProductAtlas.java`, `/ee products`, merchants sell 21 holdable products, 3 check lines. Step 19g (turn 88): buyers (merchant, town trader, village pedlar, anybody where people swap) also take them, at their share of the seller's price (twice when brought from far); products with an item have `one` and `many` words |
| **C** | Grow to about 400 product kinds, region by region, India and its neighbours first | ongoing |
| **D** | Workplaces and chains: farms, mines, forges, looms, presses turning inputs into products each day; caravans and trains moving them | trade review (group 6) |
| **E** | Disruptions and replacements: war, blockade, famine; new products pushing out old ones by year | after D |

**`/ee check all` adds these checks (built in part B):**
- every region and year has staple food, cloth, fuel and light;
- no product appears before its first year;
- every product's inputs are made here or brought.

---

## 11. Decisions for the user

1. **Size:** start with about 120 product kinds and grow to about 400?
2. **Items:** only about 100–150 products become items you can hold, and the rest are background goods with local names?
3. **Order:** step 19 starts with the Hyderabad 1948 goods (part A), and the world list grows alongside, India first?

---

## Sources

- [D1] Seshat data and licence notes: https://github.com/datasets/seshat ; Seshat dataset review (warfare and military technology variables): https://www.researchgate.net/publication/323948084_Dataset_Review-Seshat_Global_History_Databank
- [D2] Allen–Unger Global Commodity Prices Database: https://www.sciencedirect.com/org/science/article/pii/S2452366623000269
- [D3] Khoury et al. 2016, "Origins of food crops connect countries worldwide": https://research.wur.nl/en/publications/origins-of-food-crops-connect-countries-worldwide/ ; summary: https://www.kpbs.org/news/2016/06/13/a-map-of-where-your-food-originated-may-surprise
- Wikidata counts: QLever (qlever.dev/api/wikidata), run 13 Oct 2026.
- Product facts already sourced in `PRODUCT_JOURNEYS.md` and `WEAPONS_RESEARCH.md`.

Storage note: the historical generated `PRODUCT_ATLAS_TABLE.md` is archived as `.md.xz`. Use `python3 worldfill/archived_history_reports.py PRODUCT_ATLAS_TABLE.md --print` to read verified bytes, or `--restore` when space permits. Generators still write the original path; the archive does not overwrite it.
