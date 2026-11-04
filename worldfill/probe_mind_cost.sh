#!/usr/bin/env bash
# Measures what a human-like villager mind would cost the server (no Minecraft needed).
# Model and numbers: probes/MindCostProbe.java. Needs JDK 17 (bash libs/get_jdk17.sh).
set -euo pipefail
cd "$(dirname "$0")/probes"
JAVA="${JAVA:-$HOME/.cache/jdk17/bin/java}"
[ -x "$JAVA" ] || JAVA=java
exec "$JAVA" -Xmx384m -XX:+UseSerialGC MindCostProbe.java
