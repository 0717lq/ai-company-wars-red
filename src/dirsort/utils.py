"""文件操作工具函数。"""
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
