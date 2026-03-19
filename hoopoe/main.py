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
import datetime
import collections
import signal

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
    """Paint the entire terminal in one write."""
    buf = "\033[H"
    for line in lines:
        buf += line + "\033[K\r\n"
    if hud_line is not None:
        buf += "\033[7m" + hud_line + "\033[0m\033[K"
    sys.stdout.write(buf)
    sys.stdout.flush()


def save_screenshot(lines, hud_line=None):
    """Save current frame as ANSI colored text file (.ans)."""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"hoopoe_screenshot_{ts}.ans"
    with open(filename, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\033[K\n")
        if hud_line is not None:
            f.write("\033[7m" + hud_line + "\033[0m\033[K\n")
    return filename


QUALITY_MAP = {"low": 144, "medium": 360, "high": 480}


def get_video_capture(source, local=False, quality="high"):
    if local:
        if not os.path.exists(source):
            print(f"File not found: {source}")
            sys.exit(1)
        return cv2.VideoCapture(source), os.path.basename(source), False
    try:
        import yt_dlp
    except ImportError:
        print("yt-dlp not installed. Run: pip install yt-dlp")
        sys.exit(1)
    print("hoopoe-player - fetching video info...")
    height = QUALITY_MAP.get(quality, 480)
    ydl_opts = {"format": f"best[height<={height}]", "quiet": True,
                "js_runtimes": {"node": {}}, "remote_components": {"ejs:github"}}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(source, download=False)
        is_live = bool(info.get("is_live", False))
        return cv2.VideoCapture(info["url"]), info.get("title", "Unknown"), is_live


def get_audio_info(source, local=False):
    """Returns (url, is_live, is_hls) for the best audio stream."""
    if local:
        return source, False, False
    try:
        import yt_dlp
        opts = {"format": "bestaudio/best", "quiet": True,
                "js_runtimes": {"node": {}}, "remote_components": {"ejs:github"}}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(source, download=False)
            is_live = bool(info.get("is_live", False))
            url = info.get("url", "")
            protocol = info.get("protocol", "")
            is_hls = (protocol in ("m3u8", "m3u8_native", "dash")
                      or url.endswith(".m3u8") or "manifest" in url.lower())
            return url, is_live, is_hls
    except Exception:
        return None, False, False


class AudioPlayer:
    def __init__(self, url, is_live=False, is_hls=False):
        self.url = url
        self.volume = 50
        self.is_live = is_live
        self.is_hls = is_hls
        self._proc = None
        self._paused = False
        self._lock = threading.Lock()

    def start(self, offset=0):
        self._kill()
        self._paused = False
        cmd = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet",
               "-volume", str(self.volume)]

        if self.is_live or self.is_hls:
            cmd += ["-fflags", "nobuffer",
                    "-flags", "low_delay",
                    "-framedrop",
                    "-analyzeduration", "500000",
                    "-probesize", "500000"]
        elif offset > 0:
            cmd += ["-ss", str(offset)]

        cmd.append(self.url)
        with self._lock:
            self._proc = subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def _kill(self):
        with self._lock:
            if self._proc:
                try:
                    self._proc.send_signal(signal.SIGCONT)
                except Exception:
                    pass
                self._proc.terminate()
                try:
                    self._proc.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    self._proc.kill()
                self._proc = None
        self._paused = False

    def pause(self):
        with self._lock:
            if self._proc and not self._paused:
                try:
                    self._proc.send_signal(signal.SIGSTOP)
                    self._paused = True
                except Exception:
                    pass

    def resume(self):
        with self._lock:
            if self._proc and self._paused:
                try:
                    self._proc.send_signal(signal.SIGCONT)
                    self._paused = False
                except Exception:
                    pass

    def stop(self):
        self._kill()

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


def make_hud(paused, cur_frame, total_frames, fps, volume, mode, has_sound, cols,
             is_live=False, loop=False, screenshot_msg=None, real_fps=None, sync=False):
    elapsed  = format_time(cur_frame / fps)
    total    = "🔴LIVE" if is_live else (format_time(total_frames / fps) if total_frames else "--:--")
    state    = "⏸ PAUSE" if paused else "▶ PLAY"
    vol_str  = f" 🔊{volume}%" if has_sound else ""
    loop_str = " 🔁" if loop else ""
    sync_str = " 🔗SYNC" if sync else ""
    scr_str  = f" 📸{screenshot_msg}" if screenshot_msg else ""
    fps_str  = f" {real_fps:.1f}fps" if real_fps is not None else ""
    bar = (f"  {state}  {elapsed}/{total}{fps_str}  [{mode}]{sync_str}{loop_str}{scr_str}"
           f"  P shot  Spc pause  Q quit  ")
    return bar[:cols].ljust(cols)


class FpsCounter:
    """Rolling average FPS over the last N frames."""
    def __init__(self, window=30):
        self._times = collections.deque(maxlen=window)

    def tick(self):
        self._times.append(time.monotonic())

    @property
    def fps(self):
        if len(self._times) < 2:
            return 0.0
        span = self._times[-1] - self._times[0]
        return (len(self._times) - 1) / span if span > 0 else 0.0


def play_video(source, local=False, sound=False, mode="classic", hud=False,
               loop=False, sync=False, quality="medium"):
    try:
        cap, title, is_live = get_video_capture(source, local=local, quality=quality)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    video_fps    = cap.get(cv2.CAP_PROP_FPS) or 24
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Clear screen before any output so nothing bleeds into the first render
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

    print(f"Playing: {title}")
    extra = []
    if quality != "medium": extra.append(f"Quality: {quality}")
    if sound: extra.append("Sound on")
    if is_live: extra.append("Live stream")
    if loop:  extra.append("Loop on")
    if sync:  extra.append("Sync on")
    print(f"Mode: {mode}" + ((" | " + " | ".join(extra)) if extra else ""))
    print("Controls: Space pause  P screenshot  Q quit")
    time.sleep(1)

    audio = None
    if sound:
        audio_url, audio_is_live, audio_is_hls = get_audio_info(source, local=local)
        if audio_url:
            if audio_is_live or audio_is_hls:
                print("Note: Live/HLS stream detected — using low-latency audio mode.")
                time.sleep(1)
            audio = AudioPlayer(audio_url, is_live=audio_is_live, is_hls=audio_is_hls)
            audio.start()
        else:
            print("Could not get audio stream.")
            time.sleep(2)

    keys      = KeyListener()
    paused    = False
    cur_frame = 0
    fps_counter = FpsCounter()

    last_render_ms = 1000.0 / (video_fps or 24)  # rolling estimate of render cost

    # Wall clock anchor for --sync: audio starts at t=audio_start_wall, frame 0
    audio_start_wall = time.monotonic()
    pause_wall       = 0.0  # timestamp when pause started

    screenshot_msg       = None
    screenshot_msg_until = 0.0

    last_lines    = None
    last_hud_line = None
    last_cols, last_rows = get_terminal_size()

    sys.stdout.write("\033[?1049h\033[?25l\033[2J\033[H")
    sys.stdout.flush()

    def reset_sync(frame_num, audio_offset=None):
        nonlocal audio_start_wall
        if audio and audio_offset is not None:
            audio.start(offset=audio_offset)
            audio_start_wall = time.monotonic() - audio_offset

    try:
        while True:
            if not cap.isOpened():
                break

            # ── Key handling ──────────────────────────────────────────────────
            key = keys.pop()
            if key is not None:
                if key in (b'q', b'Q', b'\x03'):
                    break

                elif key == b' ':
                    paused = not paused
                    if paused:
                        if audio: audio.pause()
                        pause_wall = time.monotonic()
                    else:
                        if audio: audio.resume()
                        # Shift anchor forward by the time we were paused
                        audio_start_wall += time.monotonic() - pause_wall
                        reset_sync(cur_frame, audio_offset=None)

                elif key in (b'p', b'P'):
                    if last_lines:
                        fname = save_screenshot(last_lines, last_hud_line)
                        screenshot_msg       = os.path.basename(fname)
                        screenshot_msg_until = time.monotonic() + 3.0

            if screenshot_msg and time.monotonic() > screenshot_msg_until:
                screenshot_msg = None

            # ── Paused ────────────────────────────────────────────────────────
            if paused:
                cols, rows = get_terminal_size()
                resized = (cols, rows) != (last_cols, last_rows)
                if (resized or screenshot_msg is not None) and last_lines is not None:
                    if resized:
                        last_cols, last_rows = cols, rows
                        video_rows = rows - 1 if hud else rows
                        saved_pos = cur_frame
                        cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, saved_pos - 1))
                        ret, frame = cap.read()
                        cap.set(cv2.CAP_PROP_POS_FRAMES, saved_pos)
                        if ret:
                            last_lines = frame_to_lines(frame, cols, video_rows, mode)
                    if hud:
                        vol = audio.volume if audio else 0
                        last_hud_line = make_hud(
                            True, cur_frame, total_frames, video_fps, vol, mode,
                            bool(audio), cols, is_live, loop, screenshot_msg,
                            real_fps=None, sync=sync)
                    render_frame(last_lines, last_hud_line)
                time.sleep(0.05)
                continue

            # ── A/V sync: decide whether to drop this frame ───────────────────
            drop_frame = False
            if sync:
                audio_pos_s    = time.monotonic() - audio_start_wall
                expected_frame = audio_pos_s * video_fps
                debt           = expected_frame - cur_frame
                if debt > 1.0:
                    drop_frame = True

            # ── Read & render ─────────────────────────────────────────────────
            t_frame_start = time.monotonic()

            ret, frame = cap.read()
            if not ret:
                if loop:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    cur_frame = 0
                    reset_sync(0, audio_offset=0)
                    continue
                else:
                    break

            cur_frame += 1

            if not drop_frame:
                fps_counter.tick()
                cols, rows = get_terminal_size()
                last_cols, last_rows = cols, rows
                video_rows = rows - 1 if hud else rows

                last_lines = frame_to_lines(frame, cols, video_rows, mode)
                last_hud_line = None
                if hud:
                    vol = audio.volume if audio else 0
                    last_hud_line = make_hud(
                        False, cur_frame, total_frames, video_fps, vol, mode,
                        bool(audio), cols, is_live, loop, screenshot_msg,
                        real_fps=fps_counter.fps, sync=sync)

                render_frame(last_lines, last_hud_line)

                render_ms = (time.monotonic() - t_frame_start) * 1000
                last_render_ms = last_render_ms * 0.7 + render_ms * 0.3

                wait = (1.0 / video_fps) - render_ms / 1000
                if wait > 0:
                    time.sleep(wait)

    except KeyboardInterrupt:
        pass
    finally:
        keys.stop()
        cap.release()
        if audio:
            audio.stop()
        sys.stdout.write("\033[?25h\033[0m\033[2J\033[H\033[?1049l")
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
    parser.add_argument("--loop",         action="store_true",
                        help="Loop video automatically when it ends")
    parser.add_argument("--sync",         action="store_true",
                        help="Sync video to audio: drop frames when rendering is slow")
    parser.add_argument("--quality",      choices=["low", "medium", "high"], default="medium",
                        help="Stream resolution: low (144p), medium (360p, default), high (480p)")
    args = parser.parse_args()
    play_video(args.source, local=args.local, sound=args.sound,
               mode=args.mode, hud=args.hud, loop=args.loop, sync=args.sync, quality=args.quality)


if __name__ == "__main__":
    main()
