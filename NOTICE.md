# Notices

This repository is licensed under the GNU General Public License v3.0 ([LICENSE](LICENSE)).

The patches in [`patches/`](patches/) are changes to these projects, which keep their own licenses. When you run
`tools/setup.py`, each project is cloned from its public repository; its license file and notices come with it.

| Upstream | License | Patch | Note |
|---|---|---|---|
| [adriadam10/mkw-recomp](https://github.com/adriadam10/mkw-recomp) | MIT, Copyright (c) 2026 Adrià | `patches/mkw-recomp.patch` | Our changes to its files are dual-licensed: GPL-3.0 **or** MIT, at your choice |
| [mihawk-99/PS5_PayloadSDK](https://github.com/mihawk-99/PS5_PayloadSDK) | GPL-3.0-or-later | `patches/PS5_PayloadSDK.patch` | |
| [mihawk-99/PS5_Vulkan](https://github.com/mihawk-99/PS5_Vulkan) | GPL-3.0-or-later | `patches/PS5_Vulkan.patch` | |
| [mihawk-99/PS5_VulkanTemplate](https://github.com/mihawk-99/PS5_VulkanTemplate) | MIT, Copyright (c) 2016 Sascha Willems | `patches/PS5_VulkanTemplate.patch` (+ `.deleted`) | |

A title built from these sources links the GPL-3.0-or-later PS5 platform layer, so the program as a whole is under
GPL-3.0-or-later. Its own `licenses/` folder lists every component, its license and its source.

The license of the code grants no rights over Mario Kart World. See [LEGAL.md](LEGAL.md).
