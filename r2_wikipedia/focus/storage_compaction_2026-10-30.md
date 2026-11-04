# Lossless review-scan JSON compaction

**Review-date provenance note:** Some earlier manifests, graphs and the compaction log record 2026-10-30, while earlier session context recorded the date as 2026-10-29 UTC. The supplied current local date is 2026-10-30 (Asia/Calcutta); the dates can overlap across time zones, but the original review timestamps were not preserved, so the discrepancy cannot be independently resolved. Treat those date labels as unverified; hash-locked evidence has not been silently changed.

Whitespace and Unicode escaping were removed from three standalone, unreviewed hazard overlap scans. Parsed JSON content was verified identical before and after; no game data, databases, rollback manifests, or assets were deleted. This changes the files’ raw byte hashes.

- `r2_wikipedia/reviews/2001_2021_ce_hazard_overlap_unreviewed.json`: 269674 → 179308 bytes; raw SHA-256 `4bf4a0f9dfeb122f73de09d0a0ab7cc2ada09b737dd1d3d2b7fe6e6ddab9d140` → `e3a087ce66c2d5d304feff137b0cc6e808eabd3bbfaa085d2f84824e21689ed9`; canonical semantic SHA-256 unchanged: `e324f7b9fa0c62be2369ed0d8b7d2e39d939c1849235a99a9c53282eb31cc4c5`.
- `r2_wikipedia/reviews/1951_1991_ce_hazard_overlap_unreviewed.json`: 222519 → 145749 bytes; raw SHA-256 `c6b8f89f44d44b1dc6b31b899614eadb47c907462a7849d582c0c5c5c7fab7ea` → `da98365d047cefaba4942624f13b8080f6755038c73e6c63b0bddfd103578d29`; canonical semantic SHA-256 unchanged: `e3633785c74ee641dbb76fde425a08c56072aa2b2c708f6d18f4f2e8164755f8`.
- `r2_wikipedia/reviews/1901_1941_ce_hazard_overlap_unreviewed.json`: 152988 → 99225 bytes; raw SHA-256 `7425e4f3c0fc3157c4c6d94b6c03a0a49003351c304b30c6558c0994b18b2fbc` → `938ae64fe15aa128b30788bfd9ece7c6c1f6e4efe261516d9ef8407d50f7e2ad`; canonical semantic SHA-256 unchanged: `29121e38664350abbddeb6c16a27b35d59608bfa0bcd59ab82b7cea862ca07b9`.

Saved 220,899 bytes.
