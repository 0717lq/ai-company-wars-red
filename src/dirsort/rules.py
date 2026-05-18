"""文件分类规则配置 — 后缀映射到类别。"""

# 默认分类规则：文件后缀 → 类别名
DEFAULT_RULES: dict[str, str] = {
    # 图片
    ".jpg": "图片",
    ".jpeg": "图片",
    ".png": "图片",
    ".gif": "图片",
    ".bmp": "图片",
    ".svg": "图片",
    ".webp": "图片",
    ".ico": "图片",
    ".tiff": "图片",
    ".heic": "图片",
    # 文档
    ".pdf": "文档",
    ".doc": "文档",
    ".docx": "文档",
    ".xls": "文档",
    ".xlsx": "文档",
    ".ppt": "文档",
    ".pptx": "文档",
    ".txt": "文档",
    ".csv": "文档",
    ".md": "文档",
    ".epub": "文档",
    # 视频
    ".mp4": "视频",
    ".avi": "视频",
    ".mkv": "视频",
    ".mov": "视频",
    ".wmv": "视频",
    ".flv": "视频",
    ".webm": "视频",
    ".m4v": "视频",
    # 音频
    ".mp3": "音频",
    ".wav": "音频",
    ".flac": "音频",
    ".aac": "音频",
    ".ogg": "音频",
    ".wma": "音频",
    ".m4a": "音频",
    # 代码
    ".py": "代码",
    ".js": "代码",
    ".ts": "代码",
    ".jsx": "代码",
    ".tsx": "代码",
    ".java": "代码",
    ".cpp": "代码",
    ".c": "代码",
    ".h": "代码",
    ".hpp": "代码",
    ".go": "代码",
    ".rs": "代码",
    ".rb": "代码",
    ".php": "代码",
    ".swift": "代码",
    ".kt": "代码",
    ".sql": "代码",
    ".sh": "代码",
    ".bash": "代码",
    ".yaml": "代码",
    ".yml": "代码",
    ".json": "代码",
    ".xml": "代码",
    ".toml": "代码",
    ".css": "代码",
    ".scss": "代码",
    ".less": "代码",
    ".html": "代码",
    ".vue": "代码",
    # 压缩包
    ".zip": "压缩包",
    ".tar": "压缩包",
    ".gz": "压缩包",
    ".bz2": "压缩包",
    ".7z": "压缩包",
    ".rar": "压缩包",
    ".xz": "压缩包",
    # 可执行程序
    ".exe": "程序",
    ".msi": "程序",
    ".app": "程序",
    ".dmg": "程序",
    ".deb": "程序",
    ".rpm": "程序",
    ".apk": "程序",
    # 设计文件
    ".psd": "设计文件",
    ".ai": "设计文件",
    ".sketch": "设计文件",
    ".fig": "设计文件",
    ".xd": "设计文件",
    # 字体
    ".ttf": "字体",
    ".otf": "字体",
    ".woff": "字体",
    ".woff2": "字体",
}


def classify(filename: str, rules: dict[str, str] | None = None) -> str:
    """根据文件名和规则返回分类名称。

    Args:
        filename: 文件名（带后缀）
        rules: 分类规则字典，默认使用 DEFAULT_RULES

    Returns:
        分类名称，无法识别时返回"其他"
    """
    if rules is None:
        rules = DEFAULT_RULES

    # 提取后缀（小写）
    dot_index = filename.rfind(".")
    if dot_index == -1:
        return "其他"

    ext = filename[dot_index:].lower()
    return rules.get(ext, "其他")


def get_all_categories(rules: dict[str, str] | None = None) -> list[str]:
    """获取所有分类名称列表（去重）。"""
    if rules is None:
        rules = DEFAULT_RULES
    return sorted(set(rules.values())) + ["其他"]
