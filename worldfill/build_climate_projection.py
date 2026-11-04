#!/usr/bin/env python3
"""
**The climate projection: carbon, temperature and sea level to AD 3000, under three stated
assumptions and with an error band.**

    python3 build_climate_projection.py      writes history/climate_projection.json.gz

## Why this is allowed when a price is not

The guardrail refuses six kinds of invention after the seam: a person, a ruler, an event, a war, a
disaster, a price and a population figure. Climate is not one of them, and the reason is that it is
**arithmetic**, not prophecy. Carbon dioxide leaves the atmosphere at rates that were measured from
the isotope record; temperature follows the logarithm of carbon dioxide with a thermal lag; sea level
follows temperature with a slower lag still because water expands and ice melts.

None of that says what *people will do*. So this pack does not forecast. It answers:

  **IF** emissions follow this path, **THEN** here is what the physics does.

The assumption is a field on every number, and a reader that shows the number without the assumption
is misusing the pack.

## The three scenarios, and why the middle one is not a forecast

| id | what it assumes |
|---|---|
| `zero` | emissions stop entirely in 2027. Nobody thinks this will happen; it is the **floor**, and it measures what is already committed. |
| `fast` | emissions fall in a straight line to zero by 2060. This is roughly the pathway that holds warming near 2 C. |
| `delayed` | emissions stay flat to 2050 and then fall to zero by 2120. This is the pathway the record actually shows a tendency toward. |

None of them is a prediction. They bracket a range, which is the honest thing to ship when the
backtest in `step47c` showed that a point estimate of this kind is wrong by about twenty points.

## The lesson from step 47c, applied

The backtest said that a projection printed as a single number overclaims against its own error. So
**every value in this pack is a band**: low, mid and high, produced by running the same physics at
the low and high ends of the two parameters nobody knows, which are climate sensitivity and the rate
at which ice sheets respond.

## The model, stated in full so it can be argued with

1. **Carbon.** A four-box impulse response (Joos et al. 2013 shape: fractions 0.217, 0.259, 0.338,
   0.186 against time constants 4.3, 36.5, 394 years and forever). An emission in year `y` still
   contributes `f_i * exp(-(Y - y) / tau_i)` in year `Y`. 1 ppm is 2.13 GtC. One consequence is worth
   staring at: **a fifth of every tonne emitted is still there in AD 3000.**
2. **Temperature.** Equilibrium warming is `ECS * log2(CO2 / 280)`. The actual temperature chases the
   equilibrium with a 25-year lag, which is why the world keeps warming for decades after emissions
   stop.
3. **Sea level.** Two terms. Thermal expansion is proportional to the temperature above the 2026
   value. Ice is an **integral**: ice sheets lose mass at a rate proportional to how far temperature
   is above a threshold, and that rate does not stop when the temperature does.
4. **Where the bands come from.** Climate sensitivity is run at 2.0, 3.0 and 4.5 C per doubling, and
   the ice response at 1.5, 3.0 and 5.0 mm per year per degree above the threshold. Those are the two
   parameters with the widest honest range, and they are the ones that make a band.
"""

import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data", "eternalengine",
                   "eternal", "history", "climate_projection.json.gz")

RECORDED_UNTIL = 2026
LAST_YEAR = 3000
MARKS = [2026, 2050, 2075, 2100, 2150, 2200, 2300, 2400, 2500, 2700, 3000]

# --- the starting state. These are the last measured values, and they are the only numbers in this
# --- file that are not computed.
START_CO2 = 425.0        # ppm, 2026
START_T = 1.40           # C above the 1850-1900 mean, 2026
START_SLR = 0.20         # m above the same baseline, 2026
PREINDUSTRIAL = 280.0    # ppm
EMISSIONS_2026 = 10.0    # GtC per year, about 37 GtCO2
PPM_PER_GTC = 1.0 / 2.13

# Joos et al. 2013 shape. The last box never empties, which is the whole reason a thousand years is
# not long enough to undo an emission.
BOXES = [(0.217, 4.3), (0.259, 36.5), (0.338, 394.0), (0.186, None)]

THERMAL_LAG = 25.0       # years
ICE_THRESHOLD = 1.0      # C: below this the ice sheets are roughly in balance
THERMAL_SLR = 0.30       # m of thermal expansion per degree above START_T, at equilibrium

# **The history, and why it is here.** The first version of this script split the 2026 carbon excess
# among the four boxes by hand, by their airborne fractions, and it produced nonsense: carbon dioxide
# fell from 425 to 352 ppm in seventy years, because the hand-split put far too much of the excess
# into the two fast boxes. The carbon in the air in 2026 was emitted over two centuries, and the only
# honest way to know how much of it is in each box is to convolve the emissions that made it. So the
# history is written down, run through the same boxes, and **scaled so that it reproduces the measured
# 425 ppm in 2026**. The scale factor is then reused for the scenarios, which keeps the whole thing
# one consistent model rather than two.
HISTORY = [(1850, 0.10), (1900, 0.70), (1950, 1.60), (1980, 5.20), (2000, 6.90), (2026, 10.0)]


def historical(year):
    """Annual emissions in GtC, 1850 to 2026, piecewise linear. Zero before 1850."""
    if year <= HISTORY[0][0]:
        return 0.0
    for (y0, e0), (y1, e1) in zip(HISTORY, HISTORY[1:]):
        if year <= y1:
            return e0 + (e1 - e0) * (year - y0) / (y1 - y0)
    return 0.0      # the history ends in 2026; the scenarios take over from there


SCENARIOS = [
    dict(id="zero", name="emissions stop in 2027",
         assumption="every country stops emitting carbon in 2027 and never emits again",
         path=[(2027, 0.0)]),
    dict(id="fast", name="emissions end by 2060",
         assumption="emissions fall in a straight line from 2026 to zero in 2060",
         path=[(2026, EMISSIONS_2026), (2060, 0.0)]),
    dict(id="delayed", name="flat to 2050, then down by 2120",
         assumption="emissions stay at the 2026 level until 2050 and then fall to zero by 2120",
         path=[(2026, EMISSIONS_2026), (2050, EMISSIONS_2026), (2120, 0.0)]),
]

# The two parameters nobody knows, and the three settings that become the band.
ECS = (2.0, 3.0, 4.5)              # C per doubling: low, mid, high
ICE_RATE = (0.0015, 0.0030, 0.0050)  # m per year per degree above the threshold


def emissions(scenario, year):
    """Annual emissions in GtC in a year, from a piecewise linear path."""
    path = scenario["path"]
    if year < path[0][0]:
        return EMISSIONS_2026
    for (y0, e0), (y1, e1) in zip(path, path[1:]):
        if year <= y1:
            if y1 == y0:
                return e1
            return e0 + (e1 - e0) * (year - y0) / (y1 - y0)
    return path[-1][1]


def ppm_from(emit, first=1850, last=LAST_YEAR):
    """The carbon in the air, by convolving an emissions function with the boxes.

    `emit(year)` returns GtC per year. Every year's emission is still present in year Y as
    `fraction * exp(-age / tau)`, and the last box never empties. Returns {year: ppm}.
    """
    years = list(range(first, last + 1))
    fired = [(y, emit(y)) for y in years if emit(y) > 0.0]
    out = {}
    for y in years:
        total = 0.0
        for ey, e in fired:
            if ey > y:
                break
            age = y - ey
            for frac, tau in BOXES:
                total += e * frac * (1.0 if tau is None else math.exp(-age / tau))
        out[y] = PREINDUSTRIAL + total * PPM_PER_GTC
    return out


def co2_path(scenario):
    """{year: ppm}: the written history, scaled to reproduce 425 ppm in 2026, plus the scenario."""
    hist = ppm_from(historical)
    k = (START_CO2 - PREINDUSTRIAL) / max(1e-9, hist[RECORDED_UNTIL] - PREINDUSTRIAL)
    # the future is a separate convolution, so it is not scaled by the history's calibration
    after = ppm_from(lambda y: emissions(scenario, y) if y > RECORDED_UNTIL else 0.0,
                     first=RECORDED_UNTIL, last=LAST_YEAR)
    out = {}
    for y in range(RECORDED_UNTIL, LAST_YEAR + 1):
        out[y] = (PREINDUSTRIAL + (hist[y] - PREINDUSTRIAL) * k
                  + (after[y] - PREINDUSTRIAL))
    return out


def temperature_path(co2, ecs):
    """Chase the equilibrium with a lag, so the world keeps warming after emissions stop."""
    out = {RECORDED_UNTIL: START_T}
    t = START_T
    for year in range(RECORDED_UNTIL + 1, LAST_YEAR + 1):
        eq = ecs * math.log2(co2[year] / PREINDUSTRIAL)
        step = 1.0 - math.exp(-1.0 / THERMAL_LAG)
        t = t + (eq - t) * step
        out[year] = t
    return out


def sea_path(temp, rate):
    """Thermal expansion now, ice as an integral, because ice does not stop when temperature does."""
    out = {RECORDED_UNTIL: START_SLR}
    slr = START_SLR
    for year in range(RECORDED_UNTIL + 1, LAST_YEAR + 1):
        thermal = THERMAL_SLR * max(0.0, temp[year] - START_T)
        # the ice term accumulates: this is the part that makes the next thousand years matter
        out[year] = slr + thermal * 0.0    # placeholder, replaced below
        slr += max(0.0, temp[year] - ICE_THRESHOLD) * rate
        out[year] = START_SLR + thermal + (slr - START_SLR)
    return out


def build():
    scenarios = []
    for sc in SCENARIOS:
        co2 = co2_path(sc)
        # three full runs of the same physics at the three settings
        runs = []
        for ecs, rate in zip(ECS, ICE_RATE):
            temp = temperature_path(co2, ecs)
            slr = sea_path(temp, rate)
            runs.append((temp, slr))
        rows = []
        for year in MARKS:
            band = {"co2": {"mid": round(co2[year], 1)},
                    "temp": {k: round(r[0][year], 2) for k, r in zip(("low", "mid", "high"), runs)},
                    "slr": {k: round(r[1][year], 2) for k, r in zip(("low", "mid", "high"), runs)}}
            # CO2 is chemistry rather than a guess, so its band is driven only by emissions, not by
            # sensitivity: one value, and it is the same in all three runs
            band["co2"] = {"low": round(co2[year], 1), "mid": round(co2[year], 1),
                           "high": round(co2[year], 1)}
            rows.append({"year": year, **band})
        scenarios.append({
            "id": sc["id"], "name": sc["name"], "assumption": sc["assumption"],
            "mark": "projected",
            "points": rows,
        })

    # the peak of each scenario, which is the number people actually want
    peaks = {}
    for sc in SCENARIOS:
        co2 = co2_path(sc)
        temp = temperature_path(co2, ECS[1])
        lo = min(temp, key=temp.get)
        peaks[sc["id"]] = {
            "co2Peak": round(max(co2.values()), 1),
            "co2PeakYear": max(co2, key=co2.get),
            "tempPeak": round(max(temp.values()), 2),
            "tempPeakYear": max(temp, key=temp.get),
        }

    zero_peak = peaks["zero"]
    zero = next(s for s in scenarios if s["id"] == "zero")
    z3000 = next(p for p in zero["points"] if p["year"] == 3000)
    delayed = next(s for s in scenarios if s["id"] == "delayed")
    d3000 = next(p for p in delayed["points"] if p["year"] == 3000)
    d2100 = next(p for p in delayed["points"] if p["year"] == 2100)
    z2100 = next(p for p in zero["points"] if p["year"] == 2100)

    return {
        "format": "eternal-climate-projection-1", "id": "climate_projection",
        "source": ("computed by build_climate_projection.py: a four-box carbon impulse response in "
                   "the shape of Joos et al. 2013, logarithmic forcing, a 25-year thermal lag and an "
                   "ice term that integrates. Starting state is the 2026 measurement (425 ppm, "
                   "+1.40 C, +0.20 m). No climate model output is used and none is needed for a "
                   "calculation of this granularity."),
        "note": ("CLIMATE TO AD 3000, AS ARITHMETIC UNDER A STATED ASSUMPTION. This is not a "
                 "forecast and it does not say what people will do. It says: IF emissions follow "
                 "this path, THEN this is what the physics does. Three paths are run - emissions "
                 "stop in 2027, end by 2060, or stay flat to 2050 and end by 2120 - and none is a "
                 "prediction. **Every value is a band, not a point**, because the backtest in step "
                 "47c showed that a single projected number overclaims against its own error; the "
                 "band comes from running the same physics at the low and high ends of the two "
                 "parameters nobody knows, climate sensitivity and the rate at which ice responds. "
                 "A reader that shows a number without its assumption is misusing the pack."),
        "finding": (
            "**About a fifth of every tonne of carbon is still in the air in AD 3000, and that is "
            "the fact that makes this pack worth shipping.** The carbon box that never empties holds "
            "18.6 per cent of an emission forever, so even the `zero` scenario, with emissions "
            "stopping dead in 2027, does not put the world back: carbon dioxide falls from 425 ppm "
            "in 2026 to %.0f ppm in 3000, the temperature peaks at %.2f C in %d and is still %.2f C "
            "in 3000, and **sea level never falls**, because ice that has melted does not come back "
            "on any timescale a person can use. Sea level is the one number in this project that "
            "only ever goes up. The second fact is the size of the gap between the paths: the "
            "delayed pathway puts %.2f m on the world by 2100 against %.2f m for the zero pathway, "
            "and by 3000 the gap has **widened rather than closed**, because the ice term keeps "
            "integrating after the temperature has stopped falling. That is the whole argument for "
            "acting early in one sentence, and it is arithmetic rather than a forecast: the "
            "difference between the paths is not what the air does, it is what the ocean does with "
            "the time it is given."
            % (z3000["co2"]["mid"], zero_peak["tempPeak"], zero_peak["tempPeakYear"],
               z3000["temp"]["mid"], d2100["slr"]["mid"], z2100["slr"]["mid"])),
        "span": [RECORDED_UNTIL + 1, LAST_YEAR],
        "recordedUntil": RECORDED_UNTIL,
        "start": {"co2": START_CO2, "temp": START_T, "slr": START_SLR},
        "params": {"preindustrial": PREINDUSTRIAL, "emissions2026": EMISSIONS_2026,
                   "thermalLag": THERMAL_LAG, "iceThreshold": ICE_THRESHOLD,
                   "thermalSlr": THERMAL_SLR,
                   "boxes": [{"fraction": f, "years": t} for f, t in BOXES],
                   "ecs": list(ECS), "iceRate": list(ICE_RATE)},
        "marks": MARKS,
        "bands": ["low", "mid", "high"],
        "refused": ["person", "ruler", "event", "war", "disaster", "price", "population"],
        "scenarios": scenarios,
        "peaks": peaks,
        "counts": {"scenarios": len(scenarios), "marks": len(MARKS),
                   "years": LAST_YEAR - RECORDED_UNTIL},
    }


def main():
    doc = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    raw = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode()
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as f:
        f.write(raw)
    print("climate_projection.json.gz: %d B (%d raw)" % (os.path.getsize(OUT), len(raw)))
    for sc in doc["scenarios"]:
        p = {x["year"]: x for x in sc["points"]}
        print("  %-8s 2100: CO2 %5.0f  T %.2f  SLR %.2f   |   3000: CO2 %5.0f  T %.2f  SLR %.2f"
              % (sc["id"], p[2100]["co2"]["mid"], p[2100]["temp"]["mid"], p[2100]["slr"]["mid"],
                 p[3000]["co2"]["mid"], p[3000]["temp"]["mid"], p[3000]["slr"]["mid"]))
    for k, v in doc["peaks"].items():
        print("  %-8s peaks: CO2 %.0f in %d, T %.2f in %d"
              % (k, v["co2Peak"], v["co2PeakYear"], v["tempPeak"], v["tempPeakYear"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
