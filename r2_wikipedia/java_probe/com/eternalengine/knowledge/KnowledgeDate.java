package com.eternalengine.knowledge;
/** Only supports compiling NewsIndex for tests of its year-only data path. */
public final class KnowledgeDate { public static int year(int key) { return Math.floorDiv(key, 10000); } }
