"""核心排序逻辑 — 扫描目录并按规则分类文件。"""
from pathlib import Path

from .rules import classify, get_all_categories


def analyze(path: Path, by_date: bool = False) -> dict[str, list[Path]]:
    """扫描目录，将文件按规则分类。

    Args:
        path: 要扫描的目录
        by_date: 如果为 True，按月份（'2026-05'）分类而非类型

    Returns:
        {分类名: [文件路径列表]}
    """
    categories: dict[str, list[Path]] = {}

    for entry in path.iterdir():
        if not entry.is_file():
            continue

        # 忽略隐藏文件（以 . 开头）
        if entry.name.startswith("."):
            continue

        if by_date:
            cat = _date_category(entry)
        else:
            cat = classify(entry.name)

        if cat not in categories:
            categories[cat] = []
        categories[cat].append(entry)

    return categories


def organize(
    path: Path, categories: dict[str, list[Path]], by_date: bool = False
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
        target_dir.mkdir(exist_ok=True)

        for src in files:
            dst = _resolve_conflict(target_dir, src.name)
            src.rename(dst)
            moves.append((src, dst))

    return moves


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
