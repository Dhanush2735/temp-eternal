#!/usr/bin/env bash
# Step 44 part 2 (E4): fetch the Allen-Unger Global Commodity Prices Database.
#
# The build reads it from /tmp, which does not survive between sessions, so run this first:
#
#     bash worldfill/fetch_prices.sh && python3 worldfill/build_prices.py
#
# The database is deposited at DANS (doi:10.17026/dans-zsu-xavf) and the IISH; this script uses
# a GitHub mirror that keeps the same 973 tab-delimited files, one per market-commodity pair,
# because it can be fetched with curl rather than clicked through a repository form.
#
# It is 120 MB compressed, so only the allenunger directory is unpacked (37 MB, 973 files).
set -euo pipefail
DEST="${1:-/tmp/fc}"
TARBALL=/tmp/fc.tar.gz
URL="https://codeload.github.com/unbalancedparentheses/forex-centuries/tar.gz/refs/heads/main"

if [ -d "$DEST/forex-centuries-main/data/sources/allenunger" ]; then
  n=$(ls "$DEST/forex-centuries-main/data/sources/allenunger" | wc -l)
  echo "already unpacked: $n files at $DEST/forex-centuries-main/data/sources/allenunger"
  exit 0
fi

echo "fetching $URL ..."
curl -sSL -o "$TARBALL" "$URL"
echo "$(stat -c%s "$TARBALL") bytes"

echo "unpacking only the allenunger files ..."
mkdir -p "$DEST"
tar xzf "$TARBALL" -C "$DEST" --wildcards "*/sources/allenunger/*"
rm -f "$TARBALL"

n=$(ls "$DEST/forex-centuries-main/data/sources/allenunger"/*.tab 2>/dev/null | wc -l)
echo "done: $n .tab files"
if [ "$n" -lt 900 ]; then
  echo "PROBLEM: expected about 973 files, got $n"
  exit 1
fi
