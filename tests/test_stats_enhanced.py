"""增强统计测试 — 覆盖 ASCII 图表、大文件 Top-N 和 CLI 集成。"""

import json
from pathlib import Path

from typer.testing import CliRunner

from dirsort.stats_enhanced import (
    find_top_files,
    render_bar_chart,
    render_pie_chart,
    render_top_files,
    storage_summary,
)

runner = CliRunner()


# ── 辅助函数 ─────────────────────────────────────────────────


def _create_files(directory: Path, specs: list[tuple[str, int]]):
    """创建指定文件和大小。specs: [(filename, size_bytes), ...]"""
    for name, size in specs:
        p = directory / name
        p.write_bytes(b"x" * size)


# ══════════════════════════════════════════════════════════════
#  render_pie_chart 测试
# ══════════════════════════════════════════════════════════════


class TestPieChart:
    """ASCII 饼图渲染。"""

    def test_empty_data(self):
        """空数据返回提示文字。"""
        result = render_pie_chart({})
        assert "无数据" in result

    def test_zero_total(self):
        """所有值为 0 时返回无数据。"""
        result = render_pie_chart({"a": 0, "b": 0})
        assert "无数据" in result

    def test_basic_render(self):
        """基本饼图渲染包含标签和百分比。"""
        data = {"图片": 50, "文档": 30, "视频": 20}
        result = render_pie_chart(data)
        assert "图片" in result
        assert "文档" in result
        assert "视频" in result
        assert "%" in result
        # 包含边框字符
        assert "╔" in result
        assert "╚" in result

    def test_more_than_8_categories(self):
        """超过 8 个分类时合并为"其他"。"""
        data = {f"type_{i}": 10 for i in range(12)}
        result = render_pie_chart(data)
        assert "其他" in result

    def test_custom_title_and_width(self):
        """自定义标题和宽度。"""
        data = {"a": 10}
        result = render_pie_chart(data, title="自定义标题", width=60)
        assert "自定义标题" in result

    def test_sorted_by_count(self):
        """结果按数量降序排列。"""
        data = {"small": 1, "big": 100, "medium": 50}
        result = render_pie_chart(data)
        lines = result.split("\n")
        # big 应该在 medium 前面，medium 在 small 前面
        big_idx = next(i for i, ln in enumerate(lines) if "big" in ln)
        med_idx = next(i for i, ln in enumerate(lines) if "medium" in ln)
        small_idx = next(i for i, ln in enumerate(lines) if "small" in ln)
        assert big_idx < med_idx < small_idx


# ══════════════════════════════════════════════════════════════
#  render_bar_chart 测试
# ══════════════════════════════════════════════════════════════


class TestBarChart:
    """ASCII 柱状图渲染。"""

    def test_empty_data(self):
        """空数据返回提示。"""
        result = render_bar_chart({})
        assert "无数据" in result

    def test_basic_render(self):
        """基本柱状图渲染。"""
        data = {"Python": 100, "JavaScript": 80, "Go": 30}
        result = render_bar_chart(data)
        assert "Python" in result
        assert "JavaScript" in result
        assert "Go" in result
        assert "█" in result

    def test_max_width(self):
        """自定义最大宽度。"""
        data = {"a": 100, "b": 50}
        result = render_bar_chart(data, max_width=10)
        # 检查条形不会超过指定宽度太多
        for line in result.split("\n"):
            bar_count = line.count("█")
            assert bar_count <= 10

    def test_sorted_by_count(self):
        """结果按数量降序。"""
        data = {"z": 1, "a": 100}
        result = render_bar_chart(data)
        lines = result.split("\n")
        a_idx = next(i for i, ln in enumerate(lines) if "a" in ln)
        z_idx = next(i for i, ln in enumerate(lines) if "z" in ln)
        assert a_idx < z_idx

    def test_limit_30_items(self):
        """最多显示 30 项。"""
        data = {f"ext_{i}": i for i in range(50)}
        result = render_bar_chart(data)
        # 只有 30 项 + 标题行 + 分隔线
        bar_lines = [ln for ln in result.split("\n") if "│" in ln]
        assert len(bar_lines) <= 30


# ══════════════════════════════════════════════════════════════
#  find_top_files 测试
# ══════════════════════════════════════════════════════════════


class TestTopFiles:
    """大文件 Top-N 查找。"""

    def test_empty_dir(self, tmp_path):
        """空目录返回空列表。"""
        result = find_top_files(tmp_path)
        assert result == []

    def test_basic_top_n(self, tmp_path):
        """返回最大的 N 个文件。"""
        _create_files(tmp_path, [
            ("small.txt", 100),
            ("medium.txt", 1000),
            ("large.txt", 10000),
        ])
        result = find_top_files(tmp_path, top_n=2)
        assert len(result) == 2
        assert result[0]["name"] == "large.txt"
        assert result[0]["size"] == 10000
        assert result[1]["name"] == "medium.txt"

    def test_respects_top_n(self, tmp_path):
        """top_n 参数正确限制返回数量。"""
        _create_files(tmp_path, [(f"f{i}.txt", i * 100) for i in range(20)])
        result = find_top_files(tmp_path, top_n=5)
        assert len(result) == 5

    def test_ignores_hidden_files(self, tmp_path):
        """跳过隐藏文件。"""
        _create_files(tmp_path, [
            ("visible.txt", 1000),
            (".hidden.txt", 10000),
        ])
        result = find_top_files(tmp_path, top_n=10)
        assert len(result) == 1
        assert result[0]["name"] == "visible.txt"

    def test_exclude_glob(self, tmp_path):
        """排除匹配 glob 模式的文件。"""
        _create_files(tmp_path, [
            ("keep.txt", 100),
            ("skip.tmp", 10000),
        ])
        result = find_top_files(tmp_path, top_n=10, exclude=["*.tmp"])
        assert len(result) == 1
        assert result[0]["name"] == "keep.txt"

    def test_exclude_dirs(self, tmp_path):
        """排除指定目录下的文件。"""
        sub = tmp_path / "node_modules"
        sub.mkdir()
        _create_files(tmp_path, [("app.js", 500)])
        _create_files(sub, [("vendor.js", 50000)])
        result = find_top_files(tmp_path, top_n=10, exclude_dirs=["node_modules"])
        assert len(result) == 1
        assert result[0]["name"] == "app.js"

    def test_result_fields(self, tmp_path):
        """返回结果包含正确的字段。"""
        _create_files(tmp_path, [("test.py", 1234)])
        result = find_top_files(tmp_path, top_n=1)
        assert len(result) == 1
        f = result[0]
        assert f["name"] == "test.py"
        assert f["size"] == 1234
        assert f["ext"] == ".py"
        assert "path" in f

    def test_no_extension(self, tmp_path):
        """无扩展名的文件标记为 (无)。"""
        _create_files(tmp_path, [("Makefile", 100)])
        result = find_top_files(tmp_path, top_n=1)
        assert result[0]["ext"] == "(无)"


# ══════════════════════════════════════════════════════════════
#  render_top_files 测试
# ══════════════════════════════════════════════════════════════


class TestRenderTopFiles:
    """大文件 Top-N 渲染。"""

    def test_empty_files(self):
        """空列表返回提示。"""
        result = render_top_files([])
        assert "无数据" in result

    def test_basic_render(self, tmp_path):
        """基本渲染包含序号、大小和文件名。"""
        files = [
            {"path": str(tmp_path / "a.txt"), "name": "a.txt", "size": 1024, "ext": ".txt"},
            {"path": str(tmp_path / "b.txt"), "name": "b.txt", "size": 512, "ext": ".txt"},
        ]
        result = render_top_files(files)
        assert "1" in result
        assert "2" in result
        assert "a.txt" in result
        assert "b.txt" in result

    def test_long_filename_truncated(self):
        """长文件名被截断。"""
        long_name = "a" * 100 + ".txt"
        files = [
            {"path": f"/tmp/{long_name}", "name": long_name, "size": 100, "ext": ".txt"},
        ]
        result = render_top_files(files)
        # 截断到 45 字符
        assert "a" * 42 + "..." in result


# ══════════════════════════════════════════════════════════════
#  storage_summary 测试
# ══════════════════════════════════════════════════════════════


class TestStorageSummary:
    """存储分析摘要。"""

    def test_empty_dir(self, tmp_path):
        """空目录返回零值摘要。"""
        result = storage_summary(tmp_path)
        assert result["total_size"] == 0
        assert result["file_count"] == 0
        assert result["by_extension"] == {}

    def test_basic_summary(self, tmp_path):
        """基本摘要包含正确的统计。"""
        _create_files(tmp_path, [
            ("a.py", 100),
            ("b.py", 200),
            ("c.txt", 300),
        ])
        result = storage_summary(tmp_path)
        assert result["file_count"] == 3
        assert result["total_size"] == 600
        assert ".py" in result["by_extension"]
        assert result["by_extension"][".py"] == 300
        assert result["extension_counts"][".py"] == 2

    def test_ignores_hidden(self, tmp_path):
        """跳过隐藏文件。"""
        _create_files(tmp_path, [
            ("visible.txt", 100),
            (".hidden", 9999),
        ])
        result = storage_summary(tmp_path)
        assert result["file_count"] == 1
        assert result["total_size"] == 100

    def test_exclude_glob(self, tmp_path):
        """排除匹配 glob 的文件。"""
        _create_files(tmp_path, [
            ("keep.py", 100),
            ("skip.tmp", 9999),
        ])
        result = storage_summary(tmp_path, exclude=["*.tmp"])
        assert result["file_count"] == 1
        assert result["total_size"] == 100

    def test_exclude_dirs(self, tmp_path):
        """排除指定目录。"""
        sub = tmp_path / "vendor"
        sub.mkdir()
        _create_files(tmp_path, [("app.js", 500)])
        _create_files(sub, [("lib.js", 50000)])
        result = storage_summary(tmp_path, exclude_dirs=["vendor"])
        assert result["file_count"] == 1
        assert result["total_size"] == 500


# ══════════════════════════════════════════════════════════════
#  CLI stats 子命令集成测试
# ══════════════════════════════════════════════════════════════


class TestStatsCLI:
    """stats CLI 集成测试。"""

    def test_stats_chart_json(self, tmp_path):
        """stats --pie --json 输出合法 JSON。"""
        _create_files(tmp_path, [
            ("a.py", 100),
            ("b.txt", 200),
        ])
        from dirsort.cli import app

        result = runner.invoke(
            app,
            ["--json", "stats", "--pie", str(tmp_path)],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["operation"] == "stats_pie"
        assert "categories" in data

    def test_stats_top_json(self, tmp_path):
        """stats --top 5 --json 输出合法 JSON。"""
        _create_files(tmp_path, [(f"f{i}.txt", i * 100) for i in range(10)])
        from dirsort.cli import app

        result = runner.invoke(
            app,
            ["--json", "stats", "--top", "5", str(tmp_path)],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["operation"] == "stats_top"
        assert data["top_n"] == 5
        assert len(data["files"]) == 5

    def test_stats_by_type_json(self, tmp_path):
        """stats --by-type --json 输出合法 JSON。"""
        _create_files(tmp_path, [
            ("a.py", 100),
            ("b.py", 200),
            ("c.txt", 300),
        ])
        from dirsort.cli import app

        result = runner.invoke(
            app,
            ["--json", "stats", "--by-type", str(tmp_path)],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["operation"] == "stats_by_type"
        assert data["total"] == 3
        assert ".py" in data["extensions"]

    def test_stats_no_path(self):
        """stats 不带路径报错。"""
        from dirsort.cli import app

        result = runner.invoke(app, ["stats"])
        assert result.exit_code == 1

    def test_stats_invalid_path(self):
        """stats 无效路径报错。"""
        from dirsort.cli import app

        result = runner.invoke(app, ["stats", "/nonexistent/path"])
        assert result.exit_code == 1
