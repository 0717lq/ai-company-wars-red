# dirsort 核心代码说明

## cli.py — CLI 入口与子命令

| 函数/类 | 作用 |
|---------|------|
| `make_app()` | 创建 Typer 应用实例，配置 help 选项和自动补全 |
| `entry()` | CLI 入口包装器 — 将 `dirsort <path>` 转为 `dirsort sort <path>` |
| `main()` | Typer callback — 全局 `--json` 选项 |
| `sort()` | **文件整理命令** — 按类型/日期分类，默认 dry-run |
| `tui()` | **交互式 TUI 命令** — 启动 Textual 终端界面 |
| `undo()` | 回滚操作 |
| `history()` | 查看操作历史 |
| `init()` | 创建默认配置 |
| `config()` | 查看配置内容 |
| `dupes()` | 重复文件检测 |
| `rename()` | 批量重命名 |
| `stats()` | 统计信息 |
| `_print_plan()` | Rich 表格整理计划 |
| `_sort_stats()` | 分类统计显示 |
| `_sort_stats_by_type()` | 按扩展名分组统计 |
| `_parse_size()` | 大小字符串解析（1MB → 1048576） |

## sorter.py — 核心排序引擎

| 函数 | 作用 |
|------|------|
| `analyze()` | 扫描目录，按规则或日期分类文件，支持排除模式和自定义规则 |
| `organize()` | 执行文件移动，创建目标目录，处理冲突 |
| `_date_category()` | 根据修改时间返回月份分类名 |
| `_resolve_conflict()` | 文件名冲突时自动编号（`file_1.txt`, `file_2.txt`） |
| `_matches_any()` | glob 模式匹配检查 |

## rules.py — 文件分类规则

| 函数/常量 | 作用 |
|-----------|------|
| `DEFAULT_RULES` | 90+ 文件后缀 → 9 个分类（图片/文档/视频/音频/代码/压缩包/程序/设计文件/字体） |
| `classify()` | 根据文件后缀返回分类名 |
| `get_all_categories()` | 获取所有分类名称列表 |

## config.py — YAML 配置系统

| 函数 | 作用 |
|------|------|
| `load_config()` | 加载 `~/.config/dirsort/rules.yaml`，解析 YAML |
| `get_merged_rules()` | 合并 DEFAULT_RULES + 配置文件规则（配置文件优先级更高） |
| `create_default_config()` | 创建默认配置文件 |
| `config_content()` | 读取配置文件内容 |
| `save_config()` | 保存配置到文件 |

## dupes.py — 重复文件检测

| 函数/类 | 作用 |
|---------|------|
| `DuplicateGroup` | 重复文件分组（相同 MD5 哈希） |
| `find_duplicates()` | 两遍扫描：先按大小分组，再对同大小文件计算 MD5 |
| `delete_duplicates()` | 删除重复文件（保留每组第一个） |

## rename.py — 批量重命名

| 函数 | 作用 |
|------|------|
| `build_rename_plan()` | 解析模板，构建重命名映射（冲突处理） |
| `execute_rename()` | 执行重命名，调用 UndoManager 记录 |

## tui_app.py — Textual TUI 应用

| 函数/类 | 作用 |
|---------|------|
| `run_tui()` | TUI 外部入口，Textual 未安装时降级提示 |
| `DirsortTUI` | Textual App 主类，4 面板 TabbedContent |
| `_update_browse_panel()` | 📂 文件浏览面板 |
| `_update_preview_panel()` | 📋 整理预览面板 |
| `_update_stats_panel()` | 📊 统计面板（条形图） |
| `_update_rules_panel()` | ⚙️ 规则管理面板 |
| `action_dry_run()` | 快捷键 d — 刷新 dry-run 预览 |
| `action_execute()` | 快捷键 e — 执行整理 |
| `_format_size()` | 文件大小格式化 |

## undo.py — Undo 回滚管理器

| 函数/类 | 作用 |
|---------|------|
| `UndoManager` | 历史记录管理器（JSON 文件 `~/.dirsort/history.json`） |
| `record()` | 记录操作（支持 sort/rename/dupes_delete 类型） |
| `list_history()` | 列出操作历史 |
| `rollback()` | 回滚指定或最晚操作 |
