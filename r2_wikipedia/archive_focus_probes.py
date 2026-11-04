"""Convert Focus probes to verified xz one at a time and adapt their test scripts.

The original byte hashes and exact original/modified script hashes are journaled
before a source is removed. Originals remain authoritative when present. No
active game source is modified. Run with all test writers stopped.
"""
import hashlib,json,lzma,os,re,subprocess,tempfile
from pathlib import Path
import probe_source_archive as A
from storage_guard import within_budget
LIMIT=125_000_000
sha=lambda b:hashlib.sha256(b).hexdigest()
def converted_script(text,name):
 candidates=['"$ROOT/r2_wikipedia/java_probe/'+name+'"','"$ROOT"/r2_wikipedia/java_probe/'+name]
 matches=[x for x in candidates if text.count(x)==1]
 if len(matches)!=1:raise ValueError('Expected exactly one source reference')
 new='"$(python3 "$ROOT/r2_wikipedia/probe_source_archive.py" extract '+name+' "$TMP")"'
 return text.replace(matches[0],new)
def restore_script(name):
 r=A.record(name);p=A.ROOT/r['script'];current=p.read_bytes()
 if sha(current)==r['script_original_sha256']:return p
 if not (A.PROBES/name).exists():raise RuntimeError('Restore the probe source before restoring its original script')
 if sha(current)!=r['script_converted_sha256']:
  import probe_script_archive as S
  if current!=S.wrapper(p.name):raise ValueError('Test script changed since conversion')
  current=S.read(p.name)
 old=r.get('original_source_expression','"$ROOT/r2_wikipedia/java_probe/'+name+'"');new='"$(python3 "$ROOT/r2_wikipedia/probe_source_archive.py" extract '+name+' "$TMP")"'
 result=current.decode().replace(new,old)
 if sha(result.encode())!=r['script_original_sha256']:raise ValueError('Original script hash mismatch')
 atomic_script(p,result.encode());return p
def atomic_script(path,data):
 cache=Path('/home/user/.cache/r2-atomic-probe-stage');cache.mkdir(parents=True,exist_ok=True)
 if os.stat(cache).st_dev!=os.stat(path.parent).st_dev:raise RuntimeError('Different filesystems')
 fd,tmp=tempfile.mkstemp(dir=cache)
 try:
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.chmod(tmp,path.stat().st_mode & 0o777);subprocess.run(['bash','-n',tmp],check=True)
  used=within_budget(125)[1]
  if used-path.stat().st_size+len(data)>=LIMIT:raise RuntimeError('Guard blocks script replacement')
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def convert_one(src,script):
 name=src.name;raw=src.read_bytes();z=lzma.compress(raw,preset=9);old=script.read_bytes();new=converted_script(old.decode(),name).encode()
 if lzma.decompress(z)!=raw:raise ValueError('Round trip failed')
 orig='"$ROOT/r2_wikipedia/java_probe/'+name+'"' if ('"$ROOT/r2_wikipedia/java_probe/'+name+'"') in old.decode() else '"$ROOT"/r2_wikipedia/java_probe/'+name
 rec={'name':name,'raw_bytes':len(raw),'raw_sha256':sha(raw),'xz_sha256':sha(z),'script':script.name,'script_original_sha256':sha(old),'script_converted_sha256':sha(new),'original_source_expression':orig};line=(json.dumps(rec,separators=(',',':'))+'\n').encode();dest=src.with_name(name+'.xz')
 if dest.exists() or (A.MAP.exists() and any(x['name']==name for x in A.records())):raise FileExistsError(name)
 if within_budget(125)[1]+len(z)+len(line)+1024>=LIMIT:raise RuntimeError('Guard blocks group')
 with dest.open('xb') as f:f.write(z);f.flush();os.fsync(f.fileno())
 if dest.read_bytes()!=z or lzma.decompress(dest.read_bytes())!=raw:raise ValueError('Archive verification failed')
 with A.MAP.open('ab') as f:f.write(line);f.flush();os.fsync(f.fileno())
 atomic_script(script,new)
 if sha(src.read_bytes())!=rec['raw_sha256']:raise ValueError('Source changed; kept original')
 src.unlink()
 return len(raw)-len(z)-len(line)-(len(new)-len(old))
def main():
 if not A.MAP.exists() and Path(str(A.MAP)+'.gz').exists():raise RuntimeError('Restore the complete journal before any new conversion')
 files=sorted(A.PROBES.glob('Focus*Probe.java'));scripts=list(A.ROOT.glob('*.sh'));refs={}
 for script in scripts:
  for name in re.findall(r'java_probe/(Focus[^/"\s]+\.java)',script.read_text()):refs.setdefault(name,[]).append(script)
 if any(len(refs.get(p.name,[]))!=1 for p in files):raise ValueError('Each probe must have exactly one test script')
 total=0
 for p in files:total+=convert_one(p,refs[p.name][0])
 print('converted',len(files),'probes; net byte saving before utility overhead',total)
if __name__=='__main__':main()
