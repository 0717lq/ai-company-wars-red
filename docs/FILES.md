# dirsort v0.6.0 — 文件功能说明

## src/dirsort/

| 文件 | 功能 |
|------|------|
| `__init__.py` | 包初始化，定义版本号 `0.6.0` |
| `__main__.py` | `python -m dirsort` 入口 |
| `cli.py` | Typer CLI 定义（10+ 子命令：sort/undo/history/init/config/dupes/rename/stats/tui/plugin） |
| `config.py` | YAML 配置文件加载和合并 |
| `dupes.py` | 重复文件检测（MD5 哈希，两遍扫描优化） |
| `plugin_base.py` | **NEW** 插件抽象基类 PluginBase（classify + generate_report hooks） |
| `plugin_system.py` | **NEW** 插件加载/注册/执行引擎（importlib 动态导入，安全隔离） |
| `rename.py` | 批量重命名（glob 匹配 + 序号模板 + 冲突处理） |
| `rules.py` | 内置分类规则定义 |
| `sorter.py` | 核心分类逻辑（analyze + organize） |
| `stats_enhanced.py` | **NEW** 增强统计（ASCII 饼图/柱状图 + 大文件 Top-N + 存储分析） |
| `tui_app.py` | Textual TUI 交互式界面 |
| `tui_screens/` | TUI 屏幕组件包 |
| `undo.py` | 操作回滚管理器 |
| `utils.py` | 工具函数（format_bytes, format_json_output） |

## tests/

| 文件 | 测试数 | 覆盖 |
|------|--------|------|
| `test_cli.py` | ~30 | CLI 命令集成测试 |
| `test_config.py` | ~9 | 配置文件加载 |
| `test_dupes.py` | ~18 | 重复文件检测 |
| `test_rename.py` | ~12 | 批量重命名 |
| `test_plugin_system.py` | ~30 | **NEW** 插件系统（base + manager + hooks + CLI） |
| `test_stats_enhanced.py` | ~28 | **NEW** 增强统计（charts + top files + CLI） |
| `test_tui.py` | ~11 | TUI 测试 |
| `test_sorter.py` | ~15 | 核心分类 |
| `test_sorter_extra.py` | ~15 | 排除/配置规则 |
| `test_undo.py` | ~4 | 基础回滚 |
| `test_undo_extra.py` | ~5 | 边界情况 |
| `test_utils.py` | ~8 | 工具函数 |
| `test_trial_verify.py` | 2 | 试跑验证 |
| **总计** | **207** | **全部通过** |

## plugins/

| 文件 | 说明 |
|------|------|
| `example_classifier.py` | 示例插件 — 按文件大小分类（小/中/大文件） |
