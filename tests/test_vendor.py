"""vendor 发现逻辑单元测试：_is_dirsearch_root 判定、find 的环境变量与缺失报错。"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from dirsearchx.core import vendor


def test_is_root_false_for_empty_dir(tmp_path: Path):
    assert vendor._is_dirsearch_root(str(tmp_path)) is False


def test_is_root_true_when_dirsearch_py_present(tmp_path: Path):
    (tmp_path / "dirsearch.py").write_text("# stub")
    assert vendor._is_dirsearch_root(str(tmp_path)) is True


def test_is_root_true_when_options_py_present(tmp_path: Path):
    core = tmp_path / "lib" / "core"
    core.mkdir(parents=True)
    (core / "options.py").write_text("# stub")
    assert vendor._is_dirsearch_root(str(tmp_path)) is True


def test_find_raises_when_nothing_found(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("DIRSEARCH_HOME", raising=False)
    monkeypatch.delenv("DIRSEARCH_PATH", raising=False)
    monkeypatch.setattr(vendor.shutil, "which", lambda _: None)
    monkeypatch.setattr(vendor, "_CANDIDATES", [str(tmp_path / "nope")])
    with pytest.raises(FileNotFoundError) as exc:
        vendor.find()
    assert "dirsearch" in str(exc.value)


def test_find_via_env_var(monkeypatch, tmp_path: Path):
    (tmp_path / "dirsearch.py").write_text("# stub")
    monkeypatch.setenv("DIRSEARCH_HOME", str(tmp_path))
    monkeypatch.setattr(vendor.shutil, "which", lambda _: None)
    monkeypatch.setattr(vendor, "_CANDIDATES", [str(tmp_path / "nope")])
    home = vendor.find()
    assert os.path.abspath(home.path) == os.path.abspath(str(tmp_path))
    assert "env:DIRSEARCH_HOME" in home.source


def test_find_via_pip_package(monkeypatch, tmp_path: Path):
    pkg = tmp_path / "dirsearch"
    pkg.mkdir()
    (pkg / "dirsearch.py").write_text("# stub")

    class _Spec:
        origin = str(pkg / "__init__.py")

    monkeypatch.delenv("DIRSEARCH_HOME", raising=False)
    monkeypatch.delenv("DIRSEARCH_PATH", raising=False)
    monkeypatch.setattr(vendor.importlib.util, "find_spec",
                        lambda name: _Spec() if name == "dirsearch" else None)
    monkeypatch.setattr(vendor.shutil, "which", lambda _: None)
    monkeypatch.setattr(vendor, "_CANDIDATES", [str(tmp_path / "nope")])
    home = vendor.find()
    assert os.path.abspath(home.path) == os.path.abspath(str(pkg))
    assert home.source == "pip"
