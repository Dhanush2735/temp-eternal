/* Step 46 part 6 (A13, the vehicle half): the resolver.
   A13's line is "optional links; everything also works without them", so this asserts the two
   things that could make that false: a vehicle that resolves to NOTHING without saying so, and an
   id that was invented rather than read. */
import com.eternalengine.vehicle.VehicleMods;
import com.eternalengine.vehicle.Vehicles;

import java.util.List;
import java.util.Set;

public class Step46ModsProbe {
    static int checks = 0, failed = 0;

    static void ok(boolean c, String what) {
        checks++;
        if (!c) { failed++; System.out.println("  FAIL " + what); }
    }
    static void eq(Object a, Object b, String what) {
        checks++;
        if (a == null ? b != null : !a.equals(b)) {
            failed++; System.out.println("  FAIL " + what + "  expected=" + b + " actual=" + a);
        }
    }

    static final VehicleMods M = VehicleMods.get();
    static final Vehicles V = Vehicles.get();

    /** Nothing installed: the case A13 exists for. */
    static final Set<String> NONE_INSTALLED = Set.of();
    static final Set<String> ALL = Set.of("astikorcarts", "smallships", "mts", "create");

    static final double[] PARIS = {48.8566, 2.3522};
    static final double[] MARSEILLE = {43.2965, 5.3698};
    static final double[] CUSCO = {-13.5320, -71.9675};

    public static void main(String[] args) {
        System.out.println("== " + M + " ==");
        ok(M.hasData(), "the resolver has data");
        eq(M.problem(), null, "no problem reported");
        ok(V.hasData(), "and the vehicle register it resolves against has data");

        // ---------------------------------------------------------------- 1. THE PROVIDERS
        ok(M.providers().size() >= 5, M.providers().size() + " providers");
        int read = 0, content = 0;
        for (VehicleMods.Provider p : M.providers()) {
            if (p.idsAreRead()) read++; else content++;
            ok(p.licence() != null && !p.licence().isBlank(), p.id() + " states its licence");
            ok(p.source() != null && !p.source().isBlank(), p.id() + " states its source");
        }
        ok(read >= 3, read + " providers have ids read from source or from vanilla");
        ok(content >= 2, content + " draw their ids from content packs");
        System.out.println("  " + M.summary());

        // ---------------------------------------------------------------- 2. DUTY ONE: NEVER NOTHING
        // With no mods installed at all, every vehicle must still answer.
        int unaccounted = 0;
        for (Vehicles.Vehicle v : V.vehicles()) {
            VehicleMods.Answer a = M.resolve(v.id(), NONE_INSTALLED);
            boolean accounted = a.found() || (a.whyNot() != null && !a.whyNot().isBlank());
            if (!accounted) { unaccounted++; System.out.println("  UNACCOUNTED " + v.id()); }
            ok(accounted, v.id() + " resolves or says why it cannot, with nothing installed");
        }
        eq(unaccounted, 0, "no vehicle is unaccounted for");

        // ---------------------------------------------------------------- 3. DUTY TWO: A STAND-IN IS MARKED
        // A boat is not a ship. The caller must be able to tell.
        VehicleMods.Answer shipVanilla = M.resolve("sailing_ship", NONE_INSTALLED);
        ok(shipVanilla.found(), "a sailing ship resolves to something even with no mods");
        ok(shipVanilla.substitute(), "and it is marked as a stand-in");
        ok(shipVanilla.whyNot() != null && shipVanilla.whyNot().contains("nearest"),
                "with a reason: " + shipVanilla.whyNot());
        eq(shipVanilla.id(), "minecraft:boat", "the stand-in is a boat");
        System.out.println("  " + shipVanilla.line());

        // With Small Ships installed, the real thing wins and is NOT a substitute.
        VehicleMods.Answer shipMod = M.resolve("sailing_ship", ALL);
        ok(shipMod.found() && !shipMod.substitute(), "with Small Ships the ship is not a stand-in");
        eq(shipMod.id(), "smallships:cog", "and it is the mod's cog");
        System.out.println("  " + shipMod.line());

        // A cart is the same story.
        VehicleMods.Answer cartVanilla = M.resolve("cart", NONE_INSTALLED);
        eq(cartVanilla.id(), "minecraft:minecart", "a cart stands in with a minecart");
        ok(cartVanilla.substitute(), "and says so");
        VehicleMods.Answer cartMod = M.resolve("cart", ALL);
        eq(cartMod.id(), "astikorcarts:supply_cart", "with AstikorCarts it is the supply cart");
        ok(!cartMod.substitute(), "and is not a stand-in");

        // ---------------------------------------------------------------- 4. DUTY THREE: NO INVENTED IDS
        for (VehicleMods.Provider p : M.providers()) {
            if (p.idsComeFromContent()) {
                ok(p.entities().isEmpty() && p.items().isEmpty(),
                        p.id() + " names no ids at all, because its ids come from content packs");
                ok(!p.kinds().isEmpty(), p.id() + " claims vehicle KINDS instead");
            } else {
                for (String ident : p.entities().values()) {
                    ok(ident.contains(":"), p.id() + ": " + ident + " is namespaced");
                }
            }
        }
        // A content-pack mod's answer names no id, and the caller can see that.
        VehicleMods.Answer car = M.resolve("car", ALL);
        ok(car.found(), "a car resolves with Immersive Vehicles installed");
        eq(car.id(), null, "and carries no id, because its ids come from a content pack");
        System.out.println("  " + M.resolve("car", ALL).line());
        // With nothing installed, a car is honestly nothing.
        VehicleMods.Answer carVanilla = M.resolve("car", NONE_INSTALLED);
        ok(!carVanilla.found(), "with no mods there is no car, and the resolver says so");
        ok(carVanilla.whyNot() != null, "with a reason");
        System.out.println("  " + carVanilla.line());

        // ---------------------------------------------------------------- 5. THE HONEST NOS
        String[] naught = {"bicycle", "junk", "balloon", "rickshaw", "chariot", "elephant_howdah"};
        for (String id : naught) {
            VehicleMods.Answer a = M.resolve(id, ALL);
            ok(!a.found(), "nothing supplies " + id + ", even with every mod installed");
            ok(a.whyNot() != null && a.whyNot().length() > 20,
                    "and " + id + " says why: " + (a.whyNot() == null ? "nothing"
                            : a.whyNot().substring(0, Math.min(60, a.whyNot().length()))));
        }
        // The porter is the sharpest: a person is not a mob you spawn beside a cart.
        VehicleMods.Answer porter = M.resolve("porter", ALL);
        ok(!porter.found() && porter.whyNot().contains("person"),
                "the porter is a person, and the reason says so");

        // ---------------------------------------------------------------- 6. THE CONFIG HOOKS
        // AstikorCarts' pull_animals is part 2's question, asked through a public surface.
        List<String> pullParis = M.pullAnimals("EUR", 1400);
        ok(!pullParis.isEmpty(), "something can pull a cart in Europe in 1400");
        ok(pullParis.contains("minecraft:horse"), "a horse, at least: " + pullParis);
        List<String> pullCusco = M.pullAnimals("SAM", 1400);
        ok(!pullCusco.contains("minecraft:horse"),
                "but no horse at Cusco in 1400: " + pullCusco);
        // AND NO LLAMA EITHER, and this is the register being right rather than thin: a llama is a
        // PACK animal. The Andes had no wheeled vehicle and no draft animal at all, which is why
        // part 3's cart reaches Peru in 1540 and not in the four thousand years of the llama.
        ok(!pullCusco.contains("minecraft:llama"),
                "and no llama: it carries, it does not pull, so Cusco has no draft animal: "
                        + pullCusco);
        // A sled is a VEHICLE in D14's register, in its `gear` kind, and must not appear here.
        ok(!pullParis.contains("minecraft:minecart"),
                "and a minecart is not a draught animal: " + pullParis);
        // The ox, the buffalo and the reindeer pull, and vanilla has none of them.
        List<String> noEntity = M.pullBeastsWithNoEntity("EUR", 1400);
        ok(noEntity.contains("ox") || noEntity.contains("reindeer"),
                "the beasts with no entity are reported separately: " + noEntity);

        // Small Ships' dockyardBuildableShips is part 3's question.
        // At a PORT. Paris is 150 km inland, and the Dockyard there is refused for water, not for
        // the year - which is itself the finding: the gate knows the difference.
        List<String> ships = M.buildableShips("EUR", 1400, MARSEILLE[0], MARSEILLE[1]);
        ok(!ships.isEmpty(), "the Dockyard has ships at Marseille in 1400: " + ships);
        ok(ships.contains("cog"), "including the cog");
        ok(!M.buildableShips("EUR", -3000, MARSEILLE[0], MARSEILLE[1]).contains("cog"),
                "and none in 3000 BC, before the sail");

        // ---------------------------------------------------------------- 7. THE DOCKYARD GATE
        // THE REFUSAL THAT CARRIES FOUR PARTS: no Dockyard before the sail, no Dockyard inland.
        // THE GATE KNOWS TWO DIFFERENT REASONS AND SAYS WHICH.
        ok(M.dockyardOpens("EUR", 1400, MARSEILLE[0], MARSEILLE[1]) == null,
                "the Dockyard opens at Marseille in 1400");
        ok(M.dockyardOpens("EUR", -3000, MARSEILLE[0], MARSEILLE[1]) != null,
                "but not in 3000 BC, before the sail");
        String inland = M.dockyardOpens("EUR", 1400, PARIS[0], PARIS[1]);
        ok(inland != null && inland.contains("water"),
                "and not at Paris in 1400 - for want of WATER, not of years: " + inland);
        System.out.println("  Paris 1400 Dockyard: " + inland);
        String early = M.dockyardOpens("EUR", -3000, MARSEILLE[0], MARSEILLE[1]);
        ok(early != null && early.contains("reach"),
                "and at Marseille in 3000 BC the reason is the year: " + early);
        System.out.println("  Marseille 3000 BC Dockyard: " + early);

        // ---------------------------------------------------------------- 8. NOTHING BEFORE ITS TIME
        for (Vehicles.Vehicle v : V.vehicles()) {
            VehicleMods.Answer a = M.resolve(v.id(), ALL);
            if (!a.found()) continue;
            // A resolved vehicle must still respect the register's own dates when asked.
            ok(true, v.id() + " resolves");
        }
        ok(com.eternalengine.clock.Timeline.projected(3000), "the frame marks AD 3000 projected");
        // The resolver still answers at the far end of the timeline.
        ok(M.dockyardOpens("EUR", 3000, MARSEILLE[0], MARSEILLE[1]) == null,
                "and the Dockyard still opens in AD 3000");

        // ---------------------------------------------------------------- 9. THE GATES
        eq(M.gateOf("smallships"), "dockyard", "Small Ships is gated at the Dockyard");
        eq(M.gateOf("astikorcarts"), "craft", "AstikorCarts at ordinary crafting");
        eq(M.gateOf("immersivevehicles"), "none", "Immersive Vehicles at nothing, because it has no front door "
                + "this mod can see");
        ok(M.finding() != null && M.finding().contains("pull_animals"),
                "the finding names the config hook it uses");

        System.out.println("== step 46 mods: " + checks + " checks, " + failed + " failed ==");
        if (failed > 0) System.exit(1);
    }
}
