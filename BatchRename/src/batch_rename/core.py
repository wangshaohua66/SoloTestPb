"""
批量文件重命名核心模块
包含所有重命名策略和BatchRenamer主类
"""

import os
import re
import json
import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
from pathlib import Path


class RenameStrategy(ABC):
    """
    重命名策略抽象基类
    定义所有重命名策略的公共接口
    """

    @abstractmethod
    def generate_new_name(self, old_name: str, index: int) -> str:
        """
        根据策略生成新文件名
        
        Args:
            old_name: 原始文件名
            index: 文件在列表中的索引
            
        Returns:
            新文件名(包含扩展名)
        """
        pass


class SequenceRenameStrategy(RenameStrategy):
    """
    按序号重命名策略
    格式: {name}_{填充序号}.{扩展名}
    例如: file_001.txt, file_002.txt
    """

    def __init__(self, name: str, start: int = 1, padding: int = 3):
        """
        初始化序列重命名策略
        
        Args:
            name: 基础名称
            start: 起始序号，默认为1
            padding: 序号填充位数，默认为3位
        """
        self.name = name
        self.start = start
        self.padding = padding

    def generate_new_name(self, old_name: str, index: int) -> str:
        """
        生成带有序号的新文件名
        
        Args:
            old_name: 原始文件名
            index: 文件在列表中的索引
            
        Returns:
            新文件名
        """
        path = Path(old_name)
        stem = path.stem
        suffix = path.suffix
        sequence = self.start + index
        sequence_str = str(sequence).zfill(self.padding)
        new_stem = f"{self.name}_{sequence_str}"
        new_name = new_stem + suffix
        return new_name


class TimestampRenameStrategy(RenameStrategy):
    """
    按日期时间戳重命名策略
    格式: {时间戳}_{序号}.{扩展名} 或自定义格式
    """

    def __init__(self, timestamp: Optional[datetime.datetime] = None,
                 format_str: str = "%Y%m%d_%H%M%S"):
        """
        初始化时间戳重命名策略
        
        Args:
            timestamp: 指定的时间戳，默认为当前时间
            format_str: 时间格式字符串，默认为"%Y%m%d_%H%M%S"
        """
        self.timestamp = timestamp if timestamp else datetime.datetime.now()
        self.format_str = format_str

    def generate_new_name(self, old_name: str, index: int) -> str:
        """
        生成带有时间戳的新文件名
        
        Args:
            old_name: 原始文件名
            index: 文件在列表中的索引
            
        Returns:
            新文件名
        """
        path = Path(old_name)
        stem = path.stem
        suffix = path.suffix
        time_str = self.timestamp.strftime(self.format_str)
        new_stem = f"{time_str}_{index + 1}"
        new_name = new_stem + suffix
        return new_name


class ReplaceRenameStrategy(RenameStrategy):
    """
    查找替换重命名策略
    替换文件名中的特定字符串
    """

    def __init__(self, find: str, replace: str):
        """
        初始化查找替换策略
        
        Args:
            find: 要查找的字符串
            replace: 替换的字符串
        """
        self.find = find
        self.replace = replace

    def generate_new_name(self, old_name: str, index: int) -> str:
        """
        替换文件名中的特定字符串
        
        Args:
            old_name: 原始文件名
            index: 文件在列表中的索引
            
        Returns:
            新文件名
        """
        path = Path(old_name)
        stem = path.stem
        suffix = path.suffix
        new_stem = stem.replace(self.find, self.replace)
        new_name = new_stem + suffix
        return new_name


class PrefixRenameStrategy(RenameStrategy):
    """
    添加前缀重命名策略
    """

    def __init__(self, prefix: str):
        """
        初始化前缀策略
        
        Args:
            prefix: 要添加的前缀
        """
        self.prefix = prefix

    def generate_new_name(self, old_name: str, index: int) -> str:
        """
        在文件名前添加前缀
        
        Args:
            old_name: 原始文件名
            index: 文件在列表中的索引
            
        Returns:
            新文件名
        """
        path = Path(old_name)
        stem = path.stem
        suffix = path.suffix
        new_stem = f"{self.prefix}{stem}"
        new_name = new_stem + suffix
        return new_name


class SuffixRenameStrategy(RenameStrategy):
    """
    添加后缀重命名策略
    """

    def __init__(self, suffix_str: str):
        """
        初始化后缀策略
        
        Args:
            suffix_str: 要添加的后缀
        """
        self.suffix_str = suffix_str

    def generate_new_name(self, old_name: str, index: int) -> str:
        """
        在文件名(不含扩展名)后添加后缀
        
        Args:
            old_name: 原始文件名
            index: 文件在列表中的索引
            
        Returns:
            新文件名
        """
        path = Path(old_name)
        stem = path.stem
        suffix = path.suffix
        new_stem = f"{stem}{self.suffix_str}"
        new_name = new_stem + suffix
        return new_name


class RegexRenameStrategy(RenameStrategy):
    """
    正则表达式匹配替换重命名策略
    """

    def __init__(self, pattern: str, replace: str):
        """
        初始化正则表达式策略
        
        Args:
            pattern: 正则表达式匹配模式
            replace: 替换字符串(支持反向引用如\1, \2等)
        """
        self.pattern = pattern
        self.replace = replace
        self.regex = re.compile(pattern)

    def generate_new_name(self, old_name: str, index: int) -> str:
        """
        使用正则表达式匹配和替换文件名
        
        Args:
            old_name: 原始文件名
            index: 文件在列表中的索引
            
        Returns:
            新文件名
        """
        path = Path(old_name)
        stem = path.stem
        suffix = path.suffix
        new_stem = self.regex.sub(self.replace, stem)
        new_name = new_stem + suffix
        return new_name


class HistoryManager:
    """
    重命名历史管理器
    负责记录和恢复重命名操作
    """

    HISTORY_FILE = ".rename_history.json"

    def __init__(self, directory: str):
        """
        初始化历史管理器
        
        Args:
            directory: 工作目录
        """
        self.directory = directory
        self.history_file = os.path.join(directory, self.HISTORY_FILE)

    def save_history(self, operations: List[Dict[str, str]]):
        """
        保存重命名操作历史
        
        Args:
            operations: 操作列表，每个元素包含old_path和new_path
        """
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(operations, f, ensure_ascii=False, indent=2)

    def load_history(self) -> Optional[List[Dict[str, str]]]:
        """
        加载重命名操作历史
        
        Returns:
            操作列表，如果没有历史则返回None
        """
        if not os.path.exists(self.history_file):
            return None
        with open(self.history_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def clear_history(self):
        """
        清除重命名历史
        """
        if os.path.exists(self.history_file):
            os.remove(self.history_file)

    def has_history(self) -> bool:
        """
        检查是否有可撤销的历史
        
        Returns:
            是否存在历史文件
        """
        return os.path.exists(self.history_file)


class BatchRenamer:
    """
    批量重命名主类
    协调各种重命名策略，提供预览和执行功能
    """

    def __init__(self, directory: str, strategy: RenameStrategy,
                 file_extensions: Optional[List[str]] = None):
        """
        初始化批量重命名器
        
        Args:
            directory: 文件所在目录
            strategy: 重命名策略实例
            file_extensions: 可选的文件扩展名过滤列表，如['.jpg', '.png']
        """
        self.directory = os.path.abspath(directory)
        self.strategy = strategy
        self.file_extensions = file_extensions
        self.history_manager = HistoryManager(self.directory)

    def get_files(self) -> List[str]:
        """
        获取目录下的文件列表
        
        Returns:
            文件名列表，按名称排序
        """
        if not os.path.exists(self.directory):
            raise FileNotFoundError(f"目录不存在: {self.directory}")

        files = []
        for filename in os.listdir(self.directory):
            file_path = os.path.join(self.directory, filename)
            if os.path.isfile(file_path):
                if self.file_extensions:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in [e.lower() for e in self.file_extensions]:
                        files.append(filename)
                else:
                    files.append(filename)
        files.sort()
        return files

    def preview(self) -> List[Tuple[str, str]]:
        """
        预览重命名结果
        
        Returns:
            元组列表，每个元组为(原文件名, 新文件名)
        """
        files = self.get_files()
        preview_list = []
        for index, old_name in enumerate(files):
            new_name = self.strategy.generate_new_name(old_name, index)
            preview_list.append((old_name, new_name))
        return preview_list

    def execute(self, preview: bool = False) -> List[Tuple[str, str, bool]]:
        """
        执行批量重命名
        
        Args:
            preview: 是否为预览模式，True则不实际执行
            
        Returns:
            结果列表，每个元素为(原文件名, 新文件名, 是否成功)
        """
        files = self.get_files()
        results = []
        operations = []

        for index, old_name in enumerate(files):
            new_name = self.strategy.generate_new_name(old_name, index)
            old_path = os.path.join(self.directory, old_name)
            new_path = os.path.join(self.directory, new_name)

            success = True
            if not preview:
                try:
                    if old_path != new_path:
                        os.rename(old_path, new_path)
                    operations.append({
                        "old_path": old_path,
                        "new_path": new_path
                    })
                except OSError as e:
                    print(f"重命名失败: {old_name} -> {new_name}, 错误: {e}")
                    success = False

            results.append((old_name, new_name, success))

        if not preview and operations:
            self.history_manager.save_history(operations)

        return results

    def undo(self) -> List[Tuple[str, str, bool]]:
        """
        撤销上次批量重命名操作
        
        Returns:
            撤销结果列表，每个元素为(新文件名, 原文件名, 是否成功)
        """
        history = self.history_manager.load_history()
        if not history:
            return []

        results = []
        for op in reversed(history):
            old_path = op["old_path"]
            new_path = op["new_path"]
            old_name = os.path.basename(old_path)
            new_name = os.path.basename(new_path)

            success = True
            try:
                if os.path.exists(new_path):
                    os.rename(new_path, old_path)
            except OSError as e:
                print(f"撤销失败: {new_name} -> {old_name}, 错误: {e}")
                success = False

            results.append((new_name, old_name, success))

        self.history_manager.clear_history()
        return results
