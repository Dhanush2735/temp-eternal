import com.eternalengine.civilization.HistoryGazetteer;
import com.eternalengine.player.InWorldInterventionDetector;
import com.eternalengine.player.PlayerAction;
import com.eternalengine.player.PlayerActionType;

import java.util.Optional;
import java.util.UUID;

/**
 * <b>A player teleports to 28.6019164, 77.2144645 in 1948 and acts against Nathuram Godse.</b>
 * What does the project actually do? (2026-10-27)
 *
 * <p>This runs the real gazetteer and the real intervention detector. Nothing is stubbed except the world:
 * the sink records the fork instead of building a branch, because there is no Minecraft server here.
 */
public final class Delhi1948Probe {
    private static final double LAT = 28.6019164;
    private static final double LON = 77.2144645;
    private static final int YEAR = 1948;
    private static final UUID PLAYER = UUID.nameUUIDFromBytes("traveller".getBytes());

    public static void main(String[] args) {
        System.out.println("teleport target: " + LAT + ", " + LON + " in " + YEAR);
        System.out.println();

        // 1. What is here?
        Optional<HistoryGazetteer.EventHit> hit = HistoryGazetteer.get().nearestLocalEvent(LAT, LON, YEAR);
        if (hit.isEmpty()) {
            System.out.println("RESULT: no event here at all.");
            return;
        }
        HistoryGazetteer.Event ev = hit.get().event();
        System.out.println("nearest local event : " + ev.name());
        System.out.println("  distance          : " + Math.round(hit.get().distanceKm() * 1000) + " m");
        System.out.println("  radius            : " + ev.radiusKm() + " km   (inside = "
                + (hit.get().distanceKm() <= ev.radiusKm()) + ")");
        System.out.println("  kind              : " + ev.kind() + "  -> effective kind "
                + com.eternalengine.player.EventKind.effective(ev.kind(), ev.name()));
        System.out.println("  live in years     : [" + ev.start() + ", " + ev.end() + ")   active in " + YEAR + " = "
                + ev.activeIn(YEAR));
        System.out.println("  regional pin?     : " + HistoryGazetteer.isRegional(ev));
        System.out.println();

        // 2. Is a hostile kill here even counted?
        String[] names = {"traveller"};
        InWorldInterventionDetector detector = new InWorldInterventionDetector(
                (lat, lon, year) -> HistoryGazetteer.get().nearestLocalEvent(lat, lon, year)
                        .map(h -> new InWorldInterventionDetector.LocatedEvent(
                                h.event().id(), h.event().name(), h.event().lat(), h.event().lon(),
                                h.event().start(), h.event().end(), h.event().radiusKm(), h.event().kind())),
                (event, cause, reason) -> {
                    System.out.println("  >>> FORK FIRED: the engine would now create a branch");
                    System.out.println("      cause: " + reason);
                    return true;
                });

        System.out.println("threshold " + detector.threshold() + " force, and at least 3 separate actions.");
        System.out.println();
        System.out.println("--- A: player kills ONE hostile at the pin (a bodyguard, an attacker) ---");
        observe(detector, PlayerActionType.KILL_HOSTILE, YEAR, "killed=attacker");

        System.out.println();
        System.out.println("--- B: player keeps going, 3 hostile kills ---");
        InWorldInterventionDetector d2 = fresh();
        for (int i = 0; i < 3; i++) {
            observe(d2, PlayerActionType.KILL_HOSTILE, YEAR, "killed=attacker#" + i);
        }
        System.out.println("  force " + d2.forceAt(id()) + " of " + d2.threshold() + "; actions " + d2.actionsAt(id()));

        System.out.println();
        System.out.println("--- C: player kills SIX hostiles at the pin ---");
        InWorldInterventionDetector d3 = fresh();
        for (int i = 0; i < 6; i++) {
            observe(d3, PlayerActionType.KILL_HOSTILE, YEAR, "killed=attacker#" + i);
        }
        System.out.println("  force " + d3.forceAt(id()) + "; actions " + d3.actionsAt(id())
                + "; history changed = " + d3.hasDecided(id()));

        System.out.println();
        System.out.println("--- D: the player kills Godse as a VILLAGER (an ordinary NPC standing there) ---");
        InWorldInterventionDetector d4 = fresh();
        for (int i = 0; i < 6; i++) {
            observe(d4, PlayerActionType.KILL_VILLAGER, YEAR, "killed=npc_nathuram_godse");
        }
        System.out.println("  force " + d4.forceAt(id()) + "  actions " + d4.actionsAt(id())
                + "  (weight of KILL_VILLAGER = "
                + InWorldInterventionDetector.weightOf(PlayerActionType.KILL_VILLAGER) + ")");

        System.out.println();
        System.out.println("--- E: the same six kills in 1955, seven years late ---");
        InWorldInterventionDetector d5 = new InWorldInterventionDetector(
                (lat, lon, year) -> HistoryGazetteer.get().nearestLocalEvent(lat, lon, year)
                        .map(h -> new InWorldInterventionDetector.LocatedEvent(
                                h.event().id(), h.event().name(), h.event().lat(), h.event().lon(),
                                h.event().start(), h.event().end(), h.event().radiusKm(), h.event().kind())),
                (event, cause, reason) -> true);
        for (int i = 0; i < 6; i++) {
            observe(d5, PlayerActionType.KILL_HOSTILE, 1955, "killed=attacker#" + i);
        }
        System.out.println("  force " + d5.forceAt(id()) + "; changed = " + d5.hasDecided(id())
                + "  (the past is not for sale)");
        afterForkEffect();
    }


    // ==================== what the world shows afterwards ====================

    private static void afterForkEffect() {
        String pinId = id();
        System.out.println();
        System.out.println("--- F: what the WORLD shows after the fork ---");

        // The real suppression hook the timeline system installs.
        boolean suppressedBefore = HistoryGazetteer.suppressionFilter().test(pinId);
        HistoryGazetteer.setSuppressionFilter(id -> id.equals(pinId));
        boolean suppressedAfter = HistoryGazetteer.suppressionFilter().test(pinId);
        java.util.Optional<HistoryGazetteer.EventHit> stillThere =
                HistoryGazetteer.get().nearestLocalEvent(LAT, LON, YEAR);
        System.out.println("  pin suppressed before fork : " + suppressedBefore);
        System.out.println("  pin suppressed after fork  : " + suppressedAfter);
        System.out.println("  lookup at the same spot now: " + stillThere
                .map(h -> h.event().name()).orElse("NOTHING - the event is gone from this timeline"));
        HistoryGazetteer.setSuppressionFilter(null);
        System.out.println("  (filter restored)");
    }

    private static String id() {
        return HistoryGazetteer.get().nearestLocalEvent(LAT, LON, YEAR)
                .map(h -> h.event().id()).orElse("?");
    }

    private static InWorldInterventionDetector fresh() {
        return new InWorldInterventionDetector(
                (lat, lon, year) -> HistoryGazetteer.get().nearestLocalEvent(lat, lon, year)
                        .map(h -> new InWorldInterventionDetector.LocatedEvent(
                                h.event().id(), h.event().name(), h.event().lat(), h.event().lon(),
                                h.event().start(), h.event().end(), h.event().radiusKm(), h.event().kind())),
                (event, cause, reason) -> {
                    System.out.println("  >>> FORK FIRED at action " + cause.year() + ": " + reason);
                    return true;
                });
    }

    private static void observe(InWorldInterventionDetector d, PlayerActionType type, int year, String details) {
        PlayerAction a = new PlayerAction(PLAYER, "traveller", type, year, "overworld", 0, 64, 0, details,
                System.currentTimeMillis());
        Optional<String> msg = d.observe(a, LAT, LON);
        System.out.println("  [" + type + "] " + (msg.orElse("(silence)")));
    }
}
