import com.eternalengine.civilization.HistoryGazetteer;
import com.eternalengine.civilization.Disasters;
import com.eternalengine.civilization.R2EventChecks;
import com.eternalengine.knowledge.NewsIndex;
import com.eternalengine.testing.R2PeopleChecks;
import java.util.*;
public class R2ChecksProbe {
 static int n=0;
 static void ck(boolean ok,String m){n++;if(!ok)throw new AssertionError(m);}
 static boolean e(List<R2EventChecks.Result> r,R2EventChecks.Status s,String text){return r.stream().anyMatch(x->x.status()==s&&x.text().contains(text));}
 static boolean p(List<R2PeopleChecks.Result> r,R2PeopleChecks.Status s,String text){return r.stream().anyMatch(x->x.status()==s&&x.text().contains(text));}
 public static void main(String[] args){
  var g=HistoryGazetteer.get(); var d=Disasters.get(); var news=NewsIndex.all();
  var ok=R2EventChecks.run();
  ck(e(ok,R2EventChecks.Status.OK,"six reviewed"),"real reviewed event sample");
  ck(e(ok,R2EventChecks.Status.OK,"four uncertain"),"real hazard sample");
  ck(e(ok,R2EventChecks.Status.OK,"six events are indexed"),"real news sample");
  ck(e(ok,R2EventChecks.Status.KNOWN,"end-year conventions"),"known year-boundary defect detected");
  var rows=new ArrayList<>(g.allEvents()); rows.removeIf(x->x.id().equals("q12950513"));
  var gone=R2EventChecks.evaluate(rows,news,Set.of(),true);
  ck(e(gone,R2EventChecks.Status.FAIL,"six reviewed"),"missing event fails");
  ck(e(gone,R2EventChecks.Status.FAIL,"six events are indexed"),"missing sample is not news pass");
  var duplicates=new ArrayList<>(g.allEvents());duplicates.add(g.allEvents().stream().filter(x->x.id().equals("q619030")).findFirst().orElseThrow());
  ck(e(R2EventChecks.evaluate(duplicates,news,Set.of(),true),R2EventChecks.Status.FAIL,"six reviewed"),"duplicate sample fails");
  ck(e(R2EventChecks.evaluate(g.allEvents(),news,Set.of("hz_c82c5fc69e"),true),R2EventChecks.Status.FAIL,"four uncertain"),"hazard wrongly active fails");
  ck(e(R2EventChecks.evaluate(g.allEvents(),news,Set.of(),false),R2EventChecks.Status.FAIL,"four uncertain"),"unloaded disaster register fails");
  ck(e(R2EventChecks.evaluate(g.allEvents(),List.of(),Set.of(),true),R2EventChecks.Status.FAIL,"six events are indexed"),"missing news fails");
  var vip=new R2PeopleChecks.Vip("a","Person",-50,-10,30,40,0,false,false);
  var npc=new R2PeopleChecks.Npc("1","human","rome","citizen",List.of());
  var tagged=new R2PeopleChecks.Npc("2","human","rome","citizen",List.of("a"));
  var people=R2PeopleChecks.evaluate(List.of(npc,tagged),true,List.of(vip),true,-30);
  ck(p(people,R2PeopleChecks.Status.OK,"VIP registry"),"valid registry");
  ck(p(people,R2PeopleChecks.Status.OK,"ordinary NPCs"),"ordinary npc");
  ck(p(people,R2PeopleChecks.Status.OK,"Nearby VIP entities"),"tagged npc");
  ck(p(people,R2PeopleChecks.Status.KNOWN,"historical behavior were not exercised"),"no false behavior pass");
  ck(p(R2PeopleChecks.evaluate(List.of(),true,List.of(vip),true,-30),R2PeopleChecks.Status.KNOWN,"none nearby"),"empty NPC skipped");
  ck(p(R2PeopleChecks.evaluate(List.of(),false,List.of(vip),true,-30),R2PeopleChecks.Status.KNOWN,"run as a player"),"console skips nearby check");
  var bad=new R2PeopleChecks.Npc("3","human","rome","citizen",List.of("missing"));
  ck(p(R2PeopleChecks.evaluate(List.of(bad),true,List.of(vip),true,-30),R2PeopleChecks.Status.FAIL,"Nearby VIP entities"),"unresolved ID fails");
  var dupeTags=new R2PeopleChecks.Npc("3","human","rome","citizen",List.of("a","a"));
  ck(p(R2PeopleChecks.evaluate(List.of(dupeTags),true,List.of(vip),true,-30),R2PeopleChecks.Status.FAIL,"Nearby VIP entities"),"duplicate tags fail");
  ck(p(R2PeopleChecks.evaluate(List.of(npc),true,List.of(),true,-30),R2PeopleChecks.Status.FAIL,"registry is unavailable"),"empty registry fails");
  ck(p(R2PeopleChecks.evaluate(List.of(),true,List.of(vip),true,-100),R2PeopleChecks.Status.KNOWN,"0 alive-by-date"),"outside lifespan not available");
  var defaults=new R2PeopleChecks.Vip("b","B",-3000,9999,0,0,0,false,false);
  ck(p(R2PeopleChecks.evaluate(List.of(),true,List.of(defaults),true,0),R2PeopleChecks.Status.KNOWN,"defaults"),"default flags warn");
  var invalid=new R2PeopleChecks.Vip("c","C",5,4,95,0,0,false,false);
  ck(p(R2PeopleChecks.evaluate(List.of(),true,List.of(invalid),true,0),R2PeopleChecks.Status.FAIL,"VIP registry:"),"bad dates and coordinates fail");
  ck(p(R2PeopleChecks.evaluate(List.of(npc,npc),true,List.of(vip),true,-30),R2PeopleChecks.Status.FAIL,"ordinary NPCs"),"duplicate entity detected");
  System.out.println("PASS "+n+" R2 event/NPC/VIP checks, including negative and skip cases (headless)");
 }
}
