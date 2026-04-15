#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, asdict
from http import HTTPStatus
from pathlib import Path
from urllib import error, request

import numpy as np


@dataclass
class ChromeWindow:
    window_id: str
    desktop: str
    wm_class: str
    host: str
    title: str


@dataclass
class CaptureResult:
    index: int
    url: str
    item_dir: Path
    window: ChromeWindow | None
    screenshot_paths: list[Path]
    interaction_error: str
    skipped_capture: bool
    result_summary: str
    precheck_status_code: int | None
    precheck_location: str


@dataclass
class PrecheckResult:
    skipped_capture: bool
    status_code: int | None
    location: str
    result_summary: str


def run(cmd: list[str], check: bool = True, capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=check,
        text=True,
        capture_output=capture,
    )


def require_binary(name: str) -> None:
    if not shutil_which(name):
        raise SystemExit(f"missing required binary: {name}")


def shutil_which(name: str) -> str | None:
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(directory) / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def list_chrome_windows() -> list[ChromeWindow]:
    result = run(["wmctrl", "-lx"])
    windows: list[ChromeWindow] = []
    for raw_line in result.stdout.splitlines():
        parts = raw_line.split(None, 4)
        if len(parts) < 5:
            continue
        wm_class = parts[2].lower()
        if "chrome" not in wm_class and "chromium" not in wm_class:
            continue
        windows.append(
            ChromeWindow(
                window_id=parts[0],
                desktop=parts[1],
                wm_class=parts[2],
                host=parts[3],
                title=parts[4],
            )
        )
    return windows


def choose_window(windows: list[ChromeWindow], hint: str | None) -> ChromeWindow:
    if not windows:
        raise SystemExit("no visible Chrome window found")
    if hint:
        lowered = hint.lower()
        for window in windows:
            if lowered in window.title.lower():
                return window
    return windows[0]


def get_active_window_id() -> str | None:
    result = run(["xprop", "-root", "_NET_ACTIVE_WINDOW"], check=False)
    match = re.search(r"window id # (0x[0-9a-fA-F]+)", result.stdout)
    if not match:
        return None
    return match.group(1).lower()


def choose_target_window(windows: list[ChromeWindow], hint: str | None, active_window_id: str | None, before_ids: set[str]) -> ChromeWindow:
    if hint:
        return choose_window(windows, hint)
    if active_window_id:
        for window in windows:
            if window.window_id.lower() == active_window_id:
                return window
    new_windows = [window for window in windows if window.window_id not in before_ids]
    if new_windows:
        return new_windows[-1]
    return choose_window(windows, None)


def get_window_geometry(window_id: str) -> dict[str, int]:
    result = run(["xwininfo", "-id", window_id])
    text = result.stdout

    def find_int(pattern: str) -> int:
        match = re.search(pattern, text)
        if not match:
            raise SystemExit(f"failed to parse window geometry for {pattern}")
        return int(match.group(1))

    return {
        "x": find_int(r"Absolute upper-left X:\s+(-?\d+)"),
        "y": find_int(r"Absolute upper-left Y:\s+(-?\d+)"),
        "width": find_int(r"Width:\s+(\d+)"),
        "height": find_int(r"Height:\s+(\d+)"),
    }


def activate_window(window_id: str) -> None:
    run(["wmctrl", "-ia", window_id], capture=False)
    time.sleep(1.0)


def open_url(url: str) -> None:
    chrome = shutil_which("google-chrome") or shutil_which("google-chrome-stable") or shutil_which("chromium")
    if not chrome:
        raise SystemExit("no Chrome/Chromium binary found")
    subprocess.Popen([chrome, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def save_window_screenshot(path: Path) -> None:
    run(["gnome-screenshot", "-w", "-f", str(path)], capture=False)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_x11_session() -> None:
    session_type = os.environ.get("XDG_SESSION_TYPE", "").strip().lower()
    if session_type and session_type != "x11":
        raise SystemExit(f"unsupported session type: {session_type}")
    if not os.environ.get("DISPLAY"):
        raise SystemExit("missing DISPLAY for X11 session")


def extract_urls(raw_inputs: list[str]) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for raw_input in raw_inputs:
        matches = re.findall(r"https?://[^\s<>'\"`]+", raw_input)
        if not matches and raw_input.startswith(("http://", "https://")):
            matches = [raw_input]
        for match in matches:
            url = match.rstrip(".,;:!?)]}>'\"，。；：！？）】")
            if url and url not in seen:
                seen.add(url)
                urls.append(url)
    if not urls:
        raise SystemExit("no URL found in input")
    return urls


class NoRedirectHandler(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[override]
        return None


def precheck_url(url: str, timeout: float = 10.0) -> PrecheckResult:
    opener = request.build_opener(NoRedirectHandler)
    req = request.Request(
        url,
        method="HEAD",
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*",
        },
    )
    status_code: int | None = None
    location = ""
    try:
        with opener.open(req, timeout=timeout) as response:
            status_code = response.getcode()
            location = response.headers.get("Location", "")
    except error.HTTPError as exc:
        status_code = exc.code
        location = exc.headers.get("Location", "")
    except error.URLError:
        return PrecheckResult(
            skipped_capture=False,
            status_code=None,
            location="",
            result_summary="",
        )
    except Exception:
        return PrecheckResult(
            skipped_capture=False,
            status_code=None,
            location="",
            result_summary="",
        )
    if status_code == HTTPStatus.FOUND:
        return PrecheckResult(
            skipped_capture=True,
            status_code=status_code,
            location=location,
            result_summary="页面不存在或已下架",
        )
    if status_code == HTTPStatus.NOT_FOUND and ("/404" in url or "/404" in location):
        return PrecheckResult(
            skipped_capture=True,
            status_code=status_code,
            location=location,
            result_summary="页面不存在或已下架",
        )
    return PrecheckResult(
        skipped_capture=False,
        status_code=status_code,
        location=location,
        result_summary="",
    )


def load_rgb_image(path: Path) -> np.ndarray:
    probe = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=s=x:p=0",
            str(path),
        ]
    )
    width_text, height_text = probe.stdout.strip().split("x")
    width = int(width_text)
    height = int(height_text)
    frame = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(path),
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ],
        check=True,
        capture_output=True,
    )
    rgb = np.frombuffer(frame.stdout, dtype=np.uint8)
    return rgb.reshape((height, width, 3))


def dilate_mask(mask: np.ndarray, radius_y: int, radius_x: int) -> np.ndarray:
    height, width = mask.shape
    dilated = np.zeros_like(mask, dtype=bool)
    for dy in range(-radius_y, radius_y + 1):
        src_y0 = max(0, -dy)
        src_y1 = min(height, height - dy)
        dst_y0 = max(0, dy)
        dst_y1 = min(height, height + dy)
        for dx in range(-radius_x, radius_x + 1):
            src_x0 = max(0, -dx)
            src_x1 = min(width, width - dx)
            dst_x0 = max(0, dx)
            dst_x1 = min(width, width + dx)
            dilated[dst_y0:dst_y1, dst_x0:dst_x1] |= mask[src_y0:src_y1, src_x0:src_x1]
    return dilated


def connected_components(mask: np.ndarray) -> list[tuple[int, int, int, int]]:
    height, width = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    components: list[tuple[int, int, int, int]] = []
    points = np.argwhere(mask)
    for start_y, start_x in points:
        if visited[start_y, start_x]:
            continue
        stack = [(int(start_y), int(start_x))]
        visited[start_y, start_x] = True
        min_y = max_y = int(start_y)
        min_x = max_x = int(start_x)
        while stack:
            y, x = stack.pop()
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            for next_y in range(max(0, y - 1), min(height, y + 2)):
                for next_x in range(max(0, x - 1), min(width, x + 2)):
                    if not mask[next_y, next_x] or visited[next_y, next_x]:
                        continue
                    visited[next_y, next_x] = True
                    stack.append((next_y, next_x))
        components.append((min_y, max_y, min_x, max_x))
    return components


def find_expand_reply_targets(path: Path) -> list[tuple[int, int]]:
    image = load_rgb_image(path)
    height, width, _ = image.shape
    x0 = int(width * 0.62)
    x1 = int(width * 0.97)
    y0 = int(height * 0.16)
    y1 = int(height * 0.96)
    cropped = image[y0:y1, x0:x1]
    red = cropped[:, :, 0].astype(np.int16)
    green = cropped[:, :, 1].astype(np.int16)
    blue = cropped[:, :, 2].astype(np.int16)
    blue_mask = (
        (blue >= 85)
        & (blue - red >= 18)
        & (blue - green >= 6)
        & (green <= 190)
    )
    dilated = dilate_mask(blue_mask, radius_y=1, radius_x=6)
    candidates: list[tuple[int, int, int, int]] = []
    crop_height, crop_width = blue_mask.shape
    for min_y, max_y, min_x, max_x in connected_components(dilated):
        box_width = max_x - min_x + 1
        box_height = max_y - min_y + 1
        pixel_count = int(blue_mask[min_y:max_y + 1, min_x:max_x + 1].sum())
        center_x = min_x + box_width // 2
        if box_width < 35 or box_width > 260:
            continue
        if box_height < 8 or box_height > 36:
            continue
        if pixel_count < 18 or pixel_count > 1200:
            continue
        if center_x > int(crop_width * 0.72):
            continue
        if min_y < int(crop_height * 0.05):
            continue
        candidates.append((min_y, max_y, min_x, max_x))
    merged: list[tuple[int, int, int, int]] = []
    for candidate in sorted(candidates, key=lambda item: (item[0], item[2])):
        if not merged:
            merged.append(candidate)
            continue
        prev_min_y, prev_max_y, prev_min_x, prev_max_x = merged[-1]
        min_y, max_y, min_x, max_x = candidate
        if abs(min_y - prev_min_y) <= 8 and abs(min_x - prev_min_x) <= 18:
            merged[-1] = (
                min(prev_min_y, min_y),
                max(prev_max_y, max_y),
                min(prev_min_x, min_x),
                max(prev_max_x, max_x),
            )
            continue
        merged.append(candidate)
    return [
        (x0 + (min_x + max_x) // 2, y0 + (min_y + max_y) // 2)
        for min_y, max_y, min_x, max_x in merged
    ]


class XController:
    def __init__(self) -> None:
        try:
            from Xlib import X, XK, display  # type: ignore
            from Xlib.ext import xtest  # type: ignore

            self.backend = "python-xlib"
            self.X = X
            self.XK = XK
            self.display = display.Display()
            self.root = self.display.screen().root
            self.xtest = xtest
        except ModuleNotFoundError:
            self.backend = "ctypes"
            self._init_ctypes()

    def _init_ctypes(self) -> None:
        self.lib_x11 = ctypes.cdll.LoadLibrary("libX11.so.6")
        self.lib_xtst = ctypes.cdll.LoadLibrary("libXtst.so.6")
        self.lib_x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
        self.lib_x11.XOpenDisplay.restype = ctypes.c_void_p
        self.lib_x11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
        self.lib_x11.XDefaultRootWindow.restype = ctypes.c_ulong
        self.lib_x11.XStringToKeysym.argtypes = [ctypes.c_char_p]
        self.lib_x11.XStringToKeysym.restype = ctypes.c_ulong
        self.lib_x11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        self.lib_x11.XKeysymToKeycode.restype = ctypes.c_uint
        self.lib_x11.XWarpPointer.argtypes = [
            ctypes.c_void_p,
            ctypes.c_ulong,
            ctypes.c_ulong,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_int,
            ctypes.c_int,
        ]
        self.lib_x11.XWarpPointer.restype = ctypes.c_int
        self.lib_x11.XFlush.argtypes = [ctypes.c_void_p]
        self.lib_x11.XFlush.restype = ctypes.c_int
        self.lib_x11.XSync.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.lib_x11.XSync.restype = ctypes.c_int
        self.lib_xtst.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
        self.lib_xtst.XTestFakeKeyEvent.restype = ctypes.c_int
        self.lib_xtst.XTestFakeButtonEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
        self.lib_xtst.XTestFakeButtonEvent.restype = ctypes.c_int
        self.display = self.lib_x11.XOpenDisplay(None)
        if not self.display:
            raise RuntimeError("failed to open X11 display")
        self.root = self.lib_x11.XDefaultRootWindow(self.display)

    def press_key(self, key_name: str) -> None:
        if self.backend == "python-xlib":
            keycode = self.display.keysym_to_keycode(self.XK.string_to_keysym(key_name))
            self.xtest.fake_input(self.display, self.X.KeyPress, keycode)
            self.xtest.fake_input(self.display, self.X.KeyRelease, keycode)
            self.display.sync()
            return
        keysym = self.lib_x11.XStringToKeysym(key_name.encode("utf-8"))
        keycode = self.lib_x11.XKeysymToKeycode(self.display, keysym)
        self.lib_xtst.XTestFakeKeyEvent(self.display, keycode, 1, 0)
        self.lib_xtst.XTestFakeKeyEvent(self.display, keycode, 0, 0)
        self.lib_x11.XSync(self.display, 0)

    def click(self, x: int, y: int) -> None:
        if self.backend == "python-xlib":
            self.root.warp_pointer(x, y)
            self.display.sync()
            time.sleep(0.2)
            self.xtest.fake_input(self.display, self.X.ButtonPress, 1)
            self.xtest.fake_input(self.display, self.X.ButtonRelease, 1)
            self.display.sync()
            return
        self.lib_x11.XWarpPointer(self.display, 0, self.root, 0, 0, 0, 0, x, y)
        self.lib_x11.XFlush(self.display)
        time.sleep(0.2)
        self.lib_xtst.XTestFakeButtonEvent(self.display, 1, 1, 0)
        self.lib_xtst.XTestFakeButtonEvent(self.display, 1, 0, 0)
        self.lib_x11.XSync(self.display, 0)

    def scroll_down(self, steps: int) -> None:
        if self.backend == "python-xlib":
            for _ in range(steps):
                self.xtest.fake_input(self.display, self.X.ButtonPress, 5)
                self.xtest.fake_input(self.display, self.X.ButtonRelease, 5)
                self.display.sync()
                time.sleep(0.12)
            return
        for _ in range(steps):
            self.lib_xtst.XTestFakeButtonEvent(self.display, 5, 1, 0)
            self.lib_xtst.XTestFakeButtonEvent(self.display, 5, 0, 0)
            self.lib_x11.XSync(self.display, 0)
            time.sleep(0.12)


def expand_visible_reply_links(
    geometry: dict[str, int],
    controller: XController,
    screenshot_dir: Path,
    screenshot_index: int,
) -> int:
    probe_path = screenshot_dir / f"_expand_probe_{screenshot_index}.png"
    click_targets: list[tuple[int, int]] = []
    attempts = 0
    while attempts < 8:
        save_window_screenshot(probe_path)
        targets = find_expand_reply_targets(probe_path)
        next_target = None
        for target_x, target_y in targets:
            if any(abs(target_x - clicked_x) <= 14 and abs(target_y - clicked_y) <= 10 for clicked_x, clicked_y in click_targets):
                continue
            next_target = (target_x, target_y)
            break
        if next_target is None:
            break
        controller.click(geometry["x"] + next_target[0], geometry["y"] + next_target[1])
        click_targets.append(next_target)
        attempts += 1
        time.sleep(0.9)
    probe_path.unlink(missing_ok=True)
    return len(click_targets)


def build_report(results: list[CaptureResult], root_dir: Path) -> str:
    lines = [
        "# Chrome Visual Extraction",
        "",
        f"- Total items: {len(results)}",
        "",
    ]
    for result in results:
        lines.extend(
            [
                f"## Item {result.index}",
                "",
                f"- URL: {result.url}",
            ]
        )
        if result.result_summary:
            lines.append(f"- Result: {result.result_summary}")
        if result.precheck_status_code is not None:
            lines.append(f"- HTTP precheck: {result.precheck_status_code}")
        if result.precheck_location:
            lines.append(f"- Redirect location: {result.precheck_location}")
        if result.skipped_capture:
            lines.append("")
            continue
        screenshot_text = ", ".join(str(path.relative_to(root_dir)) for path in result.screenshot_paths)
        lines.extend(
            [
                f"- Output dir: {result.item_dir.relative_to(root_dir)}",
                f"- Window title: {result.window.title if result.window else 'none'}",
                f"- Screenshots: {screenshot_text}",
                f"- Interaction error: {result.interaction_error or 'none'}",
                "",
                "### To Fill After Visual Review",
                "",
                "- Author:",
                "- Note title:",
                "- Publish time / location:",
                "- Media type:",
                "- Visible text:",
                "- Visible comments:",
                "- Engagement data:",
                "- Notes:",
                "",
            ]
        )
    return "\n".join(lines)


def capture_item(
    url: str,
    item_index: int,
    root_dir: Path,
    wait_seconds: float,
    window_hint: str,
    skip_comment_scroll: bool,
    max_pages: int,
    scroll_steps: int,
) -> CaptureResult:
    item_dir = root_dir / f"item_{item_index}"
    item_dir.mkdir(parents=True, exist_ok=True)
    precheck = precheck_url(url)
    if precheck.skipped_capture:
        manifest = {
            "item_index": item_index,
            "url": url,
            "window": None,
            "screenshots": [],
            "output_dir": str(item_dir),
            "interaction_error": "",
            "skipped_capture": True,
            "result_summary": precheck.result_summary,
            "precheck_status_code": precheck.status_code,
            "precheck_location": precheck.location,
        }
        (item_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return CaptureResult(
            index=item_index,
            url=url,
            item_dir=item_dir,
            window=None,
            screenshot_paths=[],
            interaction_error="",
            skipped_capture=True,
            result_summary=precheck.result_summary,
            precheck_status_code=precheck.status_code,
            precheck_location=precheck.location,
        )
    screenshot_dir = item_dir / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    before_ids = {window.window_id for window in list_chrome_windows()}
    open_url(url)
    time.sleep(wait_seconds)
    windows = list_chrome_windows()
    active_window_id = get_active_window_id()
    target_window = choose_target_window(windows, window_hint or None, active_window_id, before_ids)
    activate_window(target_window.window_id)
    screenshot_paths: list[Path] = []
    seen_hashes: set[str] = set()
    interaction_error = ""
    try:
        geometry = get_window_geometry(target_window.window_id)
        controller = XController()
        controller.press_key("Escape")
        time.sleep(0.5)
        comment_x = geometry["x"] + int(geometry["width"] * 0.87)
        comment_y = geometry["y"] + int(geometry["height"] * 0.62)
        controller.click(comment_x, comment_y)
        time.sleep(0.5)
        while len(screenshot_paths) < max_pages:
            expand_visible_reply_links(geometry, controller, screenshot_dir, len(screenshot_paths) + 1)
            next_page = screenshot_dir / f"page_{len(screenshot_paths) + 1}.png"
            save_window_screenshot(next_page)
            next_hash = file_sha256(next_page)
            if next_hash in seen_hashes:
                next_page.unlink(missing_ok=True)
                break
            seen_hashes.add(next_hash)
            screenshot_paths.append(next_page)
            if skip_comment_scroll:
                break
            controller.scroll_down(scroll_steps)
            time.sleep(0.8)
    except Exception as exc:  # noqa: BLE001
        interaction_error = str(exc)
        if not screenshot_paths:
            fallback_path = screenshot_dir / "page_1.png"
            save_window_screenshot(fallback_path)
            screenshot_paths.append(fallback_path)
    manifest = {
        "item_index": item_index,
        "url": url,
        "window": asdict(target_window),
        "screenshots": [str(path) for path in screenshot_paths],
        "output_dir": str(item_dir),
        "interaction_error": interaction_error,
        "skipped_capture": False,
        "result_summary": "",
        "precheck_status_code": precheck.status_code,
        "precheck_location": precheck.location,
    }
    (item_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return CaptureResult(
        index=item_index,
        url=url,
        item_dir=item_dir,
        window=target_window,
        screenshot_paths=screenshot_paths,
        interaction_error=interaction_error,
        skipped_capture=False,
        result_summary="",
        precheck_status_code=precheck.status_code,
        precheck_location=precheck.location,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Visually capture one or more pages from local GUI Chrome.")
    parser.add_argument("inputs", nargs="+", help="One or more URLs or raw text blocks containing URLs")
    parser.add_argument("--out-dir", default="", help="Directory for screenshots and metadata")
    parser.add_argument("--wait-seconds", type=float, default=8.0, help="Wait after opening the URL")
    parser.add_argument("--window-hint", default="", help="Prefer a Chrome window whose title contains this text")
    parser.add_argument("--skip-comment-scroll", action="store_true", help="Only capture the initial page")
    parser.add_argument("--max-pages", type=int, default=20, help="Maximum screenshots to keep for one link")
    parser.add_argument("--scroll-steps", type=int, default=8, help="Mouse-wheel steps between screenshots")
    args = parser.parse_args()

    require_binary("wmctrl")
    require_binary("xwininfo")
    require_binary("gnome-screenshot")
    require_binary("xprop")
    require_binary("ffmpeg")
    require_binary("ffprobe")
    require_x11_session()

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.out_dir) if args.out_dir else Path.cwd() / "tmp" / f"chrome_capture_{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    urls = extract_urls(args.inputs)
    results = [
        capture_item(
            url,
            index,
            out_dir,
            args.wait_seconds,
            args.window_hint,
            args.skip_comment_scroll,
            args.max_pages,
            args.scroll_steps,
        )
        for index, url in enumerate(urls, start=1)
    ]
    (out_dir / "REPORT.md").write_text(
        build_report(results, out_dir),
        encoding="utf-8",
    )
    print(str(out_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
