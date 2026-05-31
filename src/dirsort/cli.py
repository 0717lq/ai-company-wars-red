"""Typer CLI 定义 — dirsort 命令行入口。"""
from fnmatch import fnmatch
from pathlib import Path

import typer

from . import __version__
from .config import (
    DEFAULT_CONFIG_FILE,
    config_content,
    create_default_config,
    get_merged_rules,
    load_config,
)
from .dupes import (
    find_duplicates,
)
from .plugin_system import PluginManager
from .rename import build_rename_plan, execute_rename
from .sorter import analyze, organize
from .stats_enhanced import (
    find_top_files,
    render_pie_chart,
    storage_summary,
)
from .tui_app import run_tui as _run_tui
from .undo import UndoManager
from .utils import format_bytes, format_json_output

# ── Rich 降级兼容 ──────────────────────────────────────────────
try:
    from rich import box
    from rich.console import Console
    from rich.progress import track
    from rich.table import Table

    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    # 类型桩，确保 linter 不报未绑定错误
    Console = object  # type: ignore
    Table = object  # type: ignore
    box = object  # type: ignore
    track = None  # type: ignore


# ── 全局 --json 上下文 ─────────────────────────────────────────


def _is_json(ctx: typer.Context) -> bool:
    """检查是否启用了 JSON 输出模式。"""
    return ctx.obj and ctx.obj.get("json", False)


def _build_metadata() -> dict:
    """构建 JSON 输出的 metadata 字段（版本、插件、引擎）。"""
    from . import __version__
    mgr = PluginManager()
    mgr.discover_and_load()
    plugins = [{"name": p.name, "version": p.version} for p in mgr.list_plugins()]
    return {
        "version": __version__,
        "engine": f"dirsort/{__version__}",
        "plugins": plugins,
    }


# ── Typer 应用 ─────────────────────────────────────────────────


def make_app() -> typer.Typer:
    """创建 Typer 应用实例。"""
    return typer.Typer(
        name="dirsort",
        help="智能文件目录整理工具 — 一键解决杂乱目录的烦恼。",
        add_completion=True,
        no_args_is_help=True,
        context_settings={"help_option_names": ["--help", "-h"]},
    )


app = make_app()


@app.callback()
def main(
    ctx: typer.Context,
    json: bool = typer.Option(False, "--json", help="以 JSON 格式输出结果"),
    version: bool = typer.Option(False, "--version", help="显示版本号并退出"),
):
    """智能文件目录整理工具 — 按类型或日期一键整理杂乱目录。"""
    ctx.ensure_object(dict)
    ctx.obj["json"] = json
    if version:
        typer.echo(f"dirsort {__version__}")
        raise typer.Exit()


def entry():
    """CLI 入口包装器，使 `dirsort <path>` 等价于 `dirsort sort <path>`。"""
    import sys

    # 检查第一个参数是否是已知子命令
    known_commands = {
        "sort", "undo", "history", "init", "config",
        "dupes", "rename", "stats", "tui", "plugin",
        "--help", "-h", "--install-completion",
        "--show-completion",
    }
    if len(sys.argv) > 1 and sys.argv[1] not in known_commands:
        # 将 `dirsort <path>` 转为 `dirsort sort <path>`
        sys.argv.insert(1, "sort")
    app()


# ══════════════════════════════════════════════════════════════
#  子命令：sort
# ══════════════════════════════════════════════════════════════


@app.command()
def sort(
    ctx: typer.Context,
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
        help="排除匹配的文件（glob 模式，可多次指定）",
    ),
    exclude_dir: list[str] = typer.Option(
        [],
        "--exclude-dir",
        help="排除匹配的目录（可多次指定）",
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
    if not _is_json(ctx):
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

    if stats:
        _sort_stats(ctx, categories, rules, config_path)
        return

    total = sum(len(files) for files in categories.values())

    if total == 0:
        if _is_json(ctx):
            typer.echo(format_json_output({
                "operation": "sort",
                "path": str(target),
                "status": "clean",
                "message": "目录已经很整洁了，无需整理",
                "metadata": _build_metadata(),
            }))
        elif HAS_RICH:
            Console().print("[bold green]✨ 目录已经很整洁了，无需整理！[/]")
        else:
            typer.echo("✨ 目录已经很整洁了，无需整理！")
        return

    is_dry_run = not execute

    if _is_json(ctx):
        # JSON 输出
        plan_data: list[dict] = []
        for cat, files in sorted(categories.items()):
            if not files:
                continue
            plan_data.append({
                "category": cat,
                "count": len(files),
                "files": [str(f.name) for f in files[:10]],
            })
        typer.echo(format_json_output({
            "operation": "sort",
            "path": str(target),
            "status": "dry_run" if is_dry_run else "executed",
            "total": total,
            "categories": plan_data,
            "metadata": _build_metadata(),
        }))
        if is_dry_run:
            return
    else:
        _print_plan(categories, target, by_date=by_date)
        if is_dry_run:
            if HAS_RICH:
                Console().print(
                    "\n[bold yellow]⏸️  Dry-run 模式 — 未执行任何操作。[/]"
                )
                Console().print("[dim]使用 [bold]--execute[/] 标志来真正执行整理。[/]")
            else:
                typer.echo("\n⏸️  Dry-run 模式 — 未执行任何操作。使用 --execute 标志来真正执行。")
            return

    # 执行整理
    if not _is_json(ctx) and HAS_RICH:
        Console().print("\n[bold green]🔄 正在整理...[/]")
    else:
        pass

    moves = organize(target, categories, by_date=by_date)
    undo_mgr = UndoManager()
    undo_mgr.record(target, moves, operation_type="sort")

    if not _is_json(ctx):
        if HAS_RICH:
            Console().print(f"\n[bold green]✅ 整理完成！移动了 {len(moves)} 个文件。[/]")
            Console().print("[dim]💡 如需回滚，请执行: [bold]dirsort undo[/][/]")
        else:
            typer.echo(f"\n✅ 整理完成！移动了 {len(moves)} 个文件。")
            typer.echo("💡 如需回滚，请执行: dirsort undo")


# ══════════════════════════════════════════════════════════════
#  子命令：init（新建配置）
# ══════════════════════════════════════════════════════════════


@app.command()
def init(
    ctx: typer.Context,
    global_: bool = typer.Option(
        False, "--global", help="在用户全局目录创建默认配置文件",
    ),
):
    """创建默认配置文件 ~/.config/dirsort/rules.yaml。"""
    config_path = create_default_config()

    if _is_json(ctx):
        typer.echo(format_json_output({
            "operation": "init",
            "path": str(config_path),
            "status": "created" if config_path.exists() else "exists",
        }))
    else:
        if HAS_RICH:
            console = Console()
            console.print(f"[bold green]✅ 已创建配置文件:[/] {config_path}")
            console.print("[dim]💡 使用 [bold]dirsort config[/] 查看配置内容")
        else:
            typer.echo(f"✅ 已创建配置文件: {config_path}")
            typer.echo("💡 使用 'dirsort config' 查看配置内容")


# ══════════════════════════════════════════════════════════════
#  子命令：config（查看配置）
# ══════════════════════════════════════════════════════════════


@app.command()
def config(
    ctx: typer.Context,
    path: bool = typer.Option(
        False, "--path", help="显示配置文件路径",
    ),
):
    """查看当前配置文件内容。"""
    if path:
        if _is_json(ctx):
            typer.echo(format_json_output({
                "operation": "config_path",
                "path": str(DEFAULT_CONFIG_FILE),
                "exists": DEFAULT_CONFIG_FILE.exists(),
            }))
        else:
            if HAS_RICH:
                console = Console()
                console.print(f"[bold]配置文件路径:[/] {DEFAULT_CONFIG_FILE}")
            else:
                typer.echo(f"配置文件路径: {DEFAULT_CONFIG_FILE}")
        return

    content = config_content()
    if content is None:
        if _is_json(ctx):
            typer.echo(format_json_output({
                "operation": "config",
                "status": "not_found",
                "path": str(DEFAULT_CONFIG_FILE),
            }))
        else:
            if HAS_RICH:
                console = Console()
                console.print("[yellow]⚠️  配置文件不存在。[/]")
                console.print("[dim]使用 [bold]dirsort init[/] 创建默认配置。[/]")
            else:
                typer.echo("⚠️  配置文件不存在。")
                typer.echo("使用 'dirsort init' 创建默认配置。")
        return

    if _is_json(ctx):
        typer.echo(format_json_output({
            "operation": "config",
            "status": "found",
            "path": str(DEFAULT_CONFIG_FILE),
            "content": content,
        }))
    else:
        if HAS_RICH:
            console = Console()
            console.print(f"[bold]📄 {DEFAULT_CONFIG_FILE}[/]\n")
            console.print(content)
        else:
            typer.echo(f"📄 {DEFAULT_CONFIG_FILE}")
            typer.echo("")
            typer.echo(content)


# ══════════════════════════════════════════════════════════════
#  子命令：dupes（重复文件检测）
# ══════════════════════════════════════════════════════════════


@app.command()
def dupes(
    ctx: typer.Context,
    path: str = typer.Argument(
        ...,
        help="要扫描的目录路径",
    ),
    min_size: str = typer.Option(
        "0", "--min-size", help="最小文件大小（如 1MB, 100KB, 0=不限）",
    ),
    delete: bool = typer.Option(
        False, "--delete", help="删除重复文件（保留每个分组第一个）",
    ),
    dry_run: bool = typer.Option(
        True, "--dry-run", "-n", help="仅预览不删除（默认启用）",
    ),
    exclude: list[str] = typer.Option(
        [], "--exclude", "-x", help="排除匹配的文件（glob 模式）",
    ),
    exclude_dir: list[str] = typer.Option(
        [], "--exclude-dir", help="排除匹配的目录名",
    ),
):
    """检测指定目录中的重复文件（相同 MD5 内容）。"""
    target = Path(path)
    if not target.exists() or not target.is_dir():
        typer.echo(f"❌ 错误：目录不存在或不可读: {path}")
        raise typer.Exit(1)

    # 解析 --min-size 参数
    size_bytes = _parse_size(min_size)

    if not _is_json(ctx) and HAS_RICH:
        Console().print(f"[bold blue]🔍 正在扫描重复文件:[/] {target}")

    groups = find_duplicates(
        target,
        min_size=size_bytes,
        exclude=list(exclude) if exclude else None,
        exclude_dirs=list(exclude_dir) if exclude_dir else None,
    )

    if not groups:
        if _is_json(ctx):
            typer.echo(format_json_output({
                "operation": "dupes",
                "path": str(target),
                "groups": [],
                "total_duplicates": 0,
                "savable_bytes": 0,
            }))
        elif HAS_RICH:
            Console().print("[bold green]✅ 没有找到重复文件！[/]")
        else:
            typer.echo("✅ 没有找到重复文件！")
        return

    total_dupes = sum(len(g.dup_files()) for g in groups)
    savable_bytes = sum(g.size for g in groups)

    if _is_json(ctx):
        typer.echo(format_json_output({
            "operation": "dupes",
            "path": str(target),
            "groups": [g.to_dict() for g in groups],
            "total_duplicates": total_dupes,
            "savable_bytes": savable_bytes,
            "dry_run": not delete,
        }))
        if delete:
            _execute_dupes_delete(groups, ctx)
        return

    _print_dupes_result(groups, total_dupes, savable_bytes)

    if delete:
        _execute_dupes_delete(groups, ctx)


def _print_dupes_result(
    groups: list, total_dupes: int, savable_bytes: int,
):
    """用 Rich 美化输出重复文件检测结果。"""
    if HAS_RICH:
        console = Console()
        # 按重复文件数排序，显示前几组
        sorted_groups = sorted(groups, key=lambda g: len(g.files), reverse=True)
        console.print(f"\n[bold red]🔁 发现 {total_dupes} 个重复文件（可节省 {format_bytes(savable_bytes)}）[/]")

        table = Table(box=box.ROUNDED)
        table.add_column("分组", style="dim")
        table.add_column("哈希值（前8位）", style="cyan")
        table.add_column("大小", style="green", justify="right")
        table.add_column("重复文件数", style="red", justify="right")
        table.add_column("保留/删除", style="white")

        for i, g in enumerate(sorted_groups[:15], 1):
            keep = g.files[0].name
            dupes_only = [f.name for f in g.files[1:]]
            h_short = g.file_hash[:8]
            table.add_row(
                str(i), h_short,
                get_size_display(g.size),
                str(len(g.dup_files())),
                f"保留: {keep}\n删除: {', '.join(dupes_only[:3])}" +
                (f" …等{len(dupes_only)-3}个" if len(dupes_only) > 3 else ""),
            )

        if len(sorted_groups) > 15:
            console.print(f"[dim]…以及另外 {len(sorted_groups) - 15} 组[/]")

        console.print(table)
        console.print("[dim]💡 使用 [bold]--delete[/] 标志删除重复文件（保留每组第一个）。[/]")
    else:
        typer.echo(f"\n🔁 发现 {total_dupes} 个重复文件（可节省 {format_bytes(savable_bytes)}）")
        for i, g in enumerate(groups[:10], 1):
            typer.echo(f"  {i}. 哈希={g.file_hash[:8]}… ({len(g.files)} 个副本)")
            for f in g.files[:5]:
                typer.echo(f"     📄 {f}")
        typer.echo("\n💡 使用 --delete 标志删除重复文件。")


def _execute_dupes_delete(groups: list, ctx: typer.Context):
    """执行重复文件删除并记录到 undo 日志。"""
    undo_mgr = UndoManager()
    deleted_files: list[tuple[Path, Path]] = []

    for group in groups:
        for dup in group.dup_files():
            # 记录用于 undo（from=当前路径, to=空路径标记删除）
            deleted_files.append((dup, dup))
            try:
                dup.unlink()
            except (PermissionError, OSError):
                continue

    if deleted_files:
        # 记录删除操作到 undo 日志
        deleted_dirs: set[Path] = set()
        for src, _ in deleted_files:
            deleted_dirs.add(src.parent)

        # 为每个目录记录一次
        for d in deleted_dirs:
            group_moves = [(src, src) for src, _ in deleted_files if src.parent == d]
            if group_moves:
                undo_mgr.record(d, group_moves, operation_type="dupes_delete")

        if not _is_json(ctx):
            if HAS_RICH:
                Console().print(
                    f"\n[bold green]✅ 已删除 {len(deleted_files)} 个重复文件。[/]"
                )
                Console().print("[dim]💡 使用 [bold]dirsort undo[/] 无法恢复已删除文件（物理删除）。[/]")
            else:
                typer.echo(f"\n✅ 已删除 {len(deleted_files)} 个重复文件。")
                typer.echo("⚠️  已删除的文件无法通过 undo 恢复。")


# ══════════════════════════════════════════════════════════════
#  子命令：rename（批量重命名）
# ══════════════════════════════════════════════════════════════


@app.command()
def rename(
    ctx: typer.Context,
    path: str = typer.Argument(
        ...,
        help="目标目录路径",
    ),
    pattern: str = typer.Argument(
        ...,
        help="匹配模式（glob 格式，如 \"*.jpg\"）",
    ),
    template: str = typer.Argument(
        ...,
        help="重命名模板（如 \"photo_%04d\"），%d 替换为序号",
    ),
    execute: bool = typer.Option(
        False, "--execute", "-e",
        help="实际执行重命名（默认仅预览）",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n",
        help="仅预览不执行",
    ),
    exclude: list[str] = typer.Option(
        [], "--exclude", "-x", help="排除匹配的文件（glob 模式）",
    ),
    exclude_dir: list[str] = typer.Option(
        [], "--exclude-dir", help="排除匹配的目录名",
    ),
):
    """批量重命名文件。默认只预览不执行。"""
    target = Path(path)
    if not target.exists() or not target.is_dir():
        typer.echo(f"❌ 错误：目录不存在或不可读: {path}")
        raise typer.Exit(1)

    try:
        entries = build_rename_plan(
            target,
            pattern,
            template,
            exclude=list(exclude) if exclude else None,
            exclude_dirs=list(exclude_dir) if exclude_dir else None,
        )
    except ValueError as e:
        typer.echo(f"❌ 参数错误: {e}")
        raise typer.Exit(1)

    if not entries:
        if _is_json(ctx):
            typer.echo(format_json_output({
                "operation": "rename",
                "path": str(target),
                "pattern": pattern,
                "template": template,
                "entries": [],
                "count": 0,
            }))
        else:
            typer.echo("ℹ️  没有找到匹配的文件。")
        return

    is_dry_run = not execute

    if _is_json(ctx):
        typer.echo(format_json_output({
            "operation": "rename",
            "path": str(target),
            "pattern": pattern,
            "template": template,
            "entries": [e.to_dict() for e in entries],
            "count": len(entries),
            "dry_run": is_dry_run,
        }))
        if not is_dry_run:
            _execute_rename_and_record(entries, ctx)
        return

    _print_rename_plan(entries, target, pattern, template)

    if is_dry_run:
        if HAS_RICH:
            Console().print("\n[bold yellow]⏸️  预览模式 — 未执行任何操作。[/]")
            Console().print("[dim]使用 [bold]--execute[/] 标志来真正执行重命名。[/]")
        else:
            typer.echo("\n⏸️  预览模式 — 未执行任何操作。使用 --execute 标志来真正执行。")
        return

    _execute_rename_and_record(entries, ctx)


def _print_rename_plan(
    entries: list, path: Path, pattern: str, template: str,
):
    """打印重命名计划。"""
    if HAS_RICH:
        console = Console()
        console.print(f"[bold blue]📋 重命名计划:[/] {path}（模式: {pattern} → {template}）")

        table = Table(box=box.ROUNDED)
        table.add_column("#", style="dim")
        table.add_column("原文件名", style="cyan")
        table.add_column("新文件名", style="green")
        for i, e in enumerate(entries[:20], 1):
            table.add_row(str(i), e.src.name, e.dst.name)
        console.print(table)
        if len(entries) > 20:
            console.print(f"[dim]…及另外 {len(entries) - 20} 个文件[/]")
        console.print(f"[dim]共 {len(entries)} 个文件将被重命名。[/]")
    else:
        typer.echo(f"\n📋 重命名计划: {path}（共 {len(entries)} 个文件）")
        for i, e in enumerate(entries[:10], 1):
            typer.echo(f"  {i}. {e.src.name} → {e.dst.name}")


def _execute_rename_and_record(entries: list, ctx: typer.Context):
    """执行重命名并记录到 undo 日志。"""
    executed = execute_rename(entries)
    if executed:
        undo_mgr = UndoManager()
        moves = [(e.src, e.dst) for e in executed]
        undo_mgr.record(executed[0].src.parent, moves, operation_type="rename")

        if not _is_json(ctx):
            if HAS_RICH:
                Console().print(f"\n[bold green]✅ 已重命名 {len(executed)} 个文件。[/]")
                Console().print("[dim]💡 使用 [bold]dirsort undo[/] 可回滚此操作。[/]")
            else:
                typer.echo(f"\n✅ 已重命名 {len(executed)} 个文件。")
                typer.echo("💡 使用 'dirsort undo' 可回滚此操作。")


# ══════════════════════════════════════════════════════════════
#  子命令：undo（回滚）
# ══════════════════════════════════════════════════════════════


@app.command()
def undo(
    ctx: typer.Context,
    path: str = typer.Argument(
        None,
        help="要回滚的目录（留空则回滚最近一次操作）",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="显示回滚的详细文件列表"
    ),
):
    """回滚上次整理/重命名操作。"""
    undo_mgr = UndoManager()
    target = Path(path) if path else None

    history_before = undo_mgr.list_history()
    if not history_before:
        if _is_json(ctx):
            typer.echo(format_json_output({
                "operation": "undo",
                "status": "no_history",
                "files_restored": 0,
            }))
        else:
            typer.echo("ℹ️  没有找到可回滚的操作。")
        return

    count = undo_mgr.rollback(target)

    if _is_json(ctx):
        typer.echo(format_json_output({
            "operation": "undo",
            "status": "done" if count > 0 else "no_history",
            "files_restored": count,
        }))
        return

    if count > 0:
        if HAS_RICH:
            console = Console()
            if verbose and history_before:
                rollback_entry = history_before[-1]
                table = Table(title="↩️ 回滚详情", box=box.ROUNDED)
                table.add_column("文件名", style="cyan")
                table.add_column("操作类型", style="yellow")
                table.add_column("从", style="dim")
                table.add_column("恢复至", style="green")
                for move in reversed(rollback_entry.get("moves", [])):
                    dst = Path(move["to"])
                    src = Path(move["from"])
                    op_type = history_before[-1].get("operation_type", "sort")
                    table.add_row(dst.name, op_type, str(dst.parent), str(src.parent))
                console.print(table)
            console.print(f"\n[bold green]✅ 已回滚 {count} 个文件的操作。[/]")
        else:
            typer.echo(f"\n✅ 已回滚 {count} 个文件的操作。")
            if verbose and history_before:
                rollback_entry = history_before[-1]
                typer.echo("回滚详情：")
                for move in reversed(rollback_entry.get("moves", [])):
                    dst = Path(move["to"])
                    src = Path(move["from"])
                    typer.echo(f"  {dst.name}: {dst.parent} → {src.parent}")
    else:
        if _is_json(ctx):
                    typer.echo(format_json_output({
                "operation": "undo",
                "status": "no_history",
                "files_restored": 0,
            }))
        else:
            typer.echo("ℹ️  没有找到可回滚的操作。")


# ══════════════════════════════════════════════════════════════
#  子命令：history（查看历史）
# ══════════════════════════════════════════════════════════════


@app.command()
def history(
    ctx: typer.Context,
):
    """查看操作历史记录。"""
    undo_mgr = UndoManager()
    records = undo_mgr.list_history()
    if not records:
        if _is_json(ctx):
            typer.echo(format_json_output({
                "operation": "history",
                "records": [],
            }))
        else:
            typer.echo("ℹ️  暂无操作历史记录。")
        return

    if _is_json(ctx):
        typer.echo(format_json_output({
            "operation": "history",
            "records": [
                {
                    "timestamp": r.get("timestamp", ""),
                    "source_dir": r.get("source_dir", ""),
                    "operation_type": r.get("operation_type", "sort"),
                    "file_count": len(r.get("moves", [])),
                }
                for r in records
            ],
        }))
        return

    if HAS_RICH:
        console = Console()
        table = Table(title="📋 操作历史", box=box.ROUNDED)
        table.add_column("#", style="dim")
        table.add_column("时间", style="cyan")
        table.add_column("目录", style="white")
        table.add_column("操作类型", style="yellow")
        table.add_column("文件数", style="green", justify="right")
        for i, rec in enumerate(records, 1):
            ts = rec.get("timestamp", "未知时间")[:19]
            p = rec.get("source_dir", "未知目录")
            n = len(rec.get("moves", []))
            op_type = rec.get("operation_type", "sort")
            table.add_row(str(i), ts, p, op_type, str(n))
        console.print(table)
    else:
        typer.echo("📋 操作历史：")
        for i, rec in enumerate(records, 1):
            ts = rec.get("timestamp", "未知时间")
            p = rec.get("source_dir", "未知目录")
            n = len(rec.get("moves", []))
            op_type = rec.get("operation_type", "sort")
            typer.echo(f"  {i}. [{ts}] ({op_type}) {p} — {n} 个文件")


# ══════════════════════════════════════════════════════════════
#  子命令：stats（增强统计）
# ══════════════════════════════════════════════════════════════


@app.command()
def stats(
    ctx: typer.Context,
    path: str = typer.Argument(
        None,
        help="要统计的目录路径（留空则仅显示全局信息）",
    ),
    by_type: bool = typer.Option(
        False, "--by-type", "--by-extension",
        help="按扩展名分组显示（而非默认分类）",
    ),
    chart: bool = typer.Option(
        False, "--chart", help="显示条形图",
    ),
    pie: bool = typer.Option(
        False, "--pie", help="显示 ASCII 饼图（文件类型分布）",
    ),
    top: int = typer.Option(
        0, "--top", "-t", help="显示大文件 Top-N 排行（如 --top 10）",
    ),
    exclude: list[str] = typer.Option(
        [], "--exclude", "-x", help="排除匹配的文件",
    ),
    exclude_dir: list[str] = typer.Option(
        [], "--exclude-dir", help="排除匹配的目录",
    ),
):
    """统计目录中的文件信息，支持按扩展名分组和图表。"""
    if not path:
        typer.echo("ℹ️  请指定要统计的目录路径。")
        typer.echo("示例: dirsort stats ~/Downloads")
        raise typer.Exit(1)

    target = Path(path)
    if not target.exists() or not target.is_dir():
        typer.echo(f"❌ 错误：目录不存在或不可读: {path}")
        raise typer.Exit(1)

    categories = analyze(
        target,
        exclude=list(exclude) if exclude else None,
        exclude_dirs=list(exclude_dir) if exclude_dir else None,
    )

    # --top N: 显示大文件排行
    if top > 0:
        _stats_top_files(ctx, target, top, exclude, exclude_dir)
        return

    # --pie: 显示 ASCII 饼图
    if pie:
        _stats_pie_chart(ctx, target, categories, exclude, exclude_dir)
        return

    if by_type:
        _sort_stats_by_type(ctx, target, exclude, exclude_dir, show_chart=chart)
    else:
        _sort_stats(ctx, categories, None, None)


def _sort_stats(
    ctx: typer.Context,
    categories: dict,
    rules: dict | None,
    config_path: Path | None,
):
    """显示分类统计信息。"""
    total = sum(len(files) for files in categories.values())

    if _is_json(ctx):
        typer.echo(format_json_output({
            "operation": "stats",
            "total_files": total,
            "categories": {
                cat: len(files) for cat, files in sorted(categories.items())
                if files
            },
        }))
        return

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


def _sort_stats_by_type(
    ctx: typer.Context,
    target: Path,
    exclude: list[str] | None,
    exclude_dirs: list[str] | None,
    show_chart: bool = False,
):
    """按扩展名分组统计。"""
    from collections import Counter
    ext_counts: Counter = Counter()

    try:
        for entry in target.rglob("*"):
            if not entry.is_file():
                continue
            if entry.name.startswith("."):
                continue
            if exclude and any(fnmatch_match(entry.name, p) for p in exclude):
                continue
            if exclude_dirs and entry.parent.name in exclude_dirs:
                continue
            try:
                ext = entry.suffix.lower() if entry.suffix else "(无扩展名)"
                ext_counts[ext] += 1
            except (PermissionError, OSError):
                continue
    except (PermissionError, OSError):
        typer.echo(f"❌ 无法读取目录: {target}")
        raise typer.Exit(1)

    if not ext_counts:
        if _is_json(ctx):
            typer.echo(format_json_output({
                "operation": "stats_by_type",
                "extensions": {},
                "total": 0,
            }))
        else:
            typer.echo("ℹ️  没有找到文件。")
        return

    total = sum(ext_counts.values())
    sorted_exts = ext_counts.most_common()

    if _is_json(ctx):
        typer.echo(format_json_output({
            "operation": "stats_by_type",
            "total": total,
            "extensions": {ext: count for ext, count in sorted_exts},
        }))
        return

    if HAS_RICH:
        console = Console()
        table = Table(
            title=f"📊 按扩展名统计（共 {total} 个文件）",
            box=box.ROUNDED,
        )
        table.add_column("扩展名", style="cyan")
        table.add_column("文件数", justify="right", style="green")
        table.add_column("占比", style="dim")

        max_count = sorted_exts[0][1] if sorted_exts else 0
        for ext, count in sorted_exts[:30]:
            pct = f"{count / total * 100:.1f}%"
            bar = _make_bar(count, max_count) if show_chart else ""
            label = f"{ext} {bar}" if bar else ext
            table.add_row(label, str(count), pct)

        if len(sorted_exts) > 30:
            other = sum(c for _, c in sorted_exts[30:])
            table.add_row("其他", str(other), f"{other / total * 100:.1f}%")

        console.print(table)
    else:
        typer.echo(f"\n📊 按扩展名统计（共 {total} 个文件）：")
        for ext, count in sorted_exts[:20]:
            bar = _make_bar(count, sorted_exts[0][1]) if show_chart else ""
            typer.echo(f"  {ext}: {count} {bar}")


def _stats_top_files(
    ctx: typer.Context,
    target: Path,
    top_n: int,
    exclude: list[str],
    exclude_dirs: list[str],
):
    """显示大文件 Top-N 排行。"""
    top_files = find_top_files(
        target,
        top_n=top_n,
        exclude=list(exclude) if exclude else None,
        exclude_dirs=list(exclude_dirs) if exclude_dirs else None,
    )

    if _is_json(ctx):
        typer.echo(format_json_output({
            "operation": "stats_top",
            "path": str(target),
            "top_n": top_n,
            "files": top_files,
        }))
        return

    if not top_files:
        typer.echo("ℹ️  没有找到文件。")
        return

    if HAS_RICH:
        console = Console()
        table = Table(
            title=f"📊 大文件 Top-{top_n}",
            box=box.ROUNDED,
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("大小", style="green", justify="right")
        table.add_column("扩展名", style="cyan")
        table.add_column("文件名", style="white")

        for i, f in enumerate(top_files, 1):
            table.add_row(
                str(i),
                format_bytes(f["size"]),
                f["ext"],
                f["name"][:50],
            )
        console.print(table)
    else:
        typer.echo(f"\n📊 大文件 Top-{top_n}：")
        for i, f in enumerate(top_files, 1):
            typer.echo(f"  {i}. {format_bytes(f['size']):>10}  {f['name']}")


def _stats_pie_chart(
    ctx: typer.Context,
    target: Path,
    categories: dict,
    exclude: list[str],
    exclude_dirs: list[str],
):
    """显示文件类型分布 ASCII 饼图。"""
    # 用分类数据构建饼图
    data = {
        cat: len(files)
        for cat, files in sorted(categories.items())
        if files
    }

    if _is_json(ctx):
        summary = storage_summary(
            target,
            exclude=list(exclude) if exclude else None,
            exclude_dirs=list(exclude_dirs) if exclude_dirs else None,
        )
        typer.echo(format_json_output({
            "operation": "stats_pie",
            "path": str(target),
            "categories": data,
            "summary": summary,
        }))
        return

    if not data:
        typer.echo("ℹ️  没有找到文件。")
        return

    pie_output = render_pie_chart(data, title=f"📊 {target.name} 文件类型分布")
    typer.echo(pie_output)


def _make_bar(value: int, max_value: int, width: int = 20) -> str:
    """生成 ASCII 条形图。"""
    if max_value == 0:
        return ""
    bar_len = int(value / max_value * width)
    return "█" * bar_len


def fnmatch_match(name: str, pattern: str) -> bool:
    """封装 fnmatch 匹配。"""
    return fnmatch(name, pattern)


# ══════════════════════════════════════════════════════════════
#  内部辅助函数
# ══════════════════════════════════════════════════════════════


def _parse_size(size_str: str) -> int:
    """解析大小字符串为字节数。

    支持格式：100, 100KB, 1MB, 1.5GB
    """
    size_str = size_str.strip().upper()
    if not size_str:
        return 0

    if size_str.endswith("KB"):
        return int(float(size_str[:-2]) * 1024)
    elif size_str.endswith("MB"):
        return int(float(size_str[:-2]) * 1024 * 1024)
    elif size_str.endswith("GB"):
        return int(float(size_str[:-2]) * 1024 * 1024 * 1024)
    else:
        return int(float(size_str))


def get_size_display(size: int) -> str:
    """获取文件大小的显示字符串。"""
    return format_bytes(size)


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
            typer.echo(f"\n  📁 → {cat}/ ({len(files)} 个文件)")
            for f in files[:5]:
                typer.echo(f"      📄 {f.name}")
            if len(files) > 5:
                typer.echo(f"      ... 还有 {len(files) - 5} 个")


# ══════════════════════════════════════════════════════════════
#  子命令：tui（Textual 交互式 TUI）
# ══════════════════════════════════════════════════════════════


@app.command()
def tui(
    ctx: typer.Context,
    path: str = typer.Argument(
        ...,
        help="要整理的目录路径",
    ),
):
    """启动交互式 TUI 界面（Textual 终端应用）。需安装 dirsort[tui]。"""
    target = Path(path)
    if not target.exists() or not target.is_dir():
        typer.echo(f"❌ 错误：目录不存在或不可读: {path}")
        raise typer.Exit(1)

    _run_tui(target)


# ══════════════════════════════════════════════════════════════
#  子命令组：plugin（插件管理）
# ══════════════════════════════════════════════════════════════

plugin_app = typer.Typer(
    name="plugin",
    help="插件管理 — 列出、安装、创建和查看插件信息。",
    no_args_is_help=True,
)
app.add_typer(plugin_app, name="plugin")


@plugin_app.command("list")
def plugin_list(
    ctx: typer.Context,
):
    """列出已安装的插件。"""
    mgr = PluginManager()
    mgr.discover_and_load()
    plugins = mgr.list_plugins()

    if _is_json(ctx):
        typer.echo(format_json_output({
            "operation": "plugin_list",
            "plugins": [
                {
                    "name": p.name,
                    "version": p.version,
                    "description": p.description,
                }
                for p in plugins
            ],
            "count": len(plugins),
        }))
        return

    if not plugins:
        if HAS_RICH:
            Console().print("[yellow]📭 没有已安装的插件。[/]")
            Console().print(
                "[dim]使用 [bold]dirsort plugin create <name>[/] 创建新插件[/]"
            )
        else:
            typer.echo("📭 没有已安装的插件。")
            typer.echo("使用 'dirsort plugin create <name>' 创建新插件。")
        return

    if HAS_RICH:
        console = Console()
        table = Table(title="🔌 已安装插件", box=box.ROUNDED)
        table.add_column("名称", style="cyan")
        table.add_column("版本", style="green")
        table.add_column("描述", style="white")
        for p in plugins:
            table.add_row(p.name, p.version, p.description)
        console.print(table)
    else:
        typer.echo("🔌 已安装插件：")
        for p in plugins:
            typer.echo(f"  • {p.name} v{p.version} — {p.description}")


@plugin_app.command("install")
def plugin_install(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="插件 .py 文件路径"),
):
    """安装自定义 Python 插件。"""
    source = Path(path)
    mgr = PluginManager()

    try:
        plugin = mgr.install_plugin(source)
    except FileNotFoundError as e:
        typer.echo(f"❌ {e}")
        raise typer.Exit(1)
    except ValueError as e:
        typer.echo(f"❌ {e}")
        raise typer.Exit(1)

    if _is_json(ctx):
        typer.echo(format_json_output({
            "operation": "plugin_install",
            "status": "success",
            "plugin": {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
            },
        }))
        return

    if HAS_RICH:
        Console().print(f"[bold green]✅ 已安装插件:[/] {plugin.name} v{plugin.version}")
        Console().print(f"[dim]{plugin.description}[/]")
    else:
        typer.echo(f"✅ 已安装插件: {plugin.name} v{plugin.version}")
        typer.echo(plugin.description)


@plugin_app.command("create")
def plugin_create(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="插件名称（如 my-classifier）"),
    output: str = typer.Option(
        None, "--output", "-o", help="输出文件路径（默认: <name>.py）",
    ),
):
    """生成插件模板脚手架。"""
    mgr = PluginManager()
    template = mgr.create_plugin_template(name)

    out_path = Path(output) if output else Path(f"{name}.py")
    out_path.write_text(template, encoding="utf-8")

    if _is_json(ctx):
        typer.echo(format_json_output({
            "operation": "plugin_create",
            "name": name,
            "output": str(out_path),
            "status": "created",
        }))
        return

    if HAS_RICH:
        Console().print(f"[bold green]✅ 插件模板已创建:[/] {out_path}")
        Console().print("[dim]编辑此文件实现自定义分类逻辑，然后用 dirsort plugin install 安装。[/]")
    else:
        typer.echo(f"✅ 插件模板已创建: {out_path}")
        typer.echo("编辑此文件实现自定义分类逻辑，然后用 'dirsort plugin install' 安装。")


@plugin_app.command("info")
def plugin_info(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="插件名称"),
):
    """显示插件详情。"""
    mgr = PluginManager()
    mgr.discover_and_load()
    info = mgr.get_plugin_info(name)

    if info is None:
        typer.echo(f"❌ 未找到插件: {name}")
        raise typer.Exit(1)

    if _is_json(ctx):
        typer.echo(format_json_output({
            "operation": "plugin_info",
            "plugin": info,
        }))
        return

    if HAS_RICH:
        console = Console()
        console.print(f"[bold cyan]🔌 {info['name']}[/] v{info['version']}")
        console.print(f"  描述: {info['description']}")
        console.print(f"  classify hook: {'✅' if info['has_classify'] else '❌'}")
        console.print(f"  report hook: {'✅' if info['has_report'] else '❌'}")
    else:
        typer.echo(f"🔌 {info['name']} v{info['version']}")
        typer.echo(f"  描述: {info['description']}")
        typer.echo(f"  classify hook: {'有' if info['has_classify'] else '无'}")
        typer.echo(f"  report hook: {'有' if info['has_report'] else '无'}")


@plugin_app.command("reload")
def plugin_reload(
    ctx: typer.Context,
):
    """重新加载所有插件（热重载）。"""
    mgr = PluginManager()
    count = mgr.reload()

    if _is_json(ctx):
        typer.echo(format_json_output({
            "operation": "plugin_reload",
            "reloaded": count,
        }))
        return

    if HAS_RICH:
        Console().print(f"[bold green]🔄 已重新加载 {count} 个插件。[/]")
    else:
        typer.echo(f"🔄 已重新加载 {count} 个插件。")
