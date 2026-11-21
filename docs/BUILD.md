# Building MKW-RECOMP-PS5

From the sources in this repository and **your own dump** to a title folder for the PS5. Everything happens on your
PC; nothing of the game is ever downloaded. Read [LEGAL.md](../LEGAL.md) first.

Tested on Linux x86-64 (Ubuntu 24.04). Needs about **40 GB** free (generated C, objects, shaders) and 16 GB of RAM.
Building the game code takes ~25 minutes on 6 cores.

## 0. What you need

- **Your dump of Mario Kart World 1.0.0**, decrypted, made from your own Switch 2: `exefs/` (`main`, `sdk`,
  `subsdk*`, `main.npdm`) and `romfs/`. Other versions have not been tested on the PS5.
- A **PS5 that runs homebrew** with a loader that starts titles from `/data/homebrew/<TITLE_ID>` and an FTP server
  (port 2121 by default).
- Host tools: `git`, `python3` (3.12+), [`uv`](https://docs.astral.sh/uv/) (mkw-recomp's tools use Python 3.14
  through it), `clang`/`lld`, `cmake`, `ninja`, `make`, `glslangValidator`, `zstd`, `curl`, `rsync`.
- For the shaders: the **SM86 encoding specification**, generated on your machine from NVIDIA's `nvdisasm` (not
  shipped). Follow upstream's
  [tools/shaders/README.md](https://github.com/adriadam10/mkw-recomp/blob/main/tools/shaders/README.md).
- Python packages for the title images: `pip install pillow etcpak`.

## 1. The PS5 Vulkan stack (toolchain)

The title is compiled with Mihawk-99's PS5 toolchain and Vulkan driver. Set it up in a folder of its own (called
`STACK` below) by following the instructions of those repositories:

```sh
mkdir STACK && cd STACK
git clone https://github.com/mihawk-99/PS5_Vulkan.git
git clone https://github.com/mihawk-99/PS5_VulkanTemplate.git
# then each repository's README / setup scripts (tools/setup-native-dependencies.sh, make, bootstrap),
# which fetch the public payload SDK, LLVM, Mesa and the other pinned dependencies
```

When it is ready, these exist:

```
STACK/PS5_Vulkan/tooling/prospero-clang18
STACK/PS5_VulkanTemplate/.deps/native/ps5-payload-sdk
STACK/PS5_VulkanTemplate/external
```

## 2. Sources: upstreams + patches

```sh
git clone <this repository> MKW-RECOMP-PS5 && cd MKW-RECOMP-PS5
python3 tools/setup.py --work ../work
```

This clones [mkw-recomp](https://github.com/adriadam10/mkw-recomp), PS5_PayloadSDK, PS5_Vulkan and
PS5_VulkanTemplate **at the commits pinned in [upstreams.json](../upstreams.json)** into `../work/`, and applies the
patches on a branch `mkw-recomp-ps5`. The folder names matter (the build finds its siblings by name):

```
work/mkw-recomp       work/PS5_PayloadSDK       work/PS5_VulkanBuild (PS5_Vulkan)       work/PS5_MKWProbe (the title)
```

Then build `work/PS5_VulkanBuild` once (`make`): it gives the ELF → SELF converter and the clean-room `libc.prx`.

## 3. Build

```sh
python3 tools/build.py --work ../work --stack STACK --exefs DUMP/exefs --romfs DUMP/romfs
```

The steps, which can also be run one at a time with `--steps`:

| Step | What it does | Output |
|---|---|---|
| `deps` | pinned VMA/xxHash headers; zstd, Opus and libvpx cross-compiled for the PS5 | `work/mkw-recomp/build/ps5-deps` |
| `game` | recompiles the game's code from **your** ExeFS to C and cross-compiles it (`MKW_GAME_OPT=O2`) | `work/mkw-recomp/build/ps5-full` |
| `title` | compiles the runtime and links `eboot.bin` + `sce_module/libc.prx` | `work/PS5_MKWProbe/dist/PPSA99861` |
| `shaders` | extracts the game's shaders from **your** RomFS and translates them to SPIR-V | `work/mkw-recomp/build/spirv` |
| `romfs` | indexes your RomFS (the title reads the index instead of listing 30 000+ files) | `work/mkw-recomp/build/romfs.index` |
| `tests` | the 26 PS5 host checks | `work/mkw-recomp/build/ps5-boot/host-checks.log` |

Notes:

- Any change to the guest CPU headers changes the runtime/game identity and needs the `game` step again: the title
  refuses to start with game objects of another identity.
- Never raise the GPU memory limit or inline the whole game into one object: a ~1 GB executable makes the PS5
  kernel panic.

## 4. Title images and package

```sh
python3 tools/make_sce_sys.py --out build/sce_sys --icon MY_ICON.png --background MY_BACKGROUND.png
python3 tools/package.py --work ../work --out build/PPSA99861 --sce-sys build/sce_sys [--splash MY_SPLASH.png]
```

- The icon is any image (512×512 RGBA is written; transparency is kept). Without `--icon` a plain generated icon is
  used.
- The background is written as `pic0.dds`/`pic1.dds`: 3840×2160 **BC7 in a DDS with a DX10 header**, the format the
  PS5 home screen reads. A PNG is ignored.
- `--splash` is an optional picture shown behind the loading bar.
- Only use images you have the rights to.

`build/` is ignored by git: the title folder contains your recompiled game code and must never be committed or shared.

## 5. Install on the console

```sh
python3 tools/deploy.py --host PS5_IP --title build/PPSA99861 --exefs DUMP/exefs --romfs DUMP/romfs
```

The first time it uploads your ExeFS and RomFS too (large; later runs skip files that are already there). Close the
game on the console before deploying. Details and pitfalls: [CONSOLE.md](CONSOLE.md).

The first start compiles the GPU pipelines and takes a few minutes; later starts use the cache.

## Updating

When this repository changes: `git pull`, then `python3 tools/setup.py --work ../work --force` (the old folders are
moved aside, never deleted; build outputs can be moved back into place to avoid a full rebuild), and build again.
