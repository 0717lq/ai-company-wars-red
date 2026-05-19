"""重复文件检测模块 — 通过内容哈希（MD5）检测重复文件。"""
import hashlib
from pathlib import Path
from fnmatch import fnmatch
from .utils import get_size_str

# 分块读取大小（64KB）
CHUNK_SIZE = 64 * 1024  # 65536 bytes


class DuplicateGroup:
    """表示一组重复文件。"""

    def __init__(self, file_hash: str, files: list[Path]):
        self.file_hash = file_hash  # MD5 哈希值
        self.files = files  # 所有具有相同哈希的文件路径
        self.size = files[0].stat().st_size if files else 0  # 文件大小（字节）

    def keep_file(self) -> Path:
        """返回要保留的文件（第一个），其余为可删除的副本。"""
        return self.files[0]

    def dup_files(self) -> list[Path]:
        """返回应删除的副本文件列表。"""
        return self.files[1:]

    def to_dict(self) -> dict:
        """序列化为 JSON 兼容的字典。"""
        return {
            "hash": self.file_hash,
            "size": self.size,
            "size_str": get_size_str(self.files[0]) if self.files else "0 B",
            "files": [str(f) for f in self.files],
            "keep": str(self.files[0]),
            "duplicates": [str(f) for f in self.files[1:]],
        }


def _md5_file(path: Path) -> str | None:
    """计算文件的 MD5 哈希值。分块读取，避免大文件内存溢出。

    Args:
        path: 文件路径

    Returns:
        MD5 十六进制字符串，读取失败（权限不足等）返回 None
    """
    hasher = hashlib.md5()
    try:
        with open(path, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except (PermissionError, OSError):
        return None


def _matches_any(name: str, patterns: list[str]) -> bool:
    """检查文件名是否匹配任意一个 glob 模式。"""
    for pattern in patterns:
        if fnmatch(name, pattern):
            return True
    return False


def find_duplicates(
    path: Path,
    min_size: int = 0,
    exclude: list[str] | None = None,
    exclude_dirs: list[str] | None = None,
) -> list[DuplicateGroup]:
    """扫描目录并找出所有重复文件。

    算法：
    1. 第一遍：按文件大小分组（相同大小的文件才可能是重复的）
    2. 第二遍：对同大小的文件计算 MD5 哈希
    3. 返回哈希相同的文件组

    Args:
        path: 要扫描的目录
        min_size: 最小文件大小（跳过过小文件），单位字节
        exclude: 要排除的 glob 模式列表
        exclude_dirs: 要排除的目录名称列表

    Returns:
        重复文件组列表，每组包含哈希值和所有拥有相同内容的文件路径
    """
    # 第一遍：按文件大小分组
    size_groups: dict[int, list[Path]] = {}

    try:
        for entry in path.rglob("*"):
            if not entry.is_file():
                continue
            # 跳过隐藏文件
            if entry.name.startswith("."):
                continue
            # 检查排除模式
            if exclude and _matches_any(entry.name, exclude):
                continue
            # 检查排除目录
            if exclude_dirs and entry.parent.name in exclude_dirs:
                continue
            try:
                fsize = entry.stat().st_size
                if fsize < min_size:
                    continue
                if fsize not in size_groups:
                    size_groups[fsize] = []
                size_groups[fsize].append(entry)
            except (PermissionError, OSError):
                continue
    except (PermissionError, OSError):
        # 根目录不可读
        return []

    # 第二遍：对同大小文件计算哈希
    # 只有 ≥2 个文件相同大小时才有可能重复
    hash_groups: dict[str, list[Path]] = {}

    for size, files in size_groups.items():
        if len(files) < 2:
            continue  # 大小唯一，不可能是重复
        for f in files:
            file_hash = _md5_file(f)
            if file_hash is None:
                continue  # 无法读取的文件跳过
            if file_hash not in hash_groups:
                hash_groups[file_hash] = []
            hash_groups[file_hash].append(f)

    # 只保留实际有重复的组（≥2 个文件）
    result: list[DuplicateGroup] = []
    for file_hash, files in hash_groups.items():
        if len(files) >= 2:
            # 按路径排序，保持输出稳定
            files.sort(key=lambda p: str(p))
            result.append(DuplicateGroup(file_hash, files))

    # 按大小降序排列（大文件重复更值得关注）
    result.sort(key=lambda g: g.size, reverse=True)
    return result


def delete_duplicates(
    groups: list[DuplicateGroup],
) -> int:
    """删除每组中的重复文件（保留每组第一个文件）。

    Args:
        groups: 重复文件组列表

    Returns:
        实际删除的文件数量
    """
    deleted = 0
    for group in groups:
        for dup in group.dup_files():
            try:
                dup.unlink()
                deleted += 1
            except (PermissionError, OSError):
                continue
    return deleted
