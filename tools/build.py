#!/usr/bin/env python3
"""Build the PS5 title from the patched sources and YOUR OWN dump. Runs the steps of docs/BUILD.md in order.

Usage: python3 tools/build.py --work DIR --stack STACK --exefs DUMP/exefs --romfs DUMP/romfs [--jobs N]
                              [--steps deps,game,title,shaders,romfs,tests]

  --work    the folder tools/setup.py filled (mkw-recomp, PS5_PayloadSDK, PS5_VulkanBuild, PS5_MKWProbe)
  --stack   Mihawk-99's PS5 Vulkan stack, set up by its own instructions (docs/BUILD.md, step 1): it must hold
            PS5_Vulkan/tooling/prospero-clang18, PS5_VulkanTemplate/.deps/native/ps5-payload-sdk and
            PS5_VulkanTemplate/external
  --exefs   your decrypted ExeFS (main, sdk, subsdk*), Mario Kart World 1.0.0
  --romfs   your decrypted RomFS

Steps (all outputs stay under DIR/*/build and DIR/PS5_MKWProbe/dist, never in this repository):
  deps     pinned VMA/xxHash headers, native zstd, Opus and libvpx for the PS5      (tools/build/ps5_deps.py --codecs)
  game     recompile the game's code to C and cross-compile it (-O2; ~25 min at -j6) (tools/build/ps5_game.py)
  title    compile the runtime and link eboot.bin + sce_module/libc.prx              (tools/build/ps5_boot.py --link)
  shaders  extract the game's shaders and translate them to SPIR-V (needs the SM86 spec, see docs/BUILD.md)
  romfs    index the RomFS (romfs.index)
  tests    the 26 PS5 host checks
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

STEPS = ['deps', 'game', 'title', 'shaders', 'romfs', 'tests']


def run(cmd, cwd, env=None):
    print('\n+', ' '.join(map(str, cmd)), flush=True)
    subprocess.run(list(map(str, cmd)), cwd=cwd, check=True, env=env)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--stack', type=Path, required=True)
    ap.add_argument('--exefs', type=Path)
    ap.add_argument('--romfs', type=Path)
    ap.add_argument('--jobs', type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument('--steps', default=','.join(STEPS))
    ap.add_argument('--regenerate', action='store_true', default=True,
                    help='regenerate the C from the ExeFS (default; the generated code is never shipped)')
    args = ap.parse_args()
    steps = [s for s in args.steps.split(',') if s]
    for s in steps:
        if s not in STEPS:
            sys.exit(f'unknown step {s}; steps: {",".join(STEPS)}')

    work, stack = args.work.resolve(), args.stack.resolve()
    mkw = work / 'mkw-recomp'
    for folder in ('mkw-recomp', 'PS5_PayloadSDK', 'PS5_VulkanBuild', 'PS5_MKWProbe'):
        if not (work / folder).is_dir():
            sys.exit(f'{work / folder} is missing: run tools/setup.py --work {work} first')
    for need in ('PS5_Vulkan/tooling/prospero-clang18', 'PS5_VulkanTemplate/.deps/native/ps5-payload-sdk',
                 'PS5_VulkanTemplate/external'):
        if not (stack / need).exists():
            sys.exit(f'{stack / need} is missing: set up the PS5 Vulkan stack first (docs/BUILD.md, step 1)')
    if {'game', 'shaders'} & set(steps) and not (args.exefs and (args.exefs / 'main').is_file()):
        sys.exit('--exefs must point at your decrypted ExeFS (a folder with main, sdk, subsdk*)')
    if {'shaders', 'romfs'} & set(steps) and not (args.romfs and args.romfs.is_dir()):
        sys.exit('--romfs must point at your decrypted RomFS folder')

    uv = ['uv', 'run'] if shutil.which('uv') else [sys.executable]   # upstream's tools expect uv (Python 3.14)
    env = dict(os.environ, MKW_GAME_OPT=os.environ.get('MKW_GAME_OPT', 'O2'))

    if 'deps' in steps:
        run([sys.executable, 'tools/build/ps5_deps.py', '--stack', stack, '--jobs', args.jobs, '--codecs'], mkw)
        if not (work / 'PS5_VulkanBuild/build/host/ps5-native-tool').exists():
            run(['make'], work / 'PS5_VulkanBuild')   # the ELF -> SELF tool and the clean-room libc.prx
    if 'game' in steps:
        cmd = [sys.executable, 'tools/build/ps5_game.py', '--stack', stack, '--exefs', args.exefs.resolve(),
               '--jobs', args.jobs]
        run(cmd + (['--regenerate'] if args.regenerate else []), mkw, env)
    if 'title' in steps:
        run([sys.executable, 'tools/build/ps5_boot.py', '--stack', stack, '--jobs', min(args.jobs, 4), '--link'], mkw, env)
    if 'shaders' in steps:
        run(uv + ['tools/shaders/extract.py', '--romfs', args.romfs.resolve(), '--exefs', args.exefs.resolve()], mkw)
        run(uv + ['tools/shaders/translate.py', '--jobs', args.jobs, '--progress'], mkw)
    if 'romfs' in steps:
        run(uv + ['tools/romfs/index.py', args.romfs.resolve(), mkw / 'build/romfs.index'], mkw)
    if 'tests' in steps:
        log = mkw / 'build/ps5-boot/host-checks.log'
        log.parent.mkdir(parents=True, exist_ok=True)
        print('\n+ PS5 host checks ->', log, flush=True)
        r = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_ps5_*.py'],
                           cwd=mkw, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        log.write_text(r.stdout)
        print(r.stdout[-400:])
        if r.returncode:
            sys.exit('host checks failed')
    print('\nBuild done. Next: tools/make_sce_sys.py and tools/package.py (docs/BUILD.md, step 4).')


if __name__ == '__main__':
    main()
