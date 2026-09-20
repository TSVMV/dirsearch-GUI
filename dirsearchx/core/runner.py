"""子进程 runner：在线程中启动 dirsearch，逐行回读 stdout。"""
from __future__ import annotations

import re
import subprocess
import threading
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from .argv import build_argv
from .catalog import Catalog
from .vendor import DirsearchHome

_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(s: str) -> str:
    return _ANSI.sub("", s)


@dataclass
class RunResult:
    exit_code: int
    output: str
    argv: List[str] = field(default_factory=list)
    target: str = ""


class Runner:
    """在守护线程里跑 dirsearch，on_line 回调逐行推送（已去 ANSI）。"""

    def __init__(self, home: DirsearchHome, opts: Dict[str, object],
                 catalog: Catalog,
                 on_line: Optional[Callable[[str], None]] = None,
                 on_done: Optional[Callable[[RunResult], None]] = None,
                 raw_argv: Optional[List[str]] = None):
        self.home = home
        self.opts = opts
        self.catalog = catalog
        self.on_line = on_line
        self.on_done = on_done
        self.argv = raw_argv if raw_argv is not None else build_argv(opts, catalog)
        self._proc: Optional[subprocess.Popen] = None
        self._thread: Optional[threading.Thread] = None

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._proc and self._proc.poll() is None:
            self._proc.kill()

    def _run(self) -> None:
        try:
            proc = self._proc = self.home.spawn(self.argv)
            out_lines: List[str] = []
            assert proc.stdout is not None
            for raw in proc.stdout:
                line = strip_ansi(raw.rstrip("\n"))
                out_lines.append(line)
                if self.on_line:
                    self.on_line(line)
            rc = proc.wait()
            result = RunResult(exit_code=rc, output="\n".join(out_lines),
                               argv=self.argv)
        except Exception as e:
            result = RunResult(exit_code=1,
                               output=f"dirsearch 启动失败: {e}", argv=self.argv)
        if self.on_done:
            self.on_done(result)
