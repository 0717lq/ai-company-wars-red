"""dirsort TUI 应用 — 基于 Textual 的交互式终端界面。

使用方式：`dirsort tui <PATH>`
提供目录树浏览、整理预览、统计面板、规则管理等交互功能。

Textual 是可选依赖，未安装时降级为提示信息。
"""

from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING

# ── Textual 降级兼容 ──
try:
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.widgets import Header, Footer, Static, RichLog, TabbedContent, TabPane

    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False

from .sorter import analyze, organize
from .undo import UndoManager
from .config import get_merged_rules


# ══════════════════════════════════════════════════════════════
#  外部入口
# ══════════════════════════════════════════════════════════════


def run_tui(path: Path) -> None:
    """启动 dirsort TUI 应用（外部入口）。"""
    if not HAS_TEXTUAL:
        from rich.console import Console as RichConsole
        RichConsole().print(
            "[yellow]⚠️ Textual 未安装，请执行以下命令安装 TUI 依赖:[/]\n"
            "  pip install dirsort[tui]\n"
            "  # 或\n"
            "  pip install textual>=0.52"
        )
        return
    app = DirsortTUI(path)
    app.run()


# ══════════════════════════════════════════════════════════════
#  TUI 主应用（仅在 HAVE_TEXTUAL=True 时可用）
# ══════════════════════════════════════════════════════════════

if HAS_TEXTUAL:

    class DirsortTUI(App):
        """dirsort 交互式 TUI 主应用。

        快捷键：
            d — 执行 Dry-run 预览（默认）
            e — 执行整理
            q — 退出
            r — 切换到规则面板
            s — 切换到统计面板
            b — 切换到浏览面板
            p — 切换到预览面板
        """

        TITLE = "dirsort 文件整理工具"
        SUB_TITLE = "交互式文件整理 — 默认 dry-run，e 键执行"

        BINDINGS = [
            Binding("d", "action_dry_run", "Dry-run 预览"),
            Binding("e", "action_execute", "执行整理"),
            Binding("q", "action_quit", "退出"),
            Binding("r", "switch_tab('rules')", "规则"),
            Binding("s", "switch_tab('stats')", "统计"),
            Binding("b", "switch_tab('browse')", "浏览"),
            Binding("p", "switch_tab('preview')", "预览"),
        ]

        def __init__(self, target_path: Path) -> None:
            super().__init__()
            self.target_path = target_path
            self.categories: dict[str, list[Path]] = {}
            self.total_files = 0
            self._moves: list[tuple[Path, Path]] = []
            self._executed = False

        def compose(self) -> ComposeResult:
            """构建 TUI 布局。"""
            yield Header(show_clock=True)
            with TabbedContent(initial="browse"):
                with TabPane("📂 文件浏览", id="browse"):
                    yield Static("加载中…", id="browse-content")
                with TabPane("📋 整理预览", id="preview"):
                    yield RichLog(id="preview-content", highlight=True, markup=True)
                with TabPane("📊 统计面板", id="stats"):
                    yield Static("加载中…", id="stats-content")
                with TabPane("⚙️ 规则管理", id="rules"):
                    yield RichLog(id="rules-content", highlight=True, markup=True)
            yield Footer()

        def on_mount(self) -> None:
            """应用挂载时执行扫描。"""
            self.title = f"dirsort — {self.target_path}"
            self.call_from_thread(self.refresh_all)

        def refresh_all(self) -> None:
            """刷新所有面板数据。"""
            try:
                rules = get_merged_rules()
                self.categories = analyze(
                    self.target_path,
                    by_date=False,
                    exclude=None,
                    exclude_dirs=None,
                    rules=rules,
                )
                self.total_files = sum(len(files) for files in self.categories.values())
            except (PermissionError, OSError) as e:
                self._update_browse_panel(f"[red]❌ 无法读取目录: {e}[/]")
                self._update_preview_panel(f"[red]❌ 无法读取目录: {e}[/]")
                return

            self._update_browse_panel()
            self._update_preview_panel()
            self._update_stats_panel()
            self._update_rules_panel()

        def _update_browse_panel(self, error_msg: str | None = None) -> None:
            """更新文件浏览面板。"""
            if error_msg:
                self.query_one("#browse-content", Static).update(error_msg)
                return
            lines = [f"[bold blue]📂 目录: {self.target_path}[/]\n"]
            if not self.categories:
                lines.append("[dim]（空目录或所有文件已被排除）[/]")
            else:
                for cat_name, files in sorted(self.categories.items()):
                    if not files:
                        continue
                    lines.append(f"\n[bold]{cat_name}[/] ({len(files)} 个文件):")
                    for f in files[:20]:
                        size = f.stat().st_size if f.exists() else 0
                        size_str = _format_size(size)
                        lines.append(f"  📄 {f.name} [dim]{size_str}[/]")
                    if len(files) > 20:
                        lines.append(f"  [dim]…以及 {len(files) - 20} 个更多文件[/]")
            self.query_one("#browse-content", Static).update("\n".join(lines))

        def _update_preview_panel(self, error_msg: str | None = None) -> None:
            """更新整理预览面板。"""
            preview = self.query_one("#preview-content", RichLog)
            preview.clear()
            if error_msg:
                preview.write(error_msg)
                return
            if self._executed:
                preview.write("[bold green]✅ 已执行整理！[/]")
                preview.write(f"[dim]移动了 {len(self._moves)} 个文件 — 可用 [bold]dirsort undo[/] 回滚[/]")
                return

            if not self.categories:
                preview.write("[bold green]✨ 目录已经很整洁了，无需整理！[/]")
                return

            preview.write(f"[bold]📋 整理计划 — {self.target_path}[/]\n")
            for cat_name, files in sorted(self.categories.items()):
                if not files:
                    continue
                preview.write(f"\n[bold underline]{cat_name}[/] — {len(files)} 个文件")
                for f in files[:10]:
                    preview.write(f"  📄 {f.name} → [green]{cat_name}/[/]")
                if len(files) > 10:
                    preview.write(f"  [dim]…以及 {len(files) - 10} 个文件[/]")

            preview.write(f"\n[bold yellow]⏸️  Dry-run 模式[/] — 总计 {self.total_files} 个文件待整理")
            preview.write("[dim]按 [bold]e[/] 键执行整理，按 [bold]d[/] 键刷新预览[/]")

        def _update_stats_panel(self) -> None:
            """更新统计面板。"""
            lines = [f"[bold]📊 统计报表 — {self.target_path}[/]\n"]
            if not self.categories:
                lines.append("[dim]无文件数据[/]")
            else:
                lines.append(f"文件总数: [bold]{self.total_files}[/]\n")
                for cat_name, files in sorted(self.categories.items()):
                    if not files:
                        continue
                    total_size = sum(f.stat().st_size for f in files if f.exists())
                    pct = self.total_files and (len(files) / self.total_files * 100) or 0
                    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
                    lines.append(
                        f"{bar}  [bold]{cat_name}[/]  {len(files):>4} 个  "
                        f"{_format_size(total_size):>8}  ({pct:.0f}%)"
                    )
            self.query_one("#stats-content", Static).update("\n".join(lines))

        def _update_rules_panel(self) -> None:
            """更新规则管理面板。"""
            rules_panel = self.query_one("#rules-content", RichLog)
            rules_panel.clear()
            rules_panel.write("[bold]⚙️  文件分类规则[/]\n")
            rules = get_merged_rules()
            if rules:
                cat_rules: dict[str, list[str]] = {}
                for ext, cat in rules.items():
                    if cat not in cat_rules:
                        cat_rules[cat] = []
                    cat_rules[cat].append(ext)
                for cat, exts in sorted(cat_rules.items()):
                    rules_panel.write(f"\n[bold underline]{cat}[/]")
                    chunks = [exts[i:i+6] for i in range(0, len(exts), 6)]
                    for chunk in chunks:
                        rules_panel.write(f"  [dim]{', '.join(chunk)}[/]")
            rules_panel.write("\n[dim]💡 规则存储在 ~/.config/dirsort/rules.yaml[/]")
            rules_panel.write("[dim]使用 [bold]dirsort config[/] 查看完整配置[/]")

        # ── 动作 ────────────────────────────────────────────────

        def action_dry_run(self) -> None:
            """执行 Dry-run 预览（刷新数据）。"""
            self.refresh_all()
            self._update_preview_panel()
            self.notify("🔄 已刷新 Dry-run 预览", severity="information", timeout=3)

        def action_execute(self) -> None:
            """执行文件整理。"""
            if not self.categories or self.total_files == 0:
                self.notify("✨ 没有文件需要整理", severity="warning", timeout=3)
                return
            if self._executed:
                self.notify("✅ 已经整理过了！使用 `dirsort undo` 回滚", severity="warning", timeout=3)
                return

            self._moves = organize(self.target_path, self.categories, by_date=False)
            undo_mgr = UndoManager()
            undo_mgr.record(self.target_path, self._moves, operation_type="sort")
            self._executed = True

            self._update_preview_panel()
            self.notify(
                f"✅ 整理完成！移动了 {len(self._moves)} 个文件",
                severity="information",
                timeout=5,
            )

        def action_switch_tab(self, tab_id: str) -> None:
            """切换到指定标签页。"""
            tabs = self.query_one(TabbedContent)
            tabs.active = tab_id

        def action_action_quit(self) -> None:
            """退出应用。"""
            self.exit()


# ── 工具函数 ────────────────────────────────────────────────


def _format_size(size_bytes: int) -> str:
    """格式化文件大小为可读字符串。"""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / 1024 / 1024:.1f}MB"
    else:
        return f"{size_bytes / 1024 / 1024 / 1024:.1f}GB"
