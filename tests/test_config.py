"""config 数据目录解析单元测试。"""
from __future__ import annotations

from pathlib import Path

from dirsearchx.core import config


def test_data_dir_prefers_repo_when_writable(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(config, "BASE_DIR", tmp_path)
    monkeypatch.setattr(config, "_writable", lambda p: True)
    assert config._data_dir() == tmp_path / "profiles"


def test_data_dir_uses_user_dir_when_readonly(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(config, "BASE_DIR", tmp_path)
    monkeypatch.setattr(config, "_writable", lambda p: False)
    monkeypatch.setenv("DIRSEARCHX_DATA", str(tmp_path / "userdata"))
    assert config._data_dir() == tmp_path / "userdata"


def test_data_dir_default_when_readonly(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(config, "BASE_DIR", tmp_path)
    monkeypatch.setattr(config, "_writable", lambda p: False)
    monkeypatch.delenv("DIRSEARCHX_DATA", raising=False)
    out = config._data_dir()
    assert out.name == "dirsearchx"
    assert tmp_path not in out.parents


def test_writable_true_for_tmp(tmp_path: Path):
    assert config._writable(tmp_path) is True
