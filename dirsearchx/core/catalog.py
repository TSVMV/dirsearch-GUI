"""dirsearch 选项编目：按 --help-all 分组，供专家面板/构建 argv 使用。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Option:
    name: str                # 形如 "-t" 或 "--threads"
    long_name: Optional[str] = None
    is_flag: bool = False    # 无取值的布尔开关
    value_help: str = ""     # 取值说明（简短）
    group: str = "General"


def _o(name: str, long_name: Optional[str] = None,
       is_flag: bool = False, help_: str = "") -> Option:
    """Option 构造助手：避免位置参数错位。"""
    return Option(name=name, long_name=long_name, is_flag=is_flag,
                  value_help=help_)


# 分组与选项清单（取自 dirsearch --help-all，仅收录 GUI 常用项；
# 完整选项可走 CLI 透传，不强制在此穷举）
OPTIONS: List[Option] = [
    # --- 目标 ---
    _o("-u", long_name="--url", is_flag=False, help_="目标 URL，可多次"),
    _o("-l", long_name="--urls-file", is_flag=False, help_="URL 列表文件"),
    _o("--cidr", long_name=None, help_="目标 CIDR"),
    _o("--raw", long_name=None, help_="从文件读原始 HTTP 请求"),
    _o("-s", long_name="--session", is_flag=False, help_="会话文件"),
    _o("--config", long_name=None, help_="配置文件路径"),

    # --- 字典 ---
    _o("-w", long_name="--wordlists", is_flag=False, help_="词表文件或目录（逗号分隔）"),
    _o("--wordlist-categories", is_flag=False, help_="词表类别（common,conf,web…；all）"),
    _o("-e", long_name="--extensions", is_flag=False, help_="扩展名列表（逗号分隔）"),
    _o("-f", is_flag=True, help_="把扩展名追加到每个词表项尾部"),
    _o("--exclude-extensions", long_name=None, help_="排除扩展名"),
    _o("--prefixes", long_name=None, help_="自定义前缀（逗号分隔）"),
    _o("--suffixes", long_name=None, help_="自定义后缀（逗号分隔）"),

    # --- 通用 ---
    _o("-t", long_name="--threads", is_flag=False, help_="线程数"),
    _o("-a", long_name="--async", is_flag=True, help_="异步模式"),
    _o("--sync", is_flag=True, help_="同步 Python 模式"),
    _o("-r", long_name="--recursive", is_flag=True, help_="递归爆破"),
    _o("-R", long_name="--max-recursion-depth", is_flag=False, help_="最大递归深度（0 无限）"),
    _o("--recursion-status", long_name=None, help_="触发递归的状态码"),
    _o("-i", long_name="--include-status", is_flag=False, help_="包含状态码（逗号/区间）"),
    _o("-x", long_name="--exclude-status", is_flag=False, help_="排除状态码"),
    _o("--exclude-sizes", long_name=None, help_="按响应大小排除"),
    _o("--exclude-text", long_name=None, help_="按响应文本排除"),
    _o("--exclude-regex", long_name=None, help_="按响应正则排除"),
    _o("--exclude-redirect", long_name=None, help_="按跳转 URL 排除"),
    _o("--max-time", long_name=None, help_="扫描总时限（秒）"),
    _o("--target-max-time", long_name=None, help_="单目标时限（秒）"),
    _o("--exit-on-error", is_flag=True, help_="出错即退出"),

    # --- 高级过滤 ---
    _o("--auto-calibration", is_flag=True, help_="强制通配符校准"),
    _o("--matcher-mode", long_name="--mmode", is_flag=False, help_="匹配器 and/or"),
    _o("--filter-mode", long_name="--fmode", is_flag=False, help_="过滤器 and/or"),
    _o("--match-status", long_name="--mc", is_flag=False, help_="高级状态码匹配"),
    _o("--filter-status", long_name="--fc", is_flag=False, help_="高级状态码过滤"),
    _o("--match-size", long_name="--ms", is_flag=False, help_="高级大小匹配"),
    _o("--filter-size", long_name="--fs", is_flag=False, help_="高级大小过滤"),
    _o("--match-words", long_name="--mw", is_flag=False, help_="高级词数匹配"),
    _o("--filter-words", long_name="--fw", is_flag=False, help_="高级词数过滤"),
    _o("--match-lines", long_name="--ml", is_flag=False, help_="高级行数匹配"),
    _o("--filter-lines", long_name="--fl", is_flag=False, help_="高级行数过滤"),
    _o("--match-regex", long_name="--mr", is_flag=False, help_="响应体正则匹配"),
    _o("--filter-regex", long_name="--fr", is_flag=False, help_="响应体正则过滤"),
    _o("--match-header", long_name=None, help_="响应头文本匹配（可多次）"),
    _o("--filter-header", long_name=None, help_="响应头文本过滤（可多次）"),
    _o("--match-header-regex", long_name=None, help_="响应头正则匹配"),
    _o("--filter-header-regex", long_name=None, help_="响应头正则过滤"),
    _o("--match-time", long_name="--mt", is_flag=False, help_="耗时匹配，如 >100"),
    _o("--filter-time", long_name="--ft", is_flag=False, help_="耗时过滤"),
    _o("--filter-threshold", long_name=None, help_="重复响应过滤阈值"),
    _o("--subdirs", long_name=None, help_="扫描子目录（逗号分隔）"),
    _o("--exclude-subdirs", long_name=None, help_="排除子目录"),
    _o("--exclude-response", long_name=None, help_="排除相似响应（路径）"),
    _o("--skip-on-status", long_name=None, help_="命中即跳过该目标"),
    _o("--min-response-size", long_name=None, help_="最小响应长度"),
    _o("--max-response-size", long_name=None, help_="最大响应长度"),

    # --- 请求 ---
    _o("-m", long_name="--http-method", is_flag=False, help_="HTTP 方法"),
    _o("--request-backend", long_name=None, help_="请求后端 python/native"),
    _o("-d", long_name="--data", is_flag=False, help_="请求体"),
    _o("--data-file", long_name=None, help_="请求体文件"),
    _o("-H", long_name="--header", is_flag=False, help_="请求头（可多次）"),
    _o("--headers-file", long_name=None, help_="请求头文件"),
    _o("-F", long_name="--follow-redirects", is_flag=True, help_="跟随重定向"),
    _o("--random-agent", is_flag=True, help_="随机 User-Agent"),
    _o("--auth", long_name=None, help_="凭据 user:pass 或 bearer"),
    _o("--auth-type", long_name=None, help_="basic/digest/bearer/ntlm/jwt"),
    _o("--cert-file", long_name=None, help_="客户端证书"),
    _o("--key-file", long_name=None, help_="客户端私钥"),
    _o("--user-agent", long_name=None, help_="自定义 UA"),
    _o("--cookie", long_name=None, help_="Cookie"),

    # --- 连接 ---
    _o("--timeout", is_flag=False, help_="连接超时（秒/毫秒）"),
    _o("--delay", long_name=None, help_="请求间隔（秒，逗号分隔列表）"),
    _o("-p", long_name="--proxy", is_flag=False, help_="代理 URL（可多次）"),
    _o("--proxies-file", long_name=None, help_="代理列表文件"),
    _o("--proxy-auth", long_name=None, help_="代理凭据"),
    _o("--replay-proxy", long_name=None, help_="回放进程代理"),
    _o("--tor", is_flag=True, help_="Tor 代理"),
    _o("--scheme", long_name=None, help_="协议 scheme"),
    _o("--max-rate", long_name=None, help_="最大请求速率/秒"),
    _o("--retries", long_name=None, help_="失败重试次数"),
    _o("--ip", long_name=None, help_="服务器 IP"),
    _o("--interface", long_name=None, help_="网络接口"),

    # --- 高级 ---
    _o("--crawl", is_flag=True, help_="响应爬取发现路径"),
    _o("--find-backup", is_flag=True, help_="查找备份文件"),

    # --- 视图 ---
    _o("-q", long_name="--quiet", is_flag=True, help_="安静模式"),
    _o("--full-url", is_flag=True, help_="输出完整 URL"),
    _o("--redirects-history", is_flag=True, help_="显示跳转历史"),
    _o("--no-color", is_flag=True, help_="禁用彩色输出"),
    _o("--disable-cli", is_flag=True, help_="关闭命令行输出"),
    _o("-v", long_name="--verbose", is_flag=True, help_="显示耗时与内容类型"),

    # --- 输出 ---
    _o("-O", long_name="--output-formats", is_flag=False, help_="报表格式（simple,plain,json,xml,md,csv,html,sqlite）"),
    _o("-o", long_name="--output-file", is_flag=False, help_="输出文件路径"),
    _o("--mysql-url", long_name=None, help_="MySQL 数据库 URL"),
    _o("--postgres-url", long_name=None, help_="PostgreSQL 数据库 URL"),
    _o("--save-response", long_name=None, help_="保存响应体目录"),
    _o("--save-response-jsonl", long_name=None, help_="JSONL 响应追加"),
    _o("--log", long_name=None, help_="日志文件"),
]

# 组归类（专家面板 tab 顺序）
GROUPS: Dict[str, List[str]] = {
    "目标": ["-u", "-l", "--cidr", "--raw", "-s", "--config"],
    "字典": ["-w", "--wordlist-categories", "-e", "-f", "--exclude-extensions",
            "--prefixes", "--suffixes"],
    "通用": ["-t", "-a", "--sync", "-r", "-R", "--recursion-status", "-i", "-x",
            "--exclude-sizes", "--exclude-text", "--exclude-regex", "--exclude-redirect",
            "--max-time", "--target-max-time", "--exit-on-error"],
    "高级过滤": ["--auto-calibration", "--matcher-mode", "--filter-mode",
               "--match-status", "--filter-status", "--match-size", "--filter-size",
               "--match-words", "--filter-words", "--match-lines", "--filter-lines",
               "--match-regex", "--filter-regex", "--match-header", "--filter-header",
               "--match-header-regex", "--filter-header-regex", "--match-time",
               "--filter-time", "--filter-threshold", "--subdirs", "--exclude-subdirs",
               "--exclude-response", "--skip-on-status", "--min-response-size",
               "--max-response-size"],
    "请求": ["-m", "--request-backend", "-d", "--data-file", "-H", "--headers-file",
            "-F", "--random-agent", "--auth", "--auth-type", "--cert-file", "--key-file",
            "--user-agent", "--cookie"],
    "连接": ["--timeout", "--delay", "-p", "--proxies-file", "--proxy-auth",
            "--replay-proxy", "--tor", "--scheme", "--max-rate", "--retries",
            "--ip", "--interface"],
    "高级": ["--crawl", "--find-backup"],
    "视图": ["--full-url", "--redirects-history", "--no-color", "-q", "--disable-cli", "-v"],
    "输出": ["-O", "-o", "--mysql-url", "--postgres-url", "--save-response",
            "--save-response-jsonl", "--log"],
}


class Catalog:
    def __init__(self, options: Optional[List[Option]] = None,
                 groups: Optional[Dict[str, List[str]]] = None,
                 version: str = ""):
        self.options = options if options is not None else OPTIONS
        self.groups = groups if groups is not None else GROUPS
        self.version = version
        self.by_name: Dict[str, Option] = {}
        for o in self.options:
            self.by_name[o.name] = o
            if o.long_name:
                self.by_name[o.long_name] = o

    def is_flag(self, name: str) -> bool:
        o = self.by_name.get(name)
        return o.is_flag if o else True

    def by_group(self) -> Dict[str, List[Option]]:
        out: Dict[str, List[Option]] = {}
        for g, names in self.groups.items():
            out[g] = [self.by_name[n] for n in names if n in self.by_name]
        return out


def load() -> Catalog:
    return Catalog()
