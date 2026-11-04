#!/usr/bin/env python3
"""Stage/apply/rollback reviewed corrections to existing history-event records.

Fails closed on changed inputs and writes atomically. No NPC records, indexes,
other packs or unrelated event fields are altered. Event provenance is embedded
in each changed record, and the manifest retains the exact prior record.
"""
import argparse,copy,gzip,json,math,os,stat,tempfile
from pathlib import Path
from reconcile_events import normalized,candidate_key
from staged_exports import open_text as open_staged_text

ROOT=Path(__file__).resolve().parent.parent
PACK=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history/events_wikipedia.json.gz'
MANIFEST=ROOT/'r2_wikipedia/reviews/event_corrections_2026-10.json'
CANDIDATES=ROOT/'r2_wikipedia/history_candidates.jsonl.gz'
ALLOWED={'start','end','name','lat','lon','confidence','radiusKm'}


def corrected(update,candidate):
 before=update['before'];changes=update['changes'];source=update['candidate_source']
 if before.get('id')!=update['event_id']:raise ValueError('Manifest event ID mismatch')
 if candidate['id']!=update['candidate_id'] or candidate['source']!=source:raise ValueError('Candidate source changed')
 if candidate_key(candidate)!=normalized(before['name']):raise ValueError('Text identity check failed')
 evidence=candidate.get('explicit_leading_year')
 if not evidence or evidence.get('approximate') or evidence['year']!=changes.get('start'):raise ValueError('Source year label does not match correction')
 if set(changes)-ALLOWED or changes.get('end')!=changes['start']+1:raise ValueError('Invalid change set')
 if 'radiusKm' in changes:
  radius=changes['radiusKm']
  if isinstance(radius,bool) or not isinstance(radius,(int,float)) or not math.isfinite(radius) or not 0<radius<=200:
   raise ValueError('Invalid radius; it is a gameplay search radius, not a verified geographic extent')
 if not update.get('corroborating_sources') or not update.get('review_note'):raise ValueError('Review evidence missing')
 result=copy.deepcopy(before);result.update(changes)
 result['r2SourceEvidence']={'candidate_id':update['candidate_id'],'wikipedia_source':source,
   'corroborating_sources':update['corroborating_sources'],'review_note':update['review_note'],
   'reviewed_as_of':update['reviewed_as_of'],'date_precision':'year','location_precision':'regional reference point' if changes.get('confidence')=='wikipedia_region' else 'existing reference point'}
 return result


def transform(doc,manifest,candidates,reverse=False):
 if not isinstance(doc,dict) or not isinstance(doc.get('events'),list):raise ValueError('Invalid event pack')
 by_candidate={r['id']:r for r in candidates};updates=manifest['updates'];ids=[u['event_id'] for u in updates]
 if not ids or len(ids)!=len(set(ids)):raise ValueError('Empty or duplicate review IDs')
 index={}
 for i,row in enumerate(doc['events']):
  if isinstance(row,dict) and row.get('id') in ids:
   if row['id'] in index:raise ValueError('Duplicate event ID in pack')
   index[row['id']]=i
 if set(index)!=set(ids):raise ValueError('Reviewed event ID missing from pack')
 result=copy.deepcopy(doc)
 for update in updates:
  if not reverse and update.get('known_possible_duplicate_event_ids'):
   raise ValueError('Unresolved possible duplicates: '+update['event_id'])
  # Rollback must remain possible if the live staging export later changes or disappears.
  candidate=update.get('candidate_snapshot') if reverse else by_candidate.get(update['candidate_id'])
  if candidate is None:raise ValueError('Missing candidate or retained rollback snapshot')
  new=corrected(update,candidate);before=update['before'];i=index[update['event_id']]
  if doc['events'][i]!=(new if reverse else before):raise ValueError('Existing record differs from expected: '+update['event_id'])
  result['events'][i]=copy.deepcopy(before if reverse else new)
 # Deep-equality check for all unrelated pack content and rows.
 restored=copy.deepcopy(result)
 for update in updates:restored['events'][index[update['event_id']]]=doc['events'][index[update['event_id']]]
 if restored!=doc:raise ValueError('Unrelated pack content changed')
 return result


def reject_exact_year_duplicates(manifest,history_dir,target_name):
 """Reject matching old OR revised titles at the corrected year in indexed packs.

 This is only a lower bound: different wording can describe the same event, so
 manual review remains mandatory and known semantic duplicates also block writes.
 """
 history_dir=Path(history_dir)
 index=json.loads((history_dir/'index.json').read_text(encoding='utf8'))
 if target_name not in index['packs']:raise ValueError('Target pack is not indexed')
 sought={}
 for u in manifest['updates']:
  year=u['changes']['start']
  for name in (u['before']['name'],u['changes'].get('name',u['before']['name'])):
   sought.setdefault((normalized(name),year),[]).append(u['event_id'])
 for name in index['packs']:
  path=history_dir/name
  with (gzip.open(path,'rt',encoding='utf8') if name.endswith('.gz') else open(path,encoding='utf8')) as f:
   doc=json.load(f)
  for row in doc.get('events',[]):
   if not isinstance(row,dict):continue
   for event_id in sought.get((normalized(row.get('name')),row.get('start')),()):
    if name==target_name and row.get('id')==event_id:continue
    raise ValueError(f'Possible exact-text duplicate at corrected year: {event_id} vs {name}:{row.get("id")}')


def write_atomic_gzip(path,doc):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 mode=stat.S_IMODE(path.stat().st_mode) if path.exists() else None
 fd,tmp=tempfile.mkstemp(prefix='.reviewed-events-',suffix='.gz',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as out:
   out.write(json.dumps(doc,ensure_ascii=False,separators=(',',':')).encode('utf8'))
  with gzip.open(tmp,'rt',encoding='utf8') as f:
   if json.load(f)!=doc:raise ValueError('Output verification failed')
  if mode is not None:os.chmod(tmp,mode)
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)


def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['stage','apply','rollback']);ap.add_argument('--pack',default=str(PACK));ap.add_argument('--manifest',default=str(MANIFEST));ap.add_argument('--candidates',default=str(CANDIDATES));ap.add_argument('--output',default='/home/user/.cache/r2_storage/staged_events.json.gz');a=ap.parse_args()
 m=json.loads(Path(a.manifest).read_text(encoding='utf8'))
 if m.get('schema')!='eternal-r2-reviewed-event-corrections-v1' or Path(a.pack).name!=m.get('target'):raise ValueError('Wrong manifest or target pack')
 with gzip.open(a.pack,'rt',encoding='utf8') as f:doc=json.load(f)
 if a.action=='rollback':cs=[]
 else:
  with open_staged_text(a.candidates) as f:cs=[json.loads(l) for l in f]
 result=transform(doc,m,cs,reverse=a.action=='rollback')
 if a.action!='rollback':reject_exact_year_duplicates(m,Path(a.pack).parent,Path(a.pack).name)
 out=a.output if a.action=='stage' else a.pack
 if a.action=='stage' and Path(out).resolve()==Path(a.pack).resolve():raise ValueError('Stage output must differ from input')
 write_atomic_gzip(out,result);print(a.action,'complete:',len(m['updates']),'reviewed events, pack has',len(result['events']),'events;',out)
if __name__=='__main__':main()
