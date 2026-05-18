"""测试 UndoManager 和回滚逻辑。"""
import tempfile
from pathlib import Path

from dirsort.undo import UndoManager


class TestUndoManager:
    def test_record_and_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            undo_dir = Path(tmp) / ".dirsort"
            mgr = UndoManager(undo_dir=undo_dir)
            moves = [
                (Path("/tmp/a.txt"), Path("/tmp/文档/a.txt")),
                (Path("/tmp/b.jpg"), Path("/tmp/图片/b.jpg")),
            ]
            mgr.record(Path("/tmp"), moves)
            history = mgr.list_history()
            assert len(history) == 1
            assert history[0]["source_dir"] == "/tmp"
            assert len(history[0]["moves"]) == 2

    def test_list_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            undo_dir = Path(tmp) / ".dirsort"
            mgr = UndoManager(undo_dir=undo_dir)
            assert mgr.list_history() == []

    def test_multiple_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            undo_dir = Path(tmp) / ".dirsort"
            mgr = UndoManager(undo_dir=undo_dir)
            mgr.record(Path("/a"), [(Path("/a/f1.txt"), Path("/a/文档/f1.txt"))])
            mgr.record(Path("/b"), [(Path("/b/f2.jpg"), Path("/b/图片/f2.jpg"))])
            assert len(mgr.list_history()) == 2

    def test_rollback_actual_files(self):
        # 测试实际文件移动然后回滚
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            src_dir = base / "source"
            src_dir.mkdir()
            target_dir = base / "target"
            target_dir.mkdir()

            undo_dir = base / ".dirsort"
            mgr = UndoManager(undo_dir=undo_dir)

            # 创建文件、移动、记录
            test_file = src_dir / "test.txt"
            test_file.write_text("hello")
            moved_file = target_dir / "test.txt"
            test_file.rename(moved_file)

            moves = [(src_dir / "test.txt", moved_file)]
            mgr.record(src_dir, moves)

            # 回滚
            count = mgr.rollback(src_dir)
            assert count == 1
            assert (src_dir / "test.txt").exists()
            assert not (target_dir / "test.txt").exists()
