"""文件操作工具函数。"""
import json
import shutil
from pathlib import Path


def get_size_str(path: Path) -> str:
    """获取文件的可读大小字符串。"""
    size = path.stat().st_size
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def count_files(path: Path) -> int:
    """统计目录中的文件数量（非递归）。"""
    return sum(1 for entry in path.iterdir() if entry.is_file())


def get_disk_usage(path: Path) -> int:
    """获取目录占用磁盘空间（字节）。"""
    total = 0
    for entry in path.iterdir():
        if entry.is_file():
            total += entry.stat().st_size
    return total


def format_bytes(size: int) -> str:
    """将字节数格式化为可读字符串。"""
    b = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


def format_json_output(data: dict, indent: int = 2) -> str:
    """将字典格式化为 JSON 字符串，支持中文不转义。

    Args:
        data: 要序列化的字典
        indent: 缩进空格数

    Returns:
        JSON 字符串
    """
    return json.dumps(data, ensure_ascii=False, indent=indent)
