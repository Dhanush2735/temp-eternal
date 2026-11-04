import com.eternalengine.civilization.HistoryGazetteer;
import com.eternalengine.timeline.SiblingIndex;
import java.util.*;

/** Full-tree measurement of the current proximity heuristic, not a correctness census. */
public class FullSiblingRiskAudit {
  public static void main(String[] args) {
    var pins=new ArrayList<SiblingIndex.Pin>();
    var regional=new HashSet<String>();
    var events=new LinkedHashMap<String,HistoryGazetteer.Event>();
    int rows=0, duplicates=0;
    for (var e: HistoryGazetteer.get().allEvents()) {
      rows++;
      if (events.put(e.id(),e)!=null) duplicates++;
      pins.add(new SiblingIndex.Pin(e.id(), e.lat(),e.lon(),e.start(),Math.max(e.end(), e.start()+1)));
      if (HistoryGazetteer.isRegional(e)) regional.add(e.id());
    }
    var index=SiblingIndex.build(pins,regional);
    Set<String> seen=new HashSet<>(); int grouped=0, groupCount=0, maxSize=0; Set<String> largest=Set.of();
    for(String id:events.keySet()) {
      if(seen.contains(id))continue;
      var cluster=index.clusterOfId(id);
      if(cluster.size()>1){groupCount++;grouped+=cluster.size();seen.addAll(cluster);if(cluster.size()>maxSize){maxSize=cluster.size();largest=cluster;}}
    }
    List<HistoryGazetteer.Event> order=new ArrayList<>();for(String id:largest){var e=events.get(id);if(e!=null)order.add(e);}
    order.sort(Comparator.comparingInt(HistoryGazetteer.Event::start));
    System.out.printf("rows=%d distinct IDs=%d duplicate IDs=%d regional IDs=%d indexed=%d groups=%d grouped IDs=%d largest=%d%n",rows,events.size(),duplicates,regional.size(),index.pinCount(),groupCount,grouped,maxSize);
    if(!order.isEmpty()) {
      System.out.printf("largest cluster event start-year range: %d to %d%n",order.get(0).start(),order.get(order.size()-1).start());
      for (var e:List.of(order.get(0),order.get(order.size()/2),order.get(order.size()-1)))
        System.out.printf("  %s year=%d (%s,%s) confidence=%s name=%s%n",e.id(),e.start(),e.lat(),e.lon(),e.confidence(),e.name());
    }
    // These are distinct events 118 years apart, yet previously share a transitive cluster.
    String cold="wpy_3b7439cae9", launch="wpy_23e5c34f56";
    if(!index.clusterOfId(cold).contains(launch)) throw new AssertionError("corpus fixture no longer demonstrates transitive grouping");
    var independent=SiblingIndex.buildIndependent(pins);
    if(independent.pinCount()!=index.pinCount() || independent.clusterCount()!=0)
      throw new AssertionError("independent index lost IDs or invented groups");
    if(!independent.suppressionSetFor(cold).equals(Set.of(cold)) || !independent.suppressionSetFor(launch).equals(Set.of(launch)))
      throw new AssertionError("independent events still coupled");
    System.out.println("PASS: ID-only index retains all indexed IDs and separates the 1908 and 2026 events.");
    // Two differently dated storm rows collide on one ID. Show the residual ID-level problem
    // through the actual Gazetteer spatial lookup and actual branch predicate.
    var gaz=HistoryGazetteer.get(); String collision="q272450";
    var colliding=gaz.allEvents().stream().filter(e->collision.equals(e.id())).toList();
    if(colliding.size()!=2 || colliding.get(0).start()==colliding.get(1).start()) throw new AssertionError("storm collision fixture changed");
    HistoryGazetteer.setSuppressionFilter(null);
    for(var e:colliding) if(gaz.eventsNear(e.lat(),e.lon(),e.start(),0.1).stream().noneMatch(h->h.event().id().equals(collision))) throw new AssertionError("collision not visible");
    var branch=new com.eternalengine.timeline.BranchSuppression();branch.register("test","main");branch.suppress("test",collision);
    HistoryGazetteer.setSuppressionFilter(id->branch.isSuppressed("test",id));
    for(var e:colliding) if(gaz.eventsNear(e.lat(),e.lon(),e.start(),0.1).stream().anyMatch(h->h.event().id().equals(collision))) throw new AssertionError("collision not filtered");
    HistoryGazetteer.setSuppressionFilter(null);
    System.out.println("RESIDUAL RISK CONFIRMED: suppressing shared ID q272450 hides both differently dated storm rows.");
    System.out.println("Grouping counts are algorithm results, not a count of duplicate or erroneous historical events.");
  }
}
