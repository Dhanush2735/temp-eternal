import hashlib,json,subprocess,tempfile,unittest
from pathlib import Path
import probe_source_archive as A
class ProbeArchiveTests(unittest.TestCase):
 def test_all_sources_and_scripts_exact(self):
  rows=A.records();self.assertEqual(len(rows),73);self.assertEqual(len({r['name'] for r in rows}),73)
  for r in rows:
   raw=A.read(r['name']);self.assertEqual(A.sha(raw),r['raw_sha256']);p=A.ROOT/r['script'];current=p.read_bytes()
   if A.sha(current)!=r['script_converted_sha256']:
    import probe_script_archive as S
    self.assertEqual(current,S.wrapper(r['script']));cur=S.read(r['script'])
   else:cur=current
   self.assertEqual(A.sha(cur),r['script_converted_sha256'])
   old=r.get('original_source_expression','"$ROOT/r2_wikipedia/java_probe/'+r['name']+'"');new='"$(python3 "$ROOT/r2_wikipedia/probe_source_archive.py" extract '+r['name']+' "$TMP")"';self.assertEqual(cur.decode().count(new),1);self.assertEqual(A.sha(cur.decode().replace(new,old).encode()),r['script_original_sha256']);subprocess.run(['bash','-n',str(p)],check=True)
 def test_extract_and_no_overwrite(self):
  r=A.records()[0]
  with tempfile.TemporaryDirectory() as tmp:
   dest=Path(tmp)/r['name'];subprocess.run(['python3',str(A.ROOT/'probe_source_archive.py'),'extract',r['name'],tmp],check=True,capture_output=True);self.assertEqual(A.sha(dest.read_bytes()),r['raw_sha256'])
   with self.assertRaises(FileExistsError):A.write(r['name'],dest)
  with self.assertRaises(ValueError):A.read('../bad')
if __name__=='__main__':unittest.main()
