# dirsort — 项目目录结构

```
project/
├── pyproject.toml               # 项目配置、依赖、CLI 入口
├── README.md                    # 项目说明
├── LICENSE                      # MIT 许可证
├── .gitignore
├── .github/workflows/ci.yml     # CI 配置
├── docs/
│   ├── STRUCTURE.md             # 本文件 — 目录结构说明
│   ├── FILES.md                 # 文件功能说明
│   └── CODE.md                  # 核心代码说明
├── src/
│   └── dirsort/
│       ├── __init__.py          # 包初始化，版本号
│       ├── __main__.py          # python -m 入口
│       ├── cli.py               # Typer CLI 定义
│       ├── rules.py             # 文件分类规则
│       ├── sorter.py            # 核心排序逻辑
│       ├── undo.py              # 回滚功能
│       └── utils.py             # 文件操作工具
└── tests/
    ├── __init__.py
    ├── test_cli.py              # CLI 命令测试
    ├── test_sorter.py           # 排序逻辑测试
    ├── test_sorter_extra.py     # 排序逻辑补充测试
    ├── test_undo.py             # 回滚功能测试
    ├── test_undo_extra.py       # 回滚补充测试
    ├── test_utils.py            # 工具函数测试
    └── test_trial_verify.py     # 试跑验证测试
```
