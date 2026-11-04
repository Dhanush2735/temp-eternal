/* Step 46 interlude: the timeline extended to AD 3000.
   What is projected must never look like what is recorded, so every check here that asks about a
   year after the record also asks whether the answer is MARKED as a projection. */
import com.eternalengine.clock.Timeline;
import com.eternalengine.technology.TechnologyAtlas;
import com.eternalengine.money.ProductAtlas;
import com.eternalengine.civilization.RulerRegister;

public class SpanProbe {
    static int checks = 0, failed = 0;

    static void ok(boolean c, String what) {
        checks++;
        if (!c) { failed++; System.out.println("  FAIL " + what); }
    }
    static void eq(Object a, Object b, String what) {
        checks++;
        if (a == null ? b != null : !a.equals(b)) {
            failed++;
            System.out.println("  FAIL " + what + "  expected=" + b + " actual=" + a);
        }
    }

    public static void main(String[] args) {
        System.out.println("== the span: " + Timeline.span() + " ==");

        // ---------------------------------------------------------------- 1. THE SPAN ITSELF
        eq(Timeline.FIRST_YEAR, -3000, "the world begins in 3000 BC");
        eq(Timeline.LAST_YEAR, 3000, "the world ends in AD 3000");
        eq(Timeline.RECORDED_UNTIL, 2026, "the record stops at 2026");
        ok(Timeline.inSpan(-3000), "3000 BC is in span");
        ok(Timeline.inSpan(3000), "AD 3000 is in span");
        ok(Timeline.inSpan(0), "AD 0 is in span");
        ok(Timeline.inSpan(2500), "AD 2500 is in span, in the projected part");
        ok(!Timeline.inSpan(-3001), "3001 BC is out of span");
        ok(!Timeline.inSpan(3001), "AD 3001 is out of span");
        ok(Timeline.projectedYears() == 3000 - 2026, "the projection covers "
                + Timeline.projectedYears() + " years");

        // ---------------------------------------------------------------- 2. THE MARK
        ok(!Timeline.projected(2026), "2026 is recorded, not projected");
        ok(!Timeline.projected(-500), "500 BC is recorded, not projected");
        ok(Timeline.projected(2027), "2027 is projected");
        ok(Timeline.projected(3000), "AD 3000 is projected");
        eq(Timeline.markFor(1600), "recorded", "1600 is recorded");
        eq(Timeline.markFor(2500), "projected", "2500 is PROJECTED");
        ok(!"recorded".equals(Timeline.markFor(2500)),
                "a projected year is never marked recorded - that is the whole guardrail");
        ok(Timeline.projectionNote(2500) != null, "a projected year carries a note");
        ok(Timeline.projectionNote(1600) == null, "a recorded year carries none");
        ok(Timeline.projectionNote(2500).contains("projection"), "the note says so");
        System.out.println("  e.g. " + Timeline.projectionNote(2500));

        // ---------------------------------------------------------------- 3. READING PAST THE RECORD
        eq(Timeline.readAt(2500), 2026, "2500 is read at the last recorded year");
        eq(Timeline.readAt(1600), 1600, "1600 is read at itself");
        eq(Timeline.readAt(9999), 2026, "a wild year is read at the last recorded year");
        eq(Timeline.readAt(-9999), -3000, "and at the first year at the other end");

        // ---------------------------------------------------------------- 4. THE TECHNOLOGY ATLAS CONTINUES
        // A technology that reached a place is still there in 2500. The atlas has always
        // extrapolated past its last year; what is new is that this is now SAYABLE.
        TechnologyAtlas atlas = TechnologyAtlas.get();
        ok(atlas.loaded(), "the technology atlas is loaded: " + atlas.problem());
        double[] paris = {48.8566, 2.3522};
        double[] agra = {27.1750, 78.0422};
        double[] cusco = {-13.5320, -71.9675};

        var town = com.eternalengine.civilization.SettlementRank.TOWN;
        // The railway reaches Paris; once it has, it is there in AD 3000 too.
        for (String tech : new String[]{"railway", "car", "air_travel", "electric_car"}) {
            var t = atlas.tech(tech);
            ok(t != null, "the atlas knows " + tech);
            if (t == null) continue;
            boolean at2026 = atlas.present(t, paris[0], paris[1], 2026, town);
            boolean at3000 = atlas.present(t, paris[0], paris[1], 3000, town);
            ok(at2026 == at3000, tech + " in Paris reads the same in 3000 as in 2026 ("
                    + at2026 + " / " + at3000 + "): a thing that arrived stays arrived");
            if (at2026) {
                ok(at3000, tech + " is still present in Paris in AD 3000");
            }
        }
        // And a thing that never reached a place is still absent in 3000 - the projection must
        // not quietly invent a spread that never happened.
        var horses = atlas.tech("horses");
        if (horses != null) {
            boolean cusco1500 = atlas.present(horses, cusco[0], cusco[1], 1500, town);
            ok(!cusco1500, "horses have not reached Cusco in 1500");
        }

        // ---------------------------------------------------------------- 5. THE PRODUCT ATLAS CONTINUES
        ProductAtlas P = ProductAtlas.get();
        for (int y : new int[]{-3000, 0, 1500, 2026, 2500, 3000}) {
            var place = P.place(paris[0], paris[1], y);
            ok(place != null, "the atlas places Paris in " + y);
            if (place != null) {
                ok(place.area() != null && !place.area().isBlank(),
                        "Paris has an area in " + y + ": " + place.area());
            }
        }
        // Products: a car's first year is a fact about the record, and asking for it in AD 3000
        // must not change it. The projection continues the answer; it does not re-derive it.
        for (String prod : new String[]{"car", "railway", "aeroplane", "electric_cars"}) {
            ProductAtlas.Product p = P.product(prod);
            ok(p != null, "the product atlas knows " + prod);
            if (p == null) continue;
            int inEur = p.firstIn("EUR");
            ok(inEur != Integer.MAX_VALUE && inEur != 0,
                    prod + " has a first year in Europe: " + inEur);
            ok(inEur <= 2026, prod + " arrives before the record ends (" + inEur + ")");
            // and once it has arrived it is gone in no year we know of, so it is still there
            ok(p.goneIn("EUR") == 0 || p.goneIn("EUR") > inEur,
                    prod + " has no end year before it began");
        }

        // ---------------------------------------------------------------- 6. THE RULERS GO ON, MARKED
        RulerRegister R = RulerRegister.get();
        ok(R.summary().loaded(), "the ruler register is loaded");
        ok(R.lastYear() >= 2000, "the register reaches the modern day (" + R.lastYear() + ")");
        ok(R.recordedUntil() >= 2000, "and says so (" + R.recordedUntil() + ")");
        // The register's own data runs -3400 to 2026, so it can cover the whole span. Whether it
        // answers a particular place in a particular year is a fact about that place: NO STATE
        // RULED NEOLITHIC PARIS, and the register is right to say nothing rather than invent one.
        ok(R.lastYear() >= 2026, "the register reaches the last recorded year");
        for (int y : new int[]{-3000, -200, 800, 1500, 1800, 2026}) {
            var at = R.rulerAt(paris[0], paris[1], y);
            at.ifPresent(h -> ok(h.ruler() != null && !h.ruler().isBlank(),
                    "Paris has a ruler in " + Timeline.label(y) + ": " + h.ruler()));
            // either answer is honest; what must never happen is an exception or a blank name
            ok(at.isEmpty() || !at.get().ruler().isBlank(),
                    "the register answers Paris in " + Timeline.label(y)
                    + " with a name or with nothing, never with a blank");
        }
        // But every PROJECTED year must answer, by continuing the last recorded one. A player who
        // walks into AD 2500 must not find an empty world.
        for (int y : new int[]{2100, 2500, 3000}) {
            var at = R.rulerAt(paris[0], paris[1], y);
            ok(at.isPresent(), "the register answers Paris in " + Timeline.label(y));
        }
        // The ruler of AD 3000 is the last recorded one, because nothing is invented beyond the
        // record. That is a projection, and the frame marks it as one.
        var at2026 = R.rulerAt(paris[0], paris[1], 2026);
        var at3000 = R.rulerAt(paris[0], paris[1], 3000);
        if (at2026.isPresent() && at3000.isPresent()) {
            eq(at3000.get().ruler(), at2026.get().ruler(),
                    "the ruler of AD 3000 is the last recorded one, not an invented one: "
                    + at3000.get().ruler());
            ok(Timeline.projected(3000), "and the frame marks AD 3000 as projected");
            ok(!"recorded".equals(Timeline.markFor(3000)),
                    "so it is never presented as recorded fact");
        }
        System.out.println("  e.g. Paris AD 3000: " + at3000.map(h -> h.ruler()).orElse("(none)")
                + "  [" + Timeline.markFor(3000) + "]");

        // ------------------------------------------------- 7. THE SKY REACHES AD 3000 FOR REAL
        // This is the one part of the world where the far end is not a projection at all.
        // Eclipses are COMPUTED, not recorded: NASA's Five Millennium Catalog runs 1999 BCE to
        // 3000 CE, and the mod ships all of it. So the sky in AD 3000 is a fact, not a guess.
        var sky = com.eternalengine.sky.SkyEclipses.get();
        ok(sky != null, "the eclipse catalogue is loaded");
        ok(sky.solarToYear() >= 3000,
                "the solar catalogue reaches AD " + sky.solarToYear() + " - past our end year");
        ok(sky.lunarToYear() >= 3000,
                "the lunar catalogue reaches AD " + sky.lunarToYear());
        ok(sky.solarFromYear() <= -1999, "and begins in " + sky.solarFromYear());
        for (int y : new int[]{-1999, 0, 1500, 2026, 2500, 2999, 3000}) {
            ok(!sky.solarInYear(y).isEmpty() || !sky.lunarInYear(y).isEmpty(),
                    "there is an eclipse somewhere in " + Timeline.label(y));
        }
        // AD 3000 specifically: the last year of the world has a real, computed sky.
        ok(!sky.solarInYear(3000).isEmpty(), "there are solar eclipses in AD 3000");
        System.out.println("  e.g. AD 3000 has " + sky.solarInYear(3000).size()
                + " solar and " + sky.lunarInYear(3000).size() + " lunar eclipses (computed)");

        // ---------------------------------------------------------------- 8. LABELS
        eq(Timeline.label(3000), "AD 3000", "AD 3000 is labelled AD 3000");
        eq(Timeline.label(-3000), "3000 BC", "3000 BC is labelled 3000 BC");
        eq(Timeline.span(), "3000 BC to AD 3000", "the span reads as one line");

        System.out.println("== span probe: " + checks + " checks, " + failed + " failed ==");
        System.out.println("  span " + Timeline.span() + "; records to AD "
                + Timeline.RECORDED_UNTIL + "; " + Timeline.projectedYears()
                + " years marked projected, not recorded");
        if (failed > 0) System.exit(1);
    }
}
