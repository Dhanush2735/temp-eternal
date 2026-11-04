package eetest.helper;

import com.eternalengine.civilization.SettlementRank;
import com.eternalengine.entity.HumanNpcEntity;
import com.eternalengine.population.CrowdFigures;
import com.eternalengine.terrabridge.TerraCoordinateHelper;
import com.mojang.authlib.GameProfile;
import com.mojang.brigadier.arguments.DoubleArgumentType;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.LongArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.logging.LogUtils;
import net.minecraft.commands.CommandSource;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.common.util.FakePlayerFactory;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.slf4j.Logger;

import java.util.Locale;
import java.util.UUID;

/**
 * SANDBOX ONLY, NEVER SHIPPED. A tiny extra mod for worldfill/tools/run_test_server.sh (EE_TEST_HELPER=1).
 *
 * <p>The sandbox's test server has no player, so the crowd code never ran there, and the crash the user saw
 * (CrowdFigures.occupiedInChunk, 2026-10-12) was never seen in the sandbox. The sandbox's Terra++ jar also
 * cannot turn a block position into a place on Earth, so the real spawner (PresenceLocalSpawner) cannot find
 * a town in the flat test world. This helper calls the code that crashed, CrowdFigures.ensure, the way
 * PresenceLocalSpawner.tickAround calls it (every 40 ticks, for a player standing in a city), with a Forge
 * fake player at the given block, and counts what happens.
 *
 * <pre>
 *   eetest crowd start &lt;x&gt; &lt;z&gt; &lt;year&gt; &lt;population&gt;   a watcher at x z; the chunks around it are force-loaded
 *   eetest crowd startgeo &lt;lat&gt; &lt;lon&gt; &lt;year&gt; &lt;population&gt;
 *        the same at a place on Earth, and first lays one grass block in every column around it at the
 *        height Terra++ gives as the ground there (the flat test world's own ground is at y -61, where no
 *        real place is; the crowd stands where Terra++ says the ground is). Use a low place: the test
 *        world ends at y 320.
 *   eetest crowd walk &lt;dx&gt; &lt;dz&gt; &lt;cycles&gt;               move the watcher by dx dz blocks before each of the next cycles
 *   eetest crowd status                                 cycles, failures, figures standing, time per call, and
 *                                                       whether every figure can be found by its own UUID
 *   eetest crowd check                                  run "ee check all" as the watcher (a player source, permission 4)
 *   eetest crowd stop
 *   eetest player join &lt;lat&gt; &lt;lon&gt;    a fake player IN the level at a place (ground laid as for startgeo): the
 *                                     mod's own spawner, talk and crowd then run for it as for a real player
 *   eetest people                       the living townspeople around that player: names, roles, talk
 *   eetest player leave
 *   eetest as &lt;command&gt;               run a command as that player (permission 4); what it is told goes to the log
 * </pre>
 * Every result line in the log starts with [EE test helper].
 */
@Mod("eetesthelper")
public final class EeTestHelper {
    private static final Logger LOG = LogUtils.getLogger();
    private static final int PERIOD_TICKS = 40;
    private static final int FORCE_RADIUS_CHUNKS = 6;

    private static FakePlayer watcher;
    private static ServerLevel level;
    private static BlockPos heart;
    private static int year;
    private static long population;
    private static int cycles;
    private static int failures;
    private static int changedTotal;
    private static long nanosTotal;
    private static long nanosMax;
    private static String lastError = "";
    private static int walkDx;
    private static int walkDz;
    private static int walkLeft;
    private static final java.util.Set<UUID> everSeen = new java.util.HashSet<>();
    /** true: this helper calls CrowdFigures.ensure itself; false: a joined player, the mod's spawner does it. */
    private static boolean drive = true;

    public EeTestHelper() {
        MinecraftForge.EVENT_BUS.register(this);
        LOG.info("[EE test helper] loaded (sandbox test server only)");
    }

    @SubscribeEvent
    public void onCommands(RegisterCommandsEvent event) {
        // Step 18e: stand-ins for Terra++'s /terra timejump <year> and /terra timescale <n>x (the sandbox's Terra++ has no
        // time feature), the same shape as Terra++'s, so the test server can show that the mod refuses a jump back before
        // the command runs and turns timescale into /ee speed set. Only when this Terra++ has no timejump of its own.
        var terra = event.getDispatcher().getRoot().getChild("terra");
        if (terra == null || terra.getChild("timejump") == null) {
            event.getDispatcher().register(Commands.literal("terra").requires(s -> s.hasPermission(2))
                    .then(Commands.literal("timejump")
                            .then(Commands.argument("year", IntegerArgumentType.integer(-3000, 9999))
                                    .executes(c -> terraStub(c.getSource(), "timejump " + IntegerArgumentType.getInteger(c, "year")))))
                    .then(Commands.literal("timescale")
                            .then(Commands.literal("1x").executes(c -> terraStub(c.getSource(), "timescale 1x")))
                            .then(Commands.literal("10x").executes(c -> terraStub(c.getSource(), "timescale 10x")))
                            .then(Commands.literal("25x").executes(c -> terraStub(c.getSource(), "timescale 25x")))
                            .then(Commands.literal("50x").executes(c -> terraStub(c.getSource(), "timescale 50x")))));
            LOG.info("[EE test helper] stand-in /terra timejump and /terra timescale registered (this Terra++ has no time)");
        }
        event.getDispatcher().register(Commands.literal("eetest").requires(s -> s.hasPermission(4))
                .then(Commands.literal("crowd")
                        .then(Commands.literal("start")
                                .then(Commands.argument("x", IntegerArgumentType.integer())
                                        .then(Commands.argument("z", IntegerArgumentType.integer())
                                                .then(Commands.argument("year", IntegerArgumentType.integer())
                                                        .then(Commands.argument("population", LongArgumentType.longArg(1))
                                                                .executes(c -> start(c.getSource(),
                                                                        IntegerArgumentType.getInteger(c, "x"),
                                                                        IntegerArgumentType.getInteger(c, "z"),
                                                                        IntegerArgumentType.getInteger(c, "year"),
                                                                        LongArgumentType.getLong(c, "population"))))))))
                        .then(Commands.literal("startgeo")
                                .then(Commands.argument("lat", DoubleArgumentType.doubleArg(-90, 90))
                                        .then(Commands.argument("lon", DoubleArgumentType.doubleArg(-180, 180))
                                                .then(Commands.argument("year", IntegerArgumentType.integer())
                                                        .then(Commands.argument("population", LongArgumentType.longArg(1))
                                                                .executes(c -> startGeo(c.getSource(),
                                                                        DoubleArgumentType.getDouble(c, "lat"),
                                                                        DoubleArgumentType.getDouble(c, "lon"),
                                                                        IntegerArgumentType.getInteger(c, "year"),
                                                                        LongArgumentType.getLong(c, "population"))))))))
                        .then(Commands.literal("walk")
                                .then(Commands.argument("dx", IntegerArgumentType.integer(-16, 16))
                                        .then(Commands.argument("dz", IntegerArgumentType.integer(-16, 16))
                                                .then(Commands.argument("cycles", IntegerArgumentType.integer(1, 200))
                                                        .executes(c -> {
                                                            walkDx = IntegerArgumentType.getInteger(c, "dx");
                                                            walkDz = IntegerArgumentType.getInteger(c, "dz");
                                                            walkLeft = IntegerArgumentType.getInteger(c, "cycles");
                                                            LOG.info("[EE test helper] walking {} {} for {} cycles",
                                                                    walkDx, walkDz, walkLeft);
                                                            return 1;
                                                        })))))
                        .then(Commands.literal("check").executes(c -> {
                            if (watcher == null) {
                                c.getSource().sendFailure(Component.literal("[EE test helper] not started"));
                                return 0;
                            }
                            LOG.info("[EE test helper] running ee check all as the watcher");
                            c.getSource().getServer().getCommands().performPrefixedCommand(
                                    watcher.createCommandSourceStack().withPermission(4), "ee check all");
                            return 1;
                        }))
                        .then(Commands.literal("status").executes(c -> status(c.getSource())))
                        .then(Commands.literal("stop").executes(c -> stop(c.getSource()))))
                .then(Commands.literal("player")
                        .then(Commands.literal("join")
                                .then(Commands.argument("lat", DoubleArgumentType.doubleArg(-90, 90))
                                        .then(Commands.argument("lon", DoubleArgumentType.doubleArg(-180, 180))
                                                .executes(c -> join(c.getSource(),
                                                        DoubleArgumentType.getDouble(c, "lat"),
                                                        DoubleArgumentType.getDouble(c, "lon"))))))
                        .then(Commands.literal("leave").executes(c -> leave(c.getSource())))
                        .then(Commands.literal("jump")
                                .then(Commands.argument("dx", IntegerArgumentType.integer(-5000, 5000))
                                        .then(Commands.argument("dz", IntegerArgumentType.integer(-5000, 5000))
                                                .executes(c -> {
                                                    if (watcher == null) {
                                                        return 0;
                                                    }
                                                    int nx = watcher.getBlockX() + IntegerArgumentType.getInteger(c, "dx");
                                                    int nz = watcher.getBlockZ() + IntegerArgumentType.getInteger(c, "dz");
                                                    int ny = Math.max(level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, nx, nz),
                                                            TerraCoordinateHelper.getPlacementY(level, nx, nz));
                                                    watcher.moveTo(nx + 0.5, ny, nz + 0.5, watcher.getYRot(), 0.0f);
                                                    level.getChunkSource().move(watcher);
                                                    LOG.info("[EE test helper] jumped to {} {} {}", nx, ny, nz);
                                                    return 1;
                                                })))))
                .then(Commands.literal("people").executes(c -> people(c.getSource())))
                // Step 21: a jump that also lays the ground at the Terra++ height around the new place (the real game's
                // Terra++ builds that ground; the flat test world has none there), and a watch of the next cycles:
                // how many townspeople stand around the player, and why spots were refused.
                .then(Commands.literal("jumpground")
                        .then(Commands.argument("dx", IntegerArgumentType.integer(-5000, 5000))
                                .then(Commands.argument("dz", IntegerArgumentType.integer(-5000, 5000))
                                        .executes(c -> jumpGround(c.getSource(), IntegerArgumentType.getInteger(c, "dx"),
                                                IntegerArgumentType.getInteger(c, "dz"))))))
                .then(Commands.literal("refill")
                        .then(Commands.argument("cycles", IntegerArgumentType.integer(1, 100))
                                .executes(c -> {
                                    refillLeft = IntegerArgumentType.getInteger(c, "cycles");
                                    refillStart = level == null ? 0L : level.getGameTime();
                                    return 1;
                                })))
                // Step 21: the fake player walks up to the nearest crowd figure (or townsperson) and right-clicks it,
                // which holds it; "held" says what became of it; "bye" ends the talk; "mobs" counts Minecraft's own.
                .then(Commands.literal("hold")
                        .then(Commands.literal("figure").executes(c -> hold(c.getSource(), true)))
                        .then(Commands.literal("person").executes(c -> hold(c.getSource(), false))))
                .then(Commands.literal("held").executes(c -> held(c.getSource())))
                .then(Commands.literal("bye").executes(c -> bye(c.getSource())))
                .then(Commands.literal("mobs").executes(c -> mobs(c.getSource())))
                // Step 18: the fake player right-clicks the nearest townsperson (HumanNpcEntity.mobInteract).
                .then(Commands.literal("talk").executes(c -> talk(c.getSource())))
                // Step 18d: set Minecraft's day straight on the overworld, past /time, as another mod would; and the
                // calendar as it is (today, Minecraft's day, the saved part).
                .then(Commands.literal("settime")
                        .then(Commands.argument("ticks", LongArgumentType.longArg(0L))
                                .executes(c -> settime(c.getSource(), LongArgumentType.getLong(c, "ticks")))))
                .then(Commands.literal("calendar").executes(c -> calendar(c.getSource())))
                // Turn 89: time the mod's ground look-up (what the people spawner uses) against the old way, which
                // also asked the land-cover map, at count spots around a place nobody has visited yet.
                .then(Commands.literal("ground")
                        .then(Commands.argument("lat", DoubleArgumentType.doubleArg(-90, 90))
                                .then(Commands.argument("lon", DoubleArgumentType.doubleArg(-180, 180))
                                        .then(Commands.argument("count", IntegerArgumentType.integer(1, 64))
                                                .executes(c -> ground(c.getSource(),
                                                        DoubleArgumentType.getDouble(c, "lat"),
                                                        DoubleArgumentType.getDouble(c, "lon"),
                                                        IntegerArgumentType.getInteger(c, "count")))))))
                // Step 19a: a command run as the fake player (its own UUID, so its own purse), every line it is told
                // written to the log.
                .then(Commands.literal("as")
                        .then(Commands.argument("command", StringArgumentType.greedyString())
                                .executes(c -> runAs(c.getSource(), StringArgumentType.getString(c, "command"), 4))))
                // Step 22: a command run as the fake player without operator rights (what an ordinary player sees).
                .then(Commands.literal("plain")
                        .then(Commands.argument("command", StringArgumentType.greedyString())
                                .executes(c -> runAs(c.getSource(), StringArgumentType.getString(c, "command"), 0))))
                // Step 22: the history book: what the watcher carries; the first-join welcome; drop every book.
                .then(Commands.literal("book").executes(c -> book(c.getSource(), ""))
                        .then(Commands.literal("welcome").executes(c -> book(c.getSource(), "welcome")))
                        .then(Commands.literal("drop").executes(c -> book(c.getSource(), "drop"))))
                // Step 22: the nearest seller's trade list (as the talk box opens it), and buying its first book.
                .then(Commands.literal("shop").executes(c -> shop(c.getSource())))
                // Step 22: ask the nearest townsperson who sells nothing where to get something to keep notes in.
                .then(Commands.literal("notes").executes(c -> notes(c.getSource())))
                // Step 23b: the watcher's money pieces; selling a good to the nearest buyer (16 wheat given when the
                // watcher carries nothing to sell); the nearest money-changer's first offer.
                .then(Commands.literal("coins").executes(c -> coins(c.getSource())))
                .then(Commands.literal("give")
                        .then(Commands.argument("item", StringArgumentType.word())
                                .then(Commands.argument("count", IntegerArgumentType.integer(1, 2304))
                                        .executes(c -> give(c.getSource(), StringArgumentType.getString(c, "item"),
                                                IntegerArgumentType.getInteger(c, "count"))))))
                // Step 24: Minecraft's trade screen, driven on the server (a fake player has no screen).
                .then(Commands.literal("trade").executes(c -> trade(c.getSource(), "open", ""))
                        .then(Commands.literal("with")
                                .then(Commands.argument("who", StringArgumentType.word())
                                        .executes(c -> trade(c.getSource(), "open", StringArgumentType.getString(c, "who")))))
                        .then(Commands.literal("pick")
                                .then(Commands.argument("what", StringArgumentType.greedyString())
                                        .executes(c -> trade(c.getSource(), "pick", StringArgumentType.getString(c, "what")))))
                        .then(Commands.literal("put")
                                .then(Commands.argument("what", StringArgumentType.greedyString())
                                        .executes(c -> trade(c.getSource(), "put", StringArgumentType.getString(c, "what")))))
                        .then(Commands.literal("take").executes(c -> trade(c.getSource(), "take", "")))
                        .then(Commands.literal("shift").executes(c -> trade(c.getSource(), "shift", "")))
                        .then(Commands.literal("empty").executes(c -> trade(c.getSource(), "empty", "")))
                        .then(Commands.literal("show").executes(c -> trade(c.getSource(), "show", "")))
                        .then(Commands.literal("back").executes(c -> trade(c.getSource(), "back", "")))
                        .then(Commands.literal("away").executes(c -> trade(c.getSource(), "away", "")))
                        .then(Commands.literal("close").executes(c -> trade(c.getSource(), "close", "")))));
    }

    /** Step 23b: the money pieces in the watcher's inventory, stack by stack, and what they are worth. */
    private static int coins(CommandSourceStack source) {
        if (watcher == null) {
            source.sendFailure(Component.literal("[EE test helper] not started"));
            return 0;
        }
        var inv = watcher.getInventory();
        int stacks = 0;
        for (int i = 0; i < inv.getContainerSize(); i++) {
            var st = inv.getItem(i);
            if (st.getItem() instanceof com.eternalengine.money.MoneyItem) {
                stacks++;
                LOG.info("[EE test helper] coins: slot {} | {} x {} | {} | money {} | value {}", i, st.getCount(),
                        net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(st.getItem()), st.getHoverName().getString(),
                        com.eternalengine.money.MoneyItem.moneyId(st), com.eternalengine.money.MoneyItem.value(st));
            }
        }
        var purse = com.eternalengine.money.CoinPurse.of(watcher);
        int year = com.eternalengine.money.PurseService.yearNow();
        String worth = com.eternalengine.money.PurseService.holdings(com.eternalengine.money.MoneyTable.get(), purse.view(), year);
        LOG.info("[EE test helper] coins: {} stack(s): {} | worth: {}", stacks, purse.piecesLine(), worth);
        source.sendSuccess(() -> Component.literal("[EE test helper] coins: " + worth), false);
        return 1;
    }

    private static HumanNpcEntity nearestWho(java.util.function.Predicate<String> role) {
        return nearestWho(role, false);
    }

    /** The nearest living townsperson whose role fits; {@code anyTrader}: anybody who has a trade screen. */
    private static HumanNpcEntity nearestWho(java.util.function.Predicate<String> role, boolean anyTrader) {
        var near = level.getEntitiesOfClass(HumanNpcEntity.class, watcher.getBoundingBox().inflate(160.0, 256.0, 160.0),
                npc -> npc.isAlive() && !CrowdFigures.isFigure(npc) && role.test(npc.getRole())
                        && (!anyTrader || com.eternalengine.money.TradeDesk.create(watcher, npc) != null));
        near.sort(java.util.Comparator.comparingDouble(npc -> npc.distanceToSqr(watcher)));
        return near.isEmpty() ? null : near.get(0);
    }

    /** Step 24: gives the watcher items ("minecraft:wheat 16"), to sell or swap. */
    private static int give(CommandSourceStack source, String item, int count) {
        if (watcher == null) {
            source.sendFailure(Component.literal("[EE test helper] not started"));
            return 0;
        }
        var rl = net.minecraft.resources.ResourceLocation.tryParse(item.contains(":") ? item : "minecraft:" + item);
        var it = rl == null ? null : net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(rl);
        if (it == null || it == net.minecraft.world.item.Items.AIR) {
            source.sendFailure(Component.literal("[EE test helper] no item " + item));
            return 0;
        }
        int left = count;
        while (left > 0) {
            int n = Math.min(left, it.getMaxStackSize(new net.minecraft.world.item.ItemStack(it)));
            var st = new net.minecraft.world.item.ItemStack(it, n);
            watcher.getInventory().add(st);
            if (!st.isEmpty()) {
                watcher.drop(st, false);
            }
            left -= n;
        }
        LOG.info("[EE test helper] give: {} x {}", count, rl);
        source.sendSuccess(() -> Component.literal("[EE test helper] gave " + count + " " + rl), false);
        return 1;
    }

    private static String stackWords(net.minecraft.world.item.ItemStack st) {
        if (st == null || st.isEmpty()) {
            return "-";
        }
        return st.getCount() + " x " + st.getHoverName().getString();
    }

    private static String rowStack(com.eternalengine.money.TradeView.Stack st) {
        if (st == null || st.isEmpty()) {
            return "-";
        }
        String label = st.tag() != null && st.tag().contains("EeMoney") ? st.tag().getCompound("EeMoney").getString("label")
                : st.tag() != null && st.tag().contains("display") ? st.tag().getCompound("display").getString("Name") : "";
        return st.count() + " x " + st.item() + (label.isEmpty() ? "" : " (" + label + ")");
    }

    /** What the trade screen shows now: the trades (with "list"), the two slots, the result, the words, the coins. */
    private static void logTrade(String what, com.eternalengine.money.TradeMenu m, boolean list) {
        var v = m.serverView();
        if (v == null) {
            return;
        }
        if (list) {
            LOG.info("[EE test helper] trade: {} | {} | {} | {} rows | says: {}", what, v.title, v.job, v.rows.size(), v.says);
            for (int i = 0; i < v.rows.size(); i++) {
                var r = v.rows.get(i);
                LOG.info("[EE test helper] trade:   {}. {} {} | {} | {} | give {}{} + {} -> get {}{}{}{}", i + 1, r.kind(), r.id(),
                        r.name(), r.price(), rowStack(r.cost1()), r.moreCost() ? " (+more)" : "", rowStack(r.cost2()),
                        rowStack(r.result()), r.morePay() ? " (+more)" : "", r.left() >= 0 ? " | left " + r.left() : "",
                        r.owned() ? " | owned" : "");
            }
        }
        String picked = v.selected >= 0 && v.selected < v.rows.size() ? v.rows.get(v.selected).id() : "none";
        LOG.info("[EE test helper] trade: {} | picked {} | slots [{}] [{}] -> [{}] | status: {} | says: {} | {}", what, picked,
                stackWords(m.getSlot(0).getItem()), stackWords(m.getSlot(1).getItem()), stackWords(m.getSlot(2).getItem()),
                v.status, v.says, v.purse);
        LOG.info("[EE test helper] trade: {} | pieces carried: {}", what,
                com.eternalengine.money.CoinPurse.of(watcher).piecesLine());
    }

    /** Step 24: drives the trade screen of the nearest trading person on the server, as a player's clicks would. */
    private static int trade(CommandSourceStack source, String action, String arg) {
        if (watcher == null) {
            source.sendFailure(Component.literal("[EE test helper] not started"));
            return 0;
        }
        com.eternalengine.money.TradeMenu m = watcher.containerMenu instanceof com.eternalengine.money.TradeMenu tm ? tm : null;
        switch (action) {
            case "open" -> {
                if (m != null) {
                    m.removed(watcher);
                    watcher.containerMenu = watcher.inventoryMenu;
                }
                String who = arg == null ? "" : arg.toLowerCase(Locale.ROOT);
                HumanNpcEntity npc = nearestWho(r -> {
                    String role = r == null ? "" : r.toLowerCase(Locale.ROOT);
                    boolean seller = com.eternalengine.money.ShopService.sells(role);
                    boolean changer = com.eternalengine.money.MarketService.changes(role);
                    boolean buyer = com.eternalengine.money.MarketService.buyer(role);
                    return switch (who) {
                        case "seller" -> seller;
                        case "buyer" -> buyer;
                        case "changer" -> com.eternalengine.money.MarketService.MONEY_CHANGER.equals(role);
                        case "trader" -> changer;
                        case "", "any" -> seller || changer;
                        default -> role.equals(who);
                    };
                });
                if (npc == null && (who.isEmpty() || who.equals("any"))) {
                    npc = nearestWho(r -> true, true); // where people swap: anybody who swaps a little
                }
                if (npc == null) {
                    LOG.info("[EE test helper] trade: nobody to trade with ({}) within 160 blocks", who);
                    source.sendFailure(Component.literal("[EE test helper] nobody to trade with"));
                    return 0;
                }
                if (npc.distanceToSqr(watcher) > 7.0 * 7.0) {
                    watcher.teleportTo(npc.getX() + 1.5, npc.getY(), npc.getZ());
                }
                m = com.eternalengine.money.TradeMenu.openHere(watcher, npc);
                if (m == null) {
                    LOG.info("[EE test helper] trade: {} ({}) does not trade", npc.getName().getString(), npc.getRole());
                    source.sendFailure(Component.literal("[EE test helper] that person does not trade"));
                    return 0;
                }
                LOG.info("[EE test helper] trade: opened with {} ({}), {} m", npc.getName().getString(), npc.getRole(),
                        Math.round(Math.sqrt(npc.distanceToSqr(watcher))));
                logTrade("open", m, true);
            }
            case "pick" -> {
                if (m == null) {
                    source.sendFailure(Component.literal("[EE test helper] no trade screen open"));
                    return 0;
                }
                var v = m.serverView();
                int idx = -1;
                try {
                    idx = Integer.parseInt(arg.trim()) - 1;
                } catch (NumberFormatException e) {
                    for (int i = 0; v != null && i < v.rows.size(); i++) {
                        var r = v.rows.get(i);
                        if (r.id().toLowerCase(Locale.ROOT).contains(arg.toLowerCase(Locale.ROOT))
                                || r.name().toLowerCase(Locale.ROOT).contains(arg.toLowerCase(Locale.ROOT))) {
                            idx = i;
                            break;
                        }
                    }
                }
                if (idx < 0) {
                    LOG.info("[EE test helper] trade: no row for \"{}\"", arg);
                    source.sendFailure(Component.literal("[EE test helper] no such trade"));
                    return 0;
                }
                m.clickMenuButton(watcher, idx);
                logTrade("pick " + arg, m, false);
            }
            case "put" -> {
                // "put <inventory slot 0-35> <tray slot 0|1>": a whole stack, as a click on it and a click on the slot.
                if (m == null) {
                    source.sendFailure(Component.literal("[EE test helper] no trade screen open"));
                    return 0;
                }
                String[] p = arg.trim().split("\\s+");
                int inv = Integer.parseInt(p[0]);
                int tray = p.length > 1 ? Integer.parseInt(p[1]) : 0;
                int menuSlot = inv < 9 ? com.eternalengine.money.TradeMenu.USE_START + inv
                        : com.eternalengine.money.TradeMenu.INV_START + inv - 9;
                m.clicked(menuSlot, 0, net.minecraft.world.inventory.ClickType.PICKUP, watcher);
                m.clicked(tray, 0, net.minecraft.world.inventory.ClickType.PICKUP, watcher);
                if (!m.getCarried().isEmpty()) {
                    m.clicked(menuSlot, 0, net.minecraft.world.inventory.ClickType.PICKUP, watcher);
                }
                logTrade("put " + arg, m, false);
            }
            case "take" -> {
                if (m == null) {
                    source.sendFailure(Component.literal("[EE test helper] no trade screen open"));
                    return 0;
                }
                String got = stackWords(m.getSlot(2).getItem());
                m.clicked(com.eternalengine.money.TradeMenu.RESULT, 0, net.minecraft.world.inventory.ClickType.PICKUP, watcher);
                String carried = stackWords(m.getCarried());
                if (!m.getCarried().isEmpty()) {
                    watcher.getInventory().placeItemBackInInventory(m.getCarried());
                    m.setCarried(net.minecraft.world.item.ItemStack.EMPTY);
                }
                LOG.info("[EE test helper] trade: take | result was [{}] | in hand [{}]", got, carried);
                logTrade("take", m, false);
            }
            case "shift" -> {
                if (m == null) {
                    source.sendFailure(Component.literal("[EE test helper] no trade screen open"));
                    return 0;
                }
                String got = stackWords(m.getSlot(2).getItem());
                m.clicked(com.eternalengine.money.TradeMenu.RESULT, 0, net.minecraft.world.inventory.ClickType.QUICK_MOVE, watcher);
                LOG.info("[EE test helper] trade: shift | result was [{}]", got);
                logTrade("shift", m, true);
            }
            case "empty" -> {
                if (m == null) {
                    return 0;
                }
                m.clicked(0, 0, net.minecraft.world.inventory.ClickType.QUICK_MOVE, watcher);
                m.clicked(1, 0, net.minecraft.world.inventory.ClickType.QUICK_MOVE, watcher);
                logTrade("empty", m, false);
            }
            case "show" -> {
                if (m == null) {
                    source.sendFailure(Component.literal("[EE test helper] no trade screen open"));
                    return 0;
                }
                logTrade("show", m, true);
            }
            case "away" -> {
                // The player walks 20 blocks away: the server would close the screen (a fake player has no tick).
                if (m == null) {
                    return 0;
                }
                watcher.teleportTo(watcher.getX() + 20.0, watcher.getY(), watcher.getZ());
                boolean valid = m.stillValid(watcher);
                LOG.info("[EE test helper] trade: away | still valid: {}", valid);
                if (!valid) {
                    m.removed(watcher);
                    watcher.containerMenu = watcher.inventoryMenu;
                }
                LOG.info("[EE test helper] trade: away | closed: {} | pieces carried: {} | still held: {}", !valid,
                        com.eternalengine.money.CoinPurse.of(watcher).piecesLine(),
                        com.eternalengine.knowledge.TalkHold.count());
            }
            case "back", "close" -> {
                if (m == null) {
                    return 0;
                }
                if (action.equals("back")) {
                    m.backToTalk();
                }
                m.removed(watcher);
                watcher.containerMenu = watcher.inventoryMenu;
                LOG.info("[EE test helper] trade: {} | pieces carried: {} | still held: {}", action,
                        com.eternalengine.money.CoinPurse.of(watcher).piecesLine(),
                        com.eternalengine.knowledge.TalkHold.count());
            }
            default -> {
                return 0;
            }
        }
        source.sendSuccess(() -> Component.literal("[EE test helper] trade " + action + ": see the log"), false);
        return 1;
    }

    /** Step 22: the history books the watcher carries, in words. */
    private static String carried() {
        StringBuilder sb = new StringBuilder();
        var inv = watcher.getInventory();
        for (int i = 0; i < inv.getContainerSize(); i++) {
            var st = inv.getItem(i);
            if (st.getItem() instanceof com.eternalengine.news.HistoryBookItem b) {
                sb.append(sb.length() == 0 ? "" : ", ").append(b.form().id).append(" (slot ").append(i).append(')');
            }
        }
        return sb.length() == 0 ? "no history book" : sb.toString();
    }

    private static int book(CommandSourceStack source, String what) {
        if (watcher == null) {
            source.sendFailure(Component.literal("[EE test helper] not started"));
            return 0;
        }
        if (what.equals("welcome")) {
            com.eternalengine.knowledge.BookService.welcome(watcher);
        } else if (what.equals("drop")) {
            var inv = watcher.getInventory();
            for (int i = 0; i < inv.getContainerSize(); i++) {
                if (inv.getItem(i).getItem() instanceof com.eternalengine.news.HistoryBookItem) {
                    inv.setItem(i, net.minecraft.world.item.ItemStack.EMPTY);
                }
            }
        }
        String line = "book" + (what.isEmpty() ? "" : " " + what) + ": carries " + carried() + "; may read: "
                + com.eternalengine.knowledge.BookService.mayRead(watcher) + " (operator: " + watcher.hasPermissions(2) + ")";
        LOG.info("[EE test helper] {}", line);
        source.sendSuccess(() -> Component.literal("[EE test helper] " + line), false);
        return 1;
    }

    /** The nearest living townsperson (not a crowd figure) within 160 blocks that does or does not sell the book. */
    private static HumanNpcEntity nearest(boolean seller) {
        var near = level.getEntitiesOfClass(HumanNpcEntity.class, watcher.getBoundingBox().inflate(160.0, 256.0, 160.0),
                npc -> npc.isAlive() && !CrowdFigures.isFigure(npc)
                        && com.eternalengine.news.BookForms.sells(npc.getRole()) == seller);
        near.sort(java.util.Comparator.comparingDouble(npc -> npc.distanceToSqr(watcher)));
        return near.isEmpty() ? null : near.get(0);
    }

    /** The nearest seller's wares (the shop's list; buying is on the trade screen: "eetest trade"). */
    private static int shop(CommandSourceStack source) {
        if (watcher == null) {
            source.sendFailure(Component.literal("[EE test helper] not started"));
            return 0;
        }
        HumanNpcEntity npc = nearest(true);
        if (npc == null) {
            LOG.info("[EE test helper] shop: no seller within 160 blocks");
            source.sendFailure(Component.literal("[EE test helper] no seller within 160 blocks"));
            return 0;
        }
        var ctx = com.eternalengine.knowledge.TalkService.context(watcher, npc);
        var tv = com.eternalengine.money.ShopService.view(com.eternalengine.knowledge.TalkService.seller(ctx), watcher, null,
                null, false);
        LOG.info("[EE test helper] shop: {} | role {} | {} m | {} offers | says: {} | purse: {}", tv.npcName, npc.getRole(),
                Math.round(Math.sqrt(npc.distanceToSqr(watcher))), tv.offers.size(), tv.says, tv.purse);
        for (int i = 0; i < tv.offers.size(); i++) {
            var o = tv.offers.get(i);
            LOG.info("[EE test helper] shop:   {}. {} | {} | {} | {}{}", i + 1, o.id(), o.name(), o.priceText(), o.item(),
                    o.owned() ? " | owned" : "");
        }
        source.sendSuccess(() -> Component.literal("[EE test helper] shop: " + tv.npcName + ", " + tv.offers.size()
                + " offers (see the log)"), false);
        return 1;
    }

    private static int notes(CommandSourceStack source) {
        if (watcher == null) {
            source.sendFailure(Component.literal("[EE test helper] not started"));
            return 0;
        }
        HumanNpcEntity npc = nearest(false);
        if (npc == null) {
            LOG.info("[EE test helper] notes: nobody within 160 blocks who sells nothing");
            source.sendFailure(Component.literal("[EE test helper] nobody to ask"));
            return 0;
        }
        var ctx = com.eternalengine.knowledge.TalkService.context(watcher, npc);
        var opening = com.eternalengine.knowledge.TalkService.act(ctx, "topics", "", "");
        StringBuilder opts = new StringBuilder();
        for (int i = 0; i < opening.options.size(); i++) {
            opts.append(i == 0 ? "" : " / ").append(i + 1).append(' ').append(opening.options.get(i).label());
        }
        LOG.info("[EE test helper] notes: {} | role {} | {} options: {}", npc.getName().getString(), npc.getRole(),
                opening.options.size(), opts);
        var v = com.eternalengine.knowledge.TalkService.act(ctx, "topic", "notes", "");
        LOG.info("[EE test helper] notes: says: {} | hint: {} | carries {}", v.text, v.hint, carried());
        source.sendSuccess(() -> Component.literal("[EE test helper] notes: " + v.text), false);
        return 1;
    }

    /**
     * Step 19a: run a command as the watcher (a player source with permission 4). A fake player has no connection,
     * so what the command tells it is caught here and written to the log, one line each, as
     * "[EE test helper] as eetest_watcher: ...".
     */
    private static int runAs(CommandSourceStack source, String command, int permission) {
        if (watcher == null) {
            source.sendFailure(Component.literal("[EE test helper] not started"));
            return 0;
        }
        String name = watcher.getGameProfile().getName();
        CommandSource toLog = new CommandSource() {
            @Override
            public void sendSystemMessage(Component message) {
                for (String line : message.getString().split("\n")) {
                    LOG.info("[EE test helper] as {}: {}", name, line);
                }
            }

            @Override
            public boolean acceptsSuccess() {
                return true;
            }

            @Override
            public boolean acceptsFailure() {
                return true;
            }

            @Override
            public boolean shouldInformAdmins() {
                return false;
            }
        };
        LOG.info("[EE test helper] as {}: /{}", name, command);
        int result = source.getServer().getCommands().performPrefixedCommand(
                watcher.createCommandSourceStack().withSource(toLog).withPermission(permission), command);
        LOG.info("[EE test helper] as {}: /{} returned {}", name, command, result);
        return 1;
    }

    /** Step 18e: the stand-in ran, so the mod let the /terra command through. */
    private static int terraStub(CommandSourceStack source, String what) {
        LOG.info("[EE test helper] stand-in /terra {} ran (the mod let it through)", what);
        source.sendSuccess(() -> Component.literal("[EE test helper] stand-in /terra " + what + " ran"), false);
        return 1;
    }

    /** Step 18d: what another mod setting the time would do; the calendar's guard should put it right next tick. */
    private static int settime(CommandSourceStack source, long ticks) {
        ServerLevel over = source.getServer().overworld();
        long before = over.getDayTime();
        over.setDayTime(ticks);
        LOG.info("[EE test helper] settime: Minecraft's day {} (tick {}) -> {} (tick {}), past /time", before / 24000L,
                before % 24000L, ticks / 24000L, ticks % 24000L);
        source.sendSuccess(() -> Component.literal("[EE test helper] settime " + before + " -> " + ticks), false);
        return 1;
    }

    private static int calendar(CommandSourceStack source) {
        long t = source.getServer().overworld().getDayTime();
        int today = com.eternalengine.clock.WorldCalendar.today();
        String line = "today " + com.eternalengine.knowledge.KnowledgeDate.label(today) + "; Minecraft day " + (t / 24000L)
                + " tick " + (t % 24000L) + "; daylight cycle " + source.getServer().overworld().getGameRules()
                .getBoolean(net.minecraft.world.level.GameRules.RULE_DAYLIGHT) + "; " + com.eternalengine.clock.WorldCalendar.toJson()
                + "; restores " + com.eternalengine.clock.WorldCalendar.restores();
        LOG.info("[EE test helper] calendar: {}", line);
        source.sendSuccess(() -> Component.literal("[EE test helper] calendar: " + line), false);
        return 1;
    }

    private static int startGeo(CommandSourceStack source, double lat, double lon, int y0, long people) {
        int[] xz = placeAt(source, lat, lon);
        if (xz == null) {
            return 0;
        }
        drive = true;
        return start(source, xz[0], xz[1], y0, people);
    }

    /** A fake player in the level at a place: the mod's own systems treat it as a player standing there. */
    private static int join(CommandSourceStack source, double lat, double lon) {
        int[] xz = placeAt(source, lat, lon);
        if (xz == null) {
            return 0;
        }
        start(source, xz[0], xz[1], 0, 1L);
        drive = false;
        if (watcher.isRemoved()) {
            // Step 24: after "leave" the cached fake player was discarded (not alive): make it alive again, or what lies
            // in the trade screen's slots would be dropped when it closes, as for a dead player.
            try {
                java.lang.reflect.Method revive = net.minecraft.world.entity.Entity.class.getDeclaredMethod("unsetRemoved");
                revive.setAccessible(true);
                revive.invoke(watcher);
            } catch (ReflectiveOperationException | RuntimeException e) {
                LOG.info("[EE test helper] could not make the fake player alive again: {}", e.toString());
            }
        }
        level.addNewPlayer(watcher);
        String msg = String.format(Locale.ROOT, "[EE test helper] the fake player %s is in the level at %d %d %d;"
                + " level.players() = %d", watcher.getGameProfile().getName(), watcher.getBlockX(),
                watcher.getBlockY(), watcher.getBlockZ(), level.players().size());
        LOG.info(msg);
        source.sendSuccess(() -> Component.literal(msg), false);
        return 1;
    }

    private static int leave(CommandSourceStack source) {
        if (watcher != null && level != null && level.players().contains(watcher)) {
            level.removePlayerImmediately(watcher, net.minecraft.world.entity.Entity.RemovalReason.DISCARDED);
        }
        return stop(source);
    }

    /** The living townspeople (not crowd figures) within 128 blocks of the watcher. */
    /** Turn 89: the ground look-up timed, the new way first (it never touches the land-cover map), then the old. */
    private static int ground(CommandSourceStack source, double lat, double lon, int count) {
        double[] xz = TerraCoordinateHelper.fromGeo(lat, lon);
        if (xz == null) {
            LOG.info("[EE test helper] ground: no block for {}, {}", lat, lon);
            return 0;
        }
        int x0 = (int) Math.floor(xz[0]);
        int z0 = (int) Math.floor(xz[1]);
        long[] newWay = new long[2];
        long[] oldWay = new long[2];
        StringBuilder ys = new StringBuilder();
        for (int i = 0; i < count; i++) {
            int x = x0 + (i % 8) * 37;
            int z = z0 + (i / 8) * 37;
            long t0 = System.nanoTime();
            int y = TerraCoordinateHelper.getPlacementY(source.getLevel(), x, z);
            long t1 = System.nanoTime();
            newWay[0] += t1 - t0;
            newWay[1] = Math.max(newWay[1], t1 - t0);
            if (i < 6) {
                ys.append(i == 0 ? "" : " ").append(y);
            }
        }
        StringBuilder same = new StringBuilder();
        for (int i = 0; i < count; i++) {
            int x = x0 + (i % 8) * 37;
            int z = z0 + (i / 8) * 37;
            long t0 = System.nanoTime();
            var snap = TerraCoordinateHelper.probe(x, z);
            long t1 = System.nanoTime();
            oldWay[0] += t1 - t0;
            oldWay[1] = Math.max(oldWay[1], t1 - t0);
            if (i < 6) {
                same.append(i == 0 ? "" : " ").append(snap.valid() ? snap.surfaceY() + 1 : -1);
            }
        }
        String line = String.format(Locale.ROOT, "[EE test helper] ground at %.4f, %.4f, %d spots: new way %d ms in all"
                        + " (slowest %d ms), heights %s; old way with the land-cover map %d ms in all (slowest %d ms),"
                        + " heights %s", lat, lon, count, newWay[0] / 1_000_000L, newWay[1] / 1_000_000L, ys,
                oldWay[0] / 1_000_000L, oldWay[1] / 1_000_000L, same);
        LOG.info(line);
        source.sendSuccess(() -> Component.literal(line), false);
        return 1;
    }

    private static int refillLeft;
    private static long refillStart;

    /** Step 21: jump dx dz, lay the ground there as for a join, and stand on it. */
    private static int jumpGround(CommandSourceStack source, int dx, int dz) {
        if (watcher == null) {
            return 0;
        }
        int nx = watcher.getBlockX() + dx;
        int nz = watcher.getBlockZ() + dz;
        long t0 = System.nanoTime();
        layGround(level, nx, nz);
        int ny = Math.max(level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, nx, nz),
                TerraCoordinateHelper.getPlacementY(level, nx, nz));
        watcher.moveTo(nx + 0.5, ny, nz + 0.5, watcher.getYRot(), 0.0f);
        level.getChunkSource().move(watcher);
        LOG.info("[EE test helper] jumped with ground to {} {} {} ({} ms for the ground)", nx, ny, nz,
                (System.nanoTime() - t0) / 1_000_000L);
        return 1;
    }

    /** Step 21: one line of the refill watch. */
    private static void refillLine() {
        var near = level.getEntitiesOfClass(HumanNpcEntity.class, watcher.getBoundingBox().inflate(128.0, 256.0, 128.0),
                HumanNpcEntity::isAlive);
        int living = 0;
        int figures = 0;
        for (HumanNpcEntity npc : near) {
            if (CrowdFigures.isFigure(npc)) {
                figures++;
            } else {
                living++;
            }
        }
        LOG.info("[EE test helper] refill +{}s: {} townspeople and {} figures within 128 blocks | {}",
                (level.getGameTime() - refillStart) / 20L, living, figures,
                com.eternalengine.villager.PresenceLocalSpawner.lastTownCycle());
    }

    /** Step 21: the entity the watcher holds in a talk (its UUID survives a re-load, the id does not). */
    private static UUID heldUuid;
    private static double[] heldAt;

    /**
     * Step 21: walk up to the nearest crowd figure (figure) or townsperson (person), stand 2 blocks from it and
     * right-click it, as a player opening the talk.
     */
    private static int hold(CommandSourceStack source, boolean figure) {
        if (watcher == null) {
            source.sendFailure(Component.literal("[EE test helper] not started"));
            return 0;
        }
        var near = level.getEntitiesOfClass(HumanNpcEntity.class, watcher.getBoundingBox().inflate(160.0, 256.0, 160.0),
                npc -> npc.isAlive() && CrowdFigures.isFigure(npc) == figure);
        if (near.isEmpty()) {
            LOG.info("[EE test helper] hold: no {} within 160 blocks", figure ? "crowd figure" : "townsperson");
            source.sendFailure(Component.literal("[EE test helper] nobody to talk to"));
            return 0;
        }
        near.sort(java.util.Comparator.comparingDouble(npc -> npc.distanceToSqr(watcher)));
        HumanNpcEntity npc = near.get(0);
        watcher.moveTo(npc.getX() + 2.0, npc.getY(), npc.getZ(), watcher.getYRot(), 0.0f);
        level.getChunkSource().move(watcher);
        var result = npc.interact(watcher, net.minecraft.world.InteractionHand.MAIN_HAND);
        heldUuid = npc.getUUID();
        heldAt = new double[]{npc.getX(), npc.getY(), npc.getZ()};
        String line = String.format(Locale.ROOT, "[EE test helper] hold: right-clicked %s %s at %.1f %.1f %.1f, %.1f m away"
                        + " | result %s | now figure %s, townsperson %s, met %s, AI off %s, invulnerable %s | busy %s | held %d",
                figure ? "the crowd figure" : "the townsperson", npc.getName().getString(), npc.getX(), npc.getY(), npc.getZ(),
                Math.sqrt(npc.distanceToSqr(watcher)), result, CrowdFigures.isFigure(npc),
                com.eternalengine.villager.PresenceLocalSpawner.isPresenceNpc(npc),
                com.eternalengine.villager.PresenceLocalSpawner.isMet(npc), npc.isNoAi(), npc.isInvulnerable(),
                com.eternalengine.knowledge.TalkHold.busy(npc), com.eternalengine.knowledge.TalkHold.count());
        LOG.info(line);
        source.sendSuccess(() -> Component.literal(line), false);
        return 1;
    }

    /** Step 21: is the held person still there, where, and still held? */
    private static int held(CommandSourceStack source) {
        if (watcher == null || heldUuid == null) {
            source.sendFailure(Component.literal("[EE test helper] nobody held"));
            return 0;
        }
        var e = level.getEntity(heldUuid);
        String line;
        if (e instanceof HumanNpcEntity npc && npc.isAlive()) {
            double moved = Math.sqrt(npc.distanceToSqr(heldAt[0], heldAt[1], heldAt[2]));
            float face = (float) (Math.toDegrees(Math.atan2(watcher.getZ() - npc.getZ(), watcher.getX() - npc.getX()))) - 90.0f;
            float off = Math.abs(net.minecraft.util.Mth.wrapDegrees(npc.getYHeadRot() - face));
            line = String.format(Locale.ROOT, "[EE test helper] held: %s is still there, moved %.1f blocks, %.1f m from the"
                            + " player, head %.0f degrees off facing the player | figure %s, townsperson %s, met %s, year %d"
                            + " | busy %s | held %d", npc.getName().getString(), moved, Math.sqrt(npc.distanceToSqr(watcher)), off,
                    CrowdFigures.isFigure(npc), com.eternalengine.villager.PresenceLocalSpawner.isPresenceNpc(npc),
                    com.eternalengine.villager.PresenceLocalSpawner.isMet(npc),
                    npc.getPersistentData().getInt("eternalengine.presenceYear"),
                    com.eternalengine.knowledge.TalkHold.busy(npc), com.eternalengine.knowledge.TalkHold.count());
        } else {
            var memory = com.eternalengine.villager.PeopleMemory.get(level);
            line = "[EE test helper] held: " + heldUuid + " is gone from the world" + (e == null ? "" : " (dead)")
                    + "; remembered by the place: " + memory.remembers(heldUuid) + "; the people memory holds "
                    + memory.size() + " person(s) in " + memory.places().size() + " place(s)";
        }
        LOG.info(line);
        String l = line;
        source.sendSuccess(() -> Component.literal(l), false);
        return 1;
    }

    /** Step 21: the watcher says goodbye (closes the talk). */
    private static int bye(CommandSourceStack source) {
        if (watcher == null) {
            return 0;
        }
        com.eternalengine.knowledge.TalkService.forget(watcher.getUUID());
        LOG.info("[EE test helper] bye: the talk is over; held {}", com.eternalengine.knowledge.TalkHold.count());
        return 1;
    }

    /** Step 21: Minecraft's own mobs within 128 blocks of the watcher, by kind. */
    private static int mobs(CommandSourceStack source) {
        if (watcher == null) {
            return 0;
        }
        var all = level.getEntitiesOfClass(net.minecraft.world.entity.Mob.class, watcher.getBoundingBox().inflate(128.0, 256.0, 128.0),
                m -> !(m instanceof HumanNpcEntity));
        java.util.Map<String, Integer> byType = new java.util.TreeMap<>();
        int monsters = 0;
        for (var m : all) {
            byType.merge(net.minecraft.world.entity.EntityType.getKey(m.getType()).getPath(), 1, Integer::sum);
            if (m.getType().getCategory() == net.minecraft.world.entity.MobCategory.MONSTER) {
                monsters++;
            }
        }
        String line = String.format(Locale.ROOT, "[EE test helper] mobs: %d Minecraft mobs within 128 blocks, %d of them"
                        + " monsters; by type %s | difficulty %s, day time %d, %s", all.size(), monsters, byType,
                level.getDifficulty(), level.getDayTime() % 24000L,
                com.eternalengine.population.MinecraftMobs.stoppedLine());
        LOG.info(line);
        source.sendSuccess(() -> Component.literal(line), false);
        return 1;
    }

    private static int people(CommandSourceStack source) {
        if (watcher == null) {
            source.sendFailure(Component.literal("[EE test helper] not started"));
            return 0;
        }
        var living = level.getEntitiesOfClass(HumanNpcEntity.class, watcher.getBoundingBox().inflate(128.0, 256.0, 128.0),
                npc -> !CrowdFigures.isFigure(npc) && npc.isAlive());
        java.util.Map<String, Integer> byCiv = new java.util.TreeMap<>();
        for (HumanNpcEntity npc : living) {
            byCiv.merge(String.valueOf(npc.getCivilizationId()), 1, Integer::sum);
        }
        LOG.info("[EE test helper] people: {} living townspeople within 128 blocks; by civilization {}", living.size(),
                byCiv);
        living.sort(java.util.Comparator.comparingDouble(npc -> npc.distanceToSqr(watcher)));
        for (int i = 0; i < Math.min(60, living.size()); i++) {
            HumanNpcEntity npc = living.get(i);
            LOG.info("[EE test helper] person: {} | role {} | civ {} | era {} | {} | skin {} | {} m | says: {}",
                    npc.getName().getString(), npc.getRole(), npc.getCivilizationId(), npc.getEra(), npc.getGender(),
                    npc.getSkinId(), Math.round(Math.sqrt(npc.distanceToSqr(watcher))),
                    npc.isSpeaking() ? npc.getSpeechText() : "-");
        }
        source.sendSuccess(() -> Component.literal("[EE test helper] " + living.size() + " living townspeople"), false);
        return 1;
    }

    /**
     * Step 18: the fake player right-clicks the nearest townsperson, as a player would. A fake player has no
     * connection, so it gets the speech bubble (and the chat line) instead of the talk screen.
     */
    private static int talk(CommandSourceStack source) {
        if (watcher == null) {
            source.sendFailure(Component.literal("[EE test helper] not started"));
            return 0;
        }
        var living = level.getEntitiesOfClass(HumanNpcEntity.class, watcher.getBoundingBox().inflate(160.0, 256.0, 160.0),
                npc -> !CrowdFigures.isFigure(npc) && npc.isAlive());
        if (living.isEmpty()) {
            source.sendFailure(Component.literal("[EE test helper] no townsperson within 160 blocks"));
            return 0;
        }
        living.sort(java.util.Comparator.comparingDouble(npc -> npc.distanceToSqr(watcher)));
        HumanNpcEntity npc = living.get(0);
        var result = npc.interact(watcher, net.minecraft.world.InteractionHand.MAIN_HAND);
        String said = npc.isSpeaking() ? npc.getSpeechText() : "-";
        LOG.info("[EE test helper] talk: right-clicked {} | role {} | {} m | result {} | says: {}", npc.getName().getString(),
                npc.getRole(), Math.round(Math.sqrt(npc.distanceToSqr(watcher))), result, said);
        source.sendSuccess(() -> Component.literal("[EE test helper] " + npc.getName().getString() + " says: " + said), false);
        return 1;
    }

    /** The block whose toGeo is the place, with grass laid at the Terra++ ground height around it. */
    private static int[] placeAt(CommandSourceStack source, double lat, double lon) {
        ServerLevel lvl = source.getServer().overworld();
        double[] xz = TerraCoordinateHelper.fromGeo(lat, lon);
        if (xz == null) {
            source.sendFailure(Component.literal("[EE test helper] Terra++ cannot place " + lat + ", " + lon));
            return null;
        }
        // The sandbox's older Terra++ jar has two projections that disagree: its public fromGeo is not the
        // inverse of the generator's toGeo, which is what the mod reads positions with. Find the block whose
        // toGeo is the place (Newton steps with a numeric Jacobian), so the watcher stands where the mod thinks.
        double bx0 = xz[0];
        double bz0 = xz[1];
        for (int it = 0; it < 40; it++) {
            var g = TerraCoordinateHelper.toGeoPoint((int) Math.floor(bx0), (int) Math.floor(bz0));
            if (g == null) {
                break;
            }
            double eLat = lat - g.latitude();
            double eLon = lon - g.longitude();
            if (Math.abs(eLat) < 2e-5 && Math.abs(eLon) < 2e-5) {
                break;
            }
            double h = 512.0;
            var gx = TerraCoordinateHelper.toGeoPoint((int) Math.floor(bx0 + h), (int) Math.floor(bz0));
            var gz = TerraCoordinateHelper.toGeoPoint((int) Math.floor(bx0), (int) Math.floor(bz0 + h));
            if (gx == null || gz == null) {
                break;
            }
            double a11 = (gx.latitude() - g.latitude()) / h;
            double a12 = (gz.latitude() - g.latitude()) / h;
            double a21 = (gx.longitude() - g.longitude()) / h;
            double a22 = (gz.longitude() - g.longitude()) / h;
            double det = a11 * a22 - a12 * a21;
            if (det == 0.0) {
                break;
            }
            double dx = (a22 * eLat - a12 * eLon) / det;
            double dz = (-a21 * eLat + a11 * eLon) / det;
            double len = Math.hypot(dx, dz);
            if (len > 1_500_000.0) {
                dx *= 1_500_000.0 / len;
                dz *= 1_500_000.0 / len;
            }
            bx0 += dx;
            bz0 += dz;
        }
        int x = (int) Math.floor(bx0);
        int z = (int) Math.floor(bz0);
        var check = TerraCoordinateHelper.toGeoPoint(x, z);
        LOG.info("[EE test helper] {}, {}: the mod reads block {} {} as {}", lat, lon, x, z,
                check == null ? "nothing" : String.format(Locale.ROOT, "%.4f, %.4f", check.latitude(), check.longitude()));
        String msg = String.format(Locale.ROOT, "[EE test helper] %.4f, %.4f is block %d %d; %s", lat, lon, x, z,
                layGround(lvl, x, z));
        LOG.info(msg);
        source.sendSuccess(() -> Component.literal(msg), false);
        return new int[] {x, z};
    }

    /** Lays one grass block in every column of the 13 x 13 chunks around x z at the Terra++ ground height. */
    private static String layGround(ServerLevel lvl, int x, int z) {
        int cx = x >> 4;
        int cz = z >> 4;
        for (int dx = -FORCE_RADIUS_CHUNKS; dx <= FORCE_RADIUS_CHUNKS; dx++) {
            for (int dz = -FORCE_RADIUS_CHUNKS; dz <= FORCE_RADIUS_CHUNKS; dz++) {
                lvl.getChunk(cx + dx, cz + dz); // generated now, so the ground can be laid
            }
        }
        long t0 = System.nanoTime();
        int laid = 0;
        int minY = Integer.MAX_VALUE;
        int maxY = Integer.MIN_VALUE;
        int reach = FORCE_RADIUS_CHUNKS * 16;
        BlockPos.MutableBlockPos at = new BlockPos.MutableBlockPos();
        for (int bx = (cx << 4) - reach; bx < (cx << 4) + 16 + reach; bx++) {
            for (int bz = (cz << 4) - reach; bz < (cz << 4) + 16 + reach; bz++) {
                int y = TerraCoordinateHelper.getPlacementY(lvl, bx, bz) - 1;
                if (y < lvl.getMinBuildHeight() || y >= lvl.getMaxBuildHeight() - 3) {
                    continue;
                }
                lvl.setBlock(at.set(bx, y, bz), Blocks.GRASS_BLOCK.defaultBlockState(), 2);
                laid++;
                minY = Math.min(minY, y);
                maxY = Math.max(maxY, y);
            }
        }
        return String.format(Locale.ROOT, "laid %,d grass blocks at the Terra++ ground height (y %d..%d) in %.1f s",
                laid, minY, maxY, (System.nanoTime() - t0) / 1e9);
    }

    private static int start(CommandSourceStack source, int x, int z, int y0, long people) {
        level = source.getServer().overworld();
        int cx = x >> 4;
        int cz = z >> 4;
        for (int dx = -FORCE_RADIUS_CHUNKS; dx <= FORCE_RADIUS_CHUNKS; dx++) {
            for (int dz = -FORCE_RADIUS_CHUNKS; dz <= FORCE_RADIUS_CHUNKS; dz++) {
                level.setChunkForced(cx + dx, cz + dz, true);
            }
        }
        int ground = Math.max(level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z),
                TerraCoordinateHelper.getPlacementY(level, x, z));
        watcher = FakePlayerFactory.get(level, new GameProfile(
                UUID.fromString("0e7e57e5-0000-4000-8000-00000000c0de"), "eetest_watcher"));
        watcher.moveTo(x + 0.5, ground, z + 0.5, 0.0f, 0.0f);
        heart = new BlockPos(x, ground, z);
        year = y0;
        population = people;
        cycles = 0;
        failures = 0;
        changedTotal = 0;
        nanosTotal = 0L;
        nanosMax = 0L;
        lastError = "";
        String msg = String.format(Locale.ROOT, "[EE test helper] watcher at %d %d %d (chunk %d %d), year %d,"
                + " %,d people; %d chunks force-loaded; CrowdFigures.ensure every %d ticks", x, ground, z, cx, cz,
                year, population, (2 * FORCE_RADIUS_CHUNKS + 1) * (2 * FORCE_RADIUS_CHUNKS + 1), PERIOD_TICKS);
        LOG.info(msg);
        source.sendSuccess(() -> Component.literal(msg), false);
        return 1;
    }

    @SubscribeEvent
    public void onTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || watcher == null || level == null
                || level.getGameTime() % PERIOD_TICKS != 0) {
            return;
        }
        if (walkLeft > 0) {
            int nx = watcher.getBlockX() + walkDx;
            int nz = watcher.getBlockZ() + walkDz;
            int ny = Math.max(level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, nx, nz),
                    TerraCoordinateHelper.getPlacementY(level, nx, nz));
            watcher.moveTo(nx + 0.5, ny, nz + 0.5, watcher.getYRot(), 0.0f);
            if (!drive) {
                level.getChunkSource().move(watcher); // what a real player's move packet does: chunks follow
            }
            walkLeft--;
        }
        if (refillLeft > 0) {
            refillLeft--;
            refillLine();
        }
        if (!drive) {
            return; // a joined player: the mod's own spawner runs for it
        }
        long t0 = System.nanoTime();
        try {
            changedTotal += CrowdFigures.ensure(level, watcher, heart, SettlementRank.CITY, population, 6.0d, year,
                    64.0d);
        } catch (Throwable t) {
            failures++;
            lastError = t.toString();
            if (failures == 1) {
                LOG.error("[EE test helper] CrowdFigures.ensure failed", t);
            } else {
                LOG.error("[EE test helper] CrowdFigures.ensure failed again ({}x): {}", failures, lastError);
            }
        }
        long dt = System.nanoTime() - t0;
        cycles++;
        nanosTotal += dt;
        nanosMax = Math.max(nanosMax, dt);
        if (cycles % 5 == 0) {
            LOG.info(line());
        }
    }

    private static int status(CommandSourceStack source) {
        String msg = line();
        LOG.info(msg);
        source.sendSuccess(() -> Component.literal(msg), false);
        return 1;
    }

    private static String line() {
        if (watcher == null) {
            return "[EE test helper] not started";
        }
        var figures = level.getEntitiesOfClass(HumanNpcEntity.class, new AABB(heart).inflate(160.0, 4096.0, 160.0),
                CrowdFigures::isFigure);
        int standing = figures.size();
        java.util.Set<UUID> ids = new java.util.HashSet<>();
        int lost = 0;
        for (HumanNpcEntity f : figures) {
            ids.add(f.getUUID());
            everSeen.add(f.getUUID());
            if (level.getEntity(f.getUUID()) != f) {
                lost++; // the level cannot find this figure by its own UUID: its index is stale
            }
        }
        String index = String.format(Locale.ROOT, "; %d distinct UUIDs, %d figures the level cannot find by their"
                + " own UUID, %d different figures seen so far", ids.size(), lost, everSeen.size());
        return String.format(Locale.ROOT, "[EE test helper] cycles %d, failures %d, figures standing %d, stood up or"
                        + " moved %d, CrowdFigures.ensure %.1f ms on average, %.1f ms at most; server %.1f ms per tick%s",
                cycles, failures, standing, changedTotal, cycles == 0 ? 0.0 : nanosTotal / 1e6 / cycles,
                nanosMax / 1e6, level.getServer().getAverageTickTime(),
                lastError.isEmpty() ? "" : ", last error: " + lastError) + index
                + String.format(Locale.ROOT, "; watcher at %d %d", watcher.getBlockX(), watcher.getBlockZ());
    }

    private static int stop(CommandSourceStack source) {
        if (watcher != null && level != null) {
            int cx = heart.getX() >> 4;
            int cz = heart.getZ() >> 4;
            for (int dx = -FORCE_RADIUS_CHUNKS; dx <= FORCE_RADIUS_CHUNKS; dx++) {
                for (int dz = -FORCE_RADIUS_CHUNKS; dz <= FORCE_RADIUS_CHUNKS; dz++) {
                    level.setChunkForced(cx + dx, cz + dz, false);
                }
            }
        }
        String msg = line() + " -- stopped";
        LOG.info(msg);
        watcher = null;
        source.sendSuccess(() -> Component.literal(msg), false);
        return 1;
    }
}
