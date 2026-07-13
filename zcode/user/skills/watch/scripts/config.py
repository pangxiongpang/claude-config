#!/usr/bin/env python3
"""Shared /watch configuration helpers."""
from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path


CONFIG_DIR = Path.home() / ".config" / "watch"
CONFIG_FILE = CONFIG_DIR / ".env"

DEFAULT_DETAIL = "balanced"

DETAILS = {"transcript", "efficient", "balanced", "token-burner"}

# ═══════════════════════════════════════════════════════════════════
# Platform PATH fixes — ensure ffmpeg/yt-dlp are findable even when
# the shell hasn't picked up the Windows PATH after winget install.
# ═══════════════════════════════════════════════════════════════════
_WINGET_FFMPEG = (
    Path.home()
    / "AppData"
    / "Local"
    / "Microsoft"
    / "WinGet"
    / "Packages"
    / "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    / "ffmpeg-8.1.2-full_build"
    / "bin"
)

_KNOWN_BIN_PATHS: list[Path] = []
if platform.system() == "Windows":
    if _WINGET_FFMPEG.exists():
        _KNOWN_BIN_PATHS.append(_WINGET_FFMPEG)

for _bin_dir in _KNOWN_BIN_PATHS:
    _str = str(_bin_dir.resolve())
    if _str not in os.environ.get("PATH", ""):
        old = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{_str}{os.pathsep}{old}"

# Workaround: on Windows, shutil.which() can miss executables that
# were added to PATH after the current process started.  Pre-warm
# shutil's cache by touching each known binary.
for _bin_dir in _KNOWN_BIN_PATHS:
    for _exe in ("ffmpeg.exe", "ffprobe.exe", "ffplay.exe"):
        _full = _bin_dir / _exe
        if _full.exists():
            shutil.which(str(_full))  # warm cache
# ═══════════════════════════════════════════════════════════════════


def read_env_file(path: Path | None = None) -> dict[str, str]:
    if path is None:
        path = CONFIG_FILE
    values: dict[str, str] = {}
    if not path.exists():
        return values
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return values
    for line in lines:
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, _, value = raw.partition("=")
        value = value.strip()
        if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]
        else:
            # Strip an inline comment (a '#' preceded by whitespace) from an
            # unquoted value. Without this, `WATCH_DETAIL=balanced  # note`
            # parses as "balanced  # note", fails validation, and silently
            # falls back to the default. Keeps '#' inside quotes / API keys.
            for i, ch in enumerate(value):
                if ch == "#" and i > 0 and value[i - 1] in " \t":
                    value = value[:i].rstrip()
                    break
        values[key.strip()] = value
    return values


def get_config() -> dict[str, object]:
    file_values = read_env_file()

    detail = (
        os.environ.get("WATCH_DETAIL")
        or file_values.get("WATCH_DETAIL")
        or DEFAULT_DETAIL
    )
    if detail not in DETAILS:
        detail = DEFAULT_DETAIL

    return {
        "detail": detail,
        "config_file": str(CONFIG_FILE),
    }


def frame_cap(detail: str) -> int | None:
    if detail == "efficient":
        return 50
    if detail == "balanced":
        return 100
    if detail == "token-burner":
        return None
    if detail == "transcript":
        return None
    return 100
