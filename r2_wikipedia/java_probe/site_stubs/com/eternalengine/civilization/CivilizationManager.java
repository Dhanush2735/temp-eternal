package com.eternalengine.civilization; import java.util.*;import com.eternalengine.core.WorldStateManager;
public class CivilizationManager {
 private final Map<String,Civilization> all=new HashMap<>();
 public Optional<Civilization> getCivilization(String id){return Optional.ofNullable(all.get(id));}
 public void addCivilization(Civilization c,WorldStateManager state){all.put(c.id(),c);}
 public List<Civilization> all(){return List.copyOf(all.values());}
}
