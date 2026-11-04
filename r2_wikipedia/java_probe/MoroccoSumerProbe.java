import com.eternalengine.civilization.*;
import com.eternalengine.knowledge.NewsIndex;
/** Real full-index Gazetteer/NewsIndex/CivHints; some dependencies stubbed. */
public class MoroccoSumerProbe {
 static void check(boolean b,String m){if(!b)throw new AssertionError(m);}
 static HistoryGazetteer.Event event(HistoryGazetteer g,String id,boolean regional){
  var rows=g.allEvents().stream().filter(e->e.id().equals(id)).toList();check(rows.size()==1,"missing/shared event "+id);var e=rows.get(0);
  check(e.start()==-3000&&e.end()==-2999,"bad event dates "+id);check(e.kind().equals("cultural")&&e.effect().equals("note"),"bad kind "+id);
  check(HistoryGazetteer.isRegional(e)==regional,"bad regional flag "+id);
  check(g.eventsNear(e.lat(),e.lon(),-3000,.01).stream().anyMatch(h->h.event().id().equals(id)),"missing event index "+id);
  check(NewsIndex.all().stream().filter(n->n.name().equals(e.name())&&n.start()==-3000&&n.end()==-3000).count()==1,"missing NewsIndex "+id);
  if(regional)check(g.nearestLocalEvent(e.lat(),e.lon(),-3000).stream().noneMatch(h->h.event().id().equals(id)),"regional event treated as local");
  return e;
 }
 public static void main(String[] args){
  var g=HistoryGazetteer.get();var oued=event(g,"r2_oued_beht_farming_c3000",false);var sumer=event(g,"wpy_2e31a84306",true);
  check(oued.name().contains("Oued Beht")&&sumer.name().contains("Uruk"),"wrong names");
  var rows=g.allSites().stream().filter(s->s.id().equals("pl_594703044")).toList();check(rows.size()==1,"missing/shared site");var site=rows.get(0);
  check(site.civHint().isEmpty()&&CivHints.resolve(site.civHint(),RulerRegister.get()).isEmpty(),"site has false civ hint");
  check(site.occupiedStart()==-4000&&site.occupiedEnd()==641,"unexpected site dates");
  check(g.nearestOccupied(site.lat(),site.lon(),-3000).map(h->h.site().id().equals(site.id())).orElse(false),"site not selected");
  System.out.println("PASS: Oued Beht site and event, Sumer regional event, Gazetteer/NewsIndex/CivHints (headless; other dependencies stubbed)");
 }
}
