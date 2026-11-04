import com.eternalengine.clock.WorldCalendar;
import com.eternalengine.knowledge.KnowledgeDate;
import com.eternalengine.terrabridge.TerraTimeBridge;
import com.google.gson.JsonObject;

/**
 * Step 18d: the world's one calendar (WorldCalendar) and the Terra++ speed change (TerraTimeBridge.dayKeepingDate), on
 * made-up Minecraft times, with the mod's real code. No Minecraft server: what needs one (the guard putting the day
 * right, /time set itself) is tested on the test server.
 */
public class CalendarProbe {

    static final long DAY = WorldCalendar.DAY;
    /** 1 January 1948 with Terra++ time at 1x; any day works for the Eternal Engine clock. */
    static final long N = 1806020L * DAY;
    static final int[] SPEEDS = {1, 5, 10, 25, 50};

    static int passed;
    static int failed;

    static void check(boolean ok, String what, String detail) {
        if (ok) {
            passed++;
            System.out.println("  ok   " + what);
        } else {
            failed++;
            System.out.println("  FAIL " + what + " -- " + detail);
        }
    }

    static String l(int key) {
        return KnowledgeDate.label(key);
    }

    static long plusDays(int key, long days) {
        return WorldCalendar.keyOfEpochDay(WorldCalendar.epochDay(key) + days);
    }

    public static void main(String[] args) {
        System.out.println("CalendarProbe (step 18d)");

        String broken = WorldCalendar.selfTest();
        check(broken == null, "the rules /ee check all tests hold", String.valueOf(broken));

        // 1. 1x: three years, every 100 ticks.
        {
            int start = KnowledgeDate.key(1947, 1, 1);
            long[] a = WorldCalendar.anchorFor(start, N, 1);
            int prev = WorldCalendar.dateAt((int) a[0], a[1], 1, N);
            boolean ok = prev == start;
            String bad = ok ? "" : "starts at " + l(prev);
            int changes = 0;
            long end = N + 1097 * DAY;
            for (long t = N; t <= end && ok; t += 100) {
                int k = WorldCalendar.dateAt((int) a[0], a[1], 1, t);
                if (k != prev) {
                    changes++;
                    if (Math.floorMod(t, DAY) != 0 || k != KnowledgeDate.nextDay(prev)) {
                        ok = false;
                        bad = "at tick " + Math.floorMod(t, DAY) + " of a day: " + l(prev) + " -> " + l(k);
                    }
                }
                prev = k;
            }
            check(ok && changes == 1097 && prev == KnowledgeDate.key(1950, 1, 2),
                    "1x: over three years (1947-1949, with the leap day of 1948) the date changes once per Minecraft day,"
                            + " exactly when Minecraft's day changes (6 in the morning), by one day",
                    bad + " changes=" + changes + " end=" + l(prev));
        }

        // 2. Faster speeds.
        {
            boolean ok = true;
            String bad = "";
            for (int r : new int[] {5, 10, 25, 50}) {
                int start = KnowledgeDate.key(1948, 9, 1);
                long[] a = WorldCalendar.anchorFor(start, N, r);
                int prev = start;
                for (long t = N; t <= N + 30 * DAY && ok; t += 60) {
                    int k = WorldCalendar.dateAt((int) a[0], a[1], r, t);
                    if (k < prev) {
                        ok = false;
                        bad = r + "x went back at " + t;
                    }
                    if (Math.floorMod(t - N, DAY) == 0 && k != plusDays(start, (t - N) / DAY * r)) {
                        ok = false;
                        bad = r + "x after " + (t - N) / DAY + " days: " + l(k);
                    }
                    prev = k;
                }
            }
            check(ok, "5x, 10x, 25x, 50x: after n Minecraft days the date is n x speed days on, and it never goes back"
                    + " tick by tick", bad);
        }

        // 3. Speed changes at odd times of day.
        {
            long[][] changes = {{N + 6000, 50}, {N + DAY + 12000, 5}, {N + 2 * DAY + 21000, 1}, {N + 4 * DAY + 3000, 25},
                    {N + 4 * DAY + 3001, 10}, {N + 6 * DAY + 17000, 1}};
            int rate = 1;
            int start = KnowledgeDate.key(1948, 9, 13);
            long[] a = WorldCalendar.anchorFor(start, N, rate);
            int prev = start;
            int next = 0;
            boolean ok = true;
            String bad = "";
            long lastChange = changes[changes.length - 1][0];
            for (long t = N; t <= N + 12 * DAY && ok; t++) {
                if (next < changes.length && t == changes[next][0]) {
                    int today = WorldCalendar.dateAt((int) a[0], a[1], rate, t);
                    int newRate = (int) changes[next][1];
                    long[] b = WorldCalendar.anchorFor(today, t, newRate);
                    if (WorldCalendar.dateAt((int) b[0], b[1], newRate, t) != today) {
                        ok = false;
                        bad = rate + "x -> " + newRate + "x moved the date";
                    }
                    a = b;
                    rate = newRate;
                    next++;
                }
                int k = WorldCalendar.dateAt((int) a[0], a[1], rate, t);
                if (k < prev) {
                    ok = false;
                    bad = "went back at tick " + t;
                }
                if (t > lastChange && k != prev && Math.floorMod(t, DAY) != 0) {
                    ok = false;
                    bad = "after going back to 1x the date changed at tick " + Math.floorMod(t, DAY) + " of a day";
                }
                prev = k;
            }
            check(ok, "a new speed keeps the date (1x->50x at noon, 50x->5x in the evening, 5x->1x at 3 in the night,"
                    + " 25x and 10x a tick apart, back to 1x): never back, and at 1x again it changes at 6 in the morning", bad);
        }

        // 4. /ee date: awkward dates at awkward times and speeds.
        {
            int[] dates = {KnowledgeDate.key(1948, 2, 29), KnowledgeDate.key(1948, 12, 31), KnowledgeDate.key(1949, 3, 1),
                    KnowledgeDate.key(-44, 3, 15), KnowledgeDate.key(-3000, 1, 1), KnowledgeDate.key(2000, 2, 29),
                    KnowledgeDate.key(1900, 2, 28), KnowledgeDate.key(1, 1, 1), KnowledgeDate.key(0, 12, 31)};
            boolean ok = true;
            String bad = "";
            for (int key : dates) {
                for (int r : SPEEDS) {
                    for (long t : new long[] {0, 1, 6000, 12345, 23999}) {
                        long now = N + t;
                        long[] a = WorldCalendar.anchorFor(key, now, r);
                        int got = WorldCalendar.dateAt((int) a[0], a[1], r, now);
                        int later = WorldCalendar.dateAt((int) a[0], a[1], r, now + 1);
                        if (got != key || later < key) {
                            ok = false;
                            bad = l(key) + " at " + r + "x tick " + t + ": " + l(got);
                        }
                    }
                }
                long[] a = WorldCalendar.anchorFor(key, N + 9000, 1);
                if (WorldCalendar.dateAt((int) a[0], a[1], 1, N + DAY) != KnowledgeDate.nextDay(key)) {
                    ok = false;
                    bad = "the morning after " + l(key);
                }
            }
            check(ok, "/ee date: 29 Feb 1948, 31 Dec 1948, 15 Mar 44 BCE, 1 Jan 3000 BCE, 29 Feb 2000, 28 Feb 1900 (no"
                    + " leap day), year 1 and year 0, at five times of day and five speeds, read back; the next morning is"
                    + " the next day", bad);
            long[] a = WorldCalendar.anchorFor(KnowledgeDate.key(1900, 2, 28), N, 1);
            check(WorldCalendar.dateAt((int) a[0], a[1], 1, N + DAY) == KnowledgeDate.key(1900, 3, 1),
                    "1900 has no 29 February; 1948 and 2000 do", l(WorldCalendar.dateAt((int) a[0], a[1], 1, N + DAY)));
        }

        // 5. /time set: every pair of times of day, every 250 ticks.
        {
            boolean ok = true;
            String bad = "";
            int pairs = 0;
            for (int r : new int[] {1, 50}) {
                long[] a = WorldCalendar.anchorFor(KnowledgeDate.key(1948, 9, 14), N, r);
                for (long cur = N; cur < N + DAY; cur += 250) {
                    for (long target = 0; target < DAY + 6000; target += 250) {
                        long got = WorldCalendar.forwardTo(cur, target);
                        pairs++;
                        if (got < cur || got >= cur + DAY || Math.floorMod(got, DAY) != Math.floorMod(target, DAY)
                                || WorldCalendar.dateAt((int) a[0], a[1], r, got) < WorldCalendar.dateAt((int) a[0], a[1], r, cur)) {
                            ok = false;
                            bad = "from " + Math.floorMod(cur, DAY) + " to " + target + " gave " + (got - cur) + " ticks on";
                        }
                    }
                }
            }
            check(ok, "/time set (" + pairs + " pairs of times of day, at 1x and 50x): lands on the hour asked for, less than"
                    + " a day later, never earlier, and the date never goes back", bad);
            long night = N + 13000;
            check(WorldCalendar.forwardTo(night, 1000) == N + DAY + 1000 && WorldCalendar.forwardTo(N + 500, 1000) == N + 1000
                            && WorldCalendar.forwardTo(N + 6000, 6000) == N + 6000,
                    "/time set day at night = the next morning (like sleeping); at 6:30 in the morning = the same day;"
                            + " /time set noon at noon changes nothing", "");
        }

        // 6. The guard's way back.
        {
            boolean ok = true;
            String bad = "";
            for (long last : new long[] {N, N + 500, N + 13000, N + 23999}) {
                for (long now : new long[] {0, 1000, 13000, last - 100, last - 23999, last - 24000, last - 5 * DAY, 5 * DAY + 7000}) {
                    if (now >= last) {
                        continue;
                    }
                    long r = WorldCalendar.restoreTarget(last, now);
                    boolean small = last - now < DAY;
                    if (r < last || (small && r != last)
                            || (!small && (Math.floorMod(r, DAY) != Math.floorMod(now, DAY) || r >= last + DAY))) {
                        ok = false;
                        bad = "last " + last + " now " + now + " -> " + r;
                    }
                }
            }
            check(ok, "the guard: a day count put back is never left earlier than it was; a small step back (under a day)"
                    + " is undone; a big one (a time set from day 0) goes forward to that hour", bad);
        }

        // 7. Terra++ /ee speed: the day is kept (TerraTimeBridge.dayKeepingDate).
        {
            boolean ok = true;
            boolean same = true;
            String bad = "";
            int tried = 0;
            int base = -3000, dpy = 365;
            for (int s1 : SPEEDS) {
                long from = KnowledgeDate.terraDayFor(KnowledgeDate.key(1947, 12, 1), s1, base, dpy);
                long to = KnowledgeDate.terraDayFor(KnowledgeDate.key(1950, 1, 1), s1, base, dpy);
                for (long d = from; d <= to; d++) {
                    int key = KnowledgeDate.fromTerraDay(d, s1, base, dpy);
                    for (int s2 : SPEEDS) {
                        long nd = TerraTimeBridge.dayKeepingDate(d, s1, s2, base, dpy);
                        int k2 = KnowledgeDate.fromTerraDay(nd, s2, base, dpy);
                        tried++;
                        long ahead = WorldCalendar.epochDay(k2) - WorldCalendar.epochDay(key);
                        if (nd < 0 || k2 < key || ahead > 2L * s2) {
                            ok = false;
                            bad = l(key) + " " + s1 + "x -> " + s2 + "x shows " + l(k2);
                        }
                        if (s1 == s2 && nd != d) {
                            same = false;
                        }
                    }
                }
            }
            check(ok, "Terra++ time, /ee speed: every day from December 1947 to 1949 at every pair of speeds (" + tried
                    + " cases) keeps its date or the first later one the new speed can show (step 14 went to 1 January)", bad);
            check(same, "Terra++ time: the same speed again leaves the day count alone", "");
            long d = KnowledgeDate.terraDayFor(KnowledgeDate.key(1948, 9, 14), 1, base, dpy);
            int k = KnowledgeDate.fromTerraDay(TerraTimeBridge.dayKeepingDate(d, 1, 5, base, dpy), 5, base, dpy);
            int k1 = KnowledgeDate.fromTerraDay(TerraTimeBridge.dayKeepingDate(d, 1, 10, base, dpy), 10, base, dpy);
            System.out.println("       14 September 1948 at 1x -> 5x shows " + l(k) + "; -> 10x shows " + l(k1));
        }

        // 8. A world from before step 18d, and the save.
        {
            boolean ok = true;
            String bad = "";
            for (long ticks : new long[] {0, 1200, 2399}) {
                double frac = Math.max(0.0d, Math.min(0.9999d, ticks / 2400.0d));
                int old = KnowledgeDate.fromDayOfYear(1948, 1 + (int) Math.floor(frac * 366));
                WorldCalendar.start(null, 1948, ticks, 10, 1);
                int now = WorldCalendar.todayAt(0L);
                if (now != old) {
                    ok = false;
                    bad = ticks + " ticks at 10x: the old clock showed " + l(old) + ", the calendar starts at " + l(now);
                }
            }
            check(ok, "a world saved before step 18d (the old clock at 10x, at three points of 1948) starts the calendar on"
                    + " the day the old clock showed", bad);
            WorldCalendar.setRate(1);
            WorldCalendar.setDate(KnowledgeDate.key(1948, 9, 14));
            JsonObject saved = WorldCalendar.toJson();
            WorldCalendar.start(saved, 1900, 0L, 10, 25);
            check(saved != null && saved.has("anchorKey") && WorldCalendar.todayAt(0L) == KnowledgeDate.key(1948, 9, 14)
                            && WorldCalendar.todayAt(DAY) == KnowledgeDate.key(1948, 9, 15),
                    "the calendar reads back from the save (state.json \"calendar\"): the same date, and the same speed",
                    String.valueOf(saved));
        }

        System.out.println("CalendarProbe: " + passed + " passed, " + failed + " failed");
        if (failed > 0) {
            System.exit(1);
        }
    }
}
