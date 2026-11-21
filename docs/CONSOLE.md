# Console notes

## Layout on the PS5

```
/data/homebrew/PPSA99861/
  eboot.bin  sce_module/libc.prx  sce_sys/  assets/  shaders/  licenses/  LEGAL.txt  build-info.json
  mkw.ini  romfs.index  spirv/  [boot-splash.png]
  exefs/  romfs/                      <- your dump (uploaded once)
  cache/  pipeline-cache.bin  pipeline-keys.bin  radv-shader-cache/   <- made by the title on first start
  profile/                            <- saves
  logs/mkw.log                        <- the log
/user/appmeta/PPSA99861/
  icon0.png  param.json  pic0.dds  pic1.dds   <- what the home screen shows
```

## Home screen icon and background

- The homebrew loader copies `icon0.png` and `param.json` to `/user/appmeta/PPSA99861/`, but **not** the background:
  `tools/deploy.py` copies `pic0.dds`/`pic1.dds` there too, so the background shows when the title is selected, not
  only while it starts.
- The background must be a DDS (BC7, DX10 header, 3840×2160). `tools/make_sce_sys.py` writes it.
- `icon0.png` may be RGBA; the transparency shows on the home screen.

## FTP pitfalls

- **Never copy `eboot.bin` or `sce_module/libc.prx` from the console and upload them again.** The console's FTP
  server returns the *decrypted* view of signed (SELF/SPRX) files; uploaded back, the console reports that "the data
  is corrupted". Always upload them from your build.
- `DELE` may be answered with code 226 instead of 250; `MLSD` does not take a path argument (change directory first).
- Do not deploy while the title is running.

## In game

- **Create + Options**: hidden settings menu (resolution, fps, graphics). It writes the `[display]` section of
  `mkw.ini`.
- **L3 + R3**: performance overlay.

## Logs

`/data/homebrew/PPSA99861/logs/mkw.log` (written by a background thread, so logging never stalls the game). Attach the
relevant part when you open an issue — after checking it holds nothing personal.
