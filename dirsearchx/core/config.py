"""config: 启动前检查 dirsearch 可发现性。"""
from __future__ import annotations

from . import vendor


def check_dirsearch():
    """返回 (home, version)；找不到时抛 FileNotFoundError。"""
    home = vendor.find()
    try:
        ver = home.version()
    except Exception:
        ver = "unknown"
    return home, ver
