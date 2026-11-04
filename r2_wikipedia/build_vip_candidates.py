#!/usr/bin/env python3
"""Prepare compact, source-linked VIP *candidates* from collected biography data.

The result is staging data, not a mod pack. It does not assert locations of presence,
resolve conflicting dates, infer missing lifespan, invent scenes, or spawn NPCs.
"""
import argparse,gzip,json,re,sys
from collections import Counter
from pathlib import Path
from staged_exports import open_text as open_staged_text

PROPERTIES={
 'P569':'birth_date','P570':'death_date','P19':'birth_place','P20':'death_place',
 'P551':'residence','P937':'work_location','P106':'occupations','P39':'offices',
 'P27':'citizenships','P22':'father','P25':'mother','P26':'spouses','P40':'children',
 'P3373':'siblings','P69':'education','P102':'political_parties','P463':'memberships',
 'P108':'employers','P1344':'events_participated','P1412':'languages','P140':'religions',
 'P166':'awards','P800':'works','P21':'sex_or_gender',
}
# JSON API dates are in historical numbering: -0001 is 1 BCE, unlike RDF/SPARQL.
TIME_RE=re.compile(r'^([+-])(\d{4,})-(\d{2})-(\d{2})T')


def decode_snak(s):
 kind=s.get('snaktype','unknown')
 result={'snaktype':kind}
 if kind!='value':return result
 dv=s.get('datavalue',{}); t=dv.get('type'); value=dv.get('value');result['type']=t
 if t=='wikibase-entityid' and isinstance(value,dict):
  result['entity_id']=value.get('id')
 elif t=='time' and isinstance(value,dict):
  result['time_original']=value.get('time');result['precision']=value.get('precision')
  result['calendar_model']=value.get('calendarmodel');result['before']=value.get('before');result['after']=value.get('after')
  m=TIME_RE.match(value.get('time') or '')
  prec=value.get('precision') if isinstance(value.get('precision'),int) else 0
  if m:
   n=int(m.group(2)); y=(-n if m.group(1)=='-' else n)
   # Coarser-than-year values only identify a bucket, not the person's actual year.
   result['year_value']=y if y!=0 and prec>=9 else None
   result['month_value']=int(m.group(3)) if prec>=10 and int(m.group(3)) else None
   result['day_value']=int(m.group(4)) if prec>=11 and int(m.group(4)) else None
  else:result['year_value']=None
 else:result['value']=value
 return result


def normalize_claim(claim):
 return {'statement_id':claim.get('id'), 'rank':claim.get('rank','normal'),
         'value':decode_snak(claim.get('mainsnak',{})),
         # Do not erase qualifiers (approximate dates, start/end and other context).
         'qualifiers':{p:[decode_snak(s) for s in snaks] for p,snaks in claim.get('qualifiers',{}).items()},
         'reference_hashes':[r.get('hash') for r in claim.get('references',[]) if r.get('hash')]}


def build(row):
 wd=row['wikidata_source'];claims=wd.get('claims',{})
 details={name:[normalize_claim(c) for c in claims.get(pid,[])] for pid,name in PROPERTIES.items() if claims.get(pid)}
 issues=[]
 for name in ('birth_date','death_date'):
  active=[x for x in details.get(name,[]) if x['rank']!='deprecated']
  if not active: issues.append('missing_'+name)
  elif len({x['value'].get('year_value') for x in active if x['value'].get('year_value') is not None})>1:issues.append('multiple_'+name+'_years')
  if active and any(x['value'].get('year_value') is None for x in active): issues.append('imprecise_or_unknown_'+name)
 return {'schema':'eternal-r3-vip-candidate-v1','status':'unreviewed_not_spawnable',
    'id':row['identity']['wikidata_id'],'name':row['name'],
    'wikipedia':row['wikipedia_source'],
    'wikidata':{k:wd.get(k) for k in ('entity_id','revision_id','url','description_en')},
    'discovered_from':row.get('discovered_from',[]),
    'infobox_raw':row['infobox']['raw_fields'],'details':details,'review_flags':issues,
    'limits':['Wikipedia and Wikidata are separate sources; the claims below are Wikidata statements, not verified Wikipedia facts.',
      'Birth/death places are not evidence of where the person lived or acted at every date.',
      'Qualifiers, ranks, precision and conflicting values require interpretation; do not auto-spawn from this record.']}


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',default='r2_wikipedia/people_candidates.jsonl.gz');p.add_argument('--output',default='r2_wikipedia/vip_candidates.jsonl.gz');args=p.parse_args()
 n=0; flags=Counter();ids=set()
 with open_staged_text(args.input) as src,open(args.output,'wb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as dst:
  for line in src:
   r=build(json.loads(line))
   if r['id'] in ids:raise ValueError('duplicate person ID: '+r['id'])
   ids.add(r['id']);flags.update(r['review_flags']);dst.write((json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n').encode());n+=1
 print('Staged',n,'unreviewed VIP candidates in',args.output);print('review flags:',dict(flags))
if __name__=='__main__':main()
