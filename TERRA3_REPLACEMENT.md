# Terra++ source replacement

On 3 November 2026 the existing `terra3/` folder was replaced with a verified source snapshot from `https://github.com/Dhanush2735/terra3.git`, branch `main`, commit `e6e79dc4f6363c8bd67103eecc16a8801174b2bc`.

The 249 ordinary files in the snapshot were byte-identical to the old folder. The other 54 tracked files are old `javac.*.args` compiler-invocation files; they also matched the old folder's lossless archive. To stay under the workspace storage guard they remain in `terra3/legacy_javac_args.tar.xz`, with a hash manifest, rather than being expanded. This is a source snapshot, **not a Git checkout**: `.git` is not present, so it cannot `git pull` without recloning or initializing a repository. No source-code changes were made to Terra++.

Eternal Engine's `build.gradle` still uses the existing `eternal/libs/terraplusplus-2.0.0-alpha.jar` (SHA-256 `814310a78240e2aaf7f2aac840b6d5a08051a7f1f636efde102a5d258dab48bf`). It was not replaced, and its provenance relative to that commit has not been established. The source snapshot therefore does **not** prove the game is running a newly built version of the repository.

A build was attempted using Java 17 and `bash gradlew jarJar --no-daemon --max-workers=1`, with a 768 MB Gradle heap. It reached Forge MCP setup and the `rename` step, then the Gradle daemon disappeared unexpectedly. The cause was not established. No replacement JAR was produced, and no game or compatibility test was performed. The repository specifies Minecraft 1.20.1 and Forge 47.4.10; Eternal specifies Minecraft 1.20.1 and Forge 47.2.0, so compatibility must be verified rather than assumed. A successful build followed by controlled replacement, integration checks and live testing remain necessary.
