# 2994–2990 BCE: linked-article follow-up

**Status:** Partial research only. These five years were already included in the earlier 2999–2990 BCE pass. No exact-year events were established; none of these years is fully collected. Totals remain **512 historical years partly worked; 0 fully collected**. Earlier work is not continuous coverage.

## Active game-data improvement

Updated the existing indexed Harappa event `r2_harappa_ravi_c3000` in `events_wikipedia.json.gz`, preserving its ID, position and effect. Instead of appearing only in the 3000 BCE reference slot, it now describes a bounded c. 3000–2800 BCE *archaeological context*. It is not a precise founding event, nor evidence of uninterrupted habitation or a new event every year. The UNESCO tentative-list submission describes Harappa's Ravi aspect as c. 3300–2800 BCE and distinguishes the later mature urban phase. The broader regional Early Harappan note is a separate existing regional reference.

Storage uses `start=-3000`, `end=-2799`. Gazetteer-style exclusive-end interpretation includes -2800; the Wikipedia-pack NewsIndex conversion may also include the stored end, so **NewsIndex may surface this context in -2799**. In either reader a long contextual note may repeat annually; this is not evidence for yearly activity. Runtime and saved-world behavior have not been tested. The Wiki site coordinates retained in the event (30.62889, 72.86389) and the coarse coordinates printed in the UNESCO tentative submission differ materially; the latter were not substituted without investigation.

- Sources: [Harappa](https://en.wikipedia.org/wiki/Harappa), [UNESCO tentative list submission](https://whc.unesco.org/en/tentativelists/1878/), [Indus Valley Civilisation](https://en.wikipedia.org/wiki/Indus_Valley_Civilisation).
- Reversible before/after manifest: `reviews/2994_2990_bce_ravi_2026-10.json`; canonical SHA-256 `fd72c7d0bc05de4944370fbb75d4c5d9834c7a451824d56aa04dc5102a2e7b90`.
- Guarded installer: `apply_2994_2990_bce_ravi.py`; nine unit tests before and after, staged reversal and unique installed after-image passed. No Forge/game/save test or jar rebuild.

## Further checked sources and unresolved issues

- The five year-title pages redirect to [30th century BC](https://en.wikipedia.org/wiki/30th_century_BC). A redirect is not a verified yearly event list.
- [Alvastra pile-dwelling](https://en.wikipedia.org/wiki/Alvastra_pile-dwelling) and the [Swedish History Museum](https://alvastra.historiska.se/the-site/alvastra-pile-dwelling/) place construction around 3000 BCE. The 42-year tree-ring sequence is floating and radiocarbon-associated; it does not establish a specific 2990s year. No site or event was added on this basis.
- [Barbar Temple](https://en.wikipedia.org/wiki/Barbar_Temple) gives an earliest date around 3000 BCE, whereas [Bahrain's tourism site](https://www.bahrain.com/en/barbar-temples) dates the first temple around 2100 BCE. The chronology conflicts. Existing `pl_291184549` has an early range and Sumer hint; neither was changed without further review.
- [Tepe Sialk](https://en.wikipedia.org/wiki/Tepe_Sialk) has much earlier settlement than its attributed stepped platform; the date and even interpretation of the platform merit further review. Existing `pl_464208937` has a Sumer hint and a broad interval; no new duplicate was created.
- [Diraz Temple](https://en.wikipedia.org/wiki/Diraz_Temple) is broadly dated to the third millennium; this does not establish a 2990s construction event.
- [Djer](https://en.wikipedia.org/wiki/Djer) has uncertain chronology; the century page gives death c. 2990–2980 BCE, not a definite 2990 death. His burial site does not prove the place of death. No VIP was added or made spawnable.
- Existing Harappa Pleiades records `pl_93441396_1` and `_2` do not cover 2994 BCE, despite evidence for a Ravi-phase context. Their ranks, ranges and possible gameplay consequences require separate review; the event update above does not repair site-based spawning.

## Next

Continue from 2989 BCE, following linked material while deepening the incomplete 3000–2990 BCE research. The current jar remains stale, natural VIP spawning remains unimplemented, and full-year collection has not been established.
