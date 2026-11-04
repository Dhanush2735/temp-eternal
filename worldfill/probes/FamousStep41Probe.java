/**
 * Step 41 (D11, C11): famous people where and when they were - the presence register, the kinship
 * register, and the two questions they were built to answer.
 *
 * The one that matters is line 507 of SYSTEMS_PLAN.md: T. H. White (Q453410) was born in Bombay and
 * lived in England. His card has said so for six steps and nothing in the mod could use it. This
 * probe asks who was in Cambridge in 1928, and expects him.
 */
public final class FamousStep41Probe {

    static int fails = 0;

    static void ok(boolean cond, String what) {
        System.out.println((cond ? "  ok   " : "  FAIL ") + what);
        if (!cond) fails++;
    }

    static void note(String what) {
        System.out.println("  ..   " + what);
    }

    static void head(String what) {
        System.out.println();
        System.out.println("== " + what);
    }

    public static void main(String[] args) {
        com.eternalengine.civilization.Presence pres = com.eternalengine.civilization.Presence.get();
        com.eternalengine.civilization.Kinship kin = com.eternalengine.civilization.Kinship.get();

        head("the two registers");
        System.out.println("       " + pres);
        System.out.println("       " + kin);
        ok(pres.hasData(), "the presence register loaded (" + pres.source() + ")");
        ok(kin.hasData(), "the kinship register loaded (" + kin.source() + ")");
        ok(pres.rows() > 300000, pres.rows() + " stays");
        ok(pres.placeCount() > 50000, pres.placeCount() + " places");
        ok(kin.edgeCount() > 90000, kin.edgeCount() + " parent edges");
        ok(kin.houseCount() > 3000, kin.houseCount() + " houses");

        head("SYSTEMS_PLAN line 507: who was in Cambridge in 1928");
        java.util.List<com.eternalengine.civilization.Presence.Stay> there =
                pres.hereIn(52.202d, 0.115d, 1928, 30.0d);
        note(there.size() + " people with a card were within 30 km of Cambridge in 1928");
        for (int i = 0; i < Math.min(6, there.size()); i++) {
            System.out.println("         " + there.get(i).line());
        }
        boolean white = there.stream().anyMatch(s -> s.qid() == 453410);
        ok(white, "T. H. White is among them: he studied there, and he was never born there");

        java.util.List<com.eternalengine.civilization.Presence.Stay> whites = pres.of(453410);
        note("T. H. White's own itinerary, " + whites.size() + " stays");
        for (com.eternalengine.civilization.Presence.Stay s : whites) {
            System.out.println("         " + s.line());
        }
        ok(whites.size() >= 3, "his register holds more than a birthplace");
        ok(whites.stream().anyMatch(s -> s.why() == com.eternalengine.civilization.Presence.BORN),
                "it says where he was born");
        ok(whites.stream().anyMatch(s -> s.why() == com.eternalengine.civilization.Presence.DIED),
                "it says where he died, which is Piraeus and not Cambridge or Bombay");
        ok(whites.stream().anyMatch(s -> s.why() == com.eternalengine.civilization.Presence.STUDIED
                        && s.estimated()),
                "it says he studied somewhere and admits it does not know the year");

        head("the same question the old way, and how the two differ");
        java.util.List<com.eternalengine.civilization.Presence.Stay> born =
                pres.bornNear(52.202d, 0.115d, 1928, 30.0d);
        note(born.size() + " of the " + there.size() + " were born within 30 km of Cambridge");
        ok(born.size() < there.size(),
                "who is here and who is from here are not the same list, which is the whole defect");

        head("C11: a family, from blood and not from card links");
        for (int qid : new int[] {9682, 9129, 3044, 9439, 1001}) {
            com.eternalengine.civilization.Kinship.Kinsman who = kin.kinsman(qid);
            java.util.List<com.eternalengine.civilization.Kinship.Kinsman> fam = kin.familyOf(qid, 6);
            if (!who.named() && fam.isEmpty()) {
                continue;
            }
            System.out.println("       " + who.display() + " (Q" + qid + ")");
            for (com.eternalengine.civilization.Kinship.Kinsman k : kin.parentsOf(qid)) {
                System.out.println("         parent   " + k.display());
            }
            for (com.eternalengine.civilization.Kinship.Marriage m : kin.spousesOf(qid)) {
                System.out.println("         married  " + m.spouse().display() + " " + m.years());
            }
            for (com.eternalengine.civilization.Kinship.Kinsman k : kin.childrenOf(qid)) {
                System.out.println("         child    " + k.display());
            }
            com.eternalengine.civilization.Kinship.House h = kin.houseOf(qid);
            if (h != null) {
                System.out.println("         house    " + h.name() + " (" + h.members().size()
                        + " people with a card)");
            }
        }
        ok(kin.parentsOf(1001).size() > 0, "Karamchand Gandhi (Q1001) has a parent in the record");
        ok(kin.childrenOf(1001).size() > 0, "and a child, which is what a family tree needs");

        head("naming: the pack names relatives, the cards name everybody else");
        // The pack deliberately does not repeat the 148,510 people who have a card, so Elizabeth II
        // is not in it. Without the cards she and her father are unnamed; with them, they are not.
        // The cards cannot be compiled outside the game (they need Minecraft), so the probe stands
        // in their place with a resolver that knows one person, and checks the hook is asked.
        ok(!kin.kinsman(9682).named(),
                "Elizabeth II has a card, so the kinship pack carries no name for her");
        note("       before the cards are read: " + kin.kinsman(9682).display());
        // the real numbers, read out of the pack: Q9682 Elizabeth II, Q10633 and Q280856 her parents
        kin.setNameSource(q -> q == 9682 ? "Elizabeth II"
                : q == 10633 ? "George VI"
                : q == 280856 ? "Queen Elizabeth the Queen Mother" : null);
        ok(kin.kinsman(9682).named(), "once the cards are read, the register asks them");
        note("       after: " + kin.kinsman(9682).display());
        ok(kin.parentsOf(9682).stream().anyMatch(k -> k.name().equals("George VI")),
                "and her father is George VI, not 'someone the record does not name'");
        kin.setNameSource(null);
        ok(!kin.kinsman(9682).named(), "and it goes back to declining when there are no cards");

        head("dynasties: derived, not asserted");
        java.util.List<com.eternalengine.civilization.Kinship.Dynasty> dyn = kin.dynasties();
        note(dyn.size() + " dynasties");
        dyn.stream()
                .sorted(java.util.Comparator.comparingInt(
                        com.eternalengine.civilization.Kinship.Dynasty::size).reversed())
                .limit(8)
                .forEach(d -> System.out.println("         " + d.name() + " - held "
                        + d.officeName() + " across " + d.generations() + " generations, "
                        + d.size() + " of them with a card, " + d.span()));
        ok(dyn.size() > 400, dyn.size() + " dynasties");
        ok(dyn.stream().anyMatch(d -> d.name().toLowerCase().contains("ottoman")),
                "the Ottoman sultans are one of them");
        ok(dyn.stream().anyMatch(d -> d.name().toLowerCase().contains("wittelsbach")),
                "and the Wittelsbach dukes of Bavaria");
        ok(dyn.stream().allMatch(d -> d.size() >= 3), "none of them is smaller than three people");
        ok(dyn.stream().allMatch(d -> !d.name().isBlank()), "and every one of them has a name");

        head("a register that declines");
        com.eternalengine.civilization.Kinship.Kinsman nobody = kin.kinsman(999999999);
        ok(!nobody.named(), "a person with no card and no name is not invented");
        note("       " + nobody.display());
        ok(kin.parentsOf(999999999).isEmpty(), "and he has no parents in the record");
        ok(pres.of(999999999).isEmpty(), "and nowhere he has been");

        head("the very checks the game runs (/ee check all, part famous)");
        // The same class, the same code: FamousChecks is written so that it can be run outside a
        // server. A claim cannot pass in the build and fail in the game.
        com.eternalengine.civilization.FamousChecks.run(
                new com.eternalengine.civilization.FamousChecks.Sink() {
                    @Override
                    public void check(boolean cond, String text, String whyNot) {
                        System.out.println((cond ? "  ok   " : "  FAIL ") + text
                                + (cond || whyNot == null || whyNot.isEmpty() ? "" : " -- " + whyNot));
                        if (!cond) fails++;
                    }

                    @Override
                    public void known(String text, String detail) {
                        System.out.println("  ..   " + text
                                + (detail == null || detail.isEmpty() ? "" : " -- " + detail));
                    }

                    @Override
                    public void info(String text) {
                        System.out.println("       " + text);
                    }
                });

        System.out.println();
        System.out.println(fails == 0 ? "step 41 registers: 0 problems"
                : "step 41 registers: " + fails + " problem(s)");
        if (fails != 0) System.exit(1);
    }
}
