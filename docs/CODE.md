# dirsort — 核心代码说明

## `cli.py`

| 函数 | 作用 |
|------|------|
| `entry()` | CLI 入口包装器，自动将 `dirsort <path>` 转为 `dirsort sort <path>`，同时保留 undo/history 等子命令 |
| `sort()` | 整理命令：按类型（默认）或按月份（`--by-date`）整理文件，支持 `--dry-run` 预览和 `--stats` 统计 |
| `undo()` | 回滚最近一次整理操作，将文件移回原位 |
| `history()` | 显示所有历史整理记录（时间、目录、文件数） |

## `rules.py`

| 函数/变量 | 作用 |
|-----------|------|
| `DEFAULT_RULES` | 字典类型，定义文件后缀到中文类别名的映射，覆盖10+类别 |
| `classify()` | 根据后缀返回对应类别名，未识别的归为"其他" |
| `get_all_categories()` | 返回所有唯一类别名列表 |

## `sorter.py`

| 函数 | 作用 |
|------|------|
| `analyze()` | 递归扫描目录，返回以类别名为 key、Path 列表为 value 的字典 |
| `organize()` | 执行文件整理：创建类别目录 → 移动文件 → 冲突时自动重命名（_1/_2后缀）→ 记录快照用于回滚 |

## `undo.py`

| 类/函数 | 作用 |
|---------|------|
| `UndoManager` | 管理整理历史：记录到 `~/.dirsort/history.json`，支持按 ID 回滚 |
| `record_sort()` | 记录一次整理操作的所有文件移动记录 |
| `undo()` | 按快照 ID 回滚，将文件移回原始位置 |
| `get_history()` | 列出所有整理历史记录 |
