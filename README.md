<div align="center">

# dirsort 🗂️

### 智能文件目录整理 CLI 工具 — 一键解决杂乱目录的烦恼

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/0717lq/ai-company-wars-red/actions/workflows/ci.yml/badge.svg)](https://github.com/0717lq/ai-company-wars-red/actions/workflows/ci.yml)
[![PyPI - Version](https://img.shields.io/badge/pypi-v0.2.0-orange)](https://pypi.org/project/dirsort/)
[![OS - Linux | macOS | Windows](https://img.shields.io/badge/OS-Linux%20|%20macOS%20|%20Windows-lightgrey)](https://pypi.org/project/dirsort/)
[![Coverage](https://img.shields.io/badge/coverage-82%25-brightgreen)]()
[![Rich](https://img.shields.io/badge/✨-Rich%20Output-ff69b4)]()

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
$ dirsort ~/Downloads --execute
📂 正在扫描: /Users/me/Downloads
🔄 正在整理...
✅ 整理完成！移动了 42 个文件。
💡 如需回滚，请执行: dirsort undo
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

---

## 📦 安装

### 从 PyPI 安装（推荐）

```bash
pip install dirsort
# 如需富文本输出和配置文件支持：
pip install "dirsort[full]"
```

### 从源码安装

```bash
git clone https://github.com/0717lq/ai-company-wars-red.git
cd ai-company-wars-red
pip install -e ".[full,dev]"   # 开发模式，全部依赖
```

---

## 🎮 使用指南

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
# 只看数字，不移动文件
# 📊 统计结果（共 42 个文件）：
# ╭──────────┬────────┬────────╮
# │ 分类     │ 文件数 │ 占比   │
# ├──────────┼────────┼────────┤
# │ 图片     │      8 │ 19.0%  │
# │ 文档     │     15 │ 35.7%  │
# │ 代码     │      6 │ 14.3%  │
# ╰──────────┴────────┴────────╯
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

示例规则文件 `my-rules.yaml`：

```yaml
rules:
  - pattern: "*.pdf"
    category: "Documents/PDFs"
  - pattern: "*.jpg"
    category: "My Images"
  - pattern: "*.tar.gz"
    category: "Archives"
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

### 帮助

```bash
dirsort --help

# 子命令帮助
dirsort sort --help
dirsort undo --help
```

---

## 🧩 功能特性

| 功能 | 说明 |
|------|------|
| ✅ **默认安全模式** | 默认 dry-run，必须加 `--execute` 才执行，彻底杜绝误操作 |
| ✅ **按文件类型分类** | 图片、文档、视频、音频、代码、压缩包等 10+ 类别，90+ 文件后缀 |
| ✅ **按日期分类** | 自动按修改时间分到 `2026-05/` 等月份子目录 |
| ✅ **文件排除** | `--exclude "*.tmp"` 跳过指定模式文件，`--exclude-dir node_modules` 跳过目录 |
| ✅ **Rich 美化输出** | 彩色表格、对齐格式化、emoji 图标。无 Rich 自动降级到纯文本 |
| ✅ **自动冲突处理** | 同名文件自动加编号后缀，不丢失 |
| ✅ **Undo 回滚** | 一键撤销上次整理，后悔药管够 |
| ✅ **统计模式** | 带占比的 Rich 表格统计，一目了然 |
| ✅ **配置文件系统** | `--config rules.yaml` 自定义分类规则，支持 `~/.config/dirsort/rules.yaml` 自动加载 |
| ✅ **错误处理** | PermissionError/OSError 优雅跳过，不中断流程 |
| ✅ **隐藏文件保护** | 不触碰 `.` 开头的文件 |
| ✅ **中文友好** | 完整中文界面和分类名 |
| ✅ **跨平台** | Linux / macOS / Windows 全支持 |
| ✅ **零配置** | 安装即用，无需额外设置 |

### 文件分类规则

| 类别 | 支持的后缀 |
|------|-----------|
| 🖼️ 图片 | `.jpg` `.png` `.gif` `.svg` `.webp` `.ico` `.tiff` `.heic` 等 |
| 📄 文档 | `.pdf` `.docx` `.txt` `.md` `.csv` `.epub` 等 |
| 🎬 视频 | `.mp4` `.avi` `.mkv` `.mov` `.webm` `.m4v` 等 |
| 🎵 音频 | `.mp3` `.wav` `.flac` `.aac` `.ogg` `.m4a` 等 |
| 💻 代码 | `.py` `.js` `.ts` `.java` `.go` `.rs` `.html` `.css` 等 25+ 种 |
| 📦 压缩包 | `.zip` `.tar` `.gz` `.7z` `.rar` `.xz` 等 |
| ⚙️ 程序 | `.exe` `.msi` `.app` `.dmg` `.deb` `.apk` 等 |
| 🎨 设计文件 | `.psd` `.ai` `.sketch` `.fig` `.xd` |
| 🔤 字体 | `.ttf` `.otf` `.woff` `.woff2` |

---

## 📊 对比同类工具

| 特性 | **dirsort v0.2.0** 🏆 | organize-cli | fclean (蓝队) | 手动整理 |
|------|----------------------|-------------|--------------|---------|
| 默认安全模式（dry-run） | ✅ **默认** | ❌ | ✅ | — |
| Undo 回滚 | ✅ | ❌ | ❌ | 😭 |
| 按日期分类 | ✅ | ❌ | ✅ | 手动 |
| 文件排除 | ✅ | ✅ | ✅ | — |
| Rich 美化输出 | ✅ | ❌ | ✅ | — |
| **配置文件系统** | ✅ **独家** | ❌ | ❌ | — |
| 中文界面 | ✅ | ❌ | ❌ | — |
| 统计模式 | ✅ | ❌ | ❌ | — |
| 零配置开箱即用 | ✅ | ✅ | ✅ | — |
| 安装 | `pip install dirsort` | 需要配置规则文件 | `pip install fclean` | 无 |

**dirsort 的差异化优势：** 更安全（默认 dry-run + undo 双保险）、更灵活（配置文件系统独家卖点）、更易用（零配置、中文友好、Rich 美化输出）。

---

## 🛠️ 配置文件系统（独家卖点）

`dirsort --config rules.yaml` 让你的整理规则完全自定义：

```yaml
# ~/.config/dirsort/rules.yaml
rules:
  # 自定义分类：将 PDF 放入专用目录
  - pattern: "*.pdf"
    category: "Documents/PDFs"

  # 自定义分类：学术论文
  - pattern: "*.paper"
    category: "Research"

  # 多后缀文件支持
  - pattern: "*.tar.gz"
    category: "Source Archives"
```

**三大优势：**
- **覆盖默认规则** — 自定义分类名会覆盖默认分类
- **自动加载** — 放在 `~/.config/dirsort/rules.yaml` 自动生效
- **可分享** — 配置文件可以分享为 dotfiles，团队统一使用

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

1. **Fork** 本仓库
2. 创建你的特性分支：`git checkout -b feat/amazing-feature`
3. **提交代码**：`git commit -m 'feat: add amazing feature'`
4. **推送**：`git push origin feat/amazing-feature`
5. 提交 **Pull Request**

### 开发环境

```bash
git clone https://github.com/0717lq/ai-company-wars-red.git
cd ai-company-wars-red
pip install -e ".[full,dev]"
pytest              # 运行测试（77 个测试全通过）
pytest --cov=src    # 测试覆盖率（82%+）
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
