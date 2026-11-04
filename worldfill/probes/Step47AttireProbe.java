/* Step 47 part 4 (E21): clothes the player can wear to blend in.
   The claim: three things make a person stand out, and the worst is not fashion but impossibility.
   The mod reports; it does not punish. */
import com.eternalengine.skin.Attire;

import java.util.List;

public class Step47AttireProbe {
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

    /** Stands in for Anachronisms, so this probe runs without a Minecraft classpath. */
    static final Attire.AnachronismCheck NO_MAGIC = (item, year) ->
            !item.contains("ender_pearl") && !item.contains("netherite") && !item.contains("elytra");

    public static void main(String[] args) {
        // ------------------------------------------------ 1. THE LOCAL NORM EXISTS
        List<String> rome = Attire.toBlendIn("rome", 100, false);
        ok(!rome.isEmpty(), "the register can say what a Roman wears: " + rome);
        ok(rome.contains("tunic"), "a tunic");
        List<String> deccan = Attire.toBlendIn("deccan", 1400, false);
        ok(deccan.contains("kurta"), "and what a Deccan artisan wears in 1400: " + deccan);
        System.out.println("  Rome AD 100: " + rome);
        System.out.println("  Deccan 1400: " + deccan);

        // ------------------------------------------------ 2. DRESSED LIKE A LOCAL
        Attire.Reading blend = Attire.read(rome, "rome", 100, NO_MAGIC);
        ok(blend.blends(), "a man in a tunic and a toga in Rome is dressed like a Roman");
        eq(blend.level(), Attire.Level.BLEND, "level BLEND");
        ok(blend.what().contains("toga"), "and the reading says what the locals wear");
        System.out.println("  " + blend.line());

        // ------------------------------------------------ 3. THE WRONG CLOTH IS THE MILDEst
        Attire.Reading tee = Attire.read(List.of("crew_tee"), "rome", 100, NO_MAGIC);
        eq(tee.level(), Attire.Level.FOREIGN, "a T-shirt in Rome is FOREIGN, not IMPOSSIBLE");
        ok(tee.reason().contains("later century"), "and the reason is the century: " + tee.reason());
        System.out.println("  " + tee.line());

        // ------------------------------------------------ 4. METAL BEFORE ITS YEAR
        // THE FORM BEFORE THE MATERIAL. Iron is ancient; iron PLATE is not.
        Attire.Reading plate = Attire.read(List.of("iron_chestplate"), "rome", 100, NO_MAGIC);
        eq(plate.level(), Attire.Level.STRANGE, "an iron chestplate in AD 100 is STRANGE");
        ok(plate.reason().contains("plate armour"), "because the FORM is the problem: "
                + plate.reason());
        System.out.println("  " + plate.line());
        // But an iron SWORD in the same year is ordinary, and this is the pair that matters.
        ok(Attire.read(List.of("iron_sword"), "rome", 100, NO_MAGIC).level()
                != Attire.Level.STRANGE, "an iron sword in AD 100 is not strange at all");
        // And by 1400 a chestplate is ordinary, because it has been invented.
        ok(Attire.read(List.of("iron_chestplate"), "rome", 1400, NO_MAGIC).level()
                != Attire.Level.STRANGE, "and neither is a chestplate by 1400");
        // Mail is older than plate, by most of a millennium.
        ok(Attire.read(List.of("chainmail_chestplate"), "rome", 0, NO_MAGIC).level()
                != Attire.Level.STRANGE, "while mail in AD 0 is ancient by then");
        // Leather is never strange: it is the oldest armour there is.
        eq(Attire.read(List.of("leather_chestplate"), "rome", 100, NO_MAGIC).level(),
                Attire.Level.BLEND, "and leather never is");

        // ------------------------------------------------ 5. THE IMPOSSIBLE OUTRANKS EVERYTHING
        Attire.Reading pearl = Attire.read(List.of("ender_pearl", "tunic"), "rome", 100, NO_MAGIC);
        eq(pearl.level(), Attire.Level.IMPOSSIBLE,
                "an ender pearl outranks the tunic he is wearing with it");
        ok(pearl.reason().contains("does not exist"), "and says why: " + pearl.reason());
        System.out.println("  " + pearl.line());

        // ------------------------------------------------ 6. NAKED IN A DRESSED WORLD
        eq(Attire.read(List.of(), "rome", 100, NO_MAGIC).level(), Attire.Level.STRANGE,
                "wearing nothing where there is a wardrobe is STRANGE");
        // But where the register knows of no wardrobe, being naked is not a fashion error.
        eq(Attire.read(List.of(), "african", -2500, NO_MAGIC).level(), Attire.Level.BLEND,
                "and where there is no wardrobe known, it is not");

        // ------------------------------------------------ 7. THE LEVELS ARE ORDERED
        ok(Attire.Level.IMPOSSIBLE.weight() > Attire.Level.STRANGE.weight(), "impossible > strange");
        ok(Attire.Level.STRANGE.weight() > Attire.Level.FOREIGN.weight(), "strange > foreign");
        ok(Attire.Level.FOREIGN.weight() > Attire.Level.BLEND.weight(), "foreign > blend");
        eq(Attire.levels().size(), 4, "four levels are listed for a command");

        // ------------------------------------------------ 8. IT REPORTS AND DOES NOT PUNISH
        // There is no score, no fine and no damage in any verdict: only a level and a reason.
        for (Attire.Level l : Attire.Level.values()) {
            ok(l.note() != null && l.note().length() > 20,
                    l + " explains what the world is thinking, not what it does about it");
        }
        ok(!Attire.Level.IMPOSSIBLE.note().contains("damage"),
                "and no level mentions a penalty");
        // An unknown culture must not throw.
        ok(Attire.read(List.of("tunic"), "atlantis", 100, NO_MAGIC).level() != null,
                "an unknown culture answers rather than throwing");
        ok(Attire.read(null, "rome", 100, NO_MAGIC).level() != null, "and a null list does too");

        System.out.println("== step 47 attire: " + checks + " checks, " + failed + " failed ==");
        if (failed > 0) System.exit(1);
    }
}
