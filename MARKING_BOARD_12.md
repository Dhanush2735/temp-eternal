# Marking board 12 — the artifact

_2026-10-23. Every gate before this one tested the source tree, the compiled classes, or the data on
disk. None of them opened the thing a player installs. This sitting did: it built the jar, opened
it, checked it against the manifest byte by byte, proved it is reobfuscated, and then **booted a
production Forge server with nothing but that jar and Terra++ in `mods/`**._

## 1. What a player gets

```
eternal/build/libs/eternalengine-1.0.0.jar     61,870,675 bytes
  1,526 entries · 1,232 classes · 132 data files · mods.toml (v1.0.0) · pack.mcmeta (pack_format 15)
  the 45 MB famous-people master is not inside; the 12.5 MB tile pack built from it is
```

New gate, `testrun/check_jar.py`, 11 checks, all green:

```
ok  mods.toml present, version substituted: 1.0.0        ok  mod id: eternalengine
ok  the logo the mod list draws is in the jar: logo.png  ok  pack.mcmeta pack_format 15 (1.20.1)
ok  every shipped file the manifest lists is in the jar
ok  131/131 shipped files match the manifest's size and SHA-256
ok  the 1 master kept out of the jar is indeed out
ok  1232 classes in the jar (1232 in the compiled tree)
ok  every data file in the jar is listed in the manifest
ok  reobfuscated: 1730 Minecraft references in production (SRG) names, 279 plain names that the
    production jar itself declares, 0 unresolvable
ok  every class is Java 17 bytecode (major 61)
```

The reobfuscation line is the one that matters and the one nobody had checked. Probes run against the
*development* classpath, where Minecraft's members have readable names; in a released game those
members are SRG-named (`m_12345_`), so a reference left deobfuscated throws `NoSuchMethodError` the
first time a player walks into that code path — and it would look like a normal in-game crash. So
every `net/minecraft/*` reference in the jar was resolved against **Forge's production (SRG) jar**,
walking superclasses and interfaces exactly as the JVM does:

| references into Minecraft | count | verdict |
|---|---|---|
| in SRG form (`m_…_`, `f_…_`) | 1,730 | correct for production |
| in plain names the production jar itself declares (`getCapability`, `getString`, `FriendlyByteBuf.readInt` …) | 279 | correct: these are Forge's own additions |
| **unresolvable** | **0** | nothing here would throw |

## 2. The production server: the jar, not the dev classpath

`verify_prod_server.sh` installs a real Forge 1.20.1-47.2.0 server, copies the built jar and
Terra++ into `mods/`, boots it and drives it over RCON. Run twice, identically:

```
install            server installed
mods_installed     eternalengine-1.0.0.jar (61,870,675 bytes) + terraplusplus-2.0.0-alpha.jar
jar_boots          Done (5.963s)! For help, type "help"
ee_check_all       436 passed, 0 failed, 12 known limits
commands           212 commands on the live server
commands_answered  0 command(s) with an empty answer
shutdown           ThreadedAnvilChunkStorage: All dimensions are saved
7 passed, 0 failed
```

**This retires a `CANNOT JUDGE HERE` that has stood since board 9.** The standing verdict says
`[TerraBridge] Terra++ classes are not available` cannot be judged because the sandbox has no Terra++
jar. It has had one all along — `eternal/libs/terraplusplus-2.0.0-alpha.jar` — and with it in `mods/`:

```
[EE] Found Terra++ version: 2.0.0-alpha
[TerraBridge] Terra++ classes available; waiting for active generator
[EE check]  [ OK ] Terra++ is available (the world is a real place on Earth)
[Terra++Density] BTE projection loaded: ScaleProjectionTransform, zoom=15, Y=[-2032,2032]
```

The gap was in the marking, not the mod.

The 212 commands answered with real text (`/ee year` → *Current simulation year: 3000 BCE*, `/ee
data paths`, `/ee performance`, the codex…), 0 exceptions, slowest **410 ms** (`/ee data load`).
Server performance on the artifact: **8,174 ticks, average 0.03 ms, last 100 ticks 0.01 ms, peak
18.86 ms, 1 second over the 10 ms budget** — the same shape as board 10's dev run.

Honest limits of this test: the world is **flat**, so terrain generation, chunk streaming and the
crowd were not exercised (Terra++ still loaded and its projection bound); there is **no client**, so
G6's visual half and G7's fps remain exactly as blocked as they were.

## 3. The eight defects this sitting found

**1. The 212-command run that first "passed" was a lie.** Run against the production server with the
wrong RCON password, the client recorded **212/212 ANSWERED**. Every answer was an empty string: the
server signals a refused password with request id `-1`, and the client only ever looked at the packet
*type*, which is `2` either way. So the connection test passed, the socket was refused, and nothing
ran. Fixed in `worldfill/probes/rcon.py`: auth checks the id, and after auth it proves the link by
running `list` and requiring a non-empty answer before any row is recorded. Wrong password now fails
loudly — verified both ways.

**2. Eighteen more gzip writers still stamped the clock.** Board 11 patched the `gzip.open(…, "wb")`
writers; **eighteen more wrote text mode** (`gzip.open(path, "wt", …)`): `build_building_culture`,
`build_scripts`, `build_people`, `build_polity_facts`, `fix_state_ids`, `fill_rulers`, `tidy_state_facts`
and ten others. Two of them had just rewritten shipped packs mid-sweep. The worst part is what it did
to the *install*: the manifest records the file's SHA-256 and `DataManifest.verify()` compares it at
load, so those two packs would have shown up **in your game** as "different content". Fixed by making
one writer the only writer (`modpack.gzopen`, `mtime=0`, closes the file beneath it), routing all 18
sites through the same shape, and — proven — writing the same pack twice now gives identical bytes.

**3. The manifest gate could not see that.** `verify_all.sh` checked the manifest at L0, *before* the
probes, and several probes rebuild packs as they run. The gate passed at 09:20; two packs were
rewritten at 09:37 and 09:39; the sweep ended green with a manifest that no longer described the data.
Fixed: a second, post-probe manifest check (`manifest_after`) now closes the ledger, and it is what
caught this.

**4. `logoFile = "logo.png"` pointed at nothing.** `mods.toml` has advertised a logo since the
beginning and no such file was ever in the jar: Forge draws a blank tile on the mods screen. A 256×256
logo now exists at `src/main/resources/logo.png` (a globe over a horizon line) and is verified in the jar.

**5. The mod called itself "YourName".** `gradle.properties` shipped `mod_authors=YourName` and
`mod_description=Eternal Engine Mod` — both printed on the mods screen a player sees. The description
is now the real one (184,060 people, 1,153 states, 1:1 Earth); the author line reads **"Eternal Engine
contributors"** because the marking will not invent a person's name. Put yours there if you want it.

**6. `gradlew` is not executable in the tree.** `-rw-r--r--`: `./gradlew build` fails with
*Permission denied* on a fresh copy. The scripts all call `sh gradlew`, which is why no gate ever
noticed. Mode fixed; `sh gradlew` remains the portable form.

**7. `TerraTimeBridge` looks for a class Terra++ does not have.** It probes
`net.buildtheearth.terraplusplus.generator.historical.TerraTimeManager`; the 2.0.0-alpha jar carries
423 classes and none of them is that. So the line *"No Terra++ time in this game
(ClassNotFoundException)"* is not a sandbox artefact — it is the permanent state with this Terra++
version, and the fallback (the mod's own clock) is what always runs. Not broken, but the bridge's
name promises something it cannot do.

**8. The count was 435, not 436, and it mattered.** First production run reported **435 passed, 0
failed**; board 10's dev server reported 436. Investigating instead of shrugging: the missing check is
`this alternate timeline has a chronicle`, which only fires once a world has diverged. The dev world
had (an earlier test command had diverged it); the fresh production world had not. After the 212-command
sweep diverged it, `/ee check all` on the same production server returned **436 passed, 0 failed, 12
known limits** — the two servers agree exactly.

## 4. The ledger, end to end

```
./verify_all.sh --all       149 passed, 0 failed   (141 probes + 8 gates)
  syntax_gate               no syntax errors (4,519 diagnostics)
  manifest                  manifest.json: up to date
  compileJava               BUILD SUCCESSFUL in 7s — 1,232 classes
  command_surface           212 commands: 212 PASS, 0 LEAK
  ee_check_all              422 passed, 11 failed, 12 known limits  (no world: board 10 proves all 11)
  jar_build                 eternalengine-1.0.0.jar
  jar_check                 JAR OK: 11 checks passed, 0 failed
  manifest_after            manifest.json: up to date; DATA_CREDITS.md: up to date
./verify_server.sh          5 passed, 0 failed     (dev server: 212 commands, datapack 10/10)
./verify_prod_server.sh     7 passed, 0 failed     (the jar on a real Forge server)
```

**9. My own fix destroyed two packs, and the new gate caught it.** Fixing the eighteen text-mode
writers, the mechanical patch put `encoding="utf-8"` on `gzip.GzipFile`, which does not take that
argument — on **nine** call sites. Worse, those sites open the target file first, so the file was
**truncated to zero bytes before the `TypeError` fired**: `building_culture.json.gz` and
`scripts.json.gz` became 0 bytes during the sweep, five probes failed on the `TypeError`, and the jar
built mid-sweep carried two empty packs. The `manifest_after` check added twenty minutes earlier is
what flagged it (`2 files drifted: size 0`). Both packs were regenerated by their own builders — their
**content SHA-256 is unchanged** (`22f205ed…`, `e6ec4e0d…`), so no fact was lost, only bytes — the
manifest was rebuilt and the jar re-checked green (`131/131`). All nine sites now use one shape
(`GzipFile(mode="wb")` + `io.TextIOWrapper`), and no text-mode `GzipFile` remains in `worldfill/`.

## 5. Self-corrections, sixteen to twenty

16. **The first 212-command run against the production server was counted as a pass while every
    answer was empty** — a wrong password plus a client that could not tell. It is the same mistake
    as board 9's "128 broken commands" and board 11's "the probe overwrote the grid": the measurement
    lied and I believed it.
17. **Board 11's "27 builders now write deterministic gzip" was two-thirds true** — it fixed the
    binary-mode writers and missed the eighteen text-mode ones, two of which then corrupted the
    shipped packs' recorded hashes.
18. **The manifest gate was in the wrong place in the sequence**, so a sweep could end green on a
    data set the mod would reject at load. Checking a thing once, early, is not checking it.
19. **"Terra++ classes are not available" was never a sandbox limit** — the jar was in
    `eternal/libs/` the whole time and one line in `mods/` settles it. A `CANNOT JUDGE` is a claim
    and it needs checking like any other.
20. **A mechanical patch is not a fix until it has been run.** The eighteen-writer change compiled,
    passed `py_compile`, looked right in review — and then truncated two shipped packs on its first
    execution. Reading a diff is not a test; only the sweep was.

## 6. Where this leaves the gates

G1–G5 stand. G5 is now stronger than it has ever been: the **artifact** builds, packages every
licensed byte correctly, carries no deobfuscated Minecraft reference, boots on a production server and
answers all 212 commands there. G6's visual half and G7's client half are untouched by any of this —
they need your jar, your world and your eyes, and they are the only things left.
