#!/usr/bin/env bash
# Build and install the Wikipedia history pack (harvester v2, see FIXES.md).
#
# Usage:
#   ./finalize.sh            # offline: re-harvest every year 3000 BC .. AD 2026 from the frozen
#                            #   census snapshot (+ the 292 overview pages), postprocess, leave out
#                            #   events the mod already has, install, verify through the real gazetteer
#   ./finalize.sh --preview  # same build, but writes only to /tmp and touches NOTHING in the mod
#   ./finalize.sh --live     # harvest from the live API instead of the snapshot (slow without a
#                            #   contact address: export HARVEST_UA="Name/1.0 (you@example.org)")
set -euo pipefail
cd /home/user/harvest

MODE=real; SRC=--snapshot
for a in "$@"; do
  case "$a" in
    --preview) MODE=preview ;;
    --live) SRC="" ;;
    *) echo "unknown option $a"; exit 2 ;;
  esac
done
if [ "$MODE" = preview ]; then OUTDIR=/tmp/wp_preview; mkdir -p "$OUTDIR"; else OUTDIR=/home/user/harvest; fi
RAW="$OUTDIR/events_v2_raw.jsonl"
PACK="$OUTDIR/events_wikipedia_v2.json"

echo "== 1. harvest (${SRC:-live}) =="
python3 harvest_run.py $SRC --overview "$RAW" | tail -40

echo "== 2. postprocess =="
python3 postprocess.py "$RAW" "$PACK" | tail -16

echo "== 3. install (duplicates of existing pins left out) =="
if [ "$MODE" = preview ]; then
  python3 install_pack.py "$PACK" --dry-run | head -20
  echo "== PREVIEW ONLY: nothing installed =="
  exit 0
fi
python3 install_pack.py "$PACK" | tail -2
# keep the saved workspace small (snapshot cap ~128 MB): the intermediates are rebuilt in ~10 s
gzip -f -9 "$RAW" "$PACK" "$OUTDIR/install_report.json"

echo "== 4. verify through the mod's HistoryGazetteer =="
bash verify.sh | tail -40
