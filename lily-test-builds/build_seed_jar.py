#!/usr/bin/env python3
"""Build the test-5 lwjgl-glfw-classes jar:
shim classes (incl. Lily's WorldSeeder) + current Pojlib libs + the bundled one_tiny_room world zip.
Same merge semantics as build_lwjgl_jar.py (the test-4 full rebuild), plus the jar resource."""
import zipfile, os
from collections import Counter

SHIM = '/tmp/glfw-build'
LIBS = '/workspace/pojlib/jre_lwjgl3glfw/libs'
OUT = '/tmp/new3-glfw.jar'
WORLD = '/workspace/first-room/one_tiny_room.zip'
EXCL = ['net/java/openjdk/cacio/ctc/', 'META-INF/versions/']

def excluded(n): return any(n.startswith(e) for e in EXCL)

shim = []
for root, _, files in os.walk(SHIM):
    for f in sorted(files):
        if f.endswith('.class'):
            rel = os.path.relpath(os.path.join(root, f), SHIM)
            if rel.startswith('net/java/openjdk/cacio/ctc/'): continue
            shim.append((rel, open(os.path.join(root, f), 'rb').read()))
shim.sort()
assert any(rel == 'org/lily/WorldSeeder.class' for rel, _ in shim), 'WorldSeeder not compiled!'
assert any(rel == 'org/lwjgl/glfw/GLFW.class' for rel, _ in shim), 'GLFW class missing!'

oldman = zipfile.ZipFile('/tmp/jarcheck/ship-glfw.jar').read('META-INF/MANIFEST.MF')
seen = set(); entries = [('META-INF/MANIFEST.MF', oldman, zipfile.ZIP_DEFLATED, (2025, 1, 15, 10, 21, 0))]
seen.add('META-INF/MANIFEST.MF')
for rel, data in shim:
    entries.append((rel, data, zipfile.ZIP_DEFLATED, (2026, 9, 16, 0, 0, 0))); seen.add(rel)

dups = []
for j in sorted(os.listdir(LIBS)):
    if not j.endswith('.jar'): continue
    z = zipfile.ZipFile(os.path.join(LIBS, j))
    for info in z.infolist():
        n = info.filename
        if excluded(n): continue
        if n in seen:
            if not n.endswith('/'): dups.append((j, n))
            continue
        seen.add(n)
        entries.append((n, z.read(n), info.compress_type, info.date_time))

world = open(WORLD, 'rb').read()
entries.append(('lily/one_tiny_room.zip', world, zipfile.ZIP_DEFLATED, (2026, 9, 16, 0, 0, 0)))

print('shim classes:', len(shim), '| total entries:', len(entries), '| file dupes skipped:', len(dups))
print('dupes by jar:', Counter([d[0] for d in dups]).most_common())
print('sample dupes:', dups[:10])

with zipfile.ZipFile(OUT, 'w') as z:
    for name, data, ct, dt in entries:
        zi = zipfile.ZipInfo(name, dt); zi.compress_type = ct
        z.writestr(zi, data)
print('written:', OUT, os.path.getsize(OUT))
with zipfile.ZipFile(OUT) as z:
    names = z.namelist()
    print('lily entries:', [n for n in names if n.startswith('lily/')])
    print('WorldSeeder.class present:', 'org/lily/WorldSeeder.class' in names)
    print('GLFW.class size:', z.getinfo('org/lwjgl/glfw/GLFW.class').file_size)
    print('world zip size in jar:', z.getinfo('lily/one_tiny_room.zip').file_size)
