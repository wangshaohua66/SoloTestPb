# -*- coding: utf-8 -*-
"""
BackupSync 核心功能单元测试
"""
import os
import shutil
import tempfile
import time
import pytest
import zipfile
from pathlib import Path
from backupsync import BackupSync


class TestBackupSync:
    """
    BackupSync 类的测试用例
    """
    
    @pytest.fixture
    def temp_dirs(self):
        """
        临时目录 fixture，在每个测试用例前后创建和清理
        """
        source_dir = tempfile.mkdtemp(prefix='test_source_')
        target_dir = tempfile.mkdtemp(prefix='test_target_')
        
        yield source_dir, target_dir
        
        shutil.rmtree(source_dir, ignore_errors=True)
        shutil.rmtree(target_dir, ignore_errors=True)
    
    def create_test_file(self, directory, filename, content='test content'):
        """
        创建测试文件
        """
        file_path = Path(directory) / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    def test_initialization(self, temp_dirs):
        """
        测试初始化功能
        """
        source_dir, target_dir = temp_dirs
        
        backup = BackupSync(
            source_dir=source_dir,
            target_dir=target_dir,
            exclude_patterns=['*.tmp'],
            exclude_extensions=['log', 'bak'],
            exclude_dirs=['node_modules', '__pycache__'],
            version_count=3
        )
        
        assert backup.source_dir == Path(source_dir).resolve()
        assert backup.target_dir == Path(target_dir).resolve()
        assert '*.tmp' in backup.exclude_patterns
        assert 'log' in backup.exclude_extensions
        assert 'node_modules' in backup.exclude_dirs
        assert backup.version_count == 3
    
    def test_get_changed_files_initial_backup(self, temp_dirs):
        """
        测试首次备份时的文件检测
        """
        source_dir, target_dir = temp_dirs
        
        self.create_test_file(source_dir, 'file1.txt', 'content1')
        self.create_test_file(source_dir, 'subdir/file2.txt', 'content2')
        
        backup = BackupSync(source_dir=source_dir, target_dir=target_dir)
        added, modified, deleted = backup.get_changed_files()
        
        assert len(added) == 2
        assert len(modified) == 0
        assert len(deleted) == 0
    
    def test_sync_initial_backup(self, temp_dirs):
        """
        测试首次备份功能
        """
        source_dir, target_dir = temp_dirs
        
        self.create_test_file(source_dir, 'file1.txt', 'content1')
        self.create_test_file(source_dir, 'subdir/file2.txt', 'content2')
        
        backup = BackupSync(source_dir=source_dir, target_dir=target_dir)
        stats = backup.sync()
        
        assert stats['added_count'] == 2
        assert stats['modified_count'] == 0
        assert stats['deleted_count'] == 0
        assert stats['total_copied'] == 2
        
        current_dir = Path(target_dir) / 'current'
        assert current_dir.exists()
        assert (current_dir / 'file1.txt').exists()
        assert (current_dir / 'subdir' / 'file2.txt').exists()
    
    def test_sync_incremental_modified_file(self, temp_dirs):
        """
        测试增量备份 - 修改文件的检测
        """
        source_dir, target_dir = temp_dirs
        
        file1 = self.create_test_file(source_dir, 'file1.txt', 'content1')
        file2 = self.create_test_file(source_dir, 'file2.txt', 'content2')
        
        backup = BackupSync(source_dir=source_dir, target_dir=target_dir, version_count=10)
        backup.sync()
        
        time.sleep(0.1)
        
        file1.write_text('modified content', encoding='utf-8')
        
        stats = backup.sync()
        
        assert stats['added_count'] == 0
        assert stats['modified_count'] == 1
        assert stats['deleted_count'] == 0
    
    def test_sync_incremental_new_file(self, temp_dirs):
        """
        测试增量备份 - 新增文件的检测
        """
        source_dir, target_dir = temp_dirs
        
        self.create_test_file(source_dir, 'file1.txt', 'content1')
        
        backup = BackupSync(source_dir=source_dir, target_dir=target_dir, version_count=10)
        backup.sync()
        
        time.sleep(0.1)
        
        self.create_test_file(source_dir, 'file2.txt', 'content2')
        
        stats = backup.sync()
        
        assert stats['added_count'] == 1
        assert stats['modified_count'] == 0
        assert stats['deleted_count'] == 0
    
    def test_sync_incremental_deleted_file(self, temp_dirs):
        """
        测试增量备份 - 删除文件的检测
        """
        source_dir, target_dir = temp_dirs
        
        file1 = self.create_test_file(source_dir, 'file1.txt', 'content1')
        self.create_test_file(source_dir, 'file2.txt', 'content2')
        
        backup = BackupSync(source_dir=source_dir, target_dir=target_dir, version_count=10)
        backup.sync()
        
        time.sleep(0.1)
        
        file1.unlink()
        
        stats = backup.sync()
        
        assert stats['added_count'] == 0
        assert stats['modified_count'] == 0
        assert stats['deleted_count'] == 1
    
    def test_exclude_extensions(self, temp_dirs):
        """
        测试文件扩展名过滤
        """
        source_dir, target_dir = temp_dirs
        
        self.create_test_file(source_dir, 'file1.txt', 'content1')
        self.create_test_file(source_dir, 'file2.log', 'log content')
        self.create_test_file(source_dir, 'file3.tmp', 'temp content')
        
        backup = BackupSync(
            source_dir=source_dir,
            target_dir=target_dir,
            exclude_extensions=['log', 'tmp']
        )
        
        added, modified, deleted = backup.get_changed_files()
        
        file_names = {f.name for f in added}
        assert 'file1.txt' in file_names
        assert 'file2.log' not in file_names
        assert 'file3.tmp' not in file_names
    
    def test_exclude_dirs(self, temp_dirs):
        """
        测试目录名过滤
        """
        source_dir, target_dir = temp_dirs
        source_path = Path(source_dir)
        
        self.create_test_file(source_dir, 'src/file1.txt', 'content1')
        self.create_test_file(source_dir, 'node_modules/package.json', '{}')
        self.create_test_file(source_dir, '__pycache__/module.pyc', 'bytecode')
        
        backup = BackupSync(
            source_dir=source_dir,
            target_dir=target_dir,
            exclude_dirs=['node_modules', '__pycache__']
        )
        
        added, modified, deleted = backup.get_changed_files()
        
        file_names = {f.name for f in added}
        parent_dirs = {f.parent.name for f in added}
        
        assert 'file1.txt' in file_names
        assert 'package.json' not in file_names
        assert 'module.pyc' not in file_names
        assert 'src' in parent_dirs
        assert 'node_modules' not in parent_dirs
        assert '__pycache__' not in parent_dirs
    
    def test_version_cleanup(self, temp_dirs):
        """
        测试历史版本清理
        """
        source_dir, target_dir = temp_dirs
        
        self.create_test_file(source_dir, 'file1.txt', 'content1')
        
        backup = BackupSync(source_dir=source_dir, target_dir=target_dir, version_count=2)
        
        import time as time_module
        for i in range(4):
            time_module.sleep(1.1)
            self.create_test_file(source_dir, f'file{i}.txt', f'content{i}')
            backup.sync()
        
        target_path = Path(target_dir)
        version_dirs = [d for d in target_path.iterdir() if d.is_dir() and d.name.startswith('v_')]
        
        assert len(version_dirs) == 2
    
    def test_compress_version(self, temp_dirs):
        """
        测试版本压缩功能
        """
        source_dir, target_dir = temp_dirs
        
        self.create_test_file(source_dir, 'file1.txt', 'content1')
        self.create_test_file(source_dir, 'subdir/file2.txt', 'content2')
        
        backup = BackupSync(source_dir=source_dir, target_dir=target_dir)
        backup.sync()
        
        zip_path = backup.compress_version()
        
        assert zip_path.exists()
        assert zip_path.suffix == '.zip'
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            namelist = zipf.namelist()
            assert 'file1.txt' in namelist
            assert 'subdir/file2.txt' in namelist
    
    def test_source_not_exists(self, temp_dirs):
        """
        测试源目录不存在的情况
        """
        source_dir, target_dir = temp_dirs
        shutil.rmtree(source_dir)
        
        backup = BackupSync(source_dir=source_dir, target_dir=target_dir)
        
        with pytest.raises(ValueError, match='源目录不存在'):
            backup.get_changed_files()
    
    def test_incremental_accuracy(self, temp_dirs):
        """
        测试增量备份检测准确率 100%
        """
        source_dir, target_dir = temp_dirs
        
        files_to_create = [
            'file1.txt', 'file2.txt', 'subdir1/file3.txt', 'subdir2/subsubdir/file4.txt'
        ]
        
        for fname in files_to_create:
            self.create_test_file(source_dir, fname, f'content_{fname}')
        
        backup = BackupSync(source_dir=source_dir, target_dir=target_dir, version_count=10)
        stats1 = backup.sync()
        
        assert stats1['added_count'] == 4
        assert stats1['modified_count'] == 0
        assert stats1['deleted_count'] == 0
        
        time.sleep(0.1)
        
        self.create_test_file(source_dir, 'new_file.txt', 'new content')
        Path(source_dir + '/file1.txt').write_text('modified file1', encoding='utf-8')
        Path(source_dir + '/subdir1/file3.txt').unlink()
        
        stats2 = backup.sync()
        
        assert stats2['added_count'] == 1
        assert stats2['modified_count'] == 1
        assert stats2['deleted_count'] == 1
        
        current_dir = Path(target_dir) / 'current'
        assert (current_dir / 'new_file.txt').exists()
        assert (current_dir / 'file1.txt').read_text() == 'modified file1'
        assert not (current_dir / 'subdir1/file3.txt').exists()
    
    def test_version_name_uniqueness(self, temp_dirs):
        """
        测试时间戳冲突场景 - 版本名称唯一性
        """
        source_dir, target_dir = temp_dirs
        
        self.create_test_file(source_dir, 'file1.txt', 'content1')
        
        backup = BackupSync(source_dir=source_dir, target_dir=target_dir, version_count=10)
        
        stats1 = backup.sync()
        version1_name = stats1.get('version_name')
        
        assert version1_name is not None
        assert version1_name.startswith('v_')
        assert len(version1_name) > len('v_YYYYMMDD_HHMMSS')
        
        time.sleep(0.01)
        
        stats2 = backup.sync()
        version2_name = stats2.get('version_name')
        
        assert version1_name != version2_name
        
        target_path = Path(target_dir)
        version_dirs = [d for d in target_path.iterdir() if d.is_dir() and d.name.startswith('v_')]
        
        assert len(version_dirs) == 2
        assert all(not str(d).endswith(' (deleted)') for d in version_dirs)
    
    def test_empty_directory_backup(self, temp_dirs):
        """
        测试空目录备份场景
        """
        source_dir, target_dir = temp_dirs
        source_path = Path(source_dir)
        
        (source_path / 'emptydir1').mkdir()
        (source_path / 'subdir').mkdir()
        (source_path / 'subdir' / 'emptydir2').mkdir()
        (source_path / 'subdir' / 'file1.txt').write_text('content1', encoding='utf-8')
        
        backup = BackupSync(source_dir=source_dir, target_dir=target_dir)
        stats = backup.sync()
        
        assert 'synced_dirs_count' in stats
        assert stats['synced_dirs_count'] == 3
        
        current_dir = Path(target_dir) / 'current'
        
        assert current_dir.exists()
        assert (current_dir / 'emptydir1').exists()
        assert (current_dir / 'emptydir1').is_dir()
        assert (current_dir / 'subdir').exists()
        assert (current_dir / 'subdir' / 'emptydir2').exists()
        assert (current_dir / 'subdir' / 'emptydir2').is_dir()
        assert (current_dir / 'subdir' / 'file1.txt').exists()
    
    def test_empty_directory_incremental_deletion(self, temp_dirs):
        """
        测试空目录增量删除场景
        """
        source_dir, target_dir = temp_dirs
        source_path = Path(source_dir)
        
        (source_path / 'emptydir1').mkdir()
        (source_path / 'subdir').mkdir()
        (source_path / 'subdir' / 'emptydir2').mkdir()
        (source_path / 'subdir' / 'file1.txt').write_text('content1', encoding='utf-8')
        
        backup = BackupSync(source_dir=source_dir, target_dir=target_dir, version_count=10)
        backup.sync()
        
        shutil.rmtree(source_path / 'emptydir1')
        shutil.rmtree(source_path / 'subdir' / 'emptydir2')
        
        stats = backup.sync()
        
        assert 'deleted_dirs_count' in stats
        assert stats['deleted_dirs_count'] == 2
        
        current_dir = Path(target_dir) / 'current'
        assert not (current_dir / 'emptydir1').exists()
        assert (current_dir / 'subdir').exists()
        assert not (current_dir / 'subdir' / 'emptydir2').exists()
        assert (current_dir / 'subdir' / 'file1.txt').exists()
    
    def test_cross_platform_path_compatibility(self, temp_dirs):
        """
        测试跨平台路径兼容性 - 删除文件路径计算
        """
        source_dir, target_dir = temp_dirs
        source_path = Path(source_dir)
        
        (source_path / 'subdir1').mkdir()
        (source_path / 'subdir1' / 'subdir2').mkdir()
        (source_path / 'subdir1' / 'file1.txt').write_text('content1', encoding='utf-8')
        (source_path / 'subdir1' / 'subdir2' / 'file2.txt').write_text('content2', encoding='utf-8')
        
        backup = BackupSync(source_dir=source_dir, target_dir=target_dir, version_count=10)
        stats1 = backup.sync()
        
        current_dir = Path(target_dir) / 'current'
        assert (current_dir / 'subdir1' / 'file1.txt').exists()
        assert (current_dir / 'subdir1' / 'subdir2' / 'file2.txt').exists()
        
        (source_path / 'subdir1' / 'file1.txt').unlink()
        
        stats2 = backup.sync()
        
        assert stats2['deleted_count'] == 1
        assert stats2['added_count'] == 0
        
        current_dir = Path(target_dir) / 'current'
        assert not (current_dir / 'subdir1' / 'file1.txt').exists()
        assert (current_dir / 'subdir1' / 'subdir2' / 'file2.txt').exists()
        
        shutil.rmtree(source_path / 'subdir1' / 'subdir2')
        
        stats3 = backup.sync()
        
        assert stats3['deleted_count'] == 1
        assert stats3['deleted_dirs_count'] >= 1
        
        current_dir = Path(target_dir) / 'current'
        assert not (current_dir / 'subdir1' / 'subdir2').exists()
    
    def test_version_name_microsecond_precision(self, temp_dirs):
        """
        测试微秒级时间戳精度
        """
        source_dir, target_dir = temp_dirs
        
        self.create_test_file(source_dir, 'file1.txt', 'content1')
        
        backup = BackupSync(source_dir=source_dir, target_dir=target_dir, version_count=10)
        
        stats1 = backup.sync()
        version1 = stats1['version_name']
        
        parts = version1.split('_')
        assert len(parts) >= 4
        assert len(parts[3]) == 6
        
        self.create_test_file(source_dir, 'file2.txt', 'content2')
        stats2 = backup.sync()
        version2 = stats2['version_name']
        
        assert version1 != version2
        assert len(version1) == len(version2) or (
            len(version1) > len('v_YYYYMMDD_HHMMSS_ffffff')
        )
