"""
文件类型识别模块
负责根据文件扩展名识别文件类型并匹配到对应的分类
"""

import os
from typing import Dict, List, Optional, Tuple


class FileClassifier:
    """
    文件分类器类
    根据文件扩展名和配置的分类规则，将文件分类到相应的类别
    """

    def __init__(self, categories: Dict[str, Dict]):
        """
        初始化文件分类器

        Args:
            categories: 分类配置字典，格式为 {category_name: {extensions: [...], target_dir: ...}}
        """
        self.categories = categories
        self._extension_map = self._build_extension_map()

    def _build_extension_map(self) -> Dict[str, str]:
        """
        构建扩展名到分类名称的映射表

        Returns:
            扩展名映射表，格式为 {extension: category_name}
        """
        extension_map = {}
        for category_name, category_config in self.categories.items():
            extensions = category_config.get("extensions", [])
            for ext in extensions:
                ext_lower = ext.lower()
                if ext_lower not in extension_map:
                    extension_map[ext_lower] = category_name
        return extension_map

    def get_file_extension(self, file_path: str) -> str:
        """
        获取文件的扩展名

        Args:
            file_path: 文件路径

        Returns:
            小写的文件扩展名，包含点号（如 .pdf）
        """
        _, ext = os.path.splitext(file_path)
        return ext.lower()

    def classify_file(self, file_path: str) -> Tuple[str, Optional[str]]:
        """
        分类文件

        Args:
            file_path: 文件路径

        Returns:
            元组 (分类名称, 目标目录路径)
            如果未匹配到任何分类，则返回 ("others", others的目标目录)
        """
        ext = self.get_file_extension(file_path)
        
        if ext in self._extension_map:
            category_name = self._extension_map[ext]
            target_dir = self.categories[category_name].get("target_dir", category_name)
            return category_name, target_dir
        
        others_config = self.categories.get("others", {})
        target_dir = others_config.get("target_dir", "Others")
        return "others", target_dir

    def get_category_target_dir(self, category_name: str) -> Optional[str]:
        """
        获取指定分类的目标目录

        Args:
            category_name: 分类名称

        Returns:
            目标目录名称，如果分类不存在则返回None
        """
        if category_name in self.categories:
            return self.categories[category_name].get("target_dir", category_name)
        return None

    def list_categories(self) -> List[str]:
        """
        列出所有可用的分类

        Returns:
            分类名称列表
        """
        return list(self.categories.keys())

    def get_category_extensions(self, category_name: str) -> List[str]:
        """
        获取指定分类的所有扩展名

        Args:
            category_name: 分类名称

        Returns:
            扩展名列表，如果分类不存在则返回空列表
        """
        if category_name in self.categories:
            return self.categories[category_name].get("extensions", [])
        return []

    def is_extension_in_category(self, extension: str, category_name: str) -> bool:
        """
        检查扩展名是否属于指定分类

        Args:
            extension: 文件扩展名
            category_name: 分类名称

        Returns:
            是否属于该分类
        """
        extensions = self.get_category_extensions(category_name)
        return extension.lower() in [ext.lower() for ext in extensions]

    def update_categories(self, categories: Dict[str, Dict]) -> None:
        """
        更新分类配置

        Args:
            categories: 新的分类配置字典
        """
        self.categories = categories
        self._extension_map = self._build_extension_map()
