# Source check 2 — Brzeg, and what one town page changed

_2026-10-24. You sent [Brzeg](https://en.wikipedia.org/wiki/Brzeg). It closed a gap I had flagged as
"incomplete" one turn earlier, and it exposed a second defect in the same rule._

## What the page says

> "From the **early 14th to late 17th centuries**, the town was ruled by the **Piast dynasty** as fiefs of the
> **Bohemian Crown** within the **Holy Roman Empire**."

Also: first mentioned 1234 as a trading settlement; Magdeburg town rights 1248; **town rights 1248**; after the
Silesian Wars it passed to Prussia.

## What the engine said before

```
Brzeg 1619  ->  Holy Roman Empire     (the register has no Duchy of Brzeg at all)
Brzeg 1400  ->  Kingdom of Bohemia    (again the overlord, not the duke)
```

Both answers name **the power above the town** rather than **the dynasty that ruled it** — the same defect as
Legnica, and the second version of it: the register calls the overlord "Kingdom of Bohemia" in 1400 and "Holy
Roman Empire" in 1619, and my first rule only recognised the second name.

## The fix, in two parts

1. **A row for a polity the register does not hold.** `Vassal` gained a `displayName`, so a declared row can
   name *Duchy of Brzeg* in its own right instead of showing a bare id. The row is sourced to the page above.
2. **Both overlord names accepted.** A Bohemian fief's overlord is written two ways in the register; the row
   now holds a **list** of overlord names, and the rule fires on either.

## After

```
Brzeg 1619  ->  Duchy of Brzeg        [VASSAL_DECLARED]   right
Brzeg 1400  ->  Duchy of Brzeg        [VASSAL_DECLARED]   right
Brzeg 1700  ->  Habsburg Monarchy     [REGISTER]          right - and the rule stops at 1675, so it
                                                           cannot claim the Habsburg period
```

## The guard that matters more than the fix

A territory box is dangerous, so the box was drawn **before** the row went in, and every neighbour was checked:

| neighbouring town | its own duchy | in the box? | answer after |
|---|---|---|---|
| Oława 50.944 / 17.293 | Duchy of Oława | **no** (17.29 < 17.35) | Holy Roman Empire — correctly untouched |
| Namysłów 51.077 / 17.717 | separate | **no** (17.72 > 17.65) | Polish-Lithuanian Commonwealth — untouched |
| Ziębice 50.601 / 17.041 | Duchy of Ziębice | **no** (lat and lon) | Habsburg Monarchy — untouched |
| Opole 50.667 / 17.924 | Duchy of Opole | **no** | Holy Roman Empire — untouched |

**No dated town in the whole 9,790-town audit falls inside the Brzeg box**, so the row claims Brzeg's own
ground and nothing else. That is the check I failed to run for the Crimean box, and the reason that one was
retracted.

## Pinned in the game

`checkWhoRuledAnswersWithItsProvenance` now pins **four** places, two of which must stay wrong-answer-free in
opposite directions:

- Brzeg 1619 → **Duchy of Brzeg** (the vassal must win)
- Oława 1619 → **Holy Roman Empire** (the neighbour must not be swallowed)
- Legnica 1619 → **Duchy of Legnica**
- Odesa 1594 → **Ottoman Empire** (the retraction must hold)

```
compileJava    : BUILD SUCCESSFUL — 1,248 classes (15 s)
command_surface: 220 commands, 220 PASS
/ee check all  : 426 passed, 12 failed (baseline unchanged)
```

## What this pattern now amounts to

Three Polish-Silesian cases, all fixed from one page each, all with the same shape: **the register knows the
overlord and not the duke.** The register has 1,581 polities and the Silesian duchies alone number more than
twenty. So this is not three bugs — it is **a category with a known recipe**:

1. read the town's page,
2. add a row naming the specific polity and its source,
3. draw the box *before* the row, and check every neighbour against it,
4. pin both directions in the check — the town that must be claimed, and the neighbour that must not.

That recipe is what the remaining 274 self-consistency failures should be worked through with, thirty at a
time.
