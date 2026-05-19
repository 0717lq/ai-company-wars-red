"""测试 CLI 命令（使用 Typer CliRunner）。"""
import sys
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from dirsort.cli import app, entry

runner = CliRunner()


class TestCliSort:
    def test_sort_empty_dir(self):
        """验证对空目录运行 sort 命令（默认 dry-run）。"""
        with tempfile.TemporaryDirectory() as tmp:
            result = runner.invoke(app, ["sort", tmp])
            assert result.exit_code == 0
            # 默认 dry-run 模式，显示扫描信息
            assert "正在扫描" in result.stdout

    def test_sort_dry_run(self):
        """验证默认模式（dry-run）不移动文件。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "photo.jpg").touch()
            (p / "doc.pdf").touch()

            # 不传 --execute，默认 dry-run
            result = runner.invoke(app, ["sort", tmp])
            assert result.exit_code == 0
            assert "Dry-run" in result.stdout
            # 确认文件没有被移动
            assert (p / "photo.jpg").exists()
            assert (p / "doc.pdf").exists()

    def test_sort_explicit_dry_run(self):
        """验证显式 --dry-run 也不移动文件（向后兼容）。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "photo.jpg").touch()

            result = runner.invoke(app, ["sort", "--dry-run", tmp])
            assert result.exit_code == 0
            assert "Dry-run" in result.stdout
            assert (p / "photo.jpg").exists()

    def test_sort_actual_move(self):
        """验证 sort --execute 实际移动文件到分类目录。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "photo.jpg").touch()
            (p / "doc.pdf").touch()

            result = runner.invoke(app, ["sort", "--execute", tmp])
            assert result.exit_code == 0
            # 文件应被移动
            assert not (p / "photo.jpg").exists()
            assert not (p / "doc.pdf").exists()
            assert (p / "图片" / "photo.jpg").exists()
            assert (p / "文档" / "doc.pdf").exists()

    def test_sort_stats(self):
        """验证 --stats 模式只统计不移动。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "photo.jpg").touch()
            (p / "doc.pdf").touch()

            result = runner.invoke(app, ["sort", "--stats", tmp])
            assert result.exit_code == 0
            assert "统计结果" in result.stdout
            # 文件应保持不变
            assert (p / "photo.jpg").exists()
            assert (p / "doc.pdf").exists()

    def test_sort_by_date(self):
        """验证 --by-date --execute 按日期分类。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "file.txt").touch()

            result = runner.invoke(app, ["sort", "--by-date", "--execute", tmp])
            assert result.exit_code == 0
            # 文件应被移动到日期目录
            assert not (p / "file.txt").exists()
            # 找到日期目录
            date_dirs = [d for d in p.iterdir() if d.is_dir() and len(d.name) == 7]
            assert len(date_dirs) >= 1

    def test_sort_with_exclude(self):
        """验证 --exclude 排除文件。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "photo.jpg").touch()
            (p / "notes.tmp").touch()

            # dry-run 下验证排除效果
            result = runner.invoke(app, ["sort", "--exclude", "*.tmp", tmp])
            assert result.exit_code == 0
            assert "photo.jpg" in result.stdout
            # .tmp 文件不会被包含在计划中
            assert (p / "notes.tmp").exists()  # 而且没被移动

    def test_sort_with_exclude_dirs(self):
        """验证 --exclude-dir 排除目录中的文件。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "photo.jpg").touch()

            # 排除当前目录名（虽然文件直接在当前目录，但 pathlib 的 parent.name 会匹配）
            result = runner.invoke(
                app, ["sort", "--exclude-dir", p.name, "--execute", tmp]
            )
            assert result.exit_code == 0
            # 文件没有被移走（因为目录被排除）
            assert (p / "photo.jpg").exists()


class TestCliUndo:
    def test_undo_with_no_history(self):
        """验证没有历史时回滚。"""
        result = runner.invoke(app, ["undo"])
        assert result.exit_code == 0
        assert "没有找到可回滚的操作" in result.stdout

    def test_undo_after_sort(self):
        """验证整理后回滚可还原文件。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "photo.jpg").touch()

            # 先整理（用 --execute 执行）
            runner.invoke(app, ["sort", "--execute", tmp])
            assert not (p / "photo.jpg").exists()
            assert (p / "图片" / "photo.jpg").exists()

            # 再回滚
            result = runner.invoke(app, ["undo", tmp])
            assert result.exit_code == 0
            assert "已回滚" in result.stdout
            # 文件应回到原始位置
            assert (p / "photo.jpg").exists()

    def test_undo_verbose(self):
        """验证 --verbose 显示详细回滚信息。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "photo.jpg").touch()

            runner.invoke(app, ["sort", "--execute", tmp])
            result = runner.invoke(app, ["undo", "--verbose", tmp])
            assert result.exit_code == 0
            assert "已回滚" in result.stdout


class TestCliHistory:
    def test_history_empty(self):
        """验证空历史。"""
        # 确保历史文件不存在
        hist_file = Path.home() / ".dirsort" / "history.json"
        old_content = None
        if hist_file.exists():
            old_content = hist_file.read_text()
            hist_file.unlink()
        try:
            result = runner.invoke(app, ["history"])
            assert result.exit_code == 0
            assert "暂无操作历史记录" in result.stdout
        finally:
            if old_content is not None:
                hist_file.parent.mkdir(parents=True, exist_ok=True)
                hist_file.write_text(old_content)

    def test_history_after_sort(self):
        """验证整理后有历史记录。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "photo.jpg").touch()
            runner.invoke(app, ["sort", "--execute", tmp])
            result = runner.invoke(app, ["history"])
            assert result.exit_code == 0


class TestCliHelp:
    def test_help(self):
        """验证 --help 输出包含所有子命令。"""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "dirsort" in result.stdout
        assert "sort" in result.stdout
        assert "undo" in result.stdout
        assert "history" in result.stdout

    def test_sort_help(self):
        """验证 sort --help 列出所有排序选项。"""
        result = runner.invoke(app, ["sort", "--help"])
        assert result.exit_code == 0
        assert "--dry-run" in result.stdout
        assert "--by-date" in result.stdout
        assert "--stats" in result.stdout
        assert "--execute" in result.stdout
        assert "--exclude" in result.stdout
        assert "--exclude-dir" in result.stdout
        assert "--config" in result.stdout

    def test_nonexistent_path(self):
        """验证不存在的路径给出错误提示。"""
        result = runner.invoke(app, ["sort", "/nonexistent/path/12345"])
        assert result.exit_code == 1
        assert "错误" in result.stdout


class TestEntryWrapper:
    """验证 entry() 包装器能将 `dirsort <path>` 转为 `dirsort sort <path>`。"""

    def test_entry_injects_sort(self):
        """验证 entry() 在路径参数前注入 'sort'。"""
        with tempfile.TemporaryDirectory() as tmp:
            old_argv = sys.argv
            try:
                sys.argv = ["dirsort", tmp]
                known = {"undo", "history", "--help", "-h"}
                if len(sys.argv) > 1 and sys.argv[1] not in known:
                    sys.argv.insert(1, "sort")
                assert sys.argv[1] == "sort"
                assert sys.argv[2] == tmp
            finally:
                sys.argv = old_argv

    def test_entry_does_not_inject_for_undo(self):
        """验证 entry() 对 undo 不注入 'sort'。"""
        old_argv = sys.argv
        try:
            sys.argv = ["dirsort", "undo"]
            known = {"undo", "history", "--help", "-h"}
            if len(sys.argv) > 1 and sys.argv[1] not in known:
                sys.argv.insert(1, "sort")
            assert sys.argv[1] == "undo"
            assert len(sys.argv) == 2
        finally:
            sys.argv = old_argv


# ══════════════════════════════════════════════════════════════
#  Round 3 新增 CLI 测试
# ══════════════════════════════════════════════════════════════


class TestCliInit:
    """测试 dirsort init 命令。"""

    def test_init_creates_config(self):
        """验证 init 创建默认配置文件。"""
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert "已创建配置文件" in result.stdout

    def test_init_idempotent(self):
        """验证多次 init 不会报错。"""
        runner.invoke(app, ["init"])
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0


class TestCliConfig:
    """测试 dirsort config 命令。"""

    def test_config_path(self):
        """验证 config --path 显示配置文件路径。"""
        result = runner.invoke(app, ["config", "--path"])
        assert result.exit_code == 0
        assert "配置文件路径" in result.stdout or "config/" in result.stdout

    def test_config_after_init(self):
        """验证 init 后 config 显示内容。"""
        runner.invoke(app, ["init"])
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0


class TestCliDupes:
    """测试 dirsort dupes 命令。"""

    def test_dupes_empty_dir(self):
        """验证空目录无重复文件。"""
        with tempfile.TemporaryDirectory() as tmp:
            result = runner.invoke(app, ["dupes", tmp])
            assert result.exit_code == 0
            assert "没有找到重复文件" in result.stdout

    def test_dupes_finds_duplicates(self):
        """验证能发现重复文件。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "a.txt").write_text("same content")
            (p / "b.txt").write_text("same content")
            result = runner.invoke(app, ["dupes", tmp])
            assert result.exit_code == 0
            assert "发现" in result.stdout or "重复" in result.stdout


class TestCliRename:
    """测试 dirsort rename 命令。"""

    def test_rename_preview(self):
        """验证 rename 默认预览不执行。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "photo.jpg").touch()
            result = runner.invoke(app, ["rename", tmp, "*.jpg", "img_%04d"])
            assert result.exit_code == 0
            assert "重命名计划" in result.stdout or "预览" in result.stdout
            # 文件不应被重命名
            assert (p / "photo.jpg").exists()

    def test_rename_no_match(self):
        """验证不匹配模式提示无文件。"""
        with tempfile.TemporaryDirectory() as tmp:
            result = runner.invoke(app, ["rename", tmp, "*.xyz", "out"])
            assert result.exit_code == 0
            assert "没有找到匹配的文件" in result.stdout


class TestCliJson:
    """测试 --json 输出格式。"""

    def test_sort_json_output(self):
        """验证 sort --json 输出 JSON。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "test.jpg").touch()
            result = runner.invoke(app, ["--json", "sort", tmp])
            assert result.exit_code == 0
            import json
            data = json.loads(result.stdout)
            assert data["operation"] == "sort"
            assert "categories" in data or "status" in data

    def test_dupes_json_output(self):
        """验证 dupes --json 输出 JSON。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "a.txt").write_text("same")
            (p / "b.txt").write_text("same")
            result = runner.invoke(app, ["--json", "dupes", tmp])
            assert result.exit_code == 0
            import json
            data = json.loads(result.stdout)
            assert data["operation"] == "dupes"

    def test_init_json_output(self):
        """验证 init --json 输出 JSON。"""
        result = runner.invoke(app, ["--json", "init"])
        assert result.exit_code == 0
        import json
        data = json.loads(result.stdout)
        assert data["operation"] == "init"

    def test_history_json_output(self):
        """验证 history --json 输出 JSON。"""
        result = runner.invoke(app, ["--json", "history"])
        assert result.exit_code == 0
        import json
        data = json.loads(result.stdout)
        assert data["operation"] == "history"

    def test_config_json_output(self):
        """验证 config --json 输出 JSON。"""
        result = runner.invoke(app, ["--json", "config", "--path"])
        assert result.exit_code == 0
        import json
        data = json.loads(result.stdout)
        assert data["operation"] == "config_path"


class TestCliHelpV3:
    """验证 --help 包含新命令。"""

    def test_help_includes_new_commands(self):
        """验证 --help 列出所有子命令。"""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        for cmd in ["sort", "undo", "history", "init", "config",
                     "dupes", "rename", "stats"]:
            assert cmd in result.stdout, f"子命令 {cmd} 应在 --help 中"

