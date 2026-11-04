#!/usr/bin/env python3
"""Archive a first set of Hyderabad Wikipedia source revisions; not a completeness claim."""
import concurrent.futures,datetime,hashlib,json,lzma,sys
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'r2_wikipedia'))
from batch_year_resolver import resolve_chunk,years
from storage_guard import workspace_bytes,HYDERABAD_PILOT_LIMIT_BYTES
API='https://en.wikipedia.org/w/api.php'
UA='EternalEngine Hyderabad historical research/1.0 (English Wikipedia, reproducible source archive)'
TITLES=['3rd millennium BC','30th century BC','History of Hyderabad','History of Telangana','Hyderabad','Secunderabad','Charminar','Golconda','Hasmathpet cairns','Khajaguda','Jubilee Hills','Durgam Cheruvu','Musi River (India)','Qutb Shahi tombs','Golconda Sultanate','Muhammad Quli Qutb Shah','Ibrahim Quli Qutb Shah Wali','Hayat Bakshi Begum','Sultan Muhammad Qutb Shah','Abdullah Qutb Shah','Hyderabad State','Operation Polo','Great Musi Flood','2013 Hyderabad blasts','Malkajgiri','Hussain Sagar']
OUT=ROOT/'hyderabad_research/wikipedia_foundation_2026-11.json.xz'
# Original PEOPLE run included the unrelated Bangladeshi naval officer Mahbub Ali Khan.
# Keep the archived revision as an explicitly excluded false positive; use CORRECTIONS below.
PEOPLE=['30th century BC','Hussain Shah Wali','Kshetrayya','Amjad Hyderabadi','Mahbub Ali Khan','Sarojini Naidu','Makhdoom Mohiuddin','Rudrama Devi','Quli Qutb Mulk','Challagalla Narasimham','Bhagmati']
CORRECTIONS=['30th century BC','Mahbub Ali Khan, Asaf Jah VI','Osman Ali Khan, Asaf Jah VII','Salar Jung I','Moula Ali','Dilsukhnagar','Padmaja Naidu','Aghorenath Chattopadhyay']
def query(params):
 if workspace_bytes()>=HYDERABAD_PILOT_LIMIT_BYTES:raise RuntimeError('Pilot storage guard reached')
 r=requests.get(API,params={'action':'query','format':'json','formatversion':2,'maxlag':5,**params},headers={'User-Agent':UA},timeout=45);r.raise_for_status();d=r.json()
 if 'error' in d or 'continue' in d:raise RuntimeError('API error or pagination: '+str(d.get('error',d.get('continue'))))
 return d

def collect(titles=TITLES,out=OUT):
 if out.exists():raise FileExistsError(out)
 info=query({'prop':'info|pageprops','redirects':1,'titles':'|'.join(titles)})
 resolutions=resolve_chunk(titles,info)
 pages=info['query']['pages'];indexed={x['title']:x for x in pages}
 for r in resolutions:
  if r['status']!='resolved' or 'disambiguation' in indexed[r['canonical_title']].get('pageprops',{}):raise ValueError('Unresolved or ambiguous '+str(r))
 ids=sorted({r['lastrevid'] for r in resolutions})
 def fetch(g):return query({'revids':'|'.join(map(str,g)),'prop':'revisions|pageprops','rvprop':'ids|timestamp|content','rvslots':'main'})['query']['pages']
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:found=[p for batch in pool.map(fetch,[ids[i:i+10] for i in range(0,len(ids),10)]) for p in batch]
 if {(p['pageid'],p['revisions'][0]['revid'],p['title']) for p in found}!={(r['pageid'],r['lastrevid'],r['canonical_title']) for r in resolutions}:raise ValueError('Revision identity changed or is incomplete')
 for p in found:
  text=p['revisions'][0]['slots']['main']['content'];p['wikitext_sha256']=hashlib.sha256(text.encode('utf-8')).hexdigest()
 labels=years(3000,2951)
 yearinfo=query({'prop':'info|pageprops','redirects':1,'titles':'|'.join(labels)})
 yearrows=resolve_chunk(labels,yearinfo)
 if any(x['status']!='resolved' for x in yearrows):raise ValueError('A year title is missing')
 if any((x['pageid'],x['lastrevid'],x['canonical_title']) not in {(p['pageid'],p['revisions'][0]['revid'],p['title']) for p in found} for x in yearrows):raise ValueError('Year targets not in archive or changed')
 doc={'schema':'hyderabad-wikipedia-research-foundation-v1','retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'license':'Wikipedia text CC BY-SA; attribution required: https://en.wikipedia.org/wiki/Wikipedia:Copyrights','scope':'Selected source archive and 50 BCE redirect checks. No claim of full linked article collection, year coverage, historical accuracy, gameplay updates or spawnable people.','notes':'Year titles can redirect to broader periods, not evidence of precise yearly events. All wikitext is raw and transclusions unexpanded; some article content is inaccurate, contested or unsourced. Hyderabad region is not the same as the current city footprint. Future projections must be separate.','resolutions':resolutions,'year_title_resolutions_3000_2951_bce':yearrows,'pages':found}
 payload=lzma.compress(json.dumps(doc,ensure_ascii=False,separators=(',',':')).encode(),preset=9)
 if workspace_bytes()+len(payload)>=HYDERABAD_PILOT_LIMIT_BYTES:raise RuntimeError('Pilot storage guard refuses source archive')
 with out.open('xb') as f:f.write(payload)
 if json.loads(lzma.decompress(out.read_bytes()))!=doc:
  out.unlink();raise ValueError('Saved archive verification failed')
 print('Archived',len(found),'distinct source revisions;',len(yearrows),'BCE year-title resolutions;',len(payload),'bytes. No years fully collected.')
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group();group.add_argument('--people',action='store_true');group.add_argument('--corrections',action='store_true');args=parser.parse_args()
 if args.people:collect(PEOPLE,ROOT/'hyderabad_research/wikipedia_people_2026-11.json.xz')
 elif args.corrections:collect(CORRECTIONS,ROOT/'hyderabad_research/wikipedia_corrections_2026-11.json.xz')
 else:collect()
