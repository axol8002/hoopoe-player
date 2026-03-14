![hoopoe-player logo](assets/logo.png)

# hoopoe-player

> Play any video as colorful ASCII art directly in your terminal.

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

## Usage

```bash
# Play a YouTube video
hoopoe https://www.youtube.com/watch?v=xxxxx

# Play a local file
hoopoe -l video.mp4

# Enable audio
hoopoe -s https://www.youtube.com/watch?v=xxxxx

# Change character mode
hoopoe -m blocks https://www.youtube.com/watch?v=xxxxx

# Show status bar (time, volume, controls)
hoopoe --hud https://www.youtube.com/watch?v=xxxxx

# Combine options
hoopoe -l -s -m invert --hud video.mp4
```

## Controls

| Key | Action |
|-----|--------|
| `Space` | Pause / Play |
| `←` / `→` | Seek −10s / +10s |
| `↑` / `↓` | Volume +10 / −10 (only with `-s`) |
| `Q` or `Ctrl+C` | Quit |

## Character modes

| Mode | Style |
|------|-------|
| `classic` | `. : - = + * # % @` — default, coloured |
| `blocks` | `░ ▒ ▓ █` — bold blocks, coloured |
| `braille` | `⠁ ⠃ ⠇ ⠿ ⣿` — dense dots, coloured |
| `minimal` | `· • ● ■` — clean and minimal, coloured |
| `invert` | colour as background — selection effect |
| `nocolor` | classic chars, no colour — for legacy terminals |

## Requirements

- Python 3.8+
- ffmpeg (optional, needed for `-s` audio)
- A terminal with true color support (for all modes except `nocolor`)

## Roadmap

- [ ] Fix audio/video sync — audio can drift ahead when rendering is slow
- [ ] Fix scaling when paused — terminal resize not applied until next frame
- [ ] Optimize rendering performance — reduce CPU usage per frame
- [ ] Screenshot to file — press a key to save the current frame as a colored text file (ANSI)
- [ ] Loop mode — replay the video automatically when it ends (`--loop`)

## License

MIT
