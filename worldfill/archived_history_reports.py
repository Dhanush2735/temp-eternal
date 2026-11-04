"""Read/restore archived generated history reports, with hash and space guards."""
import hashlib,lzma,os,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'r2_wikipedia'))
from storage_guard import within_budget
SPECS={
 'PRODUCT_JOURNEYS.original.md':('c881af68ec4e73b4cd6cf69987401d097f5d80e4c383d80d507663fab94a9bc8','e9f9ee619aedc75f4c3938435c11ae391987f21b7bf1136592b4fda5286e24bc'),
 'WEAPONS_RESEARCH.original.md':('156fc0add40efa94ff77f95a06b02390b51b00046106e06df6947daf740f0e29','ecc28843c3e0460ce4ee2eb9ec3c61101255628e89f252413c134126ee3e8db6'),
 'TEST_CHECKLIST.original.md':('b28d74214fc33095c695d27e88be87f09392e9473cf6c64510b2e444b18d40d9','4dca22a62440ba964b4f25b53fa3884c8f1e894a55a1d1bdc5fc7842ef9bda56'),
 'npc_talk_ui_preview.html':('933742f440f4a8d7709821863d24666db68970c5811d64fc0fcc37447e7ed6d5','16761a19203aa7159f50bdcb4247ddd12383723561b03d664f0166336909e71c'),
 'npc_knowledge_ui_preview.html':('0bb3cfa79c8a2f8934724702758fd02cad670256d31cf79b70119ef9248053ff','bc7bcfaf6fda5510a3c35c66d0a9540ca468ae11adba7dfc395b5da75cf87f38'),
 'money_coverage_report.json':('5fb3a861bfbdc7c2b530f11e9db545a2ef0e13698ce7233c690e276d8459672f','a5f2adb0352a3fccca3911b87595c2beee66e5ddf4953f045dcf0ad7c4ebcc10'),
 'hazards_report.json':('ab74e079e4448a48b12b5d7dce8c9161d1c9b36b6f6a12cedf85e05ed012a67b','b62f78f72f86186d0f64bb5e28e4e6c78600402af0e68c0192f41d6931627048'),
 'README.original.md':('b9134188f764ec6c37f4641f0edcec88f82dcb4feaaea29d2d4f85622dc26249','f6bb471f650551207aaf8ac45bc10a085a41ab7b93c42211e4cf66af6330ef3f'),
 'fact_audit_summary.json':('5edc30cbd858a7fc9dd96e56082882bbf179d2287b96b19287227beedffe86cf','9708873f1af9c932f78a202800cacd331743f3cc44b9c1aae5d4ab893bcc2505'),
 'PRODUCT_ATLAS_TABLE.md':('ec30ddca925ed93bb3873a1e25ac6b9a573730757e7d10179d8ce0507f9e756b','9646266f17ec7f1c3892a19447cc9dd5e31b3e1b556b61878d5f99af923e8412'),
 'build_places_report.json':('04994323e7f7ffb02ad1c5547a180c3328663249df4e55c12d3934953883c16a','4a93988df7db890c459415b51ec12979081fedc0092853b912da19ee6bac719f'),
 'data_use_probe.json':('2c53300138e627b57417f70a6fb7dc7ba856be73821e2fc089e27d9dbc9514b6','e46c7dd7a58d55fc74d3bf3404b8a343a069c8788bb73a989f6941602a8d66ba'),
 'sample_ee_check_all_log.txt': ('8b5aa828feeb63dfdba8a827e8f778738d30c3e3014a0c3baa7857bfc2ce261a','50139e2ecb3ca5c4abede67aaddeeafb77e416698e3cd8aacedd5b28e0cea482'),
 'sample_ee_check_all_player_log.txt': ('85de54a50eeb7e371108aa6278f796ef8c58ddc9aae9fd35da273899de6b63af','88f227da48789bcd00d97b52b8058a9b1e6a5d4246e7988f4e3b32fb77d0121b'),
 'fact_audit_findings.csv':('64a9313de0309e9f01b129a54bde46fe1ae0f9f3759747b822272c99b28677fc','d182a644b461582c3af95736faf47a8c5e773aa993956258d9c4b21f3fbbd403'),
 'regional_report.json':('11b8cb67aa52212ee9a64a5a2e9abe67b356eedd4a0e04570369870acc1514f0','817bd9fcb142bd33757812e8304f304843bd49d6a71bac159014cdfeb71b6ac7')}
def sha(b):return hashlib.sha256(b).hexdigest()
def read(name):
 rh,xh=SPECS[name];b=(ROOT/(name+'.xz')).read_bytes()
 if sha(b)!=xh:raise ValueError('Archive checksum mismatch')
 raw=lzma.decompress(b)
 if sha(raw)!=rh:raise ValueError('Raw checksum mismatch')
 return raw
def restore(name):
 p=ROOT/name
 if p.exists():raise FileExistsError(p)
 raw=read(name)
 if within_budget(125)[1]+len(raw)>=125000000:raise RuntimeError('125 MB guard blocks restoration')
 d=ROOT.parent/'.cache/r2-atomic-pack-stage';d.mkdir(parents=True,exist_ok=True)
 if os.stat(d).st_dev!=os.stat(ROOT).st_dev:raise RuntimeError('Different staging filesystem')
 fd,tmp=tempfile.mkstemp(dir=d,prefix='report-restore-')
 try:
  with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
  os.link(tmp,p)
 finally:os.unlink(tmp)
 return p
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('name',choices=SPECS);ap.add_argument('--restore',action='store_true');ap.add_argument('--print',action='store_true',dest='print_data');a=ap.parse_args()
 if a.restore and a.print_data:ap.error('choose one action')
 if a.restore:print('Restored',restore(a.name))
 elif a.print_data:sys.stdout.buffer.write(read(a.name))
 else:print('Verified bytes:',len(read(a.name)))
