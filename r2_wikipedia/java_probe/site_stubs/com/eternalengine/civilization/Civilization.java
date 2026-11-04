package com.eternalengine.civilization;
public class Civilization {
 private final String id,name;private final int start;private final double lat,lon;private boolean active;private String gov="";private int fall=Integer.MAX_VALUE;
 public Civilization(String id,String name,int start,double lat,double lon){this.id=id;this.name=name;this.start=start;this.lat=lat;this.lon=lon;}
 public String id(){return id;} public String name(){return name;} public int foundingYear(){return start;}
 public double capitalLat(){return lat;}public double capitalLon(){return lon;}public boolean active(){return active;}
 public String governmentType(){return gov;}public long population(){return 0;}public long treasury(){return 0;}
 public int technologyLevel(){return 0;}public String religionId(){return "none";}public int fallYear(){return fall;}public int peakYear(){return 0;}
 public void setActive(boolean v){active=v;}public void setGovernmentType(String v){gov=v;}public void setFallYear(int v){fall=v;}
}
