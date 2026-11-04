#!/usr/bin/env bash
# THE VOCABULARY INVARIANT: no register may cite an id the rest of the mod cannot resolve.
#
# Born 2026-10-22 from the marking turn: 96.4% of site civHints were pack ids the ruler register had
# never heard of ("india", "rome", "china_tang") while its own vocabulary is polity slugs. A cited id
# that resolves to nothing is a name the mod will invent a civilization from.
#
# Threshold, written before the numbers are seen: UNKNOWN must be 0 for borders and polity ids, and
# every remaining site id must be classified as known, aliasable, or a declared region.
set -uo pipefail
JDK="${JDK17:-/home/user/.cache/jdk17}"; GSON=/home/user/libs/gson-2.10.1.jar
MOD=/home/user/eternal; HERE=/home/user/worldfill; OUT=/home/user/.cache/wf_probe_vocab
rm -rf "$OUT"; mkdir -p "$OUT"
"$JDK/bin/javac" -J-Xmx900m -encoding UTF-8 -nowarn -proc:none -cp "$GSON" \
  -sourcepath "$HERE/stubs:$HERE/stubs_headless:$MOD/src/main/java" -d "$OUT" \
  "$HERE/probes/VocabularyProbe.java" || { echo "COMPILE FAILED"; exit 2; }
"$JDK/bin/java" -Xmx1600m -Dfile.encoding=UTF-8 -cp "$OUT:$MOD/src/main/resources:$GSON" VocabularyProbe
