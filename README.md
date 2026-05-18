<div align="center">

# dirsort 🗂️

### 智能文件目录整理 CLI 工具 — 一键解决杂乱目录的烦恼

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/0717lq/ai-company-wars-red/actions/workflows/ci.yml/badge.svg)](https://github.com/0717lq/ai-company-wars-red/actions/workflows/ci.yml)
[![PyPI - Version](https://img.shields.io/badge/pypi-v0.1.0-orange)](https://pypi.org/project/dirsort/)
[![OS - Linux | macOS | Windows](https://img.shields.io/badge/OS-Linux%20|%20macOS%20|%20Windows-lightgrey)](https://pypi.org/project/dirsort/)
[![Downloads](https://img.shields.io/badge/dynamic/json?label=downloads&query=downloads&url=https%3A%2F%2Fpypistats.org%2Fapi%2Fpackages%2Fdirsort%2Frecent%3Fperiod%3Dmonth&color=blue)]()

**🇨🇳 中文** · [English](./README.md)

</div>

---

## 📸 效果一览

```text
$ dirsort ~/Downloads

📂 正在扫描: /Users/me/Downloads

📋 整理计划（共 42 个文件）：

  📁 → 图片/ (8 个文件)
      📄 screencast.png
      📄 photo_001.jpg
      📄 logo.svg
      ...

  📁 → 文档/ (15 个文件)
      📄 report.pdf
      📄 meeting-notes.docx
      📄 README.md
      ...

  📁 → 压缩包/ (3 个文件)
      📄 project.zip
      📄 archive.tar.gz

⏸️  Dry-run 模式 — 未执行任何操作。移除 --dry-run 以执行。
```

```text
$ dirsort ~/Downloads
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

# 2. 预览整理效果（安全模式，不执行任何操作）
dirsort ~/Downloads --dry-run

# 3. 执行整理
dirsort ~/Downloads

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
| 怕弄乱不敢整理 | 啥也不干 | `--dry-run` 先预览 |
| 整理完后悔了 | 一个个拖回去 | `dirsort undo` 回滚 |

---

## 📦 安装

### 从 PyPI 安装（推荐）

```bash
pip install dirsort
```

### 从源码安装

```bash
git clone https://github.com/0717lq/ai-company-wars-red.git
cd ai-company-wars-red
pip install -e ".[dev]"   # 开发模式，包含测试依赖
```

---

## 🎮 使用指南

### 基本用法

```bash
# 整理一个目录（按文件类型分类）
dirsort ~/Downloads

# 简写路径也行
dirsort .
```

### 安全预览

```bash
dirsort ~/Downloads --dry-run    # 或 -n
# 显示分类计划，不移动任何文件
```

### 按日期分类

```bash
dirsort ~/Downloads --by-date    # 或 -d
# 按月份分到 2026-05/、2026-04/ 等子目录
```

### 仅统计

```bash
dirsort ~/Downloads --stats      # 或 -s
# 只看数字，不移动文件
# 📊 统计结果（共 42 个文件）：
#   图片: 8 个文件
#   文档: 15 个文件
#   视频: 2 个文件
#   代码: 6 个文件
#   压缩包: 3 个文件
#   其他: 8 个文件
```

### 回滚操作

```bash
# 回滚最近一次整理
dirsort undo

# 回滚指定目录的最近一次整理
dirsort undo ~/Downloads

# 查看整理历史
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
| ✅ **按文件类型分类** | 图片、文档、视频、音频、代码、压缩包等 10+ 类别，90+ 文件后缀 |
| ✅ **按日期分类** | 自动按修改时间分到 `2026-05/` 等月份子目录 |
| ✅ **Dry-run 模式** | 先预览后执行，零风险 |
| ✅ **自动冲突处理** | 同名文件自动加编号后缀，不丢失 |
| ✅ **Undo 回滚** | 一键撤销上次整理，后悔药管够 |
| ✅ **统计模式** | 只看数据不动手 |
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

| 特性 | **dirsort** 🏆 | organize-cli | ffs | 手动整理 |
|------|---------------|-------------|-----|---------|
| Dry-run 预览 | ✅ | ✅ | ❌ | — |
| Undo 回滚 | ✅ | ❌ | ❌ | 😭 |
| 按日期分类 | ✅ | ❌ | ✅ | 手动 |
| 中文界面 | ✅ | ❌ | ❌ | — |
| 统计模式 | ✅ | ❌ | ❌ | — |
| 零配置开箱即用 | ✅ | ✅ | ❌ | — |
| 安装 | `pip install dirsort` | 需要配置规则文件 | 复杂 | 无 |

**dirsort 的差异化优势：** 更安全（dry-run + undo 双保险）、更易用（零配置、中文友好）、更全面（类型 + 日期双模式）。

---

## 🛠️ 自定义与扩展

> 计划中 — 后续版本将支持：

- [ ] 自定义配置文件（`~/.dirsort/config.toml`）
- [ ] 定时自动整理
- [ ] Web UI 界面
- [ ] 重复文件检测
- [ ] 自定义分类规则

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
pip install -e ".[dev]"
pytest              # 运行测试
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
