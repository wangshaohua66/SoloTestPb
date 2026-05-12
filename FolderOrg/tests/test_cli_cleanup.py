"""
CLI清理命令单元测试
"""

import os
import json
import argparse
import pytest
from folder_organizer.file_classifier import FileClassifier
from folder_organizer.file_organizer import FileOrganizer


class TestCLICleanup:
    """
    CLI清理命令测试类
    """

    def _create_test_history(self, temp_dir, num_valid=3, num_invalid=2):
        """
        创建测试历史记录
        
        Args:
            temp_dir: 临时目录
            num_valid: 有效记录数量
            num_invalid: 无效记录数量（目标文件不存在）
            
        Returns:
            历史文件路径
        """
        history_file = os.path.join(temp_dir, ".folderorg_history.json")
        
        history = []
        
        for i in range(num_valid):
            valid_file = os.path.join(temp_dir, f"valid_file_{i}.pdf")
            target_file = os.path.join(temp_dir, "Documents", f"valid_file_{i}.pdf")
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            with open(target_file, "w") as f:
                f.write("test")
            
            history.append({
                "source_path": valid_file,
                "target_path": target_file,
                "category": "documents",
                "timestamp": f"2024-01-01T00:0{i}:00"
            })
        
        for i in range(num_invalid):
            history.append({
                "source_path": f"/non/existent/invalid_{i}.pdf",
                "target_path": f"/non/existent/Documents/invalid_{i}.pdf",
                "category": "documents",
                "timestamp": f"2024-01-01T00:{i+num_valid}:00"
            })
        
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f)
        
        return history_file

    def test_aggressive_with_yes_skips_confirmation(self, temp_dir, test_categories):
        """
        测试激进模式配合--yes参数跳过确认
        """
        history_file = self._create_test_history(temp_dir, num_valid=2, num_invalid=3)
        
        args = argparse.Namespace(
            source_dir=temp_dir,
            mode="aggressive",
            dry_run=False,
            skip_confirm=True
        )
        
        classifier = FileClassifier(test_categories)
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        result = organizer.cleanup_invalid_history(mode=args.mode, dry_run=args.dry_run)
        
        assert result["mode"] == "aggressive"
        assert result["total_records"] == 5
        assert result["cleaned_records"] == 3
        assert result["remaining_records"] == 2
        assert len(organizer.get_move_history()) == 2

    def test_conservative_mode_no_confirmation_needed(self, temp_dir, test_categories):
        """
        测试保守模式无需确认
        """
        history_file = self._create_test_history(temp_dir, num_valid=2, num_invalid=3)
        
        args = argparse.Namespace(
            source_dir=temp_dir,
            mode="conservative",
            dry_run=False,
            skip_confirm=False
        )
        
        classifier = FileClassifier(test_categories)
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        result = organizer.cleanup_invalid_history(mode=args.mode, dry_run=args.dry_run)
        
        assert result["mode"] == "conservative"
        assert result["total_records"] == 5
        assert result["cleaned_records"] == 0
        assert result["remaining_records"] == 5
        assert len(organizer.get_move_history()) == 5

    def test_dry_run_does_not_modify_history(self, temp_dir, test_categories):
        """
        测试dry_run模式不修改历史记录
        """
        history_file = self._create_test_history(temp_dir, num_valid=2, num_invalid=3)
        
        args = argparse.Namespace(
            source_dir=temp_dir,
            mode="aggressive",
            dry_run=True,
            skip_confirm=False
        )
        
        classifier = FileClassifier(test_categories)
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        result = organizer.cleanup_invalid_history(mode=args.mode, dry_run=args.dry_run)
        
        assert result["dry_run"] is True
        assert result["cleaned_records"] == 3
        assert len(organizer.get_move_history()) == 5

    def test_force_parameter_same_as_yes(self, temp_dir, test_categories):
        """
        测试--force参数与--yes效果相同
        """
        history_file = self._create_test_history(temp_dir, num_valid=1, num_invalid=2)
        
        args = argparse.Namespace(
            source_dir=temp_dir,
            mode="aggressive",
            dry_run=False,
            skip_confirm=True
        )
        
        classifier = FileClassifier(test_categories)
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        result = organizer.cleanup_invalid_history(mode=args.mode, dry_run=args.dry_run)
        
        assert result["mode"] == "aggressive"
        assert result["cleaned_records"] == 2
        assert result["remaining_records"] == 1

    def test_incomplete_records_cleaned_in_both_modes(self, temp_dir, test_categories):
        """
        测试格式不完整的记录在两种模式下都被清理
        """
        history_file = os.path.join(temp_dir, ".folderorg_history.json")
        
        history = [
            {
                "source_path": os.path.join(temp_dir, "valid.pdf"),
                "target_path": os.path.join(temp_dir, "Documents", "valid.pdf"),
                "category": "documents",
                "timestamp": "2024-01-01T00:00:00"
            },
            {
                "incomplete": "entry"
            },
            {
                "source_path": "/missing/path.pdf"
            }
        ]
        
        os.makedirs(os.path.dirname(history[0]["target_path"]), exist_ok=True)
        with open(history[0]["target_path"], "w") as f:
            f.write("test")
        
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f)
        
        classifier = FileClassifier(test_categories)
        
        organizer_conservative = FileOrganizer(temp_dir, classifier, history_file)
        result_conservative = organizer_conservative.cleanup_invalid_history(mode="conservative")
        assert result_conservative["cleaned_records"] == 2
        assert len(organizer_conservative.get_move_history()) == 1
        
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f)
        
        organizer_aggressive = FileOrganizer(temp_dir, classifier, history_file)
        result_aggressive = organizer_aggressive.cleanup_invalid_history(mode="aggressive", dry_run=True)
        assert result_aggressive["cleaned_records"] == 2
