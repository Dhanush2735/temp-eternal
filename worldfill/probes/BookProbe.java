import com.eternalengine.knowledge.BookService;
import com.eternalengine.knowledge.BookView;
import com.eternalengine.knowledge.KnowledgeCard;
import com.eternalengine.knowledge.KnowledgeDate;
import com.eternalengine.knowledge.KnowledgePacks;
import com.eternalengine.knowledge.PlayerKnowledge;
import io.netty.buffer.ByteBuf;
import io.netty.buffer.Unpooled;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;

import java.util.UUID;

/**
 * Step 20: the history book and the tracker compass with the mod's real code and data, no server (the screen itself:
 * probe_screens.sh). Run by worldfill/probe_book.sh. Exit code 1 if a check fails.
 */
public final class BookProbe {
    private static int pass;
    private static int fail;

    public static void main(String[] args) {
        System.out.println("1. The book's own check");
        String self = BookService.selfTest();
        check("BookService.selfTest", self == null, String.valueOf(self));

        System.out.println("\n2. Distance words (the compass and the book)");
        word(17.3616, 78.4747, 17.3928, 78.4808, "about 3.5 km north", "Charminar to King Kothi");
        word(17.3616, 78.4747, 17.3620, 78.4750, "about 50 m north-east", "a few steps");
        word(17.3616, 78.4747, 17.3616, 78.4747, "right here", "the same spot");
        word(17.3616, 78.4747, 18.94, 72.83, "about 622 km west", "Hyderabad to Bombay");
        word(51.5074, -0.1278, 48.8566, 2.3522, "about 344 km south-east", "London to Paris");

        System.out.println("\n3. Saved and read back");
        PlayerKnowledge pk = new PlayerKnowledge();
        UUID who = new UUID(20L, 3L);
        int date = KnowledgeDate.key(1948, 9, 14);
        pk.heard(who, "nizam", "The Nizam", "Person");
        pk.note(who, "nizam", "The Nizam", "Person", new PlayerKnowledge.Note(date, "Saleem, paper seller", "who", "Text."));
        pk.journal(who, date, "Learned about The Nizam from Saleem.", "nizam");
        pk.track(who, new PlayerKnowledge.Track("king_kothi", "King Kothi", 17.3928, 78.4808));
        boolean firstBook = pk.giveBookOnce(who);
        boolean secondBook = pk.giveBookOnce(who);
        PlayerKnowledge back = PlayerKnowledge.load(pk.save(new CompoundTag()));
        check("the journal, the compass target and the gift come back after saving",
                back.journalOf(who).size() == 1 && back.trackOf(who) != null && back.trackOf(who).label().equals("King Kothi")
                        && firstBook && !secondBook && !back.giveBookOnce(who) && back.of(who).get("nizam").notes().size() == 1,
                back.journalOf(who) + " " + back.trackOf(who));
        for (int i = 0; i < 250; i++) {
            pk.journal(who, date, "line " + i, "");
        }
        check("the journal keeps the newest " + PlayerKnowledge.MAX_JOURNAL + " lines, newest first",
                pk.journalOf(who).size() == PlayerKnowledge.MAX_JOURNAL && pk.journalOf(who).get(0).text().equals("line 249"), "");

        System.out.println("\n4. Every name of the Hyderabad pack in one book");
        KnowledgePacks.Pack pack = KnowledgePacks.covering(17.3616, 78.4747, date).get(0);
        PlayerKnowledge all = new PlayerKnowledge();
        for (KnowledgeCard c : pack.cards().values()) {
            all.heard(who, c.id(), c.title(), c.kind());
        }
        BookView v = BookService.build(all, who, new double[] {17.3616, 78.4747}, date, "", "notes", "", false);
        int located = 0;
        for (KnowledgeCard c : pack.cards().values()) {
            located += c.hasLocation() ? 1 : 0;
        }
        String lastGroup = "";
        boolean ordered = true;
        int lastIndex = -1;
        String[] order = {"Events", "People", "Groups", "Families", "States", "Places"};
        for (BookView.Entry e : v.entries) {
            String g = BookView.groupName(e.kind());
            int idx = java.util.Arrays.asList(order).indexOf(g);
            if (!g.equals(lastGroup)) {
                ordered &= idx < 0 || idx > lastIndex;
                lastIndex = Math.max(lastIndex, idx);
                lastGroup = g;
            }
        }
        check(v.entries.size() + " names in groups in the preview's order (Events, People, Groups, Families, States, Places);"
                + " " + located + " of them have a place to track", v.entries.size() == pack.cards().size() && ordered
                && located > 0, "");
        check("a name only heard says so: \"" + v.nothing + "\"", v.notes.isEmpty() && v.nothing.startsWith("You have heard"),
                v.nothing);
        ByteBuf raw = Unpooled.buffer();
        FriendlyByteBuf buf = new FriendlyByteBuf(raw);
        BookView big = new BookView();
        big.card = "x";
        big.title = "y".repeat(500);
        big.notes.add(new BookView.Note("14 Sep 1948", "z".repeat(300), "w".repeat(5000)));
        big.encode(buf);
        BookView bb = BookView.decode(buf);
        raw.release();
        check("very long words are cut, not refused, on the way to the screen", bb.title.length() <= 160
                && bb.notes.get(0).text().length() <= 1200 && bb.notes.get(0).text().endsWith("…"), "");

        System.out.println("\n" + pass + " passed, " + fail + " failed");
        System.exit(fail == 0 ? 0 : 1);
    }

    static void word(double a, double b, double c, double d, String expect, String what) {
        String w = BookService.where(a, b, c, d);
        check(what + ": " + w, w.equals(expect), "expected " + expect);
    }

    static void check(String what, boolean ok, String detail) {
        if (ok) {
            pass++;
            System.out.println("  PASS " + what);
        } else {
            fail++;
            System.out.println("  FAIL " + what + (detail == null || detail.isEmpty() ? "" : " -- " + detail));
        }
    }
}
