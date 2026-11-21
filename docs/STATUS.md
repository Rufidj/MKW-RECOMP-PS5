# Status

Last update: 21/11/2026. Base: mkw-recomp `e652497`; tested with Mario Kart World 1.0.0.

## Works

- Boot, intro, menus, races, sound, saves.
- 1080p output with FSR 1 sharpening; 720p + FSR upscaling and 1440p ("original") also selectable.
- Automatic frame rate: ~45–56 fps in races, the game runs at real speed. No long stalls; long sessions survive.
- Hidden settings menu (Create + Options) and performance overlay (L3 + R3).
- Custom title name, icon and home-screen background.

## Known limits

- **Not a locked 60 fps.** The remaining bottleneck is the CPU thread that replays the game's NVN command stream into
  Vulkan (16–24 ms a frame in busy races). The GPU has headroom. Forcing `FPS=60` makes the game run in slow motion
  when a frame is late.
- Occasional small flickers.
- 1440p costs ~8 fps in races.
- No online play.

## What the port changes (summary)

- **Guest memory**: the game's memory lives in a checked region with per-page rights; loads and stores go through
  per-size entry points with a fast path (a page table of biased pointers) and lock-free atomics, including 16-byte
  compare-and-swap.
- **Time**: `clock_gettime` is a system call on the PS5; time is read from the TSC instead, re-anchored regularly.
- **Thread-local storage**: a faster emulated TLS keyed by the thread's TCB pointer.
- **Logging**: asynchronous writer thread (synchronous writes blocked the game for up to 500 ms).
- **Graphics**: the NVN → Vulkan replay runs on its own thread, followed by recorder and submit threads; only the
  submits whose results the CPU reads wait for the GPU.
- **Memory pressure**: texture caches trimmed when free memory runs low.
- **Packaging**: title folder, home-screen images, staged FTP deploy.

## Ideas

- More work on the replay thread (fewer TLS lookups, cheaper state tracking) toward a locked 60 fps.
- 1440p once there is CPU margin.
