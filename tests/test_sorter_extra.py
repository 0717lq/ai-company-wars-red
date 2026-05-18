"""测试 sorter.py 中的 organize 功能和深层冲突处理。"""
import os
import tempfile
from pathlib import Path

from dirsort.sorter import analyze, organize, _resolve_conflict
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
