"""测试 UndoManager 的边缘情况。"""
import tempfile
from pathlib import Path

from dirsort.undo import UndoManager


class TestUndoManagerEdgeCases:
    def test_rollback_by_directory(self):
        """验证按指定目录回滚。"""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            undo_dir = base / ".dirsort"
            mgr = UndoManager(undo_dir=undo_dir)

            # 创建两次不同目录的整理记录
            src_a = base / "dir_a"
            src_b = base / "dir_b"
            src_a.mkdir()
            src_b.mkdir()

            file_a = src_a / "a.txt"
            file_a.touch()
            file_b = src_b / "b.txt"
            file_b.touch()

            target_dir = base / "文档"
            target_dir.mkdir()

            moved_a = target_dir / "a.txt"
            moved_b = target_dir / "b.txt"
            file_a.rename(moved_a)
            file_b.rename(moved_b)

            mgr.record(src_a, [(src_a / "a.txt", moved_a)])
            mgr.record(src_b, [(src_b / "b.txt", moved_b)])

            # 回滚 dir_a 的记录
            count = mgr.rollback(src_a)
            assert count == 1
            assert (src_a / "a.txt").exists()
            # dir_b 的记录应保留
            assert len(mgr.list_history()) == 1

    def test_rollback_with_nonexistent_dir(self):
        """验证回滚不存在的目录。"""
        with tempfile.TemporaryDirectory() as tmp:
            undo_dir = Path(tmp) / ".dirsort"
            mgr = UndoManager(undo_dir=undo_dir)
            count = mgr.rollback(Path("/nonexistent/path"))
            assert count == 0

    def test_record_limit(self):
        """验证记录数限制（最多 20 条）。"""
        with tempfile.TemporaryDirectory() as tmp:
            undo_dir = Path(tmp) / ".dirsort"
            mgr = UndoManager(undo_dir=undo_dir)

            # 创建 25 条记录
            for i in range(25):
                s = Path(f"/tmp/dir_{i}")
                mgr.record(s, [(s / f"f{i}.txt", Path(f"/tmp/文档/f{i}.txt"))])

            history = mgr.list_history()
            assert len(history) == 20

    def test_corrupted_history(self):
        """验证损坏的 history 文件可以优雅处理。"""
        with tempfile.TemporaryDirectory() as tmp:
            undo_dir = Path(tmp) / ".dirsort"
            undo_dir.mkdir()
            history_file = undo_dir / "history.json"
            history_file.write_text("not valid json{", encoding="utf-8")

            mgr = UndoManager(undo_dir=undo_dir)
            assert mgr.list_history() == []

    def test_rollback_source_not_found(self):
        """验证回滚时源目录已被删除的情况。"""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            undo_dir = base / ".dirsort"
            mgr = UndoManager(undo_dir=undo_dir)

            # 记录一个移动，但目标文件已被删除
            mgr.record(
                base / "src",
                [(base / "src" / "f.txt", base / "文档" / "f.txt")],
            )

            # 回滚（文件不存在，应跳过）
            count = mgr.rollback(base / "src")
            assert count == 0
