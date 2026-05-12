"""
递归处理子目录和多目录隔离功能单元测试
"""

import os
import json
import pytest
from folder_organizer.file_classifier import FileClassifier
from folder_organizer.file_organizer import FileOrganizer


class TestRecursiveProcessing:
    """
    递归处理子目录功能测试类
    """

    def test_recursive_scan_files(self, temp_dir, test_categories):
        """
        测试递归扫描子目录中的文件
        """
        subdir1 = os.path.join(temp_dir, "subdir1")
        subdir2 = os.path.join(temp_dir, "subdir2")
        nested = os.path.join(subdir2, "nested")
        os.makedirs(subdir1)
        os.makedirs(nested)
        
        files = [
            os.path.join(temp_dir, "file1.pdf"),
            os.path.join(subdir1, "file2.jpg"),
            os.path.join(subdir2, "file3.mp3"),
            os.path.join(nested, "file4.txt")
        ]
        
        for file_path in files:
            with open(file_path, "w") as f:
                f.write("test")
        
        classifier = FileClassifier(test_categories)
        organizer = FileOrganizer(temp_dir, classifier, recursive=True)
        
        scanned_files = organizer.scan_files()
        
        assert len(scanned_files) == 4
        for file_path in files:
            assert file_path in scanned_files

    def test_non_recursive_scan_files(self, temp_dir, test_categories):
        """
        测试非递归扫描（只扫描直接文件）
        """
        subdir1 = os.path.join(temp_dir, "subdir1")
        os.makedirs(subdir1)
        
        root_file = os.path.join(temp_dir, "file1.pdf")
        sub_file = os.path.join(subdir1, "file2.jpg")
        
        with open(root_file, "w") as f:
            f.write("test")
        with open(sub_file, "w") as f:
            f.write("test")
        
        classifier = FileClassifier(test_categories)
        organizer = FileOrganizer(temp_dir, classifier, recursive=False)
        
        scanned_files = organizer.scan_files()
        
        assert len(scanned_files) == 1
        assert root_file in scanned_files
        assert sub_file not in scanned_files

    def test_recursive_organize_preserves_structure(self, temp_dir, test_categories):
        """
        测试递归整理时保持相对路径结构
        """
        subdir1 = os.path.join(temp_dir, "subdir1")
        nested = os.path.join(subdir1, "nested")
        os.makedirs(nested)
        
        root_file = os.path.join(temp_dir, "root.pdf")
        sub_file = os.path.join(subdir1, "sub.jpg")
        nested_file = os.path.join(nested, "nested.txt")
        
        for file_path in [root_file, sub_file, nested_file]:
            with open(file_path, "w") as f:
                f.write("test")
        
        classifier = FileClassifier(test_categories)
        organizer = FileOrganizer(temp_dir, classifier, recursive=True)
        
        result = organizer.organize(recursive=True)
        
        assert result["total_files"] == 3
        assert result["moved_files"] == 3
        
        docs_dir = os.path.join(temp_dir, "Documents")
        images_dir = os.path.join(temp_dir, "Images")
        
        assert os.path.exists(os.path.join(docs_dir, "root.pdf"))
        assert os.path.exists(os.path.join(images_dir, "subdir1", "sub.jpg"))
        assert os.path.exists(os.path.join(docs_dir, "subdir1", "nested", "nested.txt"))

    def test_recursive_organize_history(self, temp_dir, test_categories):
        """
        测试递归整理时的历史记录
        """
        subdir1 = os.path.join(temp_dir, "subdir1")
        os.makedirs(subdir1)
        
        files = [
            os.path.join(temp_dir, "file1.pdf"),
            os.path.join(subdir1, "file2.jpg")
        ]
        
        for file_path in files:
            with open(file_path, "w") as f:
                f.write("test")
        
        classifier = FileClassifier(test_categories)
        organizer = FileOrganizer(temp_dir, classifier, recursive=True)
        
        organizer.organize(recursive=True)
        
        history = organizer.get_move_history()
        assert len(history) == 2
        
        source_paths = [entry["source_path"] for entry in history]
        for file_path in files:
            assert file_path in source_paths

    def test_recursive_restore(self, temp_dir, test_categories):
        """
        测试递归整理后的文件还原
        """
        from folder_organizer.file_restorer import FileRestorer
        
        subdir1 = os.path.join(temp_dir, "subdir1")
        os.makedirs(subdir1)
        
        files = [
            os.path.join(temp_dir, "file1.pdf"),
            os.path.join(subdir1, "file2.jpg")
        ]
        
        for file_path in files:
            with open(file_path, "w") as f:
                f.write("test")
        
        classifier = FileClassifier(test_categories)
        organizer = FileOrganizer(temp_dir, classifier, recursive=True)
        
        organizer.organize(recursive=True)
        
        history = organizer.get_move_history()
        restorer = FileRestorer(history)
        
        result = restorer.restore_all()
        
        assert result["success_count"] == 2
        
        for file_path in files:
            assert os.path.exists(file_path)

    def test_recursive_organize_flatten_mode(self, temp_dir, test_categories):
        """
        测试递归整理的扁平化模式（所有文件直接放到分类目录）
        """
        subdir1 = os.path.join(temp_dir, "subdir1")
        nested = os.path.join(subdir1, "nested")
        os.makedirs(nested)
        
        root_file = os.path.join(temp_dir, "root.pdf")
        sub_file = os.path.join(subdir1, "sub.jpg")
        nested_file = os.path.join(nested, "nested.txt")
        
        for file_path in [root_file, sub_file, nested_file]:
            with open(file_path, "w") as f:
                f.write("test")
        
        classifier = FileClassifier(test_categories)
        organizer = FileOrganizer(temp_dir, classifier, recursive=True, flatten=True)
        
        result = organizer.organize(recursive=True, flatten=True)
        
        assert result["total_files"] == 3
        assert result["moved_files"] == 3
        
        docs_dir = os.path.join(temp_dir, "Documents")
        images_dir = os.path.join(temp_dir, "Images")
        
        assert os.path.exists(os.path.join(docs_dir, "root.pdf"))
        assert os.path.exists(os.path.join(images_dir, "sub.jpg"))
        assert os.path.exists(os.path.join(docs_dir, "nested.txt"))
        
        assert not os.path.exists(os.path.join(docs_dir, "subdir1"))
        assert not os.path.exists(os.path.join(images_dir, "subdir1"))

    def test_recursive_organize_flatten_with_duplicate_names(self, temp_dir, test_categories):
        """
        测试扁平化模式下的同名文件处理（自动重命名）
        """
        subdir1 = os.path.join(temp_dir, "subdir1")
        subdir2 = os.path.join(temp_dir, "subdir2")
        os.makedirs(subdir1)
        os.makedirs(subdir2)
        
        file1 = os.path.join(temp_dir, "file.pdf")
        file2 = os.path.join(subdir1, "file.pdf")
        file3 = os.path.join(subdir2, "file.pdf")
        
        for file_path in [file1, file2, file3]:
            with open(file_path, "w") as f:
                f.write("test")
        
        classifier = FileClassifier(test_categories)
        organizer = FileOrganizer(temp_dir, classifier, recursive=True, flatten=True)
        
        result = organizer.organize(recursive=True, flatten=True)
        
        assert result["total_files"] == 3
        assert result["moved_files"] == 3
        
        docs_dir = os.path.join(temp_dir, "Documents")
        
        assert os.path.exists(os.path.join(docs_dir, "file.pdf"))
        assert os.path.exists(os.path.join(docs_dir, "file_1.pdf"))
        assert os.path.exists(os.path.join(docs_dir, "file_2.pdf"))

    def test_flatten_vs_structure_mode(self, temp_dir, test_categories):
        """
        对比测试：扁平化模式 vs 保持结构模式
        """
        import shutil
        
        classifier = FileClassifier(test_categories)
        docs_dir = os.path.join(temp_dir, "Documents")
        
        subdir1 = os.path.join(temp_dir, "flatten_test", "subdir")
        os.makedirs(subdir1)
        
        for i in range(3):
            file_path = os.path.join(subdir1, f"file_{i}.pdf")
            with open(file_path, "w") as f:
                f.write("test")
        
        organizer_flatten = FileOrganizer(os.path.join(temp_dir, "flatten_test"), classifier, recursive=True, flatten=True)
        result_flatten = organizer_flatten.organize(recursive=True, flatten=True)
        
        assert result_flatten["moved_files"] == 3
        flatten_docs_dir = os.path.join(temp_dir, "flatten_test", "Documents")
        for i in range(3):
            assert os.path.exists(os.path.join(flatten_docs_dir, f"file_{i}.pdf"))
        assert not os.path.exists(os.path.join(flatten_docs_dir, "subdir"))
        
        subdir2 = os.path.join(temp_dir, "structure_test", "subdir")
        os.makedirs(subdir2)
        
        for i in range(3):
            file_path = os.path.join(subdir2, f"file_{i}.pdf")
            with open(file_path, "w") as f:
                f.write("test")
        
        organizer_structure = FileOrganizer(os.path.join(temp_dir, "structure_test"), classifier, recursive=True, flatten=False)
        result_structure = organizer_structure.organize(recursive=True, flatten=False)
        
        assert result_structure["moved_files"] == 3
        structure_docs_dir = os.path.join(temp_dir, "structure_test", "Documents")
        for i in range(3):
            assert os.path.exists(os.path.join(structure_docs_dir, "subdir", f"file_{i}.pdf"))


class TestMultiDirectoryIsolation:
    """
    多目录隔离功能测试类
    """

    def test_separate_history_files(self, temp_dir, test_categories):
        """
        测试不同源目录使用独立的历史文件
        """
        dir1 = os.path.join(temp_dir, "dir1")
        dir2 = os.path.join(temp_dir, "dir2")
        os.makedirs(dir1)
        os.makedirs(dir2)
        
        file1 = os.path.join(dir1, "file1.pdf")
        file2 = os.path.join(dir2, "file2.jpg")
        
        with open(file1, "w") as f:
            f.write("test")
        with open(file2, "w") as f:
            f.write("test")
        
        classifier = FileClassifier(test_categories)
        
        organizer1 = FileOrganizer(dir1, classifier)
        organizer2 = FileOrganizer(dir2, classifier)
        
        organizer1.organize()
        organizer2.organize()
        
        history_file1 = os.path.join(dir1, ".folderorg_history.json")
        history_file2 = os.path.join(dir2, ".folderorg_history.json")
        
        assert os.path.exists(history_file1)
        assert os.path.exists(history_file2)
        
        with open(history_file1, "r", encoding="utf-8") as f:
            history1 = json.load(f)
        with open(history_file2, "r", encoding="utf-8") as f:
            history2 = json.load(f)
        
        assert len(history1) == 1
        assert len(history2) == 1
        assert history1[0]["source_path"] == file1
        assert history2[0]["source_path"] == file2

    def test_history_isolation(self, temp_dir, test_categories):
        """
        测试不同目录的历史记录互不干扰
        """
        dir1 = os.path.join(temp_dir, "dir1")
        dir2 = os.path.join(temp_dir, "dir2")
        os.makedirs(dir1)
        os.makedirs(dir2)
        
        for i in range(3):
            file_path = os.path.join(dir1, f"file{i}.pdf")
            with open(file_path, "w") as f:
                f.write("test")
        
        for i in range(5):
            file_path = os.path.join(dir2, f"file{i}.jpg")
            with open(file_path, "w") as f:
                f.write("test")
        
        classifier = FileClassifier(test_categories)
        
        organizer1 = FileOrganizer(dir1, classifier)
        organizer2 = FileOrganizer(dir2, classifier)
        
        organizer1.organize()
        organizer2.organize()
        
        history1 = organizer1.get_move_history()
        history2 = organizer2.get_move_history()
        
        assert len(history1) == 3
        assert len(history2) == 5
        
        for entry in history1:
            assert dir1 in entry["source_path"]
        
        for entry in history2:
            assert dir2 in entry["source_path"]

    def test_restore_isolation(self, temp_dir, test_categories):
        """
        测试不同目录的还原操作互不干扰
        """
        from folder_organizer.file_restorer import FileRestorer
        
        dir1 = os.path.join(temp_dir, "dir1")
        dir2 = os.path.join(temp_dir, "dir2")
        os.makedirs(dir1)
        os.makedirs(dir2)
        
        file1 = os.path.join(dir1, "file1.pdf")
        file2 = os.path.join(dir2, "file2.jpg")
        
        with open(file1, "w") as f:
            f.write("test")
        with open(file2, "w") as f:
            f.write("test")
        
        classifier = FileClassifier(test_categories)
        
        organizer1 = FileOrganizer(dir1, classifier)
        organizer2 = FileOrganizer(dir2, classifier)
        
        organizer1.organize()
        organizer2.organize()
        
        history1 = organizer1.get_move_history()
        restorer1 = FileRestorer(history1)
        restorer1.restore_all()
        
        assert os.path.exists(file1)
        assert not os.path.exists(file2)

    def test_history_file_excluded_from_scan(self, temp_dir, test_categories):
        """
        测试历史文件被排除在扫描之外
        """
        classifier = FileClassifier(test_categories)
        organizer = FileOrganizer(temp_dir, classifier)
        
        history_file = os.path.join(temp_dir, ".folderorg_history.json")
        regular_file = os.path.join(temp_dir, "test.pdf")
        
        with open(regular_file, "w") as f:
            f.write("test")
        
        files = organizer.scan_files()
        
        assert regular_file in files
        assert history_file not in files
