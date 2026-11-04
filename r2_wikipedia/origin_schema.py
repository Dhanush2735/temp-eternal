"""Compact storage for the complete people-discovery provenance graph.

The `origins` view preserves the original six-column interface. Source metadata
and repeated candidate IDs are stored once. The insert trigger preserves the
original primary-key and ignore-duplicate semantics.
"""
STATEMENTS = [
'''CREATE TABLE IF NOT EXISTS origin_sources (
 id INTEGER PRIMARY KEY, source_pageid INTEGER NOT NULL, source_title TEXT NOT NULL,
 source_revid INTEGER NOT NULL, UNIQUE(source_pageid, source_title, source_revid))''',
'''CREATE TABLE IF NOT EXISTS origin_candidates (
 id INTEGER PRIMARY KEY, candidate_id TEXT NOT NULL UNIQUE)''',
'''CREATE TABLE IF NOT EXISTS origin_links (
 subject_id INTEGER NOT NULL REFERENCES subjects(id), source_id INTEGER NOT NULL REFERENCES origin_sources(id),
 source_pageid INTEGER NOT NULL, source_revid INTEGER NOT NULL, source_line INTEGER NOT NULL,
 candidate_key INTEGER NOT NULL REFERENCES origin_candidates(id),
 PRIMARY KEY(subject_id,source_pageid,source_revid,source_line)) WITHOUT ROWID''',
'''CREATE VIEW IF NOT EXISTS origins AS
 SELECT s.title AS title, p.source_pageid AS source_pageid, p.source_title AS source_title,
 p.source_revid AS source_revid, l.source_line AS source_line, c.candidate_id AS candidate_id
 FROM origin_links l JOIN subjects s ON s.id=l.subject_id JOIN origin_sources p ON p.id=l.source_id
 JOIN origin_candidates c ON c.id=l.candidate_key''',
'''CREATE TRIGGER IF NOT EXISTS origins_insert INSTEAD OF INSERT ON origins BEGIN
 SELECT CASE WHEN NOT EXISTS(SELECT 1 FROM subjects WHERE title=NEW.title)
             THEN RAISE(ABORT,'origin subject missing') END;
 INSERT OR IGNORE INTO origin_sources(source_pageid,source_title,source_revid)
 VALUES(NEW.source_pageid,NEW.source_title,NEW.source_revid);
 INSERT OR IGNORE INTO origin_candidates(candidate_id) VALUES(NEW.candidate_id);
 INSERT OR IGNORE INTO origin_links(subject_id,source_id,source_pageid,source_revid,source_line,candidate_key)
 VALUES((SELECT id FROM subjects WHERE title=NEW.title),
   (SELECT id FROM origin_sources WHERE source_pageid=NEW.source_pageid AND source_title=NEW.source_title AND source_revid=NEW.source_revid),
   NEW.source_pageid,NEW.source_revid,NEW.source_line,
   (SELECT id FROM origin_candidates WHERE candidate_id=NEW.candidate_id));
 END''',
]
SCHEMA = ';\n'.join(STATEMENTS)+';\n'
