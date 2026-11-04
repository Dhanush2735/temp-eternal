# Villagers and the other world systems (turn 50, 2026-10-13)

**Question:** systems in other groups also touch NPCs (money, trade and more). Do we add them now or later?

**Answer:** plan the links now and connect each system later.
- **Now:** small "joints" go into NPC steps 1–2.
- **Later:** each system is reviewed, fixed, and then plugged in when we reach its group (4 to 8).

Nothing in the mod was changed for this note. New probe: `probe_npc_links.sh` + `probes/NpcLinkProbe.java`.

## 1. What exists today (read from the code)

**Shared body:** every NPC in the mod uses the same body, `HumanNpcEntity`, with about 20 roles:
- townspeople: farmer, artisan, merchant, citizen, priest, guard;
- caravan master and guard; ship captain and marine; bandit;
- commander, infantry, archer, cavalry;
- royal guard, chancellor, ruler, imperial mason;
- doctor, quarantine inspector;
- background scholar.

So one mind and one talk menu can serve all of them.

| # | System | NPCs it puts in the world | What it really does today |
|---|---|---|---|
| 31 | Economy | none | One treasury per country, and tax is always 2% of the population. There is **no villager or player money** anywhere. Every country pays 1,000 for **every war in the world**, even wars it is not in (`EconomyEngine.calculateMilitaryCost`). |
| 40 | Prices | none | 13 goods with base prices. Supply and demand stay at 50 because nothing calls `adjustSupply`/`adjustDemand`. Caravans always price with distance 20 and danger 15, so every price is a constant (bread is always 3.38). Cargo "GRAIN" is not in the list, so it gets the fallback price of 10. |
| 40 | Caravans, ships, bandits | caravan master + guards, ship captain + marines, bandits | Start only by command. **Delivery pay is lost:** `CaravanEntityGroup` and `MerchantShipConvoy` call `applyIncome(..., null)`, and `applyIncome` returns at once when the state is null. |
| 29 | Social classes | none | Class shares per country (ancient default; "industrial" from 1750). Not linked to any person. |
| 32 | Farming and famine | none | Food per country. Countries with no population count as 1,000 people (`Math.max(1000, …)`), so their food numbers are made up. |
| 34 | Religion | none | 3 built-in religions and the country table's religion. This is a second faith source next to the villagers' faith line. |
| 37–38 | War, sieges | commander, infantry, archers, cavalry | Per country. Starts by command or by a broken treaty. The talk briefing only says "Active wars recorded: N". |
| 43 | Contagion, doctors | doctors, quarantine inspectors; infects any human NPC | An infection list kept apart from the person (by entity id). Starts by command. |
| 46 | VIP authority | none | A loyalty list per (person, VIP) that nothing calls. |
| 13 | Villager loyalty | every villager | Set to 50 at birth and never changed. This is a second loyalty store. |
| 48 | Reputation | none | Per player. Villagers do not use it. |
| 49, 52 | Royal court, imperial command | ruler, royal guards, chancellor, masons | By command. "Currency debasement" adds treasury money. |

## 2. Two different lists of countries

The villagers take their country from the history data (`HistoricalPresence.spawnCivId`). The money, food, faith and war systems run on the country table: 133 hand-made records plus synthetic stubs, 220 in total.

`probe_npc_links.sh`, 40 well-known towns:

| Result | Towns |
|---|---|
| Real record with numbers: **31** | Paris 1789, Hampi 1520, Rome 100, Delhi/Agra/Varanasi (Mughal), Thanjavur 1010, Patna −250, London, Madrid, Vienna, Moscow, Istanbul, Athens, Baghdad, Damascus, Isfahan, Samarkand, Beijing, Angkor, Timbuktu, Great Zimbabwe, Tenochtitlan, Cusco, Boston, Memphis, Babylon, Mohenjo-daro, Kano, Lisbon, Venice |
| Empty stub, population 0 (no tax, made-up food): **5** | Golconda 1650 (`qutb_shahi`), Hyderabad 1850 (`hyderabad_state`), Kolkata 1850, Chennai 1700, Mumbai 1700 (`british_india`) |
| Country id the table does not know: **4** | Cairo 1300 (`mamluk_sultanate`), Jerusalem 30 (`roman_empire`; the table calls it `rome`), Xi'an 750 (`tang_dynasty`), Kyoto 1600 (`warring_states_japan`) |

Other mismatches:
- Boston 1775 villagers say "ruled by George III", but their country id is `haudenosaunee`.
- **Faith, two sources:**

  | Town | Country table says | Villagers say |
  |---|---|---|
  | London 1600 | Anglican (right) | Roman Catholicism |
  | Patna −250 | Buddhism/Jainism | Brahmanism |
  | Beijing 1600 | Neo-Confucianism | Heaven worship |
  | Timbuktu 1350 | Sunni Islam | Traditional African religion |
  | Chennai 1700 | nothing | Dutch Reformed |

## 3. The plan

### Now: joints inside NPC steps 1–2 (about one extra step of work)

1. **A life record for every person**, saved with them, even while they are far away or "remembered":
   - name, family, age, job and workplace;
   - money level: poor / getting by / comfortable / rich (no coins yet);
   - faith and health;
   - **one** loyalty number (replaces the two stores);
   - opinion of each player.
2. **A "town situation" reader.** The mind and the talk ask only this reader: food, safety, sickness, prices, ruler, news.
   - Every answer carries its source, and "unknown" is allowed.
   - At first it reads only the history data, whose 122,422 loaded events already have types:
     - about 49,000 wars, battles and sieges;
     - about 5,600 plagues and epidemics;
     - about 400 famines;
     - about 25,000 earthquakes, volcanoes, floods and other disasters.
   - The event effects say what changes for people: military presence, disruption (trade and travel suffer), lockdown, political, memorial.
3. **Jobs** picked so they can fit goods later: baker → bread, weaver → cloth, smith → iron, and so on.

### Later: each group, fix first, then plug into the reader

| Group | Fix | Then villagers get |
|---|---|---|
| 3 History and timelines | (no NPC money parts) | — |
| 4 States and society | one country list for every system; the war-cost bug; a single faith source | hunger from food, money level from class, faith from one source |
| 5 War | — | soldiers get the mind and talk; a war nearby means fear and news |
| 6 Trade | lost delivery pay; prices that never move; goods lists for the routes | caravan masters and captains say where they go and what they carry; prices react to sieges and disruption; then trading with villagers (choose emeralds or era coins) |
| 7 Disease | infection kept in the life record | sick villagers, plague doctors; outbreaks mean fear |
| 8 Rulers, VIPs, reputation | one loyalty store | greetings and orders depend on loyalty and reputation; the crown as a fork |

### Much later

Families, personal money and shops.

### Why this order

- **Nothing has to be rebuilt.** Systems only plug into the reader, and the mind never talks to them directly.
- **Villagers never repeat unchecked numbers.** This is the same rule that dropped AI chat.
- **The group-by-group review order stays.**
- **New topics appear by themselves.** The talk menu already hides topics with no data, so "What does bread cost?" appears once trade works.

## 4. Data problems seen while checking (not changed)

- Jerusalem AD 30:
  - "This is Tower of David";
  - "People here speak Latin" (should be Aramaic, Greek and Hebrew);
  - "main faith Imperial cult-driven polytheism" (should be Judaism);
  - the news is the exile of Herod Antipas, which happened in AD 39.
- Cairo 1300 shows the raw id `cairo_fustat` as the place name.
- Cairo 1300 news keeps a raw date prefix ("October 28 (13 Safar 700 AH) –").
- Chennai 1700, "Dutch Reformed": the Dutch were at Pulicat, about 40 km north. Madras was English, and most people were Hindu.
- Timbuktu 1350: the town was a Muslim centre by then; the Djinguereber Mosque dates from 1327.
