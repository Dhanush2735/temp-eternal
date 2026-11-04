import com.eternalengine.civilization.*;
/** Actual Gazetteer, CivHints and CivSynthesis; all other dependencies are minimal stubs. */
public class EarlySiteProbe {
 static void check(boolean ok,String msg){if(!ok)throw new AssertionError(msg);}
 static HistoryGazetteer.Site site(HistoryGazetteer g,String id,int start,int end){
  var rows=g.allSites().stream().filter(s->s.id().equals(id)).toList();check(rows.size()==1,"missing/shared "+id);
  var s=rows.get(0);check(s.civHint().isEmpty(),"false hint retained "+id);
  check(s.occupiedStart()==start&&s.occupiedEnd()==end,"bad span "+id);
  check(CivHints.resolve(s.civHint(),RulerRegister.get()).isEmpty(),"blank hint resolves to a polity "+id);
  return s;
 }
 static void nearest(HistoryGazetteer g,HistoryGazetteer.Site s,int y){
  var hit=g.nearestOccupied(s.lat(),s.lon(),y);check(hit.isPresent()&&hit.get().site().id().equals(s.id()),"site not selected in "+y+" for "+s.id());
  check(hit.get().site().civHint().isBlank(),"selected site has a civ assertion");
 }
 public static void main(String[] args){
  var g=HistoryGazetteer.get();var sh=site(g,"pl_377547413",-3550,-1799);var ca=site(g,"caral",-2600,-2000);var kn=site(g,"pl_229296321",-5000,-3299);
  nearest(g,sh,-3000);nearest(g,ca,-2500);nearest(g,kn,-3500);
  check(!sh.occupiedIn(-3551)&&sh.occupiedIn(-3550)&&sh.occupiedIn(-1800)&&!sh.occupiedIn(-1799),"site end/start boundary error");
  var m=new CivilizationManager();var result=CivSynthesis.reconcile(m,null);
  check(m.getCivilization("").isEmpty(),"blank civ synthesized");
  check(result.synthesisedIds().stream().noneMatch(String::isBlank),"blank civ id cited");
  System.out.println("PASS: 3 site rows and nearest-site index; real CivHints ignores blank and real CivSynthesis does not synthesize a blank civ (other dependencies stubbed)");
 }
}
