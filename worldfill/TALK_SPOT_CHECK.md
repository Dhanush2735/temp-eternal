# Spot check: what a history-curious player hears today (turn 51, 2026-10-13)

**Question:** are the talk menu (A), the mood wording (B) and the chatter (C) reliable for players who want to learn history from villagers?

**How I checked:**
- I ran `ChatFactsProbe` for 20 well-known towns and years. Half of them are in India.
- It printed the exact lines the mod gives a villager today: place, ruler, language and faith, a famous person, way of life, trade route, road and news.
- I read every line and marked it as one of three:
  - **fine**;
  - **wrong**: clearly false for that place and year;
  - **odd**: broken text, true but from far away, doubtful, or a name shown in lowercase.
- Nothing in the mod was changed.

## Result: 122 lines

| | Lines | Share |
|---|---|---|
| Fine | 70 | 57% |
| **Wrong** | **12** | **10%** (about 1 answer in 10) |
| Odd (real problems) | 25 | 20% |
| Odd (only a lowercase or raw place name) | 15 | 12% |

**Where the errors are:**
- The wrong lines cluster in colonial-era India (8 of 12) and in two European towns (4 of 12).
- My automatic check from step 12 (`FACT_AUDIT.md`) caught almost none of them. It finds broken patterns, such as a reign after death or a faith listed before it was founded. It does not find believable mistakes.

## The 12 wrong lines

| Town, year | What the villager says | Why it is wrong |
|---|---|---|
| Hyderabad 1850 | "This land belongs to the British Empire, ruled by Victoria" | Hyderabad was the Nizam's state (Nasir-ud-Daula, 1829–57) |
| Hyderabad 1850 | "Most people around here work in workshops, mills, shops and offices" | too modern for 1850 |
| Delhi 1650 | "people here speak Eastern Panjabi" | Delhi spoke Hindustani (Khari Boli) and Braj; the court spoke Persian |
| Varanasi 1600 | "People here speak Persian. The main faith here is Islam." | a Hindu holy city; Persian was only the court language |
| Chennai 1700 | "Dutch Republic, ruled by Anthonie Heinsius" | Madras (Fort St. George) was English; the Dutch were at Pulicat, about 40 km north |
| Chennai 1700 | "Dutch or Dutch Low Saxon … Dutch Reformed" | same cause |
| Mumbai 1700 | "Mughal Empire, ruled by Aurangzeb" | Bombay island was English (East India Company) from 1668 |
| Mumbai 1700 | "People here speak Persian. The main faith here is Islam." | Marathi, Konkani and Gujarati; mixed faiths |
| London 1600 | "The main faith here is Roman Catholicism" | the Church of England |
| London 1600 | "This is a town of the Hanseatic League" | London was never a member; the Hanse's London base (the Steelyard) was closed in 1598 |
| Vienna 1700 | "People here speak Slovak" | German (Slovak is Bratislava, 55 km east) |
| Vienna 1700 | "ruled by Leopold VI (Ruler of Austria)" | the emperor then is known as Leopold I; Leopold VI was a duke (1198–1230) |

## The 25 odd lines (real problems)

**Far away, true but out of place:**
- Paris 1789: Tischbein, a German painter who died in Kassel.
- Hyderabad and Kolkata 1850: "Hōne Heke has died" (a New Zealand chief).
- Varanasi 1600: the court painter Basawan.
- Chennai 1700: the Dutch painter Lambert Doomer.

**Broken text:**
- Hampi: "defeat the Adil Shahi under at".
- Thanjavur: a run-on temple sentence.
- Athens −430: "Phidias, returns to Athens, where he is imprisoned, has died"; "because of Athens suffers a major pestilence".
- Madrid: "SpanishPortuguese"; "Philip III and II".
- Rome: "Main hall, Trajan's Market, Rome, is made (until AD 112)".
- Cairo: a raw date prefix "October 28 (13 Safar 700 AH) –".
- Moscow: "Adrian … dies … He is replaced … as Patriarch Stefan" (Stefan Yavorsky was only a stand-in; no new patriarch was named).

**Doubtful:**
- Paris "or Breton".
- Hampi and Thanjavur "or Sanskrit", as a spoken language.
- Agra "main faith Islam".
- Samudragupta "born near" Delhi.
- Mahinda "born near" Pataliputra (the chronicles say Ujjain).
- Vienna: Rákóczi's arrest (1701) told in 1700.
- London: the playing-card monopoly told as Nicholas Fuller's.
- Kolkata 1850 "ruled by Victoria" (the East India Company governed).
- Kolkata 1850 "mills, shops and offices".
- "Grand Trunk Road" in 250 BC.

**Place names:** 14 towns show in lowercase ("This is hampi"), and Cairo shows a raw id ("cairo_fustat").

## Other limits found

- **Shallow:** each town has only 4–8 facts. A curious player runs out after a few questions.
- **Tone (B):** mood wording must never make a villager sound happy or flippant about deaths, massacres or plagues.
- **Repetition (C):** chatter repeats the same facts, so a wrong line is heard more often.

## How much more the data knows than villagers say (turn 52)

Events within 30 km (all years) and famous people born within 30 km, read from the mod's data files:

| Town | Local events | People born there | Lines a villager says today |
|---|---|---|---|
| Paris | 579 (51 BC to 2025) | 4,741 | 6 |
| Rome | 910 (753 BC to 2026) | 1,639 | 8 |
| Hyderabad | 103 (AD 550 to 2013) | 24 | 5 |
| Varanasi | 6 | 13 | 7 |
| Hampi | 0 (only regional news) | 1 | 6 |

**What this means:**
- Depth is very uneven. A learner in Europe would find a lot; in India very little.
- The English Wikipedia year pages are thin for India. A history book would need more sources for places like these, such as city history pages.

## What would make A, B and C reliable for history learners

1. **Fix the data first.** Start with rulers, then language and faith lines, far-away famous people, broken news text, and place names.
2. **Better silent than wrong.** A line that fails a check is hidden, not said, like the hidden Tischbein line in the preview.
3. **A "How do you know?" button.** It shows the source and whether a fact is recorded or estimated.
4. **A tone rule for B.** Sad or violent news is always told seriously; the mood only changes small words.
5. **More depth from data we already have:**
   - "Who ruled before?" (17,700 reigns);
   - "What happened here in the past?" (122,422 dated events);
   - "Who else was born here?" (184,193 people);
   - "How old is this town?"
6. **A "That's wrong" button.** The line goes to the server log, with no files, so it can be fixed.
