"""解析 dirsearch 输出：提取结果行 [HH:MM:SS] STATUS - SIZE - PATH。"""
from __future__ import annotations

import re
from dataclasses import dataclass

# 结果行形如: [12:34:56] 200 -    1234 - /admin/
# 结果行形如: [17:03:11] 200 -    24B - /.git/config
# 注意：size 可带 B/K/M/G/T 单位
_RESULT = re.compile(
    r"\[(?P<time>\d{2}:\d{2}:\d{2})\]\s+"
    r"(?P<status>\d{3})\s+-\s+"
    r"(?P<size>\d+\s*[BKMGT]?)\s+-\s+"
    r"(?P<path>.+)")

_PROGRESS = re.compile(r"\[.*?\]\s*Progress:|Elapsed Time|Requests:|Status:|Errors:|Found:")


@dataclass
class FoundPath:
    time: str
    status: int
    size: int
    size_label: str
    path: str
    redirect: str | None = None


def parse_founds(output: str) -> list[FoundPath]:
    """从完整输出里抽出所有结果路径行。"""
    out: list[FoundPath] = []
    for line in output.splitlines():
        m = _RESULT.search(line)
        if m:
            path = m.group("path").strip()
            # 提取 -> 重定向
            redir = None
            if "  ->  " in path:
                path, redir = [x.strip() for x in path.split("  ->  ", 1)]
            out.append(FoundPath(
                time=m.group("time"),
                status=int(m.group("status")),
                size=int(re.sub(r"[^0-9]", "", m.group("size")) or 0),
                size_label=m.group("size").strip(),
                path=path,
                redirect=redir,
            ))
    return out


def parse_log(output: str) -> list[str]:
    """生成一行摘要（请求数 / 找到数 / 耗时等）。"""
    lines: list[str] = []
    finds = parse_founds(output)
    if finds:
        lines.append(f"找到 {len(finds)} 个路径")
    m = re.search(r"Requests:\s*(\d+)", output)
    if m:
        lines.append(f"请求 {m.group(1)}")
    m = re.search(r"Elapsed Time:\s*(\S+)", output)
    if m:
        lines.append(f"耗时 {m.group(1)}")
    return lines


def status_color(status: int) -> str:
    """按状态码给 GUI tag 着色。"""
    if status in (200, 201, 204):
        return "ok"
    if status == 401:
        return "warn"
    if status == 403:
        return "info"
    if 300 <= status < 400:
        return "redir"
    if 500 <= status < 600:
        return "err"
    return "found"
