#!/usr/bin/env bash
# Provision a JDK for the syntax gate into a directory the turn-end SNAPSHOT IGNORES.
#
# Why this exists (turn 234): the workspace snapshot is best-effort capped at about 128 MB /
# 10,000 files. A JDK is ~300 MB, so installing it INSIDE the snapshot area (e.g. /home/user/tools)
# steals the room that shipped data needs, and the snapshot culls it anyway (turn 232 saw a JDK
# half-extracted with execute bits stripped - the gate then reported "0 diagnostics" and looked
# clean while javac could not even load libjli.so). Regenerable tools live in excluded dirs:
# build/, .cache/, dist/, out/, target/, node_modules/ and friends are never snapshotted.
#
# Usage:  bash worldfill/bootstrap_jdk.sh
# Then:   export JDK17=/home/user/build/jdk17 && bash worldfill/syntax_gate.sh [files...]
set -euo pipefail
DEST="${JDK_HOME:-/home/user/build/jdk17}"
if [ -x "$DEST/bin/javac" ] && "$DEST/bin/javac" -version >/dev/null 2>&1; then
  echo "JDK ready at $DEST ($("$DEST/bin/javac" -version 2>&1))"
  echo "export JDK17=$DEST"
  exit 0
fi
echo "downloading Adoptium JDK 17 to $DEST ..."
rm -rf "$DEST"
mkdir -p "$DEST"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
curl -sL -o "$TMP/jdk17.tar.gz" \
  "https://api.adoptium.net/v3/binary/latest/17/ga/linux/x64/jdk/hotspot/normal/eclipse"
tar -xzf "$TMP/jdk17.tar.gz" -C "$DEST" --strip-components=1
chmod -R u+x "$DEST/bin" "$DEST/libexec" 2>/dev/null || true
if [ ! -f "$DEST/lib/libjli.so" ]; then
  echo "FAIL: extraction incomplete (lib/libjli.so missing) - delete $DEST and retry" >&2
  exit 1
fi
"$DEST/bin/javac" -version
echo "export JDK17=$DEST"
