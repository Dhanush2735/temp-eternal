package com.eternalengine.core;
import java.util.*;
/** In-memory test double; this does not exercise Minecraft state serialization. */
public class WorldStateManager {
  public static class TimelineBranchState {
    public String branchId,parentId,divergenceEventId,cause,scenarioId="",historyLogEntry="";
    public int divergenceYear, authoredUntilYear;
    public boolean isMain;
    public final List<String> suppressedEventIds=new ArrayList<>();
  }
  private final Map<String,TimelineBranchState> branches=new LinkedHashMap<>();
  private String active="main";
  public Map<String,TimelineBranchState> getAllTimelineBranches(){return branches;}
  public String getActiveTimelineBranchId(){return active;}
  public void addTimelineBranch(TimelineBranchState s){branches.put(s.branchId,s);}
  public void setActiveTimelineBranch(String id){active=id;}
  public void setFlag(String k,String v){}
}
