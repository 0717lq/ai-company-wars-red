# 文件功能说明

## src/dirsort/__init__.py
dirsort 包定义。导出 `__version__ = "0.2.0"`。
包描述：智能文件目录整理 CLI 工具。支持 YAML 配置规则、富文本输出、安全 Dry-run 模式。

## src/dirsort/__main__.py
`python -m dirsort` 入口。调用 `cli.app()` 启动命令行。

## src/dirsort/cli.py
**Typer CLI 定义 — 命令行入口（Round 2 增强版）**

核心入口函数和所有子命令定义：

- `entry()` — CLI 入口包装器，使 `dirsort <path>` 等价于 `dirsort sort <path>`
- `sort()` — 整理子命令。接收 path、--execute、--dry-run、--by-date、--stats、--exclude、--exclude-dir、--config 等参数
- `undo()` — 回滚子命令。支持 --verbose 显示详细文件列表（Rich 表格）
- `history()` — 查看整理历史（Rich 表格展示）
- `_show_stats()` — 统计展示函数（支持 Rich 表格降级）
- `_print_plan()` — 整理计划展示函数（支持 Rich 表格降级）

**新增功能（Round 2）：** 默认 dry-run、--execute 标志、--exclude/--exclude-dir 排除、Rich 美化输出、--config 配置加载、undo --verbose、history Rich 表格、错误处理

## src/dirsort/sorter.py
**核心排序逻辑 — 扫描目录并按规则分类文件。**

- `analyze()` — 扫描目录，将文件按规则分类。支持 exclude/exclude_dirs/rules 参数
- `organize()` — 执行文件移动操作。返回 [(原路径, 新路径)] 列表
- `_matches_any()` — 检查文件名是否匹配任意一个 glob 模式
- `_date_category()` — 根据文件修改时间返回月份分类名
- `_resolve_conflict()` — 处理文件名冲突，自动添加编号后缀

**新增功能（Round 2）：** exclude 过滤、exclude-dir 过滤、自定义规则支持（rules 参数）、PermissionError/OSError 错误处理

## src/dirsort/rules.py
**文件分类规则配置 — 后缀映射到类别。**

- `DEFAULT_RULES` — 默认分类规则字典（90+ 文件后缀，10+ 类别）
- `classify()` — 根据文件名和规则返回分类名称
- `get_all_categories()` — 获取所有分类名称列表（去重）

## src/dirsort/config.py
**[新建] 配置文件系统 — 加载 YAML 格式的自定义分类规则。**

- `load_config()` — 加载 YAML 配置文件，返回自定义分类规则字典
- `get_merged_rules()` — 获取合并后的分类规则（自定义规则优先，默认规则 fallback）

从 `--config rules.yaml` 加载，自动检测 `~/.config/dirsort/rules.yaml`。无效配置静默降级。

## src/dirsort/undo.py
**回滚功能 — 记录整理操作用于撤销。**

- `UndoManager` — 管理整理操作的撤销和记录
  - `record()` — 记录一次整理操作（最多 20 条）
  - `rollback()` — 回滚整理操作（按目录或最近一次）
  - `list_history()` — 列出所有整理历史

## src/dirsort/utils.py
**文件操作工具函数。**

- `get_size_str()` — 获取文件可读大小字符串
- `count_files()` — 统计目录中的文件数量（非递归）
- `get_disk_usage()` — 获取目录占用磁盘空间（字节）
