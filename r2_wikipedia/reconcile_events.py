#!/usr/bin/env python3
"""Propose exact-text links between history candidates and existing game events.

This is review-only. Name similarity does not establish event identity or truth;
coordinates, dates and the existing game records are never changed. Historic
sources and non-Wikipedia event packs remain in place.
"""
import argparse,collections,gzip,json,re,unicodedata
from pathlib import Path
from prepare_history import explicit_label,PREFIX
from staged_exports import open_text as open_staged_text

ROOT=Path(__file__).resolve().parent.parent
HISTORY=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'


def normalized(text):
 text=unicodedata.normalize('NFKC',text or '').casefold()
 # Convert punctuation to boundaries, preserving words and numbers.
 return ' '.join(''.join(ch if ch.isalnum() else ' ' for ch in text).split())


def candidate_key(record):
 text=record.get('display_text_unverified','').strip()
 # Remove only a recognized simple date label; never strip an unparsed range.
 if explicit_label(text):text=text[PREFIX.match(text).end():].strip()
 n=normalized(text)
 if len(n)<32 or len(n.split())<5:return None
 if record.get('section_kind')=='reference_or_navigation_section':return None
 return n


def assessment(candidate,event):
 year=candidate.get('explicit_leading_year');start=event.get('start')
 if not year or year.get('approximate') or not isinstance(start,int) or isinstance(start,bool):return 'exact_text_year_not_comparable'
 if year['year']==start:return 'exact_text_same_labeled_start_year'
 return 'exact_text_possible_start_year_conflict'


def compare(candidates,pack_paths):
 lookup=collections.defaultdict(list)
 for r in candidates:
  key=candidate_key(r)
  if key:lookup[key].append(r)
 matches=collections.defaultdict(list);packs=0;events=0
 for path in pack_paths:
  path=Path(path)
  with (gzip.open(path,'rt',encoding='utf8') if path.name.endswith('.gz') else open(path,'r',encoding='utf8')) as f: data=json.load(f)
  if not isinstance(data,dict) or not isinstance(data.get('events'),list):continue
  packs+=1
  for e in data['events']:
   if not isinstance(e,dict) or not isinstance(e.get('name'),str):continue
   events+=1
   for candidate in lookup.get(normalized(e['name']),()):
    matches[candidate['id']].append({'pack':path.name,'event_id':e.get('id'),'existing_name':e['name'],
      'existing_start':e.get('start'),'existing_end':e.get('end'),'existing_confidence':e.get('confidence'),
      'assessment':assessment(candidate,e)})
 out=[]
 for r in candidates:
  if r['id'] in matches:
   out.append({'schema':'eternal-r2-event-reconciliation-v1','candidate_id':r['id'],'source':r['source'],
      'candidate_text':r['display_text_unverified'],'candidate_explicit_year':r.get('explicit_leading_year'),
      'matches':matches[r['id']], 'status':'review_only_not_an_identity_or_truth_verification'})
 return out,{'packs':packs,'events':events,'candidates':len(candidates),'matched_candidates':len(out),
   'pairs':sum(len(r['matches']) for r in out),'assessments':dict(collections.Counter(m['assessment'] for r in out for m in r['matches']))}


def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--input',default='r2_wikipedia/history_candidates.jsonl.gz');ap.add_argument('--history-dir',default=str(HISTORY));ap.add_argument('--output',default='r2_wikipedia/event_reconciliation.jsonl.gz');ap.add_argument('--summary',default='r2_wikipedia/event_reconciliation_summary.json');a=ap.parse_args()
 base=Path(a.history_dir);index=json.loads((base/'index.json').read_text(encoding='utf8'))
 # Fail closed on a missing indexed pack, rather than misrepresent a partial comparison.
 paths=[base/p for p in index['packs']]
 for p in paths:
  if not p.is_file():raise FileNotFoundError(f'Indexed pack missing: {p}')
 with open_staged_text(a.input) as f:candidates=[json.loads(l) for l in f]
 out,stats=compare(candidates,paths)
 with open(a.output,'wb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as gz:
  for r in out:gz.write((json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n').encode())
 Path(a.summary).write_text(json.dumps(stats,indent=2)+'\n',encoding='utf8')
 print(json.dumps(stats,indent=2));print('Exact-text matches are suggestions, not verified duplicates. No game records changed.')
if __name__=='__main__':main()
