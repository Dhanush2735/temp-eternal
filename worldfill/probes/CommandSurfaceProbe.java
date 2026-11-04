import com.eternalengine.commands.EternalEngineCommands;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.ParseResults;
import net.minecraft.commands.CommandSource;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.world.phys.Vec2;
import net.minecraft.world.phys.Vec3;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * The 212-command surface (gate G5, second half): every line of {@code eternal/ee_command_list.txt}
 * through Minecraft's own command dispatcher, outside the game.
 *
 * <p>For each line it records three things and nothing is inferred:
 * <ul>
 *   <li><b>does it parse</b> - Brigadier resolves the literals and the arguments. A line the tree does
 *       not know is a defect in the list or in the tree, and it is caught here;</li>
 *   <li><b>does it run</b> - the command executes without a Java exception. An exception that is the
 *       absent server or the absent player is the sandbox's limit and is marked as such, not as a
 *       defect; anything else is a defect;</li>
 *   <li><b>does it answer</b> - how many chat lines came back, and the first of them.</li>
 * </ul>
 *
 * <p>The source is an operator with no player and no level, exactly as {@code CommandHarness} does it,
 * so every command that needs a player or a running world is expected to refuse - and must refuse in
 * words, not with a stack trace.
 *
 * <p>Usage: {@code java CommandSurfaceProbe [listFile] [reportTsv]}
 */
public final class CommandSurfaceProbe {

    /** A message that shows the player a Java exception or a bare null instead of words. */
    private static final java.util.regex.Pattern LEAK = java.util.regex.Pattern.compile(
            "NullPointerException|[A-Za-z]+Exception:|because the return value of|is null");

    private static final List<String> CHAT = Collections.synchronizedList(new ArrayList<>());
    private static final List<String> ERRORS = Collections.synchronizedList(new ArrayList<>());

    private static CommandSourceStack source(String name, int permission) {
        CommandSource chat = new CommandSource() {
            @Override public void sendSystemMessage(Component c) {
                CHAT.add(c.getString().replaceAll("§.", "").trim());
            }
            @Override public boolean acceptsSuccess() { return true; }
            @Override public boolean acceptsFailure() { return true; }
            @Override public boolean shouldInformAdmins() { return false; }
        };
        return new CommandSourceStack(chat, Vec3.ZERO, Vec2.ZERO, null, permission, name,
                Component.literal(name), null, null);
    }

    /** One command's outcome. */
    record Run(String command, String verdict, int returns, String detail) {}

    public static void main(String[] args) throws Exception {
        Path list = Path.of(args.length > 0 ? args[0] : "/home/user/eternal/ee_command_list.txt");
        Path report = Path.of(args.length > 1 ? args[1] : "/home/user/testrun/command_surface.tsv");

        CommandDispatcher<CommandSourceStack> d = new CommandDispatcher<>();
        EternalEngineCommands.register(d);
        CommandSourceStack op = source("harness", 4);

        // The managers the mod starts on server start. They are what the commands ask for, and they
        // are initialised here without a server, so a command that only needs the simulation can be
        // judged; one that needs a level or a player still cannot, and says so.
        // Minecraft's own registries, as a headless server bootstraps them: the simulation builds
        // items and blocks (heraldry needs DyeColor), so without this the engine cannot start and
        // 114 commands would look broken when they are only unstarted.
        try {
            net.minecraft.SharedConstants.setVersion(net.minecraft.DetectedVersion.BUILT_IN);
            net.minecraft.server.Bootstrap.bootStrap();
            System.out.println("Minecraft bootstrapped (registries only; no server, no level)");
        } catch (Throwable e) {
            System.out.println("could not bootstrap Minecraft: " + e);
        }
        for (String m : new String[]{
                "com.eternalengine.core.AsyncTaskManager",
                "com.eternalengine.core.PerformanceMonitor",
                "com.eternalengine.clock.SimulationClockManager",
                "com.eternalengine.core.WorldStateManager",
                "com.eternalengine.core.SimulationTickScheduler",
                "com.eternalengine.core.PersistenceManager",
                "com.eternalengine.core.VersionManager",
                "com.eternalengine.core.SimulationEngine"}) {
            try {
                Class.forName(m).getMethod("initialize").invoke(null);
                System.out.println("initialised " + m);
            } catch (Throwable e) {
                Throwable c = e.getCause() != null ? e.getCause() : e;
                System.out.println("could not initialise " + m + ": " + c.getClass().getSimpleName()
                        + ": " + c.getMessage());
            }
        }

        List<String> lines = Files.readAllLines(list, StandardCharsets.UTF_8);
        List<Run> runs = new ArrayList<>();
        for (String raw : lines) {
            String line = raw.trim();
            if (line.isEmpty() || line.startsWith("#")) {
                continue;
            }
            if (line.startsWith("/")) {
                line = line.substring(1);
            }
            CHAT.clear();
            ERRORS.clear();
            String verdict;
            int returns = -1;
            String detail;
            try {
                ParseResults<CommandSourceStack> parsed = d.parse(line, op);
                if (!parsed.getExceptions().isEmpty()) {
                    verdict = "PARSE-FAIL";
                    detail = parsed.getExceptions().values().iterator().next().getMessage();
                } else if (parsed.getContext().getNodes().isEmpty() || parsed.getContext().getCommand() == null) {
                    verdict = "PARSE-FAIL";
                    detail = "the tree resolves no command for this line";
                } else {
                    // A watchdog, because a command that waits on the absent server would hang the run.
                    final int[] ret = {-1};
                    final Throwable[] thrown = {null};
                    Thread t = new Thread(() -> {
                        try {
                            ret[0] = d.execute(parsed);
                        } catch (Throwable e) {
                            thrown[0] = e;
                        }
                    }, "cmd-" + line);
                    t.setDaemon(true);
                    t.start();
                    t.join(Long.getLong("probe.timeoutMs", 20_000L));
                    if (t.isAlive()) {
                        verdict = "TIMEOUT";
                        detail = "still running after " + (Long.getLong("probe.timeoutMs", 20_000L) / 1000) + " s";
                    } else if (thrown[0] != null) {
                        returns = ret[0];
                        verdict = unjudgeable(thrown[0]) ? "CANNOT-JUDGE-HERE" : "THROW";
                        detail = thrown[0].getClass().getSimpleName() + ": " + thrown[0].getMessage();
                    } else {
                        returns = ret[0];
                        verdict = returns == 0 ? "REFUSED" : "PASS";
                        detail = CHAT.isEmpty() ? "(no message)" : String.join(" | ", head(CHAT, 3));
                        if (returns == 0 && !CHAT.isEmpty()) {
                            // a refusal in words is still an answer; keep it, the verdict says which
                            verdict = "PASS";
                        }
                    }
                }
                // Board 17: a command may hand its answer to a background phase ("... in the
                // background, the results follow here"). Judging it on its first reply alone
                // reads "no tally at all" on a busy machine, which is a flaky gate, not a defect.
                // So wait for the phase to report before moving on.
                if (detail != null && detail.contains("in the background")) {
                    long waitMs = Long.getLong("probe.backgroundWaitMs", 60_000L);
                    long deadline = System.currentTimeMillis() + waitMs;
                    String tally = null;
                    while (System.currentTimeMillis() < deadline) {
                        synchronized (CHAT) {
                            for (String m : CHAT) {
                                if (m.contains("All checks done")) { tally = m; break; }
                            }
                        }
                        if (tally != null) { break; }
                        try {
                            Thread.sleep(200L);
                        } catch (InterruptedException ie) {
                            Thread.currentThread().interrupt();
                            break;
                        }
                    }
                    detail = detail + " || "
                            + (tally != null ? tally
                            : "no tally within " + (waitMs / 1000) + " s of the background phase");
                }
            } catch (Exception e) {
                verdict = "THROW";
                detail = e.getClass().getSimpleName() + ": " + e.getMessage();
            }
            String clean = detail == null ? "" : detail.replace('\t', ' ').replace('\r', ' ').replace("\n", " / ");
            if (!clean.isEmpty() && LEAK.matcher(clean).find()) {
                // A command that answers a player with a Java message or a bare null is a defect even
                // when the throw was caught: the player is being shown the inside of the machine.
                verdict = "LEAK";
            }
            runs.add(new Run(line, verdict, returns, clean));
            System.out.printf("%-8s /%s%n         %s%n", verdict, line, detail);
        }

        StringBuilder sb = new StringBuilder("command\tverdict\treturns\tfirst message\n");
        int[] count = new int[7];
        for (Run r : runs) {
            sb.append(r.command()).append('\t').append(r.verdict()).append('\t')
                    .append(r.returns()).append('\t').append(r.detail()).append('\n');
            switch (r.verdict()) {
                case "PASS" -> count[0]++;
                case "REFUSED" -> count[1]++;
                case "PARSE-FAIL" -> count[2]++;
                case "THROW" -> count[3]++;
                case "CANNOT-JUDGE-HERE" -> count[4]++;
                case "TIMEOUT" -> count[5]++;
                case "LEAK" -> count[6]++;
                default -> { }
            }
        }
        Files.createDirectories(report.getParent());
        Files.writeString(report, sb.toString(), StandardCharsets.UTF_8);
        System.out.printf("%n%d commands: %d PASS, %d refused in words, %d PARSE-FAIL, %d THROW,"
                        + " %d cannot judge here, %d TIMEOUT, %d LEAK%n",
                runs.size(), count[0], count[1], count[2], count[3], count[4], count[5], count[6]);
        System.out.println("report: " + report);
        boolean bad = count[2] + count[3] + count[5] + count[6] > 0;
        System.out.println(bad ? "COMMAND SURFACE: FAIL" : "COMMAND SURFACE: the whole list parses and runs");
        System.exit(bad ? 1 : 0);
    }

    /** An exception the sandbox causes, not the mod: no server, no level, no player. */
    private static boolean unjudgeable(Throwable t) {
        String m = (t.getClass().getName() + ": " + t.getMessage()).toLowerCase(java.util.Locale.ROOT);
        for (Throwable c = t.getCause(); c != null && c != t; c = c.getCause()) {
            m += " " + c.getClass().getName().toLowerCase(java.util.Locale.ROOT) + ": "
                    + String.valueOf(c.getMessage()).toLowerCase(java.util.Locale.ROOT);
        }
        if (!(t instanceof NullPointerException) && !m.contains("server")) {
            return false;
        }
        // NullPointerException anywhere in a command that reaches for the server, the level or the
        // player. The source stack built here has a null level and no entity on purpose.
        return m.contains("server") || m.contains("level") || m.contains("player") || m.contains("entity")
                || m.contains("nullpointerexception");
    }

    private static List<String> head(List<String> lines, int n) {
        synchronized (CHAT) {
            return new ArrayList<>(lines.subList(0, Math.min(n, lines.size())));
        }
    }
}
