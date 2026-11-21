# MKW-RECOMP-PS5

**An unofficial port of [mkw-recomp](https://github.com/adriadam10/mkw-recomp) — the static recompilation of
*Mario Kart World* by Adrià ([@adriadam10](https://github.com/adriadam10)) — to PS5 homebrew.**

> [!IMPORTANT]
> **This repository contains no part of the game.** No code, assets, shaders, keys, firmware or dumps from Nintendo
> or Sony are included, and none will be provided or linked to. To use it you need **your own legally obtained
> copy of Mario Kart World, dumped from your own Nintendo Switch 2**, and a PS5 able to run homebrew that you own.
> Read [LEGAL.md](LEGAL.md) before anything else.

This project is not affiliated with, endorsed by or sponsored by Nintendo, Sony Interactive Entertainment, or the
authors of the projects it builds on. "Mario Kart", "Nintendo Switch" and "PlayStation" are trademarks of their
respective owners and are used here only to describe compatibility.

## Credits first

The hard part — recompiling the game's AArch64 code to C, reimplementing NVN2 on Vulkan, translating the SM86
shaders, and replacing the Nintendo SDK — is **Adrià's work in [mkw-recomp](https://github.com/adriadam10/mkw-recomp)**.
This repository only carries the changes needed to run that recompilation as a native PS5 title, on top of the PS5
Vulkan stack by **[Mihawk-99](https://github.com/mihawk-99)**. Please support and credit the upstream projects. The
full list is in [CREDITS.md](CREDITS.md).

Please do not report problems of this port to the upstream projects: open an issue here instead.

## What is in this repository

| Path | Contents |
|---|---|
| [`patches/`](patches/) | Our changes, as `git` patches against **pinned public commits** of the upstream projects |
| [`upstreams.json`](upstreams.json) | The upstream repositories, the exact commits, and the folder each one is checked out into |
| [`tools/setup.py`](tools/setup.py) | Clones the upstreams at those commits and applies the patches |
| [`tools/build.py`](tools/build.py) | Runs the build steps in order (game code, title, shaders, RomFS index) |
| [`tools/package.py`](tools/package.py) | Assembles the title folder `PPSA99861/` (without any game data) |
| [`tools/make_sce_sys.py`](tools/make_sce_sys.py) | Builds `param.json`, the icon and the background (`pic0.dds`/`pic1.dds`) from **your own** images |
| [`tools/deploy.py`](tools/deploy.py) | Uploads the title folder to the console over FTP, staged and hash-verified |
| [`config/`](config/) | `mkw.ini` (the tested settings) and the title's `param.json` |
| [`docs/`](docs/) | [Build guide](docs/BUILD.md), [console notes](docs/CONSOLE.md), [status](docs/STATUS.md) |

Everything the build produces from your dump (generated C, compiled game code, the `eboot.bin` that contains it,
translated shaders, the RomFS index) stays on your machine: the `.gitignore` and the pre-commit hook in
[`tools/hooks/`](tools/hooks/) refuse it.

## Status

Playable on a PS5 at 1080p with FSR sharpening: menus, races, sound and long sessions work. The frame rate is
automatic (about 45–56 fps in races; the game runs at real speed). Known limits are in [docs/STATUS.md](docs/STATUS.md).
Only **Mario Kart World 1.0.0** has been tested.

## Quick start

You need a Linux PC, the PS5 toolchain of Mihawk-99's stack, your own dump (`exefs/` and `romfs/`), and a PS5
running a homebrew loader with an FTP server. Step by step: **[docs/BUILD.md](docs/BUILD.md)**.

```sh
python3 tools/setup.py --work ../work                 # clone upstreams at pinned commits + apply patches
python3 tools/build.py --work ../work --stack STACK --exefs DUMP/exefs --romfs DUMP/romfs
python3 tools/make_sce_sys.py --icon my-icon.png --background my-bg.png --out build/sce_sys
python3 tools/package.py --work ../work --sce-sys build/sce_sys --out build/PPSA99861
python3 tools/deploy.py --host PS5_IP --title build/PPSA99861 --romfs DUMP/romfs --exefs DUMP/exefs
```

In game: **Create + Options** opens the hidden settings menu (resolution, fps, graphics); **L3 + R3** toggles the
performance overlay.

## License

The code in this repository (patches, scripts, documentation) is licensed under the
**GNU General Public License v3.0** ([LICENSE](LICENSE)). The patches modify projects under their own licenses
(mkw-recomp: MIT; PS5_PayloadSDK and PS5_Vulkan: GPL-3.0-or-later; PS5_VulkanTemplate: MIT, based on Sascha
Willems' Vulkan examples); our changes to the MIT-licensed mkw-recomp files may also be used under the MIT license, so
they can be taken upstream. See [NOTICE.md](NOTICE.md).

The license covers **only** the code written for this project. It grants no rights over Mario Kart World or any
other Nintendo or Sony property, and a title you build from your dump contains recompiled game code: it is for
your own personal use and **must not be shared**. See [LEGAL.md](LEGAL.md).

---

### En español (resumen)

Port no oficial a homebrew de PS5 de [mkw-recomp](https://github.com/adriadam10/mkw-recomp), la recompilación
estática de *Mario Kart World* creada por **Adrià (adriadam10)**. Este repositorio **no contiene nada del juego**:
necesitas tu propia copia legal, volcada de tu propia Nintendo Switch 2. Aquí solo están nuestros parches, las
herramientas para compilar y empaquetar, y la documentación. Lo que compiles a partir de tu volcado (el `eboot.bin`,
los shaders, el índice del romfs) lleva código o datos del juego: es para tu uso personal y **no se debe
compartir**. Lee [LEGAL.md](LEGAL.md). Sin relación con Nintendo ni con Sony.
