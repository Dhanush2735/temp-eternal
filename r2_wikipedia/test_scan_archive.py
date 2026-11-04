import hashlib, json, lzma, tarfile, tempfile, unittest
from pathlib import Path
import scan_archive as A
class ScanArchiveTests(unittest.TestCase):
    def test_all_raw_and_exact_original_xz(self):
        m = json.loads(A.MAP.read_text()); archive = A.FOCUS / m['archive']
        self.assertEqual(A.sha(archive.read_bytes()), m['archive_sha256'])
        with tarfile.open(archive, 'r:xz') as tf:
            self.assertEqual(set(tf.getnames()), {x['member'] for x in m['files']})
            for item in m['files']:
                raw = tf.extractfile(item['member']).read()
                self.assertEqual(A.sha(raw), item['raw_sha256'])
                self.assertEqual(A.sha(lzma.compress(raw, preset=9)), item['compressed_sha256'])
    def test_fallback_and_path_restriction(self):
        m=json.loads(A.MAP.read_text()); name=m['files'][0]['former']
        self.assertTrue(A.read(A.FOCUS/name))
        with self.assertRaises(FileNotFoundError): A.read_former(Path('/tmp')/name)
    def test_existing_takes_precedence(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.xz'; p.write_bytes(lzma.compress(b'new'))
            self.assertEqual(A.read(p), b'new')
if __name__=='__main__': unittest.main()
