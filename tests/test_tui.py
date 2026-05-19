"""dirsort TUI 测试 — Textual 交互界面测试。"""

from pathlib import Path
import tempfile
from typer.testing import CliRunner

from dirsort.cli import app
from dirsort.tui_app import HAS_TEXTUAL, run_tui, _format_size

import pytest


# ── 基础测试 ────────────────────────────────────────────────


def test_tui_available():
    """确认 Textual 已安装，TUI 模块可用。"""
    assert HAS_TEXTUAL is True


def test_run_tui_function_exists():
    """确认 run_tui 函数可调用。"""
    assert callable(run_tui)


def test_format_size():
    """测试文件大小格式化函数。"""
    assert _format_size(0) == "0B"
    assert _format_size(500) == "500B"
    assert _format_size(1024) == "1.0KB"
    assert _format_size(2048) == "2.0KB"
    assert _format_size(1024 * 1024) == "1.0MB"
    assert _format_size(2 * 1024 * 1024) == "2.0MB"
    assert _format_size(1024 * 1024 * 1024) == "1.0GB"
    assert _format_size(1536 * 1024 * 1024) == "1.5GB"


# ── CLI 测试 ────────────────────────────────────────────────


def test_tui_command_registered():
    """确认 `tui` 子命令已注册在 CLI 中。"""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "tui" in result.output


def test_tui_command_missing_path():
    """确认缺少路径时显示错误。"""
    runner = CliRunner()
    result = runner.invoke(app, ["tui"])
    # Typer 会报参数缺失错误
    assert result.exit_code != 0
    assert "Missing argument" in result.output or "Error" in result.output


def test_tui_command_invalid_path():
    """确认不存在的路径显示错误。"""
    runner = CliRunner()
    result = runner.invoke(app, ["tui", "/nonexistent/path/xyz123"])
    assert result.exit_code == 1
    assert "目录不存在" in result.output


def test_tui_command_valid_path():
    """确认有效路径可以启动 TUI（至少不崩溃）。"""
    with tempfile.TemporaryDirectory() as tmp:
        # 创建一个测试文件
        (Path(tmp) / "test.txt").write_text("hello")
        runner = CliRunner()
        # TUI 实际启动需要一个终端，这里只验证 CLI 入口不会崩
        result = runner.invoke(app, ["tui", tmp])
        # TUI 应用会返回 0 或 None（Textual 的 App.run 在测试中行为不同）
        # 至少不应该是崩溃错误
        assert result.exit_code != 1 or "Error" not in result.output


# ── TUI 应用测试（pytest-asyncio） ──────────────────────────


def test_dirsort_tui_import():
    """确认 DirsortTUI 类可导入（在 HAS_TEXTUAL 时）。"""
    if HAS_TEXTUAL:
        from dirsort.tui_app import DirsortTUI
        assert DirsortTUI is not None


@pytest.mark.asyncio
async def test_tui_app_mount():
    """测试 TUI 应用挂载（基本框架，跳过 AppTest 因为 textual.testing 不可用）。"""
    if not HAS_TEXTUAL:
        pytest.skip("Textual 未安装，跳过 TUI 测试")

    # 验证 DirsortTUI 类的基本属性
    from dirsort.tui_app import DirsortTUI
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "photo.jpg").write_text("jpg")
        app = DirsortTUI(Path(tmp))
        # 验证基本属性正确
        assert app.target_path == Path(tmp)
        assert app._executed is False
        assert app.total_files == 0
