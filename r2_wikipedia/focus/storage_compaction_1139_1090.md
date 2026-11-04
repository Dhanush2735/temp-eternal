# 1139–1090 BCE storage compaction

Formatting only on canonical-hash-locked manifests. Parsed objects and canonical hashes were verified, and the matching installer guard validated before and after. Raw SHA text scan covered selected workspace text, not binary or external references. No rollback provenance deleted.

| Manifest | Before → after bytes | Raw SHA before → after | Canonical SHA |
|---|---:|---|---|
| `1000_960_bce_context_2026-10.json` | 55708 → 41140 | `8b192b46dd1c5b3b38b24063db53abaa10898c59aba954a90d208a8a0da29c87` → `4e8bbef23d0526e68965eede944c8b8ab3161aef6d5a97d1b8af02daf0eeec7d` | `216d8bc0c9da786884d6c954df1459fb9814b89053d90c4a487e80e893a75447` |
| `1150_1110_bce_context_2026-10.json` | 46304 → 33783 | `7f9c44b2e1eacb95a73831cc6a42859b930903760c673e398912e55c1d8ff2c5` → `5d781abd71f9b79437e20ba75ae4b02e014e84c184b314a2cb639a4461d51b7a` | `2a1b867f4ffd40ff1976315c47ffab04b8f20431eb9532a24798376282193ed4` |
| `1600_1560_bce_context_2026-10.json` | 52630 → 39325 | `7d19f977f8c6c9de9550ba055851b83e125dc87d922e3b45b8dfc4da31440a16` → `f68ae961950e2ce80857c7dcdf79f36a7b640fd1160347f73008056d5cc01437` | `a5a06da77d0dd773ebb3d30b084a24329d0a309a9848d80f4aeadb437e78c0c7` |
| `1100_1060_bce_context_2026-10.json` | 51206 → 37846 | `0eec2e1b58cc918ed786daa66269e5a7e9774d825c779ff72b1dc8007cbfb120` → `ad87a3ee3e036b3e23c259fd20956564af11f3f368d401ba806a2e2a076ff101` | `8365d4e5a47d3f4118f516e533e2933c3f29305c0948885affdc04557baed8e4` |

Saved 53754 bytes before log.

## Interrupted preparatory compaction

The first compaction attempt successfully compacted the following three locked manifests and validated their objects before and after, then stopped on an already-compact fourth file before writing its log. Their original raw-byte hashes and byte counts were not saved; this is a raw-format provenance limitation. No parsed content or canonical hash was changed. Selected text references to each old raw hash were checked before writing, but binary and external references cannot be excluded. Current raw and canonical hashes follow:

- `150_110_bce_context_2026-10.json`: raw `ca3e28a5f3050a4cafa592a5e8bcf68f931201a728a730a84c85fe12dd04992e`, canonical `296a62df5cca343a08771cd96ab21f27cf9d22a6972696b68f41b87a4824b280`.
- `100_60_bce_context_2026-10.json`: raw `6e1fe7c5718766b1bf85539f6633937b751e3e73dee7db7a67e1fccd6145da43`, canonical `60720fcca2974793f0303122dc22813cfca42a8518f4157c4103f292c880bc71`.
- `50_10_bce_context_2026-10.json`: raw `5f054055a8026fd68a80a28d9c619f00d13aab65f29b4b2bd096a582b603accb`, canonical `95efbe12a6e5de7e6e49c2880c775dd5316a0bfdb0f19afba9b69fff866e6f34`.

Later lossless gzip compression of six further BCE context manifests is mapped in `../reviews/complex_manifest_compression_1112_2026-10.json`; this table retains its historical filenames and hashes.
