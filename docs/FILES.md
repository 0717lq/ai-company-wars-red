# dirsort — 文件功能说明

## `src/dirsort/__init__.py`
- 包初始化
- 版本号 `__version__ = "0.1.0"`
- 简短项目描述 docstring

## `src/dirsort/__main__.py`
- `python -m dirsort` 入口
- 委托给 `cli.app()`

## `src/dirsort/cli.py`
- **核心**: Typer CLI 定义
- `app()` — 主应用，注册"sort"、"undo"、"history"等子命令
- `entry()` — 入口包装器，使 `dirsort <path>` 等价于 `dirsort sort <path>`
- `sort()` — 整理命令（按类型/按日期/dry-run/stats）
- `undo()` — 回滚命令
- `history()` — 查看整理历史

## `src/dirsort/rules.py`
- 文件类别定义和分类规则
- `DEFAULT_RULES` — 文件后缀到类别名的映射（图片/文档/视频/音频/代码/压缩包等10+类别）
- `classify(suffix: str) -> str` — 根据后缀返回类别名
- `get_all_categories() -> list[str]` — 返回所有类别名列表

## `src/dirsort/sorter.py`
- **核心**: 扫描目录并执行整理操作
- `analyze(path: Path, by_date: bool) -> dict[str, list[Path]]` — 扫描统计
- `organize(path: Path, by_date: bool, dry_run: bool) -> None` — 执行分类整理
- 文件冲突自动重命名（编号后缀）
- 隐藏文件保护

## `src/dirsort/undo.py`
- **撤销机制**
- `UndoManager` 类 — 记录和回滚整理操作
- `record_sort(origin_dir, records)` — 记录历史
- `undo(snapshot_id)` — 撤销指定操作
- `get_history()` — 获取历史列表

## `src/dirsort/utils.py`
- 工具函数
- `get_size_str(path: Path) -> str` — 文件大小可读化
