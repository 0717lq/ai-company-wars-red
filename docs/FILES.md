# 文件功能说明 — dirsort v0.3.0

## src/dirsort/ 源代码文件

| 文件 | 功能 |
|------|------|
| `__init__.py` | 包初始化，版本号 |
| `__main__.py` | `python -m dirsort` 入口 |
| `cli.py` | Typer CLI 主入口，定义所有子命令（sort/undo/history/init/config/dupes/rename/stats）|
| `sorter.py` | 核心排序逻辑：扫描目录、分类文件、执行移动 |
| `rules.py` | 文件分类规则：后缀映射到类别（内置 100+ 后缀规则）|
| `config.py` | 配置文件系统：YAML 加载、合并规则、创建默认配置 |
| `undo.py` | 回滚功能：记录操作历史、撤销移动/重命名 |
| `dupes.py` | 重复文件检测：MD5 哈希分块读取，按大小分组优化 |
| `rename.py` | 批量重命名：glob 模式匹配、序号模板、冲突处理 |
| `utils.py` | 工具函数：大小格式化、JSON 序列化 |

## tests/ 测试文件

| 文件 | 功能 |
|------|------|
| `test_cli.py` | CLI 命令测试（sort/undo/history/init/config/dupes/rename --json 等）|
| `test_config.py` | 配置文件加载与合并测试 |
| `test_sorter.py` | 排序核心逻辑与规则测试 |
| `test_sorter_extra.py` | 扩展排序测试（组织/排除/配置规则）|
| `test_dupes.py` | 重复文件检测模块测试（18 项）|
| `test_rename.py` | 批量重命名模块测试（12 项）|
| `test_undo.py` | 撤销功能测试 |
| `test_undo_extra.py` | 撤销边界情况测试 |
| `test_utils.py` | 工具函数测试 |
| `test_trial_verify.py` | 试跑验证测试 |

## docs/ 文档目录

| 文件 | 功能 |
|------|------|
| `STRUCTURE.md` | 项目目录结构 |
| `FILES.md` | 文件功能说明 |
| `CODE.md` | 核心代码清单 |
