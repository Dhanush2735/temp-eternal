# Marking board 28 — the wires connected, and Wikipedia catching me twice

_2026-10-24. Two jobs: connect the layers to the game, and cross-check the answers against Wikipedia. The
first worked. The second found that **my own last fix was wrong**, and I retracted it._

## 1. The wiring — done, and it compiles

Before this turn the vassal, dominion and pack layers existed **only in my probes**: 17 call sites in 13 files
still read the raw register, so the game gave the old answers.

The fix is a single gateway that returns the register's own type, so each call site changed by one word and the
compiler proved all 17:

```java
WhoRuled.hit(lat, lon, year)   // returns Optional<RulerRegister.Hit>, exactly as before
```

Plus `WhoRuled.packCapitals()`, which reads `foundation_civilizations.json` from the mod's own resources - so
the pack layer works in game and headless, with no `CivilizationManager` and no world.

| file | call sites |
|---|---|
| LawRegister · Justice | 2 each |
| EternalEngineCommands, TalkService, Calendars, Units, Arms, WorldQuery, Borders, Reactions, Signs, Soundscape, HistoricalPresence, PhotoRoute, HereAndNow | 1 each |

```
files wired                  : 13   (call sites: 17)
WhoRuled.hit(...) verified   : Legnica 1619 -> Duchy of Legnica, wikidata Q570740
                               Athens -430  -> Athens (from the pack)
                               open ocean   -> empty
compileJava                  : BUILD SUCCESSFUL - 1,248 classes
command_surface              : 220 commands, 220 PASS
/ee check all                : 426 passed, 12 failed (baseline unchanged)
```

`HistoryChecks` was deliberately left on the raw register - those checks test the register itself, and wiring
them would make the register grade its own homework.

## 2. Wikipedia cross-check — and the retraction

### Odesa 1594: **my correction was wrong; the register was right**

Last turn I added a declared Crimean Khanate territory so that Tavriiske 1755 would stop answering "Ottoman
Empire". It produced three corrections. Then I read the sources:

> "Khadjibey came under **direct control of the Ottoman Empire after 1529** ... administered in the Ottoman
> Silistra (Özi) Eyalet" — [Odesa](https://en.wikipedia.org/wiki/Odesa), [Yedisan](https://en.wikipedia.org/wiki/Yedisan)

So at Odesa in 1594 the Ottoman answer was **correct**, and my box broke it. Dubossary 1680 was wrong too —
Podolia was an Ottoman eyalet 1672–1699. **Two of my three corrections were errors.**

**Action: the Crimean Khanate row is withdrawn**, with the reason written into the source so it cannot be
re-added by accident. The lesson recorded there in one line: *a box cannot tell an eyalet fortress from a
horde's steppe, and one verified place does not license a territory.*

### The Legnica row survives — and is now bounded

Its source is explicit that **Lubin** "remained part of the Piast-ruled Duchy of Legnica until 1675"
([Lubin](https://en.wikipedia.org/wiki/Lubin)). The box was narrowed to the duchy's core so it cannot swallow
its neighbours:

| place | 1619 | verdict |
|---|---|---|
| Legnica (the capital) | **Duchy of Legnica** | right |
| Lubin | **Duchy of Legnica** | right, named by the source |
| Wrocław | Holy Roman Empire | right to exclude — Wrocław was its own duchy |
| Brzeg | Holy Roman Empire | **incomplete** — Brzeg was a separate duchy and needs its own row with its own source |

### Milan 1165 → "Holy Roman Empire": imprecise, not proven

Frederick Barbarossa **destroyed** Milan in 1162; the city surrendered 1161–62, was razed, and the Lombard
League formed in 1167 ([Frederick Barbarossa](https://en.wikipedia.org/wiki/Frederick_Barbarossa),
[Timeline of Milan](https://en.wikipedia.org/wiki/Timeline_of_Milan)). In 1165 Milan was a rebel commune being
rebuilt, not a governed imperial city. The answer is not *false* — the Kingdom of Italy was an imperial
kingdom — but **"commune in revolt" would be the honest answer**, and the register has no way to say it.
Logged as a known imprecision, not a fix.

## 3. What the cross-check changed

- **120 + 3 corrections became 120 + 0.** The dominion layer stands; the vassal layer now covers exactly one
  territory with a per-place source.
- The in-game check changed to pin the **cross-checked truth** rather than my fix: Odesa 1594 must stay
  **Ottoman Empire**, so a future declared box cannot quietly take it back.
- The engine and the game now answer with the same code path. **That was the point of the turn.**

## 4. Scoreboard

| item | before this turn | now |
|---|---|---|
| subsystems reading the layered answer | 0 of 17 | **17 of 17** |
| the game's ruler answers | raw register only | **layered: register -> vassal -> dominion -> pack** |
| declared territories | 2, one of them wrong | **1, sourced per place** |
| in-game checks | 425 | **426** |
| gates | green | green (13 s compile, 220/220, 426 passed) |
| swap for the build | wiped every session | **`provision.sh` now re-creates it** |

## Verdict

**The layers are finally live.** And the cross-check did its job in the most uncomfortable way available: it
showed that the fix I was proudest of this session was wrong at two of its three places. That is the method
working — a source read beats a clever box, every time.
