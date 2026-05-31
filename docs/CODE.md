# dirsort v0.6.0 — 核心代码说明

## plugin_base.py — 插件基类

| 元素 | 说明 |
|------|------|
| `PluginBase(ABC)` | 抽象基类，所有插件必须继承 |
| `classify(file_path) -> str | None` | **抽象方法** — 自定义文件分类，返回分类名或 None |
| `generate_report(results) -> str | None` | 可选覆盖 — 自定义报告格式 |
| `name / version / description` | 类属性 — 插件元信息 |
| `__repr__` | `<Plugin 'name' v1.0.0>` |

## plugin_system.py — 插件引擎

| 元素 | 说明 |
|------|------|
| `DEFAULT_PLUGIN_DIR` | `~/.dirsort/plugins/` |
| `PluginManager` | 插件管理器主类 |
| `.discover_and_load()` | 扫描插件目录，importlib 动态加载 .py 文件 |
| `.install_plugin(source)` | 复制 + 验证 + 注册插件 |
| `.classify_file(path)` | 插件链调用（first match wins），异常安全 |
| `.generate_reports(results)` | 收集所有插件报告 |
| `.reload()` | 热重载 — 清空后重新加载 |
| `.get_plugin_info(name)` | 插件详情（含 has_report 判断） |
| `.create_plugin_template(name)` | 生成脚手架代码 |

## stats_enhanced.py — 增强统计

| 元素 | 说明 |
|------|------|
| `render_pie_chart(data, title, width)` | ASCII 饼图（横向条形图，Unicode 块 + ANSI 颜色） |
| `render_bar_chart(data, title, max_width)` | ASCII 柱状图（水平条形图） |
| `find_top_files(target, top_n, ...)` | 大文件 Top-N 查找（rglob + stat） |
| `render_top_files(files, title)` | Top-N 格式化输出 |
| `storage_summary(target, ...)` | 存储分析摘要（total_size, by_extension, extension_counts） |

## cli.py — 新增命令

| 命令 | 说明 |
|------|------|
| `dirsort plugin list` | 列出已安装插件 |
| `dirsort plugin install <path>` | 安装 .py 插件文件 |
| `dirsort plugin create <name>` | 生成插件模板 |
| `dirsort plugin info <name>` | 插件详情 |
| `dirsort plugin reload` | 热重载插件 |
| `dirsort stats --pie` | ASCII 饼图 |
| `dirsort stats --chart` | 扩展名条形图 |
| `dirsort stats --top N` | 大文件 Top-N |

## JSON 元数据增强

`--json` 输出统一 envelope 新增 `metadata` 字段：

```json
{
  "operation": "sort",
  "metadata": {
    "version": "0.6.0",
    "engine": "dirsort/0.6.0",
    "plugins": [{"name": "...", "version": "..."}]
  }
}
```
