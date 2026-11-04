#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JAVA_HOME="${JAVA_HOME:-/home/user/.cache/jdk17download}"
GSON="${GSON_JAR:-/home/user/.cache/r2_storage/gson-2.10.1.jar}"
TMP="$(mktemp -d /home/user/.cache/r2_storage/timeline-probe-XXXXXX)"
trap 'rm -rf "$TMP"' EXIT
SRC="$ROOT/eternal/src/main/java/com/eternalengine"
"$JAVA_HOME/bin/javac" -encoding UTF-8 -cp "$GSON" -d "$TMP" \
 "$ROOT"/r2_wikipedia/java_probe/timeline_stubs/javax/annotation/Nullable.java \
 "$ROOT"/r2_wikipedia/java_probe/timeline_stubs/com/eternalengine/core/WorldStateManager.java \
 "$ROOT"/r2_wikipedia/java_probe/timeline_stubs/com/eternalengine/timeline/{DeedLedger,RealityRiftController,DivergenceCascadeEngine}.java \
 "$ROOT"/r2_wikipedia/java_probe/com/eternalengine/civilization/HistoricalPresence.java \
 "$SRC"/civilization/{SettlementRank,SettlementYearEstimator,HistoryGazetteer}.java \
 "$SRC"/incident/IncidentSeed.java "$SRC"/clock/Timeline.java \
 "$SRC"/timeline/{TimelineManager,TimelineBranch,AlternativeTimelineEngine,TimelineSeed,BranchSuppression,SiblingIndex,BranchChronicle,Chronicler,Provenance,PossibleFutureEvent,AlternativeEvent,ScenarioDefinition,ScenarioEvent,ScenarioRegistry}.java \
 "$ROOT/r2_wikipedia/java_probe/TimelineManagerProbe.java"
"$JAVA_HOME/bin/java" -Xmx1024m -cp "$TMP:$ROOT/eternal/src/main/resources:$GSON" TimelineManagerProbe
