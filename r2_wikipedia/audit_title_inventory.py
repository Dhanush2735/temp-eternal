#!/usr/bin/env python3
"""Inventory year-title resolution only. A title check is NOT collection/completion."""
import glob,json,re
import title_archive
from pathlib import Path
F=Path(__file__).resolve().parent/'focus'
bce,ce=set(),set();ignored=0
for p in title_archive.paths():
 d=title_archive.load(p)
 for r in d.get('results',[]):
  if r.get('status')!='resolved':continue
  t=r.get('requested_title','');m=re.fullmatch(r'(\d+) BC',t)
  if m:bce.add(int(m.group(1)));continue
  if p.name.endswith('_CE.json') or 'CE_chronological' in p.name:
   m=re.fullmatch(r'(\d+) \(year\)',t)
   if m:ce.add(int(m.group(1)));continue
  ignored+=1
print('Distinct resolved BCE year titles:',len(bce))
print('Missing from title files in 3000–1 BCE:',', '.join(map(str,sorted(set(range(1,3001))-bce))) or 'none')
print('Distinct resolved chronological CE year titles:',len(ce))
print('Missing from title files in 1–211 CE:',', '.join(map(str,sorted(set(range(1,212))-ce))) or 'none')
print('Unique resolved titles in these two sets:',len(bce)+len(ce))
print('Ignored exploratory or unrecognized resolved title entries:',ignored)
print('This counts titles, not examined year sections, linked articles, historical accuracy, partial years or completion; other evidence may exist outside these files.')
