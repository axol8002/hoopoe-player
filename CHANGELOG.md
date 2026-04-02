# Changelog

## [0.1.4] - 2026-04-02

### Added
- `--fps` flag — cap the rendering framerate to reduce CPU usage (works with video and webcam)

### Changed
- Refactored ANSI escape generation into a dedicated `get_ansi()` helper, reducing duplicated logic across rendering paths

### Known issues
- `--fps` does not validate against 0 or negative values (will be fixed in a future release)
- `--fps` forces `sync = True` even when audio is disabled (will be fixed in a future release)

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
