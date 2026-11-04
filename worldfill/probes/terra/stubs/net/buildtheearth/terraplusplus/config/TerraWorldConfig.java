package net.buildtheearth.terraplusplus.config;

// STUB for the step-31 harness only.
//
// The real TerraWorldConfig is a Forge/Lombok config class; it cannot be
// compiled outside a Minecraft/Forge build. The eight fields below are the
// ONLY members of it that OsmStructureIndex and OhmStructureIndex touch
// (grep: "config.<field>" over both files), so this stub compiles the real
// index sources unchanged. All switches are ON, which is the game default.
public final class TerraWorldConfig {

    public final boolean buildings   = true;
    public final boolean roads       = true;
    public final boolean railways    = true;
    public final boolean bridges     = true;
    public final boolean walls       = true;
    public final boolean gardens     = true;
    public final boolean landuse     = true;
    public final boolean streetLights = true;

    public TerraWorldConfig() {
    }
}
