#!/usr/bin/env python3
"""Patch test-2 APK -> test-3: swap the launcher's bundled patched-GLFW classes jar.
Stale jar (2025-04 build) lacks LWJGL 3.4.x API (glfwPlatformSupported etc.), so MC 26.2 crashed at
GLX._initGlfw. New jar rebuilt from the port's current Pojlib source (jre_lwjgl3glfw @ a0788606,
javac --release 8, merged over the old jar: 26 classes replaced, 6 added, 0 refs missing).
Also refreshes assets/lwjgl/version (ms timestamp, same as the gradle build does).
InstallLWJGL() rewrites the jar from assets on every launch (matchingAssetFile is ref-compare,
always false), so no clean install is needed for the jar refresh."""
import zipfile, os, time

SRC = "/workspace/qcp-apk/qcp-26.2-1.0.0-q3-launcher-j25-glfw.apk"
DST = "/workspace/qcp-apk/qcp-26.2-1.0.0-q3-launcher-j25-glfw2-unsigned.apk"
NEWJAR = "/tmp/new2-glfw.jar"

newjar = open(NEWJAR, "rb").read()
ver = str(int(time.time() * 1000)).encode()
zin = zipfile.ZipFile(SRC)

zout = zipfile.ZipFile(DST, "w")
hit_jar = hit_ver = 0
for info in zin.infolist():
    name = info.filename
    if name.startswith("META-INF/") and name.upper().endswith((".RSA", ".SF", ".MF", ".DSA", ".EC")):
        continue
    data = zin.read(name)
    if name == "assets/lwjgl/lwjgl-glfw-classes.jar":
        data = newjar; hit_jar += 1
    elif name == "assets/lwjgl/version":
        data = ver; hit_ver += 1
    zi = zipfile.ZipInfo(name, date_time=info.date_time)
    zi.compress_type = info.compress_type
    zi.external_attr = info.external_attr
    zi.create_system = info.create_system
    zout.writestr(zi, data)
zout.close()
assert hit_jar == 1 and hit_ver == 1, (hit_jar, hit_ver)

z2 = zipfile.ZipFile(DST)
d = z2.read("assets/lwjgl/lwjgl-glfw-classes.jar")
assert d == newjar, "nested jar mismatch"
assert z2.read("assets/lwjgl/version") == ver
print("patch OK. nested jar bytes:", len(d), "version:", ver.decode())
