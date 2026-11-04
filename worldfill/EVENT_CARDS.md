# Event cards: let players follow up on what a villager says (turn 53, 2026-10-13)

## The problem

A villager names an event, but the player cannot learn what it is, where it is happening, or how to go and see it. Each fact is too thin.

**Today, Hyderabad 1948** (`ChatFactsProbe`):
- The villager says: "Word from nearby: Operation Polo (Hyderabad). Soldiers on the roads, not a new town."
- The only data behind it (`events.json`) is a name, a year and one dot on the city:
  `{"id": "operation_polo_1948", "name": "Operation Polo (Hyderabad)", "year": 1948, "lat": 17.385, "lon": 78.487, "radiusKm": 20, "kind": "military", "effect": "military_presence"}`

**Related lines in the same place and year are wrong too:**
- The ruler line says "Republic of India, ruled by George VI". Until 17 September 1948 this was the Nizam's Hyderabad State, and India was a Dominion until 1950.
- "Annexation of Hyderabad" (`events_wars`) is placed at 19.0, 74.15, near Ahmednagar, about 500 km away.

## The fix in five parts

### 1. An event card for every event a villager can mention

| Part | Example: Operation Polo |
|---|---|
| What | India's military operation that made Hyderabad State join India; India called it a "police action" |
| When | 13–18 September 1948 (day dates, not only the year) |
| Where | Hyderabad State, plus a dated path of places (part 4) |
| Who | Dominion of India (Maj. Gen. J. N. Chaudhuri) against the Hyderabad State Forces and the Razakars (Nizam Mir Osman Ali Khan; El Edroos; Qasim Razvi) |
| Result | Hyderabad joined India |
| Source | Wikipedia "Indian annexation of Hyderabad" (Operation Polo redirects there); Wikidata id |

### 2. Follow-up buttons in the talk menu

Asked after the villager names the event. Example, in-game date 14 September 1948, in Hyderabad:

- Villager: "Have you heard? The Indian Army has entered the state. They call it Operation Polo."
- **What is it?** "India wants Hyderabad to join it. The Nizam wants to stay independent, so the army marched in yesterday."
- **Where?** "Yesterday they fought at Naldurg fort, about 240 km west of here. Another army is coming from the east and is near Suryapet, about 125 km away." The villager points west.
- **When?** "It started yesterday, 13 September."
- **Who?** "The Indian Army under General J. N. Chaudhuri, against the Nizam's army and the Razakars."
- **How do you know?** The source line.
- **Tell me more:** opens the page in the history book (the Chronos codex). The page has:
  - the background;
  - the five days;
  - the result;
  - the civilian deaths with their sources: the Sunderlal Committee's 30,000–40,000.

**Rule:** if a card has no answer for a part, that button does not appear.

### 3. Show "where" in the world, not only in words

- Direction and distance are worked out from the player's real position, through the Terra++ bridge.
- The villager turns and points.
- An on-screen marker, like a quest marker: "Operation Polo — Naldurg, 240 km W".
- The card is kept in the player's journal and on the codex map, so it can be found again later.

### 4. Big events are a moving path, not a dot

Operation Polo moved day by day:

| Day | Places |
|---|---|
| 13 Sept | Naldurg (first battle), Jalkot, Umarga, Tuljapur; in the east, Kodad and Munagala |
| 14 Sept | Rajeshwar, Osmanabad, Aurangabad, Jalna; near Suryapet |
| 15 Sept | Latur, Mominabad, Suryapet |
| 17–18 Sept | ceasefire and surrender |

Storing these dated places gives "where is it now?" a true answer.

### 5. Time

- At normal speed a year passes in 2 minutes, so the 5-day operation is over in under 2 seconds.
- When a big event is near a player, the clock should slow down to days. `SimulationClockManager.registerSlowdown` already exists; today's slowdowns are only 6 global year ranges.
- Villagers know only what has happened up to the in-game date: no future knowledge.

## Sources and size

- **20,922 events already carry a Wikidata id** (`events_world` 14,934; `events_wikidata_more` 5,988).
  - From Wikidata (CC0, through QLever): description, start and end dates, location, participants, part of / has parts.
  - From Wikipedia (CC BY-SA, credited): the lead sentence and the infobox (date, place, result, sides, leaders).
- **Year-page events** (about 43,000): link each one to its main article.
- **Hazards and UCDP events:** the card is built from their own numbers.
- **Paths for big events:** the article's day-by-day section gives the linked places; Wikidata gives their coordinates.
- **Checks:** the few hundred most-heard events are checked by hand.

## Reliability rules

1. Villagers only repeat the card. A missing part gets no button. Better silent than wrong.
2. Sad or sensitive events use neutral wording, whatever the mood.
3. The book page gives both names ("police action" and "annexation") and the sourced figures.
4. No future knowledge: news follows the in-game date.

## Facts checked

Source: Wikipedia, "Indian annexation of Hyderabad", fetched 2026-10-13.
- **Dates:** 13–18 September 1948; Indian forces entered at 4 a.m. on the 13th.
- **Strength:** 35,000 Indian troops; 22,000 Hyderabad State Forces and an estimated 200,000 Razakars.
- **Leaders:** India: Nehru, Patel, J. N. Chaudhuri and others. Hyderabad: Mir Osman Ali Khan, Mir Laiq Ali, El Edroos, Qasim Razvi.
- **Civilian deaths:** the Sunderlal Committee gives 30,000–40,000.
- **Distances** (worked out from the coordinates, from the Charminar area): Naldurg about 240 km west-north-west; Suryapet about 125 km east-south-east; Kodad about 160 km south-east.

## Part 2 (turn 54): linked cards, so every answer leads to the next question

**The goal:** a player in Hyderabad in 1948 hears about Operation Polo and wants to know more. Who is the Nizam? Where does he live? Who are his ministers? Who is in his family? And so on.

**The idea:** knowledge is a web, not a list.
- Every name in an answer can be asked about.
- Every card has its own links to further cards.
- Following links gives thousands of paths, so nobody has to write every question by hand.

### Example chain, in-game date 14 September 1948

| Step | Question | Answer, from the card |
|---|---|---|
| 1 | Operation Polo → **Who is the Nizam?** | "Mir Osman Ali Khan, the seventh Nizam. He has ruled since 1911." |
| 2 | **Where does he live?** | "At King Kothi Palace, about 3.5 km north of Charminar." A marker appears. |
| 3 | **Who are his ministers?** | "His prime minister is Mir Laiq Ali." Each minister is another card. |
| 4 | **His family?** | A family tree screen for the Asaf Jahi dynasty, Nizams I to VII. |
| 5 | And on, from each card | — |

### Checked against the sources (2026-10-13)

**Wikidata (QLever):**
- The Nizam is `Q468298`, with 62 statements:
  - father Asaf Jah VI; children Azam Jah and Moazzam Jah;
  - wife Azam-un-Nisa; family House of Asaf Jah;
  - born and died in Hyderabad; religion Sunni Islam; school; awards.
- King Kothi Palace is `Q12061007`: coordinates 17.3928, 78.4808; owner the Nizam of Hyderabad; architect Kamal Khan.
- Prime Minister of Hyderabad is `Q131319171`, with 5 holders, mostly **without dates**.

**Gaps in Wikidata:**
- The Nizam has no residence (P551).
- Mir Laiq Ali is not listed as a holder of the prime minister post.
- Hyderabad State (`Q1240096`) has no head of state or head of government, only its capitals.
- **Error:** Wikidata says the Nizam held "Member of the Lok Sabha". That is wrong.

**Wikipedia "King Kothi Palace":**
- The seventh Nizam lived there from his accession in 1911 until his death in 1967. He never moved to Chowmahalla.
- The gate's curtain (purdah) was lifted when he was out. That could be a nice in-game detail: is he home?

**So the web needs Wikidata (links, coordinates, dates) plus Wikipedia (infoboxes, lists, lead text), cross-checked.** A fact enters only when it passes the checks, or when both sources agree.

### Who knows what

**Villagers:**
- They have everyday knowledge, and only up to the in-game date.
- For deeper topics they point the player somewhere, which turns curiosity into exploration:
  - the palace clerks for ministers and politics;
  - a newspaper seller for news;
  - a scholar for history.

**The history book (Chronos codex):**
- Every card and every link, with search.
- What happens later is marked as the time traveller's knowledge.
- An optional online Wikipedia lookup could cover anything outside the offline pack. This is text lookup, not AI.

**Meet the people:**
- The Nizam at King Kothi and his ministers at court, through the VIP system.
- He is not among the 102 VIPs yet.

### Ideas borrowed from MCA Reborn (ideas only: MCA is GPL-3.0, so copying code would make this mod GPL)

| MCA | Here |
|---|---|
| Villager tracker: a compass to a villager's last known position | a "find this person or place" compass (the Nizam, King Kothi) |
| Civil registry: a log of all events in a village | the player's history journal |
| Family tree screen | real dynasty and family trees |
| Mail: letters when family members die | news letters ("The Nizam has surrendered") |
| Dialogue engine, personality, mood, hearts | talk menu (A), wording (B), friendship (E) |

**Not borrowed:**
- MCA's GPT-based chat: AI was dropped.
- Its knowledge: MCA villagers are fictional and know no real history.
