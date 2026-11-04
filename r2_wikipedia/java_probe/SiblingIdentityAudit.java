import com.eternalengine.civilization.HistoryGazetteer;
import com.eternalengine.timeline.SiblingIndex;
import com.eternalengine.timeline.BranchSuppression;
import java.util.*;

/** Actual SiblingIndex, Gazetteer and BranchSuppression with headless Gazetteer stubs. */
public class SiblingIdentityAudit {
  static void check(boolean ok,String message) { if (!ok) throw new AssertionError(message); }
  public static void main(String[] args) {
    var events=HistoryGazetteer.get().allEvents();
    var pins=new ArrayList<SiblingIndex.Pin>();
    var regions=new HashSet<String>();
    for (var e: events) {
      if (e.start()==1898 && Math.abs(e.lat()-47.0671)<0.002 && Math.abs(e.lon()-1.979)<0.002) {
        pins.add(new SiblingIndex.Pin(e.id(),e.lat(),e.lon(),e.start(),e.end()));
        if (HistoryGazetteer.isRegional(e)) regions.add(e.id());
      }
    }
    String a="wpr_c5ddcd7ba5"; // French Chamber elections.
    String b="wpr_946ba04772"; // Colonel Henry's death in prison.
    var legacy=SiblingIndex.build(pins);
    check(legacy.siblingsOf(a).contains(b),"fixture should reproduce the old grouping");
    var safe=SiblingIndex.build(pins,regions);
    check(regions.contains(a) && regions.contains(b),"fixture records must be regional");
    check(safe.pinCount()==legacy.pinCount(),"exclusion removed IDs");
    check(safe.clusterOfId(a).equals(Set.of(a)),"regional ID no longer resolvable");
    check(safe.suppressionSetFor(a).equals(Set.of(a)),"unrelated regional records still grouped");
    check(safe.suppressionSetFor(b).equals(Set.of(b)),"other regional record still grouped");
    var branch=new BranchSuppression();branch.register("fresh","main");
    branch.suppressAll("fresh",safe.suppressionSetFor(a));
    check(branch.isSuppressed("fresh",a) && !branch.isSuppressed("fresh",b),"fresh branch suppresses unrelated region");
    // A saved branch still restores exactly what was previously stored, including an old bad grouping.
    branch.register("restored","main");branch.suppressAll("restored",Set.of(a,b));
    check(branch.isSuppressed("restored",a) && branch.isSuppressed("restored",b),"legacy suppression set changed");
    branch.register("child","restored");
    check(branch.isSuppressed("child",a) && branch.isSuppressed("child",b),"ancestor suppressions lost");
    // Preserve old local heuristic: two nearby same-year non-regional pins can still cluster.
    var local=List.of(new SiblingIndex.Pin("localA",1,1,2000,2001),new SiblingIndex.Pin("localB",1.001,1.001,2000,2001));
    check(SiblingIndex.build(local,Set.of()).siblingsOf("localA").contains("localB"),"local legacy grouping changed");
    check(SiblingIndex.build(local,Set.of("localA")).suppressionSetFor("localA").equals(Set.of("localA")),"excluded ID still clusters");
    check(SiblingIndex.build(local,Set.of("localA")).pinCount()==2,"excluded ID removed from index");
    check(SiblingIndex.build(local,null).siblingsOf("localA").contains("localB"),"null exclusion should be empty");
    var independent=SiblingIndex.buildIndependent(local);
    check(independent.pinCount()==2 && independent.clusterCount()==0,"independent index lost pins or created a group");
    check(independent.suppressionSetFor("localA").equals(Set.of("localA")),"independent pins grouped");
    check(SiblingIndex.buildIndependent(null).pinCount()==0,"independent null index");
    System.out.println("Prior proximity-only sample clustered " + legacy.clusterOfId(a).size() + " regional records.");
    System.out.println("PASS: excluded regional pins stay resolvable and do not cluster; branch pivot, legacy saved sets, inheritance and local heuristic (headless). ");
    System.out.println("Legacy proximity builders remain unsafe; production uses an independent-ID index. No full game or actual saved-world test.");
  }
}
