import hashlib,subprocess,unittest
from pathlib import Path
import probe_source_archive as P
import probe_script_archive as S
class SolidShellTests(unittest.TestCase):
 def test_members_and_wrappers(self):
  self.assertEqual(len(P.records()),73)
  for r in P.records():
   self.assertEqual(P.sha(S.read(r['script'])),r['script_converted_sha256'])
   p=P.ROOT/r['script'];self.assertEqual(p.read_bytes(),S.wrapper(r['script']));subprocess.run(['bash','-n',str(p)],check=True)
 def test_unknown_member_refused(self):
  with self.assertRaises(ValueError):S.read('../escape')
 def test_no_eval_after_loader_failure(self):
  import os,tempfile
  with tempfile.TemporaryDirectory() as tmp:
   base=Path(tmp);(base/'r2_wikipedia').mkdir();(base/'bin').mkdir();fake=base/'bin/python3';fake.write_text('#!/bin/sh\nexit 7\n');fake.chmod(0o755)
   w=base/'r2_wikipedia/probe.sh';w.write_bytes(S.wrapper('x'));env=os.environ.copy();env['PATH']=str(base/'bin')+':'+env['PATH']
   r=subprocess.run(['bash',str(w)],env=env,capture_output=True);self.assertEqual(r.returncode,7)
if __name__=='__main__':unittest.main()
