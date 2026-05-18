"""测试分类规则和核心排序逻辑。"""
import tempfile
from pathlib import Path

from dirsort.rules import classify, DEFAULT_RULES, get_all_categories
from dirsort.sorter import analyze, _resolve_conflict


class TestRules:
    def test_classify_image(self):
        assert classify("photo.jpg") == "图片"
        assert classify("photo.jpeg") == "图片"
        assert classify("photo.PNG") == "图片"  # 大写后缀

    def test_classify_document(self):
        assert classify("report.pdf") == "文档"
        assert classify("readme.md") == "文档"
        assert classify("data.csv") == "文档"

    def test_classify_code(self):
        assert classify("main.py") == "代码"
        assert classify("app.js") == "代码"
        assert classify("style.css") == "代码"

    def test_classify_unknown(self):
        assert classify("file.xyz") == "其他"
        assert classify("noext") == "其他"

    def test_classify_hidden(self):
        # 隐藏文件按后缀规则分类，但在 analyze 中会被过滤
        assert classify(".gitignore") == "其他"

    def test_all_categories(self):
        cats = get_all_categories()
        assert "图片" in cats
        assert "文档" in cats
        assert "代码" in cats
        assert "其他" in cats


class TestSorter:
    def test_analyze_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = analyze(Path(tmp))
            assert isinstance(result, dict)
            assert len(result) == 0

    def test_analyze_single_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "photo.jpg").touch()
            result = analyze(p)
            assert "图片" in result
            assert len(result["图片"]) == 1
            assert result["图片"][0].name == "photo.jpg"

    def test_analyze_multiple_categories(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "photo.jpg").touch()
            (p / "doc.pdf").touch()
            (p / "main.py").touch()
            (p / "unknown.xyz").touch()
            result = analyze(p)
            assert sum(len(files) for files in result.values()) == 4

    def test_analyze_skips_hidden(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / ".hidden").touch()
            (p / "visible.txt").touch()
            result = analyze(p)
            count = sum(len(files) for files in result.values())
            assert count == 1

    def test_analyze_skips_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "subdir").mkdir()
            result = analyze(p)
            assert len(result) == 0

    def test_resolve_conflict_no_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            result = _resolve_conflict(p, "test.txt")
            assert result == p / "test.txt"

    def test_resolve_conflict_with_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "test.txt").touch()
            result = _resolve_conflict(p, "test.txt")
            assert result == p / "test_1.txt"
            # 再冲突一次
            result2 = _resolve_conflict(p, "test.txt")
            assert result2 == p / "test_1.txt"  # 仍然返回同一个，因为 test_1.txt 已存在

    def test_analyze_by_date(self):
        import os
        import time
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            f = p / "somefile.txt"
            f.touch()
            # 设置文件时间为当前时间
            now = time.time()
            os.utime(f, (now, now))
            result = analyze(p, by_date=True)
            # 应该有一个 "YYYY-MM" 的分类
            date_cats = [k for k in result if len(k) == 7 and k[4] == "-"]
            assert len(date_cats) >= 1
