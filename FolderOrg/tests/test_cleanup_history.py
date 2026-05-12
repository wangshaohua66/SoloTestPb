"""
历史记录清理功能单元测试
"""

import os
import json
import pytest
from folder_organizer.file_classifier import FileClassifier
from folder_organizer.file_organizer import FileOrganizer


class TestCleanupHistory:
    """
    历史记录清理功能测试类
    """

    def test_cleanup_invalid_history_no_invalid(self, temp_dir, test_categories, test_files):
        """
        测试清理无效历史记录（没有无效记录）
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        organizer.organize()
        
        result = organizer.cleanup_invalid_history()
        
        assert result["total_records"] == 6
        assert result["cleaned_records"] == 0
        assert result["remaining_records"] == 6
        assert len(organizer.get_move_history()) == 6

    def test_cleanup_invalid_history_with_missing_files_aggressive(self, temp_dir, test_categories, test_files):
        """
        测试激进模式清理无效历史记录（目标文件已被删除）
        """
        import shutil
        
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        organizer.organize()
        
        docs_dir = os.path.join(temp_dir, "Documents")
        if os.path.exists(docs_dir):
            for f in os.listdir(docs_dir):
                file_path = os.path.join(docs_dir, f)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        
        result = organizer.cleanup_invalid_history(mode="aggressive")
        
        assert result["total_records"] == 6
        assert result["cleaned_records"] == 2
        assert result["remaining_records"] == 4
        assert result["mode"] == "aggressive"

    def test_cleanup_invalid_history_with_missing_files_conservative(self, temp_dir, test_categories, test_files):
        """
        测试保守模式清理无效历史记录（目标文件已被删除但不清理）
        """
        import shutil
        
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        organizer.organize()
        
        docs_dir = os.path.join(temp_dir, "Documents")
        if os.path.exists(docs_dir):
            for f in os.listdir(docs_dir):
                file_path = os.path.join(docs_dir, f)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        
        result = organizer.cleanup_invalid_history(mode="conservative")
        
        assert result["total_records"] == 6
        assert result["cleaned_records"] == 0
        assert result["remaining_records"] == 6
        assert result["mode"] == "conservative"

    def test_cleanup_invalid_history_incomplete_entries(self, temp_dir, test_categories):
        """
        测试清理无效历史记录（格式不完整的记录）
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        test_file = os.path.join(temp_dir, "test.pdf")
        with open(test_file, "w") as f:
            f.write("test")
        
        organizer.organize()
        
        with open(history_file, "r", encoding="utf-8") as f:
            history = json.load(f)
        
        history.append({"source_path": "/invalid/path"})
        history.append({"target_path": "/invalid/path"})
        history.append({"category": "documents"})
        history.append({})
        
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f)
        
        organizer2 = FileOrganizer(temp_dir, classifier, history_file)
        result = organizer2.cleanup_invalid_history()
        
        assert result["cleaned_records"] >= 4

    def test_cleanup_invalid_history_persistence(self, temp_dir, test_categories, test_files):
        """
        测试激进模式清理后历史记录的持久化
        """
        import shutil
        
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        organizer.organize()
        
        docs_dir = os.path.join(temp_dir, "Documents")
        if os.path.exists(docs_dir):
            shutil.rmtree(docs_dir)
        
        organizer.cleanup_invalid_history(mode="aggressive")
        
        with open(history_file, "r", encoding="utf-8") as f:
            saved_history = json.load(f)
        
        assert len(saved_history) == 4
        for entry in saved_history:
            assert "target_path" in entry
            assert "source_path" in entry
            assert "category" in entry
            assert "timestamp" in entry

    def test_ensure_history_dir_exists(self, temp_dir, test_categories):
        """
        测试确保历史记录目录存在
        """
        nested_dir = os.path.join(temp_dir, "deep", "nested", "dir")
        history_file = os.path.join(nested_dir, "history.json")
        
        assert not os.path.exists(nested_dir)
        
        classifier = FileClassifier(test_categories)
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        assert os.path.exists(nested_dir)
        assert os.path.exists(os.path.dirname(history_file))

    def test_cleanup_invalid_history_all_invalid_aggressive(self, temp_dir, test_categories):
        """
        测试激进模式清理全部无效的历史记录
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        
        invalid_history = [
            {
                "source_path": "/non/existent/file1.pdf",
                "target_path": "/non/existent/Documents/file1.pdf",
                "category": "documents",
                "timestamp": "2024-01-01T00:00:00"
            },
            {
                "source_path": "/non/existent/file2.jpg",
                "target_path": "/non/existent/Images/file2.jpg",
                "category": "images",
                "timestamp": "2024-01-01T00:00:01"
            }
        ]
        
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(invalid_history, f)
        
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        result = organizer.cleanup_invalid_history(mode="aggressive")
        
        assert result["total_records"] == 2
        assert result["cleaned_records"] == 2
        assert result["remaining_records"] == 0
        assert len(organizer.get_move_history()) == 0
        assert result["mode"] == "aggressive"

    def test_cleanup_invalid_history_all_invalid_conservative(self, temp_dir, test_categories):
        """
        测试保守模式不清理目标文件不存在的历史记录
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        
        invalid_history = [
            {
                "source_path": "/non/existent/file1.pdf",
                "target_path": "/non/existent/Documents/file1.pdf",
                "category": "documents",
                "timestamp": "2024-01-01T00:00:00"
            },
            {
                "source_path": "/non/existent/file2.jpg",
                "target_path": "/non/existent/Images/file2.jpg",
                "category": "images",
                "timestamp": "2024-01-01T00:00:01"
            }
        ]
        
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(invalid_history, f)
        
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        result = organizer.cleanup_invalid_history(mode="conservative")
        
        assert result["total_records"] == 2
        assert result["cleaned_records"] == 0
        assert result["remaining_records"] == 2
        assert len(organizer.get_move_history()) == 2
        assert result["mode"] == "conservative"

    def test_cleanup_invalid_history_mixed_aggressive(self, temp_dir, test_categories):
        """
        测试激进模式清理混合有效和无效的历史记录
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        
        valid_file = os.path.join(temp_dir, "Documents", "valid.pdf")
        os.makedirs(os.path.dirname(valid_file), exist_ok=True)
        with open(valid_file, "w") as f:
            f.write("test")
        
        mixed_history = [
            {
                "source_path": os.path.join(temp_dir, "valid.pdf"),
                "target_path": valid_file,
                "category": "documents",
                "timestamp": "2024-01-01T00:00:00"
            },
            {
                "source_path": "/non/existent/file1.pdf",
                "target_path": "/non/existent/Documents/file1.pdf",
                "category": "documents",
                "timestamp": "2024-01-01T00:00:01"
            },
            {
                "source_path": "/non/existent/file2.jpg",
                "target_path": "/non/existent/Images/file2.jpg",
                "category": "images",
                "timestamp": "2024-01-01T00:00:02"
            }
        ]
        
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(mixed_history, f)
        
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        result = organizer.cleanup_invalid_history(mode="aggressive")
        
        assert result["total_records"] == 3
        assert result["cleaned_records"] == 2
        assert result["remaining_records"] == 1
        assert len(organizer.get_move_history()) == 1
        assert result["mode"] == "aggressive"

    def test_cleanup_invalid_history_mixed_conservative(self, temp_dir, test_categories):
        """
        测试保守模式清理混合有效和无效的历史记录（只清理格式不完整的）
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        
        valid_file = os.path.join(temp_dir, "Documents", "valid.pdf")
        os.makedirs(os.path.dirname(valid_file), exist_ok=True)
        with open(valid_file, "w") as f:
            f.write("test")
        
        mixed_history = [
            {
                "source_path": os.path.join(temp_dir, "valid.pdf"),
                "target_path": valid_file,
                "category": "documents",
                "timestamp": "2024-01-01T00:00:00"
            },
            {
                "source_path": "/non/existent/file1.pdf",
                "target_path": "/non/existent/Documents/file1.pdf",
                "category": "documents",
                "timestamp": "2024-01-01T00:00:01"
            },
            {
                "incomplete": "entry"
            }
        ]
        
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(mixed_history, f)
        
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        result = organizer.cleanup_invalid_history(mode="conservative")
        
        assert result["total_records"] == 3
        assert result["cleaned_records"] == 1
        assert result["remaining_records"] == 2
        assert len(organizer.get_move_history()) == 2
        assert result["mode"] == "conservative"

    def test_cleanup_dry_run(self, temp_dir, test_categories):
        """
        测试清理的预览模式（dry_run）
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        
        history = [
            {
                "incomplete": "entry"
            },
            {
                "source_path": "/valid/path/file.pdf",
                "target_path": "/valid/path/Documents/file.pdf",
                "category": "documents",
                "timestamp": "2024-01-01T00:00:00"
            }
        ]
        
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f)
        
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        result = organizer.cleanup_invalid_history(dry_run=True)
        
        assert result["dry_run"] is True
        assert result["cleaned_records"] == 1
        assert len(organizer.get_move_history()) == 2

