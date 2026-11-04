import com.eternalengine.civilization.HistoryGazetteer;
import com.eternalengine.knowledge.NewsIndex;

/** Real Gazetteer/NewsIndex against staged or installed decade data; unrelated classes are stubs. */
public class DecadeRuntimeProbe {
  static void check(boolean ok, String message) { if (!ok) throw new AssertionError(message); }
  static void event(HistoryGazetteer g, String id, String name, int year, double lat, double lon, double oldLat, double oldLon, boolean full, boolean oldNewsOutOfRange) {
    var list=g.allEvents().stream().filter(x -> x.id().equals(id)).toList();
    check(list.size()==1,"wrong row count " + id);
    var e=list.get(0);
    check(e.name().equals(name),"wrong name " + id);
    check(e.start()==year && e.end()==year+1,"wrong year " + id);
    check(Math.abs(e.lat()-lat)<0.00001 && Math.abs(e.lon()-lon)<0.00001,"wrong coordinate " + id);
    check(e.radiusKm()==20 && HistoryGazetteer.isRegional(e),"wrong region/radius " + id);
    check(g.eventsNear(lat,lon,year,0.01).stream().anyMatch(x -> x.event().id().equals(id)),"missing new point " + id);
    check(g.eventsNear(oldLat,oldLon,year,0.01).stream().noneMatch(x -> x.event().id().equals(id)),"old point still active " + id);
    check(g.eventsNear(lat,lon,year+1,0.01).stream().noneMatch(x -> x.event().id().equals(id)),"exclusive end violated " + id);
    check(g.nearestLocalEvent(lat,lon,year).stream().noneMatch(x -> x.event().id().equals(id)),"region presented as local " + id);
    HistoryGazetteer.setSuppressionFilter(s -> s.equals(id));
    check(g.eventsNear(lat,lon,year,0.01).stream().noneMatch(x -> x.event().id().equals(id)),"branch suppression failed " + id);
    HistoryGazetteer.setSuppressionFilter(null);
    var n=NewsIndex.all().stream().filter(x -> x.name().equals(name) && x.start()==year).toList();
    check(n.size()==1 && n.get(0).end()==year,"news year or count wrong " + id);
    // near() returns only one winner, so a closer/tied record in the full resource tree can win.
    if (!full) check(NewsIndex.near(lat,lon,year).stream().anyMatch(x->x.name().equals(name)),"new news point missing " + id);
    else System.out.println("Full-tree selected news near " + id + ": " + NewsIndex.near(lat,lon,year).map(NewsIndex.Event::name).orElse("none"));
    if (oldNewsOutOfRange) check(NewsIndex.near(oldLat,oldLon,year).stream().noneMatch(x->x.name().equals(name)),"old news point active " + id);
  }
  public static void main(String[] args) {
    var g=HistoryGazetteer.get(); boolean full=args.length>0 && args[0].equals("full");
    event(g,"wpd_aaa30cdc8e","Trần dynasty begins in Đại Việt",1225,21.0375,105.83861,13.7242,103.5584,full,true);
    event(g,"wpd_f55ff873e0","Vijayanagara forces defeat the Bijapur Sultanate at the Battle of Raichur",1520,16.2,77.35056,12.4849,77.9165,full,true);
    event(g,"wpd_342c3bc78d","Asante forces defeat Denkyira at the Battle of Feyiase",1701,6.61369,-1.56117,6.7867,-1.397,full,false);
    event(g,"wpd_2a4ff24090","David IV captures Tbilisi and makes it the capital of the Kingdom of Georgia",1122,41.7225,44.7925,36.1096,52.6095,full,true);
    event(g,"wpd_8de2b0f5d2","Cardinal Cisneros founds a university in Alcalá de Henares with papal authorization",1499,40.467,-3.367,42.7415,2.0069,full,true);
    event(g,"wpd_1acbbba18d","Ternatean forces under Sultan Babullah take the Portuguese fort after a long siege",1575,0.76083,127.31194,40.0197,-3.7048,full,true);
    System.out.println("PASS: decade rows in actual Gazetteer and NewsIndex, years, regional handling, old and new locations, suppression (headless; not a full mod run)");
  }
}
