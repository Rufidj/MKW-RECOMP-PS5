# Credits

This port stands on the work of many people. Thank you.

## The recompilation

**[mkw-recomp](https://github.com/adriadam10/mkw-recomp)** by **Adrià ([@adriadam10](https://github.com/adriadam10))** —
the static recompilation of Mario Kart World this port is built from: the AArch64 → C recompiler, the NVN2-on-Vulkan
graphics layer, the SM86 → SPIR-V shader translator, the reimplemented Nintendo SDK, audio, input, the FSR upscaler
integration, and the tooling to set the game up from a dump. MIT license. Every line of game support in this port
comes from there; this repository only adds the PS5 platform layer and the changes needed to run it on the console.

mkw-recomp itself credits the projects it learned from (see its README and `docs/research.md`).

## The PS5 stack

By **[Mihawk-99](https://github.com/mihawk-99)**:

- **[PS5_Vulkan](https://github.com/mihawk-99/PS5_Vulkan)** — Vulkan on PS5 (RADV with a PS5 winsys and VideoOut WSI),
  the title link recipe, the C runtime start-up and import stubs. GPL-3.0-or-later.
- **[PS5_PayloadSDK](https://github.com/mihawk-99/PS5_PayloadSDK)** — fork of the payload SDK with the shared
  platform layer (heap, direct and executable memory, libc gaps). GPL-3.0-or-later.
- **[PS5_VulkanTemplate](https://github.com/mihawk-99/PS5_VulkanTemplate)** — the native title template this port's
  title is built from. MIT (on Sascha Willems' examples).
- **PS5_Mesa** — the Mesa fork with RADV, ACO and NIR for the PS5.

And the projects that stack is built on:

- **[ps5-native-app-boilerplate](https://github.com/blackbearreloaded/ps5-native-app-boilerplate)** by
  **BlackBearReloaded** — the PS5 ELF converter, the fake-SELF writer and the **clean-room `libc.prx`** the title
  loads.
- **[ps5-payload-dev/sdk](https://github.com/ps5-payload-dev/sdk)** by **John Törnblom** and the ps5-payload-dev
  contributors — public PS5 headers, sysroot and the `prospero-clang` toolchain.
- **[Mesa](https://mesa3d.org/)** (RADV, ACO, NIR) — the Mesa contributors. MIT.
- **[opengnm-psbc](https://github.com/PS4-OpenGNM/opengnm-psbc)** — PS4-OpenGNM.
- **[Vulkan examples](https://github.com/SaschaWillems/Vulkan)** by **Sascha Willems**. MIT.

## Libraries

Dear ImGui, volk, the Vulkan headers, Vulkan Memory Allocator, glm, libktx, tinygltf, stb, nlohmann/json, zstd,
xxHash, zlib, Opus, libvpx, musl (regex), dlmalloc, LLVM libc++, AMD FidelityFX Super Resolution, DejaVu fonts —
each under its own license. The built title carries every license text in `licenses/`.

## This port

The PS5 port changes (checked guest memory, TSC clock, emulated TLS, asynchronous logging, replay pipeline tuning,
the hidden settings menu, packaging and deployment tools) were written for this repository with the help of
Claude (Anthropic).
