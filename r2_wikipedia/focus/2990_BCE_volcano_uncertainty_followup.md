# 2990 BCE: volcano-date uncertainty follow-up

This revisits previously partly worked years near the requested 3000 BCE starting point. No year or ten-year step is completed by this pass.

Three existing indexed hazard records had been displayed without their substantial date uncertainty. Their labels now communicate the estimates reported by Smithsonian's Global Volcanism Program (GVP):

- [Agua de Pau](https://volcano.si.edu/volcano.cfm?vn=382090), Azores: **2990 BCE (?)**, based on uncalibrated radiocarbon; VEI 5.
- [Ulleungdo](https://volcano.si.edu/volcano.cfm?vn=306030), Korea: **2990 BCE ± 40 years**, based on uncalibrated radiocarbon; no VEI is given for this episode.
- [Villarrica](https://volcano.si.edu/volcano.cfm?vn=357120), Chile: **2990 BCE ± 500 years**, based on tephrochronological correlation; VEI 0.

These are source estimates, not proof the eruptions occurred in the same calendar year. The radiocarbon values are explicitly uncalibrated, not asserted as calibrated calendar-year ranges. Their point coordinates represent volcano locations, not complete affected areas.

**Important gameplay limit:** Only the labels and source evidence changed. The underlying one-year 2990 BCE slots, hazard types, disruption effects and radii remain unchanged. The game can therefore still treat these uncertain eruptions as happening in that exact year. In particular, the system uses its default volcano severity when no VEI is provided. The preserved `VEI 5` and `VEI 0` labels retain their existing severity-parser tokens. Actual behavior has not been tested in a live game or saved world. Handling uncertain hazard dates without inventing an event year remains unfinished.

The strict before/after manifest is `reviews/2990_bce_volcano_uncertainty_2026-11.json.gz`, canonical SHA-256 `f603bef56980ce623539f53dba9464495f07526eeb8643ce31c479944b2384af`; installer: `apply_2990_bce_volcano_uncertainty.py`. Actual apply, rollback and reapply reproduced hashes of all 26 indexed packs, with one changed. Twelve selected new and existing tests passed; a Python regex check preserved the Java parser's VEI/deaths tokens but did not run Java.

To recover space, the old `worldfill/data_use_probe.json` report was losslessly archived to `data_use_probe.json.xz`. `worldfill/archived_history_reports.py` verifies its original and archive hashes and can restore it without overwrite when space permits. It is a historical report, not new test evidence. Two duplicated progress summaries were removed from the readable ledger only after verifying exact copies in its existing checked archive; the individual batch reports remain.

**Fully collected years: 0.** The five requested ten-year steps starting at 3000 BCE remain incomplete. No new people or VIP spawning were implemented. Storage remains close to the guard; R1 is deferred.
