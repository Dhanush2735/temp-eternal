#!/usr/bin/env bash
# Step 42: rebuild every data pack this step has added, from the sources that ARE in the snapshot.
#
# STANDING RULE (turn 155): the generated packs under
#   eternal/src/main/resources/data/eternalengine/eternal/history/
# are BUILD PRODUCTS, not sources. The workspace is near the snapshot size cap and new files in
# that directory have twice gone missing between turns, while the builders and their inputs
# (social_order_table.py, raw/step42/*.html.gz, world_rulers.json.gz, culture.json.gz) have
# always survived. So: run this at the start of any turn that needs the data, and never treat a
# .json.gz as the source of truth. Every builder prints its own check and fails loudly.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for b in build_law.py build_social.py build_justice.py build_border.py; do
  echo "--- $b"
  python3 "$HERE/$b" 2>&1 | tail -2
done
