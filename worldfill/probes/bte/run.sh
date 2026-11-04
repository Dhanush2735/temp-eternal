#!/bin/bash
# Turn 93: the world's own map projection (Terra++'s real BTE projection, copied from terra3/ with its
# Lombok, Jackson, Netty and PorkLib parts taken out) next to Terra++'s public API projection.
# Prints, for 12 cities: blocks per km, how far true north is turned from Minecraft north, and where the
# public API's block for the same place really is. Java 11 is enough.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT=/tmp/bte_out
rm -rf "$OUT" && mkdir -p "$OUT/net/buildtheearth/terraminusminus/projection/dymaxion"
cp /home/user/terra3/src/main/resources/net/buildtheearth/terraminusminus/projection/dymaxion/conformal.gz \
   "$OUT/net/buildtheearth/terraminusminus/projection/dymaxion/"
cd "$HERE"
javac -encoding UTF-8 -d "$OUT" $(find . -name "*.java")
java -cp "$OUT" Probe
java -cp "$OUT" KK
