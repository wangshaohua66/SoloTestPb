"""
文件还原模块单元测试
"""

import os
import pytest
from folder_organizer.file_classifier import FileClassifier
from folder_organizer.file_organizer import FileOrganizer
from folder_organizer.file_restorer import FileRestorer


class TestFileRestorer:
    """
    文件还原器测试类
    """

    def test_init(self, temp_dir, test_categories, test_files):
        """
        测试初始化
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        organizer.organize()
        history = organizer.get_move_history()
        restorer = FileRestorer(history)
        
        assert restorer.move_history == history

    def test_restore_last(self, temp_dir, test_categories, test_files):
        """
        测试还原最近的文件
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        organizer.organize()
        history = organizer.get_move_history()
        restorer = FileRestorer(history)
        
        result = restorer.restore_last(count=2)
        
        assert result["success_count"] == 2
        assert result["failed_count"] == 0
        assert len(result["restored_files"]) == 2

    def test_restore_all(self, temp_dir, test_categories, test_files):
        """
        测试还原所有文件
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        organizer.organize()
        history = organizer.get_move_history()
        restorer = FileRestorer(history)
        
        result = restorer.restore_all()
        
        assert result["success_count"] == 6
        assert result["failed_count"] == 0
        assert len(result["restored_files"]) == 6
        
        for filename in test_files.keys():
            assert os.path.exists(os.path.join(temp_dir, filename))

    def test_restore_by_category(self, temp_dir, test_categories, test_files):
        """
        测试按分类还原文件
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        organizer.organize()
        history = organizer.get_move_history()
        restorer = FileRestorer(history)
        
        result = restorer.restore_by_category("documents")
        
        assert result["success_count"] == 2
        assert result["failed_count"] == 0
        
        assert os.path.exists(os.path.join(temp_dir, "report.pdf"))
        assert os.path.exists(os.path.join(temp_dir, "notes.txt"))

    def test_restore_file_nonexistent(self, temp_dir, test_categories):
        """
        测试还原不存在的文件
        """
        history = [
            {
                "source_path": os.path.join(temp_dir, "nonexistent.pdf"),
                "target_path": os.path.join(temp_dir, "Documents", "nonexistent.pdf"),
                "category": "documents",
                "timestamp": "2024-01-01T00:00:00"
            }
        ]
        restorer = FileRestorer(history)
        
        success = restorer.restore_file(history[0])
        assert success is False

    def test_generate_unique_path(self, temp_dir, test_categories):
        """
        测试生成唯一路径
        """
        restorer = FileRestorer([])
        
        target_path = os.path.join(temp_dir, "test.txt")
        assert restorer._generate_unique_path(target_path) == target_path
        
        with open(target_path, "w") as f:
            f.write("test")
        
        unique_path = restorer._generate_unique_path(target_path)
        assert unique_path == os.path.join(temp_dir, "test_1.txt")

    def test_get_restore_history(self, temp_dir, test_categories, test_files):
        """
        测试获取可还原的历史记录
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        organizer.organize()
        history = organizer.get_move_history()
        restorer = FileRestorer(history)
        
        restorable = restorer.get_restore_history()
        assert len(restorable) == 6

    def test_update_history(self, temp_dir, test_categories, test_files):
        """
        测试更新历史记录
        """
        restorer = FileRestorer([])
        assert len(restorer.move_history) == 0
        
        new_history = [
            {
                "source_path": "/path/to/file.pdf",
                "target_path": "/path/to/Documents/file.pdf",
                "category": "documents",
                "timestamp": "2024-01-01T00:00:00"
            }
        ]
        restorer.update_history(new_history)
        assert restorer.move_history == new_history

    def test_restore_integration(self, temp_dir, test_categories, test_files):
        """
        测试完整的整理和还原流程
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        def get_files_in_dir(dir_path):
            return set(
                item for item in os.listdir(dir_path)
                if os.path.isfile(os.path.join(dir_path, item)) and item != "history.json"
            )
        
        original_files = get_files_in_dir(temp_dir)
        
        organizer.organize()
        organized_files = get_files_in_dir(temp_dir)
        assert original_files != organized_files
        
        history = organizer.get_move_history()
        restorer = FileRestorer(history)
        restorer.restore_all()
        
        restored_files = get_files_in_dir(temp_dir)
        assert restored_files == original_files

    def test_restore_file_creates_source_dir(self, temp_dir, test_categories):
        """
        测试还原文件时自动创建源目录
        """
        import shutil
        
        source_dir = os.path.join(temp_dir, "source")
        os.makedirs(source_dir)
        
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(source_dir, classifier, history_file)
        
        test_file = os.path.join(source_dir, "test.pdf")
        with open(test_file, "w") as f:
            f.write("test")
        
        organizer.organize()
        
        moved_file = os.path.join(source_dir, "Documents", "test.pdf")
        assert os.path.exists(moved_file)
        
        backup_dir = os.path.join(temp_dir, "backup")
        os.makedirs(backup_dir)
        shutil.move(moved_file, os.path.join(backup_dir, "test.pdf"))
        
        shutil.rmtree(source_dir)
        assert not os.path.exists(source_dir)
        
        new_source_dir = os.path.join(temp_dir, "source")
        os.makedirs(os.path.join(new_source_dir, "Documents"))
        shutil.move(os.path.join(backup_dir, "test.pdf"), os.path.join(new_source_dir, "Documents", "test.pdf"))
        
        history = [
            {
                "source_path": test_file,
                "target_path": os.path.join(new_source_dir, "Documents", "test.pdf"),
                "category": "documents",
                "timestamp": "2024-01-01T00:00:00"
            }
        ]
        restorer = FileRestorer(history)
        result = restorer.restore_all()
        
        assert result["success_count"] == 1
        assert os.path.exists(test_file)
        assert os.path.exists(source_dir)
