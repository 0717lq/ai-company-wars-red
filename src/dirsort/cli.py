"""Typer CLI 定义 — dirsort 命令行入口"""
from pathlib import Path

import typer

from .sorter import analyze, organize
from .undo import UndoManager

app = typer.Typer(
    name="dirsort",
    help="智能文件目录整理工具 — 按类型或日期一键整理杂乱目录",
    add_completion=False,
)


def entry():
    """CLI 入口包装器，使 `dirsort <path>` 等价于 `dirsort sort <path>`。"""
    import sys

    # 检查第一个参数是否是已知子命令
    known_commands = {"undo", "history", "--help", "-h"}
    if len(sys.argv) > 1 and sys.argv[1] not in known_commands:
        # 将 `dirsort <path>` 转为 `dirsort sort <path>`
        sys.argv.insert(1, "sort")
    app()


@app.command()
def sort(
    path: str = typer.Argument(
        ...,
        help="要整理的目录路径",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="只预览不执行，显示分类结果"
    ),
    by_date: bool = typer.Option(
        False, "--by-date", "-d", help="按月份分类（格式 2026-05/）"
    ),
    stats: bool = typer.Option(
        False, "--stats", "-s", help="只统计不移动，显示各类文件数量"
    ),
):
    """整理指定目录中的文件。"""
    target = Path(path)
    if not target.exists() or not target.is_dir():
        typer.echo(f"错误：目录不存在或不可读: {path}")
        raise typer.Exit(1)

    # 扫描目录
    typer.echo(f"📂 正在扫描: {target}")
    categories = analyze(target, by_date=by_date)

    if stats:
        show_stats(categories)
        return

    # 预览
    print_plan(categories, target, by_date=by_date)

    if dry_run:
        typer.echo("\n⏸️  Dry-run 模式 — 未执行任何操作。移除 --dry-run 以执行。")
        return

    # 执行整理
    typer.echo("\n🔄 正在整理...")
    moves = organize(target, categories, by_date=by_date)

    # 记录到 undo 日志
    undo_mgr = UndoManager()
    undo_mgr.record(target, moves)

    typer.echo(f"\n✅ 整理完成！移动了 {len(moves)} 个文件。")
    typer.echo("💡 如需回滚，请执行: dirsort undo")


@app.command()
def undo(
    path: str = typer.Argument(
        None,
        help="要回滚的目录（留空则回滚最近一次操作）",
    ),
):
    """回滚上次整理的移动操作。"""
    undo_mgr = UndoManager()
    target = Path(path) if path else None
    count = undo_mgr.rollback(target)
    if count > 0:
        typer.echo(f"✅ 已回滚 {count} 个文件的移动操作。")
    else:
        typer.echo("ℹ️  没有找到可回滚的操作。")


@app.command()
def history():
    """查看整理历史记录。"""
    undo_mgr = UndoManager()
    records = undo_mgr.list_history()
    if not records:
        typer.echo("ℹ️  暂无整理历史记录。")
        return
    typer.echo("📋 整理历史：")
    for i, rec in enumerate(records, 1):
        ts = rec.get("timestamp", "未知时间")
        p = rec.get("source_dir", "未知目录")
        n = len(rec.get("moves", []))
        typer.echo(f"  {i}. [{ts}] {p} — {n} 个文件")


def show_stats(categories: dict):
    """显示统计信息。"""
    total = sum(len(files) for files in categories.values())
    typer.echo(f"\n📊 统计结果（共 {total} 个文件）：")
    for cat, files in sorted(categories.items()):
        if files:
            typer.echo(f"  {cat}: {len(files)} 个文件")


def print_plan(categories: dict, path: Path, by_date: bool = False):
    """打印整理计划。"""
    total = sum(len(files) for files in categories.values())
    if total == 0:
        typer.echo("✨ 目录已经很整洁了，无需整理！")
        return

    typer.echo(f"\n📋 整理计划（共 {total} 个文件）：")
    for cat, files in sorted(categories.items()):
        if not files:
            continue
        if by_date:
            target = path / cat
        else:
            target = path / cat
        typer.echo(f"\n  📁 → {target.name}/ ({len(files)} 个文件)")
        for f in files[:5]:  # 每个分类只显示前5个
            typer.echo(f"      📄 {f.name}")
        if len(files) > 5:
            typer.echo(f"      ... 还有 {len(files) - 5} 个")
