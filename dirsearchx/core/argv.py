"""argv 构建：把 GUI 收集的 {opt: value} 翻译成 dirsearch 命令行。

- 键是选项名（短或长形式），值是 "1"（布尔开启）或具体取值。
- 输出顺序：目标 → 字典 → 其余（按 catalog 组顺序）。
"""
from __future__ import annotations

from .catalog import Catalog

# 这些选项在输出 argv 时固定放最前（目标类）
_TARGET = {"-u", "-l", "--cidr", "--raw", "-s", "--config"}
# 字典类次之
_DICT = {"-w", "--wordlist-categories", "-e", "-f", "--exclude-extensions",
         "--prefixes", "--suffixes"}


def build_argv(opts: dict[str, object], catalog: Catalog) -> list[str]:
    """构建 argv（不含 "dirsearch" 本身）。

    只输出 opts 中出现的选项，保持其顺序；目标类（-u/-l/--cidr/--raw/-s/--config）
    固定放最前，字典类次之，其余按 catalog 组顺序。
    """
    def val_of(name: str) -> str:
        v = opts.get(name)
        if v is None:
            return ""
        s = str(v).strip()
        return s

    out: list[str] = []
    seen = set()

    # 目标类（顺序固定）
    for name in ("-l", "--cidr", "--raw", "-s", "--config", "-u"):
        if name in opts:
            seen.add(name)
            out.append(name)
            s = val_of(name)
            if s:
                out.append(s)

    # 布尔开关（即使值字段非空也不输出取值；flag 选项的 dict 值为 "1"）
    _FLAG = {"-f", "-a", "-r", "-F", "-q", "-v", "--tor", "--crawl",
             "--find-backup", "--no-color", "--sync", "--random-agent",
             "--exit-on-error", "--full-url", "--redirects-history",
             "--disable-cli", "--auto-calibration"}

    # 字典类（-f 为布尔开关）
    for name in ("-w", "--wordlist-categories", "-e", "-f",
                 "--exclude-extensions", "--prefixes", "--suffixes"):
        if name not in opts:
            continue
        seen.add(name)
        out.append(name)
        s = val_of(name)
        if s and name not in _FLAG and not catalog.is_flag(name):
            out.append(s)

    # 其余：按 catalog 组顺序输出 opts 中出现的
    for _group, group_opts in catalog.by_group().items():
        for o in group_opts:
            if o.name in seen:
                continue
            if o.name not in opts:
                continue
            seen.add(o.name)
            out.append(o.name)
            s = val_of(o.name)
            if s and o.name not in _FLAG and not o.is_flag:
                out.append(s)

    return out


def render(argv: list[str]) -> str:
    import shlex
    return shlex.join(argv)
