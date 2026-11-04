#!/usr/bin/env python3
"""Make a small, source-preserving 3000 BCE supervision batch from pinned pages.

This is a manual selection, not an exhaustive crawler or an event installer.
Revisions and line numbers are locked: updated source pages need a new review.
Approximate labels never become exact years or game coordinates.
"""
import gzip,json
from pathlib import Path
from staged_exports import open_text as open_staged_text

SELECT={
 '30th century BC':{'revision':1371895853,
  'around_3000':[10,11,13,14,15,16,17,18,19,20,32,33,34,37],
  'range_or_century_context':[12,31,35,36],
  'before_3000_context':[9]},
 '3rd millennium BC':{'revision':1380374367,
  'around_3000':[39,46,92,93,94,145,153,177],
  'range_or_century_context':[32,35,45,84,85,87,95,144,171]}}

NOTES={
 ('30th century BC',15):{'note':'English Heritage describes an initial earthwork around 3000 BCE but describes the 56 posts as timber OR stone, not definitively wooden. The later large stone settings are dated to around 2500 BCE. Treat date as approximate and post material as uncertain.',
  'sources':['https://www.english-heritage.org.uk/visit/places/stonehenge/history-and-stories/building-stonehenge/','https://en.wikipedia.org/w/index.php?title=Stonehenge&oldid=1377824638']},
 ('30th century BC',17):{'note':'The 30th-century bullet says around 3000 BCE; another Wikipedia chronology gives Early Helladic I as 3200–2650 BCE. This is a periodization discrepancy and does not establish a beginning in 3000 BCE.',
  'sources':['https://en.wikipedia.org/w/index.php?title=Helladic_chronology&oldid=1380683880']},
 ('3rd millennium BC',92):{'note':'This source says around 3000 BCE; other accounts give unification around 3100 BCE or earlier. The process, date and attribution need further review; do not assign an exact year.',
  'sources':['https://louis.pressbooks.pub/worldciv/chapter/__unknown__/','https://www.worldhistory.org/Narmer/']},
 ('3rd millennium BC',39):{'note':'The museum publication describes the A-Group as flourishing about 3500–3100 BCE, while the source bullet says around 3000 BCE. Dates and nature of the transition require review.',
  'sources':['https://isac.uchicago.edu/sites/default/files/uploads/shared/docs/oimp24.pdf','https://en.wikipedia.org/w/index.php?title=A-Group_culture&oldid=1381672634']},
 ('3rd millennium BC',94):{'note':'Possibly overlaps the A-Group entry on line 39. The reported cause is tentative and the chronology is disputed; no merge or exact-year assignment has been made.',
  'sources':['https://isac.uchicago.edu/sites/default/files/uploads/shared/docs/oimp24.pdf']},
 ('3rd millennium BC',177):{'note':'Possibly the same source claim as 30th century BC line 37. Duplicate identity and dating need review; not merged.', 'sources':[]},
 ('30th century BC',37):{'note':'Possibly the same source claim as 3rd millennium BC line 177. Duplicate identity and dating need review; not merged.', 'sources':[]},
 ('3rd millennium BC',46):{'note':'The bullet states 3000 BCE without a circa qualifier, whereas another bullet on the same page gives a broader approximate range. The assertion and its characterization need review.', 'sources':[]}}


def create(input_path='r2_wikipedia/history_candidates.jsonl.gz'):
 wanted={(title,line):(spec['revision'],cat) for title,spec in SELECT.items() for cat,lines in spec.items() if isinstance(lines,list) for line in lines}
 rows={}
 with open_staged_text(input_path) as f:
  for l in f:
   r=json.loads(l);src=r['source'];key=(src['title'],src['line'])
   if key not in wanted:continue
   rev,cat=wanted[key]
   if src['revision_id']!=rev or key in rows:raise ValueError('Source revision changed or duplicate line: '+repr(key))
   rows[key]={'selection_category':cat,'record_status':'unreviewed_not_game_ready',
      'candidate':r,'crosscheck':NOTES.get(key),
      'warning':'Source claim only. No exact year, coordinates, individual or game effect inferred.'}
 missing=set(wanted)-set(rows)
 if missing:raise ValueError('Missing expected source lines: '+repr(sorted(missing)))
 return {'schema':'eternal-3000-bce-review-batch-v1','focus_year':{'year':-3000,'display':'3000 BCE','year_convention':'negative BCE; no year zero'},
   'status':'source_claims_for_supervision_not_game_ready','redirect':{'requested_title':'3000 BC','canonical_title':'30th century BC','canonical_revision':1371895853},
   'selection_method':'Manual source-line selection from the pinned 30th-century and millennium bullet exports; includes circa statements, explicit ranges and one before-year context. It is not an exhaustive search of linked articles or all events. Undated century and millennium material requires separate review.',
   'candidate_fields_note':'The candidate explicit_leading_year is a parsed source label, not an established exact date. Dates and precision must be checked against the raw wikitext. display_text_unverified can omit template content.',
   'warnings':['No year is certified complete. Approximate dates are not exact year events.',
     'Source bullets can contain multiple claims, duplicates, disputed chronology and outdated assertions; preserve and review rather than install.',
     'Range and before-year entries are context, not evidence that an event happened in exactly 3000 BCE.',
     'Locations remain unresolved; neither birthplace nor a modern location proves a historical event site.'],
   'records':[rows[key] for key in sorted(rows)]}

if __name__=='__main__':
 out=Path('r2_wikipedia/focus/3000_bce_review.json');out.parent.mkdir(parents=True,exist_ok=True)
 data=create();out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print('Wrote',len(data['records']),'source claims and context records to',out)
