"""Maintainers only: export the working trees' changes as patches against the public upstream commits.

Usage: python3 tools/export_patches.py WORK patches/ CACHE
  WORK   the folder with mkw-recomp, PS5_PayloadSDK, PS5_VulkanBuild, PS5_MKWProbe (your development trees)
  CACHE  where clones of the upstreams are kept between runs
Set MKW_EXPORT_PRIVATE to a regular expression of your own private strings (user name, paths, console address):
any hit is reported, so it can be removed before committing.

For each project: a fresh clone of the upstream at the pinned commit, our working tree's tracked and untracked
(not ignored) files laid over it, and `git diff --binary` of the result. Build output, temporary files and anything
of the game are left out; the patch is checked to apply to the clean upstream and scanned for personal data.
"""
import json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

WORK = Path(sys.argv[1])
OUT = Path(sys.argv[2])
CACHE = Path(sys.argv[3])   # clones of the upstreams
PROJECTS = [
    # name, local folder, upstream url, commit, excluded top-level or path prefixes
    ('mkw-recomp', 'mkw-recomp', 'https://github.com/adriadam10/mkw-recomp.git', 'e652497ab3284d53bed671c012d86c7e397f19f5',
     ['.ninja_deps', '.ninja_log', 'build/', 'game/']),
    ('PS5_PayloadSDK', 'PS5_PayloadSDK', 'https://github.com/mihawk-99/PS5_PayloadSDK.git', 'b5efad528e0ac1b8289f39d72a0e890ff68ff0a6',
     ['platform/build/']),
    ('PS5_Vulkan', 'PS5_VulkanBuild', 'https://github.com/mihawk-99/PS5_Vulkan.git', 'fde9e3798c2ec1d8fccc90d5067cd6060490607f',
     ['.deps', 'build/', 'dist/']),
    ('PS5_VulkanTemplate', 'PS5_MKWProbe', 'https://github.com/mihawk-99/PS5_VulkanTemplate.git', None,
     ['build/', 'dist/', '.deps', 'klog/', 'imgui.ini', 'ps5/build/', 'ps5/dist/']),
]
SENSITIVE = re.compile(rb'(?:192\.168|10\.\d+)\.\d+\.\d+|/home/[a-z][\w.-]*/|/Users/[A-Za-z][\w.-]*/|[\w.+-]+@(?:gmail|hotmail|outlook|yahoo)\.\w+'
                       + (b'|' + os.environ['MKW_EXPORT_PRIVATE'].encode() if os.environ.get('MKW_EXPORT_PRIVATE') else b''))
SUBMODULES = {'PS5_VulkanTemplate': ['external/glm']}   # initialised by tools/setup.py before the deletions
BANNED_EXT = {'.nso', '.nca', '.nsp', '.xci', '.spv', '.elf', '.o', '.a', '.bin', '.prx', '.self'}

def run(cmd, cwd, **kw):
    return subprocess.run(cmd, cwd=cwd, check=True, **kw)

def files_of(folder):
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=folder).decode().split('\0')
    extra = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '-z'], cwd=folder).decode().split('\0')
    return sorted(set(filter(None, tracked + extra)))

lock = {}
for name, local, url, commit, excluded in PROJECTS:
    src = WORK / local
    if commit is None:   # the title: the template commit our project was created from
        line = subprocess.check_output(['git', 'log', '--reverse', '--format=%s'], cwd=src).decode().splitlines()[0]
        short = re.search(r'Template ([0-9a-f]{7,40})', line).group(1)
    clone = CACHE / name
    if not clone.exists():
        run(['git', 'clone', '-q', url, str(clone)], cwd=CACHE)
    if commit is None:
        commit = subprocess.check_output(['git', 'rev-parse', short], cwd=clone).decode().strip()
    with tempfile.TemporaryDirectory() as tmp:
        tree = Path(tmp) / name
        run(['git', 'worktree', 'add', '-q', '--detach', str(tree), commit], cwd=clone)
        try:
            upstream_files = set(filter(None, subprocess.check_output(['git', 'ls-files', '-z'], cwd=tree).decode().split('\0')))
            ours = [f for f in files_of(src) if not any(f == e or f.startswith(e) for e in excluded)]
            # files deleted in ours: tracked upstream, absent locally (and not excluded)
            for f in upstream_files:
                if not (src / f).exists() and not any(f == e or f.startswith(e) for e in excluded):
                    if (tree / f).is_dir(): run(['git', 'rm', '-q', '--cached', f], cwd=tree); shutil.rmtree(tree / f)   # a submodule
                    else: (tree / f).unlink()
            for f in ours:
                s = src / f
                if not s.is_file(): continue
                own_shader = f.endswith('.spv') and f.startswith('shaders/glsl/') and (src / f[:-4]).is_file()   # the title's GLSL, compiled
                if f not in upstream_files and Path(f).suffix.lower() in BANNED_EXT and not own_shader:
                    raise SystemExit(f'{name}: refusing new binary {f}')
                d = tree / f
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(s, d)
            run(['git', 'add', '-A'], cwd=tree)
            # deletions as a list of paths (their old content is upstream's, not ours), the rest as the patch
            deleted = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '--diff-filter=D', commit], cwd=tree).decode()
            patch = subprocess.check_output(['git', 'diff', '--cached', '--binary', '--diff-filter=d', commit], cwd=tree)
            stat = subprocess.check_output(['git', 'diff', '--cached', '--shortstat', commit], cwd=tree).decode().strip()
        finally:
            run(['git', 'worktree', 'remove', '--force', str(tree)], cwd=clone)
    hits = sorted(set(m.decode(errors='replace') for m in SENSITIVE.findall(patch)))
    out = OUT / f'{name}.patch'
    out.write_bytes(patch)
    lock[name] = {'url': url, 'commit': commit, 'patch': f'patches/{name}.patch', 'folder': local}
    if name in SUBMODULES:
        lock[name]['submodules'] = SUBMODULES[name]
    if deleted.strip():
        (OUT / f'{name}.deleted').write_text(deleted)
        lock[name]['deleted'] = f'patches/{name}.deleted'
    print(f'{name}: {len(patch)} bytes, {stat}; personal data: {hits or "none"}')
(OUT.parent / 'upstreams.json').write_text(json.dumps(lock, indent=2) + '\n')
