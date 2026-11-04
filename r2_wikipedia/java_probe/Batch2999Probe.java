import com.eternalengine.civilization.HistoryGazetteer;
import com.eternalengine.knowledge.NewsIndex;
/** Actual Gazetteer and NewsIndex on the complete indexed tree; other dependencies stubbed. */
public class Batch2999Probe {
 static void check(boolean b,String m){if(!b)throw new AssertionError(m);}
 public static void main(String[] args){
  var g=HistoryGazetteer.get();String id="r2_early_harappan_regional_context";
  var rows=g.allEvents().stream().filter(e->e.id().equals(id)).toList();check(rows.size()==1,"missing/duplicate context");var e=rows.get(0);
  check(e.start()==-3300&&e.end()==-2599&&e.name().contains("Early Harappan cultures"),"bad range/name");
  check(HistoryGazetteer.isRegional(e),"not regional");
  for(int y=-2999;y<=-2990;y++){
   final int year=y;
   check(g.eventsNear(29.0,70.5,year,.01).stream().anyMatch(h->h.event().id().equals(id)),"missing in year "+year);
   check(g.nearestLocalEvent(29.0,70.5,year).stream().noneMatch(h->h.event().id().equals(id)),"regional treated as local");
  }
  check(g.eventsNear(29.0,70.5,-2599,.01).stream().noneMatch(h->h.event().id().equals(id)),"end not exclusive");
  var news=NewsIndex.all().stream().filter(n->n.name().equals(e.name())).toList();check(news.size()==1,"news missing/duplicate");
  check(news.get(0).start()==-3300&&news.get(0).end()==-2600,"bad NewsIndex inclusive boundary");
  System.out.println("PASS: regional contextual period indexed for all 10 years; Gazetteer/NewsIndex boundaries correct (headless)");
 }
}
