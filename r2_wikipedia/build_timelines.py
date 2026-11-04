#!/usr/bin/env python3
"""Build a source-linked, explicitly non-spawnable R3 person timeline staging file.

Claims are not history verified by the game. Birth/death places are events, not
whole-life residence. Residence/work location claims without both qualified bounds are
retained with unknown duration; no lifetime dates or positions are fabricated.
"""
import argparse,gzip,json
from staged_exports import open_text as open_staged_text
from collections import Counter

LOC_ROLES={'birth_place':'birth','death_place':'death','residence':'residence','work_location':'work_location'}
OTHER_ROLES={'offices':'office','events_participated':'participated_event'}


def values(snaks):
 return [s.get('year_value') for s in snaks if s.get('snaktype')=='value' and s.get('year_value') is not None]


def bounded_years(claim):
 """Return an explicit qualified year range, or None; source qualifiers remain attached.

 These years are a coarse, inclusive *staging index*, not day-level dates or proof of
 continuous physical presence. Uncertain qualifiers and conflicting bounds forbid even
 a coarse interval. Thus no number is a spawn condition.
 """
 q=claim.get('qualifiers',{})
 if any(k in q for k in ('P1480','P1319','P1326','P2241','P1013')):return None
 starts=q.get('P580',[]); ends=q.get('P582',[])
 if len(starts)!=1 or len(ends)!=1:return None
 for s in starts+ends:
  if s.get('snaktype')!='value' or s.get('year_value') is None or s.get('before')!=0 or s.get('after')!=0:return None
 a=starts[0]['year_value'];b=ends[0]['year_value']
 if a>b:return None
 return {'start_year':a,'end_year':b,'precision':'year_index_only_not_a_spawn_range'}


def build(person,places):
 out=[];details=person['details'];wd=person['wikidata']
 common={'person_id':person['id'],'name':person['name'],'status':'unreviewed_not_spawnable',
         'wikipedia_source':person['wikipedia'],'wikidata_source':wd}
 for field,role in LOC_ROLES.items():
  for claim in details.get(field,[]):
   q=claim['value'].get('entity_id'); place=places.get(q)
   entry={**common,'kind':role,'statement':claim,'place_id':q,
       'place_name':place.get('name') if place else None,
       'place_source':{'url':place.get('source_url'),'revision':place.get('wikidata_revision')} if place else None,
       'coordinate_claims':place.get('coordinate_claims',[]) if place else [],
       'time_scope':'birth_event_only' if role=='birth' else 'death_event_only' if role=='death' else 'qualified_interval_or_unknown',
       'explicit_year_index':bounded_years(claim) if role in ('residence','work_location') else None,
       'associated_life_dates':details.get('birth_date' if role=='birth' else 'death_date',[]) if role in ('birth','death') else [],
       'note':'Candidate source statements only. Place coordinates do not locate the person for a whole lifetime.'}
   out.append(entry)
 for field,role in OTHER_ROLES.items():
  for claim in details.get(field,[]):
   out.append({**common,'kind':role,'statement':claim,'explicit_year_index':bounded_years(claim),
     'note':'Role or event participation is not a physical location or a scripted scene.'})
 return out


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--vip',default='r2_wikipedia/vip_candidates.jsonl.gz');p.add_argument('--places',default='r2_wikipedia/place_candidates.jsonl.gz');p.add_argument('--output',default='r2_wikipedia/person_timelines.jsonl.gz');a=p.parse_args()
 with open_staged_text(a.places) as f:places={r['id']:r for r in map(json.loads,f)}
 counts=Counter();people=set()
 with open_staged_text(a.vip) as src,open(a.output,'wb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as dst:
  for line in src:
   for e in build(json.loads(line),places):
    counts[e['kind']]+=1;people.add(e['person_id']);dst.write((json.dumps(e,ensure_ascii=False,separators=(',',':'))+'\n').encode())
 print('timeline candidate statements:',sum(counts.values()),'people:',len(people),'kinds:',dict(counts));print('These are unreviewed and cannot be spawned directly.')
if __name__=='__main__':main()
