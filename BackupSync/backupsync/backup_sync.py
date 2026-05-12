# -*- coding: utf-8 -*-
"""
核心备份同步模块
提供文件同步、增量备份和文件过滤功能
"""
import os
import shutil
import filecmp
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Set, Tuple, Dict, Any


class BackupSync:
    """
    备份同步类，负责执行文件同步和增量备份操作
    """
    
    def __init__(
        self,
        source_dir: str,
        target_dir: str,
        exclude_patterns: List[str] = None,
        exclude_extensions: List[str] = None,
        exclude_dirs: List[str] = None,
        version_count: int = 5
    ):
        """
        初始化备份同步器
        
        参数:
            source_dir: 源目录路径
            target_dir: 目标目录路径
            exclude_patterns: 要排除的文件/目录通配符模式列表
            exclude_extensions: 要排除的文件扩展名列表（不含点）
            exclude_dirs: 要排除的目录名列表
            version_count: 保留的历史版本数量
        """
        self.source_dir = Path(source_dir).resolve()
        self.target_dir = Path(target_dir).resolve()
        self.exclude_patterns = exclude_patterns or []
        self.exclude_extensions = [ext.lower() for ext in (exclude_extensions or [])]
        self.exclude_dirs = set(exclude_dirs or [])
        self.version_count = max(1, version_count)
        self._stats: Dict[str, Any] = {}
    
    def _should_exclude(self, path: Path, base_dir: Path = None) -> bool:
        """
        检查文件或目录是否应该被排除
        
        参数:
            path: 要检查的文件或目录路径
            base_dir: 基础目录路径（用于计算相对路径）
        返回:
            如果应该排除则返回True，否则返回False
        """
        if base_dir:
            try:
                relative_path = path.relative_to(base_dir)
            except ValueError:
                relative_path = path
        else:
            relative_path = path
        
        path_str = str(relative_path)
        
        if path.is_dir():
            if path.name in self.exclude_dirs:
                return True
        
        if path.is_file():
            file_ext = path.suffix.lower().lstrip('.')
            if file_ext in self.exclude_extensions:
                return True
        
        for pattern in self.exclude_patterns:
            if relative_path.match(pattern) or path_str in pattern or pattern in path_str:
                return True
        
        return False
    
    def _get_all_files(self, base_dir: Path) -> Set[Path]:
        """
        获取目录下所有文件路径（排除过滤的文件）
        
        参数:
            base_dir: 基础目录路径
            
        返回:
            所有符合条件的文件路径集合
        """
        files = set()
        
        for root, dirs, filenames in os.walk(base_dir):
            root_path = Path(root)
            
            dirs[:] = [d for d in dirs if not self._should_exclude(root_path / d, base_dir)]
            
            for filename in filenames:
                file_path = root_path / filename
                if not self._should_exclude(file_path, base_dir):
                    files.add(file_path)
        
        return files
    
    def _get_all_dirs(self, base_dir: Path) -> Set[Path]:
        """
        获取目录下所有子目录路径（包括空目录，排除过滤的目录）
        
        参数:
            base_dir: 基础目录路径
            
        返回:
            所有符合条件的子目录路径集合（相对于base_dir）
        """
        dirs = set()
        
        for root, subdirs, _ in os.walk(base_dir):
            root_path = Path(root)
            
            subdirs[:] = [d for d in subdirs if not self._should_exclude(root_path / d, base_dir)]
            
            for subdir in subdirs:
                dir_path = root_path / subdir
                rel_path = dir_path.relative_to(base_dir)
                dirs.add(rel_path)
        
        return dirs
    
    def _get_relative_path(self, file_path: Path, base_dir: Path) -> Path:
        """
        获取文件相对于基础目录的路径
        
        参数:
            file_path: 文件绝对路径
            base_dir: 基础目录路径
            
        返回:
            相对路径
        """
        return file_path.relative_to(base_dir)
    
    def _files_are_different(self, file1: Path, file2: Path) -> bool:
        """
        比较两个文件是否不同（使用filecmp）
        
        参数:
            file1: 第一个文件路径
            file2: 第二个文件路径
            
        返回:
            如果文件不同则返回True，否则返回False
        """
        try:
            return not filecmp.cmp(str(file1), str(file2), shallow=False)
        except (OSError, IOError):
            return True
    
    def _get_file_size(self, file_path: Path) -> int:
        """
        获取文件大小（字节）
        
        参数:
            file_path: 文件路径
            
        返回:
            文件大小（字节）
        """
        try:
            return file_path.stat().st_size
        except (OSError, IOError):
            return 0
    
    def _copy_file(self, source_file: Path, target_file: Path) -> None:
        """
        复制文件，确保目标目录存在
        
        参数:
            source_file: 源文件路径
            target_file: 目标文件路径
        """
        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(source_file), str(target_file))
    
    def _create_dir(self, target_dir: Path) -> None:
        """
        创建目录，确保父目录存在
        
        参数:
            target_dir: 要创建的目录路径
        """
        target_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_unique_version_name(self) -> str:
        """
        生成唯一的版本目录名称，避免时间戳冲突
        
        返回:
            唯一的版本名称，格式为 v_YYYYMMDD_HHMMSS_ffffff[_N]
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        base_name = f"v_{timestamp}"
        version_dir = self.target_dir / base_name
        
        counter = 1
        while version_dir.exists():
            version_dir = self.target_dir / f"{base_name}_{counter}"
            counter += 1
        
        return version_dir.name
    
    def get_changed_files(self) -> Tuple[Set[Path], Set[Path], Set[Path]]:
        """
        获取需要同步的文件列表
        
        返回:
            元组包含：新增文件集合、修改文件集合、删除文件集合
        """
        if not self.source_dir.exists():
            raise ValueError(f"源目录不存在: {self.source_dir}")
        
        source_files = self._get_all_files(self.source_dir)
        
        current_dir = self.target_dir / "current"
        if not current_dir.exists():
            return source_files, set(), set()
        
        target_files = self._get_all_files(current_dir)
        
        source_relative = {self._get_relative_path(f, self.source_dir): f for f in source_files}
        target_relative = {self._get_relative_path(f, current_dir): f for f in target_files}
        
        source_keys = set(source_relative.keys())
        target_keys = set(target_relative.keys())
        
        added_files = {source_relative[k] for k in source_keys - target_keys}
        deleted_files = {target_relative[k] for k in target_keys - source_keys}
        common_files = source_keys & target_keys
        
        modified_files = set()
        for rel_path in common_files:
            src_file = source_relative[rel_path]
            tgt_file = target_relative[rel_path]
            if self._files_are_different(src_file, tgt_file):
                modified_files.add(src_file)
        
        return added_files, modified_files, deleted_files
    
    def get_changed_dirs(self) -> Tuple[Set[Path], Set[Path]]:
        """
        获取需要同步的空目录列表
        
        返回:
            元组包含：新增/存在的目录集合（相对路径）、删除的目录集合（相对路径）
        """
        if not self.source_dir.exists():
            raise ValueError(f"源目录不存在: {self.source_dir}")
        
        source_dirs = self._get_all_dirs(self.source_dir)
        
        current_dir = self.target_dir / "current"
        if not current_dir.exists():
            return source_dirs, set()
        
        target_dirs = self._get_all_dirs(current_dir)
        
        added_or_existing_dirs = source_dirs
        deleted_dirs = target_dirs - source_dirs
        
        return added_or_existing_dirs, deleted_dirs
    
    def sync(self) -> Dict[str, Any]:
        """
        执行增量备份同步
        
        返回:
            包含同步统计信息的字典
        """
        version_name = self._generate_unique_version_name()
        version_dir = self.target_dir / version_name
        current_link = self.target_dir / "current"
        timestamp = version_name
        
        added_files, modified_files, deleted_files = self.get_changed_files()
        source_dirs, deleted_dirs = self.get_changed_dirs()
        
        current_exists = False
        current_target = None
        if current_link.is_symlink():
            try:
                current_target = current_link.resolve()
                current_exists = current_target.exists() and current_target.is_dir()
            except (OSError, ValueError):
                current_exists = False
        elif current_link.exists():
            current_target = current_link
            current_exists = current_target.is_dir()
        
        if current_exists and current_target:
            shutil.copytree(
                str(current_target),
                str(version_dir),
                symlinks=False,
                ignore=None,
                copy_function=shutil.copy2
            )
        else:
            version_dir.mkdir(parents=True, exist_ok=True)
        
        total_copied = 0
        total_size = 0
        
        for file_set, label in [(added_files, "新增"), (modified_files, "修改")]:
            for src_file in file_set:
                rel_path = self._get_relative_path(src_file, self.source_dir)
                tgt_file = version_dir / rel_path
                self._copy_file(src_file, tgt_file)
                total_copied += 1
                total_size += self._get_file_size(src_file)
        
        for rel_dir in source_dirs:
            target_subdir = version_dir / rel_dir
            self._create_dir(target_subdir)
        
        if current_exists and current_target:
            current_ref_dir = current_link
            for deleted_file in deleted_files:
                try:
                    rel_path = deleted_file.relative_to(current_ref_dir)
                    tgt_file = version_dir / rel_path
                    if tgt_file.exists():
                        tgt_file.unlink()
                except ValueError:
                    try:
                        rel_path = deleted_file.relative_to(current_target)
                        tgt_file = version_dir / rel_path
                        if tgt_file.exists():
                            tgt_file.unlink()
                    except ValueError:
                        pass
            
            for deleted_rel_dir in deleted_dirs:
                target_subdir = version_dir / deleted_rel_dir
                if target_subdir.exists() and target_subdir.is_dir():
                    try:
                        target_subdir.rmdir()
                    except OSError:
                        pass
        
        if current_link.exists():
            if current_link.is_symlink():
                current_link.unlink()
            else:
                shutil.rmtree(current_link)
        
        try:
            current_link.symlink_to(version_dir, target_is_directory=True)
        except OSError:
            if current_link.exists():
                shutil.rmtree(current_link)
            shutil.copytree(str(version_dir), str(current_link))
        
        self._cleanup_old_versions()
        
        self._stats = {
            "timestamp": timestamp,
            "version_dir": str(version_dir),
            "version_name": version_name,
            "added_count": len(added_files),
            "modified_count": len(modified_files),
            "deleted_count": len(deleted_files),
            "total_copied": total_copied,
            "total_size_bytes": total_size,
            "added_files": [str(f) for f in added_files],
            "modified_files": [str(f) for f in modified_files],
            "deleted_files": [str(f) for f in deleted_files],
            "synced_dirs_count": len(source_dirs),
            "deleted_dirs_count": len(deleted_dirs)
        }
        
        return self._stats
    
    def _cleanup_old_versions(self) -> None:
        """
        清理过期的历史版本，只保留最近的version_count个版本
        """
        if not self.target_dir.exists():
            return
        
        version_dirs = []
        for item in self.target_dir.iterdir():
            if item.is_dir() and item.name.startswith("v_"):
                version_dirs.append(item)
        
        version_dirs.sort(key=lambda d: d.name, reverse=True)
        
        for old_dir in version_dirs[self.version_count:]:
            shutil.rmtree(old_dir)
    
    def compress_version(self, version_name: str = None) -> Path:
        """
        压缩指定版本为zip文件
        
        参数:
            version_name: 版本名称（例如v_20240101_120000），如果为None则压缩最新版本
            
        返回:
            压缩文件的路径
        """
        if version_name:
            version_dir = self.target_dir / version_name
        else:
            current_link = self.target_dir / "current"
            if not current_link.exists():
                raise ValueError("没有可用的备份版本")
            version_dir = current_link if not current_link.is_symlink() else current_link.resolve()
        
        if not version_dir.exists():
            raise ValueError(f"版本目录不存在: {version_dir}")
        
        zip_path = self.target_dir / f"{version_dir.name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(version_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(version_dir)
                    zipf.write(str(file_path), str(arcname))
        
        return zip_path
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取最近一次同步的统计信息
        
        返回:
            统计信息字典
        """
        return self._stats.copy()
