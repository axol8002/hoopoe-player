# Changelog

## [0.1.5] - 2026-05-09

### Added
- Image rendering (`-i`) — display a local image as ASCII art in the terminal
- Output to file (`--output`) — save the full render as an ANSI `.ans` file; accepts a file path or directory; works with video, webcam, and image modes
- ANSI playback (`--play`) — replay a recorded `.ans` file at the original framerate; supports pause and FPS override (`--fps`)
- TUI launcher (`tui/hoopoe-tui`) — interactive Bash menu with persistent settings stored in `~/.config/hoopoe-launcher.conf`
- Broader URL support — Twitch, Vimeo, direct video URLs and any of the sites supported by yt-dlp work out of the box via the generic extractor
- `--legacy-color` flag — renders using the standard 16-color ANSI palette instead of 24-bit RGB; accepts `rgb` (fast, nearest color by Euclidean RGB distance) or `lab` (perceptual, nearest color by CIE LAB distance); defaults to `rgb` when no value is given
- `--no-color` flag — disables all color output; replaces the former `-m nocolor` mode and works with any character mode

### Fixed
- `--fps` now rejects `0` and negative values with a clear error message instead of silently misbehaving

### Changed
- `-m nocolor` has been removed; use `--no-color` instead

---

## [0.1.4] - 2026-04-02

### Added
- `--fps` flag — cap the rendering framerate to reduce CPU usage (works with video and webcam)

### Changed
- Refactored ANSI escape generation into a dedicated `get_ansi()` helper, reducing duplicated logic across rendering paths

---

## [0.1.3] - 2026-03-27

### Added
- Webcam support (`--webcam`, `--camera`)
- Flip flag (`--flip h/v/hv`) for webcam feed
- Brightness inversion (`--invert`) for any character mode
- Highlight mode (`--highlight`) — renders color as background for any character mode
- New `solid` character mode — pure color blocks using background-colored spaces

### Changed
- Replaced Python pixel loops in `frame_to_lines()` with numpy vectorization
- Replaced `+=` string concatenation with `"".join()` for faster frame assembly
- Removed `invert` from `CHAR_MODES` (replaced by `--highlight` flag)

---

## [0.1.2] - 2026-03-19

### Added
- A/V sync mode (`--sync`) — drops frames to stay locked to the audio clock
- Loop mode (`--loop`) — automatically restarts video and audio at the end
- Alternate screen buffer — terminal history is preserved on exit
- Screenshot feature (`P`) — saves current frame as timestamped `.ans` ANSI file
- Dynamic terminal resize support, including while paused
- HUD (`--hud`) — status bar with timestamp, real-time FPS, mode and controls
- Live stream support with low-latency audio mode

---

## [0.1.1] - 2026-03-17

### Added
- Audio playback via ffplay (`-s`)
- Quality selector (`--quality low/medium/high`)
- Multiple character modes: classic, blocks, braille, minimal, invert, nocolor

---

## [0.1.0] - 2026-03-14

### Added
- Initial release
- YouTube and local video playback as ASCII art
- True color (24-bit RGB) support
