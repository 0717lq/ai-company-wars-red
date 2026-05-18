# dirsort 🗂️

> 智能文件目录整理 CLI 工具 — 一键解决杂乱目录的烦恼。

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

## 为什么需要它？

每个人都有一个混乱的 Downloads 文件夹 — PDF、图片、代码、压缩包混在一起。dirsort 一键搞定：

```bash
# 普通整理（按文件类型）
dirsort ~/Downloads

# 先预览，再执行
dirsort ~/Downloads --dry-run

# 按日期整理
dirsort ~/Downloads --by-date

# 回滚操作
dirsort undo
```

## 安装

```bash
pip install dirsort
```

## 使用

```bash
# 整理 Downloads 文件夹
dirsort ~/Downloads

# 只预览（安全模式）
dirsort ~/Downloads --dry-run

# 按月份分类
dirsort ~/Downloads --by-date

# 只看统计
dirsort ~/Downloads --stats

# 回滚上次操作
dirsort undo

# 查看历史
dirsort history
```

## 功能

- ✅ **按文件类型**分类：图片、文档、视频、代码、压缩包等 10+ 类别
- ✅ **按日期**分类：自动按修改时间分到 `2026-05/` 等月份子目录
- ✅ **Dry-run 模式**：先预览后执行，零风险
- ✅ **自动处理冲突**：同名文件自动添加编号后缀
- ✅ **Undo 回滚**：随时撤销上次整理
- ✅ **统计模式**：只看数据不移动
- ✅ **隐藏文件保护**：不触碰 `.` 开头的文件

## 文件分类规则

| 类别 | 后缀 |
|------|------|
| 图片 | .jpg, .png, .gif, .svg, .webp ... |
| 文档 | .pdf, .docx, .txt, .md, .csv ... |
| 视频 | .mp4, .avi, .mkv, .mov ... |
| 音频 | .mp3, .wav, .flac, .aac ... |
| 代码 | .py, .js, .ts, .java, .go, .rs ... |
| 压缩包 | .zip, .tar, .gz, .7z, .rar ... |

## 未来规划

- [ ] 自定义规则配置文件
- [ ] 定时自动整理
- [ ] Web UI 界面
- [ ] 重复文件检测
