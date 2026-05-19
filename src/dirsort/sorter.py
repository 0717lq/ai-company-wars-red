"""核心排序逻辑 — 扫描目录并按规则分类文件。"""
from pathlib import Path
from fnmatch import fnmatch

from .rules import classify as default_classify
from .config import get_merged_rules


def analyze(
    path: Path,
    by_date: bool = False,
    exclude: list[str] | None = None,
    exclude_dirs: list[str] | None = None,
    rules: dict[str, str] | None = None,
) -> dict[str, list[Path]]:
    """扫描目录，将文件按规则分类。

    Args:
        path: 要扫描的目录
        by_date: 如果为 True，按月份（'2026-05'）分类而非类型
        exclude: 要排除的 glob 模式列表（如 ["*.tmp", "*.log"]）
        exclude_dirs: 要排除的目录名称列表（如 ["node_modules", "__pycache__"]）
        rules: 自定义分类规则字典，默认使用 DEFAULT_RULES + 配置文件的合并结果

    Returns:
        {分类名: [文件路径列表]}
    """
    categories: dict[str, list[Path]] = {}

    # 使用配置文件的合并规则
    if rules is None:
        rules = get_merged_rules()

    for entry in path.iterdir():
        if not entry.is_file():
            continue

        # 忽略隐藏文件（以 . 开头）
        if entry.name.startswith("."):
            continue

        # 检查排除模式
        if exclude and _matches_any(entry.name, exclude):
            continue

        # 检查文件所在目录是否被排除（只检查父目录名）
        if exclude_dirs and entry.parent.name in exclude_dirs:
            continue

        try:
            if by_date:
                cat = _date_category(entry)
            else:
                cat = default_classify(entry.name, rules=rules)

            if cat not in categories:
                categories[cat] = []
            categories[cat].append(entry)
        except (PermissionError, OSError):
            # 跳过无法访问的文件，不中断整个流程
            continue

    return categories


def organize(
    path: Path,
    categories: dict[str, list[Path]],
    by_date: bool = False,
) -> list[tuple[Path, Path]]:
    """执行文件移动操作。

    Args:
        path: 目标根目录
        categories: analyze() 输出的分类结果
        by_date: 是否按日期分类

    Returns:
        [(原路径, 新路径)] 列表
    """
    moves: list[tuple[Path, Path]] = []

    for cat_name, files in categories.items():
        if not files:
            continue

        target_dir = path / cat_name
        try:
            target_dir.mkdir(exist_ok=True)
        except (PermissionError, OSError):
            # 无法创建目标目录时跳过该类别
            continue

        for src in files:
            try:
                dst = _resolve_conflict(target_dir, src.name)
                src.rename(dst)
                moves.append((src, dst))
            except (PermissionError, OSError):
                # 跳过无法移动的文件
                continue

    return moves


def _matches_any(name: str, patterns: list[str]) -> bool:
    """检查文件名是否匹配任意一个 glob 模式。"""
    for pattern in patterns:
        if fnmatch(name, pattern):
            return True
    return False


def _date_category(file: Path) -> str:
    """根据文件修改时间返回月份分类名（格式：2026-05）。"""
    mtime = file.stat().st_mtime
    from datetime import datetime

    return datetime.fromtimestamp(mtime).strftime("%Y-%m")


def _resolve_conflict(target_dir: Path, filename: str) -> Path:
    """处理文件名冲突——如果目标已存在，自动添加编号后缀。"""
    dst = target_dir / filename
    if not dst.exists():
        return dst

    stem = dst.stem
    suffix = dst.suffix
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = target_dir / new_name
        if not new_path.exists():
            return new_path
        counter += 1
