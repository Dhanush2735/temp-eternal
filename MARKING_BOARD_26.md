# Marking board 26 — cycle 3: the dominion repair, and the lever that makes the loop cheap

_2026-10-24. Two things happened: the audit was made **full-scale** (9,790 towns in 3 seconds instead of 200
samples by hand), and the first **fix-by-class** landed. Also: the gate script itself was OOM-killing the
Gradle daemon, and every red `compileJava` before this was that, not the code._

## Lever 1: measure everything, not a sample

`worldfill/probes/TruthAuditFull.java` audits **every** readable town, not a 200-draw:

```
towns audited    : 9,790        (run time: 3 seconds)
answered         : 9,656  (98.6%)
answered nobody  :   134  (1.4%)
sources          : REGISTER 9,534 · DOMINION 120 · PACK_CAPITAL 2 · NONE 134
```

The 200-sample audit cost a turn. The 9,790-town audit costs **three seconds**. That is the single biggest
change to the loop's economics: verification is now cheap enough to run after *every* change.

## Lever 2: fix by class, not by instance

Board 25 found 7 wrong answers with 2 causes. The first cause — *a dominion is not a colonial empire* — is now
a rule inside `WhoRuled` (`Source.DOMINION`), with a **sourced table** of twelve successor states and their
founding years (British North America Act 1867, Federation of Australia 1901, NZ dominion status 1907, South
Africa Act 1910, Anglo-Irish Treaty 1922, Indian Independence Act 1947).

The rule fires only when **all three** hold:

1. the register's answer is a **colonial** body;
2. the register's **own answer for the same cell in 2020** is a successor in the table;
3. the year is **on or after** that successor's founding year.

Nothing else is touched. The register is never overruled by a guess — only by its own later statement about
the same cell, dated by an external source.

## The re-measurement

| | before | after |
|---|---|---|
| 200-sample wrong-rate | 7 / 200 = **3.5%** | **3 / 200 = 1.5% — bar (<2%) MET on the sample** |
| full-scale colonial answers | 237 | **117** (−120 corrected) |
| corrections before the founding year | — | **0** |
| corrections in Newfoundland before 1949 (which would be wrong) | — | **0** |
| Canada answered 1867–1934 | 0 | 115 |
| New Zealand answered 1907+ | 0 | 5 |

Spot-checked: Montreal 1902, Edmonton 1886, Regina 1886, Victoria 1880, Halifax 1918, Rotorua 1911,
Christchurch 1922 — all correctly Canada / New Zealand.

## The environment defect that was faking green

`verify_all.sh` runs Gradle without a memory ceiling. On this 2 GB box the **daemon is OOM-killed**, and the
gate reports `BUILD FAILED — 0 classes`, which reads like a source error and is not one. Cycle 1 lost a turn
to this and misdiagnosed it as "dependency resolution".

Fixed at the source: `eternal/gradle.properties` now carries
`org.gradle.jvmargs=-Xmx1200m -XX:MaxMetaspaceSize=500m -XX:+UseSerialGC`. **Gate after the fix:
`compileJava` PASS, 1,247 classes · `command_surface` 220/220 PASS · `/ee check all` 425 passed, 12 baseline.**

## What is still wrong, named

- **Ibiza 1463** → `(nobody)`; the Crown of Aragon held it. **Galway 1475** → `(nobody)`; the English
  Lordship of Ireland held it. **Mar de Ajó 1969** → `(nobody)`; Argentina. These are **R2-a4b**, the
  empty-answer class, and they are the reason the 1.5% is not yet 0%.
- **117 colonial answers remain at full scale** and only 4 were hand-checked. They are **R2-a4e**.
- **The audit is still a script, not a check.** Until it runs inside `/ee check all` (**R2-a4c**), it cannot
  stop a regression.

## Verdict

**PASS on the cycle, bar MET on the sample, requirement still open.** 3.5% → 1.5% with a sourced rule, 120
wrong answers corrected at full scale for zero risk to the other 9,534, and the loop is now cheap enough that
every future change can be re-audited in three seconds.
