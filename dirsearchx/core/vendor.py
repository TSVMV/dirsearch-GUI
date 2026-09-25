"""dirsearch vendor 发现：按 包内 vendor > 环境变量 > 常见路径 > 系统命令 顺序定位。"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass

_ENV_KEYS = ("DIRSEARCH_HOME", "DIRSEARCH_PATH")

# 常见安装位置（Windows 下 dirsearch 常被放到 CTF/工具目录）
_CANDIDATES: list[str] = [
    # 包内 vendor（开发/打包时首选）
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "vendor", "dirsearch"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor", "dirsearch"),
]
_CANDIDATES += [
    os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Desktop", "CTF", "web", "dirsearch"),
    r"C:\Users\Administrator\Desktop\CTF\web\dirsearch",
]


@dataclass
class DirsearchHome:
    path: str
    source: str

    def spawn(self, argv: list[str]) -> subprocess.Popen:
        """在 vendor 目录下启动 `python -m dirsearch <argv>`。"""
        env = dict(os.environ)
        env["PYTHONPATH"] = self.path + os.pathsep + env.get("PYTHONPATH", "")
        return subprocess.Popen(
            [sys.executable, "-m", "dirsearch", *argv],
            cwd=self.path,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def version(self) -> str:
        p = self.spawn(["--version"])
        out, _ = p.communicate(timeout=30)
        return out.strip().splitlines()[-1] if out.strip() else "unknown"


def _is_dirsearch_root(d: str) -> bool:
    return os.path.isfile(os.path.join(d, "dirsearch.py")) or os.path.isfile(
        os.path.join(d, "lib", "core", "options.py"))


def find() -> DirsearchHome:
    # 1. 环境变量
    for k in _ENV_KEYS:
        v = os.environ.get(k)
        if v and _is_dirsearch_root(v):
            return DirsearchHome(os.path.abspath(v), f"env:{k}")

    # 2. 包内 vendor + 常见位置
    for c in _CANDIDATES:
        c = os.path.abspath(c)
        if _is_dirsearch_root(c):
            return DirsearchHome(c, "candidate")

    # 3. 系统 PATH 上的 dirsearch 命令
    exe = shutil.which("dirsearch")
    if exe:
        # dirsearch CLI 通常是包装脚本；取其所在目录作为根（尽力）
        return DirsearchHome(os.path.dirname(os.path.realpath(exe)), "which")

    raise FileNotFoundError(
        "未找到 dirsearch。请 git clone https://github.com/maurosoria/dirsearch 到 vendor/dirsearch，"
        "或设置环境变量 DIRSEARCH_HOME 指向其根目录。")
