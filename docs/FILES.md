# dirsort 文件功能说明

## 源代码（src/dirsort/）

| 文件 | 功能 |
|------|------|
| `__init__.py` | 包初始化，空文件 |
| `__main__.py` | `python -m dirsort` 入口 |
| `cli.py` | **主 CLI 入口** — 9 个子命令（sort/undo/history/init/config/dupes/rename/stats/tui），全局 `--json` 输出，Rich 降级兼容 |
| `config.py` | **YAML 配置系统** — `load_config()` 加载配置、`get_merged_rules()` 合并默认+配置规则、`create_default_config()` 创建默认配置、`config_content()` 读取配置内容 |
| `dupes.py` | **重复检测引擎** — 两遍扫描优化（先按大小分组，再对同大小文件计算 MD5），支持 `find_duplicates()` 和 `delete_duplicates()` |
| `rename.py` | **批量重命名引擎** — `build_rename_plan()` 构建重命名计划，`execute_rename()` 执行，支持 `%04d` 序号模板和 `{ext}` 变量，含冲突处理 |
| `rules.py` | **文件分类规则** — 90+ 文件后缀映射到 9 个分类，`classify()` 分类函数，`get_all_categories()` 获取所有分类 |
| `sorter.py` | **核心排序逻辑** — `analyze()` 扫描目录分类文件（支持排除/日期/自定义规则），`organize()` 执行移动操作，`_resolve_conflict()` 冲突处理 |
| `tui_app.py` | **Textual TUI 应用** — `DirsortTUI` 类（4 面板：浏览/预览/统计/规则），快捷键系统，`run_tui()` 外部入口 |
| `tui_screens/__init__.py` | TUI 屏幕包初始化 |
| `undo.py` | **Undo 回滚管理器** — `UndoManager` 类管理历史记录（JSON 文件持久化），支持 `record()`/`list_history()`/`rollback()`，区分 sort/rename/dupes_delete 操作 |
| `utils.py` | **工具函数** — `format_json_output()` 统一 JSON 输出、`format_bytes()` 字节格式化、`count_files()` 文件计数 |

## 测试（tests/）

| 文件 | 功能 |
|------|------|
| `test_cli.py` | CLI 集成测试 — 所有子命令入口、参数解析、Rich 降级、JSON 输出 |
| `test_config.py` | 配置系统测试 — YAML 加载、规则合并、默认配置创建 |
| `test_dupes.py` | 重复检测测试 — MD5 哈希、同大小分组、删除操作、边界条件 |
| `test_rename.py` | 批量重命名测试 — 计划构建、执行、冲突处理、序列化 |
| `test_sorter.py` | 排序基础测试 — 分类、日期模式、排除、冲突处理 |
| `test_sorter_extra.py` | 排序扩展测试 — 配置规则合并、排除模式 |
| `test_tui.py` | TUI 测试 — CLI 入口、格式化函数、应用属性 |
| `test_undo.py` | Undo 基础测试 — 记录、列表、回滚 |
| `test_undo_extra.py` | Undo 扩展测试 — 边界条件、损坏处理 |
| `test_utils.py` | 工具函数测试 |

## 基础设施

| 文件 | 功能 |
|------|------|
| `pyproject.toml` | 项目配置 — 版本 v0.4.0，依赖管理（typer/rich/pyyaml/textual），完整 classifiers |
| `Dockerfile` | Docker 镜像构建 — python:3.11-slim，多阶段构建 |
| `.dockerignore` | Docker 构建排除 |
| `.pre-commit-hooks.yaml` | Pre-commit hook — 提交前自动检查文件整理状态 |
| `.claude/skills/dirsort.md` | AI Agent Skill — Claude Code/Codex 开箱即用 |
| `README.md` | 项目说明 |
