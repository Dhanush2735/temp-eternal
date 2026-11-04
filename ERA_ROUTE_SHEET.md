# The era route — your walk sheet

_31 places from `eternal/FINAL_TEST.md` section R. The route is the project's own; the coordinates are the
real ones, fed to Terra++'s `/tpll`, which puts you where that point on Earth is built in this world._

`/tpll <lat> <lon>` is Terra++'s own command (`net/buildtheearth/terraplusplus/commands/TpllCommand`);
the coordinates below are the same form as the famous-places list bundled in that jar, and five of
them are that list's own numbers exactly — New York `40.7128 -74.0060`, London `51.5074 -0.1278`,
Tokyo `35.6762 139.6503`, Sydney `-33.8688 151.2093`, the Amazon `-3.1190`. An optional third number
is the Y to stand at; leave it off and you land on the surface (an explicit Y is handy in a city that
is built up, where the surface height can be a roof).

## Two of the three parts are now automated

| part | who does it | where it is |
|---|---|---|
| **the record's content at each stop** — the name, the people, the events, the money, the technologies | **done, by machine** | `ERA_ROUTE_DATA.md` (report) · `testrun/era_route.tsv` (table) · `worldfill/era_route_probe.py` (re-runnable) |
| **the walking** — set the year, teleport, ask the card, write it down | **done, by a script you run** | `era_route_drive.py` |
| **the looking** — dress, faces, buildings, the feel of a town | **only you** | the walk itself |

`ERA_ROUTE_DATA.md` already answers what each stop's data holds — including R17's own test: at
Tenochtitlan the atlas says iron 1519, horses 1519, carts 1519, printed books 1539, so at 1500 **none
of them have arrived**, which is exactly what R17 demands. It also flags where the honest answer is
"nothing here" (Greenland, Cahokia, the Sahara) so an empty stop is not mistaken for a bug.

## Before you start

1. You need to be **operator** (`/op <you>`) — `/tpll` and `/ee date` both want level 2.
2. Set the year **first**, then teleport. Teleporting does not change the year.
3. `/ee date <year> 1 1` is the only command that can move time **backwards**; `/ee year set` refuses
   backwards moves by design (that is F4's rule, and it is correct).
4. **A backwards jump forks the world** — the game will say *"this world forks"*. That is expected, not
   an error. The list below is in **chronological order**, so if you follow it top to bottom you go
   forward almost the whole way and fork rarely. Two exceptions: **R16 (Sahara, 1000)** sits after 1350,
   and **R31 (Siberia, 1900)** sits after 2020 — do those two where the year flows (R16 before R11, R31
   before R26) if you want a single unbroken run forward.
5. At every stop the same four moves:
   - `/ee here` — *"what the record says of where you stand this year"*. This is the place card.
   - look at **people** (right-click to talk), their **dress**, the **money** in your purse (`/ee purse`),
     and the **buildings**.
   - `/ee probe` if something looks wrong — it is a Terra++ debug snapshot with your exact position.
   - write **yes / no / screenshot**. A "no" is worth more than ten "yes"es: note the place, the year,
     the command and what the screen showed.

Good everywhere: talk, dress, money, buildings and the town's name all belong to that year. Nothing is
claimed as passed until you say so.

---

| # | place | year | continent | `/ee date` | `/tpll` | watch for | done |
|---|---|---|---|---|---|---|---|
| **R1** | Ur<br><sub>Ur (Tell el-Muqayyar), Iraq</sub> | 2500 BC | Asia | `/ee date -2500 1 1` | `/tpll 30.9626 46.1031` |  | ☐ |
| **R2** | Giza<br><sub>Giza plateau, Egypt</sub> | 2500 BC | Africa | `/ee date -2500 1 1` | `/tpll 29.9792 31.1342` |  | ☐ |
| **R3** | Mohenjo-daro<br><sub>Mohenjo-daro, Sindh</sub> | 2500 BC | Asia | `/ee date -2500 1 1` | `/tpll 27.3294 68.1386` |  | ☐ |
| **R4** | Anyang<br><sub>Yinxu / Anyang, Henan</sub> | 1200 BC | Asia | `/ee date -1200 1 1` | `/tpll 36.1267 114.3133` |  | ☐ |
| **R5** | Athens<br><sub>Athens, Greece</sub> | 430 BC | Europe | `/ee date -430 1 1` | `/tpll 37.9838 23.7275` |  | ☐ |
| **R6** | Pataliputra<br><sub>Patna (Pataliputra), Bihar</sub> | 300 BC | Asia | `/ee date -300 1 1` | `/tpll 25.5941 85.1376` |  | ☐ |
| **R7** | Rome<br><sub>Rome, Italy</sub> | AD 100 | Europe | `/ee date 100 1 1` | `/tpll 41.9028 12.4964` | aqueducts, paved roads, the Roman mile | ☐ |
| **R8** | Teotihuacan<br><sub>Teotihuacan, Mexico</sub> | AD 500 | North America | `/ee date 500 1 1` | `/tpll 19.6925 -98.8438` |  | ☐ |
| **R9** | Chang'an<br><sub>Xi'an (Chang'an), Shaanxi</sub> | 750 | Asia | `/ee date 750 1 1` | `/tpll 34.3416 108.9398` |  | ☐ |
| **R10** | Baghdad<br><sub>Baghdad, Iraq</sub> | 900 | Asia | `/ee date 900 1 1` | `/tpll 33.3152 44.3661` |  | ☐ |
| **R11** | Greenland's Norse farms<br><sub>Qassiarsuk / Brattahlid, Greenland</sub> | 1000 | North America | `/ee date 1000 1 1` | `/tpll 61.1544 -45.5156` | problem 81: they may answer nothing; say so, do not invent | ☐ |
| **R12** | Cahokia<br><sub>Cahokia Mounds, Illinois</sub> | 1100 | North America | `/ee date 1100 1 1` | `/tpll 38.655 -90.061` | problem 73: the population floor may show nothing | ☐ |
| **R13** | Angkor<br><sub>Angkor, Cambodia</sub> | 1150 | Asia | `/ee date 1150 1 1` | `/tpll 13.4125 103.867` |  | ☐ |
| **R14** | Great Zimbabwe<br><sub>Great Zimbabwe, Zimbabwe</sub> | 1300 | Africa | `/ee date 1300 1 1` | `/tpll -20.2674 30.9337` |  | ☐ |
| **R15** | Timbuktu<br><sub>Timbuktu, Mali</sub> | 1350 | Africa | `/ee date 1350 1 1` | `/tpll 16.7735 -3.0074` |  | ☐ |
| **R16** | the Sahara<br><sub>the Ahaggar, central Sahara, Algeria</sub> | 1000 | Africa | `/ee date 1000 1 1` | `/tpll 23.2833 5.5333` | and empty land nearby (see X1) | ☐ |
| **R17** | Tenochtitlan<br><sub>Mexico City (Tenochtitlan)</sub> | 1500 | North America | `/ee date 1500 1 1` | `/tpll 19.4326 -99.1332` | before contact: no iron, horses, carts or printed books | ☐ |
| **R18** | Cusco<br><sub>Cusco, Peru</sub> | 1500 | South America | `/ee date 1500 1 1` | `/tpll -13.5319 -71.9675` | before contact: no iron, horses, carts or printed books | ☐ |
| **R19** | the Amazon<br><sub>the Amazon near Manaus, Brazil</sub> | 1500 | South America | `/ee date 1500 1 1` | `/tpll -3.119 -60.0217` |  | ☐ |
| **R20** | Vijayanagara<br><sub>Hampi (Vijayanagara), Karnataka</sub> | 1520 | Asia | `/ee date 1520 1 1` | `/tpll 15.335 76.46` |  | ☐ |
| **R21** | Delhi<br><sub>Delhi, India</sub> | 1650 | Asia | `/ee date 1650 1 1` | `/tpll 28.6139 77.209` |  | ☐ |
| **R22** | Edo<br><sub>Tokyo (Edo), Japan</sub> | 1700 | Asia | `/ee date 1700 1 1` | `/tpll 35.6762 139.6503` | it is called Edo, not Tokyo | ☐ |
| **R23** | London<br><sub>London, England</sub> | 1700 | Europe | `/ee date 1700 1 1` | `/tpll 51.5074 -0.1278` |  | ☐ |
| **R24** | Paris<br><sub>Paris, France</sub> | 1789 | Europe | `/ee date 1789 1 1` | `/tpll 48.8566 2.3522` |  | ☐ |
| **R25** | Sydney<br><sub>Sydney, Australia</sub> | 1850 | Oceania | `/ee date 1850 1 1` | `/tpll -33.8688 151.2093` |  | ☐ |
| **R26** | New York<br><sub>New York, USA</sub> | 1920 | North America | `/ee date 1920 1 1` | `/tpll 40.7128 -74.006` |  | ☐ |
| **R27** | Hyderabad<br><sub>Hyderabad, India</sub> | 1948 | Asia | `/ee date 1948 1 1` | `/tpll 17.385 78.4867` | the Dominion of India, ruled by George VI; rupees; the nizam's city | ☐ |
| **R28** | Lagos<br><sub>Lagos, Nigeria</sub> | 1960 | Africa | `/ee date 1960 1 1` | `/tpll 6.5244 3.3792` |  | ☐ |
| **R29** | Moscow<br><sub>Moscow, Russia</sub> | 1980 | Europe | `/ee date 1980 1 1` | `/tpll 55.7558 37.6173` |  | ☐ |
| **R30** | Sao Paulo<br><sub>Sao Paulo, Brazil</sub> | 2020 | South America | `/ee date 2020 1 1` | `/tpll -23.5505 -46.6333` |  | ☐ |
| **R31** | Siberia<br><sub>Yakutsk, Siberia</sub> | 1900 | Asia | `/ee date 1900 1 1` | `/tpll 62.0355 129.6755` |  | ☐ |

---

## The order, in one block (copy-paste friendly)

Forward-only run: R16 moved up to just after R10, R31 moved to just before R26.

```
R1  /ee date -2500 1 1   /tpll 30.9626 46.1031      Ur, 2500 BC
R2  (same year)          /tpll 29.9792 31.1342      Giza, 2500 BC
R3  (same year)          /tpll 27.3294 68.1386      Mohenjo-daro, 2500 BC
R4  /ee date -1200 1 1   /tpll 36.1267 114.3133     Anyang, 1200 BC
R5  /ee date -430 1 1    /tpll 37.9838 23.7275      Athens, 430 BC
R6  /ee date -300 1 1    /tpll 25.5941 85.1376      Pataliputra, 300 BC
R7  /ee date 100 1 1     /tpll 41.9028 12.4964      Rome, AD 100
R8  /ee date 500 1 1     /tpll 19.6925 -98.8438     Teotihuacan, AD 500
R9  /ee date 750 1 1     /tpll 34.3416 108.9398     Chang'an, 750
R10 /ee date 900 1 1     /tpll 33.3152 44.3661      Baghdad, 900
R16 /ee date 1000 1 1    /tpll 23.2833 5.5333       the Sahara, 1000
R11 (same year)          /tpll 61.1544 -45.5156     Greenland, 1000
R12 /ee date 1100 1 1    /tpll 38.6550 -90.0610     Cahokia, 1100
R13 /ee date 1150 1 1    /tpll 13.4125 103.8670     Angkor, 1150
R14 /ee date 1300 1 1    /tpll -20.2674 30.9337     Great Zimbabwe, 1300
R15 /ee date 1350 1 1    /tpll 16.7735 -3.0074      Timbuktu, 1350
R17 /ee date 1500 1 1    /tpll 19.4326 -99.1332     Tenochtitlan, 1500
R18 (same year)          /tpll -13.5319 -71.9675    Cusco, 1500
R19 (same year)          /tpll -3.1190 -60.0217     the Amazon, 1500
R20 /ee date 1520 1 1    /tpll 15.3350 76.4600      Vijayanagara, 1520
R21 /ee date 1650 1 1    /tpll 28.6139 77.2090      Delhi, 1650
R22 /ee date 1700 1 1    /tpll 35.6762 139.6503     Edo, 1700
R23 (same year)          /tpll 51.5074 -0.1278      London, 1700
R24 /ee date 1789 1 1    /tpll 48.8566 2.3522       Paris, 1789
R25 /ee date 1850 1 1    /tpll -33.8688 151.2093    Sydney, 1850
R31 /ee date 1900 1 1    /tpll 62.0355 129.6755     Siberia, 1900
R26 /ee date 1920 1 1    /tpll 40.7128 -74.0060     New York, 1920
R27 /ee date 1948 1 1    /tpll 17.3850 78.4867      Hyderabad, 1948
R28 /ee date 1960 1 1    /tpll 6.5244 3.3792        Lagos, 1960
R29 /ee date 1980 1 1    /tpll 55.7558 37.6173       Moscow, 1980
R30 /ee date 2020 1 1    /tpll -23.5505 -46.6333     Sao Paulo, 2020
```

## At each stop, the four questions

1. **`/ee here`** — does the card name the right place and the right year, and does it say something
   true and specific rather than something safe and generic?
2. **People** — right-click one or two. Does what they say belong to their century? Do they look it?
3. **Money** — `/ee purse`, then buy something. Is the coin of that place and century?
4. **Buildings** — do they match the place and era band (see the *watch for* column for the sharp cases)?

## The sharp cases — the ones most likely to fail

| test | what makes it fail |
|---|---|
| **R7 Rome, AD 100** | no aqueducts, no paved roads, no Roman mile |
| **R11 Greenland, 1000** | answering confidently with detail it does not have. "The record says nothing here" is a **pass** |
| **R12 Cahokia, 1100** | the same for population — an honest emptiness passes, an invented crowd fails |
| **R16 the Sahara, 1000** | anything invented in empty desert |
| **R17/R18, 1500 before contact** | iron, horses, carts or printed books in the Americas |
| **R22 Edo, 1700** | being called Tokyo |
| **R27 Hyderabad, 1948** | not the Dominion of India under George VI, not rupees, not the nizam's city |

## When you are done

Say which numbers you passed and which you did not, and for any "no": the place, the year, the exact
command and what the screen showed. I will put your answers into `FINAL_TEST_SCORED.md` and the verdict
moves from *"46 open"* to whatever the session actually earned — including, if it comes to it, new
defects.

