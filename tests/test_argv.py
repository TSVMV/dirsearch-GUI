"""argv.build_argv 单元测试：选项排序、flag 处理、值输出规则。"""
from __future__ import annotations

from dirsearchx.core.argv import build_argv, render
from dirsearchx.core.catalog import load


def _catalog():
    return load()


def test_target_url_first_with_value():
    opts = {"-u": "http://example.com", "-t": "10"}
    argv = build_argv(opts, _catalog())
    assert argv[0] == "-u"
    assert argv[1] == "http://example.com"
    assert "-t" in argv
    t_idx = argv.index("-t")
    assert argv[t_idx + 1] == "10"


def test_flag_no_value():
    opts = {"-f": "1", "-u": "http://x"}
    argv = build_argv(opts, _catalog())
    f_idx = argv.index("-f")
    assert f_idx == len(argv) - 1 or argv[f_idx + 1] != "1"
    assert "1" not in argv


def test_missing_option_not_emitted():
    opts = {"-u": "http://x"}
    argv = build_argv(opts, _catalog())
    assert "-w" not in argv
    assert "-e" not in argv


def test_empty_value_emits_name_only():
    opts = {"-u": "", "-t": ""}
    argv = build_argv(opts, _catalog())
    assert "-u" in argv
    u_idx = argv.index("-u")
    if u_idx + 1 < len(argv):
        assert argv[u_idx + 1] != ""


def test_target_class_order_fixed():
    opts = {"-u": "http://x", "-l": "urls.txt"}
    argv = build_argv(opts, _catalog())
    assert argv.index("-l") < argv.index("-u")


def test_render_uses_shlex():
    out = render(["-u", "http://a b/c"])
    assert "http://a" in out
    assert "'" in out or '"' in out
