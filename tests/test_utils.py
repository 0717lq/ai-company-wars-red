"""测试文件操作工具函数。"""
import tempfile
from pathlib import Path

from dirsort.utils import count_files, get_disk_usage, get_size_str


class TestUtils:
    def test_get_size_str_bytes(self):
        """验证 get_size_str 返回 B 单位。"""
        with tempfile.NamedTemporaryFile() as f:
            f.write(b"hello")
            f.flush()
            size = get_size_str(Path(f.name))
            assert "B" in size

    def test_get_size_str_kb(self):
        """验证 get_size_str 返回 KB 单位（>1KB 时）。"""
        with tempfile.NamedTemporaryFile() as f:
            data = b"x" * 1500  # 1.5KB
            f.write(data)
            f.flush()
            size = get_size_str(Path(f.name))
            assert "KB" in size

    def test_count_files_empty_dir(self):
        """验证空目录统计为 0。"""
        with tempfile.TemporaryDirectory() as tmp:
            assert count_files(Path(tmp)) == 0

    def test_count_files_with_files(self):
        """验证目录中的文件计数。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "a.txt").touch()
            (p / "b.txt").touch()
            (p / "subdir").mkdir()
            assert count_files(p) == 2  # 只统计文件，不统计目录

    def test_get_disk_usage(self):
        """验证磁盘空间统计。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "a.txt").write_text("x" * 100)
            (p / "b.txt").write_text("x" * 200)
            total = get_disk_usage(p)
            assert total >= 300  # 至少 300 字节


class TestUtilsV3:
    """测试 Round 3 新增工具函数。"""

    def test_format_bytes_bytes(self):
        """验证 format_bytes B 单位。"""
        from dirsort.utils import format_bytes
        assert format_bytes(500) == "500.0 B"

    def test_format_bytes_kb(self):
        """验证 format_bytes KB 单位。"""
        from dirsort.utils import format_bytes
        assert "KB" in format_bytes(2048)

    def test_format_bytes_mb(self):
        """验证 format_bytes MB 单位。"""
        from dirsort.utils import format_bytes
        assert "MB" in format_bytes(1048576)

    def test_format_json_output_basic(self):
        """验证 format_json_output 基本输出。"""
        from dirsort.utils import format_json_output
        data = {"name": "test", "value": 42}
        result = format_json_output(data)
        assert '"name": "test"' in result
        assert '"value": 42' in result

    def test_format_json_output_unicode(self):
        """验证 format_json_output 中文不转义。"""
        from dirsort.utils import format_json_output
        data = {"message": "你好世界"}
        result = format_json_output(data)
        assert "你好世界" in result  # 中文不应被转义
        assert "\\u" not in result

