"""测试重复文件检测模块。"""
import hashlib
import tempfile
from pathlib import Path

from dirsort.dupes import (
    DuplicateGroup,
    _md5_file,
    delete_duplicates,
    find_duplicates,
)


class TestMd5File:
    """测试 MD5 文件哈希计算。"""

    def test_md5_small_file(self):
        """验证小文件 MD5 计算正确。"""
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "test.txt"
            f.write_text("hello world")
            expected = hashlib.md5(b"hello world").hexdigest()
            result = _md5_file(f)
            assert result == expected

    def test_md5_large_file(self):
        """验证大文件 MD5（跨分块边界）计算正确。"""
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "large.bin"
            # 写入 128KB 数据（跨越 64KB 分块边界）
            data = b"X" * (64 * 1024 + 100)
            f.write_bytes(data)
            expected = hashlib.md5(data).hexdigest()
            result = _md5_file(f)
            assert result == expected

    def test_md5_nonexistent_file(self):
        """验证不存在的文件返回 None。"""
        result = _md5_file(Path("/nonexistent/file.bin"))
        assert result is None


class TestFindDuplicates:
    """测试重复文件查找。"""

    def test_no_files(self):
        """验证空目录返回空列表。"""
        with tempfile.TemporaryDirectory() as tmp:
            groups = find_duplicates(Path(tmp))
            assert len(groups) == 0

    def test_no_duplicates(self):
        """验证无重复文件返回空列表。"""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.txt").write_text("content a")
            (Path(tmp) / "b.txt").write_text("content b")
            groups = find_duplicates(Path(tmp))
            assert len(groups) == 0

    def test_two_identical_files(self):
        """验证两个内容相同的文件被检测为重复。"""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.txt").write_text("same content")
            (Path(tmp) / "b.txt").write_text("same content")
            groups = find_duplicates(Path(tmp))
            assert len(groups) == 1
            assert len(groups[0].files) == 2
            assert groups[0].keep_file() in groups[0].files
            assert len(groups[0].dup_files()) == 1

    def test_three_identical_files(self):
        """验证三个相同文件检测为 1 组 3 个副本。"""
        with tempfile.TemporaryDirectory() as tmp:
            content = "triple duplicate"
            for i in range(3):
                (Path(tmp) / f"f{i}.txt").write_text(content)
            groups = find_duplicates(Path(tmp))
            assert len(groups) == 1
            assert len(groups[0].files) == 3

    def test_multiple_duplicate_groups(self):
        """验证多组不同内容的重复文件。"""
        with tempfile.TemporaryDirectory() as tmp:
            # Group 1: two files with "aaa"
            (Path(tmp) / "a1.txt").write_text("aaa")
            (Path(tmp) / "a2.txt").write_text("aaa")
            # Group 2: two files with "bbb"
            (Path(tmp) / "b1.txt").write_text("bbb")
            (Path(tmp) / "b2.txt").write_text("bbb")
            groups = find_duplicates(Path(tmp))
            assert len(groups) == 2
            all_files = sum(len(g.files) for g in groups)
            assert all_files == 4

    def test_min_size_filter(self):
        """验证 --min-size 过滤过小文件。"""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "small.txt").write_text("small")
            (Path(tmp) / "small2.txt").write_text("small")
            (Path(tmp) / "large.txt").write_text("X" * 2000)
            (Path(tmp) / "large2.txt").write_text("X" * 2000)
            # min-size=1KB, small files (5 bytes) should be skipped
            groups = find_duplicates(Path(tmp), min_size=1024)
            assert len(groups) == 1
            assert len(groups[0].files) == 2
            assert groups[0].files[0].name == "large.txt"

    def test_exclude_pattern(self):
        """验证 --exclude 排除文件。"""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.txt").write_text("content")
            (Path(tmp) / "b.txt").write_text("content")
            (Path(tmp) / "a.tmp").write_text("content")
            (Path(tmp) / "b.tmp").write_text("content")
            groups = find_duplicates(Path(tmp), exclude=["*.tmp"])
            assert len(groups) == 1
            # Only .txt files should be found
            assert all(f.suffix == ".txt" for g in groups for f in g.files)

    def test_exclude_hidden_files(self):
        """验证隐藏文件被自动跳过。"""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "visible.txt").write_text("same")
            (Path(tmp) / ".hidden.txt").write_text("same")
            groups = find_duplicates(Path(tmp))
            assert len(groups) == 0  # hidden file not included

    def test_nested_directories(self):
        """验证递归子目录查找。"""
        with tempfile.TemporaryDirectory() as tmp:
            sub = Path(tmp) / "subdir"
            sub.mkdir()
            (Path(tmp) / "a.txt").write_text("same")
            (sub / "b.txt").write_text("same")
            groups = find_duplicates(Path(tmp))
            assert len(groups) == 1
            assert len(groups[0].files) == 2

    def test_empty_content_file(self):
        """验证空文件检测。"""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "empty1.txt").touch()
            (Path(tmp) / "empty2.txt").touch()
            groups = find_duplicates(Path(tmp))
            assert len(groups) == 1
            assert len(groups[0].files) == 2

    def test_sort_by_size_descending(self):
        """验证结果按大小降序排列。"""
        with tempfile.TemporaryDirectory() as tmp:
            # Small dupes
            (Path(tmp) / "small1.txt").write_text("small")
            (Path(tmp) / "small2.txt").write_text("small")
            # Large dupes
            (Path(tmp) / "large1.txt").write_text("X" * 50000)
            (Path(tmp) / "large2.txt").write_text("X" * 50000)
            groups = find_duplicates(Path(tmp))
            assert len(groups) == 2
            # Large group should come first
            assert groups[0].size >= groups[1].size

    def test_recursive_exclude_dir(self):
        """验证 --exclude-dir 排除目录。"""
        with tempfile.TemporaryDirectory() as tmp:
            sub = Path(tmp) / "node_modules"
            sub.mkdir()
            (Path(tmp) / "a.txt").write_text("same")
            (sub / "b.txt").write_text("same")
            groups = find_duplicates(Path(tmp), exclude_dirs=["node_modules"])
            assert len(groups) == 0  # only file found without duplicate


class TestDeleteDuplicates:
    """测试删除重复文件。"""

    def test_delete_keeps_one_copy(self):
        """验证删除副本后保留第一个文件。"""
        with tempfile.TemporaryDirectory() as tmp:
            file1 = Path(tmp) / "keep.txt"
            file2 = Path(tmp) / "delete.txt"
            file1.write_text("content")
            file2.write_text("content")
            h = hashlib.md5(b"content").hexdigest()
            group = DuplicateGroup(h, [file1, file2])
            count = delete_duplicates([group])
            assert count == 1
            assert file1.exists()  # keep
            assert not file2.exists()  # deleted

    def test_delete_multiple_groups(self):
        """验证多组删除。"""
        with tempfile.TemporaryDirectory() as tmp:
            a1 = Path(tmp) / "a1.txt"
            a1.write_text("aaa")
            a2 = Path(tmp) / "a2.txt"
            a2.write_text("aaa")
            b1 = Path(tmp) / "b1.txt"
            b1.write_text("bbb")
            b2 = Path(tmp) / "b2.txt"
            b2.write_text("bbb")
            g1 = DuplicateGroup(
                hashlib.md5(b"aaa").hexdigest(), [a1, a2])
            g2 = DuplicateGroup(
                hashlib.md5(b"bbb").hexdigest(), [b1, b2])
            count = delete_duplicates([g1, g2])
            assert count == 2
            assert a1.exists() and b1.exists()
            assert not a2.exists() and not b2.exists()


class TestDuplicateGroup:
    """测试 DuplicateGroup 辅助方法。"""

    def test_to_dict(self):
        """验证序列化。"""
        with tempfile.TemporaryDirectory() as tmp:
            f1 = Path(tmp) / "a.txt"
            f1.write_text("content")
            f2 = Path(tmp) / "b.txt"
            f2.write_text("content")
            h = hashlib.md5(b"content").hexdigest()
            g = DuplicateGroup(h, [f1, f2])
            d = g.to_dict()
            assert d["hash"] == h
            assert d["keep"] == str(f1)
            assert d["duplicates"] == [str(f2)]
