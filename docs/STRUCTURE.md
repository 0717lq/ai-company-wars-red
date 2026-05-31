# dirsort v0.6.0 — 项目结构

```
./.claude/skills/dirsort.md
./.dockerignore
./.editorconfig
./.github/workflows/ci.yml
./.gitignore
./.pre-commit-hooks.yaml
./.ruff_cache/.gitignore
./.ruff_cache/0.15.13/14634233321026755721
./.ruff_cache/0.15.13/2435219107164422519
./.ruff_cache/0.15.13/2963265366469323823
./.ruff_cache/0.15.13/5526970298105343032
./.ruff_cache/CACHEDIR.TAG
./Dockerfile
./LICENSE
./README.en.md
./README.md
./docs/CODE.md
./docs/FILES.md
./docs/STRUCTURE.md
./plugins/example_classifier.py
./pyproject.toml
./src/dirsort/__init__.py
./src/dirsort/__main__.py
./src/dirsort/cli.py
./src/dirsort/config.py
./src/dirsort/dupes.py
./src/dirsort/plugin_base.py
./src/dirsort/plugin_system.py
./src/dirsort/rename.py
./src/dirsort/rules.py
./src/dirsort/sorter.py
./src/dirsort/stats_enhanced.py
./src/dirsort/tui_app.py
./src/dirsort/tui_screens/__init__.py
./src/dirsort/undo.py
./src/dirsort/utils.py
./tests/__init__.py
./tests/test_cli.py
./tests/test_config.py
./tests/test_dupes.py
./tests/test_plugin_system.py
./tests/test_rename.py
./tests/test_sorter.py
./tests/test_sorter_extra.py
./tests/test_stats_enhanced.py
./tests/test_trial_verify.py
./tests/test_tui.py
./tests/test_undo.py
./tests/test_undo_extra.py
./tests/test_utils.py
```

## 目录说明

| 目录/文件 | 说明 |
|-----------|------|
| `src/dirsort/` | 核心源代码 |
| `tests/` | 测试文件 |
| `plugins/` | 示例插件 |
| `docs/` | 项目文档 |
| `pyproject.toml` | 项目配置和依赖 |
| `README.md` | 中文文档 |
| `README.en.md` | 英文文档 |
| `Dockerfile` | Docker 构建文件 |
| `.pre-commit-hooks.yaml` | Pre-commit hook 配置 |
| `.editorconfig` | 编辑器配置 |
| `.claude/` | AI Agent Skill |
