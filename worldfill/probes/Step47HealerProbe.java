/* Step 47 part 6 (E15): medicine and healers by era, the half that was missing.
   The claim: a healer is a person you can get to, not a remedy that has spread, and the midwife
   needs two axes because her standing changes while her arrival does not. */
import com.eternalengine.people.Healers;

import java.util.List;

public class Step47HealerProbe {
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

    public static void main(String[] args) {
        Healers m = Healers.get();
        System.out.println("  " + m.summary());

        // ------------------------------------------------ 1. THE REGISTER LOADS
        ok(m.healers().size() >= 14, "the register carries the trades: " + m.healers().size());
        eq(m.areas().size(), 17, "over the mod's 17 areas");
        ok(m.complaints().contains("childbirth"), "and knows childbirth is a complaint");
        ok(m.healer("midwife") != null && m.healer("surgeon") != null, "including the two that "
                + "carry this register's findings");

        // ------------------------------------------------ 2. EVERYBODY GETS HELP IN 3000 BC
        // Childbirth happens everywhere in every year, so somebody must attend a birth in every
        // area in the first year of the span. This is the check that catches a register of trades
        // that has quietly listed only the people who were paid.
        for (String area : m.areas()) {
            ok(m.nearest("childbirth", area, -3000) != null,
                    "somebody attends a birth in " + area + " in 3000 BC");
        }
        ok(m.whoTends("childbirth", "SAS", -3000).stream().anyMatch(x -> x.id().equals("midwife")),
                "and in southern Asia the midwife is among the people you can send for");
        // `nearest` answers "who is closest", and the closest is the household in every case,
        // because a person with a fever does not first walk to a specialist. The probe that asked
        // for the midwife by name was testing the wrong method.
        eq(m.nearest("fever", "EUR", -3000).id(), "household", "while a fever at home in 3000 BC "
                + "is the woman of the house, because she is nearest");
        ok(m.nearest("bones", "WAF", 1200) != null, "a broken arm in medieval West Africa has "
                + "somebody: " + m.nearest("bones", "WAF", 1200).id());
        ok(m.nearest("eyes", "EUR", 1500) != null, "and so do the eyes in 1500: "
                + m.nearest("eyes", "EUR", 1500).id());

        // ------------------------------------------------ 3. THE PHYSICIAN IS LATE AND RARE
        ok(m.healer("physician").since("EUR") <= -400, "the Greek physician is there in 400 BC");
        ok(m.healer("physician").since("NNA") >= 1600, "and in northern North America only much "
                + "later: " + m.healer("physician").since("NNA"));
        ok(m.healer("physician").since("PAC") > 1700, "and in Polynesia later still: "
                + m.healer("physician").since("PAC"));
        ok(m.precedes("household", "physician", "EUR"), "the household comes before the physician");
        ok(m.precedes("herbalist", "apothecary", "EUR"), "the herbalist before the apothecary");
        ok(!m.whoTends("childbirth", "EUR", 100).isEmpty(), "and there is always somebody");

        // ------------------------------------------------ 4. THE FINDING: SURGERY BEFORE ANAESTHESIA
        for (String area : m.areas()) {
            ok(m.healer("surgeon").since(area) < 1846,
                    "the surgeon is at work in " + area + " long before 1846: "
                    + m.healer("surgeon").since(area));
        }
        ok(m.healer("surgeon").since("EUR") <= 1200, "a European cutter by 1200");
        ok(m.whoTends("wounds", "SAS", -500).stream().anyMatch(x -> x.id().equals("surgeon")),
                "and in India in 500 BC there is a surgeon to send for, four centuries before there "
                + "is a physician in that area");
        System.out.println("  wounds, India 500 BC: " + m.nearest("wounds", "SAS", -500).id());

        // ------------------------------------------------ 5. TWO AXES: THE MIDWIFE
        eq(m.healer("midwife").since("EUR"), -3000, "the midwife has been in Europe from the start");
        eq(m.healer("midwife").standingAt("EUR", 1400), "respected", "she is respected in 1400");
        eq(m.healer("midwife").standingAt("EUR", 1600), "prosecuted", "and prosecutable in 1600");
        eq(m.healer("midwife").standingAt("EUR", 1800), "ordinary", "and ordinary again by 1800");
        eq(m.healer("midwife").standingAt("SAS", 1600), "respected", "while nothing has happened to "
                + "her in southern Asia at the same date, which is the other half of the claim");
        ok(m.healer("midwife").standingChanges().size() >= 2, "the two changes are in the data");
        System.out.println("  the midwife in Europe: 1400 " + m.healer("midwife").standingAt("EUR", 1400)
                + ", 1600 " + m.healer("midwife").standingAt("EUR", 1600)
                + ", 1800 " + m.healer("midwife").standingAt("EUR", 1800));

        // ------------------------------------------------ 6. STANDING IS NOT EFFECTIVENESS
        ok(m.suspectIn("EUR", 1550).contains("iatrochemist"), "the alchemist-physician is suspect "
                + "in 1550 and his work is real: " + m.suspectIn("EUR", 1550));
        ok(m.suspectIn("EUR", 1550).contains("midwife"), "and so is the midwife");
        ok(!m.suspectIn("SAS", 1550).contains("midwife"), "but not in southern Asia");
        ok(m.healer("herbalist").standingAt("EUR", 1300).equals("suspect"), "the herbalist becomes "
                + "suspect once medicine has a Latin");
        ok(m.healer("herbalist").standingAt("EUR", 1800).equals("ordinary"), "and ordinary again "
                + "later");

        // ------------------------------------------------ 7. A REACH ORDER THAT MEANS SOMETHING
        List<Healers.Healer> fever = m.whoTends("fever", "EUR", 1250);
        ok(fever.size() > 3, "a fever in 1250 Europe has several options: " + fever.size());
        eq(fever.get(0).reach(), "household", "and the nearest is the household");
        ok(fever.get(fever.size() - 1).reach().compareTo("household") != 0,
                "with the far ones last");
        System.out.println("  fever, Europe 1250: " + fever.stream().map(Healers.Healer::id).toList());

        // ------------------------------------------------ 8. NOBODY IS PUNISHED
        for (Healers.Healer h : m.healers()) {
            ok(!h.note().toLowerCase().contains("penalty"), "no note mentions a penalty: " + h.id());
        }
        ok(m.nearest("plague", "EUR", 1350) != null, "a plague in 1350 finds a plague doctor: "
                + m.nearest("plague", "EUR", 1350).id());
        ok(m.nearest("plague", "EUR", 1200) == null, "and finds nobody at all in 1200, because the "
                + "trade is 1348 and the honest answer is that there is no one to call");

        System.out.println(failed == 0
                ? "Step47HealerProbe: " + checks + " checks, 0 failed"
                : "Step47HealerProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
