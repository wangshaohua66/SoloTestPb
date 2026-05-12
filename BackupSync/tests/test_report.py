# -*- coding: utf-8 -*-
"""
BackupReport 备份报告单元测试
"""
import os
import shutil
import tempfile
import pytest
from pathlib import Path
from backupsync import BackupReport


class TestBackupReport:
    """
    BackupReport 类的测试用例
    """
    
    @pytest.fixture
    def temp_dir(self):
        """
        临时目录 fixture
        """
        target_dir = tempfile.mkdtemp(prefix='test_target_')
        
        yield target_dir
        
        shutil.rmtree(target_dir, ignore_errors=True)
    
    def create_version_dir(self, target_dir, version_name, files):
        """
        创建测试版本目录
        """
        version_dir = Path(target_dir) / version_name
        version_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path, content in files.items():
            full_path = version_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
    
    def test_initialization(self, temp_dir):
        """
        测试初始化功能
        """
        report = BackupReport(target_dir=temp_dir)
        
        assert report.target_dir == Path(temp_dir).resolve()
    
    def test_format_size(self, temp_dir):
        """
        测试文件大小格式化
        """
        report = BackupReport(target_dir=temp_dir)
        
        assert report._format_size(100) == '100 B'
        assert report._format_size(1024) == '1.00 KB'
        assert report._format_size(1024 * 1024) == '1.00 MB'
        assert report._format_size(1024 * 1024 * 1024) == '1.00 GB'
    
    def test_generate_text_report(self, temp_dir):
        """
        测试生成文本报告
        """
        report = BackupReport(target_dir=temp_dir)
        
        stats = {
            'version_dir': '/backup/v_20240101_120000',
            'added_count': 2,
            'modified_count': 1,
            'deleted_count': 0,
            'total_copied': 3,
            'total_size_bytes': 1024,
            'added_files': ['/source/file1.txt', '/source/file2.txt'],
            'modified_files': ['/source/file3.txt'],
            'deleted_files': []
        }
        
        text_report = report.generate_text_report(stats)
        
        assert '自动备份同步工具 - 备份报告' in text_report
        assert '新增文件数: 2' in text_report
        assert '修改文件数: 1' in text_report
        assert '删除文件数: 0' in text_report
        assert '1.00 KB' in text_report
        assert '新增文件列表' in text_report
        assert '修改文件列表' in text_report
        assert 'file1.txt' in text_report
        assert 'file2.txt' in text_report
        assert 'file3.txt' in text_report
    
    def test_generate_html_report(self, temp_dir):
        """
        测试生成HTML报告
        """
        report = BackupReport(target_dir=temp_dir)
        
        stats = {
            'version_dir': '/backup/v_20240101_120000',
            'added_count': 2,
            'modified_count': 1,
            'deleted_count': 0,
            'total_copied': 3,
            'total_size_bytes': 1024,
            'added_files': ['/source/file1.txt', '/source/file2.txt'],
            'modified_files': ['/source/file3.txt'],
            'deleted_files': []
        }
        
        html_report = report.generate_html_report(stats)
        
        assert '<!DOCTYPE html>' in html_report
        assert '<title>备份报告' in html_report
        assert '新增文件数' in html_report
        assert '修改文件数' in html_report
        assert '删除文件数' in html_report
        assert 'file1.txt' in html_report
        assert 'file2.txt' in html_report
        assert 'file3.txt' in html_report
    
    def test_save_text_report(self, temp_dir):
        """
        测试保存文本报告
        """
        report = BackupReport(target_dir=temp_dir)
        
        stats = {
            'version_dir': '/backup/v_20240101_120000',
            'added_count': 1,
            'modified_count': 0,
            'deleted_count': 0,
            'total_copied': 1,
            'total_size_bytes': 100,
            'added_files': ['/source/file1.txt'],
            'modified_files': [],
            'deleted_files': []
        }
        
        report_path = report.save_report(stats, report_type='text')
        
        assert report_path.exists()
        assert report_path.suffix == '.txt'
        assert report_path.parent.name == 'reports'
        
        content = report_path.read_text(encoding='utf-8')
        assert '自动备份同步工具 - 备份报告' in content
    
    def test_save_html_report(self, temp_dir):
        """
        测试保存HTML报告
        """
        report = BackupReport(target_dir=temp_dir)
        
        stats = {
            'version_dir': '/backup/v_20240101_120000',
            'added_count': 1,
            'modified_count': 0,
            'deleted_count': 0,
            'total_copied': 1,
            'total_size_bytes': 100,
            'added_files': ['/source/file1.txt'],
            'modified_files': [],
            'deleted_files': []
        }
        
        report_path = report.save_report(stats, report_type='html')
        
        assert report_path.exists()
        assert report_path.suffix == '.html'
        assert report_path.parent.name == 'reports'
        
        content = report_path.read_text(encoding='utf-8')
        assert '<!DOCTYPE html>' in content
    
    def test_get_backup_history_empty(self, temp_dir):
        """
        测试获取空的备份历史
        """
        report = BackupReport(target_dir=temp_dir)
        
        history = report.get_backup_history()
        
        assert history == []
    
    def test_get_backup_history(self, temp_dir):
        """
        测试获取备份历史
        """
        report = BackupReport(target_dir=temp_dir)
        
        self.create_version_dir(temp_dir, 'v_20240101_120000', {
            'file1.txt': 'content1',
            'subdir/file2.txt': 'content2'
        })
        
        self.create_version_dir(temp_dir, 'v_20240102_120000', {
            'file1.txt': 'content1',
            'file3.txt': 'content3'
        })
        
        history = report.get_backup_history()
        
        assert len(history) == 2
        assert history[0]['version'] == 'v_20240102_120000'
        assert history[1]['version'] == 'v_20240101_120000'
        assert history[0]['file_count'] == 2
        assert history[0]['timestamp'] == '20240102_120000'
        assert 'formatted' in history[0]['total_size_formatted'] or 'B' in history[0]['total_size_formatted']
