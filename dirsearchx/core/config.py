"""config: 数据目录与启动前检查 dirsearch 可发现性。

数据目录在开发检出时可写则落在项目内 ``profiles/``；pip 安装到
site-packages（只读）时改用用户数据目录，可通过 ``DIRSEARCHX_DATA`` 覆盖。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from . import vendor

BASE_DIR = Path(__file__).resolve().parents[2]


def _writable(path: Path) -> bool:
    """目录是否可写（用于区分开发检出与 site-packages 安装）。"""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return os.access(path, os.W_OK)
    except OSError:
        return False


def _data_dir() -> Path:
    if _writable(BASE_DIR):
        return BASE_DIR / "profiles"
    base = os.environ.get("DIRSEARCHX_DATA")
    if base:
        return Path(base)
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", "~/AppData/Local")) / "dirsearchx"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "dirsearchx"
    return Path(os.environ.get("XDG_DATA_HOME", "~/.local/share")).expanduser() / "dirsearchx"


PROFILES_DIR = _data_dir()


def check_dirsearch():
    """返回 (home, version)；找不到时抛 FileNotFoundError。"""
    home = vendor.find()
    try:
        ver = home.version()
    except Exception:
        ver = "unknown"
    return home, ver
