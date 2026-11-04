#!/usr/bin/env python3
"""Lifts TerraOsmBridge's step-36 hooks into a runner that compiles without Forge.

TerraOsmBridge needs Forge and Minecraft to compile, but the hooks themselves are plain Java
over the mod's own registers. This pulls the step-36 section out, dedents it one level so it sits
at the top of a class, makes the hook methods static, and wraps it in a runner with a slf4j
stand-in for the logger. Same trick as worldfill/probe_sky.sh used for the step-35 hooks.

Usage: probe_life_lifthooks.py <TerraOsmBridge.java> <HooksRun.java>
"""
import sys

HOOK_SIGNATURES = [
    "public List<Disaster> disastersAt(double lat",
    "public String disasterLine(double lat",
    "public List<BuildingState> buildingLifeAt(double lat",
    "public String buildingLifeLine(double lat",
    "public List<PlayerBuilding> playerBuildingsIn(int year",
    "public PlayerEdits.Jump playerJump(int fromYear",
]

RUNNER = '''package com.eternalengine.life;

import com.eternalengine.buildings.BuildingLife;
import com.eternalengine.buildings.FamousBuildings;
import com.eternalengine.buildings.PlayerEdits;
import com.eternalengine.civilization.Disasters;

import java.util.ArrayList;
import java.util.List;

/** TerraOsmBridge's step-36 hooks, lifted out of the mod so they can be run without Forge. */
public final class HooksRun {

    private static final org.slf4j.Logger LOGGER =
            org.slf4j.LoggerFactory.getLogger(HooksRun.class);

@@HOOKS@@
    static void show(String what, Object o) {
        System.out.println("   " + what + ": " + o);
    }

    static String firstDisaster(double lat, double lon, int year) {
        List<Disaster> l = disastersAt(lat, lon, year);
        if (l.isEmpty()) {
            return "nothing recorded";
        }
        return l.get(0).name() + " (damage " + String.format("%.2f", l.get(0).damage()) + ")";
    }

    static String playerState(int year, List<String> branches, List<Integer> diverge) {
        List<PlayerBuilding> l = playerBuildingsIn(year, branches, diverge);
        if (l.isEmpty()) {
            return "nothing of theirs here";
        }
        return l.get(0).name() + " = " + l.get(0).phase();
    }

    public static void main(String[] args) {
        System.out.println("\\n== B27: what struck here ==");
        show("Pompeii AD 79", firstDisaster(40.749, 14.487, 79));
        show("Lisbon 1755", firstDisaster(38.722, -9.139, 1755));
        show("Krakatau 1883", firstDisaster(-6.10, 105.42, 1883));
        show("London 1349", disasterLine(51.514, -0.090, 1349));
        show("Ur 2500 BC", firstDisaster(30.963, 46.103, -2500));

        System.out.println("\\n== B10: what state the buildings are in ==");
        show("Rome AD 1349", buildingLifeLine(41.890, 12.492, 1349, 12.0, 6));
        for (BuildingState b : buildingLifeAt(41.890, 12.492, 1349, 12.0, 3)) {
            show("   one", b.name() + " = " + b.phase()
                    + " (" + String.format("%.2f", b.condition()) + ") "
                    + (b.cause().isEmpty() ? "" : "<- " + b.cause()));
        }
        show("Pompeii AD 80", buildingLifeLine(40.749, 14.487, 80, 12.0, 6));
        show("London AD 1667", buildingLifeLine(51.514, -0.090, 1667, 12.0, 6));

        System.out.println("\\n== B21: what the player built ==");
        PlayerEdits p = new PlayerEdits();
        p.record(PlayerEdits.Kind.BUILD, "house by the Forum", 41.891, 12.485, 100,
                PlayerEdits.MAIN, "uuid-1", "");
        setPlayerEdits(p);
        List<String> branches = List.of(PlayerEdits.MAIN);
        List<Integer> diverge = List.of(PlayerEdits.NO_DIVERGENCE);
        show("AD 90", playerState(90, branches, diverge));
        show("AD 1349", playerState(1349, branches, diverge));
        show("jump 1349 -> 90", playerJump(1349, 90, branches, diverge).line());
        show("jump 90 -> 1349", playerJump(90, 1349, branches, diverge).line());
    }
}
'''


def main():
    src, dst = sys.argv[1], sys.argv[2]
    lines = open(src, encoding="utf-8").read().splitlines(keepends=True)
    i = next(n for n, l in enumerate(lines) if "step 36: what struck here" in l)
    j = next(n for n, l in enumerate(lines)
             if n > i and "private static class CachedResult {" in l)
    hooks = "".join(lines[i:j])
    hooks = "\n".join((x[4:] if x.startswith("    ") else x) for x in hooks.split("\n"))
    for sig in HOOK_SIGNATURES:
        hooks = hooks.replace(sig, sig.replace("public ", "public static "), 1)
    open(dst, "w", encoding="utf-8").write(RUNNER.replace("@@HOOKS@@", hooks))
    print("lifted the step-36 hooks")


if __name__ == "__main__":
    main()
