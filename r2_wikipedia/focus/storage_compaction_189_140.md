# 189–140 BCE: lossless compression of unreviewed scans

These five are unreviewed CE hazard overlap scans, not gameplay packs. Restore exact original bytes using `gzip -dc FILE.json.gz > FILE.json`. Prior paths refer to uncompressed originals; selected project Python searches found no explicit readers of these filenames, but external dependencies were not checked. This report was written before removal.

| Original | Bytes original → gzip | SHA-256 original → gzip |
|---|---:|---|
| `1601_1641_ce_hazard_overlap_unreviewed.json` | 37540 → 6731 | `b73261b1abf86f05307bbd7563bea5e91b933be2ebbf09ac25cc85457f631f79` → `2ead20b962a6dc1501213adda2c1eb3851073857288ec94ed19eafbe62fe0b62` |
| `1851_1891_ce_hazard_overlap_unreviewed.json` | 34841 → 6677 | `198b3e48eaa15b0b7380a04732640270a07c22ae02d50a52abe8df492d5b6caa` → `df9f7db4ba9e4d1c6c52dc198a11aac2cd290fd4ddce8ee6ab4e0391af1554e9` |
| `1551_1591_ce_hazard_overlap_unreviewed.json` | 28879 → 5185 | `038fa391c65d95c1aff1f70205eff0069a7d21c71c361fe3fa10bb841a37c1d0` → `d36d540fc2717ef34935e3a90c348dad0e2596681ad3257ebced5ae0c6769c7a` |
| `1501_1541_ce_hazard_overlap_unreviewed.json` | 26720 → 4618 | `36d03febe1600aaebed93f6cdce8c7813896adaae666cf780c4c3cfc405e1440` → `22352cd50860feaece3cb83a8146d189ba4d7962433c7b33aff45a73a705999f` |
| `1801_1841_ce_hazard_overlap_unreviewed.json` | 24772 → 5168 | `1c8e0f8b0689dac4d2cf393a1f509cbfb134eb0a5420c6d3f9a72d3fb87d3a97` → `dc0868b5795bb809b25aabdf348595b896d765ba78f431e3950a59c73b518781` |

All decompressed bytes verified against originals before deletion.
