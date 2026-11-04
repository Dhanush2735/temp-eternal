# Worldfill documentation

The original historical README is preserved losslessly as `README.original.md.xz` to make space for R2. Read it with `python worldfill/archived_history_reports.py README.original.md --print`, or restore a verified copy to `README.original.md` with `--restore` when space permits. The archive retains the previous notes and all original bytes.

Current requirements: `REQUIREMENTS.md`. Generated report archives: `archived_history_reports.py`. R2 progress: `../r2_wikipedia/PROGRESS.md`.

Additional archived generated reports: `money_coverage_report.json.xz` and `hazards_report.json.xz`; verify or restore with `python worldfill/archived_history_reports.py NAME [--restore]` (restoration requires sufficient guard headroom). Generators continue writing the original filenames.

Research-source archive: `sources/money/wikidata_currencies.tsv.xz` preserves the original Wikidata currency TSV byte-for-byte; it is not a generated report. Verify with `python r2_wikipedia/archive_generated_aux.py worldfill/sources/money/wikidata_currencies.tsv`, or add `--restore` when guard headroom is sufficient; restoration refuses overwrite. The old uncompressed path is absent until restored.

The historical static NPC UI previews `npc_talk_ui_preview.html` and `npc_knowledge_ui_preview.html` are preserved byte-for-byte as `.html.xz`. Verify with `python worldfill/archived_history_reports.py NAME`, print with `--print`, or restore the original filename with `--restore` when guard headroom is sufficient; restoration refuses overwrite. These were visual prototypes, not active game code.
