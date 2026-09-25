"""一键任务预设 + 常用参数快捷。"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Preset:
    title: str
    desc: str
    category: str          # basic / adv
    base: dict[str, str] = field(default_factory=dict)
    needs: list[str] = field(default_factory=list)   # 需要用户补全的选项名


# 一键任务
PRESETS: list[Preset] = [
    Preset("快速探测", "默认词表 + 30 线程，适合先扫个大概", "basic",
           base={"-t": "30"}, needs=["-u"]),
    Preset("后台与配置", "conf 类别，找 .git/.env 等", "basic",
           base={"--wordlist-categories": "conf", "-i": "200,301,302,304,401,403,500"},
           needs=["-u"]),
    Preset("Web 页面", "web 类别 + 常见扩展名", "basic",
           base={"--wordlist-categories": "web", "-e": "php,asp,aspx,jsp,html,js"},
           needs=["-u"]),
    Preset("管理后台", "admin 相关路径 + 状态过滤", "basic",
           base={"--wordlist-categories": "web,conf", "-i": "200,301,302,401,403"},
           needs=["-u"]),
    Preset("全量深度", "all 类别 + 递归 + 扩展名", "adv",
           base={"--wordlist-categories": "all", "-e": "php,asp,aspx,jsp,html,txt,xml,json",
                 "-r": "1", "-R": "2"}, needs=["-u"]),
    Preset("备份文件", "backups 类别找 .bak/.old/zip 等", "adv",
           base={"--wordlist-categories": "backups"}, needs=["-u"]),
    Preset("爬虫发现", "crawl 从响应里挖新路径", "adv",
           base={"--crawl": "1"}, needs=["-u"]),
    Preset("限速礼貌扫", "低线程 + 延迟，避免打挂目标", "adv",
           base={"-t": "10", "--delay": "0.5", "-x": "404"}, needs=["-u"]),
    Preset("JSON 报表", "结果导出 json+html 便于交接", "adv",
           base={"-O": "json,html"}, needs=["-u", "-o"]),
    Preset("认证爆破", "带 Basic 凭据 + 排除 404", "adv",
           base={"--auth-type": "basic", "-x": "404"}, needs=["-u", "--auth"]),
]

# 常用参数快捷（主屏小格子）
QUICK_PARAMS: list[dict] = [
    {"opt": "-t", "label": "线程"},
    {"opt": "-e", "label": "扩展名"},
    {"opt": "--wordlist-categories", "label": "词表类别"},
    {"opt": "-w", "label": "词表路径"},
    {"opt": "-i", "label": "含状态"},
    {"opt": "-x", "label": "排状态"},
    {"opt": "-r", "label": "递归?"},
    {"opt": "-O", "label": "报表格式"},
    {"opt": "-H", "label": "Header"},
    {"opt": "--timeout", "label": "超时"},
    {"opt": "--delay", "label": "间隔"},
    {"opt": "-p", "label": "代理"},
    {"opt": "-o", "label": "输出文件"},
]


def merge(preset: Preset, user_opts: dict[str, object],
          defaults: dict[str, str]) -> dict[str, object]:
    """预设 < 默认 < 用户。用户未填的 needs 保留占位。"""
    out: dict[str, object] = {}
    for k, v in preset.base.items():
        out[k] = v
    for k, v in defaults.items():
        out[k] = v
    for k, v in user_opts.items():
        out[k] = v
    return out
