#!/usr/bin/env python3
"""Build a small human-reviewed research index, never a gameplay pack."""
import json,lzma,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'r2_wikipedia'))
from storage_guard import workspace_bytes,HYDERABAD_PILOT_LIMIT_BYTES
paths=sorted(R.glob('wikipedia_*_2026-11.json.xz'));docs=[json.load(lzma.open(p,'rt')) for p in paths]
pages={}
for d in docs:
 for p in d['pages']:
  v=p['revisions'][0];t=v['slots']['main']['content'];assert hashlib.sha256(t.encode()).hexdigest()==p['wikitext_sha256'];pages[p['title']]={'pageid':p['pageid'],'revision':v['revid'],'url':'https://en.wikipedia.org/w/index.php?oldid='+str(v['revid'])}
assert len(pages)==43 and len(docs)==3
assert all(len(d['year_title_resolutions_3000_2951_bce'])==50 and all(r['canonical_title']=='30th century BC' and r['status']=='resolved' for r in d['year_title_resolutions_3000_2951_bce']) for d in docs)
def c(id,kind,claim,sources,qualifier):return {'id':id,'type':kind,'claim':claim,'sources':[pages[x] for x in sources],'uncertainty_or_limit':qualifier,'status':'research_candidate_not_gameplay'}
claims=[
 c('city_foundation','event','Wikipedia describes Hyderabad as founded in 1591 by Muhammad Quli Qutb Shah.',['History of Hyderabad','Muhammad Quli Qutb Shah'],'Review against other references and existing 1589/1591 records; city is distinct from earlier regional settlements.'),
 c('hasmathpet','place','Wikipedia describes Hasmathpet cairns near Secunderabad and assigns them to the second century BCE.',['Hasmathpet cairns'],'That is a broad article claim, not proof of activity in any individual year; further archaeological review needed.'),
 c('hussain_sagar','place','Wikipedia dates the construction of Hussain Sagar to 1562 and associates it with Ibrahim Quli Qutb Shah and Hussain Shah Wali.',['Hussain Sagar','Hussain Shah Wali'],'The sources credit the figures differently; check primary and independent references; lake outline and water levels at any date unknown.'),
 c('flood_1908','event','Wikipedia reports a major Musi flood in Hyderabad on 28 September 1908.',['Great Musi Flood of 1908'],'The article gives inconsistent fatality estimates, including 15,000 and 50,000; local flood extent and trigger not yet validated.'),
 c('blasts_2013','event','Wikipedia reports two blasts in Dilsukhnagar on 21 February 2013.',['2013 Hyderabad blasts','Dilsukhnagar'],'Source infobox coordinates appear near Charminar, not Dilsukhnagar; timings and injury totals also vary within article. Do not use coordinates or simulation behavior without independent review.'),
 c('founder','person','Muhammad Quli Qutb Shah is identified as Hyderabad founder.',['Muhammad Quli Qutb Shah','History of Hyderabad'],'Article has sourcing warning; no day-by-day location or behavior established.'),
 c('hayat','person','Hayat Bakshi Begum is described as a Qutb Shahi figure who acted as regent after 1626.',['Hayat Bakshi Begum'],'Article has internal disagreement about her father’s death year; verify.'),
 c('sultan_muhammad','person','Sultan Muhammad Qutb Shah ruled Golconda from 1612 to 1626 according to Wikipedia.',['Sultan Muhammad Qutb Shah'],'Article has citation warning and questionable text; succession dates require review.'),
 c('abdullah','person','Abdullah Qutb Shah is described as a Golconda ruler from 1626 to 1672.',['Abdullah Qutb Shah'],'Details of marriage alliances are internally inconsistent; check further.'),
 c('kshetrayya','person','Kshetrayya was a Telugu poet whose approximate lifespan is given as c.1600–1680.',['Kshetrayya'],'Article needs additional citations; precise dates and local presence uncertain.'),
 c('hussain','person','Hussain Shah Wali is described as a Sufi figure associated with Hussain Sagar.',['Hussain Shah Wali','Hussain Sagar'],'Biography is a stub and flags overreliance on primary sources; verify attribution and dates.'),
 c('sarojini','person','Sarojini Naidu, poet and political activist, was born in Hyderabad in 1879.',['Sarojini Naidu'],'Birthplace alone does not establish residence or behavior on every date.'),
 c('amjad','person','Amjad Hyderabadi is identified as an Urdu and Persian poet and survivor of the 1908 flood.',['Amjad Hyderabadi','Great Musi Flood of 1908'],'His biography says 1878 in infobox and 1888 in lead; flood article gives age 22; do not choose an exact birth year yet.'),
 c('makhdoom','person','Makhdoom Mohiuddin was an Urdu poet and activist associated with Hyderabad.',['Makhdoom Mohiuddin'],'Article flags insufficient citations; verify dated local activities.'),
 c('bhagmati','person','Bhagmati appears in narratives connected to Muhammad Quli Qutb Shah and Hyderabad.',['Bhagmati'],'Her historicity and the naming story are debated; do not assert existence as established or make spawnable.'),
 c('asaf_jah_vi','person','Mahboob Ali Khan, Asaf Jah VI, ruled Hyderabad State during the 1908 flood.',['Mahboob Ali Khan','Great Musi Flood of 1908'],'Distinct from unrelated Bangladeshi naval officer Mahbub Ali Khan; resolve article-internal succession inconsistencies.'),
 c('family_1','relationship','Hayat Bakshi Begum was the daughter of Muhammad Quli Qutb Shah.',['Sultan Muhammad Qutb Shah','Hayat Bakshi Begum'],'Research candidate; corroborate the biographical details.'),
 c('family_2','relationship','Sultan Muhammad Qutb Shah married Hayat Bakshi Begum in 1607, according to Wikipedia.',['Sultan Muhammad Qutb Shah'],'Article needs citations; confirm precise year.'),
 c('family_3','relationship','Abdullah Qutb Shah is described as the son of Sultan Muhammad Qutb Shah and Hayat Bakshi Begum.',['Abdullah Qutb Shah'],'Research candidate; no inferred interaction schedule.'),
 c('court_poet','relationship','Wikipedia says Abdullah Qutb Shah invited the poet Kshetrayya to his court.',['Abdullah Qutb Shah','Kshetrayya'],'Exact time and locality not stated here; independent corroboration required.'),
 c('father_daughter_naidu','relationship','Wikipedia identifies Padmaja Naidu as Sarojini Naidu’s daughter.',['Sarojini Naidu','Padmaja Naidu'],'A family link is not evidence of a specific encounter at a given time or place.'),
 c('naidu_father','relationship','Wikipedia identifies Aghorenath Chattopadhyay as Sarojini Naidu’s father.',['Sarojini Naidu','Aghorenath Chattopadhyay'],'Further biographical and temporal review required.')]
obj={'scope':'Hyderabad-area research only; not a complete history or gameplay data','articles_archived_unique':43,'excluded_unrelated_article':'Mahbub Ali Khan (Bangladeshi naval officer), distinct from Mahboob Ali Khan (Asaf Jah VI)','year_title_check':'3000–2951 BCE: 50 titles resolve to same century article; zero fully researched years','claims':claims}
raw=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode();out=R/'research_candidates.json'
if workspace_bytes()+len(raw)>=HYDERABAD_PILOT_LIMIT_BYTES:raise RuntimeError('Storage guard')
out.write_bytes(raw)
print('verified archives',len(docs),'unique source revisions',len(pages),'candidate claims',len(claims),'workspace bytes',workspace_bytes())
