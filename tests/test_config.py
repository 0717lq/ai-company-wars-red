"""测试配置文件系统。"""
import tempfile
from pathlib import Path

from dirsort.config import load_config, get_merged_rules
from dirsort.rules import DEFAULT_RULES


class TestConfig:
    def test_load_nonexistent_config(self):
        """验证不存在的配置文件返回 None。"""
        result = load_config("/nonexistent/path/rules.yaml")
        assert result is None

    def test_load_valid_yaml(self):
        """验证加载有效的 YAML 配置文件。"""
        with tempfile.TemporaryDirectory() as tmp:
            config_file = Path(tmp) / "rules.yaml"
            config_file.write_text(
                "rules:\n"
                "  - pattern: \"*.pdf\"\n"
                "    category: \"Documents/PDFs\"\n"
                "  - pattern: \"*.jpg\"\n"
                "    category: \"My Images\"\n"
            )
            rules = load_config(str(config_file))
            assert rules is not None
            assert rules[".pdf"] == "Documents/PDFs"
            assert rules[".jpg"] == "My Images"

    def test_load_empty_config(self):
        """验证空配置（rules: []）返回空字典。"""
        with tempfile.TemporaryDirectory() as tmp:
            config_file = Path(tmp) / "rules.yaml"
            config_file.write_text("rules: []\n")
            rules = load_config(str(config_file))
            # 空的 rules 列表是有效配置，返回空字典
            assert rules == {}

    def test_load_invalid_yaml(self):
        """验证无效 YAML 返回 None（静默降级）。"""
        with tempfile.TemporaryDirectory() as tmp:
            config_file = Path(tmp) / "rules.yaml"
            config_file.write_text("invalid: [yaml: broken")
            rules = load_config(str(config_file))
            assert rules is None

    def test_load_missing_rules_key(self):
        """验证缺少 rules 键的配置返回 None。"""
        with tempfile.TemporaryDirectory() as tmp:
            config_file = Path(tmp) / "rules.yaml"
            config_file.write_text("something_else: true\n")
            rules = load_config(str(config_file))
            assert rules is None

    def test_load_glob_patterns(self):
        """验证 glob 格式的 pattern 正确解析。"""
        with tempfile.TemporaryDirectory() as tmp:
            config_file = Path(tmp) / "rules.yaml"
            config_file.write_text(
                "rules:\n"
                "  - pattern: \"*.md\"\n"
                "    category: \"Markdown\"\n"
                "  - pattern: \"*.tar.gz\"\n"
                "    category: \"Archives\"\n"
            )
            rules = load_config(str(config_file))
            assert rules is not None
            assert rules[".md"] == "Markdown"
            assert rules[".tar.gz"] == "Archives"

    def test_get_merged_rules_no_config(self):
        """验证没有配置时使用默认规则。"""
        merged = get_merged_rules("/nonexistent/path/rules.yaml")
        assert merged == DEFAULT_RULES

    def test_get_merged_rules_with_custom(self):
        """验证自定义规则覆盖默认规则。"""
        with tempfile.TemporaryDirectory() as tmp:
            config_file = Path(tmp) / "rules.yaml"
            config_file.write_text(
                "rules:\n"
                "  - pattern: \"*.py\"\n"
                "    category: \"Python Scripts\"\n"
            )
            merged = get_merged_rules(str(config_file))
            # .py 应使用自定义分类
            assert merged[".py"] == "Python Scripts"
            # 其他后缀仍保留默认规则
            assert merged[".jpg"] == "图片"
            assert merged[".pdf"] == "文档"

    def test_get_merged_rules_new_extension(self):
        """验证自定义规则可以添加新的后缀映射。"""
        with tempfile.TemporaryDirectory() as tmp:
            config_file = Path(tmp) / "rules.yaml"
            config_file.write_text(
                "rules:\n"
                "  - pattern: \"*.abc\"\n"
                "    category: \"Custom\"\n"
            )
            merged = get_merged_rules(str(config_file))
            assert merged[".abc"] == "Custom"
            assert merged[".jpg"] == "图片"  # 默认规则保留
