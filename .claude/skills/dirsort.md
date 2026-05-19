# dirsort — 智能文件目录整理 CLI 工具

> AI Agent Skill · dirsort v0.4.0

## 简介

dirsort 是一个智能文件目录整理 CLI 工具，支持按类型/日期自动分类、重复文件检测、批量重命名、交互式 TUI 界面、Undo 回滚等功能。

## 安装

```bash
pip install dirsort          # 核心功能
pip install dirsort[full]    # 完整功能（含 Rich 美化输出）
pip install dirsort[tui]     # TUI 交互界面
pip install dirsort[all]     # 全部安装
```

## 子命令总览

| 子命令 | 功能 | 推荐使用场景 |
|--------|------|-------------|
| `sort` | 按类型/日期整理文件 | 整理 Downloads、桌面等 |
| `dupes` | 检测重复文件 | 清理重复照片、备份 |
| `rename` | 批量重命名 | 批量编号、格式化文件名 |
| `undo` | 回滚操作 | 整理错了想恢复 |
| `history` | 查看操作历史 | 检查整理记录 |
| `stats` | 统计文件信息 | 了解目录结构 |
| `init` | 初始化配置 | 首次使用 |
| `config` | 查看/管理配置 | 自定义分类规则 |
| `tui` | 交互式 TUI | 可视化整理体验 |

## 使用示例

### 文件整理（核心功能）

```bash
# 快速整理 Downloads 目录（默认 dry-run，安全预览）
dirsort sort ~/Downloads

# 真正执行整理
dirsort sort ~/Downloads --execute

# 按日期整理（按月份分类）
dirsort sort ~/Downloads --by-date

# 排除特定文件
dirsort sort ~/Downloads --exclude "*.tmp" --exclude-dir node_modules

# 自定义配置文件
dirsort sort ~/Downloads --config my-rules.yaml
```

### 重复文件检测

```bash
# 检测重复文件
dirsort dupes ~/Downloads

# 删除重复文件（保留每组第一个）
dirsort dupes ~/Downloads --delete

# 过滤大文件（跳过 1MB 以上的文件）
dirsort dupes ~/Downloads --min-size 1MB

# JSON 输出（AI Agent 可解析）
dirsort dupes ~/Downloads --json
```

### 批量重命名

```bash
# 预览重命名（默认 dry-run）
dirsort rename "*.jpg" "vacation_{n:03d}"

# 执行重命名
dirsort rename "*.jpg" "vacation_{n:03d}{ext}" --execute

# JSON 输出
dirsort rename "*.jpg" "photo_{n:04d}" --json
```

### 交互式 TUI

```bash
# 启动 TUI 界面（需安装 dirsort[tui]）
dirsort tui ~/Downloads
```

TUI 快捷键：
- `d` — Dry-run 预览
- `e` — 执行整理
- `q` — 退出
- `r` — 切换到规则面板
- `s` — 切换到统计面板
- `b` — 切换到浏览面板
- `p` — 切换到预览面板

### JSON 输出（AI Agent 调用）

所有命令支持 `--json` 参数，输出机器可解析的 JSON：

```bash
# JSON 格式的整理预览
dirsort sort ~/Downloads --json
# → {"operation": "sort", "path": "/home/user/Downloads", "status": "dry_run", "total": 42, "categories": [...]}

# JSON 格式的重复检测
dirsort dupes ~/Downloads --json
# → {"operation": "dupes", "groups": [...], "total_duplicates": 15, "savable_bytes": 5242880}

# JSON 格式的统计
dirsort stats ~/Downloads --json
# → {"operation": "stats", "total_files": 200, "categories": {"图片": 50, "文档": 80, ...}}

# JSON 格式的历史
dirsort history --json
```

### 配置管理

```bash
# 创建默认配置
dirsort init

# 查看当前配置
dirsort config

# 查看配置路径
dirsort config --path

# JSON 格式查看
dirsort config --json
```

### 回滚与历史

```bash
# 查看历史操作记录
dirsort history

# 回滚上次操作
dirsort undo

# 回滚特定目录的操作
dirsort undo ~/Downloads

# 详细回滚信息
dirsort undo --verbose

# JSON 格式历史
dirsort history --json
```

## 典型场景

### AI Agent 整理项目文件
```bash
# 整理项目中的临时文件
dirsort sort /path/to/project --exclude "*.py" --exclude-dir .venv

# 检查是否有重复依赖
dirsort dupes /path/to/project --min-size 100KB --json
```

### 批量处理图片
```bash
# 批量重命名照片
dirsort rename "*.jpg" "photo_{n:04d}{ext}" --execute

# 按类型整理到分类目录
dirsort sort ~/Desktop --execute
```

### 自动化脚本集成
```bash
# 在 CI 中检查未整理文件
dirsort sort /path/to/repo --json | jq '.status'

# 定时清理
dirsort dupes ~/Downloads --delete --json
```

## 配置格式 (`~/.config/dirsort/rules.yaml`)

```yaml
rules:
  ".drawio": "绘图文件"
  ".log": "日志文件"
```

## 相关链接

- GitHub: https://github.com/0717lq/ai-company-wars-red
- PyPI: https://pypi.org/project/dirsort/
