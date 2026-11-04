#!/usr/bin/env bash
# Step 45 part 5: the item resolver.
set -e
JDK17=${JDK17:-/home/user/.cache/tools/jdk17}
CP=eternal/src/main/java
OUT=/tmp/ee45d
rm -rf "$OUT"; mkdir -p "$OUT"
"$JDK17"/bin/javac -nowarn -encoding UTF-8 -d "$OUT" -cp "$CP" \
  eternal/src/main/java/com/eternalengine/war/WeaponItems.java \
  worldfill/probes/Step45ItemsProbe.java 2>&1 | grep -v '^Note:' || true
"$JDK17"/bin/java -Dfile.encoding=UTF-8 -cp "$OUT:eternal/src/main/resources" Step45ItemsProbe
