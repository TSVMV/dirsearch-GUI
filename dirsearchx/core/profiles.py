"""配置档（profile）：JSON 存 target + 全量选项，可保存/加载/列出。

存储规则：profiles 目录下只允许 `profileN.json` 形式的文件。
文件名由本模块内部生成并经白名单校验；路径使用 `pathlib` 的
`Path.resolve()` + `relative_to` 双重约束，任何穿越尝试在访问磁盘前被拒绝。
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from . import config

_PROFILES_DIR: Path = config.PROFILES_DIR
_NAME_RE = re.compile(r"^profile\d+$")


@dataclass
class Profile:
    name: str
    target: str
    options: dict[str, object]

    def to_json(self) -> str:
        return json.dumps(
            {"name": self.name, "target": self.target, "options": self.options},
            ensure_ascii=False, indent=2)


def _next_name() -> str:
    n = len(list_profiles()) + 1
    while f"profile{n}" in list_profiles():
        n += 1
    return f"profile{n}"


def _resolve(name: str) -> Path:
    """把配置档名解析为 profiles 目录内的安全路径；非法即抛 ValueError。"""
    if not _NAME_RE.match(name):
        raise ValueError(f"非法配置档名: {name!r}")
    p = (_PROFILES_DIR / (name + ".json")).resolve()
    # 必须仍位于 profiles 目录内（防符号链接/穿越）
    p.relative_to(_PROFILES_DIR.resolve())
    return p


def save(p: Profile) -> str:
    if not _NAME_RE.match(p.name):
        p.name = _next_name()
    _PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    path = _resolve(p.name)
    path.write_text(p.to_json(), encoding="utf-8")
    return str(path)


def load(name: str) -> Profile | None:
    try:
        path = _resolve(name)
    except ValueError:
        return None
    if not path.is_file():
        return None
    d = json.loads(path.read_text(encoding="utf-8"))
    return Profile(d.get("name", name), d.get("target", ""),
                   d.get("options", {}))


def list_profiles() -> list[str]:
    if not _PROFILES_DIR.is_dir():
        return []
    return sorted(
        f.stem for f in _PROFILES_DIR.iterdir()
        if f.suffix == ".json" and _NAME_RE.match(f.stem))


def delete(name: str) -> bool:
    try:
        path = _resolve(name)
    except ValueError:
        return False
    if path.is_file():
        path.unlink()
        return True
    return False
