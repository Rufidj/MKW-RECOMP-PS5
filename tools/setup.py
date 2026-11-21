#!/usr/bin/env python3
"""Clone the upstream projects at their pinned commits and apply this port's patches.

Usage: python3 tools/setup.py --work DIR [--cache DIR] [--force]

For every entry of upstreams.json: clone the repository into DIR/<folder>, check out the pinned commit on a new
branch `mkw-recomp-ps5`, remove the paths listed in the entry's `.deleted` file (if any), apply the patch with
`git apply --index`, and commit the result. The four folders end up side by side, as the build expects:

    DIR/mkw-recomp  DIR/PS5_PayloadSDK  DIR/PS5_VulkanBuild  DIR/PS5_MKWProbe

--cache DIR   use existing clones in DIR/<name> as a local source (faster, offline); they are fetched from if the
              pinned commit is missing.
--force       replace a folder that already exists (it is renamed to <folder>.old-<n>, never deleted).

Nothing of the game is downloaded or needed at this step.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BRANCH = 'mkw-recomp-ps5'
IDENT = ['-c', 'user.name=mkw-recomp-ps5 setup', '-c', 'user.email=setup@localhost']


def git(*args, cwd, capture=False):
    print('+ git', ' '.join(args), flush=True)
    r = subprocess.run(['git', *args], cwd=cwd, check=True, text=True,
                       stdout=subprocess.PIPE if capture else None)
    return r.stdout.strip() if capture else None


def setup_one(name, entry, work, cache, force):
    dest = work / entry['folder']
    if dest.exists():
        if not force:
            sys.exit(f'{dest} already exists: use --force to set it aside, or choose another --work')
        n = 1
        while dest.with_name(f'{dest.name}.old-{n}').exists():
            n += 1
        dest.rename(dest.with_name(f'{dest.name}.old-{n}'))
        print(f'{dest} moved to {dest.name}.old-{n}')
    source = entry['url']
    if cache and (cache / name / '.git').exists():
        source = str((cache / name).resolve())
    git('clone', '--no-checkout', source, str(dest), cwd=work)
    if source != entry['url']:
        git('remote', 'set-url', 'origin', entry['url'], cwd=dest)
    try:
        git('cat-file', '-e', entry['commit'] + '^{commit}', cwd=dest)
    except subprocess.CalledProcessError:
        git('fetch', 'origin', entry['commit'], cwd=dest)
    git('checkout', '-q', '-b', BRANCH, entry['commit'], cwd=dest)

    for sub in entry.get('submodules', []):   # before the deletions: they remove .gitmodules
        git('submodule', 'update', '--init', '--', sub, cwd=dest)

    if entry.get('deleted'):
        paths = [p for p in (REPO / entry['deleted']).read_text().splitlines() if p.strip()]
        for i in range(0, len(paths), 500):
            subprocess.run(['git', 'rm', '-r', '-q', '-f', '--ignore-unmatch', '--', *paths[i:i + 500]],
                           cwd=dest, check=True)
        print(f'removed {len(paths)} upstream paths not used by the port')

    patch = REPO / entry['patch']
    git('apply', '--check', '--binary', '--index', str(patch), cwd=dest)
    git('apply', '--binary', '--index', '--whitespace=nowarn', str(patch), cwd=dest)
    git(*IDENT, 'commit', '-q', '-m', f'MKW-RECOMP-PS5: apply {patch.name}', cwd=dest)
    print(f'{name}: {entry["commit"][:12]} + {patch.name} -> {dest}\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--work', type=Path, required=True, help='folder that will hold the four projects')
    ap.add_argument('--cache', type=Path, help='folder with existing clones named after upstreams.json keys')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--only', help='set up only this upstream (a key of upstreams.json)')
    args = ap.parse_args()
    upstreams = json.loads((REPO / 'upstreams.json').read_text())
    args.work.mkdir(parents=True, exist_ok=True)
    for name, entry in upstreams.items():
        if args.only and name != args.only:
            continue
        setup_one(name, entry, args.work.resolve(), args.cache, args.force)
    print('Done. Next: docs/BUILD.md, step 3 (build).')


if __name__ == '__main__':
    main()
