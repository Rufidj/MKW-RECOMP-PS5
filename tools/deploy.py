#!/usr/bin/env python3
"""Upload the title folder (and, the first time, your own exefs/ and romfs/) to the PS5 over FTP.

Usage: python3 tools/deploy.py --host PS5_IP [--port 2121] --title build/PPSA99861
                               [--exefs DUMP/exefs] [--romfs DUMP/romfs] [--force]

CLOSE THE GAME ON THE CONSOLE FIRST: replacing files of a running title can crash it or the console.

- Every file goes to a temporary name and is renamed into place once its upload is checked, so an interrupted
  upload never leaves a half-written file under the real name.
- Small files are checked by SHA-256 (download after upload). eboot.bin and sce_module/libc.prx are signed SELF
  files: the console's FTP server hands back their *decrypted* view, so they are checked by the ELF magic of that
  view instead. Never download them from the console to upload them again: the console
  rejects the decrypted copy ("the data is corrupted").
- Bulk folders (spirv/, assets/, exefs/, romfs/) skip files whose remote size already matches (--force uploads all).
- The icon, title and background are also copied to /user/appmeta/PPSA99861, where the home screen reads them: the
  homebrew loader copies only the icon and param.json there, not pic0.dds/pic1.dds.

Your dump stays on your PC and your console only. The host address is never stored by this tool.
"""
import argparse
import ftplib
import hashlib
import io
import sys
from pathlib import Path

TITLE_ID = 'PPSA99861'
SELF_FILES = {'eboot.bin', 'sce_module/libc.prx'}
BULK = ('spirv/', 'assets/', 'shaders/', 'licenses/')
APPMETA = ('icon0.png', 'param.json', 'pic0.dds', 'pic1.dds')


class Uploader:
    def __init__(self, host, port):
        self.ftp = ftplib.FTP()
        self.ftp.connect(host, port, timeout=600)
        self.ftp.login()
        self.ftp.voidcmd('TYPE I')
        self.dirs = set()

    def cmd(self, line):
        try:
            return self.ftp.sendcmd(line)
        except ftplib.error_reply as e:   # this server answers some commands (DELE) with 226
            return str(e)

    def mkdirs(self, path):
        parts, cur = path.strip('/').split('/'), ''
        for p in parts:
            cur += '/' + p
            if cur in self.dirs:
                continue
            try:
                self.ftp.cwd(cur)
            except ftplib.error_perm:
                self.ftp.mkd(cur)
            self.dirs.add(cur)

    def size(self, path):
        try:
            return self.ftp.size(path)
        except ftplib.error_perm:
            return None

    def fetch_head(self, path, n):
        buf = io.BytesIO()
        try:
            self.ftp.retrbinary('RETR ' + path, buf.write, blocksize=65536)
        except ftplib.error_perm:
            return None
        return buf.getvalue()[:n]

    def sha_remote(self, path):
        h = hashlib.sha256()
        self.ftp.retrbinary('RETR ' + path, h.update, blocksize=262144)
        return h.hexdigest()

    def put(self, local, remote, check):
        folder, name = remote.rsplit('/', 1)
        self.mkdirs(folder)
        temp = f'{folder}/.upload-{name}'
        with local.open('rb') as f:
            self.ftp.storbinary('STOR ' + temp, f, blocksize=262144)
        if check == 'self':   # the server shows a SELF decrypted: valid when that view is an ELF
            if self.fetch_head(temp, 4) != b'\x7fELF':
                raise RuntimeError(f'{remote}: the console does not read the upload as a valid SELF')
        elif self.size(temp) != local.stat().st_size:
            raise RuntimeError(f'upload of {local} has the wrong size')
        if check == 'sha' and self.sha_remote(temp) != hashlib.sha256(local.read_bytes()).hexdigest():
            raise RuntimeError(f'upload of {local} does not match')
        if self.size(remote) is not None:
            self.cmd('DELE ' + remote)
        self.ftp.rename(temp, remote)


def upload_tree(up, root, remote_root, bulk_all, force, label):
    # eboot.bin last: until it is replaced, the old title still runs with files it understands
    files = sorted((p for p in root.rglob('*') if p.is_file()), key=lambda p: (p.name == 'eboot.bin', p.as_posix()))
    done = skipped = 0
    for i, f in enumerate(files, 1):
        rel = f.relative_to(root).as_posix()
        remote = f'{remote_root}/{rel}'
        bulk = bulk_all or rel.startswith(BULK)
        if bulk and not force and up.size(remote) == f.stat().st_size:
            skipped += 1
            continue
        check = 'self' if (not bulk_all and rel in SELF_FILES) else 'size' if bulk else 'sha'
        up.put(f, remote, check)
        done += 1
        if done % 200 == 0 or not bulk:
            print(f'{label}: {i}/{len(files)} {rel}', flush=True)
    print(f'{label}: {done} uploaded, {skipped} already there', flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--host', required=True)
    ap.add_argument('--port', type=int, default=2121)
    ap.add_argument('--title', type=Path, required=True, help='the folder made by tools/package.py')
    ap.add_argument('--exefs', type=Path, help='your decrypted ExeFS, uploaded to <title>/exefs')
    ap.add_argument('--romfs', type=Path, help='your decrypted RomFS, uploaded to <title>/romfs (large)')
    ap.add_argument('--remote', default=f'/data/homebrew/{TITLE_ID}')
    ap.add_argument('--force', action='store_true', help='upload bulk files even when the remote size matches')
    args = ap.parse_args()
    if not (args.title / 'eboot.bin').is_file():
        sys.exit(f'{args.title} is not a packaged title folder (no eboot.bin)')
    answer = input('Is the game closed on the PS5? [y/N] ').strip().lower()
    if answer not in ('y', 'yes', 's', 'si', 'sí'):
        sys.exit('Close it first, then run this again.')

    up = Uploader(args.host, args.port)
    try:
        upload_tree(up, args.title, args.remote, False, args.force, 'title')
        if args.exefs:
            upload_tree(up, args.exefs, args.remote + '/exefs', True, args.force, 'exefs')
        if args.romfs:
            upload_tree(up, args.romfs, args.remote + '/romfs', True, args.force, 'romfs')
        meta = f'/user/appmeta/{TITLE_ID}'
        for name in APPMETA:
            f = args.title / 'sce_sys' / name
            if f.is_file():
                up.put(f, f'{meta}/{name}', 'sha')
        print(f'appmeta: {", ".join(n for n in APPMETA if (args.title / "sce_sys" / n).is_file())} -> {meta}')
        print('Done. Start the title from the home screen; the log is at', args.remote + '/logs/mkw.log')
    finally:
        up.ftp.close()


if __name__ == '__main__':
    main()
