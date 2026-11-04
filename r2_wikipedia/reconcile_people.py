#!/usr/bin/env python3
"""Compare staged Wikipedia VIP candidates with existing mod people and VIP records.

This generates a review report only. Names and year matches are not proof of identity;
no mod files are edited, rows merged, NPCs spawned or deaths/locations inferred.
"""
import argparse,collections,gzip,json,re,unicodedata
from staged_exports import open_text as open_staged_text
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/'eternal/src/main/resources/data/eternalengine/eternal'


def name_key(name):
    # Conservative: case/punctuation/whitespace normalization, no accent folding,
    # transliteration, honorific stripping, initials guessing or fuzzy matching.
    s=unicodedata.normalize('NFKC',name or '').casefold()
    return ' '.join(re.findall(r'\w+',s,flags=re.UNICODE))


def years(person,field):
    # Keep all non-deprecated, year-precision values. Qualifiers and multiple values
    # are noted in the report rather than silently making a definitive choice.
    claims=[x for x in person.get('details',{}).get(field,[]) if x.get('rank')!='deprecated']
    vals=sorted({x.get('value',{}).get('year_value') for x in claims if isinstance(x.get('value',{}).get('year_value'),int)})
    return {'values':vals,'multiple':len(vals)>1,
            'has_qualifiers':any(bool(x.get('qualifiers')) for x in claims),
            'has_unknown_or_coarse':any(x.get('value',{}).get('year_value') is None for x in claims)}


def compare(person,old_birth,old_death):
    b=years(person,'birth_date');d=years(person,'death_date');conflicts=[];overlaps=[]
    for name,source,existing in (('birth',b,old_birth),('death',d,old_death)):
        if isinstance(existing,int) and source['values']:
            if existing in source['values']:overlaps.append(name)
            else:conflicts.append(name)
    if conflicts:label='name_match_date_conflict'
    elif len(overlaps)==2 and not (b['multiple'] or d['multiple'] or b['has_qualifiers'] or d['has_qualifiers'] or b['has_unknown_or_coarse'] or d['has_unknown_or_coarse']):label='name_and_years_agree_review_identity'
    else:label='name_match_dates_incomplete_or_uncertain'
    return {'assessment':label,'date_conflicts':conflicts,'date_overlaps':overlaps,
            'source_birth':b,'source_death':d,'identity_verified':False,'requires_review':True}


def index_records(vips,master):
    idx=collections.defaultdict(list)
    for rowno,v in enumerate(vips):
        idx[name_key(v.get('name'))].append({'dataset':'existing_vips','row':rowno,'id':v.get('vipId',v.get('id')),
           'name':v.get('name'),'birth_year':v.get('birthYear'),'death_year':v.get('historicalDeathYear')})
    for rowno,r in enumerate(master):
        if len(r)<4:continue
        idx[name_key(r[0])].append({'dataset':'famous_people_master','row':rowno,'id':None,
           'name':r[0],'birth_year':r[2],'death_year':r[3]})
    return idx


def reconcile(people,vips,master):
    idx=index_records(vips,master)
    for p in people:
        possible=[]
        for m in idx.get(name_key(p.get('name')),[]):
            possible.append({**m,**compare(p,m['birth_year'],m['death_year'])})
        yield {'person_id':p['id'],'name':p['name'],'wikipedia':p['wikipedia'],
               'wikidata':p['wikidata'],'status':'review_required',
               'match_method':'normalized complete name; not a verified identity',
               'matches':possible,'note':'Absence of an exact-name match does not prove this person is missing from the game.'}


def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--vip-candidates',default=str(ROOT/'r2_wikipedia/vip_candidates.jsonl.gz'));a.add_argument('--vips',default=str(DATA/'vips/foundation_vips.json'));a.add_argument('--master',default=str(DATA/'history/famous_people.json.gz'));a.add_argument('--out',default=str(ROOT/'r2_wikipedia/reconciliation.jsonl.gz'));args=a.parse_args()
    with open_staged_text(args.vip_candidates) as f:people=[json.loads(x) for x in f]
    with open(args.vips,encoding='utf8') as f:vips=json.load(f)
    with gzip.open(args.master,'rt',encoding='utf8') as f:master=json.load(f)['people']
    n=0;stats=collections.Counter()
    with open(args.out,'wb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as out:
        for row in reconcile(people,vips,master):
            n+=1
            for source in ('existing_vips','famous_people_master'):
                if any(m['dataset']==source for m in row['matches']):stats[f'people_with_{source}_name_match']+=1
            stats.update(m['assessment'] for m in row['matches'])
            out.write((json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n').encode())
    print('Compared',n,'candidates with',len(vips),'existing VIPs and',len(master),'people rows')
    print('Review metrics:',dict(stats));print('No existing data changed; every match requires review.')
if __name__=='__main__':main()
