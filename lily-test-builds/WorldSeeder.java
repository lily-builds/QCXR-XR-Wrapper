package org.lily;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/**
 * Lily's world seeder (launcher build test-5).
 *
 * Runs from the GLFW shim jar's static init at game boot, i.e. before the
 * singleplayer world list is ever read. Plants the bundled starter world
 * ("one_tiny_room") into this instance's saves/ exactly once.
 *
 * - skips when the world is already there;
 * - writes a marker file, so a player who deletes the world does not get it back;
 * - never throws: any failure prints to stdout (the launcher log) and the game boots on.
 */
public final class WorldSeeder {
    private static final String ZIP_RES = "/lily/one_tiny_room.zip";
    private static final String WORLD_NAME = "one_tiny_room";
    private static final String MARKER_NAME = ".lily_world_seeded";

    private WorldSeeder() {
    }

    public static void run() {
        try {
            System.out.println("[lily-seed] checking this instance for the starter world...");
            File gameDir = findGameDir();
            if (gameDir == null) {
                System.out.println("[lily-seed] no instance dir found (user.home/user.dir); nothing to do");
                return;
            }
            File saves = new File(gameDir, "saves");
            File world = new File(saves, WORLD_NAME);
            File marker = new File(saves, MARKER_NAME);

            if (marker.exists()) {
                System.out.println("[lily-seed] seeded on an earlier launch; skip");
                return;
            }
            if (world.exists()) {
                writeMarker(marker);
                System.out.println("[lily-seed] world already present; marked done");
                return;
            }

            InputStream in = WorldSeeder.class.getResourceAsStream(ZIP_RES);
            if (in == null) {
                System.out.println("[lily-seed] bundled world zip missing from jar; skip");
                return;
            }
            int files;
            try {
                files = extract(in, saves);
            } finally {
                in.close();
            }
            writeMarker(marker);
            System.out.println("[lily-seed] planted '" + WORLD_NAME + "' in " + saves + " (" + files + " files). It is in the world list now.");
        } catch (Throwable t) {
            System.out.println("[lily-seed] failed (harmless, game continues): " + t);
            t.printStackTrace(System.out);
        }
    }

    /**
     * The launcher sets -Duser.home to the instance dir and chdir()s into it before
     * starting the JVM, so user.home / user.dir / "." are the candidates. Accept the
     * first one that looks like an actual instance.
     */
    private static File findGameDir() {
        String home = System.getProperty("user.home");
        String dir = System.getProperty("user.dir");
        String[] candidates = new String[] { home, dir, "." };
        for (int i = 0; i < candidates.length; i++) {
            String c = candidates[i];
            if (c == null || c.length() == 0) {
                continue;
            }
            try {
                File f = new File(c);
                boolean looksLikeInstance = f.isDirectory()
                        && (new File(f, "mods").isDirectory()
                        || new File(f, "libraries").isDirectory()
                        || new File(f, "options.txt").isFile());
                if (looksLikeInstance) {
                    System.out.println("[lily-seed] instance dir: " + c + " (" + f.getAbsolutePath() + ")");
                    return f;
                }
            } catch (Throwable ignored) {
            }
        }
        return null;
    }

    private static int extract(InputStream in, File saves) throws Exception {
        if (!saves.isDirectory()) {
            if (!saves.mkdirs() && !saves.isDirectory()) {
                throw new IllegalStateException("cannot create " + saves);
            }
        }
        String savesRoot = saves.getCanonicalPath();
        ZipInputStream zip = new ZipInputStream(new BufferedInputStream(in));
        int count = 0;
        try {
            ZipEntry entry;
            byte[] buffer = new byte[8192];
            while ((entry = zip.getNextEntry()) != null) {
                String name = entry.getName();
                if (name.length() == 0 || name.startsWith("/") || name.contains("..")) {
                    continue;
                }
                File out = new File(saves, name);
                String canon = out.getCanonicalPath();
                if (!canon.equals(savesRoot) && !canon.startsWith(savesRoot + File.separator)) {
                    continue;
                }
                if (entry.isDirectory()) {
                    out.mkdirs();
                    continue;
                }
                File parent = out.getParentFile();
                if (parent != null && !parent.isDirectory()) {
                    parent.mkdirs();
                }
                OutputStream os = new FileOutputStream(out);
                try {
                    int n;
                    while ((n = zip.read(buffer)) > 0) {
                        os.write(buffer, 0, n);
                    }
                } finally {
                    os.close();
                }
                count++;
                zip.closeEntry();
            }
        } finally {
            zip.close();
        }
        return count;
    }

    private static void writeMarker(File marker) {
        try {
            File parent = marker.getParentFile();
            if (parent != null && !parent.isDirectory()) {
                parent.mkdirs();
            }
            FileOutputStream fos = new FileOutputStream(marker);
            try {
                fos.write(("seeded by Lily's launcher build (one tiny room).\n"
                        + "delete this file if you ever want the launcher to re-plant the world.\n").getBytes("UTF-8"));
            } finally {
                fos.close();
            }
        } catch (Throwable t) {
            System.out.println("[lily-seed] marker write failed: " + t);
        }
    }
}
