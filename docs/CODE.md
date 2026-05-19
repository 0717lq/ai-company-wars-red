# 核心代码说明

## cli.py — 命令行入口

| 函数/类 | 作用 |
|---------|------|
| `entry()` | 入口包装器：`dirsort <path>` → `dirsort sort <path>` |
| `sort()` | 整理子命令：参数解析 + 调用 sorter + 展示结果 |
| `undo()` | 回滚子命令：调用 UndoManager + Rich 表格详情 |
| `history()` | 历史查看：Rich 表格展示历史记录 |
| `_show_stats()` | 统计输出（Rich 降级兼容） |
| `_print_plan()` | 整理计划输出（Rich 降级兼容） |

## sorter.py — 核心排序逻辑

| 函数/类 | 作用 |
|---------|------|
| `analyze()` | 扫描目录 + 分类（支持 exclude/exclude_dirs/custom_rules） |
| `organize()` | 执行文件移动 + 冲突处理 + 错误跳过 |
| `_matches_any()` | fnmatch 模式匹配辅助函数 |
| `_date_category()` | 文件 mtime → "YYYY-MM" 分类名 |
| `_resolve_conflict()` | 文件冲突自动编号重命名 |

## rules.py — 文件分类规则

| 函数/类 | 作用 |
|---------|------|
| `DEFAULT_RULES` | 默认分类规则（90+ 后缀 → 10+ 类别） |
| `classify()` | 根据后缀规则分类（支持自定义 rules 参数） |
| `get_all_categories()` | 获取所有分类名（去重 + "其他"） |

## config.py — 配置文件系统（新增）

| 函数/类 | 作用 |
|---------|------|
| `load_config()` | 加载 YAML 配置（自动检测/显式路径） |
| `get_merged_rules()` | 合并自定义规则 + 默认规则（自定义优先） |

## undo.py — 回滚管理

| 函数/类 | 作用 |
|---------|------|
| `UndoManager` | 回滚管理器类 |
| `UndoManager.record()` | 记录整理操作（最多 20 条） |
| `UndoManager.rollback()` | 回滚（按目录/最近一次） |
| `UndoManager.list_history()` | 列出历史记录 |

## utils.py — 工具函数

| 函数/类 | 作用 |
|---------|------|
| `get_size_str()` | 文件大小可读化（B/KB/MB/GB） |
| `count_files()` | 目录文件计数（非递归） |
| `get_disk_usage()` | 目录磁盘占用统计 |
