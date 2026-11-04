#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JAVA_HOME="${JAVA_HOME:-/home/user/.cache/jdk17download}"
GSON="${GSON_JAR:-/home/user/.cache/r2_storage/gson-2.10.1.jar}"
TMP="$(mktemp -d /home/user/.cache/r2_storage/sibling-audit-XXXXXX)"
trap 'rm -rf "$TMP"' EXIT
"$JAVA_HOME/bin/javac" -encoding UTF-8 -cp "$GSON" -d "$TMP" \
 "$ROOT/r2_wikipedia/java_probe/com/eternalengine/civilization/HistoricalPresence.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/civilization/SettlementRank.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/civilization/SettlementYearEstimator.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/civilization/HistoryGazetteer.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/timeline/SiblingIndex.java" \
 "$ROOT/eternal/src/main/java/com/eternalengine/timeline/BranchSuppression.java" \
 "$ROOT/r2_wikipedia/java_probe/SiblingIdentityAudit.java" \
 "$ROOT/r2_wikipedia/java_probe/FullSiblingRiskAudit.java"
"$JAVA_HOME/bin/java" -Xmx1536m -cp "$TMP:$ROOT/eternal/src/main/resources:$GSON" SiblingIdentityAudit
if [[ "${1:-}" == "full" ]]; then
  "$JAVA_HOME/bin/java" -Xmx1536m -cp "$TMP:$ROOT/eternal/src/main/resources:$GSON" FullSiblingRiskAudit
fi
