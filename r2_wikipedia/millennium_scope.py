"""Reachability and fair scheduling for the 3rd millennium BCE focus.

Uses only recorded links from the current revision of each locally collected page.
A link path does not prove a page is about the millennium. Period titles outside
3000–2001 BCE are kept as deferred context rather than followed in this focus;
non-period links remain eligible. Reachability grows as pages are collected and
is not completeness. Redlinks are preserved in the crawl graph but not queued.
"""
from collections import deque,Counter
import re
from periods import classify

ROOT='3rd millennium BC'
LOW,HIGH=-3000,-2001


def in_focus(title):
    p=classify(title)
    if p:return p.start<=HIGH and p.end>=LOW
    # classify() intentionally rejects dates outside the overall 3000 BCE–3000 CE
    # range. Defer those apparent period titles too, rather than calling them
    # ordinary subjects; their identity still requires actual page review.
    s=title.strip()
    out_of_range_period=(r'(?:AD )?[1-9]\d{0,5}(?: BC| BCE| CE| AD| \(year\))?'
                         r'|(?:0|[1-9]\d*)s(?: BC)?(?: \(decade\))?'
                         r'|[1-9]\d*(?:st|nd|rd|th) (?:century|millennium)(?: BC)?')
    return not bool(re.fullmatch(out_of_range_period,s,re.I))


def graph(db):
    pages={t:(pid,rev) for pid,t,rev in db.execute('select pageid,title,revid from pages')}
    aliases={t:canonical for t,canonical in db.execute('select requested_title,canonical_title from resolutions')}
    bysource={}
    for pid,rev,target in db.execute('select source_pageid,source_revid,target_title from edges'):
        bysource.setdefault((pid,rev),[]).append(target)
    if ROOT not in pages:raise ValueError('Scoped root page has not been collected')
    depths={ROOT:0};visited=set();deferred=set();q=deque([ROOT])
    while q:
        title=q.popleft()
        if not in_focus(title):deferred.add(title);continue
        canonical=aliases.get(title,title)
        if not in_focus(canonical):deferred.add(title);continue
        if canonical not in pages or canonical in visited:continue
        visited.add(canonical)
        for target in bysource.get(pages[canonical],()):
            if target not in depths:
                depths[target]=depths[title]+1;q.append(target)
    return {'depths':depths,'visited_canonical':visited,'deferred_period_titles':deferred}


def century_band(p):
    # 0 = 30th century BCE, 9 = 21st century BCE; only focused periods.
    return min(9,max(0,(p.start+3000)//100))


def choose(db,attempt):
    g=graph(db);depths=g['depths'];states=[]
    for title,status in db.execute('select title,status from frontier'):
        if title not in depths or not in_focus(title):continue
        p=classify(title)
        states.append((title,status,p,depths[title]))
    pending=[x for x in states if x[1]=='pending']
    if not pending:return None
    # Confirm the 10 century titles before prioritizing finer units.
    centuries=[x for x in pending if x[2] and x[2].kind in ('millennium','century')]
    if centuries:
        return min(centuries,key=lambda x:(x[3],x[0]))[0::3] # title, scoped depth
    others=[x for x in pending if x[2] is None]
    years=[x for x in pending if x[2] and x[2].kind=='year']
    decades=[x for x in pending if x[2] and x[2].kind=='decade']
    # The ordinary and year slots are offset, preserving both kinds of traversal.
    chosen=years if attempt%10==1 and years else others if (attempt+1)%5==0 and others else decades or years or others
    if chosen is others:
        x=min(chosen,key=lambda x:(x[3],x[0]))
    else:
        checks=Counter(century_band(p) for _,status,p,_ in states if p and p.kind==chosen[0][2].kind and status in ('done','missing'))
        x=min(chosen,key=lambda x:(checks[century_band(x[2])],x[3],x[2].start,x[0]))
    return x[0],x[3]


def summary(db):
    g=graph(db);states={t:s for t,s in db.execute('select title,status from frontier')}
    counts=Counter()
    for title,depth in g['depths'].items():
        if not in_focus(title):continue
        p=classify(title);k=p.kind if p else 'other'
        counts[k+'_discovered']+=1
        if states.get(title) in ('done','missing'):counts[k+'_checked']+=1
    canonical=g['visited_canonical']
    counts['distinct_canonical_pages_read']=len(canonical)
    counts['century_pages_read']=sum(1 for t in canonical if (p:=classify(t)) and p.kind=='century')
    counts['year_canonical_pages']=sum(1 for t in canonical if (p:=classify(t)) and p.kind=='year')
    counts['deferred_out_of_scope_period_titles']=len(g['deferred_period_titles'])
    counts['years_certified_complete']=0
    return {'root':ROOT,'range':{'start':LOW,'end':HIGH,'convention':'negative BCE; no year zero'},
      'counts':dict(counts),'warning':'Graph reachability does not prove article relevance or completeness. Year-title checks include redirects. Canonical year titles are not yet validated year articles. Deferred period titles are not discarded.'}
