import com.eternalengine.core.WorldStateManager;
import com.eternalengine.civilization.HistoryGazetteer;
import com.eternalengine.timeline.*;
import com.google.gson.JsonParser;
import java.util.*;

/** Real TimelineManager control flow; in-memory world-state and Minecraft stubs. */
public class TimelineManagerProbe {
  static void check(boolean b,String message){if(!b)throw new AssertionError(message);}
  public static void main(String[] a){
    String p="event-a", q="event-b", legacy="old-extra";
    var pins=List.of(new SiblingIndex.Pin(p,1,1,2000,2001),new SiblingIndex.Pin(q,1.001,1.001,2000,2001));
    check(SiblingIndex.build(pins).suppressionSetFor(p).contains(q),"fixture must demonstrate old behavior");
    var index=SiblingIndex.buildIndependent(pins);
    var scenarios=new ScenarioRegistry();
    scenarios.parseInto(JsonParser.parseString("{\"scenarioId\":\"sample\",\"triggerPin\":\"event-a\",\"triggerYear\":2000,\"title\":\"Test\",\"author\":\"test\",\"authoredUntilYear\":2002,\"events\":[{\"year\":2000,\"name\":\"Initial\",\"description\":\"Test\",\"provenance\":\"authored\"},{\"year\":2001,\"name\":\"Later\",\"description\":\"Test\",\"provenance\":\"authored\"}]}"),"synthetic");
    check(scenarios.size()==1,"synthetic scenario did not load: "+scenarios.loadErrors());
    var world=new WorldStateManager(); var manager=new TimelineManager();
    manager.setSiblingIndex(index); manager.setScenarios(scenarios);
    var branch=manager.createDivergence(new TimelineSeed(123,"main",p,2000,"action"),"test",world);
    check(manager.isSuppressedInActiveBranch(p) && !manager.isSuppressedInActiveBranch(q),"fresh fork grouped neighbors");
    check(HistoryGazetteer.suppressionFilter().test(p) && !HistoryGazetteer.suppressionFilter().test(q),"overlay not wired");
    check(world.getAllTimelineBranches().get(branch.branchId()).suppressedEventIds.equals(List.of(p)),"saved fresh set incorrect");
    check(manager.activeScenario().isPresent() && !manager.activeChronicle().isEmpty(),"scenario initial consequence missing");
    manager.resetScenarioCursor(2000);check(manager.tickScenarios(2001,world)==1,"scenario pump did not tick");
    var child=manager.createDivergence(new TimelineSeed(123,branch.branchId(),q,2001,"action"),"test-child",world);
    check(manager.isSuppressedInActiveBranch(p) && manager.isSuppressedInActiveBranch(q),"new child ancestry incorrect");
    check(world.getAllTimelineBranches().get(child.branchId()).suppressedEventIds.equals(List.of(q)),"child saved inherited IDs as direct");
    // Inject an old over-suppressed ID as though it had been in the saved branch.
    world.getAllTimelineBranches().get(branch.branchId()).suppressedEventIds.add(legacy);
    var restored=new TimelineManager();restored.setSiblingIndex(index);restored.setScenarios(scenarios);
    check(restored.restoreFrom(world)==2,"incorrect restore count");
    check(restored.activeBranchId().equals(child.branchId()),"active child not restored");
    check(restored.effectiveSuppressedInActiveBranch().equals(Set.of(p,q,legacy)),"restore did not preserve old direct and inherited IDs");
    restored.installSuppressionOverlay();check(HistoryGazetteer.suppressionFilter().test(legacy),"restored overlay missing saved ID");
    check(world.getAllTimelineBranches().get(branch.branchId()).suppressedEventIds.equals(List.of(p,legacy)),"restore rewrote saved suppression");
    // Namespace-only IDs still self-suppress even without a gazetteer record.
    var other=new TimelineManager();other.setSiblingIndex(index);
    other.createDivergence(new TimelineSeed(5,"main","vip:synthetic",2000,"x"),"test",null);
    check(other.isSuppressedInActiveBranch("vip:synthetic"),"non-gazetteer pivot not suppressed");
    HistoryGazetteer.setSuppressionFilter(null);
    System.out.println("PASS: actual TimelineManager fresh fork, overlay, synthetic scenario, child ancestry, simulated saved-state restore and namespace pivot (headless stubs).");
    System.out.println("WorldStateManager, Minecraft and persistence serialization are stubbed; not an actual saved-world test.");
  }
}
