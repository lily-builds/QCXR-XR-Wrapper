#!/usr/bin/env python3
"""Patch test-4 APK -> test-5: refresh bundled lwjgl-glfw-classes jar with the test-5 build
(seeder class + bundled world zip). InstallLWJGL rewrites the jar from assets on every launch."""
import zipfile, os, time, io

SRC = "/workspace/qcp-apk/qcp-26.2-1.0.0-q3-launcher-j25-glfw2.apk"
DST = "/workspace/qcp-apk/qcp-26.2-1.0.0-q3-launcher-j25-glfw3-unsigned.apk"
NEWJAR = "/tmp/new3-glfw.jar"

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
nz = zipfile.ZipFile(io.BytesIO(d))
assert "org/lily/WorldSeeder.class" in nz.namelist()
assert "lily/one_tiny_room.zip" in nz.namelist()
assert z2.read("assets/lwjgl/version") == ver
print("patch OK. nested jar bytes:", len(d), "version:", ver.decode())
