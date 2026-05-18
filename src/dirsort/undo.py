"""回滚功能 — 记录整理操作用于撤销。"""
import json
from datetime import datetime
from pathlib import Path

UNDO_DIR = Path.home() / ".dirsort"
HISTORY_FILE = UNDO_DIR / "history.json"


class UndoManager:
    """管理整理操作的撤销和记录。"""

    def __init__(self, undo_dir: Path | None = None):
        self.undo_dir = undo_dir or UNDO_DIR
        self.undo_dir.mkdir(parents=True, exist_ok=True)

    def record(self, source_dir: Path, moves: list[tuple[Path, Path]]):
        """记录一次整理操作。

        Args:
            source_dir: 被整理的目录
            moves: [(原路径, 新路径)] 列表（原路径 = 移动前的位置）
        """
        records = self._load_history()

        entry = {
            "timestamp": datetime.now().isoformat(),
            "source_dir": str(source_dir),
            "moves": [
                {"from": str(src), "to": str(dst)} for src, dst in moves
            ],
        }
        records.append(entry)

        # 只保留最近 20 条记录
        if len(records) > 20:
            records = records[-20:]

        self._save_history(records)

    def rollback(self, source_dir: Path | None = None) -> int:
        """回滚整理操作。

        Args:
            source_dir: 指定要回滚的目录，None 则回滚最近一次

        Returns:
            回滚的文件数量
        """
        records = self._load_history()
        if not records:
            return 0

        if source_dir is None:
            # 回滚最近一次
            target = records.pop()
        else:
            # 找到指定目录的最近记录
            src_str = str(source_dir)
            idx = -1
            for i in range(len(records) - 1, -1, -1):
                if records[i]["source_dir"] == src_str:
                    idx = i
                    break
            if idx == -1:
                return 0
            target = records.pop(idx)

        count = 0
        for move in reversed(target["moves"]):
            dst = Path(move["to"])
            src = Path(move["from"])

            if dst.exists():
                # 确保原目录存在
                src.parent.mkdir(parents=True, exist_ok=True)
                dst.rename(src)
                count += 1

        self._save_history(records)
        return count

    def list_history(self) -> list[dict]:
        """列出所有整理历史。"""
        return self._load_history()

    def _load_history(self) -> list[dict]:
        history_file = self.undo_dir / "history.json"
        if history_file.exists():
            try:
                data = history_file.read_text(encoding="utf-8")
                return json.loads(data) if data.strip() else []
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def _save_history(self, records: list[dict]):
        history_file = self.undo_dir / "history.json"
        history_file.parent.mkdir(parents=True, exist_ok=True)
        history_file.write_text(
            json.dumps(records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
