<div align="center">

# dirsort 🗂️

### Smart File Organization CLI — Tame your messy Downloads folder with one command

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/0717lq/ai-company-wars-red/actions/workflows/ci.yml/badge.svg)](https://github.com/0717lq/ai-company-wars-red/actions/workflows/ci.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/dirsort?color=orange)](https://pypi.org/project/dirsort/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/dirsort?color=blue)](https://pypi.org/project/dirsort/)
[![Docker](https://img.shields.io/badge/docker-ghcr.io-blue?logo=docker)](https://github.com/0717lq/ai-company-wars-red/pkgs/container/dirsort)
[![OS - Linux | macOS | Windows](https://img.shields.io/badge/OS-Linux%20|%20macOS%20|%20Windows-lightgrey)](https://pypi.org/project/dirsort/)
[![TUI](https://img.shields.io/badge/✨-Textual%20TUI-blueviolet)](https://textual.textualize.io/)
[![Agent Skill](https://img.shields.io/badge/🤖-Agent%20Skill-blue)](.claude/skills/dirsort.md)

**English** · [🇨🇳 中文](./README.md)

</div>

---

## 🎉 What's New in v0.4.0 — "TUI + Agent-Ready"

> The biggest dirsort update yet! 🚀

| Feature | Description | How to Use |
|---------|-------------|------------|
| 🖥️ **Interactive TUI** | Textual terminal UI with 4 panels | `dirsort tui ~/Downloads` |
| 🤖 **AI Agent Skill** | Ready-to-use with Claude Code / Codex | [dirsort.md](.claude/skills/dirsort.md) |
| 🐳 **Docker Image** | `python:3.11-slim` multi-stage build | `docker run ghcr.io/0717lq/dirsort` |
| 🔧 **Pre-commit Hook** | Auto-check before git commit | [Setup guide](#pre-commit-hook) |
| ✨ `dirsort[all]` | One-line install with all deps | `pip install "dirsort[all]"` |

---

## 📸 Demo

```text
$ dirsort ~/Downloads

📂 Scanning: /Users/me/Downloads

   📋 Plan (42 files found)
╭──────────┬────────┬──────────────────────────╮
│ Target   │ Files  │ Examples                 │
├──────────┼────────┼──────────────────────────┤
│ 📁 Pictures/│     8 │ screencast.png, ...     │
│ 📁 Documents/│   15 │ report.pdf, README.md   │
│ 📁 Archives/│     3 │ project.zip, ...        │
╰──────────┴────────┴──────────────────────────╯

⏸️  Dry-run mode — nothing was moved. Use --execute to actually sort.
```

```text
$ dirsort tui ~/Downloads
  ┌─────────────────────────────────────────────────────┐
  │ dirsort — ~/Downloads                     🕐 14:30 │
  ├──────┬─────────┬────────┬────────┬──────────────────┤
  │ 📂   │  📋     │  📊    │  ⚙️    │                  │
  │Browse│  Preview│ Stats  │  Rules │  Interactive TUI │
  ├──────┴─────────┴────────┴────────┴──────────────────┤
  │ 📂 Directory: ~/Downloads              d=Dry-run    │
  │ 📁 Images/ (8 files):                   e=Execute   │
  │   📄 screencast.png  1.2MB            q=Quit       │
  │   📄 photo.jpg       456KB            r=Rules      │
  │ 📁 Documents/ (15 files):              s=Stats      │
  │   📄 report.pdf      2.1MB                          │
  │ ⏸️  Dry-run — Press e to execute                   │
  └─────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

```bash
# 1. Install
pip install dirsort

# 2. Preview sort (safe dry-run by default)
dirsort ~/Downloads

# 3. Execute when ready (add --execute flag)
dirsort ~/Downloads --execute

# 4. Not happy? Undo with one command
dirsort undo
```

---

## ✨ Why dirsort?

Everyone has a **messy Downloads folder** — PDFs mixed with images, code tangled with archives, 50 "Screenshot" files in a row… Finding anything means scrolling forever.

**dirsort fixes that with one command.**

| Situation | Before | With dirsort |
|-----------|--------|-------------|
| Find yesterday's PDF | Dig through 500 files | Go to `Documents/` |
| Clean desktop screenshots | Manual folder creation + dragging | `dirsort ~/Desktop` |
| Organize by month | Check file dates manually | `dirsort ~/Downloads --by-date` |
| Afraid to mess things up | Do nothing | **Default dry-run** — preview safely |
| Regret sorting | Drag everything back | `dirsort undo` to rollback |
| Want visual interaction | Learn a GUI tool | `dirsort tui ~/Downloads` — **Interactive TUI** |
| Let AI Agent handle it | Write scripts manually | **Agent Skill** — ready-to-use `.claude/skills/dirsort.md` |

---

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install dirsort                    # Core functionality
pip install "dirsort[full]"            # Full features (Rich + YAML)
pip install "dirsort[tui]"             # Interactive TUI
pip install "dirsort[all]"             # Everything
```

### Docker

```bash
# One-liner run (recommended)
docker run --rm -v $(pwd):/data ghcr.io/0717lq/dirsort sort /data

# Interactive TUI (needs interactive terminal)
docker run --rm -it -v $(pwd):/data ghcr.io/0717lq/dirsort tui /data

# Duplicate file detection
docker run --rm -v $(pwd):/data ghcr.io/0717lq/dirsort dupes /data
```

### From Source

```bash
git clone https://github.com/0717lq/ai-company-wars-red.git
cd ai-company-wars-red
pip install -e ".[full,dev]"   # Dev mode with all deps
```

---

## 🎮 Usage Guide

### 🖥️ Interactive TUI (NEW! v0.4.0)

```bash
# Launch the terminal UI (requires dirsort[tui])
dirsort tui ~/Downloads
```

**TUI Shortcuts:**

| Key | Action |
|-----|--------|
| `d` | Dry-run preview (refresh data) |
| `e` | Execute sorting |
| `q` | Quit |
| `r` | Switch to rules panel |
| `s` | Switch to stats panel |
| `b` | Switch to browse panel |
| `p` | Switch to preview panel |

**Four Panels:**

| Panel | Description |
|-------|-------------|
| 📂 File Browser | Directory tree, grouped by type, file sizes shown |
| 📋 Sort Preview | Clear file → target directory mapping |
| 📊 Statistics | Bar charts + file count + size distribution |
| ⚙️ Rules | Current classification rules overview |

> **Safety first:** TUI starts in dry-run mode. Press `e` to execute. Same security promise as CLI.

### Basic Usage

```bash
# Default dry-run (preview only, nothing changes)
dirsort ~/Downloads

# Actually sort (add --execute)
dirsort ~/Downloads --execute

# Short path works too
dirsort .
```

### Safe Preview

```bash
# Default is already dry-run, no extra flag needed
dirsort ~/Downloads

# Explicit dry-run (backward compatible)
dirsort ~/Downloads --dry-run
```

### Sort by Date

```bash
dirsort ~/Downloads --by-date --execute   # or -d
# Files sorted into 2026-05/, 2026-04/ etc. by modification date
```

### Statistics Only

```bash
dirsort ~/Downloads --stats      # or -s
```

### Exclude Files/Directories

```bash
# Exclude temp files
dirsort ~/Downloads --exclude "*.tmp" --exclude "*.log"

# Exclude specific directories
dirsort ~/Downloads --exclude-dir node_modules --exclude-dir __pycache__

# Combined
dirsort ~/Downloads --execute --exclude "*.tmp" --exclude-dir node_modules
```

### Custom Rules

```bash
# Use YAML config file for custom classification
dirsort ~/Downloads --config my-rules.yaml

# Auto-detect ~/.config/dirsort/rules.yaml (if exists)
```

### Undo & History

```bash
# Roll back most recent sort
dirsort undo

# Show detailed rollback info
dirsort undo --verbose

# Roll back a specific directory
dirsort undo ~/Downloads

# View sort history
dirsort history
```

### JSON Output (AI Agent Friendly)

All commands support `--json` for machine-parsable output:

```bash
dirsort ~/Downloads --json
# → {"operation":"sort","path":"/home/user/Downloads","total":42,"categories":[...]}

dirsort dupes ~/Downloads --json
# → {"operation":"dupes","groups":[...],"total_duplicates":15,"savable_bytes":5242880}
```

### Duplicate File Detection

```bash
# Detect duplicate files
dirsort dupes ~/Downloads

# Delete duplicates (keep first in each group)
dirsort dupes ~/Downloads --delete

# Filter large files
dirsort dupes ~/Downloads --min-size 1MB
```

### Batch Rename

```bash
# Preview rename (default dry-run)
dirsort rename "*.jpg" "vacation_{n:03d}"

# Execute rename
dirsort rename "*.jpg" "vacation_{n:03d}{ext}" --execute

# JSON output
dirsort rename "*.jpg" "photo_{n:04d}" --json
```

### Configuration

```bash
# Create default config
dirsort init

# View current config
dirsort config
```

### Help

```bash
dirsort --help
dirsort sort --help
dirsort tui --help
```

---

## 🧩 Feature Overview

| Feature | Description |
|---------|-------------|
| ✅ **Interactive TUI** | `dirsort tui` — Textual terminal UI with 4 panels |
| ✅ **AI Agent Skill** | `.claude/skills/dirsort.md` — ready for Claude Code / Codex |
| ✅ **JSON Output** | `--json` on every command, AI-parsable |
| ✅ **Safe by Default** | Dry-run by default, `--execute` to act |
| ✅ **Sort by Type** | Images, docs, videos, audio, code, archives, 10+ categories |
| ✅ **Sort by Date** | Auto-group into `2026-05/` month dirs by modification date |
| ✅ **Duplicate Detection** | MD5 hash + two-pass optimization, supports deletion |
| ✅ **Batch Rename** | Sequential templates, conflict handling, undo |
| ✅ **File Exclusions** | `--exclude` / `--exclude-dir` patterns |
| ✅ **Rich Output** | Colored tables, emojis. Degrades gracefully without Rich |
| ✅ **Auto Conflict Handling** | Auto-number suffix for filename conflicts |
| ✅ **Undo Rollback** | Reversible sort/rename/dupes operations |
| ✅ **Stats Mode** | By type/extension, `--chart` bar chart |
| ✅ **Config File System** | `--config` + auto-load `~/.config/dirsort/rules.yaml` |
| ✅ **Shell Completions** | `--install-completion` for bash/zsh/fish |
| ✅ **Docker Image** | `python:3.11-slim` multi-stage build |
| ✅ **Pre-commit Hook** | `.pre-commit-hooks.yaml` integration |

---

## 📊 Comparison

| Feature | **dirsort v0.4.0** 🏆 | organize-cli | fclean (Blue) |
|---------|----------------------|-------------|--------------|
| Interactive TUI | ✅ **Exclusive** | ❌ | ❌ |
| AI Agent Skill | ✅ **Exclusive** | ❌ | ❌ |
| JSON Output | ✅ **Exclusive** | ❌ | ❌ |
| Safe Default (dry-run) | ✅ **Default** | ❌ | ✅ |
| Undo Rollback | ✅ | ❌ | ✅ |
| Sort by Date | ✅ | ❌ | ✅ |
| File Exclusions | ✅ | ✅ | ✅ |
| Duplicate Detection | ✅ **Exclusive** | ❌ | ❌ |
| Batch Rename | ✅ **Exclusive** | ❌ | ✅ (v0.3.0) |
| Shell Completions | ✅ **Exclusive** | ❌ | ❌ |
| Config File System | ✅ **Exclusive** | ❌ | ✅ |
| Docker Image | ✅ **Exclusive** | ❌ | ❌ |
| Pre-commit Hook | ✅ **Exclusive** | ❌ | ❌ |
| Rich Output | ✅ | ❌ | ✅ |
| Install | `pip install dirsort` | Requires config setup | `pip install fclean` |

**Why dirsort?** Interactive TUI, AI Agent Skill, JSON output, duplicate detection, batch rename, Docker image — leading across the board.

---

## 🤖 AI Agent Skill

dirsort includes an **Agent Skill file** (`.claude/skills/dirsort.md`) so AI coding agents like Claude Code / Codex can use it immediately:

```
# In Claude Code:
User: "Organize my Downloads folder"
Claude: dirsort sort ~/Downloads  # uses the skill doc automatically

User: "Check for duplicate files in this project"
Claude: dirsort dupes /path/to/project --json
```

All commands support `--json` for easy AI parsing and decision-making.

---

## 🐳 Docker

Pull from GitHub Container Registry:

```bash
docker pull ghcr.io/0717lq/dirsort:latest

# Sort current directory
docker run --rm -v $(pwd):/data ghcr.io/0717lq/dirsort sort /data

# Detect duplicates
docker run --rm -v $(pwd):/data ghcr.io/0717lq/dirsort dupes /data

# TUI interactive mode (requires interactive terminal)
docker run --rm -it -v $(pwd):/data ghcr.io/0717lq/dirsort tui /data
```

Build locally:

```bash
git clone https://github.com/0717lq/ai-company-wars-red.git
cd ai-company-wars-red
docker build -t dirsort .
docker run --rm -v $(pwd):/data dirsort sort /data
```

---

## 🔧 Pre-commit Hook

Add dirsort checks to your project (auto-detect unsorted temp files before commits):

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/0717lq/ai-company-wars-red
    rev: v0.4.0
    hooks:
      - id: dirsort-check
```

---

## 🛠️ Config File System

`dirsort --config rules.yaml` for fully customizable rules:

```yaml
# ~/.config/dirsort/rules.yaml
rules:
  - pattern: "*.pdf"
    category: "Documents/PDFs"
  - pattern: "*.tar.gz"
    category: "Source Archives"
```

---

## 🤝 Contributing

All contributions are welcome!

1. **Fork** this repo
2. Create a feature branch: `git checkout -b feat/amazing-feature`
3. **Commit** your changes: `git commit -m 'feat: add amazing feature'`
4. **Push**: `git push origin feat/amazing-feature`
5. Open a **Pull Request**

### Dev Setup

```bash
git clone https://github.com/0717lq/ai-company-wars-red.git
cd ai-company-wars-red
pip install -e ".[full,dev]"
pytest              # Run tests (138 passing)
pytest --cov=src    # Coverage report
```

All PRs run CI tests automatically (Python 3.10 / 3.11 / 3.12).

---

## 📄 License

[MIT License](./LICENSE) © 2026 Red Team

---

<div align="center">

**dirsort** — Give your Downloads folder a fresh start ✨

⭐ Star this project if you find it useful!

</div>
