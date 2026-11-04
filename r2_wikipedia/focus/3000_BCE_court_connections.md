# 3000 BCE revisit — court connections

This partial pass follows people connected to Djer, Djet and the First Dynasty, not only kings. Their absolute dates are disputed; inclusion does **not** prove that any particular person was alive in 3000 BCE or that the people were all together.

## People and relationships collected

- [Amka](https://en.wikipedia.org/w/index.php?title=Amka_(official)&oldid=1379754079), an official, is associated in the biography with the reigns of Djer, Djet and Den. [Sekhemkasedj](https://en.wikipedia.org/w/index.php?title=Sekhemkasedj&oldid=1379754005) is described as an official under Djet and during Merneith's regency. These two already had research profiles in `history/sources/wikipedia_2980_bce.json`; they were linked rather than added as duplicate active VIPs.
- [Herneith](https://en.wikipedia.org/w/index.php?title=Herneith&oldid=1340595429) is tentatively connected to Djer, but the article says her identity and role are not certain. [Nakhtneith](https://en.wikipedia.org/w/index.php?title=Nakhtneith&oldid=1379753618) is described as a wife of Djer. [Penebui](https://en.wikipedia.org/w/index.php?title=Penebui&oldid=1374951721) is possibly linked to Djer; interpretations of inscriptions and her death are not treated as settled.
- [Ahaneith](https://en.wikipedia.org/w/index.php?title=Ahaneith&oldid=1361518183) is known from a named stela found in Djet's tomb; her relationship or role is unknown. [Seshemetka](https://en.wikipedia.org/w/index.php?title=Seshemetka&oldid=1374950597)'s article reports conflicting associations with Djer and Den, so both are recorded as disputed rather than choosing one.
- [Mastaba S3503](https://en.wikipedia.org/w/index.php?title=Mastaba_S3503&oldid=1223286344) has an unknown occupant. The previous suggestion that it was Merneith's burial was abandoned; no occupant was added as fact.

The additional research-only file `history/sources/wikipedia_3000_bce_court_network.json` records five profiles, six links to earlier research profiles, and eleven sourced relationship assertions. Dates, life locations and alternate outcomes were not invented. The file is not loaded by the VIP runtime.

## Active game-data change

Updated existing indexed regional entry `r2_djet_reign_reference_c2980` to mention officials **Amka and Sekhemkasedj**, with their linked biographies in its source evidence. The existing ID, reference year, coordinates, radius and note effect remain unchanged. The year is a debated reference slot, not proof the two officials were present in Abydos or alive in exactly 2980 BCE; the place is Djet's burial area, not a known location of their work or an event.

Guarded manifest `reviews/3000_bce_djet_officials_2026-10.json` (canonical SHA-256 `2a0968ef78c4154bfa27ca726e09a993510b30098bacbb5222f670ebad0ea5b9`) preserves before/after for rollback. Nine unit tests passed before and after, staged reversal and the unique installed after-image passed. No game, Forge, save or jar test, and no integrity-manifest regeneration.

## Status

No VIP became spawnable; natural VIP spawning and player-driven timeline branching remain unimplemented. These people and relationships are evidence leads, not programmed decisions or behavior. Research remains incomplete worldwide and for all earlier years. **557 historical years partly worked; 0 fully collected**, unchanged because this revisits prior work. Continue connected-person research across regions and chronological backfill beyond 2940 BCE. The full crawler remains blocked by its storage guard.
