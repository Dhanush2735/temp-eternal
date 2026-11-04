package com.eternalengine.civilization;
import java.util.*;
public class RulerRegister {
 public record Polity(String civHint,String name){} public record Extent(int start,int end,double lat,double lon,String name){}
 public record Summary(){public String display(){return "stub";}}
 public static RulerRegister get(){return new RulerRegister();} public List<Polity> deccanPolities(){return List.of();}
 public List<Polity> polities(){return List.of();} public Optional<Extent> extentOf(String s){return Optional.empty();}
 public Summary summary(){return new Summary();}
}
