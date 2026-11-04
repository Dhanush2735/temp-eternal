/* Step 49 part 3 (G2): what depends on what.
   The claim: the record carries no causal graph - 41,788 dated events and 120 stated causes - so the graph
   is built from time and place, and where that is ambiguous the answer says so instead of choosing. */
import com.eternalengine.timeline.Depends;

import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.zip.GZIPInputStream;

public class Step49DependsProbe {
    static int checks = 0, failed = 0;
    static void ok(boolean c, String what) {
        checks++;
        if (!c) { failed++; System.out.println("  FAIL " + what); }
    }
    static void eq(Object a, Object b, String what) {
        checks++;
        if (a == null ? b != null : !a.equals(b)) {
            failed++; System.out.println("  FAIL " + what + "  expected=" + b + " actual=" + a);
        }
    }

    static InputStream open(String name) {
        return Step49DependsProbe.class.getResourceAsStream(
                "/data/eternalengine/eternal/history/" + name);
    }

    /** Every dated event in a pack of the shape { events: [...] } with name, start, end, lat, lon, radiusKm. */
    static List<Depends.Node> loadEvents(String file) {
        List<Depends.Node> out = new ArrayList<>();
        try (InputStream in = open(file)) {
            if (in == null) return out;
            // Guessing by name is how the first run of this probe lost 13,987 events and measured
            // 26% instead of 39%; sniff the gzip magic instead (the packs ship both ways).
            java.io.BufferedInputStream buf = new java.io.BufferedInputStream(in);
            buf.mark(2);
            int b0 = buf.read(), b1 = buf.read();
            buf.reset();
            java.io.InputStream body = (b0 == 0x1f && b1 == 0x8b) ? new GZIPInputStream(buf) : buf;
            JsonReader r = new JsonReader(new InputStreamReader(body, StandardCharsets.UTF_8));
            r.beginObject();
            while (r.hasNext()) {
                if (!"events".equals(r.nextName())) { r.skipValue(); continue; }
                r.beginArray();
                while (r.hasNext()) {
                    r.beginObject();
                    String name = "";
                    String kind = "";
                    int start = 0, end = 0;
                    double lat = 0, lon = 0, radius = 20;
                    while (r.hasNext()) {
                        String k = r.nextName();
                        switch (k) {
                            case "name" -> name = r.nextString();
                            case "kind" -> kind = r.nextString();
                            case "start" -> start = r.nextInt();
                            case "end" -> end = r.nextInt();
                            case "lat" -> lat = r.nextDouble();
                            case "lon" -> lon = r.nextDouble();
                            case "radiusKm" -> radius = r.nextDouble();
                            default -> r.skipValue();
                        }
                    }
                    r.endObject();
                    out.add(new Depends.Node(start, end, name, kind, lat, lon, radius));
                }
                r.endArray();
            }
            r.endObject();
        } catch (Exception e) {
            System.out.println("  error reading " + file + ": " + e);
        }
        return out;
    }

    public static void main(String[] args) {
        List<Depends.Node> wars = loadEvents("events_wars.json.gz");
        List<Depends.Node> world = loadEvents("events_world.json.gz");
        List<Depends.Node> more = loadEvents("events_wikidata_more.json.gz");
        ok(wars.size() == 2397, "the war pack: " + wars.size());
        ok(world.size() > 13000, "the Wikidata events: " + world.size());
        List<Depends.Node> battles = new ArrayList<>();
        for (Depends.Node n : world) if (n.kind().equals("battle") || n.kind().equals("siege")) battles.add(n);
        for (Depends.Node n : more) if (n.kind().equals("battle") || n.kind().equals("siege")) battles.add(n);
        ok(battles.size() > 14000, "battles and sieges with dates and places: " + battles.size());

        // ------------------------------------------------ 1. THE TWO THINGS AN EDGE CAN BE MADE OF
        Depends.Node war = new Depends.Node(1756, 1763, "the Seven Years War", "war", 51.0, 13.0, 500);
        Depends.Node battle = new Depends.Node(1757, 1757, "the battle of Rossbach", "battle", 51.2, 11.6, 20);
        ok(battle.inside(war), "a battle inside a war's dates and radius fits");
        ok(battle.fits(war, Depends.Node.SLACK_YEARS), "and one that fits exactly fits with slack too");
        Depends.Node elsewhere = new Depends.Node(1757, 1757, "a battle in Bengal", "battle", 23.0, 88.0, 20);
        ok(!elsewhere.inside(war), "and a battle on another continent does not");
        Depends.Node later = new Depends.Node(1900, 1900, "a battle long after", "battle", 51.2, 11.6, 20);
        ok(!later.inside(war), "nor does one a century later at the same place");
        ok(!war.inside(war), "and nothing depends on itself");
        eq(Depends.overlap(war, battle), 1, "the overlap is counted in years");
        eq(Depends.overlap(battle, later), 0, "and is zero when there is none");

        // ------------------------------------------------ 2. A STATED CAUSE WINS, AND IS KEPT WHOLE
        String cause = "To bring the Yadava ruler of Deogiri to submission";
        List<Depends.Edge> stated = Depends.edgesInto(battle, List.of(war, elsewhere), cause);
        eq(stated.size(), 1, "a stated cause gives exactly one edge");
        eq(stated.get(0).basis(), Depends.Basis.STATED, "and it is marked as stated");
        ok(!stated.get(0).ambiguous(), "a stated cause is not ambiguous, whatever else fits");
        eq(stated.get(0).statedCause(), cause, "and the sentence is carried, not paraphrased");
        ok(stated.get(0).usable(), "so a change may follow it");

        // ------------------------------------------------ 3. WHERE NOTHING IS STATED, EVERY CANDIDATE COMES BACK
        List<Depends.Edge> two = Depends.edgesInto(battle,
                List.of(war, new Depends.Node(1756, 1762, "a second war", "war", 51.1, 11.5, 300)), null);
        eq(two.size(), 2, "two wars fit, so two candidates are returned");
        for (Depends.Edge e : two) {
            ok(e.ambiguous(), "and both are marked ambiguous: " + e.parent().name());
            eq(e.basis(), Depends.Basis.TIME_AND_PLACE, "with the basis that produced them");
            ok(!e.usable(), "so the engine must not follow either of them");
        }
        ok(two.get(0).km() <= two.get(1).km(), "nearest first, so a reader can see the order");
        System.out.println("  " + two.get(0).line());

        // One candidate and it is not ambiguous: the common case.
        List<Depends.Edge> one = Depends.edgesInto(battle, List.of(war), null);
        eq(one.size(), 1, "one war fit, so one edge");
        ok(!one.get(0).ambiguous(), "and nothing to be ambiguous about");
        ok(one.get(0).usable(), "so a change may follow it");

        // ------------------------------------------------ 4. THE MEASUREMENT, REPRODUCED IN JAVA
        // The survey measured 39% coverage and 14% ambiguity on 1,500 sampled battles, in Python. This is
        // the same question asked of the same data through this class, and the numbers are asserted to
        // agree to within a few points: a measurement quoted in a README has to be reproducible.
        int sampled = 0, covered = 0, ambiguous = 0;
        for (int i = 0; i < battles.size(); i += 10) {
            Depends.Node b = battles.get(i);
            List<Depends.Edge> into = Depends.edgesInto(b, wars, null);
            sampled++;
            if (!into.isEmpty()) covered++;
            if (into.size() > 1) ambiguous++;
        }
        double coverage = 100.0 * covered / sampled;
        double ambiguity = 100.0 * ambiguous / sampled;
        System.out.println("     " + sampled + " battles: " + Math.round(coverage) + "% inside a war, "
                + Math.round(ambiguity) + "% inside more than one");
        ok(coverage > 34 && coverage < 44, "about two battles in five fall inside a recorded war: "
                + Math.round(coverage) + "%");
        ok(ambiguity > 10 && ambiguity < 18, "and about one in seven falls inside more than one: "
                + Math.round(ambiguity) + "%");
        ok(covered > 0, "so the graph is not empty");
        ok(ambiguous < covered, "and ambiguity is the smaller half of it, which is why the graph is "
                + "usable at all");

        // ------------------------------------------------ 5. WHAT A CHANGE CAN REACH, FORWARD ONLY
        Depends.Node root = new Depends.Node(1756, 1763, "the war", "war", 51.0, 13.0, 600);
        Depends.Node mid = new Depends.Node(1760, 1760, "a siege", "siege", 51.1, 13.1, 20);
        Depends.Node after = new Depends.Node(1762, 1762, "a treaty town", "political", 51.0, 13.0, 30);
        Depends.Node farFuture = new Depends.Node(1850, 1850, "something much later", "cultural", 51.0,
                13.0, 30);
        // The chain is built by hand, so the test is of reach() and not of the builder: root to mid to
        // after, and a fourth node whose only parent is too far in time to be followed.
        List<Depends.Edge> chain = new ArrayList<>();
        chain.add(new Depends.Edge(root, mid, Depends.Basis.STATED, 5, 1, false, "the siege followed"));
        chain.add(new Depends.Edge(mid, after, Depends.Basis.TIME_AND_PLACE, 5, 1, false, null));
        Depends.Node far = new Depends.Node(1850, 1850, "a thing with no parent", "cultural", 51, 13, 30);
        eq(Depends.edgesInto(far, List.of(root, mid, after), null).size(), 0,
                "and a thing a century later has no parent in this chain at all");
        ok(chain.size() == 2, "the chain is built: " + chain.size() + " edges");
        Set<Depends.Node> fiveYears = Depends.reach(root, chain, 3, 5);
        Set<Depends.Node> longHorizon = Depends.reach(root, chain, 3, 50);
        ok(!fiveYears.isEmpty(), "a change to the war reaches something: " + fiveYears.size());
        // The horizon is real: 1762 is six years past 1756, so a five-year horizon does not reach it and a
        // fifty-year one does. The first version of this probe asserted the opposite and was wrong.
        boolean shortReaches = false;
        for (Depends.Node n : fiveYears) if (n.name().contains("treaty town")) shortReaches = true;
        ok(!shortReaches, "and a five-year horizon stops before the 1762 town");
        boolean longReaches = false;
        for (Depends.Node n : longHorizon) if (n.name().contains("treaty town")) longReaches = true;
        ok(longReaches, "while a fifty-year one reaches it: " + longHorizon.size());
        eq(Depends.reach(root, chain, 1, 50).size(), 1, "one step reaches only the siege");
        // Consequences never run backwards.
        Depends.Node earlier = new Depends.Node(1700, 1700, "a much earlier thing", "cultural", 51.0, 13.0, 30);
        List<Depends.Edge> back = Depends.edgesInto(earlier, List.of(root), null);
        eq(back.size(), 0, "and nothing earlier depends on it");

        // ------------------------------------------------ 6. THE SENTENCE A READER GETS
        String line = Depends.explain(battle, two);
        System.out.println("  " + line);
        ok(line.contains("more than one parent"), "an ambiguous explanation says so: " + line);
        String lonely = Depends.explain(new Depends.Node(1200, 1200, "a quiet year", "cultural", 10, 10, 20),
                two);
        ok(lonely.contains("nothing behind it"), "and an event with no parent says that plainly rather "
                + "than inventing one: " + lonely);
        ok(lonely.contains("not a claim that it had no cause"),
                "and is careful about what that means: " + lonely);

        // ------------------------------------------------ 7. THE WHOLE GRAPH, AND ITS AMBIGUITY
        List<Depends.Node> sample = new ArrayList<>();
        for (int i = 0; i < battles.size() && sample.size() < 2000; i += 7) sample.add(battles.get(i));
        List<Depends.Edge> graph = Depends.graph(sample, wars);
        System.out.println("     graph over " + sample.size() + " battles: " + graph.size()
                + " edges, ambiguity " + Math.round(100 * Depends.ambiguousShare(graph)) + "%");
        ok(!graph.isEmpty(), "the graph over two thousand battles has edges: " + graph.size());
        // THE FINDING, and it is worse than the sample suggested: over half of the computed edges have a
        // rival. Wars overlap in space and time far more than a war and its battles do, so a computed
        // edge is the weaker kind of evidence and is marked as such rather than used silently.
        ok(Depends.ambiguousShare(graph) > 0.4, "and here is the number that limits this whole graph: "
                + Math.round(100 * Depends.ambiguousShare(graph))
                + "% of the computed edges have a rival parent");
        eq(Depends.ambiguousShare(List.of()), 0.0, "an empty graph has no ambiguity to report");

        System.out.println(failed == 0
                ? "Step49DependsProbe: " + checks + " checks, 0 failed"
                : "Step49DependsProbe: " + checks + " checks, " + failed + " FAILED");
        if (failed != 0) System.exit(1);
    }
}
