import com.eternalengine.commands.EeOperationalCheck;
import com.mojang.brigadier.CommandDispatcher;
import net.minecraft.commands.CommandSource;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.world.phys.Vec2;
import net.minecraft.world.phys.Vec3;

/** Runs /ee check sub-commands through Minecraft's real command dispatcher, as an operator with no player. */
public class CommandHarness {
    public static void main(String[] args) {
        CommandDispatcher<CommandSourceStack> d = new CommandDispatcher<>();
        d.register(Commands.literal("ee").then(EeOperationalCheck.node()));
        CommandSource chat = new CommandSource() {
            @Override public void sendSystemMessage(Component c) { System.out.println(c.getString().replaceAll("§.", "")); }
            @Override public boolean acceptsSuccess() { return true; }
            @Override public boolean acceptsFailure() { return true; }
            @Override public boolean shouldInformAdmins() { return false; }
        };
        CommandSourceStack op = new CommandSourceStack(chat, Vec3.ZERO, Vec2.ZERO, null, 4, "harness",
                Component.literal("harness"), null, null);
        CommandSourceStack player = new CommandSourceStack(chat, Vec3.ZERO, Vec2.ZERO, null, 0, "visitor",
                Component.literal("visitor"), null, null);
        for (String cmd : args) {
            boolean asPlayer = cmd.startsWith("!");
            String line = asPlayer ? cmd.substring(1) : cmd;
            System.out.println("\n>>> /" + line + (asPlayer ? "   (as a non-operator)" : ""));
            try {
                System.out.println("<<< returned " + d.execute(line, asPlayer ? player : op));
            } catch (Exception e) {
                System.out.println("<<< " + e.getClass().getSimpleName() + ": " + e.getMessage());
            }
        }
    }
}
