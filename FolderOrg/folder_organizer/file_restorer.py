"""
文件还原模块
负责将之前移动的文件还原到原位置
"""

import os
import shutil
from typing import Dict, List, Optional, Any


class FileRestorer:
    """
    文件还原器类
    负责根据移动历史记录将文件还原到原位置
    """

    def __init__(self, move_history: List[Dict[str, Any]]):
        """
        初始化文件还原器

        Args:
            move_history: 移动历史记录列表
        """
        self.move_history = move_history

    def _generate_unique_path(self, target_path: str) -> str:
        """
        生成唯一的目标路径（避免文件覆盖）

        Args:
            target_path: 原始目标路径

        Returns:
            唯一的目标路径
        """
        if not os.path.exists(target_path):
            return target_path
        
        base_dir, filename = os.path.split(target_path)
        name, ext = os.path.splitext(filename)
        counter = 1
        
        while True:
            new_filename = f"{name}_{counter}{ext}"
            new_path = os.path.join(base_dir, new_filename)
            if not os.path.exists(new_path):
                return new_path
            counter += 1

    def restore_file(self, history_entry: Dict[str, Any]) -> bool:
        """
        还原单个文件

        Args:
            history_entry: 历史记录条目，包含 source_path 和 target_path

        Returns:
            是否成功还原
        """
        target_path = history_entry.get("target_path", "")
        source_path = history_entry.get("source_path", "")
        
        if not os.path.exists(target_path) or not os.path.isfile(target_path):
            return False
        
        source_dir = os.path.dirname(source_path)
        os.makedirs(source_dir, exist_ok=True)
        
        restore_path = self._generate_unique_path(source_path)
        
        try:
            shutil.move(target_path, restore_path)
            return True
        except (shutil.Error, IOError, OSError):
            return False

    def restore_last(self, count: int = 1) -> Dict[str, Any]:
        """
        还原最近移动的文件

        Args:
            count: 要还原的文件数量

        Returns:
            还原结果字典，包含成功和失败的数量
        """
        entries_to_restore = self.move_history[-count:] if count > 0 else []
        success_count = 0
        failed_count = 0
        restored_files: List[Dict[str, str]] = []
        
        for entry in reversed(entries_to_restore):
            if self.restore_file(entry):
                success_count += 1
                restored_files.append({
                    "source": entry.get("target_path", ""),
                    "target": entry.get("source_path", ""),
                    "category": entry.get("category", "")
                })
            else:
                failed_count += 1
        
        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "restored_files": restored_files
        }

    def restore_by_category(self, category: str) -> Dict[str, Any]:
        """
        还原指定分类的所有文件

        Args:
            category: 文件分类名称

        Returns:
            还原结果字典
        """
        entries_to_restore = [
            entry for entry in self.move_history
            if entry.get("category", "") == category
        ]
        
        success_count = 0
        failed_count = 0
        restored_files: List[Dict[str, str]] = []
        
        for entry in entries_to_restore:
            if self.restore_file(entry):
                success_count += 1
                restored_files.append({
                    "source": entry.get("target_path", ""),
                    "target": entry.get("source_path", ""),
                    "category": entry.get("category", "")
                })
            else:
                failed_count += 1
        
        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "restored_files": restored_files
        }

    def restore_all(self) -> Dict[str, Any]:
        """
        还原所有文件

        Returns:
            还原结果字典
        """
        success_count = 0
        failed_count = 0
        restored_files: List[Dict[str, str]] = []
        
        for entry in self.move_history:
            if self.restore_file(entry):
                success_count += 1
                restored_files.append({
                    "source": entry.get("target_path", ""),
                    "target": entry.get("source_path", ""),
                    "category": entry.get("category", "")
                })
            else:
                failed_count += 1
        
        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "restored_files": restored_files
        }

    def get_restore_history(self) -> List[Dict[str, Any]]:
        """
        获取可还原的历史记录

        Returns:
            可还原的历史记录列表
        """
        restorable = []
        for entry in self.move_history:
            target_path = entry.get("target_path", "")
            if os.path.exists(target_path) and os.path.isfile(target_path):
                restorable.append(entry)
        return restorable

    def update_history(self, move_history: List[Dict[str, Any]]) -> None:
        """
        更新移动历史记录

        Args:
            move_history: 新的移动历史记录列表
        """
        self.move_history = move_history
