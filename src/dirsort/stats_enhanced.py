"""增强统计模块 — ASCII 图表 + 大文件 Top-N。"""

from pathlib import Path

from .utils import format_bytes

# ── ASCII 饼图 ────────────────────────────────────────────────


def render_pie_chart(
    data: dict[str, int],
    title: str = "文件类型分布",
    width: int = 40,
) -> str:
    """渲染 ASCII 饼图。

    Args:
        data: {标签: 数量} 字典
        title: 图表标题
        width: 图表宽度（字符数）

    Returns:
        ASCII 饼图字符串
    """
    if not data:
        return f"{title}\n（无数据）"

    total = sum(data.values())
    if total == 0:
        return f"{title}\n（无数据）"

    # 按数量排序（降序）
    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)

    # 选取前 8 项，其余合并为"其他"
    if len(sorted_items) > 8:
        top_items = sorted_items[:7]
        other_count = sum(v for _, v in sorted_items[7:])
        top_items.append(("其他", other_count))
        sorted_items = top_items

    # 饼图字符（Unicode 块）
    colors = [
        "\033[91m",  # 红
        "\033[92m",  # 绿
        "\033[93m",  # 黄
        "\033[94m",  # 蓝
        "\033[95m",  # 紫
        "\033[96m",  # 青
        "\033[97m",  # 白
        "\033[90m",  # 灰
    ]
    reset = "\033[0m"

    lines = [f"╔{'═' * (width - 2)}╗"]
    lines.append(f"║{title:^{width - 2}}║")
    lines.append(f"╠{'═' * (width - 2)}╣")

    # 绘制横向条形图（更实用的 ASCII 饼图替代）
    max_label_len = max(len(label) for label, _ in sorted_items)
    max_count = sorted_items[0][1] if sorted_items else 1

    for i, (label, count) in enumerate(sorted_items):
        pct = count / total * 100
        bar_width = max(1, int(count / max_count * (width - max_label_len - 15)))
        color = colors[i % len(colors)]
        bar = "█" * bar_width
        line = f" {label:<{max_label_len}} {color}{bar}{reset} {pct:5.1f}% ({count})"
        # 截断到 width
        lines.append(f"║{line:<{width - 2}}║")

    lines.append(f"╚{'═' * (width - 2)}╝")

    return "\n".join(lines)


# ── ASCII 柱状图 ──────────────────────────────────────────────


def render_bar_chart(
    data: dict[str, int],
    title: str = "统计",
    max_width: int = 40,
) -> str:
    """渲染 ASCII 柱状图（水平条形图）。

    Args:
        data: {标签: 数量} 字典
        title: 图表标题
        max_width: 最大条形宽度

    Returns:
        ASCII 柱状图字符串
    """
    if not data:
        return f"{title}\n（无数据）"

    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
    max_count = sorted_items[0][1] if sorted_items else 1
    max_label = max(len(k) for k, _ in sorted_items)

    lines = [title, "─" * (max_label + max_width + 10)]

    for label, count in sorted_items[:30]:
        bar_len = max(1, int(count / max_count * max_width)) if max_count > 0 else 0
        bar = "█" * bar_len
        lines.append(f"  {label:<{max_label}} │{bar} {count}")

    return "\n".join(lines)


# ── 大文件 Top-N ─────────────────────────────────────────────


def find_top_files(
    target: Path,
    top_n: int = 10,
    exclude: list[str] | None = None,
    exclude_dirs: list[str] | None = None,
) -> list[dict]:
    """查找目录中最大的 N 个文件。

    Args:
        target: 目标目录
        top_n: 返回前 N 个大文件
        exclude: 排除的 glob 模式列表
        exclude_dirs: 排除的目录名列表

    Returns:
        文件信息列表，每项包含 path, name, size, ext
    """
    from fnmatch import fnmatch

    files = []
    try:
        for entry in target.rglob("*"):
            if not entry.is_file():
                continue
            if entry.name.startswith("."):
                continue
            if exclude and any(fnmatch(entry.name, p) for p in exclude):
                continue
            if exclude_dirs and entry.parent.name in exclude_dirs:
                continue
            try:
                stat = entry.stat()
                files.append({
                    "path": str(entry),
                    "name": entry.name,
                    "size": stat.st_size,
                    "ext": entry.suffix.lower() if entry.suffix else "(无)",
                })
            except (OSError, PermissionError):
                continue
    except (PermissionError, OSError):
        pass

    # 按大小降序排序
    files.sort(key=lambda f: f["size"], reverse=True)
    return files[:top_n]


def render_top_files(files: list[dict], title: str = "大文件 Top-N") -> str:
    """渲染大文件 Top-N 列表。

    Args:
        files: 文件信息列表
        title: 标题

    Returns:
        格式化的文本
    """
    if not files:
        return f"{title}\n（无数据）"

    lines = [title, "─" * 70]
    lines.append(f"  {'#':>3}  {'大小':>10}  {'文件名'}")
    lines.append("─" * 70)

    for i, f in enumerate(files, 1):
        size_str = format_bytes(f["size"])
        # 截断长文件名
        name = f["name"]
        if len(name) > 45:
            name = name[:42] + "..."
        lines.append(f"  {i:>3}  {size_str:>10}  {name}")

    return "\n".join(lines)


# ── 存储分析摘要 ─────────────────────────────────────────────


def storage_summary(
    target: Path,
    exclude: list[str] | None = None,
    exclude_dirs: list[str] | None = None,
) -> dict:
    """生成存储分析摘要。

    Args:
        target: 目标目录
        exclude: 排除的 glob 模式列表
        exclude_dirs: 排除的目录名列表

    Returns:
        摘要字典，包含 total_size, file_count, by_ext, top_files
    """
    from collections import Counter
    from fnmatch import fnmatch

    ext_sizes: Counter = Counter()
    ext_counts: Counter = Counter()
    total_size = 0
    file_count = 0

    try:
        for entry in target.rglob("*"):
            if not entry.is_file():
                continue
            if entry.name.startswith("."):
                continue
            if exclude and any(fnmatch(entry.name, p) for p in exclude):
                continue
            if exclude_dirs and entry.parent.name in exclude_dirs:
                continue
            try:
                size = entry.stat().st_size
                ext = entry.suffix.lower() if entry.suffix else "(无扩展名)"
                ext_sizes[ext] += size
                ext_counts[ext] += 1
                total_size += size
                file_count += 1
            except (OSError, PermissionError):
                continue
    except (PermissionError, OSError):
        pass

    return {
        "total_size": total_size,
        "file_count": file_count,
        "by_extension": dict(ext_sizes.most_common()),
        "extension_counts": dict(ext_counts.most_common()),
    }
