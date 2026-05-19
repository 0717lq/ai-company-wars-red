# dirsort 项目结构

```
teams/red/project/
├── pyproject.toml           # 项目配置，版本 0.2.0
├── README.md                # 项目文档（中文 + 英文）
├── src/
│   └── dirsort/
│       ├── __init__.py      # 包定义，__version__ = "0.2.0"
│       ├── __main__.py      # python -m dirsort 入口
│       ├── cli.py           # Typer CLI 定义（所有子命令入口）
│       ├── sorter.py        # 核心文件扫描、分类、移动逻辑
│       ├── rules.py         # 默认文件分类规则（后缀 → 分类名）
│       ├── config.py        # [新] YAML 配置文件加载与合并逻辑
│       ├── undo.py          # 整理操作回滚管理
│       └── utils.py         # 文件操作工具函数
├── tests/
│   ├── __init__.py
│   ├── test_cli.py          # CLI 命令测试（12 个，含 Round 2 新功能）
│   ├── test_sorter.py       # 分类规则和核心排序逻辑测试（8 个）
│   ├── test_sorter_extra.py # 深入测试：organize、冲突处理、排除、配置规则（21 个）
│   ├── test_undo.py         # UndoManager 基础测试（4 个）
│   ├── test_undo_extra.py   # UndoManager 边缘情况测试（5 个）
│   ├── test_utils.py        # 工具函数测试（5 个）
│   ├── test_config.py       # [新] 配置文件系统测试（9 个）
│   └── test_trial_verify.py # 试跑验证测试（2 个）
├── docs/
│   ├── STRUCTURE.md         # 本文件 — 项目结构
│   ├── FILES.md             # 文件功能说明
│   └── CODE.md              # 核心代码说明
└── .venv/                   # Python 虚拟环境（不提交 Git）
```

## 统计数据

- **源文件**: 7 个 Python 模块（src/dirsort/）
- **测试文件**: 8 个测试模块（tests/）
- **测试数量**: 77 个测试，全部通过
- **代码覆盖率**: 82%+
- **总代码行数**: ~1500 行
