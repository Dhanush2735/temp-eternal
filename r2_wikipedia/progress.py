#!/usr/bin/env python3
"""Generate honest stage-specific progress from the actual local databases.

No overall completion percentage is computed: the total reachable Wikipedia graph,
quality checks, game integration and future projections are not yet quantified.
"""
import argparse,datetime,gzip,json,sqlite3
from pathlib import Path
from storage_guard import workspace_bytes
from staged_exports import open_text as open_staged_text, source as staged_source
from periods import classify
import millennium_scope
from apply_reviewed_events import corrected as corrected_event
from extract_candidates import harvester

ROOT=Path(__file__).resolve().parent


def ordinal(n):
    suffix='th' if 10<=n%100<=20 else {1:'st',2:'nd',3:'rd'}.get(n%10,'th')
    return f'{n}{suffix}'


def period_progress(db,kind,count):
    titles=[f'{ordinal(n)} {kind}{suffix}' for n in range(1,count+1) for suffix in (' BC','')]
    states=dict(db.execute('select title,status from frontier'))
    # A title marked done may redirect to a broader period, so count only a canonical
    # page with exactly the expected title. Never credit a redirect as its own page.
    actual={r[0] for r in db.execute('select title from pages')}
    loaded=sum(t in actual for t in titles)
    checked=sum(t in actual or states.get(t)=='done' for t in titles)
    return {'loaded':loaded,'checked':checked,'expected':len(titles),
            'percent':round(100*loaded/len(titles),2),'checked_percent':round(100*checked/len(titles),2),
            'not_read':[{'title':t,'state':('redirect_or_alias' if states.get(t)=='done' else states.get(t,'not_discovered'))} for t in titles if t not in actual]}


def percent(n,d):return round(100*n/d,2) if d else None

def format_percent(value):return 'n/a' if value is None else f'{value:.2f}%'

def discovered_period_progress(db,kind):
    """Checked title candidates among discovered titles, not article coverage."""
    states=[status for title,status in db.execute('select title,status from frontier')
            if (p:=classify(title)) is not None and p.kind==kind]
    checked=sum(s in ('done','missing') for s in states)
    return {'checked':checked,'currently_discovered':len(states),'percent_of_discovered':percent(checked,len(states))}

def recognized_year_pages(db, allowed_titles=None):
    """Count distinct canonical years whose collected pages pass the year-page checks.

    This identifies article type only. It does not verify the events on the page,
    establish exhaustive coverage of a year, or credit a redirect as a year page.
    """
    years=set()
    for title,body in db.execute('select title,wikitext_gzip from pages'):
        if allowed_titles is not None and title not in allowed_titles:continue
        p=classify(title)
        if p is None or p.kind!='year':continue
        raw=gzip.decompress(body).decode('utf8')
        if harvester.page_type(title,raw)=='year' and harvester.nav_year(raw)==p.start:
            years.add(p.start)
    return sorted(years)


def read_jsonl(path):
    if not staged_source(path).exists():return []
    with open_staged_text(path) as f:return [json.loads(x) for x in f]


def report():
    crawl=sqlite3.connect(f'file:{ROOT / "crawl.sqlite3"}?mode=ro',uri=True)
    people=sqlite3.connect(f'file:{ROOT / "people.sqlite3"}?mode=ro',uri=True)
    statuses=dict(people.execute('select status,count(*) from subjects group by status'))
    # Errors and pending are not counted as checked; unconfirmed means checked but uncertain.
    checked=sum(statuses.get(s,0) for s in ('human','unconfirmed','unresolved','missing'))
    total=sum(statuses.values())
    biographies=people.execute('select count(*) from biographies').fetchone()[0]
    staged=read_jsonl(ROOT/'vip_candidates.jsonl.gz')
    places=read_jsonl(ROOT/'place_candidates.jsonl.gz')
    bullets=read_jsonl(ROOT/'candidates.jsonl.gz')
    history=read_jsonl(ROOT/'history_candidates.jsonl.gz')
    timelines=read_jsonl(ROOT/'person_timelines.jsonl.gz')
    reconciliation=read_jsonl(ROOT/'reconciliation.jsonl.gz')
    event_summary_path=ROOT/'event_reconciliation_summary.json'
    event_summary=json.loads(event_summary_path.read_text(encoding='utf8')) if event_summary_path.exists() else {}
    future_path=ROOT/'future_game_event_audit.json'
    future_audit=json.loads(future_path.read_text(encoding='utf8')) if future_path.exists() else {}
    origin_audit_path=ROOT/'candidate_origin_audit.json'
    origin_audit=json.loads(origin_audit_path.read_text(encoding='utf8')) if origin_audit_path.exists() else {}
    archive_manifest=ROOT.parent/'worldfill/legacy_java_patches.manifest.json'
    archived=json.loads(archive_manifest.read_text(encoding='utf8')).get('files',[]) if archive_manifest.exists() else []
    installed=0;reviewed=0
    history_dir=ROOT.parent/'eternal/src/main/resources/data/eternalengine/eternal/history'
    for manifest in sorted((ROOT/'reviews').glob('event_corrections_*.json')):
        batch=json.loads(manifest.read_text(encoding='utf8'))
        updates=batch.get('updates',[]);reviewed+=len(updates)
        with gzip.open(history_dir/batch['target'],'rt',encoding='utf8') as f:rows=json.load(f)['events']
        by_id={r.get('id'):r for r in rows if isinstance(r,dict)}
        installed+=sum(by_id.get(u['event_id'])==corrected_event(u,u['candidate_snapshot']) for u in updates)
    scoped=millennium_scope.summary(crawl)
    scoped['recognized_year_pages']=recognized_year_pages(crawl,millennium_scope.graph(crawl)['visited_canonical'])
    data={'as_of_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'active_focus':scoped,
      'legacy_patches_in_archive':len(archived),
      'legacy_patches_archived_only':sum(not (ROOT.parent/'worldfill'/r['name']).exists() for r in archived),
      'estimated_persisted_workspace_bytes':workspace_bytes(),
      'default_workspace_guard_bytes':125_000_000,
      'overall_completion_percent':None,
      'overall_reason':'The total linked article graph, extraction, verification, future projection, integration and gameplay work have no established denominator.',
      'millennium_pages':period_progress(crawl,'millennium',3),
      'century_pages':period_progress(crawl,'century',30),
      'decade_title_checks':discovered_period_progress(crawl,'decade'),
      'year_title_checks':discovered_period_progress(crawl,'year'),
      'year_page_identified_years':recognized_year_pages(crawl),
      # No full-year completeness certification process exists yet; no year has
      # been certified. This count must not be used as a factual coverage metric.
      'years_certified_complete':0,
      'year_completion_note':'No year has been certified complete; no comprehensive whole-year completeness audit exists yet. Reading a year page is not completion.',
      'requested_year_slots':6000, # 3000 BCE..1 BCE and 1 CE..3000 CE; no year zero
      'people_article_checks':{'checked':checked,'currently_discovered':total,'percent_of_discovered':percent(checked,total),'statuses':statuses},
      'article_pages_read':crawl.execute('select count(*) from pages').fetchone()[0],
      'graph_edges':crawl.execute('select count(*) from edges').fetchone()[0],
      'period_bullet_candidates':len(bullets),'history_staging_records':len(history),
      'history_explicit_year_labels':sum(bool(h['explicit_leading_year']) for h in history),
      'history_future_year_context':sum(h['temporal_context']['classification']=='future_year_context' for h in history),
      'biographies_saved':biographies,'vip_candidates_staged':len(staged),
      'timeline_statements':len(timelines),'timeline_people':len({t['person_id'] for t in timelines}),
      'event_comparison':event_summary,
      'future_game_event_audit':future_audit,
      'candidate_origin_audit':origin_audit,
      'reviewed_event_batch':{'installed':installed,'reviewed':reviewed},
      'reconciled_vip_candidates':len(reconciliation),
      'possible_existing_vip_matches':sum(any(m['dataset']=='existing_vips' for m in r['matches']) for r in reconciliation),
      'possible_existing_people_matches':sum(any(m['dataset']=='famous_people_master' for m in r['matches']) for r in reconciliation),
      'potential_date_conflict_matches':sum(m['assessment']=='name_match_date_conflict' for r in reconciliation for m in r['matches']),
      'place_entities_exported':len(places),'places_checked':sum(p['status'] in ('resolved','no_coordinates') for p in places),
      'places_pending':sum(p['status']=='pending' for p in places),'places_with_coordinate_statements':sum(p['status']=='resolved' for p in places),
      'warnings':['People-check percentage uses only the currently discovered queue; the queue grows as pages are explored.',
                  'An article checked is not necessarily a person. Unconfirmed articles may still be people.',
                  'A retrieved page, biography or candidate is not a verified fact or a working NPC.']}
    return data


def future_audit_line(audit):
    if not audit or 'as_of' not in audit or 'counts' not in audit:
        return '**Game event future-year audit:** not run.'
    counts=audit['counts']
    return (f"**Game event future-year audit:** as of {audit['as_of']}, {counts.get('future_start_year',0):,} indexed rows have a start year later than that year; "
            f"{counts.get('current_start_year_day_unknown',0):,} start in the current year and require day-level review. "
            'This does not check other resources or prove that current-year events have occurred.')


def markdown(d):
    m=d['millennium_pages'];c=d['century_pages'];p=d['people_article_checks'];dec=d['decade_title_checks'];y=d['year_title_checks'];focus=d['active_focus'];fc=focus['counts']
    lines=['# Wikipedia history and VIP NPCs — progress', '',
      '**Current focus: 3rd millennium BCE (3000–2001 BCE).** The previously collected data for other eras is retained.', '',
      f"**Years certified complete in this focus: {fc['years_certified_complete']:,} out of 1,000.** No whole-year completeness audit exists yet; a year page being read is not completion.",
      f"**Recognized year pages read through this link chain: {len(focus['recognized_year_pages']):,}.** Their contents are unverified. {fc.get('year_checked',0):,} discovered year-title candidates have been checked, including redirects and missing titles.",
      f"**Focused link chain:** {fc.get('century_pages_read',0)} century pages read; {fc.get('decade_checked',0)} decade titles checked; {fc['distinct_canonical_pages_read']} distinct pages reached and read. Linked non-period articles may be from any era; out-of-focus period titles are retained as deferred context.",
      '**Overall project completion: not measurable yet.** The linked graph and work needed to verify and use it have no established total.', '',
      '| Previously collected work across all eras | Count | What it means |','|---|---:|---|',
      f"| Millennium pages read | {m['loaded']}/{m['expected']} | Only the six overview pages covering the requested range. |",
      f"| Century titles checked | {c['checked']}/{c['expected']} | {c['loaded']} distinct pages; the rest redirected. This is not content coverage. |",
      f"| Discovered decade titles checked | {dec['checked']:,}/{dec['currently_discovered']:,} | Discovered title candidates only; the queue can grow. |",
      f"| Discovered year-title candidates checked | {y['checked']:,}/{y['currently_discovered']:,} | Includes checked redirects or missing titles; not the same as year pages read. |",
      f"| Discovered titles checked for people | {p['checked']:,}/{p['currently_discovered']:,} | People queue from the last import; it can grow. |", 
      '',f"**Collected so far:** {d['article_pages_read']} crawl pages, {d['period_bullet_candidates']:,} unverified period-list entries, {d['biographies_saved']} saved biographies and {d['vip_candidates_staged']} staged VIP records.",
      f"**History review staging:** {d['history_staging_records']:,} source-linked entries prepared, including {d['history_explicit_year_labels']:,} simple leading-year labels and {d['history_future_year_context']} entries with a future-year context. Labels and contexts are not verified event dates; future context does not establish a projection.",
      future_audit_line(d.get('future_game_event_audit')),
      f"**Event comparison:** {d['event_comparison'].get('matched_candidates',0):,} candidates have exact-text matches in existing indexed event packs; {d['event_comparison'].get('assessments',{}).get('exact_text_possible_start_year_conflict',0):,} matched pairs have possible start-year conflicts. Both need review; a text match does not prove identity or an error.",
      f"**Reviewed event corrections installed:** {d['reviewed_event_batch']['installed']} from {d['reviewed_event_batch']['reviewed']} install-ready reviews. Incorrect-year rows and possible cross-pack duplicates still remain. The year-only news loader was also fixed for the three Wikipedia packs.",
      '**Timeline mitigation:** new game-source forks no longer automatically group different event IDs by proximity. Genuine multi-site siblings will not automatically suppress together. Old saved over-suppressions remain, and distinct records sharing an ID can still be suppressed together. Headless checks are not a full build or gameplay test.',
      f"**People timelines:** {d['timeline_statements']} unreviewed source statements for {d['timeline_people']} people; none is a spawn instruction.",
      f"**Retained source references:** {d.get('candidate_origin_audit',{}).get('counts',{}).get('retained_not_in_current_export_links','not audited')} people-origin links point to candidate IDs not in the current staging export. Source revisions and lines are retained; see `candidate_origin_audit.json` and `PROGRESS.md` for limitations.",
      f"**Existing-data comparison:** {d['possible_existing_people_matches']} candidate names match the existing people register and {d['possible_existing_vip_matches']} match existing VIP names. {d['potential_date_conflict_matches']} potential date conflicts need review. Name matches do not prove identity.",
      f"**Places:** {d['places_checked']} referenced place entities checked, {d['places_with_coordinate_statements']} with coordinate statements; {d['places_pending']} pending.",
      f"**Storage:** approximately {d['estimated_persisted_workspace_bytes']/1_000_000:.1f} MB of persisted workspace data; the crawler, people and place collectors stop starting new work at an estimated {d['default_workspace_guard_bytes']/1_000_000:.0f} MB. The people database now also has a per-connection page cap with estimated export headroom; journals, exports and other collectors are not hard-bounded. These are precautions, not a guaranteed snapshot quota.",
      f"**Legacy patch archive:** {d['legacy_patches_in_archive']} older patches are in `worldfill/legacy_java_patches.tar.xz`; {d['legacy_patches_archived_only']} currently exist only in the archive. Restore instructions are in `README.md`. Current game sources and assets were not archived.",
      '', f"{d['reviewed_event_batch']['installed']} reviewed corrections are in game resource files, but the unreviewed history inventory and staged VIPs have not been installed. A person’s birthplace is not automatically their position throughout their life; dates and places need review. Wikipedia and Wikidata claims retain their respective sources.",
      '', 'These counts do **not** measure all history or all people. Discovered-title totals may grow as collection expands.',
      '', f"Report generated: {d['as_of_utc']}"]
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--json',default=str(ROOT/'progress.json'));ap.add_argument('--md',default=str(ROOT/'STATUS.md'));a=ap.parse_args()
    d=report();Path(a.json).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');s=markdown(d);Path(a.md).write_text(s,encoding='utf8');print(s)
