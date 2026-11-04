import net.minecraft.core.BlockPos;
import net.minecraft.core.SectionPos;
import net.minecraft.util.AbortableIterationConsumer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.entity.EntityAccess;
import net.minecraft.world.level.entity.EntityInLevelCallback;
import net.minecraft.world.level.entity.EntitySectionStorage;
import net.minecraft.world.level.entity.Visibility;
import net.minecraft.world.phys.AABB;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.TreeSet;
import java.util.UUID;
import java.util.stream.Stream;

/**
 * The crowd spawner's crash from the user's game (2026-10-12), outside the game
 * (worldfill/probe_crowd_box.sh). It uses Minecraft's own entity storage, EntitySectionStorage, the class in
 * the user's stack trace, with test people placed around the chunk the user stood in (Hyderabad, block
 * 10070060, -2031337: chunk 629378, -126959), and asks it for the people in a chunk's box twice:
 *
 *   1. with the box line as it was before the fix (copied word for word): it must fail with the exact error
 *      from the user's log, and the probe measures how long the failing call took;
 *   2. with CrowdFigures.occupiedBox, the fixed code itself (called by reflection): no error, and exactly the
 *      people in and around that chunk, at any height.
 *
 * The same at chunk 0,0 (a normal world) and at a chunk near the world border. Exit code 1 if anything fails.
 */
public class CrowdBoxProbe {
    private static final String USER_ERROR =
            "Start element (9223367638808264704) is larger than end element (-9223372036854775808)";
    private static int pass;
    private static int fail;

    /** A test person: only what the entity storage needs (a position and a body box). */
    static final class Person implements EntityAccess {
        private static int next = 1;
        final int id = next++;
        final UUID uuid = UUID.randomUUID();
        final String name;
        final double x;
        final double y;
        final double z;

        Person(String name, double x, double y, double z) {
            this.name = name;
            this.x = x;
            this.y = y;
            this.z = z;
        }

        @Override public int getId() { return id; }
        @Override public UUID getUUID() { return uuid; }
        @Override public BlockPos blockPosition() { return BlockPos.containing(x, y, z); }
        @Override public AABB getBoundingBox() { return new AABB(x - 0.3, y, z - 0.3, x + 0.3, y + 1.8, z + 0.3); }
        @Override public void setLevelCallback(EntityInLevelCallback callback) { }
        @Override public Stream<? extends EntityAccess> getSelfAndPassengers() { return Stream.of(this); }
        @Override public Stream<? extends EntityAccess> getPassengersAndSelf() { return Stream.of(this); }
        @Override public void setRemoved(Entity.RemovalReason reason) { }
        @Override public boolean shouldBeSaved() { return false; }
        @Override public boolean isAlwaysTicking() { return false; }
    }

    public static void main(String[] args) throws Exception {
        Method fixed = Class.forName("com.eternalengine.population.CrowdFigures")
                .getDeclaredMethod("occupiedBox", int.class, int.class);
        fixed.setAccessible(true);

        EntitySectionStorage<Person> storage = new EntitySectionStorage<>(Person.class, key -> Visibility.TRACKED);
        // Around the user's chunk. Its centre is block 10070056, -2031336.
        double cx = 629378 * 16 + 8.0;
        double cz = -126959 * 16 + 8.0;
        List<Person> all = new ArrayList<>();
        all.add(new Person("A in the chunk, on the ground", cx + 3, 600, cz - 2));
        all.add(new Person("B in the chunk, deep down", cx - 5, -1500, cz + 4));
        all.add(new Person("C just east of the chunk", cx + 13, 600, cz));
        all.add(new Person("D two chunks east", cx + 40, 600, cz));
        all.add(new Person("E two chunks north", cx, 600, cz - 40));
        // Around chunk 0,0 (centre 8, 8): a normal world.
        all.add(new Person("F at 0,0, on the ground", 8 + 2, 64, 8 + 2));
        all.add(new Person("G at 0,0, far out east", 8 + 500, 64, 8));
        for (Person p : all) {
            storage.getOrCreateSection(SectionPos.asLong(p.blockPosition())).add(p);
        }

        System.out.println("== The user's chunk: Hyderabad, chunk 629378, -126959 ==");
        oldBox(storage, 629378, -126959);
        newBox(storage, fixed, 629378, -126959, "A in the chunk, on the ground", "B in the chunk, deep down",
                "C just east of the chunk");

        System.out.println();
        System.out.println("== A normal world: chunk 0, 0 ==");
        oldBox(storage, 0, 0);
        newBox(storage, fixed, 0, 0, "F at 0,0, on the ground");

        System.out.println();
        System.out.println("== Near the world border: chunk 1874999, -1874999 (nobody there) ==");
        newBox(storage, fixed, 1874999, -1874999);

        System.out.println();
        System.out.println("SUMMARY pass=" + pass + " fail=" + fail);
        System.exit(fail == 0 ? 0 : 1);
    }

    /** The box line as it was in CrowdFigures.occupiedInChunk before the fix, word for word. */
    @SuppressWarnings("IntegerDivisionInFloatingPointContext")
    private static AABB boxAsItWas(int chunkX, int chunkZ) {
        final int CHUNK_SIDE = 16;
        double centreX = chunkX * CHUNK_SIDE + CHUNK_SIDE / 2.0d;
        double centreZ = chunkZ * CHUNK_SIDE + CHUNK_SIDE / 2.0d;
        AABB box = new AABB(centreX - CHUNK_SIDE, centreX + CHUNK_SIDE, Integer.MIN_VALUE / 4,
                Integer.MAX_VALUE / 4, centreZ - CHUNK_SIDE, centreZ + CHUNK_SIDE);
        return box;
    }

    private static void oldBox(EntitySectionStorage<Person> storage, int chunkX, int chunkZ) {
        AABB box = boxAsItWas(chunkX, chunkZ);
        int from = SectionPos.posToSectionCoord(box.minX - 2.0);
        int to = SectionPos.posToSectionCoord(box.maxX + 2.0);
        System.out.printf(Locale.ROOT, "  the box as it was: x %.0f .. %.0f, so Minecraft walks %,d slices of X (%,d to %,d)%n",
                box.minX, box.maxX, (long) to - from + 1, from, to);
        long t0 = System.nanoTime();
        try {
            storage.getEntities(box, p -> AbortableIterationConsumer.Continuation.CONTINUE);
            report(false, "the box as it was fails with the user's error", "it did not fail");
        } catch (IllegalArgumentException e) {
            double ms = (System.nanoTime() - t0) / 1e6;
            report(USER_ERROR.equals(e.getMessage()),
                    String.format(Locale.ROOT, "the box as it was fails with the user's exact error, after %.0f ms"
                            + " of walking %,d empty slices: \"%s\"", ms, 2097151L - from + 1, e.getMessage()),
                    "a different message: " + e.getMessage());
        }
    }

    private static void newBox(EntitySectionStorage<Person> storage, Method fixed, int chunkX, int chunkZ,
                               String... expected) throws Exception {
        AABB box = (AABB) fixed.invoke(null, chunkX, chunkZ);
        boolean shape = box.minX == chunkX * 16 - 8 && box.maxX == chunkX * 16 + 24
                && box.minZ == chunkZ * 16 - 8 && box.maxZ == chunkZ * 16 + 24
                && box.minY <= -500_000_000 && box.maxY >= 500_000_000;
        report(shape, String.format(Locale.ROOT, "CrowdFigures.occupiedBox: x %.0f .. %.0f, z %.0f .. %.0f, every"
                + " height (the chunk and 8 blocks around it)", box.minX, box.maxX, box.minZ, box.maxZ),
                "wrong shape: " + box);
        TreeSet<String> found = new TreeSet<>();
        long t0 = System.nanoTime();
        try {
            storage.getEntities(box, p -> {
                found.add(p.name);
                return AbortableIterationConsumer.Continuation.CONTINUE;
            });
        } catch (RuntimeException e) {
            report(false, "the fixed box works", e.toString());
            return;
        }
        double ms = (System.nanoTime() - t0) / 1e6;
        TreeSet<String> want = new TreeSet<>(List.of(expected));
        report(found.equals(want), String.format(Locale.ROOT, "the fixed box works in %.3f ms and finds exactly %s",
                ms, want.isEmpty() ? "nobody" : want), "found " + found + ", expected " + want);
    }

    private static void report(boolean ok, String what, String why) {
        if (ok) {
            pass++;
            System.out.println("  PASS " + what);
        } else {
            fail++;
            System.out.println("  FAIL " + what + " -- " + why);
        }
    }
}
