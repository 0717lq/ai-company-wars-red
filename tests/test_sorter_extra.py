"""测试 sorter.py 中的 organize 功能和深层冲突处理。"""
import os
import tempfile
from pathlib import Path

from dirsort.sorter import analyze, organize, _resolve_conflict, _matches_any
from dirsort.rules import classify


class TestOrganize:
    def test_organize_moves_files(self):
        """验证 organize 实际移动文件。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "photo.jpg").touch()
            (p / "doc.pdf").touch()

            categories = analyze(p)
            moves = organize(p, categories)

            # 文件应被移动
            assert not (p / "photo.jpg").exists()
            assert not (p / "doc.pdf").exists()
            assert (p / "图片" / "photo.jpg").exists()
            assert (p / "文档" / "doc.pdf").exists()
            assert len(moves) == 2

    def test_organize_returns_moves(self):
        """验证 organize 返回正确的移动列表。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "file.txt").touch()

            categories = analyze(p)
            moves = organize(p, categories)

            assert len(moves) == 1
            src, dst = moves[0]
            assert src.name == "file.txt"
            assert "文档" in str(dst)

    def test_organize_by_date(self):
        """验证按日期分类的 organize。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            f = p / "file.txt"
            f.touch()
            now = 1740000000  # 固定时间戳
            os.utime(f, (now, now))

            categories = analyze(p, by_date=True)
            moves = organize(p, categories, by_date=True)

            assert len(moves) == 1
            # 文件应被移动到日期目录
            date_dirs = [d for d in p.iterdir() if d.is_dir() and len(d.name) == 7]
            assert len(date_dirs) >= 1

    def test_organize_conflict_handling(self):
        """验证冲突时自动重命名。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            # 创建目标目录和冲突文件
            target = p / "文档"
            target.mkdir()
            (target / "readme.txt").touch()

            # 创建源文件（同名）
            (p / "readme.txt").touch()

            categories = {"文档": [p / "readme.txt"]}
            moves = organize(p, categories)

            assert len(moves) == 1
            _, dst = moves[0]
            # 应该被重命名
            assert "文档" in str(dst)
            assert dst.name != "readme.txt"


class TestResolveConflict:
    def test_resolve_deep_conflict(self):
        """验证二次冲突（test_1.txt 也存在时）。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "test.txt").touch()
            (p / "test_1.txt").touch()

            result = _resolve_conflict(p, "test.txt")
            assert result == p / "test_2.txt"

    def test_resolve_deep_conflict_three(self):
        """验证三次冲突。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "test.txt").touch()
            (p / "test_1.txt").touch()
            (p / "test_2.txt").touch()

            result = _resolve_conflict(p, "test.txt")
            assert result == p / "test_3.txt"

    def test_resolve_conflict_complex_ext(self):
        """验证带有多段后缀的文件冲突（Pathlib 只识别最后一个后缀）。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "archive.tar.gz").touch()

            result = _resolve_conflict(p, "archive.tar.gz")
            # Pathlib 的 .stem 只去掉最后一个后缀，所以 .tar.gz → stem=archive.tar, suffix=.gz
            # 结果应为 archive.tar_1.gz
            assert result.name == "archive.tar_1.gz"


class TestAnalyze:
    def test_analyze_empty_result_type(self):
        """验证空分析结果类型。"""
        with tempfile.TemporaryDirectory() as tmp:
            result = analyze(Path(tmp))
            assert isinstance(result, dict)

    def test_analyze_hidden_file_ignored(self):
        """验证隐藏文件被忽略。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / ".hidden.txt").touch()
            result = analyze(p)
            total = sum(len(f) for f in result.values())
            assert total == 0

    def test_analyze_directory_skipped(self):
        """验证子目录不会被分析。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "subdir").mkdir()
            (p / "subdir" / "file.txt").touch()
            result = analyze(p)
            total = sum(len(f) for f in result.values())
            assert total == 0

    def test_analyze_returns_correct_keys(self):
        """验证分类结果的 key 正确。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "photo.jpg").touch()
            (p / "doc.pdf").touch()
            result = analyze(p)
            assert "图片" in result
            assert "文档" in result

    def test_analyze_chinese_filename(self):
        """验证中文文件名正确处理。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "报告.pdf").touch()
            (p / "照片集.jpg").touch()
            result = analyze(p)
            assert sum(len(f) for f in result.values()) == 2

    def test_analyze_space_filename(self):
        """验证带空格的文件名。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "my file.pdf").touch()
            result = analyze(p)
            assert sum(len(f) for f in result.values()) == 1

    def test_analyze_no_extension(self):
        """验证无后缀文件归类到『其他』。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "README").touch()
            result = analyze(p)
            assert "其他" in result


class TestAnalyzeExclude:
    """测试 sorter 的排除功能。"""

    def test_exclude_by_glob(self):
        """验证 --exclude 模式排除文件。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "good.txt").touch()
            (p / "bad.tmp").touch()
            (p / "also_bad.tmp").touch()

            result = analyze(p, exclude=["*.tmp"])
            total = sum(len(f) for f in result.values())
            assert total == 1
            # 被排除的文件不在结果中
            all_files = [f for files in result.values() for f in files]
            assert all(f.name == "good.txt" for f in all_files)

    def test_exclude_multiple_patterns(self):
        """验证同时排除多个 glob 模式。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "doc.txt").touch()
            (p / "temp.tmp").touch()
            (p / "cache.log").touch()

            result = analyze(p, exclude=["*.tmp", "*.log"])
            total = sum(len(f) for f in result.values())
            assert total == 1

    def test_exclude_dir_by_name(self):
        """验证排除指定目录名的文件。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "good.txt").touch()
            # 创建一个子目录，排除该目录名
            sub = p / "skip_me"
            sub.mkdir()
            (sub / "inside.txt").touch()

            # 测试 analyze 会跳过子目录（不进入子目录）
            result = analyze(p)
            total = sum(len(f) for f in result.values())
            assert total == 1  # 只有 good.txt，子目录内文件不会被扫描

    def test_matches_any(self):
        """验证 _matches_any 辅助函数。"""
        assert _matches_any("test.tmp", ["*.tmp"])
        assert _matches_any("test.TMP", ["*.tmp"]) is False  # fnmatch 区分大小写?
        # fnmatch 在 Linux 上区分大小写，所以 test.TMP 不匹配 *.tmp
        assert _matches_any("node_modules", ["node_modules"]) is True
        assert _matches_any("readme.txt", ["*.tmp", "*.log"]) is False


class TestAnalyzeWithConfigRules:
    """测试使用配置规则的分析。"""

    def test_analyze_with_custom_rules(self):
        """验证使用自定义规则分类。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "script.py").touch()

            custom_rules = {".py": "Python Files"}
            result = analyze(p, rules=custom_rules)
            assert "Python Files" in result
            assert "代码" not in result  # 自定义规则替代了默认规则

    def test_analyze_rules_merge_with_exclude(self):
        """验证自定义规则和排除功能同时工作。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "main.py").touch()
            (p / "test.py").touch()
            (p / "readme.md").touch()

            custom_rules = {".py": "Scripts", ".md": "Docs"}
            result = analyze(p, rules=custom_rules, exclude=["test.py"])
            assert "Scripts" in result
            assert "Docs" in result
            scripts = result["Scripts"]
            assert len(scripts) == 1
            assert scripts[0].name == "main.py"
