# Source check 1 — eight places checked against sources, the way you checked Geneva

_2026-10-24. Method: take places the register answers, open a source, judge. Then ask what class the errors
belong to, and measure the class at world scale._

## The eight checks

| # | place, year | the register said | what the source says | verdict |
|---|---|---|---|---|
| 1 | **Ben Mansour, Morocco, 155 AD** | Roman Empire | Mauretania Tingitana stretched from Tingis south to Sala Colonia and Volubilis; **Thamusida**, a Roman site, is at the Sebou beside Kénitra, in the same province | **right** |
| 2 | **Finike (Lycia), 491 BC** | Achaemenid Empire | Lycia was overrun by the Achaemenids c. 535 BC, "ruled until the mid-fourth century by the satrap at Sardis", and gave ships to Xerxes in 480 | **right** |
| 3 | **Karnak (Thebes), 221 AD** | Roman Empire | Aegyptus was a Roman province from 30 BC; the Thebaid was part of it until Diocletian's reform c. 293 | **right** |
| 4 | **Byzantium, 498 BC** | Achaemenid Empire | Achaemenid contact with Byzantium c. 513–439 BC; the city stayed under Persian control after the Ionian Revolt | **right** |
| 5 | **Byzantium area, 477 BC** | Achaemenid Empire | Pausanias took Byzantium in **478**, then held it as a private citizen from 477 | **borderline — Persian control had just ended** |
| 6 | **Samos, 1814** | Ottoman Empire | Samos was Ottoman until the Greek War of Independence (autonomous 1832, Greek 1912) | **right** |
| 7 | **Tavriiske (Kherson), 1755** | **Ottoman Empire** | The left bank of the Kherson region was the **Crimean Khanate**, an Ottoman **vassal** 1475–1774; Ottoman annexation of the area came only in 1774/1783 | **wrong in name — the vassal ruled, not the sultan** |
| 8 | **Małowice / Lubin, 1619** | **Holy Roman Empire** | Lower Silesia was a Bohemian crown land inside the HRE from 1335/1348 — but Lubin "remained part of the **Piast-ruled Duchy of Legnica until 1675**" | **wrong in name — a duchy answered as the empire** |

Sources: [Mauretania Tingitana](https://en.wikipedia.org/wiki/Mauretania_Tingitana),
[Ancient Lycia](https://en.wikipedia.org/wiki/Ancient_Lycia),
[Achaemenid satrapies (Encyclopaedia Iranica)](https://www.iranicaonline.org/articles/achaemenid-satrapies/),
[Byzantium and the Achaemenids (Encyclopaedia Iranica)](https://www.iranicaonline.org/articles/byzantium-byzantion-contact-with-the-achaemenids-ca/),
[Roman Egypt](https://en.wikipedia.org/wiki/Roman_Egypt),
[Crimean Khanate](https://en.wikipedia.org/wiki/Crimean_Khanate),
[Kherson oblast (Encyclopedia of Ukraine)](https://www.encyclopediaofukraine.com/display.asp?linkpath=pages\K\H\Khersonoblast.htm),
[Lower Silesia](https://en.wikipedia.org/wiki/Lower_Silesia),
[Duchy of Legnica](https://en.wikipedia.org/wiki/Duchy_of_Legnica),
[Lubin](https://en.wikipedia.org/wiki/Lubin).

**Score: 5 right, 1 borderline, 2 wrong — and both wrong ones are the same mistake.**

## The mistake: a vassal answered as its overlord

Both errors name a **suzerain** where a **state** ruled: the Sultan for the Khan, the Emperor for the Duke.

That is the same shape as the defect cycle 3 fixed (a dominion answered as a colonial empire): **the general
beats the specific when both cover the cell.** So I asked the decisive question — *does the register even have
these polities?*

```
register polities                        : 1,581
  "Crimean Khanate"                      : found
  "Duchy of Legnica"                     : found
```

They are both there. Then I asked whether the register can ever *name* them:

```
Bakhchysarai (the Khanate's capital) 1700  ->  Crimean Khanate [1475-1782]      correct
Tavriiske (Kherson)                  1755  ->  Ottoman Empire   [1564-1768]      vassal not covered here
Legnica (the DUCHY's own capital)    1619  ->  Holy Roman Empire [1619-1621]     vassal LOST at its own capital
Lubin (Duchy of Legnica)             1619  ->  Holy Roman Empire [1619-1621]     same
```

**Two different root causes, and they need different fixes:**

1. **Coverage gap** — the Crimean Khanate's recorded cells do not reach the Kherson steppe, so the Ottoman row
   is the only one covering the spot. Fix: extend the vassal's extent, or add a `VASSAL_OF` relation so the
   khanate answers inside its suzerain's territory.
2. **Priority bug** — at Legnica the Duchy's **own capital** answers as the Holy Roman Empire, in a strange
   two-year span `[1619-1621]`. The specific polity is in the register and loses anyway. This one is a
   selection defect, not missing data — and it is the more serious of the two.

## How big is the class?

I could not answer that by hand, so I made the register grade itself: for every polity, take its **own
recorded centre** and ask who ruled there, mid-span.

```
polities tested at their own centre : 1,550
  answered as itself                : 1,173  (75.7%)
  answered as a DIFFERENT polity    :   276  (17.8%)
  answered nobody                   :   101  ( 6.5%)

rows: testrun/verify/self_consistency.csv
```

**17.8% is a queue for checking, not a wrong-rate.** Some of those 276 are genuinely correct — an Abbasid
caliph in 950 was a figurehead under the Buyids, so `Abbasid Caliphate -> Buyid Dynasty` can be the *better*
answer. Others are exactly the Legnica bug. What the number does prove is that **the class is not rare**:
roughly one polity in six loses at its own centre, and the collateral losses are 1 each, so it is spread
across many different polities rather than concentrated in a few.

## What this means, plainly

- **The hand-check found what the gates could not.** Two of eight places name the wrong kind of ruler, and no
  existing check would ever have noticed — a wrong-but-plausible polity name passes every gate in the project.
- **Your method beats my sampling.** Geneva came from you; this class came from copying your method. The
  200-sample audit never asked "is the *specific* state named, or its overlord?"
- **A new requirement row is born:** *the answer must name the polity that actually ruled the spot, not its
  suzerain* — with the two fixes above, and a re-run of the self-consistency probe as the scoreboard.

## Next, in order

1. **R2-a5** — add `VASSAL_OF` to the register and make the specific polity win inside its suzerain's cells;
   re-run the probe and record the drop from 17.8%.
2. **R2-a6** — hand-check the 276 "different polity" cases against sources, 30 at a time, and split them into
   *legitimate* (caliph vs amir) and *defects* (Legnica). The first split sets the real wrong-rate for this class.
3. **R2-a7** — make self-consistency a gate: no polity may lose at its own capital unless the row is marked
   legitimate.
