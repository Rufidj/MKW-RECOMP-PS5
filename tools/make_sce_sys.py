#!/usr/bin/env python3
"""Make the title's sce_sys/ folder: param.json, icon0.png and the background pic0.dds/pic1.dds, from YOUR images.

Usage: python3 tools/make_sce_sys.py --out build/sce_sys [--icon ICON.png] [--background BG.png] [--title "MKW RECOMP PS5"]

  --icon        any image; scaled to 512x512 and kept RGBA (transparency shows on the home screen). Without it a plain
                generated icon is used.
  --background  any image; cropped/scaled to 3840x2160 and compressed to BC7 in a DDS with a DX10 header, the
                format the PS5 home screen reads. A PNG background is ignored by the console. Optional.
  --title       the name on the home screen (default: MKW RECOMP PS5)

Needs Pillow; the background also needs etcpak (pip install pillow etcpak).
Use only images you have the rights to: this repository never ships official game artwork (LEGAL.md).
"""
import argparse
import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
W, H = 3840, 2160


def dds_bc7(width, height, payload):
    """DDS header + DX10 extension for one BC7_UNORM 2D level (as the PS5 home screen's own backgrounds)."""
    linear = ((width + 3) // 4) * ((height + 3) // 4) * 16
    assert len(payload) == linear, (len(payload), linear)
    flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x20000 | 0x80000   # CAPS HEIGHT WIDTH PIXELFORMAT MIPMAPCOUNT LINEARSIZE
    head = struct.pack('<7I', 124, flags, height, width, linear, 1, 1) + b'\0' * 44
    pixfmt = struct.pack('<2I4s5I', 32, 0x4, b'DX10', 0, 0, 0, 0, 0)
    caps = struct.pack('<5I', 0x1000, 0, 0, 0, 0)
    dx10 = struct.pack('<5I', 98, 3, 0, 1, 3)   # DXGI_FORMAT_BC7_UNORM, TEXTURE2D, misc 0, array 1, alpha opaque
    out = b'DDS ' + head + pixfmt + caps + dx10
    assert len(out) == 148
    return out + payload


def cover(img, w, h):
    from PIL import Image
    scale = max(w / img.width, h / img.height)
    img = img.resize((max(w, round(img.width * scale)), max(h, round(img.height * scale))), Image.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def default_icon(title):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((16, 16, 496, 496), radius=96, fill=(28, 40, 72, 255))
    lines = title.split() or ['MKW']
    size = 120
    while True:   # the largest size at which the widest word fits in 400 px
        try:
            font = ImageFont.truetype('DejaVuSans-Bold.ttf', size)
        except OSError:
            font = ImageFont.load_default()
            break
        if size <= 24 or max(d.textlength(w, font=font) for w in lines) <= 400:
            break
        size -= 4
    step = size * 1.15
    y = 256 - step * len(lines) / 2
    for line in lines:
        d.text((256 - d.textlength(line, font=font) / 2, y), line, font=font, fill=(255, 255, 255, 255))
        y += step
    return im


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--icon', type=Path)
    ap.add_argument('--background', type=Path)
    ap.add_argument('--title', default='MKW RECOMP PS5')
    args = ap.parse_args()
    from PIL import Image
    args.out.mkdir(parents=True, exist_ok=True)

    param = json.loads((REPO / 'config/param.json').read_text())
    param['localizedParameters']['en-US']['titleName'] = args.title
    (args.out / 'param.json').write_text(json.dumps(param, indent=2) + '\n')

    icon = Image.open(args.icon).convert('RGBA') if args.icon else default_icon(args.title)
    if icon.size != (512, 512):
        icon = cover(icon, 512, 512) if args.icon else icon
    icon.save(args.out / 'icon0.png')

    if args.background:
        try:
            import etcpak
        except ImportError:
            raise SystemExit('the background needs etcpak: pip install etcpak')
        bg = cover(Image.open(args.background).convert('RGBA'), W, H)
        data = dds_bc7(W, H, etcpak.compress_bc7(bg.tobytes(), W, H))
        for name in ('pic0.dds', 'pic1.dds'):
            (args.out / name).write_bytes(data)
    print('wrote', ', '.join(sorted(p.name for p in args.out.iterdir())), 'in', args.out)


if __name__ == '__main__':
    main()
