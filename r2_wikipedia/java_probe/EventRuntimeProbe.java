import com.eternalengine.civilization.HistoryGazetteer;
import com.eternalengine.knowledge.NewsIndex;
import java.util.*;

/** Tests actual Gazetteer and NewsIndex loaders/indexes with a staged pack, not the full mod. */
public class EventRuntimeProbe {
  static void check(boolean ok, String message) { if (!ok) throw new AssertionError(message); }
  static void event(HistoryGazetteer g, String id, int year, int wrongYear, double lat, double lon, boolean regional) {
    List<HistoryGazetteer.Event> hits=g.allEvents().stream().filter(e -> e.id().equals(id)).toList();
    check(hits.size()==1,"missing/duplicate " + id); var e=hits.get(0);
    check(e.start()==year && e.end()==year+1,"wrong half-open years " + id);
    check(Math.abs(e.lat()-lat)<0.00001 && Math.abs(e.lon()-lon)<0.00001,"wrong coordinates " + id);
    check(HistoryGazetteer.isRegional(e)==regional,"wrong region confidence " + id);
    check(g.eventsNear(lat,lon,year,0.01).stream().anyMatch(x -> x.event().id().equals(id)),"year index misses corrected pin " + id);
    check(g.eventsNear(lat,lon,wrongYear,0.01).stream().noneMatch(x -> x.event().id().equals(id)),"old year still indexed " + id);
    check(e.activeIn(year) && !e.activeIn(year+1),"exclusive end broken " + id);
    HistoryGazetteer.setSuppressionFilter(pin -> pin.equals(id));
    check(g.eventsNear(lat,lon,year,0.01).stream().noneMatch(x -> x.event().id().equals(id)),"timeline suppression failed " + id);
    HistoryGazetteer.setSuppressionFilter(null);
    if (regional) check(g.nearestLocalEvent(lat,lon,year).stream().noneMatch(x -> x.event().id().equals(id)),"regional pin presented as local " + id);
    var news=NewsIndex.all().stream().filter(n -> n.name().equals(e.name()) && n.start()==year && Math.abs(n.lat()-lat)<0.00001 && Math.abs(n.lon()-lon)<0.00001).toList();
    check(news.size()==1,"news loader misses corrected row " + id);
    check(news.get(0).end()==year,"news end should be inclusive " + id);
    check(NewsIndex.line(news.get(0),year).contains("in " + year),"news falsely displays a range " + id);
  }
  public static void main(String[] args) {
    var g=HistoryGazetteer.get();
    event(g,"wpy_862b1162d4",1434,1450,50.02861,14.93694,false);
    event(g,"wpy_cbe4bd449d",1795,1750,21.3668482,-157.7933264,true);
    event(g,"wpy_4c5ca5c0b7",1883,1850,-6.102,105.423,false);
    event(g,"wpy_327ae6b1c8",1153,1150,47.6633,9.1753,true);
    event(g,"wpy_73ad8709b2",-3000,-3100,51.17889,-1.82611,false);
    var stonehenge = g.allEvents().stream().filter(e -> e.id().equals("wpy_73ad8709b2")).findFirst().orElseThrow();
    check(stonehenge.name().contains("uncertain") && !stonehenge.name().contains("wooden posts"),"Stonehenge uncertainty wording missing");
    if (args.length > 0 && args[0].equals("full")) {
      System.out.println("PASS: actual Gazetteer and NewsIndex with full resource tree (headless stubs; not a full mod run)");
      return;
    }
    var news=NewsIndex.all();
    for (String name : List.of("synthetic decade", "synthetic regional")) {
      var e=news.stream().filter(x->x.name().equals(name)).findFirst().orElseThrow();
      check(e.start()==2750 && e.end()==2750,"exclusive Wikipedia pack not normalized: " + name);
    }
    var hand=news.stream().filter(x->x.name().equals("synthetic hand inclusive")).findFirst().orElseThrow();
    check(hand.start()==2800 && hand.end()==2803,"hand-authored inclusive end changed");
    check(NewsIndex.near(-82,42,2749).stream().noneMatch(x->x.name().equals("synthetic decade")),"future event used as news");
    check(NewsIndex.near(-82,42,2750).stream().anyMatch(x->x.name().equals("synthetic decade")),"spatial news index misses event");
    check(NewsIndex.onDay(-82,42,27501231).stream().noneMatch(x->x.name().equals("synthetic decade")),"year-only event presented as already finished in the current year");
    check(NewsIndex.onDay(-82,42,27510101).stream().anyMatch(x->x.name().equals("synthetic decade")),"year-only event not available after its year ended");
    System.out.println("PASS: actual Gazetteer loader/year index, regional behavior, NewsIndex year and spatial indexes (headless stubs; not a full mod run)");
  }
}
