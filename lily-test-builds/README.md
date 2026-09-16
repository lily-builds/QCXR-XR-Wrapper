# Lily's test-build recipes (Quest 3 launcher line)

Scripts behind the `q3-launcher-test-N` APKs on this fork's releases.

- `WorldSeeder.java` - test-5: plants the bundled starter world into the launched instance's
  `saves/` on boot. Hooked from the GLFW shim jar's static initializer, so it runs inside the game
  JVM at window setup, before the world list is read. Idempotent (marker file), never throws.
- `build_seed_jar.py` - assembles the test-5 `lwjgl-glfw-classes.jar` (shim classes + Pojlib libs +
  `lily/one_tiny_room.zip` resource).
- `patch_seed.py` - swaps the rebuilt shim jar into the base APK and bumps `assets/lwjgl/version`.
- `patch_test4.py` - the earlier (test-4) version of the same swap.

The world zip itself ships in the `lily-builds/one-tiny-room` v1 release (281,185 B,
sha256 0bc13289dc09d0e815af07fab15973220241a1d69a08c0cbe9dd32cd47f44d72).

Build recipe (sandbox, JDK 25):

1. `javac --release 8` WorldSeeder.java + `jre_lwjgl3glfw`'s GLFW.java into the shim classes dir
2. `python3 build_seed_jar.py` -> `lwjgl-glfw-classes.jar`
3. `python3 patch_seed.py` -> unsigned APK
4. `zipalign -f -p 4`; `apksigner sign` (v2 only)
