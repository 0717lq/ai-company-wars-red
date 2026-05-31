"""插件加载/注册/执行引擎 — 管理 dirsort 插件生命周期。"""

import importlib.util
import logging
import shutil
from pathlib import Path

from .plugin_base import PluginBase

# 插件默认目录
DEFAULT_PLUGIN_DIR = Path.home() / ".dirsort" / "plugins"

logger = logging.getLogger("dirsort.plugins")


class PluginManager:
    """插件管理器：加载、注册、执行插件 hook。"""

    def __init__(self, plugin_dir: Path | None = None):
        """初始化插件管理器。

        Args:
            plugin_dir: 插件目录路径，默认 ~/.dirsort/plugins/
        """
        self.plugin_dir = plugin_dir or DEFAULT_PLUGIN_DIR
        self._plugins: dict[str, PluginBase] = {}  # name -> instance

    @property
    def plugins(self) -> dict[str, PluginBase]:
        """返回已加载的插件字典。"""
        return dict(self._plugins)

    def discover_and_load(self) -> int:
        """扫描插件目录并加载所有 .py 插件文件。

        Returns:
            成功加载的插件数量
        """
        if not self.plugin_dir.exists():
            self.plugin_dir.mkdir(parents=True, exist_ok=True)
            return 0

        loaded = 0
        for py_file in sorted(self.plugin_dir.glob("*.py")):
            if py_file.name.startswith("_"):
                continue  # 跳过 __init__.py 等
            try:
                plugin = self._load_plugin_file(py_file)
                if plugin is not None:
                    self._plugins[plugin.name] = plugin
                    loaded += 1
                    logger.debug("已加载插件: %s v%s", plugin.name, plugin.version)
            except Exception as e:
                # 插件异常不影响主流程
                logger.warning("加载插件 %s 失败: %s", py_file.name, e)

        return loaded

    def _load_plugin_file(self, py_file: Path) -> PluginBase | None:
        """从单个 .py 文件加载插件实例。

        约定：文件中必须有一个继承 PluginBase 的类。
        如果有多个，取第一个。

        Args:
            py_file: .py 文件路径

        Returns:
            PluginBase 实例，或 None（无有效插件类）
        """
        spec = importlib.util.spec_from_file_location(
            f"dirsort_plugin_{py_file.stem}", str(py_file)
        )
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            logger.warning("执行插件文件 %s 时出错: %s", py_file.name, e)
            return None

        # 找到 PluginBase 子类并实例化
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, PluginBase)
                and attr is not PluginBase
            ):
                try:
                    instance = attr()
                    return instance
                except Exception as e:
                    logger.warning("实例化插件类 %s 失败: %s", attr_name, e)
                    return None

        return None

    def install_plugin(self, source_path: Path) -> PluginBase:
        """安装插件文件到插件目录。

        Args:
            source_path: 源 .py 文件路径

        Returns:
            安装后加载的插件实例

        Raises:
            FileNotFoundError: 源文件不存在
            ValueError: 文件不是有效插件
        """
        if not source_path.exists():
            raise FileNotFoundError(f"插件文件不存在: {source_path}")

        if not source_path.suffix == ".py":
            raise ValueError(f"插件文件必须是 .py 格式: {source_path}")

        # 确保插件目录存在
        self.plugin_dir.mkdir(parents=True, exist_ok=True)

        # 复制文件
        dest = self.plugin_dir / source_path.name
        shutil.copy2(source_path, dest)

        # 尝试加载验证
        plugin = self._load_plugin_file(dest)
        if plugin is None:
            dest.unlink()  # 清理无效文件
            raise ValueError(f"文件 {source_path.name} 不包含有效的 PluginBase 子类")

        self._plugins[plugin.name] = plugin
        return plugin

    def get_plugin(self, name: str) -> PluginBase | None:
        """按名称获取已加载的插件。"""
        return self._plugins.get(name)

    def list_plugins(self) -> list[PluginBase]:
        """返回所有已加载插件的列表。"""
        return list(self._plugins.values())

    def classify_file(self, file_path: Path) -> str | None:
        """通过插件链对文件进行分类。

        执行顺序：按插件加载顺序，第一个返回非 None 的结果胜出。

        Args:
            file_path: 文件路径

        Returns:
            分类名称，或 None（所有插件都未处理）
        """
        for plugin in self._plugins.values():
            try:
                result = plugin.classify(file_path)
                if result is not None:
                    return result
            except Exception as e:
                # 插件异常不影响主流程
                logger.warning("插件 %s 分类 %s 时出错: %s", plugin.name, file_path, e)
                continue
        return None

    def generate_reports(self, results: dict) -> list[str]:
        """收集所有插件的自定义报告。

        Args:
            results: 统计结果字典

        Returns:
            报告文本列表（仅包含返回非 None 的插件）
        """
        reports = []
        for plugin in self._plugins.values():
            try:
                report = plugin.generate_report(results)
                if report is not None:
                    reports.append(report)
            except Exception as e:
                logger.warning("插件 %s 生成报告时出错: %s", plugin.name, e)
                continue
        return reports

    def reload(self) -> int:
        """重新加载所有插件（热重载）。

        Returns:
            重新加载的插件数量
        """
        self._plugins.clear()
        return self.discover_and_load()

    def get_plugin_info(self, name: str) -> dict | None:
        """获取指定插件的详细信息。

        Args:
            name: 插件名称

        Returns:
            插件信息字典，或 None
        """
        plugin = self._plugins.get(name)
        if plugin is None:
            return None
        return {
            "name": plugin.name,
            "version": plugin.version,
            "description": plugin.description,
            "has_classify": True,
            "has_report": plugin.generate_report.__func__ is not PluginBase.generate_report,
        }

    def create_plugin_template(self, name: str) -> str:
        """生成插件模板脚手架代码。

        Args:
            name: 插件名称

        Returns:
            Python 模板代码字符串
        """
        safe_name = name.replace("-", "_").replace(" ", "_")
        return f'''"""dirsort 插件: {name}"""

from pathlib import Path
from typing import Optional

# 导入插件基类
from dirsort.plugin_base import PluginBase


class {safe_name.title().replace("_", "")}Plugin(PluginBase):
    """自定义插件 — 按需修改以下内容。"""

    name = "{name}"
    version = "0.1.0"
    description = "请填写插件描述"

    def classify(self, file_path: Path) -> Optional[str]:
        """自定义分类逻辑。

        Args:
            file_path: 文件路径

        Returns:
            分类名称（如 "自定义类"），返回 None 表示不处理。
        """
        # 示例：按文件大小分类
        try:
            size = file_path.stat().st_size
            if size > 100 * 1024 * 1024:  # > 100MB
                return "大文件"
        except (OSError, PermissionError):
            pass
        return None

    def generate_report(self, results: dict) -> Optional[str]:
        """自定义报告格式（可选）。

        Args:
            results: 统计结果字典

        Returns:
            报告文本，返回 None 使用默认报告。
        """
        return None
'''
