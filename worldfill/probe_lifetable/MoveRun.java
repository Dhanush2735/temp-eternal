package com.eternalengine.lifeprobe;

import com.eternalengine.news.NewsTravel;
import com.eternalengine.people.Migrations;
import com.eternalengine.people.Migrations.Kind;
import com.eternalengine.people.Migrations.Migration;

import java.util.List;
import java.util.Locale;

/** Step 38 part 6 (C7 migrations and refugees). Run with {@code probe_lifetable.sh}. */
public final class MoveRun {

    static int checks = 0;
    static int failed = 0;

    public static void main(String[] args) {
        List<Migration> all = Migrations.all();

        ok("we have records at all", Migrations.count() >= 30);
        System.out.println("  migrations: " + Migrations.count() + " records");

        // every record is sourced, dated, placed and named at both ends
        int bad = 0;
        for (Migration m : all) {
            if (m.source() == null || m.source().isEmpty()) {
                bad++;
            }
            if (m.fromName().isEmpty() || m.toName().isEmpty()) {
                bad++;
            }
            if (m.people() <= 0) {
                bad++;
            }
            if (m.routeKm() < 50.0d || m.routeKm() > 20000.0d) {
                bad++;
            }
            if (m.lastYear() < m.year()) {
                bad++;
            }
        }
        ok("every record is sourced, named at both ends, dated, peopled and a real distance",
            bad == 0);

        // the largest first
        boolean sorted = true;
        for (int i = 1; i < all.size(); i++) {
            if (all.get(i - 1).people() < all.get(i).people()) {
                sorted = false;
            }
        }
        ok("the largest movement is first in the list", sorted);

        // 1. the largest migration in the history of the world must be in here
        long partition = 0L;
        for (Migration m : all) {
            if (m.id().startsWith("partition_")) {
                partition += m.people();
            }
        }
        ok("the Partition of India is in this table and adds to more than 13 million",
            partition > 13_000_000L);
        System.out.println("  the Partition, all four roads: " + String.format(Locale.ROOT,
            "%,d", partition) + " people");

        // 2. the Atlantic routes add to what the Slave Voyages database says was landed
        long landed = 0L;
        for (Migration m : all) {
            if (m.id().startsWith("atlantic_slave_trade_")) {
                landed += m.people();
            }
        }
        ok("the three Atlantic slave-trade routes add to the 10.7 million who were landed",
            Math.abs(landed - 10_700_000L) <= 500_000L);
        System.out.println("  the Atlantic slave trade, all three roads: "
            + String.format(Locale.ROOT, "%,d", landed) + " landed");

        // 3. most of this table is people who did not choose to go
        long forced = all.stream().filter(Migration::forced).count();
        ok("more than half the records are people who did not choose to go",
            forced * 2 > all.size());

        // 4. a route is a number of days, not a line on a map
        Migration la = Migrations.find("partition_punjab_east");
        ok("we can find the road from Lahore to Amritsar by name", la != null);
        NewsTravel.Leg leg = la.route(1947);
        ok("that road takes a real number of days in 1947",
            leg.days() > 0.0d && leg.days() < 30.0d);
        System.out.println("  Lahore to Amritsar, 1947: " + la.routeKm() + " km, "
            + NewsTravel.phrase(leg.days()) + " - " + leg.text());

        // 5. the same road is quicker in 1950 than in 1500, because the world changed under it
        double d1500 = Migrations.find("partition_punjab_east").route(1500).days();
        double d1947 = Migrations.find("partition_punjab_east").route(1947).days();
        ok("travel got quicker: 1947 is no slower than 1500 on the same road", d1947 <= d1500);

        // 6. a sea route really is a sea route
        boolean seaOk = true;
        for (Migration m : all) {
            if (m.sea() && m.routeKm() < 300.0d) {
                seaOk = false;
            }
        }
        ok("nothing marked as a sea route is a short hop across land", seaOk);
        Migration slave = Migrations.find("atlantic_slave_trade_brazil");
        ok("the Middle Passage is measured in weeks, not days",
            slave.route(1700).days() > 20.0d);
        System.out.println("  Lagos to Salvador, 1700: " + NewsTravel.phrase(
            slave.route(1700).days()) + " - " + slave.route(1700).text());

        // 7. Lahore in 1948 is on the road; Lahore in 1848 is not in the middle of this
        List<Migration> lahore48 = Migrations.near(31.55d, 74.34d, 1948);
        ok("Lahore in 1948 is on the Partition road", !lahore48.isEmpty());
        ok("the biggest thing passing Lahore in 1948 is a Partition road",
            lahore48.get(0).id().startsWith("partition_"));
        ok("Lahore in 1848 is quiet - this table is records, not a field",
            Migrations.near(31.55d, 74.34d, 1848).isEmpty());
        System.out.println("  Lahore, 1948: " + String.format(Locale.ROOT, "%,d",
            Migrations.peopleNear(31.55d, 74.34d, 1948)) + " people on the road");

        // 8. Lahore in 1947 is both an end people fled and an end they fled to, which is what the
        // Partition was: two columns walking past each other on the same road
        ok("from Lahore in 1947 Hindus and Sikhs are leaving",
            ids(Migrations.leaving(31.55d, 74.34d, 1947)).contains("partition_punjab_east"));
        ok("and Muslims are arriving in Lahore in 1947",
            ids(Migrations.arriving(31.55d, 74.34d, 1947)).contains("partition_punjab_west"));
        ok("at Amritsar the same two roads run the other way",
            ids(Migrations.arriving(31.63d, 74.87d, 1947)).contains("partition_punjab_east")
            && ids(Migrations.leaving(31.63d, 74.87d, 1947)).contains("partition_punjab_west"));

        // 8b. and that road was walked, not flown: the largest movement of people there has ever
        // been moved at thirty kilometres a day
        ok("the road out of Lahore was walked - days, not hours, and not the same day",
            la.route(1947).days() >= 1.0d && la.route(1947).days() < 30.0d);
        ok("but in 1947 a word could cross it the same day, and the register says both",
            la.fast(1947).days() < la.route(1947).days());

        // 8c. a sea crossing is its two ports, not a straight line through the land: the great
        // circle from Calcutta to British Guiana runs clean over the Punjab
        ok("no ship from Calcutta to Guiana passed over the Punjab",
            Migrations.near(31.55d, 74.34d, 1848).isEmpty());

        // 9. a place far from every road is quiet, and says so
        List<Migration> pacific = Migrations.near(-30.0d, -140.0d, 1948, 400.0d);
        ok("the middle of the South Pacific has no counted migration", pacific.isEmpty());
        ok("and the line we print for it admits the difference between unrecorded and empty",
            Migrations.line(-30.0d, -140.0d, 1948).contains("not the same as nobody leaving"));

        // 10. the deep past is in here too, and its numbers say so
        Migration bantu = Migrations.find("bantu_expansion");
        ok("the Bantu expansion is in this table", bantu != null);
        ok("and its number is marked as this table's estimate, not a source's",
            "estimated".equals(bantu.mark()));
        ok("a number offered without its mark is dishonest, so the line carries it",
            bantu.line(0).contains("estimated"));

        // 11. a forced kind really is forced
        ok("an expulsion is not chosen by the people in it", Kind.EXPULSION.forced());
        ok("a movement for work is", !Kind.ECONOMIC.forced());

        // 12. the prose
        System.out.println();
        System.out.println("  -- what the register says --");
        for (String[] s : new String[][] {
            {"Lahore", "1948"}, {"Amritsar", "1947"}, {"Aleppo", "2015"},
            {"Izmir", "1923"}, {"Wroclaw", "1946"}, {"Cork", "1847"},
            {"Kabul", "1985"}, {"Jackson", "1940"}, {"Kigali", "1994"}}) {
            double[] c = spot(s[0]);
            int y = Integer.parseInt(s[1]);
            System.out.println("  " + s[0] + " " + y + ": " + Migrations.line(c[0], c[1], y));
        }
        System.out.println();
        System.out.println("  " + Migrations.find("partition_punjab_east").line(1947));
        System.out.println("  " + Migrations.find("greek_turkish_exchange").line(1923));
        System.out.println("  " + Migrations.find("atlantic_slave_trade_brazil").line(1700));
        System.out.println("  " + Migrations.find("windrush").line(1955));
        System.out.println("  " + Migrations.find("vietnamese_boat_people").line(1980));
        System.out.println();
        System.out.println("  card, Amritsar 1947:");
        for (String l : Migrations.card(31.63d, 74.87d, 1947).split("\n")) {
            System.out.println("   " + l);
        }

        System.out.println();
        System.out.println(failed == 0
            ? "ALL " + checks + " CHECKS PASSED" : failed + " of " + checks + " CHECKS FAILED");
        if (failed > 0) {
            System.exit(1);
        }
    }

    static List<String> ids(List<Migration> ms) {
        List<String> out = new java.util.ArrayList<>();
        for (Migration m : ms) {
            out.add(m.id());
        }
        return out;
    }

    static void ok(String what, boolean pass) {
        checks++;
        if (pass) {
            System.out.println("  ok   " + what);
        } else {
            failed++;
            System.out.println("  FAIL " + what);
        }
    }

    static double[] spot(String name) {
        switch (name) {
            case "Lahore":   return new double[] {31.55d, 74.34d};
            case "Amritsar": return new double[] {31.63d, 74.87d};
            case "Aleppo":   return new double[] {36.20d, 37.16d};
            case "Izmir":    return new double[] {38.42d, 27.14d};
            case "Wroclaw":  return new double[] {51.11d, 17.04d};
            case "Cork":     return new double[] {51.90d, -8.47d};
            case "Kabul":    return new double[] {34.53d, 69.17d};
            case "Jackson":  return new double[] {32.30d, -90.18d};
            case "Kigali":   return new double[] {-1.94d, 30.06d};
            default:         return new double[] {0.0d, 0.0d};
        }
    }
}
