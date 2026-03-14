#!/usr/bin/env python3
"""
hoopoe - Play videos in your terminal as colorful ASCII art
"""

import sys
import argparse
import time
import os
import tty
import termios
import threading
import subprocess

import cv2

CHAR_MODES = {
    "classic": " .:-=+*#%@",
    "blocks":  " ░▒▓█",
    "braille": " ⠁⠃⠇⠿⣿",
    "minimal": " ·•●■",
    "invert":  "@%#*+=-:. ",
    "nocolor": " .:-=+*#%@",
}


def get_terminal_size():
    size = os.get_terminal_size()
    return size.columns, size.lines


def frame_to_lines(frame, width, height, mode):
    """Convert a frame to a list of strings, one per terminal row."""
    chars = CHAR_MODES.get(mode, CHAR_MODES["classic"])
    # Each character is ~2x taller than wide, so use width directly
    frame_resized = cv2.resize(frame, (width, height))
    gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

    lines = []
    for y in range(height):
        row = ""
        for x in range(width):
            brightness = gray[y, x]
            char = chars[int(brightness / 255 * (len(chars) - 1))]
            if mode == "nocolor":
                row += char
            elif mode == "invert":
                b, g, r = frame_resized[y, x]
                row += f"\033[48;2;{r};{g};{b}m\033[38;2;0;0;0m{char}\033[0m"
            else:
                b, g, r = frame_resized[y, x]
                row += f"\033[38;2;{r};{g};{b}m{char}\033[0m"
        lines.append(row)
    return lines


def render_frame(lines, hud_line=None):
    """
    Paint the entire terminal in one write:
    - Move to 1,1
    - Print each line followed by \033[K (erase to end of line) and \r\n
    - If hud_line, paint it on the last row
    """
    buf = "\033[H"  # cursor to top-left
    for line in lines:
        buf += line + "\033[K\r\n"
    if hud_line is not None:
        buf += "\033[7m" + hud_line + "\033[0m\033[K"
    sys.stdout.write(buf)
    sys.stdout.flush()


def get_video_capture(source, local=False):
    if local:
        if not os.path.exists(source):
            print(f"File not found: {source}")
            sys.exit(1)
        return cv2.VideoCapture(source), os.path.basename(source)
    try:
        import yt_dlp
    except ImportError:
        print("yt-dlp not installed. Run: pip install yt-dlp")
        sys.exit(1)
    print("hoopoe-player - fetching video info...")
    ydl_opts = {"format": "best[height<=480]", "quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(source, download=False)
        return cv2.VideoCapture(info["url"]), info.get("title", "Unknown")


def get_audio_url(source, local=False):
    if local:
        return source
    try:
        import yt_dlp
        with yt_dlp.YoutubeDL({"format": "bestaudio", "quiet": True}) as ydl:
            return ydl.extract_info(source, download=False)["url"]
    except Exception:
        return None


class AudioPlayer:
    def __init__(self, url):
        self.url = url
        self.volume = 50
        self._proc = None

    def start(self, offset=0):
        self._kill()
        self._proc = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet",
             "-volume", str(self.volume), "-ss", str(int(offset)), self.url],
            stdin=subprocess.DEVNULL
        )

    def _kill(self):
        if self._proc:
            self._proc.terminate()
            self._proc = None

    def stop(self):
        self._kill()

    def change_volume(self, delta, offset=0):
        self.volume = max(0, min(100, self.volume + delta))
        self.start(offset=offset)


class KeyListener:
    def __init__(self):
        self.key = None
        self._stop = False
        self._fd = sys.stdin.fileno()
        self._old = termios.tcgetattr(self._fd)
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        tty.setraw(self._fd)
        while not self._stop:
            try:
                self.key = os.read(self._fd, 3)
            except Exception:
                break

    def stop(self):
        self._stop = True
        try:
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old)
        except Exception:
            pass

    def pop(self):
        k, self.key = self.key, None
        return k


def format_time(secs):
    secs = max(0, int(secs))
    m, s = divmod(secs, 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def make_hud(paused, cur_frame, total_frames, fps, volume, mode, has_sound, cols):
    elapsed = format_time(cur_frame / fps)
    total   = format_time(total_frames / fps) if total_frames else "--:--"
    state   = "⏸ PAUSE" if paused else "▶ PLAY"
    vol_str = f" 🔊{volume}%" if has_sound else ""
    bar = f"  {state}  {elapsed}/{total}  [{mode}]{vol_str}  ←→ 10s  ↑↓ vol  Spc pause  Q quit  "
    return bar[:cols].ljust(cols)


def play_video(source, local=False, sound=False, mode="classic", hud=False):
    try:
        cap, title = get_video_capture(source, local=local)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    fps          = cap.get(cv2.CAP_PROP_FPS) or 24
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_delay  = 1.0 / fps

    print(f"Playing: {title}")
    print(f"Mode: {mode}" + (" | Sound on" if sound else " | Sound off"))
    print("Controls: Space pause  ←→ seek  ↑↓ volume  Q quit")
    time.sleep(1)

    audio = None
    if sound:
        url = get_audio_url(source, local=local)
        if url:
            audio = AudioPlayer(url)
            audio.start()
        else:
            print("Could not get audio stream.")

    keys    = KeyListener()
    paused  = False
    cur_frame = 0

    # Hide cursor + clear screen once
    sys.stdout.write("\033[?25l\033[2J")
    sys.stdout.flush()

    try:
        while cap.isOpened():
            # ── Keys ──────────────────────────────────────────────────────────
            key = keys.pop()
            if key is not None:
                if key in (b'q', b'Q', b'\x03'):
                    break
                elif key == b' ':
                    paused = not paused
                    if audio:
                        audio.stop() if paused else audio.start(offset=cur_frame / fps)
                elif key == b'\x1b[C':          # →
                    cur_frame = min(total_frames, cur_frame + int(fps * 10))
                    cap.set(cv2.CAP_PROP_POS_FRAMES, cur_frame)
                    if audio: audio.start(offset=cur_frame / fps)
                elif key == b'\x1b[D':          # ←
                    cur_frame = max(0, cur_frame - int(fps * 10))
                    cap.set(cv2.CAP_PROP_POS_FRAMES, cur_frame)
                    if audio: audio.start(offset=cur_frame / fps)
                elif key == b'\x1b[A' and audio:  # ↑
                    audio.change_volume(+10, offset=cur_frame / fps)
                elif key == b'\x1b[B' and audio:  # ↓
                    audio.change_volume(-10, offset=cur_frame / fps)

            if paused:
                time.sleep(0.05)
                continue

            # ── Read frame ────────────────────────────────────────────────────
            t0 = time.time()
            ret, frame = cap.read()
            if not ret:
                break
            cur_frame += 1

            cols, rows = get_terminal_size()
            video_rows = rows - 1 if hud else rows

            lines    = frame_to_lines(frame, cols, video_rows, mode)
            hud_line = None
            if hud:
                vol = audio.volume if audio else 0
                hud_line = make_hud(paused, cur_frame, total_frames, fps, vol, mode, bool(audio), cols)

            render_frame(lines, hud_line)

            elapsed = time.time() - t0
            wait    = frame_delay - elapsed
            if wait > 0:
                time.sleep(wait)

    except KeyboardInterrupt:
        pass
    finally:
        keys.stop()
        cap.release()
        if audio:
            audio.stop()
        sys.stdout.write("\033[?25h\033[0m\033[2J\033[H")
        sys.stdout.flush()
        print("hoopoe stopped. See you next time!")


def main():
    parser = argparse.ArgumentParser(
        description="hoopoe-player - Videos as colorful ASCII art in your terminal",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("source", help="YouTube URL or path to local video file")
    parser.add_argument("-l", "--local",  action="store_true", help="Play a local video file")
    parser.add_argument("-s", "--sound",  action="store_true", help="Enable audio (requires ffmpeg)")
    parser.add_argument("-m", "--mode",   choices=list(CHAR_MODES.keys()), default="classic",
                        help="Rendering mode: classic blocks braille minimal invert nocolor")
    parser.add_argument("--hud",          action="store_true",
                        help="Show status bar at the bottom")
    args = parser.parse_args()
    play_video(args.source, local=args.local, sound=args.sound, mode=args.mode, hud=args.hud)


if __name__ == "__main__":
    main()
