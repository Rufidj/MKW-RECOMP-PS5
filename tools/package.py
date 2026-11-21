#!/usr/bin/env python3
"""Assemble the title folder PPSA99861/ from the build outputs. Copies no game data.

Usage: python3 tools/package.py --work DIR --out build/PPSA99861 [--sce-sys build/sce_sys] [--splash IMAGE.png]
                                [--ini config/mkw.ini] [--no-spirv]

The result is what goes to /data/homebrew/PPSA99861 on the console, next to your own exefs/ and romfs/:

  eboot.bin              the title (contains YOUR recompiled game code: personal use only, never share it)
  sce_module/libc.prx    the clean-room libc module (signed fake SELF, as built; never copy it back from the console)
  sce_sys/               param.json, icon0.png, pic0.dds/pic1.dds (tools/make_sce_sys.py)
  assets/ shaders/ licenses/ LEGAL.txt build-info.json   the port's own files and license texts
  spirv/                 the game's shaders translated to SPIR-V (from your dump: personal use only)
  romfs.index            the RomFS index (from your dump)
  mkw.ini                settings (config/mkw.ini)
  boot-splash.png        optional picture for the loading screen (--splash; your own image)
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GAME_NAMES = ('main', 'sdk', 'rtld', 'main.npdm')


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--sce-sys', type=Path, help='folder made by tools/make_sce_sys.py')
    ap.add_argument('--splash', type=Path, help='optional loading-screen picture (PNG)')
    ap.add_argument('--ini', type=Path, default=REPO / 'config/mkw.ini')
    ap.add_argument('--no-spirv', action='store_true', help='leave spirv/ out (e.g. when the console already has it)')
    args = ap.parse_args()

    work = args.work.resolve()
    dist = work / 'PS5_MKWProbe/dist/PPSA99861'
    mkw = work / 'mkw-recomp/build'
    for need in (dist / 'eboot.bin', dist / 'sce_module/libc.prx'):
        if not need.is_file():
            sys.exit(f'{need} is missing: run tools/build.py (step title) first')
    out = args.out.resolve()
    if out.exists():
        if not (out / 'eboot.bin').exists() and any(out.iterdir()):
            sys.exit(f'{out} exists and does not look like a title folder: choose another --out')
        shutil.rmtree(out)

    shutil.copytree(dist, out)
    if args.sce_sys:
        for f in args.sce_sys.iterdir():
            if f.name in ('param.json', 'icon0.png', 'pic0.dds', 'pic1.dds'):
                shutil.copy2(f, out / 'sce_sys' / f.name)
    else:
        shutil.copy2(REPO / 'config/param.json', out / 'sce_sys/param.json')
    shutil.copy2(args.ini, out / 'mkw.ini')
    if args.splash:
        shutil.copy2(args.splash, out / 'boot-splash.png')

    index = mkw / 'romfs.index'
    if index.is_file():
        shutil.copy2(index, out / 'romfs.index')
    else:
        print('warning: no romfs.index (run tools/build.py --steps romfs)')
    spirv = mkw / 'spirv'
    if not args.no_spirv:
        if not spirv.is_dir():
            sys.exit(f'{spirv} is missing: run tools/build.py --steps shaders, or pass --no-spirv')
        (out / 'spirv').mkdir()
        n = 0
        for f in spirv.iterdir():   # only what the title reads: the SPIR-V and its resource layout
            if f.name.endswith(('.spv', '.res.json')):
                shutil.copy2(f, out / 'spirv' / f.name)
                n += 1
        print(f'spirv/: {n} files')

    leaked = [p for p in out.rglob('*') if p.name in GAME_NAMES or p.name.startswith('subsdk')
              or p.suffix in ('.nso', '.nca', '.nsp', '.xci')]
    if leaked:
        sys.exit(f'refusing: game files in the title folder: {leaked[:5]}')
    files = sorted(p for p in out.rglob('*') if p.is_file())
    manifest = {p.relative_to(out).as_posix(): sha(p) for p in files if not p.relative_to(out).parts[0] == 'spirv'}
    (out.parent / (out.name + '.manifest.json')).write_text(json.dumps(manifest, indent=1) + '\n')
    size = sum(p.stat().st_size for p in files)
    print(f'{out}: {len(files)} files, {size / 2**20:.0f} MiB')
    print('Personal use only: eboot.bin, spirv/ and romfs.index are derived from your dump. Do not share them.')


if __name__ == '__main__':
    main()
