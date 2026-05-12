"""
文件整理核心模块单元测试
"""

import os
import json
import pytest
from folder_organizer.file_classifier import FileClassifier
from folder_organizer.file_organizer import FileOrganizer


class TestFileOrganizer:
    """
    文件整理器测试类
    """

    def test_init(self, temp_dir, test_categories):
        """
        测试初始化
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        assert organizer.source_dir == temp_dir
        assert organizer.classifier == classifier
        assert organizer.move_history_file == history_file

    def test_scan_files(self, temp_dir, test_categories, test_files):
        """
        测试扫描文件
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        files = organizer.scan_files()
        assert len(files) == 6
        
        for file_path in test_files.values():
            assert file_path in files

    def test_scan_files_empty_dir(self, temp_dir, test_categories):
        """
        测试扫描空目录
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        files = organizer.scan_files()
        assert files == []

    def test_scan_files_nonexistent_dir(self, test_categories):
        """
        测试扫描不存在的目录
        """
        classifier = FileClassifier(test_categories)
        organizer = FileOrganizer("/non/existent/path", classifier)
        
        files = organizer.scan_files()
        assert files == []

    def test_move_file(self, temp_dir, test_categories, test_files):
        """
        测试移动单个文件
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        pdf_file = test_files["report.pdf"]
        success, target_path, category = organizer.move_file(pdf_file)
        
        assert success is True
        assert target_path is not None
        assert category == "documents"
        assert not os.path.exists(pdf_file)
        assert os.path.exists(target_path)
        assert os.path.basename(target_path) == "report.pdf"

    def test_move_file_nonexistent(self, temp_dir, test_categories):
        """
        测试移动不存在的文件
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        success, target_path, category = organizer.move_file("/non/existent/file.pdf")
        assert success is False
        assert target_path is None

    def test_move_file_creates_target_dir(self, temp_dir, test_categories, test_files):
        """
        测试移动文件时自动创建目标目录
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        images_dir = os.path.join(temp_dir, "Images")
        assert not os.path.exists(images_dir)
        
        image_file = test_files["image.jpg"]
        organizer.move_file(image_file)
        
        assert os.path.exists(images_dir)
        assert os.path.isdir(images_dir)

    def test_organize(self, temp_dir, test_categories, test_files):
        """
        测试完整的整理操作
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        result = organizer.organize()
        
        assert result["total_files"] == 6
        assert result["moved_files"] == 6
        assert result["failed_files"] == 0
        assert result["elapsed_time"] >= 0
        
        assert result["category_stats"]["documents"] == 2
        assert result["category_stats"]["images"] == 1
        assert result["category_stats"]["videos"] == 1
        assert result["category_stats"]["audio"] == 1
        assert result["category_stats"]["others"] == 1

    def test_generate_unique_path(self, temp_dir, test_categories):
        """
        测试生成唯一路径
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        target_path = os.path.join(temp_dir, "test.txt")
        
        assert organizer._generate_unique_path(target_path) == target_path
        
        with open(target_path, "w") as f:
            f.write("test")
        
        unique_path = organizer._generate_unique_path(target_path)
        assert unique_path == os.path.join(temp_dir, "test_1.txt")
        
        with open(unique_path, "w") as f:
            f.write("test")
        
        unique_path2 = organizer._generate_unique_path(target_path)
        assert unique_path2 == os.path.join(temp_dir, "test_2.txt")

    def test_move_history(self, temp_dir, test_categories, test_files):
        """
        测试移动历史记录
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        organizer.organize()
        history = organizer.get_move_history()
        
        assert len(history) == 6
        for entry in history:
            assert "source_path" in entry
            assert "target_path" in entry
            assert "category" in entry
            assert "timestamp" in entry

    def test_move_history_persistence(self, temp_dir, test_categories, test_files):
        """
        测试移动历史持久化
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        organizer.organize()
        
        with open(history_file, "r", encoding="utf-8") as f:
            saved_history = json.load(f)
        
        assert len(saved_history) == 6

    def test_clear_history(self, temp_dir, test_categories, test_files):
        """
        测试清空历史记录
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        organizer.organize()
        assert len(organizer.get_move_history()) == 6
        
        organizer.clear_history()
        assert len(organizer.get_move_history()) == 0
        
        with open(history_file, "r", encoding="utf-8") as f:
            saved_history = json.load(f)
        assert saved_history == []

    def test_get_move_history_limit(self, temp_dir, test_categories, test_files):
        """
        测试获取限制数量的历史记录
        """
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        organizer.organize()
        
        limited_history = organizer.get_move_history(limit=3)
        assert len(limited_history) == 3

    def test_performance_large_files(self, temp_dir, test_categories):
        """
        测试性能：处理多个文件的时间
        """
        import time
        
        classifier = FileClassifier(test_categories)
        history_file = os.path.join(temp_dir, "history.json")
        organizer = FileOrganizer(temp_dir, classifier, history_file)
        
        num_files = 100
        for i in range(num_files):
            ext = [".pdf", ".jpg", ".mp4", ".mp3", ".txt"][i % 5]
            file_path = os.path.join(temp_dir, f"file_{i}{ext}")
            with open(file_path, "w") as f:
                f.write("x" * 100)
        
        start_time = time.time()
        result = organizer.organize()
        elapsed_time = time.time() - start_time
        
        assert result["total_files"] == num_files
        assert result["moved_files"] == num_files
        assert elapsed_time < 30

    def test_performance_1000_files(self, temp_dir, test_categories):
        """
        测试性能：处理1000个文件的时间（验收标准要求≤30秒）
        
        测试设计：
        - 同一目录反复运行3次（消除文件系统缓存影响）
        - 每次运行后清理所有内容再重新创建文件
        - 测试不同大小的文件（1KB, 10KB, 100KB, 1MB）
        - 使用固定随机种子确保测试可重复
        """
        import time
        import shutil
        import random
        
        classifier = FileClassifier(test_categories)
        
        num_runs = 3
        total_time = 0.0
        
        file_sizes = [1024, 10240, 102400, 1048576]
        extensions = [".pdf", ".jpg", ".png", ".mp4", ".avi", ".mp3", ".wav", ".txt", ".doc", ".zip"]
        
        run_dir = os.path.join(temp_dir, "performance_test")
        os.makedirs(run_dir)
        run_history = os.path.join(run_dir, ".folderorg_history.json")
        
        for run in range(num_runs):
            random.seed(42 + run)
            organizer = FileOrganizer(run_dir, classifier, run_history)
            
            for i in range(1000):
                ext = extensions[i % len(extensions)]
                file_size = file_sizes[i % len(file_sizes)]
                file_path = os.path.join(run_dir, f"test_file_{i:04d}{ext}")
                with open(file_path, "wb") as f:
                    f.write(b"x" * file_size)
            
            start_time = time.time()
            result = organizer.organize()
            elapsed_time = time.time() - start_time
            
            assert result["total_files"] == 1000
            assert result["moved_files"] == 1000
            assert result["failed_files"] == 0
            
            total_time += elapsed_time
            
            for item in os.listdir(run_dir):
                item_path = os.path.join(run_dir, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
        
        avg_time = total_time / num_runs
        
        assert avg_time < 30, f"处理1000个文件平均耗时 {avg_time:.2f} 秒（{num_runs}次运行），超过了30秒的限制"

    def test_performance_recursive_nested_dirs(self, temp_dir, test_categories):
        """
        测试性能：递归处理深层嵌套目录（3-5层）的性能
        
        测试设计：
        - 创建5层嵌套目录结构
        - 每个目录中创建多个测试文件
        - 测试递归模式的整理性能
        - 测试保持结构模式和扁平化模式
        """
        import time
        import shutil
        
        classifier = FileClassifier(test_categories)
        
        run_dir = os.path.join(temp_dir, "recursive_performance_test")
        os.makedirs(run_dir)
        run_history = os.path.join(run_dir, ".folderorg_history.json")
        
        num_levels = 5
        files_per_level = 40
        extensions = [".pdf", ".jpg", ".txt", ".doc", ".zip"]
        file_sizes = [1024, 10240, 102400]
        
        organizer_structure = FileOrganizer(run_dir, classifier, run_history, recursive=True, flatten=False)
        
        for level in range(1, num_levels + 1):
            level_dir = run_dir
            for _ in range(level):
                level_dir = os.path.join(level_dir, f"level_{_}")
            os.makedirs(level_dir, exist_ok=True)
            
            for i in range(files_per_level):
                ext = extensions[i % len(extensions)]
                file_size = file_sizes[i % len(file_sizes)]
                file_path = os.path.join(level_dir, f"file_{level}_{i:03d}{ext}")
                with open(file_path, "wb") as f:
                    f.write(b"x" * file_size)
        
        start_time = time.time()
        result = organizer_structure.organize(recursive=True, flatten=False)
        elapsed_time_structure = time.time() - start_time
        
        assert result["total_files"] == num_levels * files_per_level
        assert result["moved_files"] == num_levels * files_per_level
        assert elapsed_time_structure < 30, f"递归整理（保持结构）耗时 {elapsed_time_structure:.2f} 秒，超过了30秒的限制"
        
        for item in os.listdir(run_dir):
            item_path = os.path.join(run_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        
        organizer_flatten = FileOrganizer(run_dir, classifier, run_history, recursive=True, flatten=True)
        
        for level in range(1, num_levels + 1):
            level_dir = run_dir
            for _ in range(level):
                level_dir = os.path.join(level_dir, f"level_{_}")
            os.makedirs(level_dir, exist_ok=True)
            
            for i in range(files_per_level):
                ext = extensions[i % len(extensions)]
                file_size = file_sizes[i % len(file_sizes)]
                file_path = os.path.join(level_dir, f"file_{level}_{i:03d}{ext}")
                with open(file_path, "wb") as f:
                    f.write(b"x" * file_size)
        
        start_time = time.time()
        result = organizer_flatten.organize(recursive=True, flatten=True)
        elapsed_time_flatten = time.time() - start_time
        
        assert result["total_files"] == num_levels * files_per_level
        assert result["moved_files"] == num_levels * files_per_level
        assert elapsed_time_flatten < 30, f"递归整理（扁平化）耗时 {elapsed_time_flatten:.2f} 秒，超过了30秒的限制"
