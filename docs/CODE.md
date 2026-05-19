# 核心代码清单 — dirsort v0.3.0

## cli.py — 命令行入口

| 函数/命令 | 说明 |
|-----------|------|
| `entry()` | CLI 入口包装器，使 `dirsort <path>` 等价于 `dirsort sort <path>` |
| `sort()` | 按类型/日期整理目录文件，默认 dry-run |
| `undo()` | 回滚上次整理/重命名操作 |
| `history()` | 查看操作历史记录 |
| `init()` | 创建默认配置文件 `~/.config/dirsort/rules.yaml` |
| `config()` | 查看当前配置文件内容 |
| `dupes()` | 检测重复文件（MD5 哈希，分块读取）|
| `rename()` | 批量重命名文件（glob 模式 + 序号模板）|
| `stats()` | 统计目录文件信息（支持 --by-type, --chart）|

## sorter.py — 排序逻辑

| 函数 | 说明 |
|------|------|
| `analyze()` | 扫描目录，按规则分类文件 |
| `organize()` | 执行文件移动操作 |
| `_resolve_conflict()` | 处理文件名冲突（编号后缀）|
| `_date_category()` | 按修改时间返回月份分类 |

## rules.py — 分类规则

| 函数 | 说明 |
|------|------|
| `classify()` | 根据后缀返回分类名称 |
| `get_all_categories()` | 获取所有分类名称列表 |

## config.py — 配置系统

| 函数 | 说明 |
|------|------|
| `create_default_config()` | 创建默认 YAML 配置文件 |
| `load_config()` | 加载 YAML 配置文件 |
| `get_merged_rules()` | 合并自定义 + 默认规则 |
| `config_content()` | 读取配置文件内容 |

## dupes.py — 重复检测

| 函数/类 | 说明 |
|---------|------|
| `find_duplicates()` | 两遍扫描：先按大小分组，再 MD5 哈希 |
| `delete_duplicates()` | 删除重复文件（保留每组第一个）|
| `DuplicateGroup` | 重复文件组，包含哈希值和文件列表 |
| `_md5_file()` | 分块计算文件 MD5（64KB/块）|

## rename.py — 批量重命名

| 函数/类 | 说明 |
|---------|------|
| `build_rename_plan()` | 构建重命名计划 |
| `execute_rename()` | 执行重命名操作 |
| `RenameEntry` | 重命名条目（原路径/新路径）|

## undo.py — 撤销系统

| 函数/类 | 说明 |
|---------|------|
| `UndoManager.record()` | 记录操作（支持 operation_type）|
| `UndoManager.rollback()` | 回滚操作 |
| `UndoManager.list_history()` | 列出操作历史 |

## utils.py — 工具函数

| 函数 | 说明 |
|------|------|
| `get_size_str()` | 获取文件可读大小 |
| `format_bytes()` | 字节数格式化 |
| `format_json_output()` | JSON 序列化（中文不转义）|
