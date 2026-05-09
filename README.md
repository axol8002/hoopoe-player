<img width="480" height="480" alt="hoopoe-logo" src="https://github.com/user-attachments/assets/425d02b8-9b29-4e82-aefb-0d854ced7538" />

# hoopoe-player

> Play videos, images, and webcam as colorful ASCII art directly in your terminal.

![PyPI version](https://img.shields.io/pypi/v/hoopoe-player)
![Total Downloads](https://static.pepy.tech/badge/hoopoe-player)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Maintained](https://img.shields.io/badge/Maintained%3F-yes-green)
[![Ask Me Anything](https://img.shields.io/badge/Ask%20me-anything-1abc9c.svg)](https://github.com/axol8002/hoopoe-player/issues)

## Table of contents

- [Installation](#installation)
- [Quick usage (CLI)](#quick-usage-cli)
- [TUI (Terminal UI)](#tui-terminal-ui)
- [Features](#features)
- [Controls](#controls)
- [Character modes](#character-modes)
- [Viewing ANSI outputs](#viewing-ansi-outputs)
- [Requirements](#requirements)
- [Roadmap](#roadmap)
- [Star History](#star-history)
- [Support the creator](#support-the-creator)
- [License](#license)

## Installation

```bash
# Most systems
pip install hoopoe-player

# Ubuntu/Debian
pipx install hoopoe-player
```

You also need `ffmpeg` for audio:

```bash
sudo apt install ffmpeg   # Ubuntu/Debian
sudo pacman -S ffmpeg     # Arch
```

---

## Quick usage (CLI)

```bash
# Play a YouTube, Twitch, Vimeo, or any yt-dlp supported site
hoopoe https://www.youtube.com/watch?v=xxxxx
hoopoe https://www.twitch.tv/videos/xxxxxxxxx
hoopoe https://vimeo.com/xxxxxxxxx

# Play a local file
hoopoe -l video.mp4
hoopoe -l video.gif

# Enable audio
hoopoe -s https://www.youtube.com/watch?v=xxxxx

# Render a local image
hoopoe -i image.jpg

# Change character mode
hoopoe -m braille https://www.youtube.com/watch?v=xxxxx

# Show status bar (time, volume, controls)
hoopoe --hud https://www.youtube.com/watch?v=xxxxx

# Loop video automatically
hoopoe --loop https://www.youtube.com/watch?v=xxxxx

# Sync video to audio clock (recommended with -s)
hoopoe -s --sync https://www.youtube.com/watch?v=xxxxx

# Limit rendering FPS
hoopoe --fps 15 https://www.youtube.com/watch?v=xxxxx
hoopoe --webcam --fps 10

# Use 16-color ANSI palette (terminals without true color support)
hoopoe --legacy-color https://www.youtube.com/watch?v=xxxxx        # rgb or lab, rgb by default

# Disable all color output (terminals with no color support)
hoopoe --no-color -m braille https://www.youtube.com/watch?v=xxxxx

# Save render to an ANSI file
hoopoe --output render.ans https://www.youtube.com/watch?v=xxxxx
hoopoe --output ~/recordings/ https://www.youtube.com/watch?v=xxxxx
hoopoe --webcam --output webcam.ans
hoopoe -i --output render.ans photo.jpg

# Stream webcam as ASCII art
hoopoe --webcam
hoopoe --webcam -m solid --hud
hoopoe --webcam --flip h --invert

# Highlight mode (color as background) with any character mode
hoopoe -m braille --highlight https://www.youtube.com/watch?v=xxxxx

# Combine options
hoopoe -l -s --sync -m classic --highlight --hud --loop video.mp4

# Replay a recorded .ans file
hoopoe --play render.ans
hoopoe --play --fps 5 render.ans
```

---

## TUI (Terminal UI)

This repository includes a dedicated TUI launcher (`tui/hoopoe-tui`) to avoid typing full CLI flags every time.

<img width="800" height="400" alt="hoopoe-tui-preview" src="https://github.com/user-attachments/assets/3f5e024f-1910-41f1-a260-cbc2314a2646" />

<img width="800" height="396" alt="hoopoe-ansi-art-preview" src="https://github.com/user-attachments/assets/d24b3bb6-7b65-4764-9bb5-caf6817d8a19" />

### What it does

- Provides an interactive menu for playback and settings
- Stores your defaults in `~/.config/hoopoe-launcher.conf`
- Lets you run videos from URL or local filenames quickly

### TUI requirements

- Bash
- Linux or WSL
- `hoopoe` available in your `PATH` (`pip install hoopoe-player`)

### Run the TUI

From a clone of this repository:

```bash
chmod +x tui/hoopoe-tui
./tui/hoopoe-tui
```

Optional (run it globally):

```bash
sudo ln -s "$(pwd)/tui/hoopoe-tui" /usr/local/bin/hoopoe-tui
hoopoe-tui
```

### TUI configurable settings

The TUI persists these options:

- Playback mode (video+audio or video only)
- Loop mode
- Character style
- Highlight mode
- FPS quality profile
- Local video directory

---

## Features

- 🎬 **YouTube, Twitch, Vimeo & more** — stream from YouTube, Twitch, Vimeo, direct video URLs (`.mp4`, `.webm`, `.m3u8`), or any platform supported by yt-dlp (1800+ sites); also plays local files
- 🎨 **6 character modes** — classic, blocks, braille, minimal, nocolor, solid
- 🌈 **True color** — full 24-bit RGB color per character for supported terminals
- 🔊 **Audio playback** (`-s`) — synced audio via ffmpeg/ffplay
- 📺 **Live stream support** — plays YouTube live streams with low-latency audio mode
- 🔗 **A/V sync mode** (`--sync`) — recommended with `-s`; drops frames to stay locked to the audio clock when rendering is slow, recovers automatically
- 🖥️ **HUD** (`--hud`) — status bar with timestamp, real-time FPS, mode and controls
- 🔁 **Loop mode** (`--loop`) — automatically restarts video and audio at the end
- 📸 **Screenshot** (`P`) — saves the current frame as a timestamped ANSI color file (`.ans`)
- 🖼️ **Image rendering** (`-i`) — displays a single local image
- 📐 **Dynamic resize** — terminal resize is applied immediately, even while paused
- 🖥️ **Alternate screen** — runs in a separate buffer like vim/htop; your terminal history is preserved on exit
- 📷 **Webcam support** (`--webcam`) — stream your webcam live as ASCII art; select camera index with `--camera`
- 🔀 **Flip** (`--flip h/v/hv`) — flip the webcam feed horizontally, vertically, or both
- 🌗 **Invert** (`--invert`) — invert brightness mapping for any character mode
- 🎨 **Highlight** (`--highlight`) — render color as background for any character mode
- 🎞️ **FPS limit** (`--fps`) — cap the rendering framerate to reduce CPU usage
- 💾 **Output to file** (`--output`) — save the full render as an ANSI file; works with video, webcam, and image modes
- ▶️ **ANSI playback** (`--play`) — replay a recorded `.ans` file at the original framerate; supports pause and FPS override
- 🎨 **Legacy color** (`--legacy-color`) — render using the 16-color ANSI palette for terminals without true color support; `rgb` mode uses fast Euclidean RGB distance, `lab` mode uses perceptual CIE LAB distance
- ⬜ **No color** (`--no-color`) — disable all color output for terminals with no color support; works with any character mode

## Controls

| Key | Action |
|-----|--------|
| `Space` | Pause / Play |
| `P` | Screenshot — save current frame as `.ans` ANSI file |
| `Q` or `Ctrl+C` | Quit |

Controls are the same for video and webcam modes.

## Character modes

| Mode | Style |
|------|-------|
| `classic` | `. : - = + * # % @` — default, coloured |
| `blocks` | `░ ▒ ▓ █` — bold blocks, coloured |
| `braille` | `⠁ ⠃ ⠇ ⠿ ⣿` — dense dots, coloured |
| `minimal` | `· • ● ■` — clean and minimal, coloured |
| `solid` | pure color blocks — no characters, most accurate color reproduction |

Use `--highlight` with any mode to render color as background instead of foreground.
Use `--invert` with any mode to invert the brightness mapping.
Use `--legacy-color` (or `--legacy-color lab` for perceptual matching) with any mode to use the 16-color ANSI palette instead of 24-bit RGB.
Use `--no-color` with any mode to disable color entirely.

## Viewing ANSI outputs

Screenshots saved with `P` and output files saved with `--output` are `.ans` files containing raw ANSI escape codes.

Replay them with:

```bash
hoopoe --play render.ans
cat hoopoe_screenshot_20260317_142301.ans

# Override playback speed
hoopoe --play --fps 5 render.ans
```

To dump the raw content to the terminal (no timing):

```bash
cat render.ans
```

## Requirements

- Python 3.10+
- ffmpeg (optional, needed for `-s` audio)
- A terminal with true color support (use `--legacy-color` or `--no-color` for terminals without it)

## Roadmap

### Features
- [x] **Webcam support** — stream your webcam live as ASCII art in the terminal (`--webcam`, `--camera`, `--flip`)
- [x] **`--fps` flag** — cap the rendering framerate to reduce CPU usage
- [x] **Image display** — render local images and online images as ASCII art in the terminal
- [x] **`--output` to file** — save the full video render as an ANSI file instead of single screenshots
- [x] **Broader URL support** — Twitch, Vimeo, direct video URLs, and any of the 1800+ sites supported by yt-dlp work out of the box
- [x] **16-color mode** — `--legacy-color` flag; uses the 16-color ANSI palette for terminals without true color support
- [ ] **Shell autocompletion** — tab-complete flags and paths for `hoopoe`
- [ ] **TUI in pip package** — `tui/hoopoe-tui` is not bundled in the PyPI release yet; must be run manually from a clone of this repository

### Performance
- [x] **Numpy vectorisation** — reduced CPU usage per frame by replacing Python loops with matrix operations
- [x] **String join optimisation** — replaced `+=` string concatenation with list accumulation and `"".join()`
- [ ] **Dirty rendering** — only redraw lines that changed between frames; reduces terminal I/O for low-motion content

### Platform support
- [ ] **macOS** — minor adjustments needed (`ffmpeg` via Homebrew, no code changes expected)
- [ ] **Windows native** — replace `tty`/`termios` with `msvcrt` for key input, replace `SIGSTOP`/`SIGCONT` with Windows-compatible pause logic; WSL already works

## Star History

<a href="https://www.star-history.com/?repos=axol8002%2Fhoopoe-player&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/image?repos=axol8002/hoopoe-player&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/image?repos=axol8002/hoopoe-player&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/image?repos=axol8002/hoopoe-player&type=date&legend=top-left" />
 </picture>
</a>

## Support the creator

<a href="https://buymeacoffee.com/axol8002">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="50" alt="Buy Me A Coffee">
</a>

## License

MIT
