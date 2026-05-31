"""插件基类定义 — 所有 dirsort 插件必须继承 PluginBase。"""

from abc import ABC, abstractmethod
from pathlib import Path


class PluginBase(ABC):
    """dirsort 插件抽象基类。

    所有自定义插件必须继承此类并实现以下 hook：
    - classify: 自定义文件分类规则
    - generate_report: 自定义报告格式

    示例：
        class MyPlugin(PluginBase):
            name = "my-plugin"
            version = "1.0.0"
            description = "按文件大小分类"

            def classify(self, file_path: Path) -> Optional[str]:
                size = file_path.stat().st_size
                if size < 1024:
                    return "小文件"
                return None
    """

    # 插件元信息（子类必须覆盖）
    name: str = "unnamed-plugin"
    version: str = "0.0.0"
    description: str = "未描述的插件"

    @abstractmethod
    def classify(self, file_path: Path) -> str | None:
        """对单个文件进行分类。

        Args:
            file_path: 文件路径

        Returns:
            分类名称字符串（如 "图片"、"文档"），返回 None 表示
            本插件不处理此文件，交给下一个插件或内置规则。
        """

    def generate_report(self, results: dict) -> str | None:
        """生成自定义报告。

        Args:
            results: 统计结果字典，包含 categories、total 等

        Returns:
            报告文本，返回 None 表示使用默认报告。
        """
        return None

    def __repr__(self) -> str:
        return f"<Plugin '{self.name}' v{self.version}>"
