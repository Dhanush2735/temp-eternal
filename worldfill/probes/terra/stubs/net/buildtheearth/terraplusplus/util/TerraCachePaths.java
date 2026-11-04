package net.buildtheearth.terraplusplus.util;

// STUB for the step-31 harness only.
// The real class resolves the Minecraft game directory through Forge's FMLPaths,
// which needs a Forge build. The harness never reads or writes the OSM disk
// cache (it parses Overpass JSON fetched beforehand), so the cache root just
// points at a scratch directory.
import java.nio.file.Path;
import java.nio.file.Paths;

public final class TerraCachePaths {
    private TerraCachePaths() {}

    public static Path root() {
        return Paths.get(System.getProperty("java.io.tmpdir"), "terra_probe_cache");
    }

    public static Path dir(String... sub) {
        Path p = root();
        for (String s : sub) p = p.resolve(s);
        return p;
    }
}
