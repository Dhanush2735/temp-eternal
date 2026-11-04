import java.util.SplittableRandom;

/**
 * How much would a "human-like mind" for villagers cost the server?
 *
 * A stand-alone model of the planned mind (no Minecraft needed), so the cost can be measured
 * before anything is built:
 *   senses   - town news (war, famine, plague, festival, taxes), time of day, is the player near
 *   needs    - hunger, safety, rest, money, company (drift with time and with the news)
 *   feelings - fear, joy, anger, grief (fade, and react to the news through the personality)
 *   traits   - five personality traits, fixed per person
 *   memory   - the last 16 notable moments (what, who, how strong, which year)
 *   friends  - up to 8 people with a trust score (the player is one of them)
 *   decision - 12 possible things to do, each scored from all of the above; the best one wins
 *   speech   - only when talked to: 24 candidate facts scored by job, mood, traits and memory
 *
 * Each person thinks once per second (every 20 ticks), spread evenly over the ticks, which is how
 * the mod already spreads its work. The probe reports milliseconds per server tick (a tick has 50).
 * Usage: java MindCostProbe.java
 */
public class MindCostProbe {

    static final int NEEDS = 5, FEEL = 4, TRAITS = 5, NEWS = 5, ACTIONS = 12, MEM = 16, FRIENDS = 8;
    static final int INPUTS = NEEDS + FEEL + TRAITS + NEWS + 2; // + time-of-day curve + player-near
    static final int FLEE = 7, CELEBRATE = 8, GREET = 9;
    static final int FACTS = 24;

    static final class Mind {
        final float[] needs = new float[NEEDS];
        final float[] feel = new float[FEEL];
        final float[] traits = new float[TRAITS];
        final int[] memWhat = new int[MEM];
        final int[] memWho = new int[MEM];
        final float[] memStrength = new float[MEM];
        final int[] memYear = new int[MEM];
        int memHead;
        final int[] friendId = new int[FRIENDS];
        final float[] trust = new float[FRIENDS];
        int friends;
        int town, activity, job;
        double x, z;
    }

    static final class Town {
        float war, famine, plague, festival, taxes;
        // the light version for background people: one mood per town
        final float[] mood = new float[FEEL];
        final float[] needs = new float[NEEDS];
    }

    static float[][] weights;   // ACTIONS x INPUTS
    static float[][] hourCurve; // ACTIONS x 24
    static float[][] factWeights; // FACTS x (jobs 8 + FEEL + TRAITS)

    static float clamp(float v) { return v < 0f ? 0f : (v > 1f ? 1f : v); }

    static int think(Mind m, Town t, int hour, double px, double pz, int year, SplittableRandom r) {
        // senses
        double dx = m.x - px, dz = m.z - pz;
        boolean playerNear = dx * dx + dz * dz < 16 * 16;

        // needs drift with time and the town's news
        float[] n = m.needs;
        n[0] = clamp(n[0] + 0.010f + t.famine * 0.05f);                      // hunger
        n[1] = clamp(n[1] - 0.010f + t.war * 0.04f + t.plague * 0.02f);      // feeling unsafe
        n[2] = clamp(n[2] + (hour >= 21 || hour < 5 ? 0.03f : 0.005f));      // tiredness
        n[3] = clamp(n[3] + t.taxes * 0.01f);                                // money worries
        n[4] = clamp(n[4] + 0.005f);                                         // loneliness

        // feelings fade, then react through the personality
        float[] f = m.feel, tr = m.traits;
        for (int i = 0; i < FEEL; i++) {
            f[i] *= 0.97f;
        }
        f[0] = clamp(f[0] + t.war * 0.05f * (0.5f + tr[4]));       // fear, more if anxious
        f[1] = clamp(f[1] + t.festival * 0.05f * (0.5f + tr[2]));  // joy, more if outgoing
        f[2] = clamp(f[2] + t.taxes * 0.02f * (1.5f - tr[3]));     // anger, more if harsh
        f[3] = clamp(f[3] + t.plague * 0.03f);                     // grief

        // trust in the player, if they are a friend
        float playerTrust = 0f;
        for (int i = 0; i < m.friends; i++) {
            if (m.friendId[i] == 0) {
                playerTrust = m.trust[i];
                break;
            }
        }

        // decision: score every possible action from everything above
        int best = 0;
        float bestScore = -1e9f;
        for (int a = 0; a < ACTIONS; a++) {
            float[] w = weights[a];
            float s = 0f;
            int k = 0;
            for (int i = 0; i < NEEDS; i++) s += w[k++] * n[i];
            for (int i = 0; i < FEEL; i++) s += w[k++] * f[i];
            for (int i = 0; i < TRAITS; i++) s += w[k++] * tr[i];
            s += w[k++] * t.war + w[k++] * t.famine + w[k++] * t.plague + w[k++] * t.festival + w[k++] * t.taxes;
            s += w[k++] * hourCurve[a][hour];
            s += w[k] * (playerNear ? 1f : 0f);
            if (a == GREET && playerNear) {
                s += playerTrust;
            }
            s += (float) (r.nextDouble() * 0.05d); // a little chance, so people are not machines
            if (s > bestScore) {
                bestScore = s;
                best = a;
            }
        }

        // doing it eases the matching need
        if (best < NEEDS) {
            n[best] = clamp(n[best] - 0.2f);
        }

        // remember notable moments
        if (best != m.activity && (best == FLEE || best == CELEBRATE || (best == GREET && playerNear))) {
            int h = m.memHead;
            m.memWhat[h] = best;
            m.memWho[h] = playerNear ? 0 : -1;
            m.memStrength[h] = bestScore;
            m.memYear[h] = year;
            m.memHead = (h + 1) % MEM;
        }
        m.activity = best;
        return best;
    }

    /** Only when the player talks to them: pick what to say from 24 candidate facts. */
    static int chooseWhatToSay(Mind m, SplittableRandom r) {
        int best = 0;
        float bestScore = -1e9f;
        for (int fct = 0; fct < FACTS; fct++) {
            float[] w = factWeights[fct];
            float s = w[m.job];
            int k = 8;
            for (int i = 0; i < FEEL; i++) s += w[k++] * m.feel[i];
            for (int i = 0; i < TRAITS; i++) s += w[k++] * m.traits[i];
            for (int i = 0; i < MEM; i++) {
                if (m.memWhat[i] == fct % ACTIONS) s += 0.1f * m.memStrength[i];
            }
            s += (float) (r.nextDouble() * 0.05d);
            if (s > bestScore) {
                bestScore = s;
                best = fct;
            }
        }
        return best;
    }

    static void updateTownMood(Town t) {
        for (int i = 0; i < FEEL; i++) t.mood[i] *= 0.97f;
        t.mood[0] = clamp(t.mood[0] + t.war * 0.05f);
        t.mood[1] = clamp(t.mood[1] + t.festival * 0.05f);
        t.mood[2] = clamp(t.mood[2] + t.taxes * 0.02f);
        t.mood[3] = clamp(t.mood[3] + t.plague * 0.03f);
        t.needs[0] = clamp(t.needs[0] + 0.01f + t.famine * 0.05f - 0.01f);
        t.needs[1] = clamp(t.needs[1] + t.war * 0.04f - 0.01f);
    }

    static Mind[] makeMinds(int count, int towns, SplittableRandom r) {
        Mind[] minds = new Mind[count];
        for (int i = 0; i < count; i++) {
            Mind m = new Mind();
            for (int j = 0; j < TRAITS; j++) m.traits[j] = (float) r.nextDouble();
            for (int j = 0; j < NEEDS; j++) m.needs[j] = (float) r.nextDouble() * 0.5f;
            m.friends = r.nextInt(FRIENDS + 1);
            for (int j = 0; j < m.friends; j++) {
                m.friendId[j] = r.nextInt(50);
                m.trust[j] = (float) r.nextDouble();
            }
            m.town = r.nextInt(towns);
            m.job = r.nextInt(8);
            m.x = r.nextDouble() * 256 - 128;
            m.z = r.nextDouble() * 256 - 128;
            minds[i] = m;
        }
        return minds;
    }

    static Town[] makeTowns(int count, SplittableRandom r) {
        Town[] towns = new Town[count];
        for (int i = 0; i < count; i++) {
            Town t = new Town();
            t.war = r.nextDouble() < 0.2 ? 1f : 0f;
            t.famine = r.nextDouble() < 0.1 ? 1f : 0f;
            t.plague = r.nextDouble() < 0.05 ? 1f : 0f;
            t.festival = r.nextDouble() < 0.1 ? 1f : 0f;
            t.taxes = (float) r.nextDouble();
            towns[i] = t;
        }
        return towns;
    }

    static long sink;

    /** Average milliseconds per tick when every person thinks once per second (1/20 of them per tick). */
    static double msPerTick(Mind[] minds, Town[] towns, int ticks, SplittableRandom r) {
        int perTick = Math.max(1, minds.length / 20);
        int cursor = 0;
        long start = System.nanoTime();
        for (int tick = 0; tick < ticks; tick++) {
            int hour = (tick / 50) % 24;
            for (int i = 0; i < perTick; i++) {
                Mind m = minds[cursor];
                sink += think(m, towns[m.town], hour, 0, 0, 1850, r);
                cursor = (cursor + 1) % minds.length;
            }
        }
        return (System.nanoTime() - start) / 1e6 / ticks;
    }

    static double townMsPerTick(Town[] towns, int ticks) {
        int perTick = Math.max(1, towns.length / 20);
        int cursor = 0;
        long start = System.nanoTime();
        for (int tick = 0; tick < ticks; tick++) {
            for (int i = 0; i < perTick; i++) {
                updateTownMood(towns[cursor]);
                cursor = (cursor + 1) % towns.length;
            }
        }
        return (System.nanoTime() - start) / 1e6 / ticks;
    }

    static long usedHeap() {
        Runtime rt = Runtime.getRuntime();
        for (int i = 0; i < 3; i++) {
            System.gc();
            try { Thread.sleep(50); } catch (InterruptedException ignored) { }
        }
        return rt.totalMemory() - rt.freeMemory();
    }

    public static void main(String[] args) {
        SplittableRandom r = new SplittableRandom(42);
        weights = new float[ACTIONS][INPUTS];
        hourCurve = new float[ACTIONS][24];
        factWeights = new float[FACTS][8 + FEEL + TRAITS];
        for (float[] row : weights) for (int i = 0; i < row.length; i++) row[i] = (float) (r.nextDouble() * 2 - 1);
        for (float[] row : hourCurve) for (int i = 0; i < row.length; i++) row[i] = (float) r.nextDouble();
        for (float[] row : factWeights) for (int i = 0; i < row.length; i++) row[i] = (float) r.nextDouble();

        Town[] towns = makeTowns(200, r);

        // warm up the JIT so the numbers are the steady state a running server sees
        Mind[] warm = makeMinds(5_000, towns.length, r);
        for (int i = 0; i < 20; i++) msPerTick(warm, towns, 2_000, r);

        System.out.println("Mind cost probe (" + Runtime.getRuntime().availableProcessors()
                + " CPU cores, one thread, Java " + System.getProperty("java.version") + ")");
        System.out.println("A server tick has 50 ms. Each person thinks once per second.");
        System.out.println();
        System.out.printf("%-30s %14s %16s%n", "people with a full mind", "ms per tick", "share of a tick");
        int[] sizes = {100, 500, 1_000, 5_000, 20_000};
        for (int size : sizes) {
            Mind[] minds = makeMinds(size, towns.length, r);
            msPerTick(minds, towns, 2_000, r); // settle
            double best = Double.MAX_VALUE;
            for (int run = 0; run < 5; run++) {
                best = Math.min(best, msPerTick(minds, towns, 4_000, r));
            }
            // a pessimistic figure too: the slowest of the runs
            double worst = 0;
            for (int run = 0; run < 5; run++) {
                worst = Math.max(worst, msPerTick(minds, towns, 4_000, r));
            }
            System.out.printf("%-30s %7.4f-%-6.4f %15.3f%%%n", String.format("%,d", size), best, worst, worst / 50 * 100);
        }

        // everyone thinking EVERY tick (20 times a second): the worst case nobody should build
        Mind[] thousand = makeMinds(1_000, towns.length, r);
        long t0 = System.nanoTime();
        int reps = 2_000;
        for (int rep = 0; rep < reps; rep++) {
            for (Mind m : thousand) sink += think(m, towns[m.town], 12, 0, 0, 1850, r);
        }
        double everyTick = (System.nanoTime() - t0) / 1e6 / reps;
        System.out.printf("%n1,000 people thinking EVERY tick (20x a second): %.3f ms per tick%n", everyTick);

        // one thought
        double perThought = everyTick / 1_000 * 1_000; // microseconds
        System.out.printf("One thought of one person: about %.2f microseconds%n", perThought);

        // choosing what to say (only when talked to)
        Mind[] talkers = makeMinds(1_000, towns.length, r);
        for (int i = 0; i < 200_000; i++) sink += chooseWhatToSay(talkers[i % 1_000], r);
        long t1 = System.nanoTime();
        int talks = 1_000_000;
        for (int i = 0; i < talks; i++) sink += chooseWhatToSay(talkers[i % 1_000], r);
        System.out.printf("Choosing what to say when talked to: about %.2f microseconds%n",
                (System.nanoTime() - t1) / 1e3 / talks);

        // the light version for the 100,000 background people: one mood per town
        Town[] manyTowns = makeTowns(5_000, r);
        for (int i = 0; i < 20; i++) townMsPerTick(manyTowns, 2_000);
        System.out.printf("Background people, light version (5,000 town moods, once a second): %.4f ms per tick%n",
                townMsPerTick(manyTowns, 20_000));

        // memory per person
        long before = usedHeap();
        Mind[] big = makeMinds(100_000, towns.length, r);
        long after = usedHeap();
        System.out.printf("Memory: about %d bytes per person (100,000 minds = %.1f MB)%n",
                (after - before) / big.length, (after - before) / 1e6);
        System.out.println("(ignore: " + (sink & 1) + big.length % 2 + ")");
    }
}
