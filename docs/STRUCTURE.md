# dirsort 项目结构

```
project/
├── pyproject.toml                    # 项目配置（v0.4.0, 依赖管理）
├── Dockerfile                        # Docker 镜像构建
├── .dockerignore                     # Docker 构建排除
├── .pre-commit-hooks.yaml            # Pre-commit hook 配置
├── .claude/
│   └── skills/
│       └── dirsort.md                # AI Agent Skill 文件
├── src/
│   └── dirsort/
│       ├── __init__.py               # 包初始化
│       ├── __main__.py               # Python -m 入口
│       ├── cli.py                    # Typer CLI 定义（所有子命令）
│       ├── config.py                 # YAML 配置加载与合并
│       ├── dupes.py                  # 重复文件检测（MD5 哈希）
│       ├── rename.py                 # 批量重命名
│       ├── rules.py                  # 文件分类规则
│       ├── sorter.py                 # 核心排序逻辑
│       ├── tui_app.py                # Textual TUI 应用
│       ├── tui_screens/
│       │   └── __init__.py           # TUI 屏幕包
│       ├── undo.py                   # Undo 回滚管理器
│       └── utils.py                  # 工具函数
├── tests/
│   ├── test_cli.py                   # CLI 测试
│   ├── test_config.py                # 配置系统测试
│   ├── test_dupes.py                 # 重复检测测试
│   ├── test_rename.py                # 重命名测试
│   ├── test_sorter.py                # 排序测试
│   ├── test_sorter_extra.py          # 排序扩展测试
│   ├── test_tui.py                   # TUI 界面测试
│   ├── test_undo.py                  # Undo 测试
│   ├── test_undo_extra.py            # Undo 扩展测试
│   ├── test_utils.py                 # 工具函数测试
│   └── __init__.py
├── docs/
│   ├── STRUCTURE.md                  # 项目结构（本文件）
│   ├── FILES.md                      # 文件功能说明
│   └── CODE.md                       # 核心代码说明
└── README.md                         # 项目说明
```
