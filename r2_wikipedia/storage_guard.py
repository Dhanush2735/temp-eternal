"""Approximate persisted workspace size and stop collection before it grows too large.

The snapshot cap is best-effort, not a quota that can be enforced from here.
Transient SQLite journals and files created after a scan can still cause overshoot.
The reserve must also leave room for exports and reports.
"""
import os
from pathlib import Path

ROOT=Path('/home/user')
# User-approved Hyderabad pilot budget. Existing R2 tools retain their own 125 MB
# limits. 130 MB leaves roughly 4.2 million bytes below 128 MiB for snapshots.
HYDERABAD_PILOT_LIMIT_BYTES=130_000_000
EXCLUDED_DIRS={'.arena','.cache','.local','.mypy_cache','.next','.nox','.npm','.nuxt',
 '.output','.parcel-cache','.playwright-cli','.pytest_cache','.ruff_cache','.svelte-kit',
 '.tox','.turbo','.venv','.vite','__pycache__','build','coverage','dist','node_modules','out','target'}
EXCLUDED_FILES={'.git-credentials','.netrc'}

def workspace_bytes(root=ROOT):
 total=0
 for current,dirs,files in os.walk(root,followlinks=False):
  dirs[:]=[d for d in dirs if d not in EXCLUDED_DIRS and not os.path.islink(os.path.join(current,d))]
  for f in files:
   if f in EXCLUDED_FILES or (os.path.basename(current)=='.git' and f in {'config','credentials'}):continue
   p=os.path.join(current,f)
   if os.path.islink(p):continue
   try:total+=os.path.getsize(p)
   except FileNotFoundError:pass # A transient file may disappear during the walk.
 return total

def within_budget(max_mb,root=ROOT):
 used=workspace_bytes(root)
 return used < max_mb*1_000_000,used
