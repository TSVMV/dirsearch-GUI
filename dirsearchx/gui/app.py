"""GUI 主屏：极简目标输入 + 一键任务 + 常用参数快捷 + 运行控制 + 流式日志 + 结果表。

专家按钮展开全选项表单（按 catalog 分组的 9 个 tab，布尔=复选框、值=复选框+输入）。
dirsearch 经子进程驱动，本体零修改；输出经 queue + after 轮询写回主线程。
结果表自动解析 [HH:MM:SS] STATUS - SIZE - PATH 行，按状态码着色。
"""
from __future__ import annotations

import queue
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional

from ..core import config, profiles
from ..core.catalog import load as load_catalog, Catalog
from ..core.runner import Runner, RunResult, build_argv
from ..core import presets
from ..core.presets import Preset
from ..core.output import parse_founds, parse_log, status_color


def main() -> int:
    try:
        home, version = config.check_dirsearch()
    except FileNotFoundError as e:
        err_root = tk.Tk()
        err_root.withdraw()
        messagebox.showerror("未找到 dirsearch", str(e))
        err_root.destroy()
        return 1
    catalog = load_catalog()
    catalog.version = version
    by_group = catalog.by_group()
    flag_names = {o.name for o in catalog.options if o.is_flag}
    out_q: "queue.Queue" = queue.Queue()

    class App:
        def __init__(self, root: tk.Tk):
            self.root = root
            self.home = home
            self.catalog = catalog
            self.runner: Optional[Runner] = None
            self.target_var = tk.StringVar()
            self.selected_preset: Optional[Preset] = None
            self.exp_checks: Dict[str, tk.BooleanVar] = {}
            self.exp_entries: Dict[str, tk.StringVar] = {}
            self.q_flags: Dict[str, tk.BooleanVar] = {}
            self.q_entries: Dict[str, tk.StringVar] = {}
            self._build()
            self.root.after(100, self._poll_log)

        # ---- UI ---------------------------------------------------------
        def _build(self):
            self.root.title(f"dirsearch-x · GUI   (dirsearch {self.catalog.version})")
            self.root.geometry("960x720")

            # 顶部：目标
            top = ttk.Frame(self.root)
            top.pack(fill="x", padx=8, pady=6)
            ttk.Label(top, text="目标 URL：", width=10, anchor="w").pack(side="left")
            ttk.Entry(top, textvariable=self.target_var).pack(
                side="left", fill="x", expand=True)

            # 一键任务
            tb = ttk.LabelFrame(self.root, text="  一键任务  ")
            tb.pack(fill="x", padx=8, pady=4)
            for i, p in enumerate(presets.PRESETS):
                mark = "·(高级)" if p.category == "adv" else ""
                b = ttk.Button(tb, text=f"{p.title}{mark}",
                               command=lambda p=p: self._pick_preset(p))
                b.grid(row=i // 5, column=i % 5, padx=4, pady=4, sticky="ew")
            for c in range(5):
                tb.columnconfigure(c, weight=1)

            # 常用参数快捷
            qb = ttk.LabelFrame(self.root, text="  常用参数  ")
            qb.pack(fill="x", padx=8, pady=4)
            for i, q in enumerate(presets.QUICK_PARAMS):
                row, col = i // 4, i % 4
                cell = ttk.Frame(qb)
                cell.grid(row=row, column=col, padx=4, pady=2, sticky="ew")
                if q["opt"] in flag_names:
                    var = tk.BooleanVar()
                    self.q_flags[q["opt"]] = var
                    ttk.Checkbutton(cell, text=q["label"], variable=var).pack(side="left")
                else:
                    sv = tk.StringVar()
                    if q.get("value"):
                        sv.set(q["value"])
                    self.q_entries[q["opt"]] = sv
                    ttk.Entry(cell, textvariable=sv).pack(side="left", fill="x", expand=True)
                    ttk.Label(cell, text=q["label"][:8]).pack(side="left", padx=(4, 0))
                for c in range(4):
                    qb.columnconfigure(c, weight=1)

            # 运行控制
            bar = ttk.Frame(self.root)
            bar.pack(fill="x", padx=8, pady=4)
            self.btn_run = ttk.Button(bar, text="▶ 运行", command=self.on_run)
            self.btn_stop = ttk.Button(bar, text="■ 停止", command=self.on_stop, state="disabled")
            self.btn_expert = ttk.Button(bar, text="专家选项 ▸", command=self.toggle_expert)
            self.btn_save = ttk.Button(bar, text="保存", command=self.on_save)
            self.btn_load = ttk.Button(bar, text="加载", command=self.on_load)
            self.btn_clear = ttk.Button(bar, text="清空", command=self.on_clear)
            for b in (self.btn_run, self.btn_stop, self.btn_expert,
                      self.btn_save, self.btn_load, self.btn_clear):
                b.pack(side="left", padx=3)
            self.profile_combo = ttk.Combobox(bar, width=14, state="readonly",
                                               values=profiles.list_profiles() or ["(无)"])
            self.profile_combo.pack(side="left", padx=6)
            self.profile_combo.bind("<<ComboboxSelected>>",
                                    lambda _e: self.on_load_from(self.profile_combo.get()))

            # 专家面板（默认隐藏）
            self.expert = ttk.Notebook(self.root)
            for group, opts in by_group.items():
                frame = ttk.Frame(self.expert)
                self.expert.add(frame, text=group)
                scroll = ttk.Scrollbar(frame)
                canvas = tk.Canvas(frame, height=300, yscrollcommand=scroll.set,
                                   highlightthickness=0, bd=0)
                inner = ttk.Frame(canvas)
                scroll.config(command=canvas.yview)
                cw = canvas.create_window((0, 0), window=inner, anchor="nw")

                def _resize(e, c=canvas, w=cw):
                    c.itemconfigure(w, width=e.width)

                inner.bind("<Configure>", _resize)
                canvas.configure(scrollregion=inner.bbox())
                scroll.pack(side="right", fill="y")
                canvas.pack(side="left", fill="both", expand=True)
                for r, o in enumerate(opts):
                    var = tk.BooleanVar()
                    self.exp_checks[o.name] = var
                    ttk.Checkbutton(inner, text=o.name, variable=var).grid(
                        row=r, column=0, sticky="w", padx=6, pady=2)
                    if not o.is_flag:
                        sv = tk.StringVar()
                        self.exp_entries[o.name] = sv
                        ttk.Entry(inner, textvariable=sv, width=32).grid(
                            row=r, column=1, sticky="w", padx=(4, 6))

            # 结果表
            rt = ttk.LabelFrame(self.root, text="  发现结果  ")
            rt.pack(fill="both", expand=True, padx=8, pady=4)
            self.rt = rt  # toggle_expert 需要把专家面板插到结果表之前
            cols = ("time", "status", "size", "path", "redirect")
            self.tree = ttk.Treeview(rt, columns=cols, show="headings", height=6)
            titles = {"time": "时间", "status": "状态", "size": "大小",
                     "path": "路径", "redirect": "跳转"}
            for c in cols:
                self.tree.heading(c, text=titles[c])
                self.tree.column(c, width=(60, 60, 70, 400, 120)[cols.index(c)],
                                 anchor="w")
            tsb = ttk.Scrollbar(rt, orient="vertical", command=self.tree.yview)
            self.tree.configure(yscrollcommand=tsb.set)
            self.tree.pack(side="left", fill="both", expand=True)
            tsb.pack(side="right", fill="y")
            for tag in ("ok", "warn", "info", "redir", "err", "found"):
                self.tree.tag_configure(tag, foreground={
                    "ok": "#0a7d33", "warn": "#b37000", "info": "#0b5394",
                    "redir": "#0b7a7a", "err": "#c00000",
                    "found": "#0a7d33"}[tag])

            # 日志
            self.log = tk.Text(self.root, height=8, state="disabled", wrap="word")
            self.log.pack(fill="x", padx=8, pady=4)
            for tag, fg in (("ok", "#0a7d33"), ("err", "#c00000"),
                            ("info", "#0b5394"), ("line", "#000000")):
                self.log.tag_config(tag, foreground=fg)

        # ---- 收集 ---------------------------------------------------------
        def _collect(self) -> Dict[str, object]:
            opts: Dict[str, object] = {}
            tg = self.target_var.get().strip()
            if tg:
                opts["-u"] = tg
            for name, var in self.exp_checks.items():
                if not var.get():
                    continue
                if name in flag_names:
                    opts[name] = "1"
                else:
                    sv = self.exp_entries.get(name)
                    s = sv.get().strip() if sv else ""
                    opts[name] = s if s else name
            for opt, var in self.q_flags.items():
                if var.get():
                    opts[opt] = "1"
            for opt, var in self.q_entries.items():
                v = var.get().strip()
                if v:
                    opts[opt] = v
            if self.selected_preset:
                opts = presets.merge(self.selected_preset, opts, {})
                for need in self.selected_preset.needs:
                    if str(opts.get(need) or "") in ("", need):
                        sv = self.exp_entries.get(need)
                        opts[need] = sv.get().strip() if sv else ""
            return opts

        # ---- 日志 ---------------------------------------------------------
        def _append(self, text: str, tag: str = "line"):
            self.log.configure(state="normal")
            self.log.insert("end", text + "\n", tag)
            self.log.see("end")
            self.log.configure(state="disabled")

        def _poll_log(self):
            try:
                while True:
                    kind, payload = out_q.get_nowait()
                    if kind == "line":
                        self._append(payload)
                    elif kind in ("ok", "err", "info"):
                        self._append(payload, kind)
                    elif kind == "done":
                        self._on_done(payload)
            except queue.Empty:
                pass
            self.root.after(100, self._poll_log)

        def _on_done(self, res: RunResult):
            self.btn_stop.configure(state="disabled")
            self._fill_results(res)
            s = parse_log(res.output)
            tail = "完成（exit 0）" if res.exit_code == 0 else f"结束（exit {res.exit_code}）"
            self._append(tail, "ok" if res.exit_code == 0 else "err")
            if s:
                self._append("摘要：" + "  ·  ".join(s), "info")

        # ---- 结果表 -------------------------------------------------------
        def _fill_results(self, res: RunResult):
            self.tree.delete(*self.tree.get_children())
            for f in parse_founds(res.output):
                tag = status_color(f.status)
                self.tree.insert("", "end", values=(
                    f.time, f.status, f.size_label, f.path,
                    f.redirect or ""), tags=(tag,))

        # ---- 运行 ---------------------------------------------------------
        def on_run(self):
            if self.runner and self.runner.is_running():
                return
            opts = self._collect()
            if self.selected_preset and not all(
                    str(opts.get(k) or "") for k in self.selected_preset.needs):
                self._append(f"预设 [{self.selected_preset.title}] 需补全 "
                             f"{self.selected_preset.needs}（专家面板/常用参数填值）", "err")
                return
            if not opts.get("-u"):
                self._append("缺少目标：请填目标 URL。", "err")
                return
            self._append("▶ 运行：" + " ".join(build_argv(opts, self.catalog)), "info")
            self.btn_stop.configure(state="normal")
            self.tree.delete(*self.tree.get_children())

            def on_line(line: str):
                out_q.put(("line", line))

            def on_done(res: RunResult):
                # 只投递队列，界面操作（_fill_results）必须在主线程完成
                out_q.put(("done", res))

            self.runner = Runner(self.home, opts, self.catalog,
                                 on_line=on_line, on_done=on_done)
            self.runner.start()

        def on_stop(self):
            if self.runner:
                self.runner.stop()
                self._append("请求停止…", "info")

        def on_clear(self):
            self.log.configure(state="normal")
            self.log.delete("1.0", "end")
            self.log.configure(state="disabled")
            self.tree.delete(*self.tree.get_children())

        def toggle_expert(self):
            if self.expert.winfo_manager():
                # ttk.Notebook.forget() 需要 tab_id，从布局移除用 pack_forget
                self.expert.pack_forget()
            else:
                # before 必须是与 expert 同父级（root）的已管理兄弟
                self.expert.pack(fill="both", expand=True, padx=8, pady=4,
                                 before=self.rt)

        def _pick_preset(self, p: Preset):
            self.selected_preset = p
            self._append(f"已选任务：[{p.title}] {p.desc}" +
                        (f"（需填 {p.needs}）" if p.needs else ""), "info")

        # ---- 配置档 -------------------------------------------------------
        def on_save(self):
            # 名字交给 profiles.save 用 _next_name 生成，避免删除后编号撞名覆盖
            p = profiles.Profile(
                name="",
                target=self.target_var.get().strip(),
                options=self._collect())
            try:
                profiles.save(p)
            except ValueError as e:
                self._append(f"保存失败：{e}", "err")
                return
            self.profile_combo.configure(values=profiles.list_profiles() or ["(无)"])
            self.profile_combo.set(p.name)
            self._append(f"已保存配置档：{p.name}", "ok")

        def on_load(self):
            self.on_load_from(self.profile_combo.get())

        def on_load_from(self, name: str):
            if not name or name == "(无)":
                self._append("无可加载配置档。", "info")
                return
            p = profiles.load(name)
            if p is None:
                self._append(f"配置档 {name} 不存在。", "err")
                return
            self.target_var.set(p.target)
            self.selected_preset = None
            for n, v in p.options.items():
                if n == "-u":
                    continue
                var = self.exp_checks.get(n)
                if var is None:
                    continue
                if n in flag_names:
                    var.set(bool(v) and str(v) not in ("", "0", "False"))
                else:
                    var.set(True)
                    self.exp_entries[n].set(str(v) if str(v) != n else "")
            self._append(f"已加载配置档：{p.name}（{len(p.options)} 项）", "info")

    root = tk.Tk()
    App(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
