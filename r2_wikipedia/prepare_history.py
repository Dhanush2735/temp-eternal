#!/usr/bin/env python3
"""Turn source-list bullets into attributable R2 staging records, not game facts.

The extractor recognizes only simple, unambiguous leading year labels. Other dates,
ranges and article-page contexts remain evidence, not inferred exact event years.
No coordinates, verified identities, historical completeness or NPC actions are guessed.
"""
import argparse,collections,datetime,gzip,json,re,sys
from staged_exports import open_text as open_staged_text
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'worldfill'))
from wikitext_clean import clean_text

# Only simple leading year labels followed by a colon or spaced dash. No piped
# links, inline years or comma/month labels. A numeric value after a dash is
# rejected below as a potential range. Labels are unverified context only.
PREFIX=re.compile(r'^\s*(?P<approx>(?:c\.|ca\.|circa)\s*)?'
 r'(?P<link>\[\[)?(?:(?P<prefix_era>AD|CE)\s+)?(?P<year>\d{1,4})'
 r'(?:\s*(?P<era>BCE|BC|AD|CE))?(?(link)\]\])'
 r'(?P<separator>\s*:|\s+(?:–|—|-|&ndash;|&mdash;)\s+)\s*',re.I)


def explicit_label(text):
 m=PREFIX.match(text or '')
 if not m:return None
 n=int(m.group('year'));era=(m.group('era') or '').upper()
 if n==0 or (m.group('prefix_era') and era in ('BC','BCE')):return None
 # A dash followed by a number or numeric wikilink could denote a range.
 if ':' not in m.group('separator') and re.match(r'(?:\[\[)?\s*(?:(?:c\.|ca\.|circa)\s*)?(?:(?:AD|CE)\s+)?\d',text[m.end():],re.I):return None
 y=-n if era in ('BC','BCE') else n
 return {'year':y,'precision':'year','approximate':bool(m.group('approx')),
         'raw_label':m.group(0).strip(),'meaning':'unverified_label_at_start_of_source_bullet'}


def section_kind(path):
 top=(path[0] if path else '').strip().lower()
 if re.match(r'^births?\b',top):return 'births_section'
 if re.match(r'^deaths?\b',top):return 'deaths_section'
 if re.search(r'people|individual|monarch|ruler',top):return 'people_section'
 if re.search(r'events|wars|disaster|civil unrest|discovery|discoveries|invention|chronology|timeline',top):return 'event_or_development_section'
 if re.search(r'reference|further reading|bibliograph|external links|see also|notes',top):return 'reference_or_navigation_section'
 return 'other_or_lead_section'


def temporal_context(period,explicit,as_of):
 # This is the time context of the source page/label, NOT a proven occurrence date.
 if explicit:lo=hi=explicit['year'];basis='leading_year_label'
 else:lo=period['start'];hi=period['end'];basis='period_page_context'
 if hi<as_of.year:classification='before_present_year_context'
 elif lo>as_of.year:classification='future_year_context'
 else:classification='includes_present_year_context'
 return {'classification':classification,'basis':basis,'start_year':lo,'end_year':hi,'as_of':as_of.isoformat(),
         'warning':'Context only: does not establish when an event occurred or whether a future claim is a projection.'}


def build(row,as_of):
 raw=row['raw_wikitext'];year=explicit_label(raw)
 return {'schema':'eternal-r2-history-candidate-v1','id':row['id'],
   'status':'unreviewed_not_game_ready','source':row['source'],
   'section_path':row['section_path'],'section_kind':section_kind(row['section_path']),
   'period_context':row['period_context'],'temporal_context':temporal_context(row['period_context'],year,as_of),
   'explicit_leading_year':year,'parent_bullets':row['parent_bullets'],
   'raw_wikitext':raw,'display_text_unverified':re.sub(r'\s+',' ',clean_text(raw)).strip(),
   'linked_articles':row['links'],
   'resolved_location':None,'event_date_verified':False,
   'note':'Source-derived candidate only; link names, section labels and page context are not proof of identity, date or location.'}


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',default='r2_wikipedia/candidates.jsonl.gz');p.add_argument('--output',default='r2_wikipedia/history_candidates.jsonl.gz');p.add_argument('--future-output',default='r2_wikipedia/history_future_context.jsonl.gz');p.add_argument('--as-of',default=datetime.date.today().isoformat(),help='Reproducible classification cutoff, YYYY-MM-DD');args=p.parse_args()
 if Path(args.output).resolve()==Path(args.future_output).resolve():p.error('main and future outputs must differ')
 asof=datetime.date.fromisoformat(args.as_of);categories=collections.Counter();temporal=collections.Counter();dated=n=0
 with open_staged_text(args.input) as src,open(args.output,'wb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as out,open(args.future_output,'wb') as future_raw,gzip.GzipFile(filename='',fileobj=future_raw,mode='wb',mtime=0) as future:
  for line in src:
   r=build(json.loads(line),asof);categories[r['section_kind']]+=1;temporal[r['temporal_context']['classification']]+=1;dated+=bool(r['explicit_leading_year']);n+=1
   data=(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n').encode();out.write(data)
   if r['temporal_context']['classification']=='future_year_context':future.write(data)
 print('Staged',n,'unverified source entries;',dated,'have a simple leading year label.')
 print('section kinds:',dict(categories));print('time contexts:',dict(temporal));print('No entries have been geocoded, verified or installed.')
if __name__=='__main__':main()
