"""CLI 透传入口：`dirsearchx-cli [dirsearch 任意参数]`。

把所有参数原样交给 dirsearch 子进程，行为与裸跑一致；
加 --json 时额外把结果路径解析为 JSON 打印到 stdout。
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Dict, List, Optional

from ..core import config
from ..core.catalog import load
from ..core.runner import Runner, RunResult


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="dirsearchx-cli",
        description="dirsearch 命令行透传（驱动 vendor 内的 dirsearch）")
    parser.add_argument("--json", action="store_true",
                        help="把找到的路径输出为 JSON 数组到 stdout")
    parser.add_argument("--list-vendor", action="store_true",
                        help="打印定位到的 dirsearch 根目录与版本后退出")
    # 剩余参数全部透传给 dirsearch
    args, passthrough = parser.parse_known_args(argv)

    if args.list_vendor:
        home, ver = config.check_dirsearch()
        print(f"dirsearch root: {home.path}  (source={home.source})")
        print(f"version: {ver}")
        return 0

    if not passthrough:
        parser.print_help()
        return 2

    home, ver = config.check_dirsearch()
    catalog = load()
    catalog.version = ver

    opts = _passthrough_to_opts(passthrough, catalog)

    result_holder: Dict[str, object] = {}

    def on_line(line: str):
        if not args.json:
            print(line, flush=True)

    def on_done(res: RunResult):
        result_holder["res"] = res

    runner = Runner(home, opts, catalog, on_line=on_line, on_done=on_done)
    runner.start()
    runner._thread.join()  # 等待完成

    res: Optional[RunResult] = result_holder.get("res")
    if res is None:
        print("dirsearch 未返回结果。", file=sys.stderr)
        return 1

    if args.json:
        from ..core.output import parse_founds
        found = parse_founds(res.output)
        print(json.dumps(
            [{"time": f.time, "status": f.status, "size": f.size,
              "size_label": f.size_label, "path": f.path,
              "redirect": f.redirect} for f in found],
            ensure_ascii=False, indent=2))

    return 0 if res.exit_code == 0 else res.exit_code


def _passthrough_to_opts(argv: List[str], catalog) -> Dict[str, object]:
    """把透传 argv 还原成 {opt: value}，复用 build_argv。

    用 catalog 的 flag 知识判断每个 token 是否为无值开关。
    """
    opts: Dict[str, object] = {}
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok.startswith("-"):
            name, _, val = tok.partition("=")
            if val:
                opts[name] = val
            elif catalog.is_flag(name):
                opts[name] = "1"
            else:
                # 取下一个 token 作为值
                i += 1
                if i < len(argv):
                    opts[name] = argv[i]
        i += 1
    return opts


if __name__ == "__main__":
    sys.exit(main())
