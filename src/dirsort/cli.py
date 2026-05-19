"""Typer CLI 定义 — dirsort 命令行入口（Round 2 增强版）"""
from pathlib import Path

import typer

from .sorter import analyze, organize
from .undo import UndoManager
from .config import load_config, get_merged_rules

# ── Rich 降级兼容 ──────────────────────────────────────────────
try:
    from rich.console import Console
    from rich.table import Table
    from rich import box

    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    # 类型桩，确保 linter 不报未绑定错误
    Console = object  # type: ignore
    Table = object  # type: ignore
    box = object  # type: ignore

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
    execute: bool = typer.Option(
        False,
        "--execute",
        "-e",
        help="默认只预览（dry-run），加上此标志才真正执行文件移动",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="只预览不执行（默认已是 dry-run，此标志保留向后兼容）",
    ),
    by_date: bool = typer.Option(
        False, "--by-date", "-d", help="按月份分类（格式 2026-05/）"
    ),
    stats: bool = typer.Option(
        False, "--stats", "-s", help="只统计不移动，显示各类文件数量"
    ),
    exclude: list[str] = typer.Option(
        [],
        "--exclude",
        "-x",
        help="排除匹配的文件（glob 模式，可多次指定，如 --exclude '*.tmp'）",
    ),
    exclude_dir: list[str] = typer.Option(
        [],
        "--exclude-dir",
        help="排除匹配的目录（可多次指定，如 --exclude-dir node_modules）",
    ),
    config: str = typer.Option(
        None,
        "--config",
        "-c",
        help="YAML 配置文件路径，自定义分类规则",
    ),
):
    """整理指定目录中的文件。默认只预览不执行（safe dry-run）。"""
    target = Path(path)
    if not target.exists() or not target.is_dir():
        typer.echo(f"❌ 错误：目录不存在或不可读: {path}")
        raise typer.Exit(1)

    # 加载配置文件
    rules = None
    config_path = Path(config) if config else None
    if config_path is not None or load_config() is not None:
        rules = get_merged_rules(config_path)

    # 扫描目录
    if HAS_RICH:
        Console().print(f"[bold blue]📂 正在扫描:[/] {target}")
    else:
        typer.echo(f"📂 正在扫描: {target}")

    try:
        categories = analyze(
            target,
            by_date=by_date,
            exclude=list(exclude) if exclude else None,
            exclude_dirs=list(exclude_dir) if exclude_dir else None,
            rules=rules,
        )
    except (PermissionError, OSError) as e:
        typer.echo(f"❌ 无法读取目录: {e}")
        raise typer.Exit(1)

    # 加载配置信息显示
    config_info = ""
    config_path_resolved = config_path or (Path.home() / ".config" / "dirsort" / "rules.yaml")
    if rules is not None and config_path_resolved.exists():
        config_info = f"（已加载配置: {config_path_resolved}）"

    if stats:
        _show_stats(categories)
        if config_info:
            typer.echo(f"ℹ️  {config_info}")
        return

    # 预览整理计划
    _print_plan(categories, target, by_date=by_date, config_info=config_info)

    # 决定是否执行（默认 dry-run）
    # --dry-run 向后兼容：显式指定也触发 dry-run
    # --execute 时真正执行
    is_dry_run = not execute  # 默认 dry-run，--execute 才执行
    if is_dry_run:
        if HAS_RICH:
            Console().print(
                "\n[bold yellow]⏸️  Dry-run 模式 — 未执行任何操作。[/]"
            )
            Console().print(
                "[dim]使用 [bold]--execute[/] 标志来真正执行整理。[/]"
            )
        else:
            typer.echo(
                "\n⏸️  Dry-run 模式 — 未执行任何操作。使用 --execute 标志来真正执行。"
            )
        return

    # 执行整理
    if HAS_RICH:
        Console().print("\n[bold green]🔄 正在整理...[/]")
    else:
        typer.echo("\n🔄 正在整理...")

    moves = organize(target, categories, by_date=by_date)

    # 记录到 undo 日志
    undo_mgr = UndoManager()
    undo_mgr.record(target, moves)

    if HAS_RICH:
        console = Console()
        console.print(f"\n[bold green]✅ 整理完成！移动了 {len(moves)} 个文件。[/]")
        console.print("[dim]💡 如需回滚，请执行: [bold]dirsort undo[/][/]")
    else:
        typer.echo(f"\n✅ 整理完成！移动了 {len(moves)} 个文件。")
        typer.echo("💡 如需回滚，请执行: dirsort undo")


@app.command()
def undo(
    path: str = typer.Argument(
        None,
        help="要回滚的目录（留空则回滚最近一次操作）",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="显示回滚的详细文件列表"
    ),
):
    """回滚上次整理的移动操作。"""
    undo_mgr = UndoManager()
    target = Path(path) if path else None

    # 获取回滚前的历史，用于展示
    history_before = undo_mgr.list_history()
    if not history_before:
        typer.echo("ℹ️  没有找到可回滚的操作。")
        return

    # 找到要回滚的条目
    if target is None:
        rollback_entry = history_before[-1]
    else:
        src_str = str(target)
        rollback_entry = None
        for rec in reversed(history_before):
            if rec["source_dir"] == src_str:
                rollback_entry = rec
                break
        if rollback_entry is None:
            typer.echo(f"ℹ️  没有找到目录 '{path}' 的回滚记录。")
            return

    count = undo_mgr.rollback(target)

    if count > 0:
        if HAS_RICH:
            console = Console()
            # 显示回滚详情
            table = Table(title="↩️ 回滚详情", box=box.ROUNDED)
            table.add_column("文件名", style="cyan")
            table.add_column("从", style="dim")
            table.add_column("恢复至", style="green")
            for move in reversed(rollback_entry["moves"]):
                dst = Path(move["to"])
                src = Path(move["from"])
                table.add_row(dst.name, str(dst.parent), str(src.parent))
            if verbose and rollback_entry:
                console.print(table)
            console.print(f"\n[bold green]✅ 已回滚 {count} 个文件的移动操作。[/]")
        else:
            typer.echo(f"\n✅ 已回滚 {count} 个文件的移动操作。")
            if verbose and rollback_entry:
                typer.echo("回滚详情：")
                for move in reversed(rollback_entry["moves"]):
                    dst = Path(move["to"])
                    src = Path(move["from"])
                    typer.echo(f"  {dst.name}: {dst.parent} → {src.parent}")
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

    if HAS_RICH:
        console = Console()
        table = Table(title="📋 整理历史", box=box.ROUNDED)
        table.add_column("#", style="dim")
        table.add_column("时间", style="cyan")
        table.add_column("目录", style="white")
        table.add_column("文件数", style="green", justify="right")
        for i, rec in enumerate(records, 1):
            ts = rec.get("timestamp", "未知时间")[:19]  # 截断毫秒
            p = rec.get("source_dir", "未知目录")
            n = len(rec.get("moves", []))
            table.add_row(str(i), ts, p, str(n))
        console.print(table)
    else:
        typer.echo("📋 整理历史：")
        for i, rec in enumerate(records, 1):
            ts = rec.get("timestamp", "未知时间")
            p = rec.get("source_dir", "未知目录")
            n = len(rec.get("moves", []))
            typer.echo(f"  {i}. [{ts}] {p} — {n} 个文件")


# ── 内部展示函数 ──────────────────────────────────────────────


def _show_stats(categories: dict):
    """显示统计信息（支持 Rich 美化输出）。"""
    total = sum(len(files) for files in categories.values())

    if HAS_RICH:
        console = Console()
        table = Table(title=f"📊 统计结果（共 {total} 个文件）", box=box.ROUNDED)
        table.add_column("分类", style="cyan")
        table.add_column("文件数", justify="right", style="green")
        table.add_column("占比", justify="right", style="dim")
        for cat, files in sorted(categories.items()):
            if files:
                pct = f"{len(files) / total * 100:.1f}%" if total else "0%"
                table.add_row(cat, str(len(files)), pct)
        console.print(table)
    else:
        typer.echo(f"\n📊 统计结果（共 {total} 个文件）：")
        for cat, files in sorted(categories.items()):
            if files:
                typer.echo(f"  {cat}: {len(files)} 个文件")


def _print_plan(
    categories: dict,
    path: Path,
    by_date: bool = False,
    config_info: str = "",
):
    """打印整理计划（支持 Rich 美化输出）。"""
    total = sum(len(files) for files in categories.values())
    if total == 0:
        if HAS_RICH:
            Console().print("[bold green]✨ 目录已经很整洁了，无需整理！[/]")
        else:
            typer.echo("✨ 目录已经很整洁了，无需整理！")
        return

    if HAS_RICH:
        console = Console()
        table = Table(
            title=f"📋 整理计划（共 {total} 个文件）{config_info}",
            box=box.ROUNDED,
        )
        table.add_column("目标目录", style="cyan")
        table.add_column("文件数", justify="right", style="green", no_wrap=True)
        table.add_column("文件示例", style="dim")
        for cat, files in sorted(categories.items()):
            if not files:
                continue
            examples = ", ".join(f.name for f in files[:3])
            if len(files) > 3:
                examples += f" ... 及另外 {len(files) - 3} 个"
            table.add_row(f"📁 {cat}/", str(len(files)), examples)
        console.print(table)
    else:
        typer.echo(f"\n📋 整理计划（共 {total} 个文件）{config_info}")
        for cat, files in sorted(categories.items()):
            if not files:
                continue
            if by_date:
                target = path / cat
            else:
                target = path / cat
            typer.echo(f"\n  📁 → {target.name}/ ({len(files)} 个文件)")
            for f in files[:5]:
                typer.echo(f"      📄 {f.name}")
            if len(files) > 5:
                typer.echo(f"      ... 还有 {len(files) - 5} 个")
