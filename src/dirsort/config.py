"""配置文件系统 — 加载 YAML 格式的自定义分类规则。"""
import os
from pathlib import Path
from typing import Any

from .rules import DEFAULT_RULES, classify as default_classify

# 默认配置路径
DEFAULT_CONFIG_DIR = Path.home() / ".config" / "dirsort"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "rules.yaml"


def load_config(config_path: str | Path | None = None) -> dict[str, str] | None:
    """加载 YAML 配置文件，返回自定义分类规则。

    Args:
        config_path: 用户指定的配置路径。为 None 时自动检测默认路径。

    Returns:
        自定义规则字典 {后缀: 分类名}，如果文件不存在或配置无效返回 None。
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_FILE

    config_path = Path(config_path)
    if not config_path.exists():
        return None

    try:
        import yaml

        with open(config_path, "r", encoding="utf-8") as f:
            data: dict[str, Any] = yaml.safe_load(f)

        if not isinstance(data, dict) or "rules" not in data:
            return None

        rules: dict[str, str] = {}
        for rule in data["rules"]:
            pattern = rule.get("pattern", "")
            category = rule.get("category", "其他")

            # 将 glob 模式（如 "*.pdf"）转为后缀映射
            if pattern.startswith("*."):
                ext = pattern[1:].lower()  # ".pdf"
                rules[ext] = category
            else:
                # 直接匹配文件名
                rules[pattern.lower()] = category

        return rules
    except Exception:
        # YAML 解析失败时静默降级，使用默认规则
        return None


def get_merged_rules(config_path: str | Path | None = None) -> dict[str, str]:
    """获取合并后的分类规则：自定义规则优先，默认规则作为 fallback。

    Args:
        config_path: 可选的配置文件路径

    Returns:
        合并后的规则字典
    """
    custom_rules = load_config(config_path)
    if custom_rules is None:
        return dict(DEFAULT_RULES)

    # 自定义规则优先，缺失的后缀用默认规则补充
    merged = dict(DEFAULT_RULES)
    merged.update(custom_rules)
    return merged
