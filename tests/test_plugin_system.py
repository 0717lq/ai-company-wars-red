"""插件系统测试 — 覆盖 plugin_base、plugin_system 和 CLI 子命令。"""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from dirsort.plugin_base import PluginBase
from dirsort.plugin_system import PluginManager

runner = CliRunner()


# ── 辅助：临时插件文件 ──────────────────────────────────────────


def _write_plugin(directory: Path, name: str = "test_plugin", **overrides) -> Path:
    """在指定目录写一个可加载的插件文件，返回文件路径。"""
    plugin_name = overrides.get("plugin_name", "test-plugin")
    version = overrides.get("version", "1.0.0")
    description = overrides.get("description", "测试插件")
    classify_return = overrides.get("classify_return", 'return "测试分类"')
    report_body = overrides.get("report_body", "return None")

    code = f'''"""测试插件。"""

from pathlib import Path
from typing import Optional

from dirsort.plugin_base import PluginBase


class TestPlugin(PluginBase):
    name = "{plugin_name}"
    version = "{version}"
    description = "{description}"

    def classify(self, file_path: Path) -> Optional[str]:
        {classify_return}

    def generate_report(self, results: dict) -> Optional[str]:
        {report_body}
'''
    p = directory / f"{name}.py"
    p.write_text(code, encoding="utf-8")
    return p


def _write_broken_plugin(directory: Path, name: str = "broken") -> Path:
    """写一个语法错误的插件文件。"""
    p = directory / f"{name}.py"
    p.write_text("import nonexistent_module_xyz_123\n", encoding="utf-8")
    return p


def _write_no_class_plugin(directory: Path, name: str = "no_class") -> Path:
    """写一个没有 PluginBase 子类的插件文件。"""
    p = directory / f"{name}.py"
    p.write_text('"""无插件类"""\nFOO = 42\n', encoding="utf-8")
    return p


# ══════════════════════════════════════════════════════════════
#  PluginBase 基类测试
# ══════════════════════════════════════════════════════════════


class TestPluginBase:
    """PluginBase 抽象基类定义正确性。"""

    def test_plugin_base_is_abstract(self):
        """PluginBase 不能直接实例化（classify 是 abstractmethod）。"""
        with pytest.raises(TypeError, match="abstract method"):
            PluginBase()

    def test_plugin_base_default_attributes(self):
        """PluginBase 的默认类属性值正确。"""
        assert PluginBase.name == "unnamed-plugin"
        assert PluginBase.version == "0.0.0"
        assert PluginBase.description == "未描述的插件"

    def test_plugin_base_repr(self):
        """PluginBase.__repr__ 输出格式正确。"""

        class Minimal(PluginBase):
            name = "minimal"
            version = "0.1.0"

            def classify(self, file_path):
                return None

        p = Minimal()
        assert repr(p) == "<Plugin 'minimal' v0.1.0>"

    def test_plugin_base_generate_report_default(self):
        """generate_report 默认返回 None。"""

        class Minimal(PluginBase):
            name = "m"
            version = "0.0.1"

            def classify(self, file_path):
                return None

        p = Minimal()
        assert p.generate_report({}) is None


# ══════════════════════════════════════════════════════════════
#  PluginManager 加载/注册测试
# ══════════════════════════════════════════════════════════════


class TestPluginManagerLoad:
    """PluginManager 发现和加载插件。"""

    def test_discover_empty_dir(self, tmp_path):
        """空插件目录返回 0 个加载。"""
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()
        mgr = PluginManager(plugin_dir=plugin_dir)
        count = mgr.discover_and_load()
        assert count == 0
        assert mgr.list_plugins() == []

    def test_discover_creates_dir(self, tmp_path):
        """插件目录不存在时自动创建。"""
        plugin_dir = tmp_path / "nonexistent" / "plugins"
        mgr = PluginManager(plugin_dir=plugin_dir)
        count = mgr.discover_and_load()
        assert count == 0
        assert plugin_dir.exists()

    def test_load_valid_plugin(self, tmp_path):
        """加载一个有效的插件文件。"""
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()
        _write_plugin(plugin_dir)
        mgr = PluginManager(plugin_dir=plugin_dir)
        count = mgr.discover_and_load()
        assert count == 1
        plugins = mgr.list_plugins()
        assert len(plugins) == 1
        assert plugins[0].name == "test-plugin"

    def test_load_multiple_plugins(self, tmp_path):
        """加载多个插件文件。"""
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()
        _write_plugin(plugin_dir, name="p1", plugin_name="plugin-1")
        _write_plugin(plugin_dir, name="p2", plugin_name="plugin-2")
        mgr = PluginManager(plugin_dir=plugin_dir)
        count = mgr.discover_and_load()
        assert count == 2
        names = {p.name for p in mgr.list_plugins()}
        assert names == {"plugin-1", "plugin-2"}

    def test_skip_underscore_files(self, tmp_path):
        """以 _ 开头的文件被跳过。"""
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()
        _write_plugin(plugin_dir, name="valid")
        (plugin_dir / "__init__.py").write_text("", encoding="utf-8")
        mgr = PluginManager(plugin_dir=plugin_dir)
        count = mgr.discover_and_load()
        assert count == 1

    def test_broken_plugin_no_crash(self, tmp_path):
        """语法错误的插件不影响其他插件加载。"""
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()
        _write_broken_plugin(plugin_dir)
        _write_plugin(plugin_dir, name="good", plugin_name="good-plugin")
        mgr = PluginManager(plugin_dir=plugin_dir)
        count = mgr.discover_and_load()
        assert count == 1
        assert mgr.list_plugins()[0].name == "good-plugin"

    def test_no_class_plugin_returns_none(self, tmp_path):
        """没有 PluginBase 子类的文件不加载。"""
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()
        _write_no_class_plugin(plugin_dir)
        mgr = PluginManager(plugin_dir=plugin_dir)
        count = mgr.discover_and_load()
        assert count == 0

    def test_get_plugin(self, tmp_path):
        """按名称获取插件。"""
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()
        _write_plugin(plugin_dir, plugin_name="my-plugin")
        mgr = PluginManager(plugin_dir=plugin_dir)
        mgr.discover_and_load()
        p = mgr.get_plugin("my-plugin")
        assert p is not None
        assert p.name == "my-plugin"
        assert mgr.get_plugin("nonexistent") is None

    def test_plugins_property_returns_copy(self, tmp_path):
        """plugins 属性返回副本，不直接暴露内部字典。"""
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()
        _write_plugin(plugin_dir)
        mgr = PluginManager(plugin_dir=plugin_dir)
        mgr.discover_and_load()
        p1 = mgr.plugins
        p2 = mgr.plugins
        assert p1 == p2
        assert p1 is not p2


# ══════════════════════════════════════════════════════════════
#  classify_file / generate_reports 测试
# ══════════════════════════════════════════════════════════════


class TestPluginHooks:
    """插件 hook 调用链测试。"""

    def test_classify_file_first_match_wins(self, tmp_path):
        """多个插件 classify 时，第一个返回非 None 的结果胜出。"""
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()

        # 第一个插件返回 None（不处理）
        _write_plugin(
            plugin_dir,
            name="p1",
            plugin_name="p1",
            classify_return="return None",
        )
        # 第二个插件返回分类
        _write_plugin(
            plugin_dir,
            name="p2",
            plugin_name="p2",
            classify_return='return "自定义分类"',
        )

        mgr = PluginManager(plugin_dir=plugin_dir)
        mgr.discover_and_load()

        test_file = tmp_path / "test.txt"
        test_file.write_text("hello", encoding="utf-8")
        result = mgr.classify_file(test_file)
        assert result == "自定义分类"

    def test_classify_file_all_none(self, tmp_path):
        """所有插件返回 None 时，classify_file 返回 None。"""
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()
        _write_plugin(
            plugin_dir,
            classify_return="return None",
        )
        mgr = PluginManager(plugin_dir=plugin_dir)
        mgr.discover_and_load()

        test_file = tmp_path / "test.txt"
        test_file.write_text("hello", encoding="utf-8")
        assert mgr.classify_file(test_file) is None

    def test_classify_file_plugin_exception(self, tmp_path):
        """插件 classify 抛异常时不影响主流程。"""
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()
        _write_plugin(
            plugin_dir,
            classify_return="raise ValueError('boom')",
        )
        mgr = PluginManager(plugin_dir=plugin_dir)
        mgr.discover_and_load()

        test_file = tmp_path / "test.txt"
        test_file.write_text("hello", encoding="utf-8")
        # 异常被捕获，返回 None
        assert mgr.classify_file(test_file) is None

    def test_generate_reports_collects(self, tmp_path):
        """generate_reports 收集所有返回非 None 的插件报告。"""
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()
        _write_plugin(
            plugin_dir,
            name="reporter",
            plugin_name="reporter",
            report_body='return "自定义报告内容"',
        )
        mgr = PluginManager(plugin_dir=plugin_dir)
        mgr.discover_and_load()

        reports = mgr.generate_reports({"total": 10})
        assert len(reports) == 1
        assert reports[0] == "自定义报告内容"

    def test_generate_reports_exception(self, tmp_path):
        """插件 generate_report 抛异常时不影响其他插件。"""
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()
        _write_plugin(
            plugin_dir,
            name="bad_report",
            plugin_name="bad-report",
            report_body="raise RuntimeError('report error')",
        )
        mgr = PluginManager(plugin_dir=plugin_dir)
        mgr.discover_and_load()

        reports = mgr.generate_reports({})
        assert reports == []


# ══════════════════════════════════════════════════════════════
#  install_plugin 测试
# ══════════════════════════════════════════════════════════════


class TestPluginInstall:
    """插件安装测试。"""

    def test_install_valid_plugin(self, tmp_path):
        """安装一个有效的插件文件。"""
        plugin_dir = tmp_path / "plugins"
        source = _write_plugin(tmp_path, plugin_name="installed")
        mgr = PluginManager(plugin_dir=plugin_dir)
        plugin = mgr.install_plugin(source)
        assert plugin.name == "installed"
        assert (plugin_dir / source.name).exists()

    def test_install_nonexistent(self, tmp_path):
        """安装不存在的文件抛出 FileNotFoundError。"""
        mgr = PluginManager(plugin_dir=tmp_path / "plugins")
        with pytest.raises(FileNotFoundError):
            mgr.install_plugin(tmp_path / "nonexistent.py")

    def test_install_non_py(self, tmp_path):
        """安装非 .py 文件抛出 ValueError。"""
        txt = tmp_path / "plugin.txt"
        txt.write_text("hello", encoding="utf-8")
        mgr = PluginManager(plugin_dir=tmp_path / "plugins")
        with pytest.raises(ValueError, match=r"\.py"):
            mgr.install_plugin(txt)

    def test_install_invalid_plugin(self, tmp_path):
        """安装没有 PluginBase 子类的文件抛出 ValueError。"""
        source = _write_no_class_plugin(tmp_path)
        mgr = PluginManager(plugin_dir=tmp_path / "plugins")
        with pytest.raises(ValueError, match="PluginBase"):
            mgr.install_plugin(source)

    def test_install_overwrites(self, tmp_path):
        """重复安装同名文件覆盖旧文件。"""
        plugin_dir = tmp_path / "plugins"
        source1 = _write_plugin(
            tmp_path, name="myplug", plugin_name="my-plug", version="1.0.0"
        )
        source2 = _write_plugin(
            tmp_path, name="myplug2", plugin_name="my-plug", version="2.0.0"
        )
        source2.rename(source1)  # 同文件名

        mgr = PluginManager(plugin_dir=plugin_dir)
        mgr.install_plugin(source1)
        # 重新写一个 v2 的同名文件
        source_v2 = _write_plugin(
            tmp_path, name="myplug", plugin_name="my-plug", version="2.0.0"
        )
        plugin = mgr.install_plugin(source_v2)
        assert plugin.version == "2.0.0"


# ══════════════════════════════════════════════════════════════
#  reload / get_plugin_info 测试
# ══════════════════════════════════════════════════════════════


class TestPluginReloadAndInfo:
    """热重载和插件信息查询。"""

    def test_reload(self, tmp_path):
        """reload 清空后重新加载。"""
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()
        _write_plugin(plugin_dir, plugin_name="before")
        mgr = PluginManager(plugin_dir=plugin_dir)
        mgr.discover_and_load()
        assert len(mgr.list_plugins()) == 1

        # 删除旧插件，加新的
        for f in plugin_dir.glob("*.py"):
            f.unlink()
        _write_plugin(plugin_dir, name="new", plugin_name="after")

        count = mgr.reload()
        assert count == 1
        assert mgr.list_plugins()[0].name == "after"

    def test_get_plugin_info(self, tmp_path):
        """get_plugin_info 返回正确信息。"""
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()
        _write_plugin(plugin_dir, plugin_name="info-test", version="2.0.0")
        mgr = PluginManager(plugin_dir=plugin_dir)
        mgr.discover_and_load()

        info = mgr.get_plugin_info("info-test")
        assert info is not None
        assert info["name"] == "info-test"
        assert info["version"] == "2.0.0"
        assert info["has_classify"] is True
        # has_report 是 True，因为 _write_plugin 生成的类覆盖了 generate_report
        assert info["has_report"] is True

    def test_get_plugin_info_nonexistent(self, tmp_path):
        """不存在的插件返回 None。"""
        mgr = PluginManager(plugin_dir=tmp_path / "plugins")
        assert mgr.get_plugin_info("nope") is None


# ══════════════════════════════════════════════════════════════
#  create_plugin_template 测试
# ══════════════════════════════════════════════════════════════


class TestPluginTemplate:
    """插件模板生成。"""

    def test_template_contains_class(self):
        """模板包含 PluginBase 子类。"""
        mgr = PluginManager()
        code = mgr.create_plugin_template("my-plugin")
        assert "class MyPlugin" in code
        assert "PluginBase" in code
        assert 'name = "my-plugin"' in code

    def test_template_safe_name(self):
        """名称中的连字符和空格被替换为下划线。"""
        mgr = PluginManager()
        code = mgr.create_plugin_template("my cool plugin")
        assert "class MyCoolPlugin" in code
        assert 'name = "my cool plugin"' in code

    def test_template_has_docstring(self):
        """模板包含文档字符串。"""
        mgr = PluginManager()
        code = mgr.create_plugin_template("demo")
        assert '"""' in code
        assert "dirsort 插件: demo" in code


# ══════════════════════════════════════════════════════════════
#  CLI 子命令测试
# ══════════════════════════════════════════════════════════════


class TestPluginCLI:
    """plugin 子命令 CLI 测试。"""

    def test_plugin_list_empty(self, tmp_path, monkeypatch):
        """plugin list 无插件时输出提示。"""
        empty_dir = tmp_path / "empty_plugins"
        empty_dir.mkdir()
        monkeypatch.setattr("dirsort.plugin_system.DEFAULT_PLUGIN_DIR", empty_dir)

        from dirsort.cli import app

        result = runner.invoke(app, ["--json", "plugin", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["operation"] == "plugin_list"
        assert data["count"] == 0

    def test_plugin_list_json(self, tmp_path, monkeypatch):
        """plugin list --json 输出格式正确。"""
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir(parents=True)
        _write_plugin(plugin_dir, plugin_name="cli-test")
        monkeypatch.setattr("dirsort.plugin_system.DEFAULT_PLUGIN_DIR", plugin_dir)

        from dirsort.cli import app

        result = runner.invoke(app, ["--json", "plugin", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["count"] == 1
        assert data["plugins"][0]["name"] == "cli-test"

    def test_plugin_install_cli(self, tmp_path):
        """plugin install 安装插件文件。"""
        source = _write_plugin(tmp_path, plugin_name="installed-cli")

        from dirsort.cli import app

        result = runner.invoke(
            app,
            ["--json", "plugin", "install", str(source)],
            env={"HOME": str(tmp_path)},
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "success"
        assert data["plugin"]["name"] == "installed-cli"

    def test_plugin_install_nonexistent(self, tmp_path):
        """plugin install 不存在的文件报错。"""
        from dirsort.cli import app

        result = runner.invoke(
            app,
            ["plugin", "install", str(tmp_path / "nope.py")],
            env={"HOME": str(tmp_path)},
        )
        assert result.exit_code == 1

    def test_plugin_create_cli(self, tmp_path):
        """plugin create 生成模板文件。"""
        from dirsort.cli import app

        out_file = tmp_path / "my_new_plugin.py"
        result = runner.invoke(
            app,
            ["--json", "plugin", "create", "my-new-plugin", "-o", str(out_file)],
            env={"HOME": str(tmp_path)},
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "created"
        assert out_file.exists()
        content = out_file.read_text(encoding="utf-8")
        assert "PluginBase" in content

    def test_plugin_info_cli(self, tmp_path, monkeypatch):
        """plugin info 输出插件详情。"""
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir(parents=True)
        _write_plugin(plugin_dir, plugin_name="info-cli", version="3.0.0")
        monkeypatch.setattr("dirsort.plugin_system.DEFAULT_PLUGIN_DIR", plugin_dir)

        from dirsort.cli import app

        result = runner.invoke(app, ["--json", "plugin", "info", "info-cli"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["plugin"]["name"] == "info-cli"
        assert data["plugin"]["version"] == "3.0.0"

    def test_plugin_info_not_found(self, tmp_path):
        """plugin info 不存在的插件报错。"""
        from dirsort.cli import app

        result = runner.invoke(
            app,
            ["plugin", "info", "nope"],
            env={"HOME": str(tmp_path)},
        )
        assert result.exit_code == 1

    def test_plugin_reload_cli(self, tmp_path):
        """plugin reload 重新加载插件。"""
        plugin_dir = tmp_path / ".dirsort" / "plugins"
        plugin_dir.mkdir(parents=True)
        _write_plugin(plugin_dir, plugin_name="reload-test")

        from dirsort.cli import app

        result = runner.invoke(
            app,
            ["--json", "plugin", "reload"],
            env={"HOME": str(tmp_path)},
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["operation"] == "plugin_reload"
        assert data["reloaded"] == 1
