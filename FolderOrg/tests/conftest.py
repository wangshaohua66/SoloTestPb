"""
pytest 测试配置和夹具
"""

import os
import tempfile
import shutil
from typing import Generator, Dict, Any

import pytest


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """
    创建临时目录，测试完成后自动清理

    Yields:
        临时目录路径
    """
    temp_path = tempfile.mkdtemp(prefix="folder_org_test_")
    try:
        yield temp_path
    finally:
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)


@pytest.fixture
def test_categories() -> Dict[str, Dict[str, Any]]:
    """
    提供测试用的分类配置

    Returns:
        分类配置字典
    """
    return {
        "documents": {
            "extensions": [".pdf", ".doc", ".docx", ".txt"],
            "target_dir": "Documents"
        },
        "images": {
            "extensions": [".jpg", ".png", ".gif"],
            "target_dir": "Images"
        },
        "videos": {
            "extensions": [".mp4", ".avi"],
            "target_dir": "Videos"
        },
        "audio": {
            "extensions": [".mp3", ".wav"],
            "target_dir": "Audio"
        },
        "others": {
            "extensions": [],
            "target_dir": "Others"
        }
    }


@pytest.fixture
def test_files(temp_dir: str) -> Dict[str, str]:
    """
    在临时目录中创建测试文件

    Args:
        temp_dir: 临时目录路径

    Returns:
        文件路径字典，格式为 {文件名: 完整路径}
    """
    files = {
        "report.pdf": os.path.join(temp_dir, "report.pdf"),
        "image.jpg": os.path.join(temp_dir, "image.jpg"),
        "video.mp4": os.path.join(temp_dir, "video.mp4"),
        "song.mp3": os.path.join(temp_dir, "song.mp3"),
        "unknown.xyz": os.path.join(temp_dir, "unknown.xyz"),
        "notes.txt": os.path.join(temp_dir, "notes.txt")
    }
    
    for file_path in files.values():
        with open(file_path, "w") as f:
            f.write("test content")
    
    return files
