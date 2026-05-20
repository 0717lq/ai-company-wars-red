"""批量重命名模块 — 按匹配模式批量重命名文件，支持序号模板。"""
import re
from fnmatch import fnmatch
from pathlib import Path


class RenameEntry:
    """表示一个重命名操作的记录。"""

    def __init__(self, src: Path, dst: Path):
        self.src = src  # 原路径
        self.dst = dst  # 新路径

    def to_dict(self) -> dict:
        """序列化为 JSON 兼容字典。"""
        return {"from": str(self.src), "to": str(self.dst)}


def _matches_any(name: str, patterns: list[str]) -> bool:
    """检查文件名是否匹配任意一个 glob 模式。"""
    for pattern in patterns:
        if fnmatch(name, pattern):
            return True
    return False


def build_rename_plan(
    path: Path,
    pattern: str,
    template: str,
    exclude: list[str] | None = None,
    exclude_dirs: list[str] | None = None,
) -> list[RenameEntry]:
    """根据匹配模式和模板构建重命名计划。

    Args:
        path: 目标目录
        pattern: 匹配模式（glob 格式，如 "*.jpg"）
        template: 目标模板（如 "photo_%04d"），
                  %d 或 %04d 等格式会被替换为序号
        exclude: 要排除的 glob 模式列表
        exclude_dirs: 要排除的目录名称列表

    Returns:
        重命名条目列表 [(原路径, 新路径)]

    Raises:
        ValueError: pattern 或 template 为空
    """
    if not pattern:
        raise ValueError("pattern 不能为空")
    if not template:
        raise ValueError("template 不能为空")

    # 收集匹配的文件
    matched: list[Path] = []
    try:
        for entry in path.iterdir():
            if not entry.is_file():
                continue
            if entry.name.startswith("."):
                continue  # 跳过隐藏文件
            if exclude and _matches_any(entry.name, exclude):
                continue
            if exclude_dirs and entry.parent.name in exclude_dirs:
                continue
            if fnmatch(entry.name, pattern):
                matched.append(entry)
    except (PermissionError, OSError):
        return []

    # 按文件名排序，确保顺序可预测
    matched.sort(key=lambda p: p.name)

    # 构建重命名计划
    entries: list[RenameEntry] = []
    for i, src in enumerate(matched, 1):
        # 替换 %d 或 %04d 等格式为序号
        # 检查模板是否包含 %d / %04d 等序号模式
        has_counter = bool(re.search(r"%\d*d", template))
        if has_counter:
            def replace_counter(m: re.Match, _i: int = i) -> str:
                fmt = m.group(0)
                # 从格式中提取宽度（如果有）
                width_match = re.search(r"%0?(\d+)?d", fmt)
                if width_match and width_match.group(1):
                    return f"{_i:0{width_match.group(1)}d}"
                return str(_i)

            new_stem = re.sub(r"%\d*d", replace_counter, template)
        else:
            new_stem = template

        # 保留原文件扩展名
        suffix = src.suffix
        new_name = f"{new_stem}{suffix}"

        dst = src.parent / new_name

        # 如果新文件名已存在，加编号后缀
        if dst.exists():
            counter = 1
            while True:
                dst = src.parent / f"{new_stem}_{counter}{suffix}"
                if not dst.exists():
                    break
                counter += 1

        # 避免src和dst相同（同名文件保留）
        if src == dst:
            continue

        entries.append(RenameEntry(src, dst))

    return entries


def execute_rename(entries: list[RenameEntry]) -> list[RenameEntry]:
    """执行重命名操作。

    Args:
        entries: 重命名条目列表

    Returns:
        实际执行成功的条目列表
    """
    executed: list[RenameEntry] = []
    for entry in entries:
        try:
            entry.src.rename(entry.dst)
            executed.append(entry)
        except (PermissionError, OSError):
            continue
    return executed
