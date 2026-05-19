<div align="center">

# dirsort 🗂️

### 智能文件目录整理 CLI 工具 — 一键解决杂乱目录的烦恼

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/0717lq/ai-company-wars-red/actions/workflows/ci.yml/badge.svg)](https://github.com/0717lq/ai-company-wars-red/actions/workflows/ci.yml)
[![PyPI - Version](https://img.shields.io/badge/pypi-v0.4.0-orange)](https://pypi.org/project/dirsort/)
[![OS - Linux | macOS | Windows](https://img.shields.io/badge/OS-Linux%20|%20macOS%20|%20Windows-lightgrey)](https://pypi.org/project/dirsort/)
[![Coverage](https://img.shields.io/badge/coverage-82%25-brightgreen)]()
[![TUI](https://img.shields.io/badge/✨-Textual%20TUI-blueviolet)]()
[![Agent Skill](https://img.shields.io/badge/🤖-Agent%20Skill-blue)]()

**🇨🇳 中文** · [English](./README.md)

</div>

---

## 📸 效果一览

```text
$ dirsort ~/Downloads

📂 正在扫描: /Users/me/Downloads

   📋 整理计划（共 42 个文件）    
╭──────────┬────────┬──────────────────────────╮
│ 目标目录 │ 文件数 │ 文件示例                 │
├──────────┼────────┼──────────────────────────┤
│ 📁 图片/ │      8 │ screencast.png, ...      │
│ 📁 文档/ │     15 │ report.pdf, README.md... │
│ 📁 压缩包│      3 │ project.zip, ...         │
╰──────────┴────────┴──────────────────────────╯

⏸️  Dry-run 模式 — 未执行任何操作。使用 --execute 来真正执行整理。
```

```text
$ dirsort tui ~/Downloads
  ┌─────────────────────────────────────────────────────┐
  │ dirsort — ~/Downloads                     🕐 14:30 │
  ├──────┬─────────┬────────┬────────┬──────────────────┤
  │ 📂   │  📋     │  📊    │  ⚙️    │                  │
  │ 浏览 │  预览   │  统计  │  规则  │  交互式 TUI     │
  ├──────┴─────────┴────────┴────────┴──────────────────┤
  │ 📂 目录: ~/Downloads                  d=Dry-run    │
  │ 📁 图片/ (8 个文件):                   e=执行       │
  │   📄 screencast.png  1.2MB            q=退出       │
  │   📄 photo.jpg       456KB            r=规则       │
  │ 📁 文档/ (15 个文件):                  s=统计       │
  │   📄 report.pdf      2.1MB                          │
  │ ⏸️  Dry-run — 按 e 执行整理                         │
  └─────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

```bash
# 1. 安装
pip install dirsort

# 2. 预览整理效果（默认 safe dry-run，不执行任何操作）
dirsort ~/Downloads

# 3. 确认无误后执行（加 --execute 标志）
dirsort ~/Downloads --execute

# 4. 不满意？一键回滚
dirsort undo
```

---

## ✨ 为什么需要 dirsort？

每个人都有一个**杂乱无章的 Downloads 文件夹** — PDF 和图片混在一起、代码和压缩包纠缠不清、几十个"屏幕截图"排成一排… 找文件全靠滚滚滚。

**dirsort 一键搞定。**

| 场景 | 以前 | 用了 dirsort |
|------|------|-------------|
| 找昨天下的 PDF | 在 500 个文件里翻 | 直接去 `文档/` 目录 |
| 清理桌面截图 | 手动建文件夹、拖拽 | `dirsort ~/Desktop` |
| 想按月份看文件 | 自己看修改时间 | `dirsort ~/Downloads --by-date` |
| 怕弄乱不敢整理 | 啥也不干 | **默认 dry-run** — 安全先预览 |
| 整理完后悔了 | 一个个拖回去 | `dirsort undo` 回滚 |
| 想要可视化操作 | 要学 GUI 工具 | `dirsort tui ~/Downloads` — **交互式 TUI** |
| 让 AI Agent 帮我整理 | 手工写脚本 | **Agent Skill** — `.claude/skills/dirsort.md` 开箱即用 |

---

## 📦 安装

### 从 PyPI 安装（推荐）

```bash
pip install dirsort                    # 核心功能
pip install "dirsort[full]"            # 完整功能（Rich + YAML）
pip install "dirsort[tui]"             # 交互式 TUI 界面
pip install "dirsort[all]"             # 全部安装
```

### Docker 运行

```bash
docker run --rm -v $(pwd):/data ghcr.io/0717lq/dirsort sort /data
docker run --rm -v $(pwd):/data ghcr.io/0717lq/dirsort tui /data  # TUI 需交互式终端
```

### 从源码安装

```bash
git clone https://github.com/0717lq/ai-company-wars-red.git
cd ai-company-wars-red
pip install -e ".[full,dev]"   # 开发模式，全部依赖
```

---

## 🎮 使用指南

### 🖥️ 交互式 TUI（全新！v0.4.0）

```bash
# 启动交互式终端界面（需安装 dirsort[tui]）
dirsort tui ~/Downloads
```

**TUI 快捷键：**

| 按键 | 功能 |
|------|------|
| `d` | Dry-run 预览（刷新数据） |
| `e` | 执行整理 |
| `q` | 退出 |
| `r` | 切换到规则面板 |
| `s` | 切换到统计面板 |
| `b` | 切换到浏览面板 |
| `p` | 切换到预览面板 |

**四大面板：**

| 面板 | 功能 |
|------|------|
| 📂 文件浏览 | 目录树展示，按类型分组，显示文件大小 |
| 📋 整理预览 | 清晰展示文件 → 目标目录的映射 |
| 📊 统计面板 | 条形图 + 文件数 + 大小占比 |
| ⚙️ 规则管理 | 当前分类规则一览 |

> **安全设计：** TUI 默认 dry-run，必须按 `e` 键才执行整理。dirsort 的安全承诺一脉相承。

### 基本用法

```bash
# 默认 dry-run（安全预览，不执行任何操作）
dirsort ~/Downloads

# 真正整理（加 --execute）
dirsort ~/Downloads --execute

# 简写路径也行
dirsort .
```

### 安全预览

```bash
# 默认已是 dry-run，不需要额外参数
dirsort ~/Downloads

# 也可以显式指定（向后兼容）
dirsort ~/Downloads --dry-run
```

### 按日期分类

```bash
dirsort ~/Downloads --by-date --execute   # 或 -d
# 按月份分到 2026-05/、2026-04/ 等子目录
```

### 仅统计

```bash
dirsort ~/Downloads --stats      # 或 -s
```

### 排除文件/目录

```bash
# 排除临时文件
dirsort ~/Downloads --exclude "*.tmp" --exclude "*.log"

# 排除特定目录
dirsort ~/Downloads --exclude-dir node_modules --exclude-dir __pycache__

# 组合使用
dirsort ~/Downloads --execute --exclude "*.tmp" --exclude-dir node_modules
```

### 自定义分类规则

```bash
# 使用 YAML 配置文件自定义分类
dirsort ~/Downloads --config my-rules.yaml

# 自动检测 ~/.config/dirsort/rules.yaml（如果存在）
```

### 回滚操作

```bash
# 回滚最近一次整理（带 Rich 表格详情）
dirsort undo

# 查看详细回滚信息
dirsort undo --verbose

# 回滚指定目录的最近一次整理
dirsort undo ~/Downloads

# 查看整理历史（Rich 表格展示）
dirsort history
```

### JSON 输出（AI Agent 友好）

所有命令支持 `--json` 参数，输出机器可解析的 JSON：

```bash
dirsort ~/Downloads --json
# → {"operation":"sort","path":"/home/user/Downloads","total":42,"categories":[...]}

dirsort dupes ~/Downloads --json
# → {"operation":"dupes","groups":[...],"total_duplicates":15,"savable_bytes":5242880}
```

### 重复文件检测

```bash
# 检测重复文件
dirsort dupes ~/Downloads

# 删除重复文件（保留每组第一个）
dirsort dupes ~/Downloads --delete

# 过滤大文件
dirsort dupes ~/Downloads --min-size 1MB
```

### 批量重命名

```bash
# 预览批量重命名（默认 dry-run）
dirsort rename "*.jpg" "vacation_{n:03d}"

# 执行重命名
dirsort rename "*.jpg" "vacation_{n:03d}{ext}" --execute
```

### 配置管理

```bash
# 创建默认配置
dirsort init

# 查看当前配置
dirsort config
```

### 帮助

```bash
dirsort --help
dirsort sort --help
dirsort tui --help
```

---

## 🧩 功能特性

| 功能 | 说明 |
|------|------|
| ✅ **交互式 TUI** | `dirsort tui` — Textual 终端界面，四大面板可视化整理 |
| ✅ **AI Agent Skill** | `.claude/skills/dirsort.md` — Claude Code / Codex 开箱即用 |
| ✅ **JSON 输出** | 所有命令 `--json`，AI 友好，机器可解析 |
| ✅ **默认安全模式** | 默认 dry-run，必须加 `--execute` 才执行 |
| ✅ **按文件类型分类** | 图片、文档、视频、音频、代码、压缩包等 10+ 类别 |
| ✅ **按日期分类** | 自动按修改时间分到 `2026-05/` 等月份子目录 |
| ✅ **重复文件检测** | MD5 哈希 + 两遍扫描优化，支持删除 |
| ✅ **批量重命名** | 序号模板、冲突处理、undo 回滚 |
| ✅ **文件排除** | `--exclude` / `--exclude-dir` |
| ✅ **Rich 美化输出** | 彩色表格、emoji。无 Rich 降级纯文本 |
| ✅ **自动冲突处理** | 同名文件自动加编号后缀 |
| ✅ **Undo 回滚** | 支持 sort/rename/dupes 三种操作回滚 |
| ✅ **统计模式** | 按类型/扩展名，支持 --chart 条形图 |
| ✅ **配置文件系统** | `--config` + `~/.config/dirsort/rules.yaml` 自动加载 |
| ✅ **Shell 补全** | `--install-completion` bash/zsh/fish |
| ✅ **Docker 镜像** | `python:3.11-slim` 多阶段构建 |
| ✅ **Pre-commit hook** | `.pre-commit-hooks.yaml` 集成 |

---

## 📊 对比同类工具

| 特性 | **dirsort v0.4.0** 🏆 | organize-cli | fclean (蓝队) |
|------|----------------------|-------------|--------------|
| 交互式 TUI | ✅ **独家** | ❌ | ❌ |
| AI Agent Skill | ✅ **独家** | ❌ | ❌ |
| JSON 输出 | ✅ **独家** | ❌ | ❌ |
| 默认安全模式（dry-run） | ✅ **默认** | ❌ | ✅ |
| Undo 回滚 | ✅ | ❌ | ✅ |
| 按日期分类 | ✅ | ❌ | ✅ |
| 文件排除 | ✅ | ✅ | ✅ |
| 重复文件检测 | ✅ **独家** | ❌ | ❌ |
| 批量重命名 | ✅ **独家** | ❌ | ✅ (v0.3.0) |
| Shell 补全 | ✅ **独家** | ❌ | ❌ |
| 配置文件系统 | ✅ **独家** | ❌ | ✅ |
| Docker 镜像 | ✅ **独家** | ❌ | ❌ |
| Pre-commit hook | ✅ **独家** | ❌ | ❌ |
| Rich 美化输出 | ✅ | ❌ | ✅ |
| 中文界面 | ✅ | ❌ | ❌ |
| 安装 | `pip install dirsort` | 需要配置规则文件 | `pip install fclean` |

**dirsort 的差异化优势：** 交互式 TUI、AI Agent Skill、JSON 输出、重复检测、批量重命名、Docker 镜像 — 全面领先。

---

## 🤖 AI Agent Skill

dirsort 附带 **Agent Skill 文件**（`.claude/skills/dirsort.md`），让 Claude Code / Codex 等 AI 编码 Agent 直接使用：

```
# Claude Code 中直接调用：
User: "整理我的 Downloads 目录"
Claude: dirsort sort ~/Downloads  # 自动使用 skill 文档

User: "检查这个项目里有没有重复文件"
Claude: dirsort dupes /path/to/project --json
```

所有命令支持 `--json` 输出，AI Agent 可轻松解析和决策。

---

## 🐳 Docker

```bash
# 构建镜像
docker build -t dirsort .

# 运行
docker run --rm -v $(pwd):/data dirsort sort /data
docker run --rm -v $(pwd):/data dirsort dupes /data
docker run --rm -it -v $(pwd):/data dirsort tui /data  # 交互模式
```

---

## 🔧 Pre-commit Hook

在项目中启用 dirsort 检查：

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/0717lq/ai-company-wars-red
    rev: v0.4.0
    hooks:
      - id: dirsort-check
```

Git commit 前自动检查项目中是否有未整理的临时文件。

---

## 🛠️ 配置文件系统

`dirsort --config rules.yaml` 让你的整理规则完全自定义：

```yaml
# ~/.config/dirsort/rules.yaml
rules:
  - pattern: "*.pdf"
    category: "Documents/PDFs"
  - pattern: "*.tar.gz"
    category: "Source Archives"
```

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feat/amazing-feature`
3. **提交代码**：`git commit -m 'feat: add amazing feature'`
4. **推送**：`git push origin feat/amazing-feature`
5. 提交 **Pull Request**

### 开发环境

```bash
git clone https://github.com/0717lq/ai-company-wars-red.git
cd ai-company-wars-red
pip install -e ".[full,dev]"
pytest              # 运行测试（138 个测试全通过）
pytest --cov=src    # 测试覆盖率
```

所有 PR 自动运行 CI 测试（Python 3.10 / 3.11 / 3.12）。

---

## 📄 许可

[MIT License](./LICENSE) © 2026 Red Team

---

<div align="center">

**dirsort** — 让你的 Downloads 文件夹重获新生 ✨

⭐ 如果这个项目对你有帮助，欢迎 Star！你的支持是我的动力。

</div>
