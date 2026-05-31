"""示例插件：按文件大小分类。

使用方法：
    dirsort plugin install plugins/example_classifier.py
    dirsort plugin list

此插件演示了 classify hook 的基本用法，将文件按大小分为三类：
- 小文件 (< 1MB)
- 中等文件 (1MB ~ 100MB)
- 大文件 (> 100MB)
"""

from pathlib import Path
from typing import Optional

from dirsort.plugin_base import PluginBase


class SizeClassifierPlugin(PluginBase):
    """按文件大小分类的示例插件。"""

    name = "size-classifier"
    version = "1.0.0"
    description = "按文件大小分类：小文件(<1MB)、中等(1-100MB)、大文件(>100MB)"

    def classify(self, file_path: Path) -> Optional[str]:
        """根据文件大小返回分类。"""
        try:
            size = file_path.stat().st_size
            if size < 1024 * 1024:  # < 1MB
                return "小文件"
            elif size < 100 * 1024 * 1024:  # < 100MB
                return "中等文件"
            else:
                return "大文件"
        except (OSError, PermissionError):
            return None
