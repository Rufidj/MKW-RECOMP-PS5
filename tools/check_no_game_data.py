#!/usr/bin/env python3
"""Refuse commits that would add game data, build outputs or private data (used by tools/hooks/pre-commit).

Usage: python3 tools/check_no_game_data.py [FILES...]   (no FILES: the files staged for commit)
"""
import re
import subprocess
import sys
from pathlib import Path

BANNED_NAMES = {'eboot.bin', 'main', 'sdk', 'rtld', 'main.npdm', 'romfs.index', 'boot-splash.png', 'icon0.png'}
BANNED_SUFFIX = {'.nso', '.nca', '.nsp', '.xci', '.nup', '.nx', '.elf', '.self', '.prx', '.spv', '.dds', '.bin',
                 '.bfsha', '.sharcb', '.bars', '.bwav', '.szs', '.zs', '.bntx', '.byml', '.sarc', '.msbt'}
BANNED_DIRS = ('romfs/', 'exefs/', 'spirv/', 'build/', 'work/', 'dist/')
PRIVATE = re.compile(rb'(?:192\.168|10\.\d+)\.\d+\.\d+|[\w.+-]+@(?:gmail|hotmail|outlook|yahoo)\.\w+|/home/[a-z][\w.-]*/')
MAX_BYTES = 2 * 1024 * 1024


def main():
    files = sys.argv[1:] or subprocess.check_output(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR'], text=True).split()
    bad = []
    for f in files:
        p = Path(f)
        if p.name in BANNED_NAMES or p.name.startswith('subsdk') or p.suffix.lower() in BANNED_SUFFIX \
                or any(f.startswith(d) or f'/{d}' in f for d in BANNED_DIRS):
            bad.append(f'{f}: game data or build output')
            continue
        if not p.is_file():
            continue
        data = p.read_bytes()
        if len(data) > MAX_BYTES and not f.startswith('patches/'):
            bad.append(f'{f}: larger than 2 MiB')
        hit = PRIVATE.search(data)
        if hit:
            bad.append(f'{f}: private data ({hit.group().decode(errors="replace")})')
    if bad:
        print('Commit refused (LEGAL.md: no game data, no builds, no private data):', *bad, sep='\n  ')
        sys.exit(1)


if __name__ == '__main__':
    main()
