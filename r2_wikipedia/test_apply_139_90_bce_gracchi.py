import unittest
import apply_139_90_bce_gracchi as m

class GracchiReview(unittest.TestCase):
 def setUp(self):
  self.manifest=m.load(m.M);m.validate(self.manifest);self.u=self.manifest['updates'][0]
 def test_office_not_election(self):
  a=self.u['after'];self.assertEqual((a['start'],a['end'],a['effect']),(-123,-121,'note'));self.assertIn('does not establish the election date',a['r2SourceEvidence']['review_note'])
 def test_current_and_round_trip(self):
  d=m.load(m.H/self.u['pack']);matches=[e for e in d['events'] if e.get('id')==self.u['event_id']];self.assertEqual(matches,[self.u['after']]);before=m.transform(d,self.manifest['updates'],True);self.assertEqual(m.transform(before,self.manifest['updates']),d)
 def test_guard(self):
  d=m.load(m.H/self.u['pack']);self.assertRaises(ValueError,m.transform,d,self.manifest['updates'])

if __name__=='__main__':unittest.main()
