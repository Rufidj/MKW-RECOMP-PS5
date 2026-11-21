# Legal terms and intended use

Please read this whole page before using anything in this repository. By cloning, building or using this project you
accept these terms.

## 1. No game content, ever

- This repository contains **no part of Mario Kart World**: no executable code, no decompiled or recompiled code, no
  assets (models, textures, audio, video, text), no shaders, and no title images or logos.
- It contains **no** console firmware, BIOS, system files, encryption or signing keys, title keys, or Sony/Nintendo
  SDK files.
- None of these will be provided, linked to, or discussed how to obtain. Requests for game files, keys, firmware,
  dumps or pre-built titles will be closed without an answer.

## 2. What you need, and must own

- A **legally purchased copy of Mario Kart World**, dumped **by you, from your own Nintendo Switch 2**.
- A **PS5 that you own**, able to run homebrew.

Downloading a dump, keys or firmware from the internet, or using somebody else's, is piracy and may be illegal in
your country. This project does not condone piracy and must not be used for it.

## 3. What you build is for your own use only

The build process reads your dump and produces, **on your own machine**:

- `eboot.bin`: the PS5 executable. It **contains the game's code**, recompiled.
- `spirv/`: the game's shaders, translated to SPIR-V.
- `romfs.index`: an index of the game's files.

These files are **derived from copyrighted material owned by Nintendo**. They are for running the copy of the game you
own, on your own console. **Do not upload, share, sell or distribute them** — not in this repository, not in issues,
not in releases, not anywhere else. This repository will never host builds, and pull requests or issues that attach
them will be removed.

The same applies to the title images: the tools take your own icon and background. Do not commit artwork you do not
have the rights to (for example, official game art).

## 4. Not affiliated

This is an independent, non-commercial fan project. It is **not affiliated with, endorsed by, sponsored by or
approved by Nintendo Co., Ltd., Sony Interactive Entertainment Inc., or any of their subsidiaries**, nor by the
authors of the upstream projects it builds on (listed in [CREDITS.md](CREDITS.md)), who are not responsible for it.

"Nintendo", "Nintendo Switch", "Mario Kart" and "Mario Kart World" are trademarks of Nintendo. "PlayStation", "PS5"
and "PlayStation 5" are trademarks of Sony Interactive Entertainment Inc. "Vulkan" is a registered trademark of the
Khronos Group Inc. They are used only to describe what this project is compatible with.

## 5. Interoperability

The software in this repository was written to make a copy of a game that the user lawfully owns run on other
hardware that the user also owns. It does not circumvent any copy protection of the game: it requires an already
decrypted dump made by the user, and it does not include or generate any keys.

## 6. No warranty and your own risk

The software is provided **"as is", without warranty of any kind** (see sections 15–16 of the
[GPL-3.0](LICENSE)). Running homebrew on a console may be against its terms of service, may void its warranty, and
may in rare cases make the console unstable (this project has caused kernel panics during development). You are
solely responsible for how you use it and for complying with the laws of your country.

## 7. Licenses of the code

- The code in this repository is under the **GNU General Public License v3.0** ([LICENSE](LICENSE)).
- The patches change projects under their own licenses; see [NOTICE.md](NOTICE.md). Our changes to files of
  mkw-recomp (MIT) are also offered under the MIT license.
- These licenses apply only to the code written by the respective authors. **They do not grant any rights over Mario
  Kart World or any other third-party property.**

## 8. Takedown

If you hold rights over something you believe is in this repository by mistake, open an issue (or contact the
owner through GitHub) and it will be removed promptly.
