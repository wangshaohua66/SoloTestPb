"""
文件整理核心模块
负责扫描文件、移动文件到目标目录，并记录移动历史
"""

import os
import shutil
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from .file_classifier import FileClassifier


class FileOrganizer:
    """
    文件整理器类
    负责执行文件整理操作，包括扫描、分类、移动和历史记录
    """

    def __init__(
        self,
        source_dir: str,
        classifier: FileClassifier,
        move_history_file: Optional[str] = None,
        recursive: bool = False,
        flatten: bool = False
    ):
        """
        初始化文件整理器

        Args:
            source_dir: 源目录路径
            classifier: 文件分类器实例
            move_history_file: 移动历史记录文件路径
            recursive: 是否递归处理子目录
            flatten: 是否扁平化整理（True时所有文件直接放到分类目录，不保持子目录结构）
        """
        self.source_dir = os.path.abspath(source_dir)
        self.classifier = classifier
        self.recursive = recursive
        self.flatten = flatten
        
        if move_history_file is None:
            move_history_file = os.path.join(self.source_dir, ".folderorg_history.json")
        
        self.move_history_file = move_history_file
        self._ensure_history_dir_exists()
        self.move_history: List[Dict[str, Any]] = []
        self._load_move_history()

    def _ensure_history_dir_exists(self) -> bool:
        """
        确保历史记录目录存在

        Returns:
            True如果成功创建或目录已存在，False如果权限不足
        """
        history_dir = os.path.dirname(self.move_history_file)
        if not history_dir:
            return True
        try:
            os.makedirs(history_dir, exist_ok=True)
            return True
        except (PermissionError, OSError) as e:
            print(f"警告: 无法创建历史记录目录 {history_dir}: {e}")
            return False

    def _load_move_history(self) -> bool:
        """
        从文件加载移动历史记录

        Returns:
            True如果成功加载（或文件不存在），False如果加载时出错
        """
        import json
        if not os.path.exists(self.move_history_file):
            self.move_history = []
            return True
        try:
            with open(self.move_history_file, "r", encoding="utf-8") as f:
                self.move_history = json.load(f)
            return True
        except (json.JSONDecodeError, IOError, OSError) as e:
            print(f"警告: 无法加载历史记录文件 {self.move_history_file}: {e}")
            self.move_history = []
            return False

    def _save_move_history(self) -> bool:
        """
        保存移动历史记录到文件

        Returns:
            True如果成功保存，False如果权限不足或出错
        """
        import json
        try:
            history_dir = os.path.dirname(self.move_history_file)
            if history_dir:
                os.makedirs(history_dir, exist_ok=True)
            with open(self.move_history_file, "w", encoding="utf-8") as f:
                json.dump(self.move_history, f, ensure_ascii=False, indent=4)
            return True
        except (PermissionError, OSError, IOError) as e:
            print(f"警告: 无法保存历史记录到 {self.move_history_file}: {e}")
            return False

    def _add_to_history(
        self,
        source_path: str,
        target_path: str,
        category: str,
        timestamp: Optional[str] = None
    ) -> None:
        """
        添加移动记录到历史

        Args:
            source_path: 源文件路径
            target_path: 目标文件路径
            category: 文件分类
            timestamp: 时间戳，如果为None则使用当前时间
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        self.move_history.append({
            "source_path": source_path,
            "target_path": target_path,
            "category": category,
            "timestamp": timestamp
        })
        self._save_move_history()

    def scan_files(self) -> List[str]:
        """
        扫描源目录中的所有文件

        Returns:
            文件路径列表
        """
        files = []
        if not os.path.exists(self.source_dir):
            return files
        
        if self.recursive:
            for root, _, filenames in os.walk(self.source_dir):
                for filename in filenames:
                    if filename == ".folderorg_history.json":
                        continue
                    file_path = os.path.join(root, filename)
                    files.append(file_path)
        else:
            for item in os.listdir(self.source_dir):
                if item == ".folderorg_history.json":
                    continue
                item_path = os.path.join(self.source_dir, item)
                if os.path.isfile(item_path):
                    files.append(item_path)
        
        return files

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

    def move_file(self, file_path: str, flatten: Optional[bool] = None) -> Tuple[bool, Optional[str], str]:
        """
        移动单个文件到对应分类目录

        Args:
            file_path: 要移动的文件路径
            flatten: 是否扁平化整理，None时使用初始化时的设置

        Returns:
            元组 (是否成功, 目标路径, 分类名称)
        """
        if flatten is None:
            flatten = self.flatten
            
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return False, None, ""
        
        file_path = os.path.abspath(file_path)
        
        category, target_dir_name = self.classifier.classify_file(file_path)
        
        if target_dir_name is None:
            return False, None, category
        
        relative_path = os.path.relpath(file_path, self.source_dir)
        relative_dir = os.path.dirname(relative_path)
        filename = os.path.basename(file_path)
        
        base_target_dir = os.path.join(self.source_dir, target_dir_name)
        
        if flatten:
            target_dir = base_target_dir
        else:
            if relative_dir and relative_dir != ".":
                target_dir = os.path.join(base_target_dir, relative_dir)
            else:
                target_dir = base_target_dir
        
        os.makedirs(target_dir, exist_ok=True)
        
        target_path = os.path.join(target_dir, filename)
        target_path = self._generate_unique_path(target_path)
        
        try:
            shutil.move(file_path, target_path)
            self._add_to_history(file_path, target_path, category)
            return True, target_path, category
        except (shutil.Error, IOError, OSError):
            return False, None, category

    def organize(self, recursive: Optional[bool] = None, flatten: Optional[bool] = None) -> Dict[str, Any]:
        """
        执行完整的文件整理操作

        Args:
            recursive: 是否递归处理子目录，如果为None则使用初始化时的设置
            flatten: 是否扁平化整理，如果为None则使用初始化时的设置

        Returns:
            整理结果字典，包含统计信息
        """
        if recursive is not None:
            self.recursive = recursive
        if flatten is not None:
            self.flatten = flatten
        
        start_time = time.time()
        files = self.scan_files()
        total_files = len(files)
        moved_files = 0
        failed_files = 0
        category_stats: Dict[str, int] = {}
        moved_paths: List[Dict[str, str]] = []
        
        for file_path in files:
            success, target_path, category = self.move_file(file_path, flatten=self.flatten)
            
            if success:
                moved_files += 1
                moved_paths.append({
                    "source": file_path,
                    "target": target_path,
                    "category": category
                })
            else:
                failed_files += 1
            
            if category:
                if category not in category_stats:
                    category_stats[category] = 0
                if success:
                    category_stats[category] += 1
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        return {
            "total_files": total_files,
            "moved_files": moved_files,
            "failed_files": failed_files,
            "category_stats": category_stats,
            "moved_paths": moved_paths,
            "elapsed_time": elapsed_time,
            "recursive": self.recursive,
            "timestamp": datetime.now().isoformat()
        }

    def get_move_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取移动历史记录

        Args:
            limit: 返回记录的数量限制（从最新的开始），None表示返回全部

        Returns:
            移动历史记录列表
        """
        if limit is not None:
            return self.move_history[-limit:]
        return self.move_history.copy()

    def clear_history(self) -> None:
        """
        清空移动历史记录
        """
        self.move_history = []
        self._save_move_history()

    def cleanup_invalid_history(
        self,
        mode: str = "conservative",
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        清理无效的历史记录

        Args:
            mode: 清理模式
                - "conservative": 保守模式，只清理格式不完整的记录（保护还原功能）
                - "aggressive": 激进模式，清理格式不完整和目标文件不存在的记录
            dry_run: 是否为预览模式，True时只返回结果不实际执行

        Returns:
            清理结果字典，包含清理的记录数量和详情
        """
        valid_history = []
        invalid_records = []
        invalid_reasons = []
        
        for entry in self.move_history:
            target_path = entry.get("target_path", "")
            source_path = entry.get("source_path", "")
            category = entry.get("category", "")
            timestamp = entry.get("timestamp", "")
            
            is_valid = True
            reason = ""
            
            if not (target_path and source_path and category and timestamp):
                is_valid = False
                reason = "格式不完整"
            elif mode == "aggressive":
                if not os.path.exists(target_path) or not os.path.isfile(target_path):
                    is_valid = False
                    reason = f"目标文件不存在: {target_path}"
            
            if is_valid:
                valid_history.append(entry)
            else:
                invalid_records.append(entry)
                invalid_reasons.append(reason)
        
        invalid_count = len(invalid_records)
        
        if invalid_count > 0 and not dry_run:
            self.move_history = valid_history
            self._save_move_history()
        
        return {
            "total_records": len(self.move_history) + invalid_count if not dry_run else len(self.move_history),
            "cleaned_records": invalid_count,
            "remaining_records": len(self.move_history) if not dry_run else len(self.move_history) - invalid_count,
            "mode": mode,
            "dry_run": dry_run,
            "invalid_reasons": invalid_reasons[:10],
            "invalid_records_count": invalid_count
        }
